from datetime import datetime, timedelta

import pytest
from conftest import TUESDAY_10AM, TZ

from summit.backend import ActionRefused, caller_turn_to_screen
from summit.models import Priority
from summit.seed import SHARED_HOUSEHOLD_PHONE
from summit.triage import Facts

GOOD_BOOKING = dict(
    first_name="Sam",
    last_name="Ortiz",
    phone="631-555-0123",
    address="9 Birch Court, Huntington",
    zip_code="11743",
    job_type="no heat",
    notes="",
    phone_read_back_confirmed=True,
    address_read_back_confirmed=True,
)


def ready_to_book(call, facts=None, zip_code="11743"):
    call.assess_situation(facts or Facts(no_heat=True, indoor_temp_f=64, vulnerable_occupant=False))
    call.check_service_address(zip_code=zip_code, property_type="house")
    call.find_appointment_options()
    return next(iter(call.offered))


# Identity


def test_caller_id_match_is_greeted_by_name_but_not_verified(member_call):
    assert "Am I speaking with Dana?" in member_call.greeting()
    assert member_call.customer is None


def test_confirming_the_name_verifies(member_call):
    result = member_call.lookup_customer(confirmed_name=True)
    assert result.startswith("Verified")
    assert member_call.is_member


def test_nothing_is_revealed_without_verification(make_call):
    call = make_call("+15165550142")
    with pytest.raises(ActionRefused):
        call.lookup_customer()
    result = call.lookup_customer(phone="516-555-0142", last_name="Somebody")
    assert "Elm" not in result and "member" not in result.lower()


def test_phone_plus_last_name_verifies(make_call):
    call = make_call(None)
    assert call.lookup_customer(phone="914 555 0188", last_name="klein").startswith("Verified")
    assert "lapsed" in call.lookup_customer()


def test_shared_phone_does_not_guess_a_name(make_call):
    call = make_call(SHARED_HOUSEHOLD_PHONE)
    assert "Am I speaking" not in call.greeting()
    with pytest.raises(ActionRefused, match="first name"):
        call.lookup_customer(last_name="Walsh")
    assert "Ann Walsh" in call.lookup_customer(last_name="Walsh", first_name="Ann")


def test_saying_no_to_the_name_drops_the_match(member_call):
    member_call.lookup_customer(confirmed_name=False, last_name="Reyes")
    assert member_call.caller_match is None


# Triage through the session


def test_priority_never_goes_down_within_a_call(make_call):
    call = make_call(None)
    call.assess_situation(Facts(no_heat=True, indoor_temp_f=55))
    call.assess_situation(Facts(indoor_temp_f=65))
    assert call.priority == Priority.P1


def test_gas_mention_raises_critical_alert_with_script(make_call, seeded):
    call = make_call("+16315550177")
    result = call.assess_situation(Facts(gas_smell=True))
    assert "word for word" in result
    assert "National Grid at one, eight hundred, four nine zero, zero zero four five" in result
    assert seeded.alerts_for_call("call-1")[0]["severity"] == "critical"
    assert call.outcome == "safety_emergency"


def test_p1_after_hours_pages_on_call(make_call, seeded):
    call = make_call(None, now=datetime(2026, 11, 3, 22, 0, tzinfo=TZ))
    result = call.assess_situation(Facts(no_cooling=True, indoor_temp_f=90))
    assert "on-call" in result
    assert "page on-call" in seeded.alerts_for_call("call-1")[0]["summary"]


# Scheduling refusals


def test_no_options_before_triage(make_call):
    call = make_call(None)
    call.check_service_address(zip_code="11743", property_type="house")
    with pytest.raises(ActionRefused, match="assess_situation"):
        call.find_appointment_options()


def test_no_options_on_p0(make_call):
    call = make_call(None)
    call.check_service_address(zip_code="11743", property_type="house")
    call.assess_situation(Facts(co_alarm_or_symptoms=True))
    with pytest.raises(ActionRefused, match="safety emergency"):
        call.find_appointment_options()


def test_no_options_out_of_area(make_call):
    call = make_call(None)
    call.assess_situation(Facts(request_type="tune_up"))
    call.check_service_address(zip_code="11215", property_type="house")
    with pytest.raises(ActionRefused, match="service address"):
        call.find_appointment_options()
    assert call.outcome == "out_of_area"


