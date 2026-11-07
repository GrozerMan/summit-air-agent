"""Is the address one we serve, and is it a home?

ZIPs come from config/service_area.csv (every ZIP in our counties, generated from
GeoNames), so a ZIP is a definite yes or no. Town names are fuzzier: callers say
neighborhoods, hamlets and boroughs, and STT spells them its own way ("Rockville
Center"). An unrecognised town is never a no on its own: the agent asks for the ZIP.
"""

import csv
import difflib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from summit.speech import normalize_zip

_COMMERCIAL_WORDS = (
    "business", "office building", "store", "shop", "restaurant", "warehouse", "commercial",
    "school", "church", "factory", "hotel", "clinic", "salon", "gym", "rooftop unit", "rtu",
    "building-wide", "whole building", "central plant", "landlord", "property manager",
    "management company", "the building's boiler", "building boiler", "my tenants", "our tenants",
)  # fmt: skip
_RESIDENTIAL_WORDS = (
    "house", "home", "condo", "apartment", "unit", "townhouse", "two-family",
    "two family", "three-family", "three family", "four-family", "four family", "duplex",
    "residence", "co-op", "coop", "brownstone", "rowhouse", "row house", "mobile home",
)  # fmt: skip
# "a 6-unit building", "twelve unit", "40 apartments": past four units it's a
# building owner's job, which Summit Air treats as commercial.
_NUMBER_WORDS = {
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "fifteen": 15, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "hundred": 100,
}  # fmt: skip
_UNITS = re.compile(
    r"\b(\d+|" + "|".join(_NUMBER_WORDS) + r")[\s-]*(?:units?|apartments?|famil(?:y|ies)|tenants?)\b", re.I
)
_MAX_RESIDENTIAL_UNITS = 4
_OWNS_BUILDING = re.compile(r"\b(?:i|we)\s+own\b|\b(?:my|our)\s+(?:building|property)\b|\bi'?m\s+the\s+owner\b", re.I)

_STATES = (
    "alabama|alaska|arizona|arkansas|california|colorado|connecticut|delaware|florida|georgia|hawaii|"
    "idaho|illinois|indiana|iowa|kansas|kentucky|louisiana|maine|maryland|massachusetts|michigan|"
    "minnesota|mississippi|missouri|montana|nebraska|nevada|new hampshire|new jersey|new mexico|"
    "north carolina|north dakota|ohio|oklahoma|oregon|pennsylvania|rhode island|south carolina|"
    "south dakota|tennessee|texas|utah|vermont|virginia|washington|west virginia|wisconsin|wyoming"
)
# A town followed by another state: "Long Beach, California", "Hoboken NJ". Only the
# unambiguous two-letter codes; "in", "me" and "or" are words.
_OTHER_STATES = re.compile(rf"\b(?:{_STATES}|nj|ct|pa|ca|fl|tx|ma|nc|sc|va|md|nh|vt|ri|conn)\s*$", re.I)
_ASK_BOROUGH = {"nyc", "new york city", "the city", "city"}
_FUZZY_CUTOFF = 0.85


@dataclass
class AreaCheck:
    in_area: bool
    county: str | None
    zip: str | None
    message: str
    ask_zip: bool = False  # not sure yet: ask for the ZIP before deciding
    outside: bool = False  # definitely not ours, as opposed to "not sure yet"


# Loading


def load_area(cfg: dict[str, Any], csv_path: Path) -> None:
    """Add `zips` {zip: county} and `places` {normalized name: (name, counties)} to
    cfg["service_area"], from the CSV plus the aliases in business.toml."""
    area = cfg["service_area"]
    counties = set(area["counties"])
    zips: dict[str, str] = {}
    places: dict[str, tuple[str, set[str]]] = {}

    def add_place(name: str, county: str) -> None:
        key = normalize_place(name)
        if key:
            places.setdefault(key, (name, set()))[1].add(county)

    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(line for line in f if not line.startswith("#")):
            if row["county"] in counties:
                zips[row["zip"]] = row["county"]
                add_place(row["place"], row["county"])
    for name, county in area.get("aliases", {}).items():
        if county not in counties:
            raise ValueError(f"alias {name!r} points at {county!r}, which isn't a served county")
        add_place(name, county)
    area["zips"] = zips
    area["places"] = places


def normalize_place(text: str) -> str:
    """"Rockville Centre, NY" and "rockville center" both become "rockville center"."""
    text = text.lower().replace("’", "'").replace("'", "").replace(".", "")
    words = re.sub(r"[^a-z0-9]+", " ", text).split()
    swaps = {"centre": "center", "saint": "st", "mount": "mt", "fort": "ft"}
    words = [swaps.get(w, w) for w in words]
    while words and words[0] in ("the", "village", "town", "city", "of", "in") and len(words) > 1:
        words = words[1:]
    if words[-2:] == ["new", "york"] and len(words) > 2:
        words = words[:-2]
    while len(words) > 1 and words[-1] in ("ny", "county", "borough"):
        words = words[:-1]
    return " ".join(words)


