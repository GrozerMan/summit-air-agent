"""P0 through the session: what the caller hears and what the dispatcher gets.

Stress report C3 (fire), C5 (gas utility before an address), H1 (word-list false
alarms stay P0 but get a callback route), M6 (the reminder that looped)."""

import pytest

from summit.backend import ActionRefused
from summit.models import Priority
from summit.triage import Facts


def test_town_and_zip_in_the_same_sentence_name_the_utility(make_call, seeded):
    call = make_call(None)
    script = call.screen_caller_turn("I'm in Yonkers, 10701, and I smell gas by the boiler.")
    assert "Con Edison" in script and "nine-one-one" in script
    alert = seeded.alerts_for_call(call.call_id)[-1]["summary"]
    assert "Location given: Yonkers 10701 (Westchester County)" in alert
    assert 'Caller said: "I\'m in Yonkers, 10701, and I smell gas by the boiler."' in alert


def test_a_town_alone_is_enough(make_call):
    call = make_call(None)
    assert "National Grid" in call.screen_caller_turn("We're in Hicksville and there's a rotten egg smell.")


def test_no_location_still_names_a_second_number(make_call, seeded):
    call = make_call(None)
    script = call.screen_caller_turn("it smells like gas in here")
    assert "call nine-one-one or your gas company" in script
    assert "it smells like gas in here" in seeded.alerts_for_call(call.call_id)[-1]["summary"]


def test_a_town_in_another_sentence_is_not_used(make_call):
    # Only the hazard's own sentence: "my sister in Yonkers" isn't where the caller is.
    call = make_call(None)
    script = call.screen_caller_turn("My sister lives in Yonkers. Anyway, I smell gas.")
    assert "Con Edison" not in script and "your gas company" in script


def test_the_script_is_read_once_even_after_the_address_is_known(make_call):
    call = make_call(None)
    first = call.screen_caller_turn("it smells like gas")
    call.check_service_address(zip_code="10701", property_type="house")
    assert call.safety_script() == first
    assert call.screen_caller_turn("what should I do with the dog?", said_so_far=first) is None


def test_sparks_reported_in_the_past_reach_p0_without_the_model(make_call, seeded):
    call = make_call(None)
    script = call.screen_caller_turn("My AC outdoor unit was sparking and now it keeps tripping the breaker.")
    assert call.priority == Priority.P0 and call.assessment.hazard == "fire"
    assert "get everyone out of the house" in script
    assert seeded.alerts_for_call(call.call_id)[-1]["severity"] == "critical"


def test_sparks_in_the_models_description_reach_p0(make_call):
    call = make_call(None)
    call.assess_situation(
        Facts(no_cooling=True, description="AC unit was sparking earlier, trips the breaker")
    )
    assert call.priority == Priority.P0


def test_a_words_only_p0_offers_the_office_callback(make_call):
    call = make_call(None)
    call.screen_caller_turn("There's a skunk smell by the furnace.")
    assert call.hazard_from_words_only
    with pytest.raises(ActionRefused, match="offer a callback from the office"):
        call.find_appointment_options()
    assert "request_callback" in call.emergency_note()
    # The callback itself is allowed on a P0 call.
    assert call.request_callback("631-555-0100", "wants a furnace visit; said there's no gas").startswith(
        "Callback set"
    )


def test_a_p0_the_model_confirms_is_not_words_only(make_call):
    call = make_call(None)
    call.screen_caller_turn("There's a skunk smell by the furnace.")
    call.assess_situation(Facts(gas_smell=True, description="skunk smell by the furnace"))
    assert call.priority == Priority.P0 and not call.hazard_from_words_only
    with pytest.raises(ActionRefused) as refused:
        call.find_appointment_options()
    assert "callback" not in str(refused.value)


def test_a_gas_report_stays_p0_when_the_caller_takes_it_back(make_call):
    call = make_call(None)
    call.screen_caller_turn("I smell gas")
    call.assess_situation(Facts(gas_smell=False, description="actually no, it's nothing"))
    assert call.priority == Priority.P0


def test_the_standing_note_stops_restating_the_script_once_the_caller_leaves(make_call):
    call = make_call(None)
    script = call.screen_caller_turn("I smell gas")
    note = call.emergency_note()
    assert "Don't repeat the instructions" in note and "end_call" in note
    call.screen_caller_turn("Okay, I'm going outside now. Bye.", said_so_far=script)
    note = call.emergency_note()
    assert "is leaving" in note and "end_call" in note and "nine-one-one" not in note


def test_cant_leave_after_saying_bye_gets_the_fixed_answer(make_call):
    call = make_call(None)
    script = call.screen_caller_turn("I smell gas")
    call.screen_caller_turn("okay bye", said_so_far=script)
    answer = call.screen_caller_turn("wait, I can't leave, my mom is in a wheelchair", said_so_far=script)
    assert "hang up and call nine-one-one" in answer and not call.caller_leaving


def test_a_place_the_caller_is_at_in_the_next_sentence_names_the_utility(make_call):
    script = make_call(None).screen_caller_turn("I smell gas. I'm in Yonkers.")
    assert "Con Edison" in script


def test_a_zip_read_digit_by_digit_names_the_utility(make_call):
    script = make_call(None).screen_caller_turn("There's a gas smell at my place, 1 0 7 0 1")
    assert "Con Edison" in script


def test_where_the_caller_is_beats_caller_id(make_call):
    # Dana lives in Nassau (National Grid) but is calling about her rental in Yonkers.
    from summit.seed import DEMO_MEMBER_PHONE

    script = make_call(DEMO_MEMBER_PHONE).screen_caller_turn(
        "Yes, it's Dana. I'm at my rental in Yonkers, 10701, and I smell gas."
    )
    assert "Con Edison" in script


def test_of_two_places_the_one_the_caller_is_at_wins(make_call):
    script = make_call(None).screen_caller_turn(
        "My mom in Huntington is fine but I'm in Yonkers and I smell gas"
    )
    assert "Con Edison" in script


def test_nyc_borough_gets_its_utility_and_queens_stays_generic(make_call):
    assert "National Grid at seven one eight" in make_call(None).screen_caller_turn(
        "I smell gas in Park Slope"
    )
    assert "your gas company" in make_call(None).screen_caller_turn("I smell gas, I'm in Astoria")
