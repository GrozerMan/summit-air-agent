import re
from dataclasses import dataclass
from typing import Any

from summit.speech import normalize_zip

# ZIP prefixes that fall in our counties. A ZIP with one of these prefixes that
# isn't on the curated list is probably ours but unverified, so we ask for the
# town rather than turn away a customer. Anything else is out of area.
_OUR_PREFIXES = ("105", "106", "107", "108", "110", "115", "117", "118", "119")

_COMMERCIAL_WORDS = (
    "business", "office building", "store", "shop", "restaurant", "warehouse", "commercial",
    "school", "church", "factory", "hotel", "clinic", "salon", "gym", "rooftop unit", "rtu",
    "building-wide", "whole building", "central plant",
)  # fmt: skip
_RESIDENTIAL_WORDS = (
    "house", "home", "condo", "apartment", "unit", "townhouse", "two-family",
    "two family", "three-family", "four-family", "duplex", "residence", "co-op",
)  # fmt: skip


@dataclass
class AreaCheck:
    in_area: bool
    county: str | None
    zip: str | None
    message: str
    ask_town: bool = False
    outside: bool = False  # definitely not ours, as opposed to "not sure yet"


def check_zip(raw: str, cfg: dict[str, Any]) -> AreaCheck:
    zip_code = normalize_zip(raw)
    if zip_code is None:
        return AreaCheck(False, None, None, f"'{raw}' isn't a 5-digit ZIP. Ask them to repeat it.")

    for county, zips in cfg["service_area"]["zips"].items():
        if zip_code in zips:
            return AreaCheck(True, county, zip_code, f"{zip_code} is in {county} County, which we serve.")

    if zip_code.startswith(_OUR_PREFIXES):
        return AreaCheck(
            False,
            None,
            zip_code,
            f"{zip_code} isn't on our list. Ask which town they're in before deciding.",
            ask_town=True,
        )
    return _out_of_area(zip_code, cfg)


def check_town(town: str, cfg: dict[str, Any], zip_code: str | None = None) -> AreaCheck:
    wanted = " ".join(town.lower().replace("-", " ").split())
    for name, county in cfg["service_area"]["towns"].items():
        if name.lower() == wanted:
            return AreaCheck(True, county, zip_code, f"{name} is in {county} County, which we serve.")
    return _out_of_area(zip_code, cfg, place=town)


def _out_of_area(zip_code: str | None, cfg: dict[str, Any], place: str | None = None) -> AreaCheck:
    counties = ", ".join(cfg["service_area"]["counties"])
    where = place or zip_code
    return AreaCheck(
        False,
        None,
        zip_code,
        f"{where} is outside our service area ({counties} counties). Let them know kindly and "
        "suggest a local HVAC company. Don't book or offer a callback unless they ask.",
        outside=True,
    )


def property_kind(description: str) -> str:
    """'residential', 'commercial' or 'unknown'. 2-4 family homes count as residential."""
    text = description.lower()
    if _mentions(text, _COMMERCIAL_WORDS):
        return "commercial"
    if _mentions(text, _RESIDENTIAL_WORDS):
        return "residential"
    return "unknown"


def _mentions(text: str, words: tuple[str, ...]) -> bool:
    return any(re.search(rf"\b{re.escape(word)}\b", text) for word in words)
