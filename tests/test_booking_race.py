import contextlib
import threading
import time

import pytest
from conftest import TUESDAY_10AM

from summit import config
from summit.models import Pool, Priority
from summit.scheduling import Scheduler
from summit.seed import seed
from summit.store import Store


def _race_for_last_seat(path, racers=4):
    """Fill a window to one seat, then have `racers` separate connections book it at once.
    Returns how many got it."""
    cfg = config.load()
    seed(Store(path), today=TUESDAY_10AM.date())
    scheduler = Scheduler(Store(path), cfg)
    option = next(
        o
        for o in scheduler.find_options("Suffolk", Priority.P3, False, TUESDAY_10AM, limit=20)
        if o.pool == Pool.REGULAR
    )
    while scheduler.seats_left(option.county, option.day, option.window, option.pool) > 1:
        scheduler.book(option, **_appointment("filler"))
    results = []
    start = threading.Barrier(racers)

    def book(k):
        own = Scheduler(Store(path), cfg)
        start.wait()
        results.append(own.book(option, **_appointment(f"r{k}")))

    threads = [threading.Thread(target=book, args=(k,)) for k in range(racers)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return sum(r is not None for r in results)


def test_the_lock_is_what_prevents_overbooking(tmp_path, monkeypatch):
    """DECISIONS 11 says this race fails without BEGIN IMMEDIATE. Take the lock away (and widen
    the gap between the seat check and the insert, as a slow disk would) and it does."""
    monkeypatch.setattr(Store, "write_lock", lambda self: contextlib.nullcontext(self.conn))
    real_seats_left = Scheduler.seats_left

    def slow_seats_left(self, *args):
        seats = real_seats_left(self, *args)
        time.sleep(0.01)
        return seats

    monkeypatch.setattr(Scheduler, "seats_left", slow_seats_left)
    overbooked = sum(_race_for_last_seat(tmp_path / f"nolock{i}.db") > 1 for i in range(5))
    assert overbooked > 0


def test_with_the_lock_a_four_way_race_has_one_winner(tmp_path):
    assert all(_race_for_last_seat(tmp_path / f"lock{i}.db") == 1 for i in range(5))


@pytest.mark.parametrize("run", range(5))
def test_two_calls_moving_the_same_appointment_move_it_once(tmp_path, run):
    """Stress report H9: both calls used to pass the 'still booked?' check outside the
    lock and both insert, leaving two booked rows for one original."""
    from summit.backend import ActionRefused, CallSession
    from summit.seed import DEMO_MEMBER_PHONE

    cfg = config.load()
    path = tmp_path / "move.db"
    seed(Store(path), today=TUESDAY_10AM.date())
    calls = []
    for k in range(2):
        call = CallSession(f"mv{k}", DEMO_MEMBER_PHONE, Store(path), cfg, clock=lambda: TUESDAY_10AM)
        call.prefetch_caller()
        call.lookup_customer(confirmed_name=True)
        call.find_appointment_options(reschedule_appointment_id=1)
        calls.append((call, list(call.offered)[k]))
    start = threading.Barrier(2)
    outcomes = []

    def move(call, option_id):
        start.wait()
        try:
            call.change_appointment(1, option_id)
            outcomes.append("moved")
        except ActionRefused:
            outcomes.append("refused")

    threads = [threading.Thread(target=move, args=c) for c in calls]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    booked = Store(path).conn.execute(
        "SELECT count(*) FROM appointments WHERE customer_id = 1 AND status = 'booked'"
    ).fetchone()[0]
    assert booked == 1 and sorted(outcomes) == ["moved", "refused"]


def test_last_seat_is_booked_exactly_once(tmp_path):
    """Two calls race for the last seat in a window; one wins, the other is told it's gone."""
    cfg = config.load()
    path = tmp_path / "race.db"
    seed(Store(path), today=TUESDAY_10AM.date())

    scheduler = Scheduler(Store(path), cfg)
    option = next(
        o
        for o in scheduler.find_options("Suffolk", Priority.P3, False, TUESDAY_10AM, limit=20)
        if o.pool == Pool.REGULAR
    )
    while scheduler.seats_left(option.county, option.day, option.window, option.pool) > 1:
        scheduler.book(option, **_appointment("filler"))

    results = []
    start = threading.Barrier(2)

    def book(name):
        own = Scheduler(Store(path), cfg)  # separate connection, like a separate call
        start.wait()
        results.append(own.book(option, **_appointment(name)))

    threads = [threading.Thread(target=book, args=(n,)) for n in ("first", "second")]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert sorted(r is None for r in results) == [False, True]
    assert scheduler.seats_left(option.county, option.day, option.window, option.pool) == 0


def _appointment(call_id):
    return dict(
        customer_id=1, call_id=call_id, job_type="tune-up", priority=Priority.P3,
        service_address="x", contact_name="x", contact_phone="+15165550000",
    )  # fmt: skip


def test_on_postgres_a_four_way_race_has_one_winner(pg_uri):
    # The deployed agent runs on Postgres, where the lock is an advisory lock, not BEGIN IMMEDIATE.
    from conftest import fresh_postgres

    assert _race_for_last_seat(fresh_postgres(pg_uri), racers=4) == 1
