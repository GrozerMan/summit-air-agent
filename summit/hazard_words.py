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
the caller's time, and a missed gas leak can cost a house. The carve-outs are narrow:

- A plain denial, with the negating word right before the hazard word ("I don't
  smell gas", "no smoke or sparks"). "It won't stop smelling like gas" and "I can't
  stand the rotten egg smell" are not denials.
- A denial of the present is an admission of the past: "I don't smell gas anymore",
  "no sparks now" stay P0, like "it's gone now".
- A question someone answered no: "I asked my wife if it smells like gas and she
  said no".
- HVAC words that only look like fire: the furnace "won't fire" or "fires up", a
  spark igniter, a smoke detector chirping.
- Everyday words that only look like fire: "it's smoking hot in here", "my husband
  smokes", cigarette smoke, "a fire going in the fireplace".
"""

import re

# Odor words that mean a possible leak by themselves. Utilities add mercaptan to
# gas so it smells like rotten eggs, sulfur or skunk, and callers use all three.
_ODORANT = r"rotten[\s-]*eggs?|sul(?:f|ph)ur\w*|skunk\w*|mercaptan|egg(?:y|ish)"

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
    # "I think the gas is leaking", "the gas line might be leaking"
    re.compile(
        rf"\b(?:gas|propane)\b(?!\s+(?:{_FUEL_THING})\b)(?:\s+\w+)?\s+"
        r"(?:is|was|'s|might\s+be|may\s+be|could\s+be|seems\s+to\s+be)\s+leak\w*",
        re.I,
    ),
    re.compile(rf"\b(?:{_SMELL})\s+(?:like\s+)?(?:rotten\s+)?eggs?\b", re.I),
    # Suspicion with no smell word: "it might be gas", "I'm worried it's gas".
    re.compile(
        r"\b(?:might\s+be|may\s+be|could\s+be|must\s+be|worried\s+(?:it'?s|it\s+is|about)|"
        r"afraid\s+(?:it'?s|it\s+is))\s+(?:a\s+|the\s+)?(?:gas|propane)\b"
        rf"(?!\s+(?:{_FUEL_THING}|heat|line|pipe|stove|meter|tank)\b)",
        re.I,
    ),
]

# A CO alarm that is sounding. A chirp is usually a low battery, so "chirping" is
# deliberately missing: the agent should ask about it, not evacuate on it.
_CO = r"carbon\s+monoxide|co|c\.o\.|c\s+o"
_DEVICE = r"alarms?|detectors?|monitors?|sensors?"
_SOUNDING = (
    r"going\s+off|went\s+off|goes\s+off|go\s+off|keeps\s+going|beep\w*|sound\w*|alarm\w*|ringing|"
    r"screaming|blaring|going\s+crazy|went\s+crazy|gone\s+crazy|won'?t\s+stop|flashing|triggered"
)
_CO_PATTERNS = [
    re.compile(rf"\b(?:{_CO})\s+(?:{_DEVICE})\b(?:\W+\w+){{0,3}}?\W+(?:{_SOUNDING})", re.I),
    # "the detector for carbon monoxide keeps beeping", "the alarm that says CO on it is going off"
    re.compile(
        rf"\b(?:{_DEVICE})\s+(?:for|that\s+(?:says|reads|detects))\s+(?:{_CO})\b"
        rf"(?:\W+\w+){{0,4}}?\W+(?:{_SOUNDING})",
        re.I,
    ),
    re.compile(r"\bcarbon\s+monoxide\s+(?:leak\w*|poison\w*)", re.I),
    # "Carbon monoxide alarm." said as what's happening, not "I have a CO alarm".
    re.compile(
        r"(?<!\ba\s)(?<!\ban\s)(?<!\bmy\s)(?<!\bnew\s)\b(?:carbon\s+monoxide|co)\s+alarm\b"
        r"(?!s|\s+(?:battery|batteries|chirp\w*|expired|install\w*|test\w*|needs|is\s+chirp\w*))",
        re.I,
    ),
]

# CO symptoms. One symptom alone ("this AC is giving me a headache") isn't enough;
# two kinds, or one that several people share or that started with the heat, is.
_SYMPTOMS = {
    "headache": r"headaches?",
    "dizzy": r"dizz\w*|light[\s-]?headed",
    "nausea": r"nause\w*|throwing\s+up|vomit\w*|sick\s+to\s+(?:my|our|their)\s+stomachs?",
    "drowsy": r"drowsy|sleepy|groggy|confused|faint\w*|passed\s+out",
}
_SYMPTOM_PATTERNS = {k: re.compile(rf"\b(?:{v})\b", re.I) for k, v in _SYMPTOMS.items()}
_SEVERAL_PEOPLE = re.compile(
    r"\b(?:we|we'?ve|we'?re|we\s+all|everyone|everybody|all\s+of\s+us|both\s+of\s+us|the\s+kids|"
    r"my\s+kids|the\s+family|family'?s?|whole\s+family|whole\s+house(?:hold)?|husband|wife|kids)\b",
    re.I,
)
_HEAT_CONTEXT = re.compile(
    r"\b(?:furnace|boiler|heater|heat(?:ing)?\s+(?:came|comes|went|turned|kicked)\s+on|since\s+the\s+heat|"
    r"when\s+the\s+heat|space\s+heater|generator|fireplace)\b",
    re.I,
)

# Smoke, sparks, flames. HVAC speech is full of fire words that aren't fires: a furnace
# that "won't fire" or "fires up", a spark igniter, a smoke detector with a low battery.
_FIRE_PATTERNS = [
    re.compile(r"\bspark(?:s|ed|ing|y)?\b(?!\s*-?\s*(?:igniters?|ignitors?|ignition|electrodes?|plugs?))", re.I),
    re.compile(r"\bsmok(?:e|ed|es|ing|y|ey)\b(?!\s+(?:detectors?|alarms?)\b)", re.I),
    re.compile(
        r"\bsmoke\s+(?:detectors?|alarms?)\b(?:\W+\w+){0,3}?\W+"
        r"(?:going\s+off|went\s+off|goes\s+off|blaring|screaming|beep\w*|sounding|won'?t\s+stop)",
        re.I,
    ),
    re.compile(r"\bflames\b", re.I),
    re.compile(
        r"\bflame\b(?:\W+\w+){0,3}?\W+(?:coming|shooting|out\s+of|outside|from\s+the\s+(?:vent|register|unit))",
        re.I,
    ),
    re.compile(r"\b(?:on|caught|catching|catch)\s+fire\b", re.I),
    re.compile(
        r"\bfire\b(?!\s+(?:up|it\s+up|off|department|hazard|risk|code|marshal|pit|extinguisher|place)\b)",
        re.I,
    ),
]
# A word right before "fire" that makes it the burner lighting: "tries to fire", "the furnace will fire".
_FIRE_AS_BURNER = {
    "to", "will", "would", "should", "can", "could", "it'll", "burner", "furnace", "boiler",
    "heater", "pilot", "then", "finally", "igniter", "ignitor", "not",
}  # fmt: skip
_IGNITER = {"igniter", "ignitor", "igniters", "ignitors", "electrode", "pilot"}

_NEGATION = re.compile(
    r"no|not|never|none|nothing|nobody|without|denies|denied|deny|\w+n't|dont|doesnt|didnt|isnt|wasnt|"
    r"cant|wont|havent|hasnt",
    re.I,
)
# Words that may sit between a negation and the hazard without breaking the denial:
# "I don't SEE ANY smoke", "no smoke OR sparks", "I haven't SMELLED gas".
_DENIAL_FILLER = {
    "any", "a", "an", "or", "and", "nor", "even", "ever", "really", "see", "seen", "saw",
    "notice", "noticed", "smell", "smelled", "smelt", "have", "has", "had", "hear", "heard",
    "detect", "detected", "get", "got", "spark", "sparks", "sparking", "smoke", "smoking",
    "flames", "fire", "gas", "of", "sign", "signs", "evidence",
}  # fmt: skip
# "not sure", "don't know", "don't think" are doubt, not denial: still escalate.
_HEDGES = {"sure", "know", "certain", "positive", "think"}
# A denial of right now is an admission of earlier: "I don't smell gas anymore".
_ONLY_NOW = re.compile(
    r"\b(?:now|anymore|any\s+more|no\s+longer|at\s+the\s+moment|currently|at\s+this\s+point)\b", re.I
)
# "I asked my wife if it smells like gas" ... "and she said no".
_ASKED = re.compile(r"\b(?:asked|asking|ask|checked|checking|check)\b(?:\W+\w+){0,4}?\W+(?:if|whether)\b", re.I)
_ANSWER = re.compile(r"\b(?:said|says|answered|replied|told\s+me)\b\W+(?:that\W+)?(.{0,40})", re.I)
_ANSWER_NO = re.compile(
    r"^(?:no|nope|nah|not|nothing|just|only|dusty|definitely\s+not|it'?s\s+(?:just|only|not|dusty)|"
    r"it\s+(?:doesn'?t|does\s+not|isn'?t|wasn'?t|didn'?t)|(?:she|he|they)\s+(?:doesn'?t|didn'?t|don'?t))\b",
    re.I,
)
# "There's a skunk living under my porch": the animal, with no smell mentioned.
_SKUNK_ANIMAL = re.compile(
    r"^\w*\W+(?:living|lives|under|family|den|ran|walking|outside|in\s+(?:the|my|our)\s+"
    r"(?:yard|garden|porch|deck|shed|garage|crawl\s*space))\b",
    re.I,
)
_SMELL_WORD = re.compile(rf"\b(?:{_SMELL}|spray\w*)\b", re.I)

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
# The caller is going: "okay, I'm going outside now", "bye".
_LEAVING = re.compile(
    r"\b(?:bye|goodbye|good\s+bye|hanging\s+up|leaving\s+now|getting\s+out\s+now|on\s+(?:my|our)\s+way\s+out|"
    r"(?:i'?m|we'?re|i\s+am|we\s+are)\s+(?:leaving|outside|out(?:\s+of\s+the\s+house)?|getting\s+out|"
    r"heading\s+out|going\s+(?:out|outside)|walking\s+out|out\s+now))\b",
    re.I,
)


_WORD = re.compile(r"[\w']+")


def _clause_before(text: str, start: int) -> str:
    """The text between the last clause break and `start`."""
    head = text[:start]
    cut = max(head.rfind(p) for p in ".,;!?")
    return head[cut + 1 :]


def _sentence_before(text: str, start: int) -> str:
    head = text[:start]
    cut = max(head.rfind(p) for p in ".!?")
    return head[cut + 1 :]


def _clause_after(text: str, end: int) -> str:
    tail = text[end:]
    cuts = [i for i in (tail.find(p) for p in ".;!?") if i >= 0]
    return tail[: min(cuts)] if cuts else tail


def _negated(text: str, match: re.Match[str]) -> bool:
    """A plain denial: the negation sits right before the hazard ("doesn't smell like
    gas", "no gas smell", "no smoke or sparks"), or right before the alarm verb inside
    the match ("the CO alarm isn't going off"). A comma ends the scope, so "No, it
    smells like gas" still counts."""
    before = _WORD.findall(_clause_before(text, match.start()))
    for word in reversed(before):
        if _NEGATION.fullmatch(word):
            return True
        if word.lower() not in _DENIAL_FILLER:
            break
    inside = _WORD.findall(match.group(0))
    for word, following in zip(inside, inside[1:]):
        if _NEGATION.fullmatch(word) and following.lower() not in _HEDGES:
            return True
    return False


def _asked_and_denied(text: str, match: re.Match[str]) -> bool:
    """"I asked my wife if it smells like gas and she said no." A question about the
    hazard that got a no. Unanswered, or answered anything but no, it still counts."""
    if not _ASKED.search(_sentence_before(text, match.start())):
        return False
    answer = _ANSWER.search(text[match.end() : match.end() + 120])
    return bool(answer and _ANSWER_NO.match(answer.group(1).strip()))


def _not_a_hazard(text: str, match: re.Match[str]) -> bool:
    if _asked_and_denied(text, match):
        return True
    if _negated(text, match):
        # "I don't smell gas anymore", "it's not sparking now": it was there earlier.
        return not _ONLY_NOW.search(_clause_after(text, match.end()))
    return False


def _hits(patterns: list[re.Pattern[str]], text: str, skip=None) -> bool:
    for pattern in patterns:
        for match in pattern.finditer(text):
            if skip and skip(text, match):
                continue
            if not _not_a_hazard(text, match):
                return True
    return False


def _skunk_animal(text: str, match: re.Match[str]) -> bool:
    if not match.group(0).lower().startswith("skunk"):
        return False
    sentence = _sentence_before(text, match.start()) + _clause_after(text, match.start())
    return bool(_SKUNK_ANIMAL.match(text[match.start() :])) and not _SMELL_WORD.search(sentence)


def _burner_word(text: str, match: re.Match[str]) -> bool:
    """'fire' as the burner lighting, and sparks from an igniter."""
    before = _WORD.findall(_clause_before(text, match.start()))
    previous = before[-1].lower() if before else ""
    word = match.group(0).lower()
    if word == "fire":
        return previous in _FIRE_AS_BURNER
    if word.startswith("spark"):
        return previous in _IGNITER
    return False


# Smoke and fire words that aren't a fire in the house: "it's smoking hot in here" (a
# heat wave, no AC), "my husband smokes", "cigarette smoke", "a fire in the fireplace".
_PERSON_BEFORE = re.compile(
    r"\b(?:i|he|she|they|we|you|he'?s|she'?s|they'?re|husband|wife|son|daughter|dad|father|mom|mother|"
    r"roommate|tenant|neighbou?r|someone|somebody|guy|kids?)\s+(?:also\s+|still\s+|used\s+to\s+|is\s+|was\s+)?$",
    re.I,
)
_TOBACCO = re.compile(r"\b(?:cigarettes?|cigars?|weed|pot|marijuana|vap\w*|hookah|tobacco|smokers?)\b", re.I)
_HOT_AFTER = re.compile(r"\s*-?\s*hot\b", re.I)
_FIREPLACE_AFTER = re.compile(
    r"^(?:\W+\w+){0,5}?\W+(?:fireplace|fire\s*pit|firepit|wood\s*(?:burning\s+)?stove|chiminea)\b", re.I
)


def _not_a_house_fire(text: str, match: re.Match[str]) -> bool:
    if _burner_word(text, match):
        return True
    word = match.group(0).lower()
    after = text[match.end() :]
    if word.startswith("smok"):
        if _HOT_AFTER.match(after):
            return True
        clause = _clause_before(text, match.start()) + " " + _clause_after(text, match.end())
        return bool(_TOBACCO.search(clause) or _PERSON_BEFORE.search(_clause_before(text, match.start())))
    if word == "fire":
        return bool(_FIREPLACE_AFTER.match(after))
    return False


def _co_symptoms(text: str) -> bool:
    kinds = set()
    for kind, pattern in _SYMPTOM_PATTERNS.items():
        if any(not _not_a_hazard(text, m) for m in pattern.finditer(text)):
            kinds.add(kind)
    if len(kinds) >= 2:
        return True
    return bool(kinds) and bool(_SEVERAL_PEOPLE.search(text) or _HEAT_CONTEXT.search(text))


def hazard_in(text: str | None) -> str | None:
    """"gas", "co", "fire", or None for whatever the caller said."""
    if not text:
        return None
    text = text.replace("’", "'")
    if _hits(_GAS_PATTERNS, text, skip=_skunk_animal):
        return "gas"
    if _hits(_CO_PATTERNS, text) or _co_symptoms(text):
        return "co"
    if _hits(_FIRE_PATTERNS, text, skip=_not_a_house_fire):
        return "fire"
    return None


def leaving(text: str | None) -> bool:
    """The caller is on their way out or saying goodbye (and not saying they can't leave)."""
    if not text:
        return False
    text = text.replace("’", "'")
    return _LEAVING.search(text) is not None and not cannot_leave(text)


def cannot_leave(text: str | None) -> bool:
    """The caller is saying they can't, or don't feel safe to, get out of the house."""
    return bool(text) and _CANT_LEAVE.search(text.replace("’", "'")) is not None
