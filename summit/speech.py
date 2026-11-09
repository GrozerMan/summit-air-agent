"""Turning spoken numbers into digits, and digits back into something TTS reads well."""

import re

_DIGIT_WORDS = {
    "zero": "0", "oh": "0", "o": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
}  # fmt: skip

_MULTIPLIERS = {"double": 2, "triple": 3}
_TEENS = {
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14", "fifteen": "15",
    "sixteen": "16", "seventeen": "17", "eighteen": "18", "nineteen": "19",
}  # fmt: skip
_TENS = {
    "twenty": "2", "thirty": "3", "forty": "4", "fifty": "5", "sixty": "6", "seventy": "7", "eighty": "8",
    "ninety": "9",
}  # fmt: skip
_UNITS = {k: v for k, v in _DIGIT_WORDS.items() if v != "0"}
# "516 555 0142, no wait, 0124": what comes after one of these replaces the end.
_CORRECTION = re.compile(
    r"\b(?:no\s+wait|wait\s+no|i\s+mean|sorry|actually|correction|scratch\s+that)\b", re.I
)


def spoken_digits(text: str) -> str:
    """Pull the digits out of something like "five one six, five fifty-five, oh one four two".

    STT usually gives digits already, but callers say "oh", "double five" and
    "fifty-five", and the transcript keeps those as words often enough to matter.
    """
    digits: list[str] = []
    repeat = 1
    tokens = re.findall(r"[a-z]+|\d", text.lower())
    i = 0
    while i < len(tokens):
        token = tokens[i]
        i += 1
        if token in _MULTIPLIERS:
            repeat = _MULTIPLIERS[token]
            continue
        if token in _TENS:
            # "fifty-five" is 55, a bare "fifty" is 50.
            unit = _UNITS.get(tokens[i]) if i < len(tokens) else None
            group = _TENS[token] + (unit or "0")
            i += 1 if unit else 0
        elif token == "hundred" and digits:
            group = "00"  # "eight hundred"
        else:
            group = token if token.isdigit() else _TEENS.get(token) or _DIGIT_WORDS.get(token)
        if group is not None:
            digits.extend(group * repeat)
        repeat = 1
    return "".join(digits)


def normalize_phone(text: str | None) -> str | None:
    """Return a US number in E.164 form (+15165550142), or None if it isn't one."""
    if not text:
        return None
    digits = spoken_digits(text)
    parts = _CORRECTION.split(text)
    if len(parts) > 1 and len(digits) > 11:
        # "516 555 0142, no wait, 0124": the correction replaces the end of the number.
        before, after = spoken_digits(" ".join(parts[:-1])), spoken_digits(parts[-1])
        if len(after) >= 10:
            digits = after
        elif after and len(before) >= 10:
            digits = before[-10:][: 10 - len(after)] + after
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10 or digits[0] in "01":
        return None
    return "+1" + digits


def normalize_zip(text: str | None) -> str | None:
    if not text:
        return None
    digits = spoken_digits(text)
    return digits if len(digits) == 5 else None


def say_phone(e164: str) -> str:
    """Format +15165550142 as 516-555-0142, which TTS reads out digit by digit."""
    digits = e164.removeprefix("+1")
    return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"


_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]


def say_hotline(number: str) -> str:
    """Spell a phone number out for TTS, group by group: "1-800-490-0045" becomes
    "one, eight hundred, four nine zero, zero zero four five".

    Used for numbers a caller has to remember under stress, where TTS reading
    "490" as "four hundred ninety" costs them a second they don't have.
    """
    groups = re.findall(r"\d+", number)
    spoken = []
    for group in groups:
        if group in ("800", "888"):
            spoken.append("eight hundred" if group == "800" else "triple eight")
        else:
            spoken.append(" ".join(_WORDS[int(d)] for d in group))
    return ", ".join(spoken)


def plain_speech(text: str) -> str:
    """Flatten markdown in a stretch of the model's reply to something a voice can say.

    The prompt says no lists and no markdown, but models format for a screen anyway, and
    TTS then reads asterisks out loud, or runs a bulleted list together into one breathless
    sentence. Bullets become clauses ("A, B, or C" rather than "dash A dash B"). Spacing at
    either end is kept, because this runs on the stream a sentence at a time. Numbered lists
    are left alone: streamed a sentence at a time, "1. " looks just like the "555. " of a
    phone number read back in groups, and losing digits there would fail the read-back check.
    """
    if not text.strip():
        return text
    lead = " " if text[0].isspace() else ""
    trail = " " if text[-1].isspace() else ""
    body = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    body = re.sub(r"(?<!\w)[*_](\S(?:.*?\S)?)[*_](?!\w)", r"\1", body)
    body = re.sub(r"`([^`]+)`", r"\1", body)
    body = re.sub(r"(?m)^\s*#{1,6}\s*", "", body)
    out = ""
    for raw in body.splitlines():
        line = re.sub(r"^\s*[-*+•–—]\s+", "", raw).strip()
        if not line:
            continue
        if not out:
            out = line
        elif out.endswith((".", "!", "?", ":", ",", ";")):
            out += " " + line
        else:
            out += ", " + line
    out = re.sub(r"\s{2,}", " ", out).strip()
    return f"{lead}{out}{trail}" if out else lead or trail


def say_confirmation(appointment_id: int) -> str:
    """The appointment number as four or more digits, said one by one ("0 0 4 7"), so it
    sounds like a confirmation number and the caller can write it down. It's the number
    the office looks the visit up by (appointment #47)."""
    return " ".join(f"{appointment_id:04d}")
