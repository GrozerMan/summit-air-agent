"""Names read back, confirmation numbers, the caller's own availability, and the
office taking over after repeated failed bookings."""

import pytest
from test_backend import GOOD_BOOKING, ready_to_book

from summit.backend import ActionRefused
from summit.models import Priority
from summit.scheduling import window_bounds
from summit.triage import Facts

# Names


def test_a_name_that_was_never_read_back_is_refused(make_call):
    call = make_call(None)
    option = ready_to_book(call)
    call.agent_said = "That's 631-555-0123 at 9 Birch Court, Huntington. Right?"
    with pytest.raises(ActionRefused, match="name back"):
        call.book_appointment(option, **GOOD_BOOKING)


def test_a_spelled_name_counts_as_read_back(make_call):
    call = make_call(None)
    option = ready_to_book(call)
    call.agent_said = (
        "That's S-A-M, and Ortiz is O R T I Z? 631-555-0123, at 9 Birch Court, Huntington. Right?"
    )
    assert call.book_appointment(option, **GOOD_BOOKING).startswith("Booked")


def test_a_misheard_name_read_back_is_refused(make_call):
    # The transcriber heard "Ortiz" as "Ortez"; the agent read back what it heard.
    call = make_call(None)
    option = ready_to_book(call)
    call.agent_said = "That's Sam Ortez, 631-555-0123 at 9 Birch Court, Huntington. Right?"
    with pytest.raises(ActionRefused, match="name back"):
        call.book_appointment(option, **GOOD_BOOKING)


def test_the_caller_saying_no_to_the_name_is_refused(make_call):
    call = make_call(None)
    option = ready_to_book(call)
    with pytest.raises(ActionRefused, match="name back"):
        call.book_appointment(option, **{**GOOD_BOOKING, "name_read_back_confirmed": False})


def test_a_verified_customer_needs_no_name_read_back(member_call):
    member_call.lookup_customer(confirmed_name=True)
    member_call.assess_situation(Facts(request_type="tune_up", description="tune-up"))
    member_call.check_service_address(zip_code="11501", property_type="house")
    member_call.find_appointment_options()
    option = next(iter(member_call.offered))
    member_call.agent_said = "That's 516-555-0142, at 12 Elm Street, Mineola. Right?"
    booking = {**GOOD_BOOKING, "first_name": "Dana", "last_name": "Reyes", "phone": "516-555-0142",
               "address": "12 Elm Street, Mineola", "zip_code": "11501"}  # fmt: skip
    assert member_call.book_appointment(option, **booking).startswith("Booked")


# Confirmation number


def test_the_confirmation_gives_the_appointment_number(make_call):
    call = make_call(None)
    option = ready_to_book(call)
    call.book_appointment(option, **GOOD_BOOKING)
    appointment_id = call.booked[-1]
    spoken = " ".join(f"{appointment_id:04d}")
    assert f"Your confirmation number is {spoken}." in call.take_announcement()


# The caller's availability


def ready_for_times(call, facts=None):
    call.assess_situation(facts or Facts(request_type="tune_up", description="tune-up"))
    call.check_service_address(zip_code="11743", property_type="house")


def test_only_windows_inside_the_callers_hours_are_offered(make_call):
    call = make_call(None)
    ready_for_times(call)
    result = call.find_appointment_options(caller_says_member=False, after_time="14:00")
    assert call.offered and "Nothing open fits" not in result
    for option in call.offered.values():
        assert window_bounds(option.window)[0].hour >= 14


def test_days_and_mornings_narrow_the_windows(make_call):
    call = make_call(None)
    ready_for_times(call)
    call.find_appointment_options(caller_says_member=False, days=["thursday", "friday"], before_time="12pm")
    assert call.offered
    for option in call.offered.values():
        assert option.day.strftime("%A") in ("Thursday", "Friday")
        assert window_bounds(option.window)[1].hour <= 12
    assert any(n.startswith("caller availability: Thursday or Friday, before noon") for n in call.notes)


def test_not_before_a_date(make_call):
    call = make_call(None)
    ready_for_times(call)
    call.find_appointment_options(caller_says_member=False, not_before="2026-11-10")
    assert call.offered and all(o.day.isoformat() >= "2026-11-10" for o in call.offered.values())


def test_nothing_fitting_offers_the_nearest_and_says_so(make_call):
    # Sundays only: routine work never goes out on a Sunday.
    call = make_call(None)
    ready_for_times(call)
    result = call.find_appointment_options(caller_says_member=False, days=["sunday"])
    assert result.startswith("Nothing open fits what they said (Sunday)")
    assert call.offered


def test_unreadable_availability_is_refused_with_the_format(make_call):
    call = make_call(None)
    ready_for_times(call)
    with pytest.raises(ActionRefused, match="HH:MM"):
        call.find_appointment_options(caller_says_member=False, after_time="after lunch")
    with pytest.raises(ActionRefused, match="YYYY-MM-DD"):
        call.find_appointment_options(caller_says_member=False, days=["someday"])


def test_an_urgent_call_is_still_offered_its_24_hour_windows(make_call):
    call = make_call(None)
    ready_for_times(call, Facts(no_heat=True, vulnerable_occupant=True, description="no heat"))
    assert call.priority == Priority.P1
    result = call.find_appointment_options(caller_says_member=False, days=["2026-11-20"])
    assert "has to be within 24 hours" in result and call.offered


# The office takes over after repeated failures


def test_three_failed_bookings_set_a_callback_once(make_call, seeded):
    call = make_call("+16315550123")
    option = ready_to_book(call)
    bad = {**GOOD_BOOKING, "phone_read_back_confirmed": False}
    for _ in range(2):
        with pytest.raises(ActionRefused) as refused:
            call.book_appointment(option, **bad)
        assert "callback is now set" not in str(refused.value)
    with pytest.raises(ActionRefused, match="callback is now set"):
        call.book_appointment(option, **bad)
    with pytest.raises(ActionRefused) as refused:
        call.book_appointment(option, **bad)
    assert "callback is now set" not in str(refused.value)
    assert len(seeded.callbacks_for_call("call-1")) == 1
    assert any("couldn't complete a booking" in a["summary"] for a in seeded.alerts_for_call("call-1"))
    # The caller can still go on and book.
    assert call.book_appointment(option, **GOOD_BOOKING).startswith("Booked")


def test_a_success_resets_the_count(make_call):
    call = make_call(None)
    option = ready_to_book(call)
    for _ in range(2):
        with pytest.raises(ActionRefused):
            call.book_appointment(option, **{**GOOD_BOOKING, "phone_read_back_confirmed": False})
    call.book_appointment(option, **GOOD_BOOKING)
    assert call.booking_failures == 0
