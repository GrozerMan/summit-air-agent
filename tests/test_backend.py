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


def read_back(call, phone=GOOD_BOOKING["phone"], address=GOOD_BOOKING["address"]):
    """What the agent says before booking; the backend checks it was actually said."""
    call.agent_said += f" Let me read that back: {phone}, and the address is {address}. Is that right?"


def ready_to_book(call, facts=None, zip_code="11743"):
    call.assess_situation(facts or Facts(no_heat=True, indoor_temp_f=64, vulnerable_occupant=False))
    call.check_service_address(zip_code=zip_code, property_type="house")
    call.find_appointment_options()
    read_back(call)
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
    call = make_call(None)
    with pytest.raises(ActionRefused):
        call.lookup_customer()
    result = call.lookup_customer(phone="516-555-0142", last_name="Somebody", zip_code="11501")
    assert "Elm" not in result and "member" not in result.lower()


def test_the_greeting_question_must_be_answered_before_a_lookup(member_call):
    # The son who never says "no": his mother's phone, her surname and her ZIP.
    with pytest.raises(ActionRefused, match="confirmed_name"):
        member_call.lookup_customer(last_name="Reyes", zip_code="11501")
    assert member_call.customer is None


def test_another_number_needs_phone_last_name_and_zip(make_call):
    call = make_call(None)
    with pytest.raises(ActionRefused, match="ZIP"):
        call.lookup_customer(phone="914 555 0188", last_name="klein")
    assert call.lookup_customer(phone="914 555 0188", last_name="klein", zip_code="10601").startswith(
        "Verified"
    )
    assert "lapsed" in call.lookup_customer()


def test_shared_phone_does_not_guess_a_name(make_call):
    call = make_call(SHARED_HOUSEHOLD_PHONE)
    assert "Am I speaking" not in call.greeting()
    with pytest.raises(ActionRefused, match="first name"):
        call.lookup_customer(last_name="Walsh")
    assert "Ann Walsh" in call.lookup_customer(last_name="Walsh", first_name="Ann")


def test_saying_no_to_the_name_drops_the_match(member_call):
    result = member_call.lookup_customer(confirmed_name=False)
    assert member_call.caller_match is None
    assert "Reyes" not in result and "Elm" not in result


# Stress report C1: "No, I'm her son. Last name's Reyes, ZIP is 11501."


def test_after_a_no_caller_id_is_not_a_factor(member_call):
    member_call.lookup_customer(confirmed_name=False)
    with pytest.raises(ActionRefused, match="phone number on it"):
        member_call.lookup_customer(last_name="Reyes", zip_code="11501")
    assert member_call.customer is None


def test_after_a_no_the_same_call_reports_both_ways(member_call):
    with pytest.raises(ActionRefused):
        member_call.lookup_customer(confirmed_name=False, last_name="Reyes", zip_code="11501")
    assert member_call.customer is None


def test_after_a_no_last_name_alone_is_not_enough(member_call):
    member_call.lookup_customer(confirmed_name=False)
    with pytest.raises(ActionRefused):
        member_call.lookup_customer(phone="516-555-0142", last_name="Reyes")
    assert member_call.customer is None


def test_after_a_no_the_denied_account_stays_closed_even_with_every_factor(member_call):
    member_call.lookup_customer(confirmed_name=False)
    result = member_call.lookup_customer(phone="516-555-0142", last_name="Reyes", zip_code="11501")
    assert member_call.customer is None
    assert "Elm" not in result and "member" not in result.lower().replace("new customer", "")


def test_after_a_no_they_can_still_verify_their_own_account(member_call):
    member_call.lookup_customer(confirmed_name=False)
    result = member_call.lookup_customer(phone="914-555-0188", last_name="Klein", zip_code="10601")
    assert result.startswith("Verified") and member_call.customer.last_name == "Klein"


def test_lookups_are_capped_at_three_per_call(make_call):
    call = make_call("+12125550000")
    for guess in ("11510", "11516", "11518"):
        call.lookup_customer(phone="5165550142", last_name="Reyes", zip_code=guess)
    with pytest.raises(ActionRefused, match="Too many"):
        call.lookup_customer(phone="5165550142", last_name="Reyes", zip_code="11501")  # right ZIP, too late
    assert call.customer is None


