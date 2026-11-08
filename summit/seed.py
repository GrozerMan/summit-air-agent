"""Load demo customers.

    uv run python -m summit.seed --member-phone +15165550142 --member-name "Dana Reyes"

The member is you: call from that phone and the agent greets you by name.
"""

import argparse
import os
from datetime import date, datetime, timedelta

from summit import config
from summit.models import Membership, Pool, Priority
from summit.speech import normalize_phone
from summit.store import Store

DEMO_MEMBER_PHONE = "+15165550142"
SHARED_HOUSEHOLD_PHONE = "+15165550199"


def seed(
    store: Store,
    member_phone: str = DEMO_MEMBER_PHONE,
    member_name: str = "Dana Reyes",
    today: date | None = None,
) -> None:
    cfg = config.load()
    today = today or datetime.now(config.timezone(cfg)).date()
    first, _, last = member_name.partition(" ")

    member = store.add_customer(
        first, last or "Member", member_phone, "12 Elm Street, Mineola", "11501", "Nassau"
    )
    store.set_membership(member, Membership.ACTIVE, today + timedelta(days=200))

    lapsed = store.add_customer(
        "Robert", "Klein", "+19145550188", "48 Oak Lane, White Plains", "10601", "Westchester"
    )
    store.set_membership(lapsed, Membership.LAPSED, today - timedelta(days=45))

    store.add_customer("Priya", "Shah", "+16315550177", "7 Harbor Road, Huntington", "11743", "Suffolk")

    # Two people on one landline: caller ID alone can't say who's calling.
    store.add_customer(
        "Tom", "Walsh", SHARED_HOUSEHOLD_PHONE, "301 Maple Ave, Garden City", "11530", "Nassau"
    )
    store.add_customer(
        "Ann", "Walsh", SHARED_HOUSEHOLD_PHONE, "301 Maple Ave, Garden City", "11530", "Nassau"
    )

    # Something for the member to reschedule: a tune-up a few days out.
    day = _next_weekday(today + timedelta(days=2))
    store.insert_appointment(
        customer_id=member,
        call_id=None,
        county="Nassau",
        day=day,
        window="10:00-12:00",
        pool=Pool.MEMBER,
        job_type="tune-up",
        priority=Priority.P3,
        service_address="12 Elm Street, Mineola, 11501",
        contact_name=member_name,
        contact_phone=member_phone,
        notes="Seasonal tune-up.",
    )


def _next_weekday(day: date) -> date:
    while day.weekday() >= 5:
        day += timedelta(days=1)
    return day


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load demo customers (into DATABASE_URL if set, else data/summit.db)"
    )
    parser.add_argument("--member-phone", default=DEMO_MEMBER_PHONE, help="your cell, e.g. +15165550142")
    parser.add_argument("--member-name", default="Dana Reyes")
    parser.add_argument("--reset", action="store_true", help="delete the existing database first")
    args = parser.parse_args()

    phone = normalize_phone(args.member_phone)
    if phone is None:
        parser.error(f"{args.member_phone} isn't a US phone number")

    if os.getenv("DATABASE_URL"):
        store = Store()
        where = "the DATABASE_URL database"
        if args.reset:
            store.drop_all()
            store = Store()
    else:
        path = config.db_path()
        where = str(path)
        if args.reset:
            for suffix in ("", "-wal", "-shm"):
                path.with_name(path.name + suffix).unlink(missing_ok=True)
        store = Store(path)
    if store.conn.execute("SELECT count(*) FROM customers").fetchone()[0]:
        parser.error("database already has customers; pass --reset to start over")
    seed(store, phone, args.member_name)
    print(f"Seeded {where}. Call from {phone} to be greeted as {args.member_name.split()[0]}.")


if __name__ == "__main__":
    main()
