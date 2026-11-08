"""System of record: SQLite locally and in tests, Postgres when deployed.

`Store()` uses Postgres when DATABASE_URL is set (the LiveKit Cloud deploy, where
the container's disk doesn't outlive a restart), SQLite at data/summit.db otherwise.
The SQL is written once, in SQLite's dialect, and translated for Postgres.

In production this would be ServiceTitan or Housecall Pro behind the same
methods; nothing above this module should need to know the difference.
"""

import json
import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Any

from summit import config
from summit.models import Appointment, Customer, Membership, Pool, Priority

SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
    id          INTEGER PRIMARY KEY,
    first_name  TEXT NOT NULL,
    last_name   TEXT NOT NULL,
    phone       TEXT NOT NULL,
    address     TEXT NOT NULL,
    zip         TEXT NOT NULL,
    county      TEXT NOT NULL,
    -- 0: made from an unverified caller's booking. Not used for caller ID or lookups
    -- until the office confirms it.
    confirmed   INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS customers_phone ON customers (phone);

CREATE TABLE IF NOT EXISTS memberships (
    customer_id INTEGER PRIMARY KEY REFERENCES customers (id),
    status      TEXT NOT NULL CHECK (status IN ('active', 'lapsed')),
    expires_on  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS appointments (
    id              INTEGER PRIMARY KEY,
    customer_id     INTEGER NOT NULL REFERENCES customers (id),
    call_id         TEXT,
    county          TEXT NOT NULL,
    day             TEXT NOT NULL,
    arrival_window  TEXT NOT NULL,
    pool            TEXT NOT NULL CHECK (pool IN ('regular', 'emergency', 'member')),
    job_type        TEXT NOT NULL,
    priority        INTEGER NOT NULL,
    service_address TEXT NOT NULL,
    contact_name    TEXT NOT NULL,
    contact_phone   TEXT NOT NULL,
    notes           TEXT NOT NULL DEFAULT '',
    status          TEXT NOT NULL DEFAULT 'booked'
                    CHECK (status IN ('booked', 'on_hold', 'moved', 'cancelled')),
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS appointments_slot ON appointments (county, day, arrival_window, pool, status);

CREATE TABLE IF NOT EXISTS calls (
    id          TEXT PRIMARY KEY,
    caller_id   TEXT,
    started_at  TEXT NOT NULL,
    ended_at    TEXT,
    last_seen   TEXT,  -- the call's heartbeat: every save moves it
    priority    INTEGER,
    outcome     TEXT,
    summary     TEXT,
    record      TEXT NOT NULL DEFAULT '{}',
    transcript  TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS alerts (
    id           INTEGER PRIMARY KEY,
    call_id      TEXT,
    severity     TEXT NOT NULL CHECK (severity IN ('critical', 'urgent', 'info')),
    summary      TEXT NOT NULL,
    acknowledged INTEGER NOT NULL DEFAULT 0,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS callbacks (
    id          INTEGER PRIMARY KEY,
    call_id     TEXT,
    phone       TEXT NOT NULL,
    name        TEXT,
    reason      TEXT NOT NULL,
    urgent      INTEGER NOT NULL DEFAULT 0,
    due_at      TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'done')),
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


_BOOKING_LOCK = 4242


class _PgRow(dict):
    """A row that, like sqlite3.Row, answers to row["name"] and row[0]."""

    def __getitem__(self, key: Any) -> Any:
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


def _pg_rows(cursor: Any) -> Any:
    names = [c.name for c in cursor.description or []]
    return lambda values: _PgRow(zip(names, values, strict=True))


class _PgConnection:
    """The part of sqlite3's connection API this module and the dashboard use, over psycopg.
    SQL comes in SQLite's dialect ("?" placeholders) and is translated here."""

    def __init__(self, url: str) -> None:
        import psycopg  # only needed when deployed

        self._conn = psycopg.connect(url, autocommit=True, row_factory=_pg_rows)

    def execute(self, sql: str, params: tuple | list = ()) -> Any:
        return self._conn.execute(sql.replace("%", "%%").replace("?", "%s"), params)

    def executescript(self, script: str) -> None:
        self._conn.execute(script)  # several statements, no parameters

    def close(self) -> None:
        self._conn.close()


def _pg_schema() -> str:
    return SCHEMA.replace("INTEGER PRIMARY KEY", "BIGSERIAL PRIMARY KEY").replace(
        "(datetime('now'))", "(now()::text)"
    )


class Store:
    def __init__(self, path: Path | str | None = None) -> None:
        url = str(path) if path else os.getenv("DATABASE_URL", "")
        self.is_postgres = url.startswith(("postgres://", "postgresql://"))
        if self.is_postgres:
            self.path = url
            self.conn: Any = _PgConnection(url)
            self.conn.executescript(_pg_schema())
            self.conn.execute(
                "ALTER TABLE customers ADD COLUMN IF NOT EXISTS confirmed INTEGER NOT NULL DEFAULT 1"
            )
            self.conn.execute("ALTER TABLE calls ADD COLUMN IF NOT EXISTS last_seen TEXT")
            return
        self.path = str(path or config.db_path())
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        # Autocommit; multi-statement writes go through write_lock() explicitly.
        self.conn = sqlite3.connect(self.path, isolation_level=None, check_same_thread=False, timeout=5)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        if self.path != ":memory:":
            self.conn.execute("PRAGMA journal_mode = WAL")
        self._migrate()
        self.conn.executescript(SCHEMA)

    def _insert(self, sql: str, params: tuple) -> int:
        """Run an INSERT and return the new row's id, in either database."""
        if self.is_postgres:
            return self.conn.execute(sql + " RETURNING id", params).fetchone()[0]
        return self.conn.execute(sql, params).lastrowid

    def _migrate(self) -> None:
        columns = [r[1] for r in self.conn.execute("PRAGMA table_info(customers)")]
        if columns and "confirmed" not in columns:
            self.conn.execute("ALTER TABLE customers ADD COLUMN confirmed INTEGER NOT NULL DEFAULT 1")
        call_columns = [r[1] for r in self.conn.execute("PRAGMA table_info(calls)")]
        if call_columns and "last_seen" not in call_columns:
            self.conn.execute("ALTER TABLE calls ADD COLUMN last_seen TEXT")
        # Databases made before 'on_hold' existed reject it; rebuild the table with the new CHECK.
        row = self.conn.execute("SELECT sql FROM sqlite_master WHERE name = 'appointments'").fetchone()
        if row is None or "on_hold" in row[0]:
            return
        create = SCHEMA[SCHEMA.index("CREATE TABLE IF NOT EXISTS appointments") :]
        create = create[: create.index(");") + 2].replace("IF NOT EXISTS appointments", "appointments_new")
        # SQLite's recipe for changing a constraint: foreign keys off, copy, swap.
        self.conn.execute("PRAGMA foreign_keys = OFF")
        try:
            with self.write_lock() as conn:
                conn.execute(create)
                conn.execute("INSERT INTO appointments_new SELECT * FROM appointments")
                conn.execute("DROP TABLE appointments")
                conn.execute("ALTER TABLE appointments_new RENAME TO appointments")
        finally:
            self.conn.execute("PRAGMA foreign_keys = ON")

    def close(self) -> None:
        self.conn.close()

    def drop_all(self) -> None:
        """Delete every table, for `seed --reset` on Postgres. Irreversible."""
        for table in ("callbacks", "alerts", "calls", "appointments", "memberships", "customers"):
            self.conn.execute(f"DROP TABLE IF EXISTS {table}")

    @contextmanager
    def write_lock(self) -> Iterator[Any]:
        """Take the write lock up front, so a seat check and the insert that depends on it
        can't interleave with another call's booking. SQLite: BEGIN IMMEDIATE. Postgres: one
        transaction-scoped advisory lock that every booking and move queues on."""
        if self.is_postgres:
            self.conn.execute("BEGIN")
            self.conn.execute("SELECT pg_advisory_xact_lock(?)", (_BOOKING_LOCK,))
        else:
            self.conn.execute("BEGIN IMMEDIATE")
        try:
            yield self.conn
        except BaseException:
            self.conn.execute("ROLLBACK")
            raise
        self.conn.execute("COMMIT")

    # Customers

    def add_customer(
        self,
        first_name: str,
        last_name: str,
        phone: str,
        address: str,
        zip_code: str,
        county: str,
        confirmed: bool = True,
    ) -> int:
        return self._insert(
            "INSERT INTO customers (first_name, last_name, phone, address, zip, county, confirmed) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (first_name, last_name, phone, address, zip_code, county, int(confirmed)),
        )

    def delete_customer_without_history(self, customer_id: int) -> None:
        """Remove a customer created for a booking that then failed. Never one with any
        appointment or membership."""
        self.conn.execute(
            "DELETE FROM customers WHERE id = ? "
            "AND NOT EXISTS (SELECT 1 FROM appointments WHERE customer_id = customers.id) "
            "AND NOT EXISTS (SELECT 1 FROM memberships WHERE customer_id = customers.id)",
            (customer_id,),
        )

    def set_membership(self, customer_id: int, status: Membership, expires_on: date) -> None:
        self.conn.execute(
            "INSERT INTO memberships (customer_id, status, expires_on) VALUES (?, ?, ?) "
            "ON CONFLICT (customer_id) DO UPDATE SET status = excluded.status, "
            "expires_on = excluded.expires_on",
            (customer_id, status.value, expires_on.isoformat()),
        )

    def get_customer(self, customer_id: int) -> Customer | None:
        rows = self._customers("c.id = ?", (customer_id,))
        return rows[0] if rows else None

    def customers_by_phone(self, phone: str) -> list[Customer]:
        """Confirmed customers on this number: the ones caller ID and lookups may match."""
        return self._customers("c.phone = ? AND c.confirmed = 1", (phone,))

    def _customers(self, where: str, params: tuple) -> list[Customer]:
        rows = self.conn.execute(
            "SELECT c.*, m.status AS membership, m.expires_on FROM customers c "
            f"LEFT JOIN memberships m ON m.customer_id = c.id WHERE {where} ORDER BY c.id",
            params,
        ).fetchall()
        return [
            Customer(
                id=r["id"],
                first_name=r["first_name"],
                last_name=r["last_name"],
                phone=r["phone"],
                address=r["address"],
                zip=r["zip"],
                county=r["county"],
                membership=Membership(r["membership"] or "none"),
                membership_expires=date.fromisoformat(r["expires_on"]) if r["expires_on"] else None,
            )
            for r in rows
        ]

    # Appointments

    def count_booked(self, county: str, day: date, pool: Pool, window: str | None = None) -> int:
        sql = (
            "SELECT count(*) FROM appointments "
            # A held appointment keeps its seat until the dispatcher releases it.
            "WHERE county = ? AND day = ? AND pool = ? AND status IN ('booked', 'on_hold')"
        )
        params: list[Any] = [county, day.isoformat(), pool.value]
        if window is not None:
            sql += " AND arrival_window = ?"
            params.append(window)
        return self.conn.execute(sql, params).fetchone()[0]

    def insert_appointment(
        self,
        *,
        customer_id: int,
        call_id: str | None,
        county: str,
        day: date,
        window: str,
        pool: Pool,
        job_type: str,
        priority: Priority,
        service_address: str,
        contact_name: str,
        contact_phone: str,
        notes: str = "",
    ) -> int:
        return self._insert(
            "INSERT INTO appointments (customer_id, call_id, county, day, arrival_window, pool, "
            "job_type, priority, service_address, contact_name, contact_phone, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                customer_id, call_id, county, day.isoformat(), window, pool.value, job_type,
                int(priority), service_address, contact_name, contact_phone, notes,
            ),
        )  # fmt: skip

    def set_appointment_status(self, appointment_id: int, status: str) -> None:
        self.conn.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id))

    def cancel_appointment(self, appointment_id: int) -> bool:
        """Booked -> cancelled, only if it's still booked."""
        cur = self.conn.execute(
            "UPDATE appointments SET status = 'cancelled' WHERE id = ? AND status = 'booked'",
            (appointment_id,),
        )
        return cur.rowcount == 1

    def mark_moved(self, appointment_id: int) -> bool:
        """Booked -> moved, only if it's still booked. False if another call got there first."""
        cur = self.conn.execute(
            "UPDATE appointments SET status = 'moved' WHERE id = ? AND status = 'booked'", (appointment_id,)
        )
        return cur.rowcount == 1

    def hold_appointment(self, appointment_id: int, reason: str) -> bool:
        """Put a booked appointment on hold for the dispatcher. False if it wasn't booked."""
        cur = self.conn.execute(
            "UPDATE appointments SET status = 'on_hold', priority = 0, notes = ? || ' ' || notes "
            "WHERE id = ? AND status = 'booked'",
            (f"ON HOLD: {reason}.", appointment_id),
        )
        return cur.rowcount == 1

    def get_appointment(self, appointment_id: int) -> Appointment | None:
        row = self.conn.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,)).fetchone()
        return _appointment(row) if row else None

    def upcoming_appointments(self, customer_id: int, today: date) -> list[Appointment]:
        rows = self.conn.execute(
            "SELECT * FROM appointments WHERE customer_id = ? AND status = 'booked' AND day >= ? "
            "ORDER BY day, arrival_window",
            (customer_id, today.isoformat()),
        ).fetchall()
        return [_appointment(r) for r in rows]

    # Calls, alerts, callbacks

    def upsert_call(
        self,
        call_id: str,
        *,
        caller_id: str | None,
        started_at: datetime,
        record: dict[str, Any],
        transcript: list[dict[str, Any]] | None = None,
        priority: Priority | None = None,
        outcome: str | None = None,
        summary: str | None = None,
        ended_at: datetime | None = None,
        last_seen: datetime | None = None,
    ) -> None:
        # A call once ended stays ended: a late save from its worker can't reopen it.
        self.conn.execute(
            "INSERT INTO calls (id, caller_id, started_at, ended_at, last_seen, priority, outcome, summary, "
            "record, transcript) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT (id) DO UPDATE SET ended_at = COALESCE(calls.ended_at, excluded.ended_at), "
            "last_seen = excluded.last_seen, "
            "priority = excluded.priority, outcome = excluded.outcome, summary = excluded.summary, "
            "record = excluded.record, "
            "transcript = CASE WHEN excluded.transcript = '[]' THEN calls.transcript "
            "ELSE excluded.transcript END",
            (
                call_id,
                caller_id,
                started_at.isoformat(),
                ended_at.isoformat() if ended_at else None,
                (last_seen or started_at).isoformat(),
                int(priority) if priority is not None else None,
                outcome,
                summary,
                json.dumps(record, default=str),
                json.dumps(transcript or [], default=str),
            ),
        )

    def get_call(self, call_id: str) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT * FROM calls WHERE id = ?", (call_id,)).fetchone()
        if row is None:
            return None
        call = dict(row)
        call["record"] = json.loads(call["record"])
        call["transcript"] = json.loads(call["transcript"])
        return call

    def open_calls_silent_since(self, cutoff: datetime) -> list[dict[str, Any]]:
        """Calls with no end time whose last save was before `cutoff`. A live call saves on
        every line and tool call (and the silence check hangs up within a minute), so one
        that has gone quiet this long lost its worker. A long call that is still talking
        keeps its heartbeat fresh and is left alone."""
        # Compared as datetimes, not strings: an ISO string's UTC offset changes with DST.
        rows = self.conn.execute("SELECT * FROM calls WHERE ended_at IS NULL").fetchall()
        return [
            {**dict(r), "record": json.loads(r["record"])}
            for r in rows
            if datetime.fromisoformat(r["last_seen"] or r["started_at"]) < cutoff
        ]

    def close_call(self, call_id: str, outcome: str, ended_at: datetime) -> None:
        self.conn.execute(
            "UPDATE calls SET outcome = ?, ended_at = ? WHERE id = ? AND ended_at IS NULL",
            (outcome, ended_at.isoformat(), call_id),
        )

    def add_alert(self, call_id: str | None, severity: str, summary: str) -> int:
        return self._insert(
            "INSERT INTO alerts (call_id, severity, summary) VALUES (?, ?, ?)",
            (call_id, severity, summary),
        )

    def acknowledge_alert(self, alert_id: int) -> None:
        self.conn.execute("UPDATE alerts SET acknowledged = 1 WHERE id = ?", (alert_id,))

    def alerts_for_call(self, call_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute("SELECT * FROM alerts WHERE call_id = ? ORDER BY id", (call_id,)).fetchall()
        return [dict(r) for r in rows]

    def add_callback(
        self,
        call_id: str | None,
        phone: str,
        reason: str,
        due_at: datetime,
        urgent: bool = False,
        name: str | None = None,
    ) -> int:
        return self._insert(
            "INSERT INTO callbacks (call_id, phone, name, reason, urgent, due_at) VALUES (?, ?, ?, ?, ?, ?)",
            (call_id, phone, name, reason, int(urgent), due_at.isoformat()),
        )

    def callbacks_for_call(self, call_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM callbacks WHERE call_id = ? ORDER BY id", (call_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    def appointments_for_call(self, call_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM appointments WHERE call_id = ? ORDER BY id", (call_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def _appointment(row: sqlite3.Row) -> Appointment:
    return Appointment(
        id=row["id"],
        customer_id=row["customer_id"],
        county=row["county"],
        day=date.fromisoformat(row["day"]),
        window=row["arrival_window"],
        pool=Pool(row["pool"]),
        job_type=row["job_type"],
        priority=Priority(row["priority"]),
        service_address=row["service_address"],
        status=row["status"],
    )