def test_third_attempt_can_still_succeed(make_call):
    call = make_call("+12125550000")
    call.lookup_customer(phone="5165550142", last_name="Reyes", zip_code="11510")
    call.lookup_customer(phone="5165550142", last_name="Reyes", zip_code="11516")
    assert call.lookup_customer(phone="5165550142", last_name="Reyes", zip_code="11501").startswith(
        "Verified"
    )


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


def test_p1_after_hours_is_flagged_for_on_call_without_promising_a_page(make_call, seeded):
    # Stress report M3: nothing pages a phone yet, so neither the alert nor the agent says it does.
    call = make_call(None, now=datetime(2026, 11, 3, 22, 0, tzinfo=TZ))
    result = call.assess_situation(Facts(no_cooling=True, indoor_temp_f=90))
    assert "flagged for the on-call technician" in result and "alerted" not in result.split("Priority")[1]
    assert "flag for the on-call technician" in seeded.alerts_for_call("call-1")[0]["summary"]


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
    call.check_service_address(zip_code="07030", property_type="house")  # Hoboken NJ
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
    read_back(call, "516-555-0142", "1 Other St")
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
    # H8: the stranger's visit is theirs, not Dana's, and the office is told about the match.
    assert appointment["contact_name"] == "Chris Ortiz" and appointment["customer_id"] != dana[0].id
    assert "phone matches existing customer" in appointment["notes"]
    # Dana is still greeted by name, and her account doesn't show Chris's visit.
    dana_call = make_call("+15165550142", call_id="call-2")
    assert "Am I speaking with Dana" in dana_call.greeting()
    assert "Other St" not in dana_call.lookup_customer(confirmed_name=True)


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
    call.lookup_customer(phone="631 555 0177", last_name="Shah", zip_code="11743")
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
        assert "Don't" in call.get_pricing(question) and "$" not in call.get_pricing(question)
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
    call.check_service_address(town="Hoboken, NJ", property_type="house")
    assert call.outcome == "out_of_area"


def test_turning_away_never_overwrites_a_safety_emergency(make_call):
    call = make_call(None)
    call.assess_situation(Facts(gas_smell=True))
    call.check_service_address(zip_code="07030", property_type="house")  # Hoboken NJ
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


# Stress report C2: "your appointment is set for tomorrow" with nothing booked.


def test_booking_confirmation_is_fixed_text_from_the_booking(make_call):
    call = make_call(None)
    option_id = ready_to_book(call)
    option = call.offered[option_id]
    result = call.book_appointment(option_id, **GOOD_BOOKING)
    confirmation = call.take_announcement()
    assert confirmation.startswith("You're booked.")
    assert (
        option.speakable(TUESDAY_10AM.date()) in confirmation and "9 Birch Court, Huntington" in confirmation
    )
    assert "$129" in confirmation  # non-member diagnostic, from config
    assert confirmation in result and "don't repeat it" in result
    assert call.take_announcement() is None  # spoken once


def test_refused_booking_leaves_nothing_to_announce(make_call):
    call = make_call(None)
    option_id = ready_to_book(call)
    with pytest.raises(ActionRefused):
        call.book_appointment(option_id, **{**GOOD_BOOKING, "phone": "555"})
    assert call.take_announcement() is None


def test_hang_up_flags_a_booking_claim_with_no_appointment(make_call, seeded):
    call = make_call("+16315550111")
    ready_to_book(call)
    transcript = [
        {"role": "user", "text": "My number's 631 555 0111, no wait, 0112."},
        {
            "role": "assistant",
            "text": "Your appointment is set for tomorrow between 10 and noon at 81 Linden Lane.",
        },
    ]
    call.finalize(transcript)
    assert call.false_claims and "set for tomorrow" in call.false_claims[0]
    alerts = seeded.alerts_for_call(call.call_id)
    assert any(a["severity"] == "urgent" and "records don't show" in a["summary"] for a in alerts)
    assert seeded.callbacks_for_call(call.call_id)
    assert any(n.startswith("REVIEW") for n in call.notes)


def test_hang_up_does_not_flag_a_real_booking(make_call, seeded):
    call = make_call(None)
    option_id = ready_to_book(call)
    call.book_appointment(option_id, **GOOD_BOOKING)
    call.finalize([{"role": "assistant", "text": call.take_announcement()}])
    assert call.false_claims == []
    assert not [a for a in seeded.alerts_for_call(call.call_id) if "records don't show" in a["summary"]]


