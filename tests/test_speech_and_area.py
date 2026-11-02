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


def test_unlisted_zip_in_our_region_asks_for_town(cfg):
    check = check_zip("11599", cfg)
    assert not check.in_area and check.ask_town


def test_brooklyn_is_out_of_area(cfg):
    check = check_zip("11215", cfg)
    assert not check.in_area and not check.ask_town
    assert "outside our service area" in check.message


def test_garbled_zip_asks_to_repeat(cfg):
    check = check_zip("115", cfg)
    assert not check.in_area and check.zip is None


def test_town_fallback_ignores_case_and_spacing(cfg):
    assert check_town("  garden   city ", cfg).county == "Nassau"
    assert check_town("white-plains", cfg).county == "Westchester"
    assert not check_town("Hoboken", cfg).in_area


@pytest.mark.parametrize(
    "description",
    ["single family house", "condo", "two-family home", "my apartment", "a 3 bedroom townhouse"],
)
def test_homes_are_residential(description):
    assert property_kind(description) == "residential"


@pytest.mark.parametrize(
    "description",
    ["restaurant", "dental office building", "rooftop unit on our store", "the whole building's boiler"],
)
def test_businesses_are_commercial(description):
    assert property_kind(description) == "commercial"


def test_home_office_is_not_commercial():
    assert property_kind("house, the AC in my home office") == "residential"
