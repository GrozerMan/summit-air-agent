import pytest

from summit.models import Priority
from summit.triage import Facts, assess, safety_script


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
    assert "911" in script
    assert "leave the house now" in script
