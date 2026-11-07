import pytest

from summit.service_area import check_town, check_zip, property_kind
from summit.speech import normalize_phone, normalize_zip, say_phone


@pytest.mark.parametrize(
    "spoken",
    [
        "516-555-0142",
        "(516) 555 0142",
        "+1 516 555 0142",
        "five one six five five five oh one four two",
        "five one six, double five five, zero one four two",
    ],
)
def test_phone_numbers_normalize(spoken):
    assert normalize_phone(spoken) == "+15165550142"


@pytest.mark.parametrize("bad", ["555 0142", "516 555 01422 9", "", None, "011 555 0142 22"])
def test_bad_phone_numbers_are_rejected(bad):
    assert normalize_phone(bad) is None


def test_phone_is_read_back_in_groups():
    assert say_phone("+15165550142") == "516-555-0142"


def test_spoken_zip():
    assert normalize_zip("one one five oh one") == "11501"
    assert normalize_zip("1150") is None


def test_known_zip_maps_to_county(cfg):
    check = check_zip("11501", cfg)
    assert check.in_area and check.county == "Nassau"


def test_every_zip_in_our_counties_is_listed(cfg):
    # Elmont, Inwood, Bayville and Carle Place were turned away by the old curated list.
    for zip_code, county in [("11003", "Nassau"), ("11096", "Nassau"), ("11709", "Nassau"), ("11514", "Nassau")]:
        assert check_zip(zip_code, cfg).county == county


def test_nyc_boroughs_are_served(cfg):
    for zip_code, county in [("11215", "Kings"), ("11375", "Queens"), ("10463", "Bronx"),
                             ("10001", "New York"), ("10301", "Richmond")]:  # fmt: skip
        check = check_zip(zip_code, cfg)
        assert check.in_area and check.county == county


def test_a_zip_outside_our_counties_is_a_definite_no(cfg):
    for zip_code in ("07030", "10956", "06830"):  # Hoboken, Rockland, Greenwich CT
        check = check_zip(zip_code, cfg)
        assert check.outside and not check.in_area
        assert "outside our service area" in check.message


def test_garbled_zip_asks_to_repeat(cfg):
    check = check_zip("115", cfg)
    assert not check.in_area and check.zip is None


def test_town_fallback_ignores_case_and_spacing(cfg):
    assert check_town("  garden   city ", cfg).county == "Nassau"
    assert check_town("white-plains", cfg).county == "Westchester"
    assert check_town("Mineola, NY", cfg).county == "Nassau"


def test_towns_the_old_list_missed_are_served(cfg):
    for town in ("Syosset", "Port Washington", "Merrick", "Plainview", "East Meadow", "Yorktown Heights"):
        assert check_town(town, cfg).in_area, town


def test_stt_spellings_still_match(cfg):
    assert check_town("Rockville Center", cfg).county == "Nassau"
    guessed = check_town("Masapequa", cfg)
    assert guessed.county == "Nassau" and "confirm the town" in guessed.message


def test_neighborhoods_and_boroughs(cfg):
    assert check_town("Park Slope", cfg).county == "Kings"
    assert check_town("Astoria", cfg).county == "Queens"
    assert check_town("the Bronx", cfg).county == "Bronx"
    assert check_town("Manhattan", cfg).county == "New York"


def test_ambiguous_or_unknown_town_asks_for_the_zip_instead_of_turning_away(cfg):
    for town in ("Floral Park", "Inwood", "NYC", "Hoboken"):
        check = check_town(town, cfg)
        assert check.ask_zip and not check.in_area and not check.outside, town


def test_another_state_is_out_of_area(cfg):
    assert check_town("Hoboken NJ", cfg).outside
    assert check_town("Greenwich, CT", cfg).outside
    assert check_town("Long Beach, California", cfg).outside
    assert check_town("Port Washington", cfg).in_area  # not the state


def test_home_office_is_not_commercial():
    assert property_kind("house, the AC in my home office") == "residential"


@pytest.mark.parametrize(
    "description, kind",
    [
        ("I'm the landlord, it's a 6 unit building", "commercial"),
        ("I own a twelve unit building", "commercial"),
        ("the building's boiler is out", "commercial"),
        ("my apartment, it's a 40-unit building", "residential"),  # lives there, not the owner
        ("a two family house", "residential"),
        ("my co-op", "residential"),
        ("brownstone", "residential"),
    ],
)
def test_building_owners_are_commercial_but_residents_are_not(description, kind):
    assert property_kind(description) == kind


@pytest.mark.parametrize(
    "spoken, number",
    [
        ("five one six, five fifty-five, oh one four two", "+15165550142"),
        ("six three one, five fifty-five, oh one fifty-five", "+16315550155"),
        # A correction replaces the end of the number.
        ("516 555 0142 no wait 0124", "+15165550124"),
        ("five one six five five five zero one four two... I mean zero one two four", "+15165550124"),
    ],
)
def test_phone_numbers_in_tens_and_with_corrections(spoken, number):
    assert normalize_phone(spoken) == number
