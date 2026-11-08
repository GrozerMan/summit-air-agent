from datetime import date, datetime, timedelta

from conftest import TUESDAY_10AM, TZ

from summit import config
from summit.models import Pool, Priority
from summit.scheduling import Scheduler, say_window, window_bounds


def start_of(option):
    return datetime.combine(option.day, window_bounds(option.window)[0], tzinfo=TZ)


def fill(store, scheduler, county, day, window, pool, n=1):
    for _ in range(n):
        store.insert_appointment(
            customer_id=1, call_id=None, county=county, day=day, window=window, pool=pool,
            job_type="test", priority=Priority.P3, service_address="x", contact_name="x",
            contact_phone="+15165550000",
        )  # fmt: skip


def fill_regular_capacity(store, scheduler, county, days):
    for day in days:
        for window in scheduler.rules["windows"]:
            n = scheduler.seats_left(county, day, window, Pool.REGULAR)
            fill(store, scheduler, county, day, window, Pool.REGULAR, n)


def test_routine_work_never_gets_same_day(seeded, cfg):
    options = Scheduler(seeded, cfg).find_options("Nassau", Priority.P3, False, TUESDAY_10AM)
    assert options and all(o.day > TUESDAY_10AM.date() for o in options)


def test_urgent_work_can_go_out_today(seeded, cfg):
    options = Scheduler(seeded, cfg).find_options("Suffolk", Priority.P1, False, TUESDAY_10AM)
    assert options[0].day == TUESDAY_10AM.date()


def test_windows_start_after_the_lead_time(seeded, cfg):
    options = Scheduler(seeded, cfg).find_options("Nassau", Priority.P1, False, TUESDAY_10AM)
    assert all(start_of(o) >= TUESDAY_10AM + timedelta(minutes=60) for o in options)


def test_p1_uses_the_emergency_reserve_when_regular_is_full(seeded, cfg):
    scheduler = Scheduler(seeded, cfg)
    today, tomorrow = TUESDAY_10AM.date(), TUESDAY_10AM.date() + timedelta(days=1)
    fill_regular_capacity(seeded, scheduler, "Westchester", [today, tomorrow])

    options = scheduler.find_options("Westchester", Priority.P1, False, TUESDAY_10AM)
    assert options and all(o.pool == Pool.EMERGENCY for o in options)


def test_p2_cannot_touch_the_emergency_reserve(seeded, cfg):
    scheduler = Scheduler(seeded, cfg)
    days = [TUESDAY_10AM.date() + timedelta(days=n) for n in range(15)]
    fill_regular_capacity(seeded, scheduler, "Westchester", days)

    assert scheduler.find_options("Westchester", Priority.P2, False, TUESDAY_10AM) == []


def test_member_capacity_is_for_members_only(seeded, cfg):
    scheduler = Scheduler(seeded, cfg)
    tomorrow = TUESDAY_10AM.date() + timedelta(days=1)
    fill_regular_capacity(seeded, scheduler, "Suffolk", [tomorrow])

    member = scheduler.find_options("Suffolk", Priority.P3, True, TUESDAY_10AM)
    non_member = scheduler.find_options("Suffolk", Priority.P3, False, TUESDAY_10AM)
    assert member[0].day == tomorrow and member[0].pool == Pool.MEMBER
    assert all(o.day != tomorrow for o in non_member)


def test_p1_never_offers_beyond_24_hours(seeded, cfg):
    options = Scheduler(seeded, cfg).find_options("Nassau", Priority.P1, False, TUESDAY_10AM)
    assert options
    assert all(start_of(o) < TUESDAY_10AM + timedelta(hours=24) for o in options)


def test_sunday_is_only_for_urgent_work(seeded, cfg):
    saturday_evening = datetime(2026, 11, 7, 19, 0, tzinfo=TZ)
    scheduler = Scheduler(seeded, cfg)
    sunday = date(2026, 11, 8)
    assert all(
        o.day != sunday for o in scheduler.find_options("Nassau", Priority.P2, False, saturday_evening)
    )
    urgent = scheduler.find_options("Nassau", Priority.P1, False, saturday_evening)
    assert urgent[0].day == sunday and urgent[0].after_hours


def test_simulated_load_is_deterministic(store, cfg):
    a, b = Scheduler(store, cfg), Scheduler(store, cfg)
    day = date(2026, 11, 4)
    loads = [a.simulated_load("Nassau", day, w) for w in cfg["scheduling"]["windows"]]
    assert loads == [b.simulated_load("Nassau", day, w) for w in cfg["scheduling"]["windows"]]


def test_booking_takes_a_seat(seeded, cfg):
    scheduler = Scheduler(seeded, cfg)
    option = scheduler.find_options("Nassau", Priority.P3, False, TUESDAY_10AM)[0]
    before = scheduler.seats_left(option.county, option.day, option.window, option.pool)
    scheduler.book(
        option, customer_id=1, call_id="c", job_type="tune-up", priority=Priority.P3,
        service_address="x", contact_name="x", contact_phone="+15165550000",
    )  # fmt: skip
    assert scheduler.seats_left(option.county, option.day, option.window, option.pool) == before - 1


def test_window_phrasing():
    assert say_window("08:00-10:00") == "between 8 and 10 AM"
    assert say_window("10:00-12:00") == "between 10 AM and noon"
    assert say_window("12:00-14:00") == "between noon and 2 PM"
    assert say_window("16:00-18:00") == "between 4 and 6 PM"


def test_routine_work_skips_thanksgiving(cfg, seeded):
    wed_3pm = datetime(2026, 11, 25, 15, 0, tzinfo=TZ)
    options = Scheduler(seeded, cfg).find_options("Nassau", Priority.P3, False, wed_3pm, limit=10)
    assert options and all(o.day.isoformat() != "2026-11-26" for o in options)


def test_the_office_is_closed_on_a_holiday(cfg):
    thanksgiving_noon = datetime(2026, 11, 26, 12, 0, tzinfo=TZ)
    assert not config.office_open(cfg, thanksgiving_noon)
    assert config.next_office_opening(cfg, thanksgiving_noon).day == 27
