import threading

from conftest import TUESDAY_10AM

from summit import config
from summit.models import Pool, Priority
from summit.scheduling import Scheduler
from summit.seed import seed
from summit.store import Store


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