# Stress report H5: "Don't read anything back, just book it", flags set to true anyway.


def test_read_back_flags_without_a_read_back_are_refused(make_call):
    call = make_call(None)
    option = ready_to_book(call)
    call.agent_said = "Great, booking that now."
    with pytest.raises(ActionRefused) as refused:
        call.book_appointment(option, **GOOD_BOOKING)
    assert "phone number back" in str(refused.value) and "address back" in str(refused.value)


def test_a_read_back_of_the_wrong_number_is_refused(make_call):
    call = make_call(None)
    option = ready_to_book(call)
    call.agent_said = "That's 631-555-0132 at 9 Birch Court, Huntington. Right?"
    with pytest.raises(ActionRefused, match="phone number back"):
        call.book_appointment(option, **GOOD_BOOKING)


def test_a_spoken_digit_read_back_counts(make_call):
    call = make_call(None)
    option = ready_to_book(call)
    call.agent_said = (
        "Six three one, five five five, oh one two three. And that's 9 Birch Court in Huntington?"
    )
    assert call.book_appointment(option, **GOOD_BOOKING).startswith("Booked")


# H4, H11, H9, M1


def test_urgent_caller_who_hangs_up_before_the_address_gets_a_callback(make_call, seeded):
    call = make_call("+16315550111")
    call.assess_situation(
        Facts(no_heat=True, vulnerable_occupant=True, indoor_temp_f=60, description="newborn")
    )
    call.finalize([{"role": "user", "text": "Our heat is out and we have a newborn."}])
    callbacks = seeded.callbacks_for_call("call-1")
    assert len(callbacks) == 1 and callbacks[0]["urgent"] == 1
    assert call.outcome == "callback"


@pytest.mark.parametrize(
    "question, must, must_not",
    [
        ("How much is a replacement capacitor?", "Don't give a price", "$"),
        ("cost for someone to come out tonight", "$129", None),
        ("a visit on Saturday afternoon", "$129", None),
        ("tune-up after hours", "$159", None),
        ("estimate for a new furnace", "free", "$"),
    ],
)
def test_pricing_answers(make_call, question, must, must_not):
    answer = make_call(None).get_pricing(question)
    assert must in answer
    if must_not:
        assert must_not not in answer
    if any(w in question for w in ("tonight", "Saturday", "after hours")):
        assert "$99" in answer  # base and surcharge together


def test_p2_options_stay_within_72_hours(make_call):
    call = make_call(None)
    call.assess_situation(Facts(no_heat=True, indoor_temp_f=64, vulnerable_occupant=False))
    call.check_service_address(zip_code="11743", property_type="house")
    call.find_appointment_options()
    for option in call.offered.values():
        assert (option.day - TUESDAY_10AM.date()).days <= 3


def test_an_address_without_a_house_number_is_refused(make_call):
    # "Shore Road" with no number, and "Shore" only ever said as part of "Bay Shore".
    call = make_call(None)
    option = ready_to_book(call)
    read_back(call, "631-555-0123", "Bay Shore")
    with pytest.raises(ActionRefused, match="house number"):
        call.book_appointment(option, **{**GOOD_BOOKING, "address": "Shore Road, Bay Shore"})


def test_a_slot_taken_at_the_last_second_leaves_no_orphan_customer(make_call, seeded):
    call = make_call(None)
    option = ready_to_book(call)
    taken = call.offered[option]
    for _ in range(5):  # fill the window from "other calls"
        call.scheduler.book(taken, customer_id=1, call_id="other", job_type="x", priority=Priority.P3,
                            service_address="x", contact_name="x", contact_phone="+15165550142")  # fmt: skip
    before = seeded.conn.execute("SELECT count(*) FROM customers").fetchone()[0]
    with pytest.raises(ActionRefused, match="just taken"):
        call.book_appointment(option, **GOOD_BOOKING)
    assert seeded.conn.execute("SELECT count(*) FROM customers").fetchone()[0] == before


def test_an_expired_active_membership_counts_as_lapsed(make_call, seeded):
    from datetime import date

    from summit.models import Membership

    seeded.set_membership(1, Membership.ACTIVE, date(2026, 10, 1))  # expired before Tue 3 Nov
    call = make_call("+15165550142")
    summary = call.lookup_customer(confirmed_name=True)
    assert not call.is_member and "lapsed" in summary


