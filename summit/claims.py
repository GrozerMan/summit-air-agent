"""What the agent said it did, checked against what the backend recorded.

The prompt says "never tell the caller something happened unless a tool just
confirmed it", and in one stress run the agent still said "your appointment is set
for tomorrow" with nothing booked. These checks run on the agent's own words at
hang-up (and in the eval grader), so a false claim gets flagged even when it
can't be stopped before it's spoken.
"""

import re

_SENTENCE = re.compile(r"(?<=[.!?])\s+")

# "You're booked", "I've scheduled you", "your appointment is set for tomorrow".
_BOOKED = re.compile(
    r"\b(?:you'?re|you\s+are|you'?ve\s+been|i'?ve|i\s+have|we'?ve|we\s+have|it'?s|that'?s|is|has\s+been)\s+"
    r"(?:all\s+|now\s+|been\s+)?(?:booked|scheduled|confirmed|set\s+(?:up\s+)?for)\b",
    re.I,
)
# "Someone will give you a call", "the office will call you back".
_CALLBACK = re.compile(
    r"\b(?:give\s+you\s+a\s+(?:call|ring)|call\s+you(?:\s+back)?|reach\s+out\s+to\s+you|be\s+in\s+touch|"
    r"callback\s+(?:is|has\s+been)\s+(?:set|scheduled|booked))\b",
    re.I,
)
# Words before the claim that make it an offer or a condition rather than a statement:
# "I can get you booked for...", "If you'd like, the office can call you back".
_NOT_A_CLAIM = re.compile(
    r"\b(?:would|could|can|shall|should|want|like|if|once|when|before|after|try|able|let\s+me|"
    r"not|never|haven'?t|hasn'?t|isn'?t|aren'?t|wasn'?t|can'?t|won'?t|don'?t|nothing)\b",
    re.I,
)


def _claims(pattern: re.Pattern[str], text: str) -> list[str]:
    found = []
    for sentence in _SENTENCE.split(text.replace("’", "'")):
        if sentence.rstrip().endswith("?"):
            continue
        for match in pattern.finditer(sentence):
            if not _NOT_A_CLAIM.search(sentence[: match.start()]):
                found.append(sentence.strip())
                break
    return found


def booking_claims(text: str) -> list[str]:
    """Sentences where the agent says something is booked or scheduled."""
    return _claims(_BOOKED, text)


def callback_claims(text: str) -> list[str]:
    """Sentences where the agent says someone will call the caller."""
    return _claims(_CALLBACK, text)


def false_claims(agent_text: str, *, has_booking: bool, has_callback: bool) -> list[str]:
    """What the agent claimed that the records don't back up."""
    problems = []
    if not has_booking:
        problems += [f"said booked with no appointment: {s!r}" for s in booking_claims(agent_text)]
    if not has_callback:
        problems += [f"promised a call with no callback: {s!r}" for s in callback_claims(agent_text)]
    return problems
