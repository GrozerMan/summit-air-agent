"""The owner's views: results, follow-ups and the morning brief (summit/insights.py)."""

from datetime import datetime

import pytest

from summit import insights
from summit.sample_week import add_sample_week
from summit.triage import Facts
from tests.conftest import TUESDAY_10AM, TZ


@pytest.fixture
def week(seeded, cfg):
    add_sample_week(seeded, cfg, TUESDAY_10AM)
    return seeded


def at(*args):
    return datetime(*args, tzinfo=TZ).isoformat()


def test_after_hours_covers_evenings_sundays_and_holidays(cfg):
    assert not insights.after_hours(at(2026, 11, 3, 10, 0), cfg)  # Tuesday morning
    assert insights.after_hours(at(2026, 11, 3, 21, 0), cfg)  # Tuesday night
    assert insights.after_hours(at(2026, 11, 8, 11, 0), cfg)  # Sunday
    assert insights.after_hours(at(2026, 11, 26, 11, 0), cfg)  # Thanksgiving


@pytest.mark.parametrize(
    "job, kind",
    [("no heat", "repair"), ("AC repair", "repair"), ("tune-up", "tune_up"),
     ("annual maintenance", "tune_up"), ("replacement estimate", "estimate")],
)  # fmt: skip
def test_job_kind(job, kind):
    assert insights.job_kind(job) == kind


def test_job_value_comes_from_config(cfg):
    assert insights.job_value("no heat", cfg) == cfg["insights"]["repair_visit_value"]
    assert insights.job_value("tune-up", cfg) == cfg["insights"]["tune_up_value"]
    assert insights.job_value("replacement estimate", cfg) == 0  # pipeline, not revenue


@pytest.mark.parametrize(
    "text, age",
    [("gas furnace, about 22 years old", 22), ("a 20-year-old boiler", 20), ("installed in 2009", 17),
     ("it's from 2004", 22), ("8 years old", 8), ("serviced 2 years ago", None), ("no idea", None)],
)  # fmt: skip
def test_equipment_age(text, age):
    assert insights.equipment_age(text, 2026) == age


def test_results_for_the_sample_week(week, cfg):
    r = insights.results(week, cfg, TUESDAY_10AM, days=7)
    assert r["calls"] == 14
    assert r["after_hours_calls"] == 10
    assert r["jobs_booked"] == 6
    assert r["jobs_by_kind"] == {"repair": 4, "tune_up": 1, "estimate": 1}
    values = cfg["insights"]
    assert r["revenue_estimate"] == 4 * values["repair_visit_value"] + values["tune_up_value"]
    assert r["replacement_leads"] == 3
    assert r["pipeline_estimate"] == 3 * values["replacement_value"]
    assert (r["emergencies"], r["urgent"], r["members_recognized"]) == (1, 2, 1)
    assert r["false_claims"] == 0
    assert r["sample"] is True
    assert r["agent_cost_per_call"] < r["answering_service_per_call"]


def test_results_today_only(week, cfg):
    r = insights.results(week, cfg, TUESDAY_10AM, days=1)
    assert r["calls"] == 1 and r["jobs_booked"] == 1


def test_real_calls_count_and_are_not_sample(make_call, cfg, seeded):
    call = make_call("+16315550177")
    call.assess_situation(Facts(gas_smell=True))
    call.finalize([{"role": "user", "text": "I smell gas"}])
    r = insights.results(seeded, cfg, TUESDAY_10AM, days=7)
    assert r["calls"] == 1 and r["emergencies"] == 1 and r["sample"] is False
    assert insights.opportunities(seeded, cfg, TUESDAY_10AM) == []  # a safety call is not a sales lead


def test_a_cancelled_visit_is_not_revenue(week, cfg):
    appt = next(a for a in week.appointments_from_calls() if a["call_id"] == "sample-01")
    week.cancel_appointment(appt["id"])
    r = insights.results(week, cfg, TUESDAY_10AM, days=7)
    assert r["jobs_booked"] == 5


def test_opportunities(week, cfg):
    found = {o["key"]: o for o in insights.opportunities(week, cfg, TUESDAY_10AM)}
    # Old systems, and someone asking about replacing theirs.
    assert "about 22 years old" in found["sample-01:replacement"]["why"]
    assert "17 years old" in found["sample-02:replacement"]["why"]
    assert "sample-06:replacement" in found
    # An 8-year-old furnace isn't a replacement lead; a non-member repair is a membership pitch.
    assert "sample-03:replacement" not in found
    assert found["sample-03:membership"]["who"] == "Priya Shah"
    # The lapsed member, the commercial lead, the callers who didn't book.
    assert found["sample-02:renewal"]["who"] == "Robert Klein"
    assert "sample-10:commercial" in found
    assert {"sample-08:unbooked", "sample-09:unbooked"} <= set(found)
    # The active member's tune-up is no lead at all; nor are out-of-area or building-heat calls.
    assert not any(k.startswith(("sample-04:", "sample-11:", "sample-12:")) for k in found)
    # Most valuable first.
    values = [o["value"] or 0 for o in found.values()]
    assert values == sorted(values, reverse=True)


def test_done_followups_drop_off(week, cfg):
    week.mark_followup_done("sample-02:renewal")
    week.mark_followup_done("sample-02:renewal")  # twice is fine
    keys = [o["key"] for o in insights.opportunities(week, cfg, TUESDAY_10AM)]
    assert "sample-02:renewal" not in keys
    every = insights.opportunities(week, cfg, TUESDAY_10AM, include_done=True)
    assert next(o for o in every if o["key"] == "sample-02:renewal")["done"] is True


def test_outside_demand(week, cfg):
    places = {d["place"]: d["calls"] for d in insights.outside_demand(week, cfg, TUESDAY_10AM)}
    assert places == {"Jersey City": 1, "Stamford": 1, "ZIP 07030": 1}


def test_last_close(cfg):
    # Tuesday 10am: Monday 7pm. Monday 9am: Saturday 2pm (closed Sunday).
    assert insights.last_close(cfg, TUESDAY_10AM) == datetime(2026, 11, 2, 19, 0, tzinfo=TZ)
    assert insights.last_close(cfg, datetime(2026, 11, 9, 9, 0, tzinfo=TZ)) == datetime(
        2026, 11, 7, 14, 0, tzinfo=TZ
    )


def test_brief(week, cfg):
    b = insights.brief(week, cfg, TUESDAY_10AM)
    assert b["overnight"]["calls"] == 4
    assert b["overnight"]["booked"] == 2
    assert [j["contact_name"] for j in b["jobs"]] == ["Robert Klein", "Priya Shah"]  # by window
    assert b["jobs"][0]["equipment"] == "oil boiler, installed in 2009"
    assert b["jobs"][0]["access"] == "ring twice, mother hard of hearing"
    assert len(b["callbacks"]) == 2
    assert len(b["followups"]) == 5
    text = insights.brief_text(b, cfg)
    assert "Since the office closed (Mon 7:00 PM): 4 calls, 2 booked" in text
    assert "Today's jobs: 2" in text
    assert text.endswith("(Includes sample data.)")


def test_parse_notes():
    notes = "P1 no heat. Caller says: cold. Equipment: gas furnace, about 22 years old. Access: side door."
    assert insights.parse_notes(notes) == {
        "equipment": "gas furnace, about 22 years old",
        "access": "side door",
    }
    assert insights.parse_notes("") == {}