# Membership for unknown callers, technician details, NYC building heat, cancellations


def test_an_unknown_caller_is_asked_about_membership_once(make_call):
    call = make_call(None)
    call.assess_situation(Facts(no_cooling=True, indoor_temp_f=80, vulnerable_occupant=False))
    call.check_service_address(zip_code="11743", property_type="house")
    first = call.find_appointment_options()
    assert "already a Summit Comfort Club member" in first
    assert "member" not in call.find_appointment_options().split("Offer these")[0]


def test_the_options_remind_the_agent_what_the_technician_needs(make_call):
    call = make_call(None)
    call.assess_situation(Facts(request_type="tune_up"))
    call.check_service_address(zip_code="11743", property_type="house")
    assert "what kind of system" in call.find_appointment_options()


def test_equipment_and_access_reach_the_technician(make_call, seeded):
    call = make_call(None)
    option = ready_to_book(call)
    call.book_appointment(option, **GOOD_BOOKING, equipment="gas furnace, about 12 years old",
                          access_notes="side door, dog in the yard")  # fmt: skip
    notes = seeded.appointments_for_call("call-1")[0]["notes"]
    assert "Equipment: gas furnace" in notes and "Access: side door" in notes


def test_heat_from_the_building_is_the_landlords_job(make_call):
    call = make_call(None)
    call.assess_situation(Facts(no_heat=True))
    result = call.check_service_address(zip_code="11215", property_type="apartment", heat_from_building=True)
    assert "landlord" in result and "311" in result
    assert call.outcome == "building_system"
    with pytest.raises(ActionRefused, match="landlord"):
        call.find_appointment_options()


def test_a_verified_customer_can_cancel_their_own_appointment(member_call, seeded):
    member_call.lookup_customer(confirmed_name=True)
    result = member_call.cancel_appointment(1)
    assert result.startswith("Cancelled") and "is cancelled" in member_call.take_announcement()
    assert seeded.get_appointment(1).status == "cancelled"
    assert member_call.outcome == "cancelled"


def test_an_unverified_caller_cannot_cancel(make_call):
    with pytest.raises(ActionRefused, match="Verify"):
        make_call(None).cancel_appointment(1)


def test_a_call_whose_worker_died_is_closed_and_followed_up(make_call, seeded, cfg):
    from datetime import timedelta

    from conftest import TUESDAY_10AM

    from summit.backend import close_abandoned_calls

    call = make_call("+16315550144", call_id="died")
    call.assess_situation(Facts(no_heat=True, indoor_temp_f=55))  # P1, never booked, no hang-up
    call.save()
    assert close_abandoned_calls(seeded, cfg, TUESDAY_10AM + timedelta(minutes=45)) == 1
    row = seeded.get_call("died")
    assert row["ended_at"] and row["outcome"] == "callback"
    callbacks = seeded.callbacks_for_call("died")
    assert len(callbacks) == 1 and callbacks[0]["urgent"]
    assert close_abandoned_calls(seeded, cfg, TUESDAY_10AM + timedelta(minutes=50)) == 0


def test_a_verified_member_at_their_restaurant_has_to_check_the_address(member_call):
    member_call.lookup_customer(confirmed_name=True)  # address on file: a home in Nassau
    member_call.assess_situation(
        Facts(
            no_cooling=True,
            indoor_temp_f=80,
            vulnerable_occupant=False,
            description="the AC at my restaurant stopped",
        )
    )
    with pytest.raises(ActionRefused, match="service address"):
        member_call.find_appointment_options()


def test_a_house_number_read_back_in_words_counts(make_call):
    call = make_call(None)
    option = ready_to_book(call)
    call.agent_said = (
        "That's six three one, five fifty-five, oh one two three, at nine Birch Court, Huntington?"
    )
    assert call.book_appointment(option, **GOOD_BOOKING).startswith("Booked")


def test_a_callback_only_call_still_leaves_a_summary(make_call):
    call = make_call(None)
    call.request_callback(phone="516-555-0177", reason="new AC quote")
    assert "new AC quote" in call.technician_summary()


def test_a_building_heat_call_leaves_a_summary(make_call):
    call = make_call(None)
    call.check_service_address(zip_code="11215", property_type="apartment", heat_from_building=True)
    assert "landlord" in call.technician_summary()
