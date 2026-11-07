"""The deterministic P0 net under the model. Every miss here is a caller who gets
offered an appointment instead of told to leave, so the "must catch" list grows
whenever a test call finds a new way to say it."""

import pytest

from summit.hazard_words import cannot_leave, hazard_in, leaving
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
    # Stress report M4: negation words that aren't denials of the smell.
    "It won't stop smelling like gas",
    "I can't stand the rotten egg smell in the basement",
    "I can't get rid of this gas smell",
    "We can't figure out where the gas smell is coming from",
    "The heat won't come on without a weird gas smell",
    # A denial of now is an admission of earlier.
    "It doesn't smell like gas now, but it did this morning",
    "I don't smell gas anymore. I did earlier though",
    "There's no gas smell now but there was one an hour ago",
    "I no longer smell gas",
    # Other phrasings the stress run found.
    "I think the gas is leaking",
    "smells eggy down by the furnace",
    "I wondered if it might be gas",
    "I asked my husband if he smelled gas",  # asked, never answered: still counts
    "I asked my wife if it smells like gas and she said yes",
    "it smells like a skunk in the basement",
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
    # Stress report H1: a question that got a no.
    "I asked my wife if it smells like gas and she said no, it's just a dusty smell. The heat's working, "
    "it's 68 inside. Can I get a tune-up?",
    "Asked if it smells like gas or rotten eggs; caller said it's just dusty",
    "There's a skunk living under my porch and my AC is broken",
    "it might be the gas furnace",
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
        # Stress report C3: 6 of 8 CO phrasings used to miss.
        "my CO detector is going crazy",
        "the detector for carbon monoxide keeps beeping",
        "the alarm that says CO on it is going off",
        "carbon monoxide alarm",
        "we all have headaches and the kids are dizzy",
        "the whole family's been really sleepy and nauseous since the heat came on",
        "I've been dizzy and nauseous all day",
    ],
)
def test_co_wording_and_symptoms_are_caught(text):
    assert hazard_in(text) == "co"


@pytest.mark.parametrize(
    "text",
    [
        "this AC is giving me a headache",
        "I have a CO alarm",
        "my carbon monoxide alarm needs a new battery",
        "do you install carbon monoxide alarms",
        "nobody has a headache or feels dizzy",
        "no, no headaches or dizziness",
    ],
)
def test_co_mentions_that_are_not_an_alarm_or_symptoms(text):
    assert hazard_in(text) is None


@pytest.mark.parametrize(
    "text",
    [
        # Stress report C3: P0 in only 3/6 live runs, because nothing but the model saw it.
        "My AC outdoor unit was sparking and now it keeps tripping the breaker",
        "it's not sparking now but it was earlier",
        "there's smoke coming from the vent",
        "there was a little smoke when it turned on",
        "I saw flames in the furnace",
        "I saw a flame coming out of the furnace door",
        "the furnace caught fire",
        "there's a fire in the basement",
        "the outlet sparked",
        "the smoke alarm is going off",
        # Still caught next to the everyday carve-outs below.
        "I smell smoke",
        "the furnace is smoking",
        "it smells smoky in the basement",
        "smoke coming from the fireplace into the room",
        "there is a fire near the furnace",
        "the fire alarm is going off",
    ],
)
def test_smoke_sparks_and_flames_are_caught(text):
    assert hazard_in(text) == "fire"


@pytest.mark.parametrize(
    "text",
    [
        # HVAC words that only look like fire.
        "the furnace won't fire",
        "it tries to fire but then shuts off",
        "the burner will fire and then shut off",
        "the boiler won't fire up",
        "it fires up then quits",
        "the igniter sparks but it won't light",
        "my smoke detector is chirping",
        "the flame keeps going out",
        "the flame sensor might be dirty",
        "is a space heater a fire hazard",
        # Denials.
        "no smoke or sparks, it just won't turn on",
        "No sparks, no smoke, nothing like that",
        "I haven't seen any smoke",
        "caller denies smoke or sparks",
        # Everyday words that only look like fire. "Smoking hot" on a no-AC call made
        # the call a permanent P0 and read the evacuation script to someone who was hot.
        "the AC is out and it's smoking hot in here",
        "it's smoking-hot upstairs",
        "my husband smokes, could that be the smell",
        "I smoke but never inside",
        "smells like cigarette smoke in the vents",
        "there was a fire in the fireplace and now the heat stopped",
        "we had a fire going in the wood stove",
        # Round-2 stress probes.
        "Nothing's sparking right now, it just won't heat.",
        "My fire alarm keeps chirping, and separately the AC needs a tune-up.",
        "I live on Fire Island, can you do a furnace tune-up?",
        "The burner flames look nice and blue, but the blower is loud.",
        "It clicks and sparks but won't light, and the heat's off.",
        "First time running the heat this year and it smells a bit smoky, like burnt dust.",
        "Can you do the smoke test on my ducts?",
        "My neighbor's house had a fire last year so I want my furnace checked.",
    ],
)
def test_hvac_fire_words_and_denials_do_not_fire(text):
    assert hazard_in(text) is None


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


@pytest.mark.parametrize("text", ["Okay, I'm going outside now. Bye.", "Goodbye", "We're leaving now"])
def test_leaving(text):
    assert leaving(text)


@pytest.mark.parametrize(
    "text", ["I can't leave, my mom is in a wheelchair", "what do I do", "Should I leave?"]
)
def test_not_leaving(text):
    assert not leaving(text)


def test_hotline_is_spelled_for_tts():
    assert say_hotline("1-800-490-0045") == "one, eight hundred, four nine zero, zero zero four five"
    assert say_hotline("1-800-752-6633") == "one, eight hundred, seven five two, six six three three"


@pytest.mark.parametrize(
    "text",
    [
        # The agent asks "any gas smell right now?" and the answer is a plain no.
        "No, I don't smell gas right now.",
        "No, I don't smell any gas at the moment, it's just cold.",
        "This furnace is giving me a headache, it keeps short cycling.",
    ],
)
def test_plain_answers_and_figures_of_speech_do_not_fire(text):
    assert hazard_in(text) is None


@pytest.mark.parametrize(
    "text, hazard",
    [
        ("there's like a sewer smell coming from the furnace room", "gas"),
        ("the pilot light went out and now there's a weird smell", "gas"),
        ("my carbon monoxide detector says 'CO' and is beeping", "co"),
        ("the CO thing on the wall keeps going off", "co"),
    ],
)
def test_round_two_misses_are_caught(text, hazard):
    assert hazard_in(text) == hazard


def test_one_persons_flu_is_not_co_but_a_sick_household_still_is():
    assert hazard_in("I've had the flu, headache and dizzy all week, and now the AC died.") is None
    # CO poisoning is classically mistaken for a family-wide flu: this stays P0 on purpose.
    assert (
        hazard_in("The heat's out and the kids have a stomach bug, they've been throwing up all night.")
        == "co"
    )