def test_commercial_caller_is_a_lead_not_a_booking(make_call):
    call = make_call(None)
    call.assess_situation(Facts(no_cooling=True))
    result = call.check_service_address(zip_code="11743", property_type="restaurant")
    assert "callback" in result
    with pytest.raises(ActionRefused, match="Commercial"):
        call.find_appointment_options()
    call.request_callback("631 555 0100", "commercial lead: rooftop unit down")
    assert call.outcome == "commercial_lead"


# Booking guardrails


def test_booking_lists_every_missing_field(make_call):
    call = make_call(None)
    option = ready_to_book(call)
    with pytest.raises(ActionRefused) as refused:
        call.book_appointment(option, **{**GOOD_BOOKING, "last_name": "", "address": " "})
    assert "last name" in str(refused.value) and "street address" in str(refused.value)


def test_booking_requires_both_read_backs(make_call):
    call = make_call(None)
    option = ready_to_book(call)
    with pytest.raises(ActionRefused) as refused:
        call.book_appointment(
            option,
            **{**GOOD_BOOKING, "phone_read_back_confirmed": False, "address_read_back_confirmed": False},
        )
    assert "phone number back" in str(refused.value) and "address back" in str(refused.value)


def test_booking_rejects_a_zip_that_was_not_checked(make_call):
    call = make_call(None)
    option = ready_to_book(call)
    with pytest.raises(ActionRefused, match="doesn't match"):
        call.book_appointment(option, **{**GOOD_BOOKING, "zip_code": "11746"})


def test_booking_rejects_an_option_that_was_not_offered(make_call):
    call = make_call(None)
    ready_to_book(call)
    with pytest.raises(ActionRefused, match="wasn't offered"):
        call.book_appointment("SUF-1225-0800-R", **GOOD_BOOKING)


def test_good_booking_goes_through_and_creates_the_customer(make_call, seeded):
    call = make_call(None)
    option = ready_to_book(call)
    result = call.book_appointment(option, **GOOD_BOOKING)
    assert result.startswith("Booked")
    assert "Summit Comfort Club" in result
    assert seeded.customers_by_phone("+16315550123")[0].last_name == "Ortiz"
    assert call.outcome == "booked"


def test_unverified_booking_does_not_overwrite_the_account(make_call, seeded):
    call = make_call("+15165550142")
    option = ready_to_book(call, zip_code="11501")
    call.book_appointment(
        option,
        **{
            **GOOD_BOOKING,
            "first_name": "Chris",
            "phone": "516-555-0142",
            "address": "1 Other St",
            "zip_code": "11501",
        },
    )
    dana = seeded.customers_by_phone("+15165550142")
    assert len(dana) == 1 and dana[0].first_name == "Dana" and dana[0].address.startswith("12 Elm")
    appointment = seeded.appointments_for_call("call-1")[0]
    assert appointment["contact_name"] == "Chris Ortiz" and appointment["customer_id"] == dana[0].id


def test_unverified_caller_gets_non_member_pricing(make_call):
    call = make_call("+15165550142")
    assert "$129" in call.get_pricing("diagnostic visit")
    call.lookup_customer(confirmed_name=True)
    assert "free for members" in call.get_pricing("diagnostic visit")


def test_slot_taken_between_offer_and_booking_is_re_offered(make_call, seeded):
    call = make_call(None)
    option_id = ready_to_book(call)
    option = call.offered[option_id]
    while call.scheduler.seats_left(option.county, option.day, option.window, option.pool) > 0:
        call.scheduler.book(
            option, customer_id=1, call_id="other", job_type="x", priority=Priority.P2,
            service_address="x", contact_name="x", contact_phone="+15165550000",
        )  # fmt: skip
    with pytest.raises(ActionRefused, match="just taken"):
        call.book_appointment(option_id, **GOOD_BOOKING)
    assert option_id not in call.offered


def test_reschedule_releases_the_old_window(member_call, seeded):
    member_call.lookup_customer(confirmed_name=True)
    old = seeded.upcoming_appointments(member_call.customer.id, TUESDAY_10AM.date())[0]
    member_call.find_appointment_options(reschedule_appointment_id=old.id)
    new_option = next(o for o in member_call.offered if o != old.id)
    result = member_call.change_appointment(old.id, new_option)
    assert result.startswith("Moved")
    assert seeded.get_appointment(old.id).status == "moved"
    assert member_call.outcome == "rescheduled"


