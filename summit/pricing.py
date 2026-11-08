"""What Summit Air charges, and what the agent may say about it. All figures come
from config/business.toml; repairs are never priced over the phone."""

import re
from collections.abc import Iterable
from typing import Any

# Asking what a repair or part costs. Matched as whole words: "part" used to match
# "apartment", "fan" matched "infant" and "total" matched "totally".
_REPAIR_COST_WORDS = (
    "repair",
    "repairs",
    "fix",
    "fixing",
    "part",
    "parts",
    "replace",
    "replacing",
    "how much will",
    "total",
)
# Components: a question about one of these is a repair question, unless it's about the visit.
_COMPONENT_WORDS = (
    "capacitor", "compressor", "motor", "fan", "coil", "blower", "igniter", "ignitor", "thermostat",
    "sensor", "circuit board", "control board", "valve", "refrigerant", "freon", "recharge", "leak",
)  # fmt: skip
_SYSTEM_WORDS = (
    "new system", "new unit", "new furnace", "new boiler", "new ac", "new a/c", "new air conditioner",
    "new heat pump", "whole system", "system replacement", "replace the system", "replace my system",
    "replace the furnace", "replace my furnace", "replace the ac", "replace my ac", "install",
    "replacement", "estimate",
)  # fmt: skip
_AFTER_HOURS_WORDS = (
    "after hours", "after-hours", "weekend", "night", "tonight", "evening", "sunday", "saturday",
    "holiday", "late",
)  # fmt: skip
_VISIT_WORDS = ("diagnos", "service call", "visit", "come out", "trip", "look at", "send someone")


def _any_word(text: str, words: Iterable[str]) -> bool:
    return any(re.search(rf"\b{re.escape(w)}\b", text) for w in words)


def answer(item: str, cfg: dict[str, Any], is_member: bool) -> str:
    """The tool result for "how much is...": a figure from config, or an instruction not to give one."""
    text = item.lower()
    p = cfg["pricing"]
    after_hours = _any_word(text, _AFTER_HOURS_WORDS)
    surcharge = f" Visits outside office hours add ${p['after_hours_surcharge']}." if after_hours else ""
    system = _any_word(text, _SYSTEM_WORDS)
    visit = any(w in text for w in _VISIT_WORDS)  # stems: "diagnos" covers diagnostic
    repair = (_any_word(text, _REPAIR_COST_WORDS) and not system) or (
        _any_word(text, _COMPONENT_WORDS) and not visit
    )
    # Repairs and parts first: "a replacement capacitor" is a repair, not a free estimate.
    if repair:
        # No figure at all here: a "$129" next to "capacitor" gets relayed as the part's price.
        return (
            "Don't give a price for the repair or the part. The technician diagnoses it and quotes on "
            "site before any work starts. If they ask what the visit costs, look up the diagnostic visit."
        )
    if system:
        return "Estimates for a new or replacement system are free."
    if "tune" in text or "maintenance" in text:
        return f"A tune-up is ${p['tune_up']}. Members get two a year included." + surcharge
    if _any_word(text, ("member", "members", "membership", "club", "plan")) and not visit:
        benefits = ", ".join(cfg["membership"]["benefits"])
        return f"{cfg['membership']['name']}: {benefits}. The office can go over membership pricing."
    if after_hours or visit or _any_word(text, ("appointment", "come", "cost", "charge", "fee")):
        # Always the base and the surcharge together, never "+$99" on its own.
        return diagnostic(cfg, is_member) + surcharge
    return "Don't estimate repairs. The technician quotes on site before any work starts."


def diagnostic(cfg: dict[str, Any], is_member: bool) -> str:
    p = cfg["pricing"]
    if is_member:
        return f"The diagnostic visit is free for members (${p['diagnostic']} otherwise)."
    return f"The diagnostic visit is ${p['diagnostic']}; it's free for {cfg['membership']['name']} members."


def confirmation_line(job_type: str, after_hours: bool, cfg: dict[str, Any], is_member: bool) -> str:
    """The price line of the spoken booking confirmation."""
    p = cfg["pricing"]
    job = job_type.lower()
    if "tune" in job or "maintenance" in job:
        price = (
            "The tune-up is included in your membership." if is_member else f"The tune-up is ${p['tune_up']}."
        )
    elif "estimate" in job or "replacement" in job:
        price = "The estimate is free."
    elif is_member:
        price = (
            "As a member there's no diagnostic fee, and the technician will quote any repair before starting."
        )
    else:
        price = f"The diagnostic visit is ${p['diagnostic']}, and the technician will quote any repair before starting."
    if after_hours:
        price += f" Because it's outside regular hours, there's an extra ${p['after_hours_surcharge']}."
    return price
