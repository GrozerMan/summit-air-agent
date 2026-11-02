"""Deterministic P0-P3 triage.

The model extracts facts from the conversation; these rules turn facts into a
priority. Same facts, same priority, and every assessment lists the rules that
fired so the office can see why a call was rated the way it was.

    P0  gas smell (even "gone now"), CO alarm or symptoms, smoke / sparks / flames
    P1  no heat with a vulnerable occupant or indoor temp at/below the threshold
        no cooling with a vulnerable occupant or indoor temp at/above the threshold
        persistent burning smell, active leak
    P2  no heat or no cooling otherwise, minor drip
    P3  everything else: tune-ups, estimates, non-urgent repairs
"""

from dataclasses import dataclass, field, fields, replace
from typing import Any

from summit.models import Priority


@dataclass
class Facts:
    """What the caller has told us. None means "not known yet", which is not the same as False."""

    gas_smell: bool | None = None
    co_alarm_or_symptoms: bool | None = None
    smoke_sparks_or_flames: bool | None = None
    burning_smell_persistent: bool | None = None
    dusty_smell_first_use: bool | None = None
    no_heat: bool | None = None
    no_cooling: bool | None = None
    indoor_temp_f: int | None = None
    vulnerable_occupant: bool | None = None
    active_leak: bool | None = None
    minor_drip: bool | None = None
    request_type: str | None = None
    description: str = ""

    def updated_with(self, newer: "Facts") -> "Facts":
        """Newer answers win, but a hazard once reported stays reported.

        A caller who smelled gas and then says "it's gone now" still gets the
        safety script; the gas company decides whether it's safe, not us.
        """
        changes: dict[str, Any] = {}
        for f in fields(self):
            new_value = getattr(newer, f.name)
            if f.name == "description":
                if new_value and new_value not in self.description:
                    changes[f.name] = f"{self.description} / {new_value}".strip(" /")
                continue
            if new_value is None:
                continue
            if f.name in _STICKY and getattr(self, f.name) is True:
                continue
            changes[f.name] = new_value
        return replace(self, **changes)

    def known(self) -> dict[str, Any]:
        return {
            f.name: getattr(self, f.name) for f in fields(self) if getattr(self, f.name) not in (None, "")
        }


_STICKY = {"gas_smell", "co_alarm_or_symptoms", "smoke_sparks_or_flames"}


@dataclass
class Assessment:
    priority: Priority
    reasons: list[str]
    hazard: str | None = None
    ask_next: list[str] = field(default_factory=list)


def assess(facts: Facts, cfg: dict[str, Any]) -> Assessment:
    rules = cfg["triage"]

    hazards = [
        ("gas", facts.gas_smell, "gas smell reported"),
        ("co", facts.co_alarm_or_symptoms, "carbon monoxide alarm or symptoms"),
        ("fire", facts.smoke_sparks_or_flames, "smoke, sparks or flames"),
    ]
    fired = [(kind, reason) for kind, present, reason in hazards if present]
    if fired:
        return Assessment(Priority.P0, [r for _, r in fired], hazard=fired[0][0])

    temp = facts.indoor_temp_f
    vulnerable = facts.vulnerable_occupant is True
    reasons: list[str] = []

    if facts.no_heat:
        if vulnerable:
            reasons.append("no heat with a vulnerable occupant")
        if temp is not None and temp <= rules["no_heat_max_indoor_f"]:
            reasons.append(f"no heat, {temp}°F inside")
    if facts.no_cooling:
        if vulnerable:
            reasons.append("no cooling with a vulnerable occupant")
        if temp is not None and temp >= rules["no_cooling_min_indoor_f"]:
            reasons.append(f"no cooling, {temp}°F inside")
    if facts.burning_smell_persistent:
        reasons.append("persistent burning smell")
    if facts.active_leak:
        reasons.append("active water leak")
    if reasons:
        return Assessment(Priority.P1, reasons)

    if facts.no_heat or facts.no_cooling:
        ask = []
        if temp is None:
            ask.append("the temperature inside right now")
        if facts.vulnerable_occupant is None:
            ask.append("whether anyone elderly, an infant, or someone with a medical need is home")
        what = "no heat" if facts.no_heat else "no cooling"
        return Assessment(Priority.P2, [what], ask_next=ask)
    if facts.minor_drip:
        return Assessment(Priority.P2, ["minor drip"])

    if facts.dusty_smell_first_use:
        return Assessment(Priority.P3, ["dusty smell on first use of the season, normal"])
    return Assessment(Priority.P3, [facts.request_type or "routine request"])


def safety_script(hazard: str, county: str | None, cfg: dict[str, Any]) -> str:
    """The exact words for a P0 call. Kept short; the caller should be leaving, not listening."""
    if hazard == "gas":
        utility = cfg["gas_utilities"].get(county or "")
        who_to_call = f"call 911 or {utility['name']} at {utility['phone']}" if utility else "call 911"
        return (
            "This could be a gas leak, so please leave the house now and take everyone with you. "
            "Don't touch light switches, appliances or phones on your way out. "
            f"Once you're outside and away from the house, {who_to_call}. "
            "Don't go back in until they tell you it's safe."
        )
    if hazard == "co":
        return (
            "Carbon monoxide is dangerous, so please get everyone out into fresh air right now, "
            "and leave the door open behind you. Once you're outside, call 911, especially if "
            "anyone has a headache, dizziness or nausea. "
            "Don't go back in until the fire department says it's safe."
        )
    return (
        "Please get everyone out of the house right now and call 911 once you're outside. "
        "Don't try to put it out or go back in."
    )
