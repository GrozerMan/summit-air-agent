from datetime import date

import pytest

from summit.models import Priority
from summit.triage import Facts, assess, cannot_leave_script, in_heating_season, safety_script


def priority(cfg, **facts):
    return assess(Facts(**facts), cfg).priority


@pytest.mark.parametrize(
    "facts",
    [
        {"gas_smell": True},
        {"co_alarm_or_symptoms": True},
        {"smoke_sparks_or_flames": True},
        {"gas_smell": True, "request_type": "tune_up"},
    ],
)
def test_hazards_are_p0(cfg, facts):
    assert priority(cfg, **facts) == Priority.P0


def test_no_heat_with_vulnerable_occupant_is_p1(cfg):
    assert priority(cfg, no_heat=True, vulnerable_occupant=True, indoor_temp_f=68) == Priority.P1


def test_no_heat_at_threshold_is_p1(cfg):
    assert priority(cfg, no_heat=True, indoor_temp_f=58) == Priority.P1


def test_no_heat_just_above_threshold_is_p2(cfg):
    assert priority(cfg, no_heat=True, indoor_temp_f=59) == Priority.P2


def test_no_cooling_when_hot_inside_is_p1(cfg):
    assert priority(cfg, no_cooling=True, indoor_temp_f=88) == Priority.P1


def test_no_cooling_when_mild_is_p2(cfg):
    assert priority(cfg, no_cooling=True, indoor_temp_f=78, vulnerable_occupant=False) == Priority.P2


def test_persistent_burning_smell_is_p1(cfg):
    assert priority(cfg, burning_smell_persistent=True) == Priority.P1


def test_active_leak_is_p1_and_minor_drip_is_p2(cfg):
    assert priority(cfg, active_leak=True) == Priority.P1
    assert priority(cfg, minor_drip=True) == Priority.P2


def test_first_use_dusty_smell_is_routine(cfg):
    assert priority(cfg, dusty_smell_first_use=True) == Priority.P3


def test_tune_up_is_routine(cfg):
    assert priority(cfg, request_type="tune_up") == Priority.P3


def test_p2_asks_for_temperature_and_occupants(cfg):
    result = assess(Facts(no_heat=True), cfg)
    assert result.priority == Priority.P2
    assert any("temperature" in q for q in result.ask_next)
    assert any("elderly" in q for q in result.ask_next)


def test_reasons_say_why(cfg):
    result = assess(Facts(no_heat=True, indoor_temp_f=55, vulnerable_occupant=True), cfg)
    assert "no heat with a vulnerable occupant" in result.reasons
    assert "no heat, 55°F inside" in result.reasons


def test_reported_hazard_is_not_undone_by_later_answers():
    facts = Facts(gas_smell=True).updated_with(Facts(gas_smell=False, description="smell is gone now"))
    assert facts.gas_smell is True
    assert "smell is gone now" in facts.description


def test_later_answers_update_ordinary_facts():
    facts = Facts(no_heat=True, indoor_temp_f=66).updated_with(Facts(indoor_temp_f=57))
    assert facts.indoor_temp_f == 57
    assert facts.no_heat is True


def test_gas_script_names_the_county_utility(cfg):
    assert "Con Edison" in safety_script("gas", "Westchester", cfg)
    assert "National Grid" in safety_script("gas", "Suffolk", cfg)


def test_gas_script_without_county_still_says_911(cfg):
    script = safety_script("gas", None, cfg)
    assert "nine-one-one" in script
    assert "leave the house now" in script


@pytest.mark.parametrize("hazard", ["gas", "co", "fire"])
@pytest.mark.parametrize("county", ["Nassau", "Westchester", None])
def test_spoken_scripts_have_no_digits(cfg, hazard, county):
    # Digits are what TTS read as "nine hundred and eleven" on test call P0-01.
    for script in (safety_script(hazard, county, cfg), cannot_leave_script(hazard)):
        assert not any(ch.isdigit() for ch in script), script
        assert "nine-one-one" in script


def test_description_with_gas_words_is_p0_even_when_the_model_says_no_gas(cfg):
    # Test call P0-01, verbatim from the tool log: the model sent gas_smell=false.
    facts = Facts(gas_smell=False, description="nasty skunk-like smell from furnace earlier but now gone")
    result = assess(facts, cfg)
    assert result.priority == Priority.P0
    assert result.hazard == "gas"
    assert "caller's words" in result.reasons[0]


def test_dusty_first_use_description_stays_routine(cfg):
    facts = Facts(
        dusty_smell_first_use=True,
        description="dusty burning smell, first time turning the heat on this year, gas furnace",
    )
    assert assess(facts, cfg).priority == Priority.P3


# The heating season: "no heat in winter" is urgent on its own (the owner's rule).
NOV_3 = date(2026, 11, 3)
JULY_9 = date(2026, 7, 9)


def test_no_heat_in_heating_season_is_urgent(cfg):
    result = assess(Facts(no_heat=True), cfg, today=NOV_3)
    assert result.priority == Priority.P1
    assert "no heat during the heating season" in result.reasons


def test_no_heat_out_of_season_is_not_urgent_by_itself(cfg):
    assert assess(Facts(no_heat=True, indoor_temp_f=70), cfg, today=JULY_9).priority == Priority.P2


def test_no_heat_in_season_but_comfortable_inside_waits(cfg):
    assert assess(Facts(no_heat=True, indoor_temp_f=68), cfg, today=NOV_3).priority == Priority.P2


def test_heating_season_wraps_the_new_year(cfg):
    assert in_heating_season(date(2027, 1, 15), cfg)
    assert in_heating_season(date(2026, 10, 1), cfg)
    assert in_heating_season(date(2027, 5, 31), cfg)
    assert not in_heating_season(date(2027, 6, 1), cfg)


def test_no_cooling_is_not_affected_by_the_season(cfg):
    assert assess(Facts(no_cooling=True, indoor_temp_f=80), cfg, today=JULY_9).priority == Priority.P2


# The model's judgement: it can raise a call to P1 with a specific fact, never lower one,
# and a caller's wish for speed isn't a fact.


def test_a_concrete_reason_raises_a_routine_call_to_p1(cfg):
    result = assess(
        Facts(request_type="other", urgent_reason="water dripping onto the electrical panel"), cfg
    )
    assert result.priority == Priority.P1
    assert result.reasons == ["agent judgement: water dripping onto the electrical panel"]


@pytest.mark.parametrize(
    "reason",
    [
        "caller says it's an emergency",
        "she needs someone out today",
        "he is very upset and can't wait",
        "caller insists it is urgent",
        "wants a tech here ASAP",
    ],
)
def test_insistence_is_not_a_reason(cfg, reason):
    assert priority(cfg, request_type="other", urgent_reason=reason) == Priority.P3


def test_a_hazard_in_the_reason_is_still_p0(cfg):
    assert priority(cfg, request_type="other", urgent_reason="smoke coming out of the vents") == Priority.P0
