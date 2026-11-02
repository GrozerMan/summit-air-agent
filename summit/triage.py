"""Deterministic P0-P3 triage.

The model extracts facts from the conversation; these rules turn facts into a
priority. Same facts, same priority, and every assessment lists the rules that
fired so the office can see why a call was rated the way it was.

    P0  gas smell (even "gone now"), CO alarm or symptoms, smoke / sparks / flames.
        All three also come from the caller's own words (hazard_words), so a
        model that reports gas_smell=false for "smelled like a skunk", or never
        reports the sparks at all, can't keep the call out of P0.
    P1  no heat with a vulnerable occupant or indoor temp at/below the threshold
        no cooling with a vulnerable occupant or indoor temp at/above the threshold
        persistent burning smell, active leak
    P2  no heat or no cooling otherwise, minor drip
    P3  everything else: tune-ups, estimates, non-urgent repairs
"""

from dataclasses import dataclass, field, fields, replace
from typing import Any

from summit.hazard_words import hazard_in
from summit.models import Priority
from summit.speech import say_hotline


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


def assess(facts: Facts, cfg: dict[str, Any], heard: set[str] | None = None) -> Assessment:
    """`heard` is hazards already found in the caller's own words this call (the screen)."""
    rules = cfg["triage"]

    heard = set(heard or ()) | {hazard_in(facts.description)}
    hazards = [
        ("gas", facts.gas_smell, "gas" in heard, "gas smell reported"),
        ("co", facts.co_alarm_or_symptoms, "co" in heard, "carbon monoxide alarm or symptoms"),
        ("fire", facts.smoke_sparks_or_flames, "fire" in heard, "smoke, sparks or flames"),
    ]
    fired = [
        (kind, reason if reported else f"{reason} (caller's words)")
        for kind, reported, in_words, reason in hazards
        if reported or in_words
    ]
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


# Spoken text says "nine-one-one". Written as "911", TTS (or the model, when it
# paraphrases) can read it as "nine hundred and eleven".
EMERGENCY = "nine-one-one"


def safety_script(hazard: str, county: str | None, cfg: dict[str, Any]) -> str:
    """The exact words for a P0 call. Kept short; the caller should be leaving, not listening."""
    if hazard == "gas":
        utility = cfg["gas_utilities"].get(county or "")
        # Without a location we can't name the utility, but every gas company runs a
        # leak line, so the caller still hears that there's a second number to call.
        who_to_call = (
            f"call {EMERGENCY}, or {utility['name']} at {say_hotline(utility['phone'])}"
            if utility
            else f"call {EMERGENCY} or your gas company"
        )
        return (
            "This could be a gas leak, so please leave the house now and take everyone with you. "
            "Don't touch light switches, appliances or phones on your way out. "
            f"Once you're outside and away from the house, {who_to_call}. "
            "Don't go back in until they tell you it's safe."
        )
    if hazard == "co":
        return (
            "Carbon monoxide is dangerous, so please get everyone out into fresh air right now, "
            "and leave the door open behind you. "
            f"Once you're outside, call {EMERGENCY}, especially if anyone has a headache, "
            "dizziness or nausea. "
            "Don't go back in until the fire department says it's safe."
        )
    return (
        f"Please get everyone out of the house right now and call {EMERGENCY} once you're outside. "
        "Don't try to put it out or go back in."
    )


def cannot_leave_script(hazard: str) -> str:
    """For a caller who, after the safety script, says they can't or won't get out.

    This used to be improvised by the model, on the most safety-critical turn of the
    call. The owner should sign off on this wording.
    """
    if hazard == "gas":
        return (
            "I understand. If you can, step just outside the front door, or go to a neighbor's, "
            "somewhere you can still see the street. "
            f"If you really can't get out, hang up and call {EMERGENCY} right now. Tell them you "
            "smell gas and can't leave. Open a door or window if you can, and don't switch "
            "anything on or off."
        )
    if hazard == "co":
        return (
            "I understand. If you really can't get out, open windows and doors, stay right by "
            f"the fresh air, and hang up and call {EMERGENCY} right now. Tell them a carbon "
            "monoxide alarm is going off and you can't leave."
        )
    return (
        f"I understand. If you can't get out, hang up and call {EMERGENCY} right now and tell "
        "them exactly where you are in the house."
    )
