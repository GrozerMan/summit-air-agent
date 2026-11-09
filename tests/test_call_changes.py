"""Stress report C4 and C6: the call changes after times were offered, or after a booking.

Offered windows used to stay bookable whatever happened next: a Suffolk window booked
for a White Plains address, a P3 window 46 hours out booked as P1, a window booked for
a restaurant. And gas reported after a booking left a routine ticket live."""

import sqlite3

import pytest
from conftest import TUESDAY_10AM

from summit.backend import ActionRefused
from summit.models import Priority
from summit.store import Store
from summit.triage import Facts

BOOK = dict(
    first_name="Sam", last_name="Ortiz", phone="631-555-0123", address="33 Shore Road, Bay Shore",
    zip_code="11706", job_type="tune-up", notes="",
    phone_read_back_confirmed=True, address_read_back_confirmed=True,
)  # fmt: skip


def offered_tune_up(call, zip_code="11706"):
    call.assess_situation(Facts(request_type="tune_up", description="tune-up"))
    call.check_service_address(zip_code=zip_code, property_type="house")
    call.find_appointment_options(caller_says_member=False)
    call.agent_said += f" That's Sam Ortiz, {BOOK['phone']}, at {BOOK['address']}. Right?"
    return dict(call.offered)


def test_new_county_voids_the_offered_windows(make_call):
    call = make_call(None)
    offered = offered_tune_up(call)
    result = call.check_service_address(zip_code="10601")  # White Plains, Westchester
    assert "no longer apply" in result and not call.offered
    with pytest.raises(ActionRefused, match="wasn't offered"):
        call.book_appointment(next(iter(offered)), **{**BOOK, "zip_code": "10601"})


def test_booking_rechecks_the_county_even_if_the_offer_survived(make_call):
    # Belt and braces: book_appointment checks the option against the call as it is now,
    # so a code path that forgets to void the offers still can't book across counties.
    call = make_call(None)
    offered = offered_tune_up(call)
    call.check_service_address(zip_code="10601")
    call.offered.update(offered)
    call.offered_for.update({k: None for k in offered})
    with pytest.raises(ActionRefused, match="Suffolk County and the address is now Westchester"):
        call.book_appointment(next(iter(offered)), **{**BOOK, "zip_code": "10601"})
    assert not call.store.appointments_for_call(call.call_id)


def test_same_address_again_keeps_the_offers(make_call):
    call = make_call(None)
    offered_tune_up(call)
    call.check_service_address(zip_code="11706", property_type="house")
    assert call.offered


def test_escalating_to_p1_voids_windows_offered_while_p3(make_call):
    call = make_call(None)
    offered = offered_tune_up(call)
    late = max(offered.values(), key=lambda o: (o.day, o.window))
    result = call.assess_situation(
        Facts(no_heat=True, indoor_temp_f=52, vulnerable_occupant=True, description="heat's out, mom is 90")
    )
    assert call.priority == Priority.P1 and "no longer apply" in result and not call.offered
    # And the scheduler itself says the old window doesn't fit a P1 call.
    reason = call.scheduler.still_fits(late, Priority.P1, False, TUESDAY_10AM)
    assert reason and "24 hours" in reason


def test_commercial_after_offer_cannot_book(make_call):
    call = make_call(None)
    offered = offered_tune_up(call)
    call.check_service_address(property_type="it's actually my restaurant")
    assert not call.offered
    with pytest.raises(ActionRefused):
        call.book_appointment(next(iter(offered)), **BOOK)


def test_a_reschedule_option_cannot_book_a_new_visit(member_call, seeded):
    member_call.lookup_customer(confirmed_name=True)
    old = seeded.upcoming_appointments(member_call.customer.id, TUESDAY_10AM.date())[0]
    member_call.find_appointment_options(reschedule_appointment_id=old.id)
    option_id = next(iter(member_call.offered))
    member_call.assess_situation(Facts(request_type="tune_up", description="tune-up"))
    with pytest.raises(ActionRefused, match="wasn't offered for a new visit"):
        member_call.book_appointment(option_id, **{**BOOK, "zip_code": "11501"})


# C6: gas after a booking.


def test_gas_after_booking_puts_the_booking_on_hold_and_says_so(make_call, seeded):
    call = make_call(None)
    option_id = next(iter(offered_tune_up(call)))
    call.book_appointment(option_id, **BOOK)
    appointment_id = call.booked[0]

    call.screen_caller_turn("oh, and there was a rotten egg smell in the basement this morning")

    row = seeded.get_appointment(appointment_id)
    assert row.status == "on_hold" and row.priority == Priority.P0
    notes = seeded.conn.execute("SELECT notes FROM appointments WHERE id = ?", (appointment_id,)).fetchone()[
        0
    ]
    assert notes.startswith("ON HOLD")
    alert = seeded.alerts_for_call(call.call_id)[-1]
    assert alert["severity"] == "critical" and f"#{appointment_id}" in alert["summary"]
    assert call.outcome == "safety_emergency"


def test_a_held_appointment_keeps_its_seat(make_call, seeded):
    call = make_call(None)
    option_id = next(iter(offered_tune_up(call)))
    option = call.offered[option_id]
    before = call.scheduler.seats_left(option.county, option.day, option.window, option.pool)
    call.book_appointment(option_id, **BOOK)
    call.screen_caller_turn("I smell gas")
    after = call.scheduler.seats_left(option.county, option.day, option.window, option.pool)
    assert after == before - 1  # the dispatcher decides whether to release it


def test_gas_mentions_other_upcoming_appointments_for_a_verified_customer(member_call, seeded):
    member_call.lookup_customer(confirmed_name=True)
    member_call.screen_caller_turn("there's a gas smell by the furnace")
    alert = seeded.alerts_for_call(member_call.call_id)[-1]["summary"]
    assert "also has upcoming appointment #1" in alert
    assert seeded.get_appointment(1).status == "booked"  # not this call's booking: flagged, not held


def test_old_databases_are_migrated_to_allow_on_hold(tmp_path):
    path = tmp_path / "old.db"
    old = sqlite3.connect(path)
    old.executescript(
        "CREATE TABLE appointments (id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL, call_id TEXT,"
        " county TEXT NOT NULL, day TEXT NOT NULL, arrival_window TEXT NOT NULL, pool TEXT NOT NULL,"
        " job_type TEXT NOT NULL, priority INTEGER NOT NULL, service_address TEXT NOT NULL,"
        " contact_name TEXT NOT NULL, contact_phone TEXT NOT NULL, notes TEXT NOT NULL DEFAULT '',"
        " status TEXT NOT NULL DEFAULT 'booked' CHECK (status IN ('booked', 'moved', 'cancelled')),"
        " created_at TEXT NOT NULL DEFAULT (datetime('now')));"
        "INSERT INTO appointments (customer_id, county, day, arrival_window, pool, job_type, priority,"
        " service_address, contact_name, contact_phone) VALUES"
        " (1, 'Nassau', '2026-11-05', '10:00-12:00', 'regular', 'tune-up', 3, 'x', 'x', '+15165550000');"
    )
    old.close()
    store = Store(path)
    assert store.hold_appointment(1, "test")
    assert store.get_appointment(1).status == "on_hold"
    Store(path).close()  # a second open doesn't migrate again
