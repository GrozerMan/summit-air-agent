"""The deterministic P0 net under the model. Every miss here is a caller who gets
offered an appointment instead of told to leave, so the "must catch" list grows
whenever a test call finds a new way to say it."""

import pytest

from summit.hazard_words import cannot_leave, hazard_in
from summit.speech import say_hotline

MUST_CATCH_GAS = [
    # Test call P0-01, as the caller said it and as the model summarized it.
    "So we've got this smell coming from our furnace. It's kinda like a skunk. It's pretty nasty. "
    "It happened earlier today. But now it's gone.",
    "nasty skunk-like smell from furnace earlier but now gone",
    "rotten eggs earlier but it stopped",
    "It smelled like rotten egg in the basement",
    "There's a sulfur smell near the furnace",
    "kind of a sulphury smell",
    "My husband thought he smelled gas this morning",
    "it smells like gas",
    "No, it smells like gas",
    "I'm not sure, but it smells like propane",
    "not sure it smells like gas",
    "Doesn't that smell like gas?",
    "I don't think it's anything but there's a gas smell",
    "the gas smell is gone now",
    "I think we have a gas leak",
    "smells like the gas stove when you leave it on",
    "there's a smell by the gas meter",
    "a weird smell near the gas line",
]

MUST_NOT_FIRE = [
    # Negative control: normal on the first heating day of the season.
    "dusty burning smell, first time turning heat on this year",
    "I need a tune-up on my gas furnace",
    "there's a burning smell from my gas furnace",
    "my gas bill is really high",
    "it smells weird, it's a gas furnace",
    "the furnace is making a banging noise",
    "No, I don't smell gas",
    "no gas smell, it's just dusty",
    "it doesn't smell like gas at all",
    "There's no smell of gas",
    "I never smelled propane",
    "Do you service gas water heaters?",
    "",
]


@pytest.mark.parametrize("text", MUST_CATCH_GAS)
def test_gas_words_are_caught(text):
    assert hazard_in(text) == "gas"


@pytest.mark.parametrize("text", MUST_NOT_FIRE)
def test_ordinary_calls_do_not_fire(text):
    assert hazard_in(text) is None


@pytest.mark.parametrize(
    "text",
    [
        "my carbon monoxide detector keeps going off",
        "the CO alarm went off earlier",
        "Isn't the CO alarm going off?",
    ],
)
def test_sounding_co_alarm_is_caught(text):
    assert hazard_in(text) == "co"


@pytest.mark.parametrize(
    "text",
    [
        # A chirp is usually a low battery: the agent asks, it doesn't evacuate.
        "the CO detector is chirping",
        "the CO detector isn't going off",
        "should I buy a carbon monoxide detector",
    ],
)
def test_co_without_an_alarm_sounding_does_not_fire(text):
    assert hazard_in(text) is None


@pytest.mark.parametrize(
    "text",
    [
        "It's kinda dark outside. And I don't feel safe leaving.",  # test call P0-01
        "I can't leave, my mom is in a wheelchair",
        "I'm not going to leave",
        "I can't get out of the house",
    ],
)
def test_cannot_leave(text):
    assert cannot_leave(text)


@pytest.mark.parametrize(
    "text",
    [
        "so I can't go back in until they say it's safe?",
        "Okay. I'm gonna hang up and do that.",
        "Okay. Is this really necessary?",
        "I'm leaving now",
    ],
)
def test_leaving_or_asking_is_not_cannot_leave(text):
    assert not cannot_leave(text)


def test_hotline_is_spelled_for_tts():
    assert say_hotline("1-800-490-0045") == "one, eight hundred, four nine zero, zero zero four five"
    assert say_hotline("1-800-752-6633") == "one, eight hundred, seven five two, six six three three"