def test_cannot_touch_someone_elses_appointment(make_call, seeded):
    call = make_call(None)
    call.lookup_customer(phone="631 555 0177", last_name="Shah")
    with pytest.raises(ActionRefused, match="isn't an upcoming appointment"):
        call.find_appointment_options(reschedule_appointment_id=1)


# Escalation and pricing


def test_no_transfer_number_means_an_honest_callback(make_call, cfg):
    call = make_call(None)
    number, message = call.plan_transfer()
    assert number is None and "callback" in message


def test_transfer_only_while_the_office_is_open(make_call, cfg, monkeypatch):
    monkeypatch.setitem(cfg["escalation"], "human_transfer_number", "+15165550100")
    assert make_call(None).plan_transfer()[0] == "+15165550100"
    night = make_call(None, now=TUESDAY_10AM.replace(hour=21))
    assert night.plan_transfer()[0] is None


def test_urgent_callback_is_due_in_30_minutes_and_alerts(make_call, seeded):
    call = make_call(None)
    result = call.request_callback("516 555 0111", "wants a person", urgent=True)
    assert "within 30 minutes" in result
    due = datetime.fromisoformat(seeded.callbacks_for_call("call-1")[0]["due_at"])
    assert due == TUESDAY_10AM + timedelta(minutes=30)
    assert seeded.alerts_for_call("call-1")[0]["severity"] == "urgent"


def test_callback_needs_a_real_number(make_call):
    with pytest.raises(ActionRefused, match="10-digit"):
        make_call(None).request_callback("555", "question about a bill")


def test_repairs_are_never_estimated(make_call):
    call = make_call(None)
    for question in ("how much to fix my compressor", "what will the repair cost", "rattling noise"):
        assert "Don't estimate" in call.get_pricing(question)
    assert "$159" in call.get_pricing("tune-up")
    assert "free" in call.get_pricing("replacement estimate")


# Hang-up


def test_unbooked_triaged_call_becomes_a_callback(make_call, seeded):
    call = make_call("+16315550177")
    call.assess_situation(Facts(no_heat=True, indoor_temp_f=55))
    call.check_service_address(zip_code="11743", property_type="house")
    call.finalize(transcript=[{"role": "user", "text": "hello?"}])
    saved = seeded.get_call("call-1")
    assert saved["outcome"] == "callback"
    assert seeded.callbacks_for_call("call-1")[0]["urgent"] == 1
    assert saved["transcript"][0]["text"] == "hello?"


def test_every_tool_call_is_saved_as_it_happens(make_call, seeded):
    call = make_call(None)
    call.log_tool("check_service_address", {"zip_code": "11743"}, "ok")
    assert seeded.get_call("call-1")["record"]["tools"][0]["tool"] == "check_service_address"


def test_out_of_area_town_without_a_zip_is_recorded(make_call):
    call = make_call(None)
    call.check_service_address(town="Hoboken", property_type="house")
    assert call.outcome == "out_of_area"


def test_turning_away_never_overwrites_a_safety_emergency(make_call):
    call = make_call(None)
    call.assess_situation(Facts(gas_smell=True))
    call.check_service_address(zip_code="11215", property_type="house")
    assert call.outcome == "safety_emergency"


# The caller's own words (test call P0-01)

P0_01_TURN = (
    "So we've got this smell coming from our furnace. It's kinda like a skunk. "
    "It's pretty nasty. It happened earlier today. But now it's gone."
)


def test_gas_words_make_the_call_p0_before_the_model_answers(make_call, seeded):
    call = make_call("+16315550177")
    said = call.screen_caller_turn(P0_01_TURN)
    assert call.priority == Priority.P0
    assert said and "leave the house now" in said
    assert seeded.alerts_for_call("call-1")[0]["severity"] == "critical"
    assert call.outcome == "safety_emergency"
    assert call.tool_log[-1]["tool"] == "hazard_screen"


