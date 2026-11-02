"""SQLite system of record.

In production this would be ServiceTitan or Housecall Pro behind the same
methods; nothing above this module should need to know the difference.
"""

import json
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
    status          TEXT NOT NULL DEFAULT 'booked' CHECK (status IN ('booked', 'moved', 'cancelled')),
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS appointments_slot ON appointments (county, day, arrival_window, pool, status);

CREATE TABLE IF NOT EXISTS calls (
    id          TEXT PRIMARY KEY,
    caller_id   TEXT,
    started_at  TEXT NOT NULL,
    ended_at    TEXT,
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


class Store:
    def __init__(self, path: Path | str | None = None) -> None:
        self.path = str(path or config.db_path())
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        # Autocommit; multi-statement writes go through write_lock() explicitly.
        self.conn = sqlite3.connect(self.path, isolation_level=None, check_same_thread=False, timeout=5)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        if self.path != ":memory:":
            self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.executescript(SCHEMA)

    def close(self) -> None:
        self.conn.close()

    @contextmanager
    def write_lock(self) -> Iterator[sqlite3.Connection]:
        """BEGIN IMMEDIATE takes the write lock up front, so a seat check and the
        insert that depends on it can't interleave with another call's booking."""
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            yield self.conn
        except BaseException:
            self.conn.execute("ROLLBACK")
            raise
        self.conn.execute("COMMIT")

    # Customers

    def add_customer(
        self, first_name: str, last_name: str, phone: str, address: str, zip_code: str, county: str
    ) -> int:
        cur = self.conn.execute(
            "INSERT INTO customers (first_name, last_name, phone, address, zip, county) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (first_name, last_name, phone, address, zip_code, county),
        )
        return cur.lastrowid

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
        return self._customers("c.phone = ?", (phone,))

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
            "WHERE county = ? AND day = ? AND pool = ? AND status = 'booked'"
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
        cur = self.conn.execute(
            "INSERT INTO appointments (customer_id, call_id, county, day, arrival_window, pool, "
            "job_type, priority, service_address, contact_name, contact_phone, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                customer_id, call_id, county, day.isoformat(), window, pool.value, job_type,
                int(priority), service_address, contact_name, contact_phone, notes,
            ),
        )  # fmt: skip
        return cur.lastrowid

    def set_appointment_status(self, appointment_id: int, status: str) -> None:
        self.conn.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id))

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
    ) -> None:
        self.conn.execute(
            "INSERT INTO calls (id, caller_id, started_at, ended_at, priority, outcome, summary, "
            "record, transcript) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT (id) DO UPDATE SET ended_at = excluded.ended_at, "
            "priority = excluded.priority, outcome = excluded.outcome, summary = excluded.summary, "
            "record = excluded.record, "
            "transcript = CASE WHEN excluded.transcript = '[]' THEN calls.transcript "
            "ELSE excluded.transcript END",
            (
                call_id,
                caller_id,
                started_at.isoformat(),
                ended_at.isoformat() if ended_at else None,
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

    def add_alert(self, call_id: str | None, severity: str, summary: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO alerts (call_id, severity, summary) VALUES (?, ?, ?)",
            (call_id, severity, summary),
        )
        return cur.lastrowid

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
        cur = self.conn.execute(
            "INSERT INTO callbacks (call_id, phone, name, reason, urgent, due_at) VALUES (?, ?, ?, ?, ?, ?)",
            (call_id, phone, name, reason, int(urgent), due_at.isoformat()),
        )
        return cur.lastrowid

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
