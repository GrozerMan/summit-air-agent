"""Turning spoken numbers into digits, and digits back into something TTS reads well."""

import re

_DIGIT_WORDS = {
    "zero": "0", "oh": "0", "o": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
}  # fmt: skip

_MULTIPLIERS = {"double": 2, "triple": 3}


def spoken_digits(text: str) -> str:
    """Pull the digits out of something like "five one six, five five five, oh one four two".

    STT usually gives digits already, but callers say "oh" and "double five", and
    the transcript keeps those as words often enough to be worth handling.
    """
    digits: list[str] = []
    repeat = 1
    for token in re.findall(r"[a-z]+|\d", text.lower()):
        if token in _MULTIPLIERS:
            repeat = _MULTIPLIERS[token]
            continue
        digit = token if token.isdigit() else _DIGIT_WORDS.get(token)
        if digit is not None:
            digits.extend(digit * repeat)
        repeat = 1
    return "".join(digits)


def normalize_phone(text: str | None) -> str | None:
    """Return a US number in E.164 form (+15165550142), or None if it isn't one."""
    if not text:
        return None
    digits = spoken_digits(text)
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