def test_p0_01_replayed_never_reaches_scheduling(make_call):
    # Same tool calls the model made on the failed call, in the same order.
    call = make_call("+16466790972")
    call.screen_caller_turn(P0_01_TURN)
    call.assess_situation(
        Facts(gas_smell=False, description="nasty skunk-like smell from furnace earlier but now gone")
    )
    call.check_service_address(zip_code="11001", property_type="house")
    with pytest.raises(ActionRefused, match="safety emergency"):
        call.find_appointment_options()
    assert call.priority == Priority.P0


def test_model_triage_alone_catches_p0_01(make_call):
    # Even without the screen, the model's own description now carries the call to P0.
    call = make_call("+16466790972")
    result = call.assess_situation(
        Facts(gas_smell=False, description="nasty skunk-like smell from furnace earlier but now gone")
    )
    assert "SAFETY EMERGENCY" in result


def test_smell_after_times_were_offered_voids_them(make_call):
    call = make_call(None)
    call.assess_situation(Facts(request_type="tune_up", description="fall tune-up"))
    call.check_service_address(zip_code="11743", property_type="house")
    offered = call.find_appointment_options()
    option_id = offered.split("\n")[1].split(":")[0].lstrip("- ")
    call.screen_caller_turn("oh and actually it smelled like rotten eggs this morning")
    assert call.offered == {}
    with pytest.raises(ActionRefused, match="safety emergency"):
        call.book_appointment(
            option_id, "Jen", "Morales", "6315550155", "33 Shore Road, Huntington", "11743",
            "tune-up", "", True, True,
        )  # fmt: skip


def test_no_rescheduling_during_an_emergency(member_call):
    member_call.lookup_customer(confirmed_name=True)
    member_call.screen_caller_turn("I smell gas")
    with pytest.raises(ActionRefused, match="safety emergency"):
        member_call.find_appointment_options(reschedule_appointment_id=1)
    with pytest.raises(ActionRefused, match="safety emergency"):
        member_call.change_appointment(1, "anything")


def test_safety_script_is_read_once(make_call):
    call = make_call(None)
    script = call.screen_caller_turn("rotten egg smell")
    assert call.screen_caller_turn("it smells like rotten eggs still", said_so_far=script) is None


def test_script_is_reread_if_the_model_paraphrased_it(make_call):
    call = make_call(None)
    call.assess_situation(Facts(gas_smell=True))  # model-triggered; it then paraphrases
    again = call.screen_caller_turn("okay", said_so_far="You should leave, call 911.")
    assert again == call.safety_script()


def test_cannot_leave_gets_the_fixed_answer(make_call):
    call = make_call(None)
    script = call.screen_caller_turn("smelled like a skunk earlier")
    reply = call.screen_caller_turn(
        "It's kinda dark outside. And I don't feel safe leaving.", said_so_far=script
    )
    assert reply and "nine-one-one" in reply and "can't leave" in reply


def test_dusty_smell_turn_is_left_to_the_model(make_call):
    call = make_call(None)
    assert call.screen_caller_turn("dusty burning smell, first time turning heat on this year") is None
    assert call.priority is None
    assert call.emergency_note() is None


def test_emergency_note_after_p0(make_call):
    call = make_call(None)
    call.screen_caller_turn("I smell gas")
    note = call.emergency_note()
    assert note and "don't book" in note and "nine-one-one" in note


def test_unverified_caller_is_not_named_as_the_account_holder(member_call, seeded):
    member_call.screen_caller_turn("rotten eggs by the furnace")
    summary = seeded.alerts_for_call("call-1")[0]["summary"]
    assert "unverified caller; caller ID matches" in summary


class _Item:
    def __init__(self, type, role=None, text=None):
        self.type, self.role, self.text_content = type, role, text


def test_only_the_first_reply_to_a_caller_turn_is_screened():
    history = [
        _Item("message", "system", "instructions"),
        _Item("message", "assistant", "Thanks for calling."),
        _Item("message", "user", "rotten eggs"),
    ]
    assert caller_turn_to_screen(history) == ("rotten eggs", "Thanks for calling.")
    after_tool = [*history, _Item("function_call"), _Item("function_call_output")]
    assert caller_turn_to_screen(after_tool)[0] is None
    # Bookkeeping items after the caller's words don't hide them from the screen.
    with_handoff = [*history, _Item("agent_handoff")]
    assert caller_turn_to_screen(with_handoff)[0] == "rotten eggs"
