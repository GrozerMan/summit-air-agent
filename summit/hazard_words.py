"""Hazard words in the caller's own speech, matched without the model.

The model fills in `gas_smell` and the rest of the triage facts, and triage can only
act on what the model reports. In test call P0-01 the caller said "kinda like a
skunk... earlier today, but now it's gone", and the model sent gas_smell=false.
Triage scored it P3 and the agent offered appointment times.

These patterns run on the caller's raw transcript and on the description the model
passes to triage. A match can only raise priority. It never lowers it, and an
unmatched turn changes nothing. So the model is no longer the only way a call
reaches P0.

The lists lean toward escalating. An unneeded evacuation costs a few minutes of
the caller's time, and a missed gas leak can cost a house. The one carve-out is
plain negation in the same clause ("I don't smell gas"), so that a "no" to a safety
question doesn't trigger the script it's checking for.
"""

import re

# Odor words that mean a possible leak by themselves. Utilities add mercaptan to
# gas so it smells like rotten eggs, sulfur or skunk, and callers use all three.
_ODORANT = r"rotten[\s-]*eggs?|sul(?:f|ph)ur\w*|skunk\w*|mercaptan"

# "gas" or "propane" with a smell word nearby, in either order.
_SMELL = r"smell\w*|odou?r\w*|whiff\w*|stinks?|stinky|stench|reek\w*|fumes?"
_FUEL = r"gas|gassy|propane"
# Gas words that name a thing rather than a smell: "smells weird near the gas furnace"
# is a question to ask, not an emergency.
# Stove, tank and meter are left out on purpose: "smells like the gas stove" is a gas smell.
_FUEL_THING = r"furnace|heater|boiler|dryer|fireplace|water|bill|station|company|mileage|pedal|prices?"
_NEAR = r"(?:\W+\w+){0,4}?\W+"

_GAS_PATTERNS = [
    re.compile(rf"\b(?:{_ODORANT})\b", re.I),
    re.compile(rf"\b(?:{_SMELL}){_NEAR}(?:{_FUEL})\b(?!\s+(?:{_FUEL_THING})\b)", re.I),
    re.compile(rf"\b(?:{_FUEL})\b(?!\s+(?:{_FUEL_THING})\b){_NEAR}(?:{_SMELL})\b", re.I),
    re.compile(rf"\b(?:{_FUEL})\s+(?:smell\w*|odou?r\w*)", re.I),
    re.compile(r"\b(?:gas|propane)\s+leak\w*|\bleak\w*\s+(?:\w+\s+)?(?:gas|propane)\b", re.I),
]

# A CO alarm that is sounding. A chirp is usually a low battery, so "chirping" is
# deliberately missing: the agent should ask about it, not evacuate on it.
_CO_PATTERNS = [
    re.compile(
        r"\b(?:carbon\s+monoxide|co|c\.o\.|c\s+o)\s+(?:alarm|detector|monitor|sensor)s?\b"
        r"(?:\W+\w+){0,3}?\W+(?:going\s+off|went\s+off|goes\s+off|keeps\s+going|"
        r"beep\w*|sound\w*|alarm\w*|ringing|screaming|blaring)",
        re.I,
    ),
    re.compile(r"\bcarbon\s+monoxide\s+(?:leak\w*|poison\w*)", re.I),
]

_NEGATION = re.compile(r"no|not|never|nothing|without|\w+n't|dont|doesnt|didnt|isnt|wasnt", re.I)
# "not sure", "don't know", "don't think" are doubt, not denial: still escalate.
_HEDGES = {"sure", "know", "certain", "positive", "think"}
# A clause that opens with a negation and then one of these is a question:
# "Doesn't that smell like gas?", "Isn't the CO alarm going off?"
_QUESTION_NEXT = {"it", "that", "this", "there", "you", "the", "my", "your", "a"}

# The caller says they can't or won't get out after hearing the safety script.
_GET_OUT = (
    r"leav\w*|evacuat\w*|get\s+out\w*|go(?!\s+back)\b|go\s+out\w*|walk\s+out|step\s+out|"
    r"outside|out\s+of\s+the\s+house"
)
_CANT_LEAVE = re.compile(
    rf"\b(?:can'?t|cannot|can\s+not|unable\s+to|won'?t|don'?t\s+(?:want\s+to|feel\s+safe)|"
    rf"not\s+(?:able|safe|comfortable|going\s+to)|afraid\s+to|scared\s+to)"
    rf"(?:\W+\w+){{0,4}}?\W+(?:{_GET_OUT})"
    rf"|\b(?:stuck|trapped|bedridden|wheelchair)\b"
    rf"|\b(?:dark|scared|afraid|unsafe)\b(?:\W+\w+){{0,4}}?\W+(?:outside|out\s+there|leav\w*)\b",
    re.I,
)


_WORD = re.compile(r"[\w']+")


def _clause_before(text: str, start: int) -> str:
    """The text between the last clause break and `start`."""
    head = text[:start]
    cut = max(head.rfind(p) for p in ".,;!?")
    return head[cut + 1 :]


def _negated(text: str, match: re.Match[str]) -> bool:
    """A plain denial in the same clause: "doesn't smell like gas", "no gas smell",
    "the CO alarm isn't going off". A comma ends the scope, so "No, it smells like
    gas" still counts."""
    before = _WORD.findall(_clause_before(text, match.start()))
    inside = _WORD.findall(match.group(0))
    words = before + inside
    first_checked = max(0, len(before) - 3)
    for i in range(first_checked, len(words) - 1):
        if not _NEGATION.fullmatch(words[i]):
            continue
        following = words[i + 1].lower()
        if following in _HEDGES:
            continue
        if i == 0 and following in _QUESTION_NEXT:
            continue
        return True
    return False


def _hits(patterns: list[re.Pattern[str]], text: str) -> bool:
    for pattern in patterns:
        for match in pattern.finditer(text):
            if not _negated(text, match):
                return True
    return False


def hazard_in(text: str | None) -> str | None:
    """"gas", "co", or None for whatever the caller said."""
    if not text:
        return None
    text = text.replace("’", "'")
    if _hits(_GAS_PATTERNS, text):
        return "gas"
    if _hits(_CO_PATTERNS, text):
        return "co"
    return None


def cannot_leave(text: str | None) -> bool:
    """The caller is saying they can't, or don't feel safe to, get out of the house."""
    return bool(text) and _CANT_LEAVE.search(text.replace("’", "'")) is not None