def area_name(county: str, cfg: dict[str, Any]) -> str:
    """How to say a county: "Brooklyn", "Nassau County"."""
    return cfg["service_area"].get("names", {}).get(county, f"{county} County")


def served_areas(cfg: dict[str, Any]) -> str:
    names = [area_name(c, cfg) for c in cfg["service_area"]["counties"]]
    return ", ".join(names[:-1]) + f" and {names[-1]}"


# Checks


def check_zip(raw: str, cfg: dict[str, Any]) -> AreaCheck:
    zip_code = normalize_zip(raw)
    if zip_code is None:
        return AreaCheck(False, None, None, f"'{raw}' isn't a 5-digit ZIP. Ask them to repeat it.", ask_zip=True)
    county = cfg["service_area"]["zips"].get(zip_code)
    if county:
        return AreaCheck(True, county, zip_code, f"{zip_code} is in {area_name(county, cfg)}, which we serve.")
    return _out_of_area(zip_code, cfg)


def check_town(town: str, cfg: dict[str, Any], zip_code: str | None = None) -> AreaCheck:
    """A town, neighborhood or borough. Only a ZIP gets a definite no."""
    places = cfg["service_area"]["places"]
    key = normalize_place(town)
    # A known place wins over a state name: "Port Washington" isn't in Washington.
    if key not in places and _OTHER_STATES.search(town.strip()):
        return _out_of_area(zip_code, cfg, place=town)
    if key in _ASK_BOROUGH:
        return AreaCheck(
            False, None, zip_code, "Ask which borough, or better, the ZIP code.", ask_zip=True
        )

    match, guessed = key, False
    if key not in places:
        close = difflib.get_close_matches(key, places.keys(), n=1, cutoff=_FUZZY_CUTOFF)
        if not close:
            return AreaCheck(
                False,
                None,
                zip_code,
                f"{town} isn't a place on our list, which doesn't mean we don't serve it. Ask for the "
                "ZIP code before deciding; if they don't know it, ask which county or borough.",
                ask_zip=True,
            )
        match, guessed = close[0], True

    name, counties = places[match]
    if len(counties) > 1:
        both = " or ".join(sorted(area_name(c, cfg) for c in counties))
        return AreaCheck(
            False, None, zip_code, f"{name} could be {both}. Ask for the ZIP code to be sure.", ask_zip=True
        )
    county = next(iter(counties))
    spoken = area_name(county, cfg)
    if normalize_place(spoken) == match:
        message = f"{name} is in our service area."
    else:
        message = f"{name} is in {spoken}, which we serve."
    if guessed:
        message = f"Sounds like {name}: confirm the town with them. " + message
    return AreaCheck(True, county, zip_code, message)


def place_in(sentence: str, cfg: dict[str, Any]) -> tuple[str, str | None] | None:
    """A served place named in a sentence: (name, county), county None if ambiguous."""
    text = f" {normalize_place(sentence)} "
    best = None
    for key, (name, counties) in cfg["service_area"]["places"].items():
        if f" {key} " in text and (best is None or len(key) > len(best[0])):
            best = (key, name, counties)
    if best is None:
        return None
    _, name, counties = best
    return name, next(iter(counties)) if len(counties) == 1 else None


def _out_of_area(zip_code: str | None, cfg: dict[str, Any], place: str | None = None) -> AreaCheck:
    where = place or zip_code
    return AreaCheck(
        False,
        None,
        zip_code,
        f"{where} is outside our service area ({served_areas(cfg)}). Let them know kindly and "
        "suggest a local HVAC company. Don't book or offer a callback unless they ask.",
        outside=True,
    )


def property_kind(description: str) -> str:
    """'residential', 'commercial' or 'unknown'. Homes of up to four units count as residential."""
    text = description.lower()
    if _mentions(text, _COMMERCIAL_WORDS) or _too_many_units(text):
        return "commercial"
    if _mentions(text, _RESIDENTIAL_WORDS):
        return "residential"
    return "unknown"


def _too_many_units(text: str) -> bool:
    """The caller owns a building of more than four units. Someone who lives in one
    (a condo or co-op with their own equipment) is still a residential customer."""
    if not _OWNS_BUILDING.search(text):
        return False
    for match in _UNITS.finditer(text):
        raw = match.group(1).lower()
        count = int(raw) if raw.isdigit() else _NUMBER_WORDS[raw]
        if count > _MAX_RESIDENTIAL_UNITS:
            return True
    return False


def _mentions(text: str, words: tuple[str, ...]) -> bool:
    return any(re.search(rf"\b{re.escape(word)}\b", text) for word in words)
