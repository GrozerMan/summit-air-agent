import pytest

from summit.claims import false_claims


@pytest.mark.parametrize(
    "text",
    [
        "You're booked for tomorrow between 8 and 10.",
        "Your appointment is set for tomorrow between 10 and noon.",
        "Great news, it's booked.",
        # Round-2 stress probes: phrasings the first detector missed.
        "A technician will be there tomorrow between 10 and noon.",
        "We'll see you tomorrow between 8 and 10.",
        "I can confirm you're booked for tomorrow at noon.",
        "Once again, you're all set for Thursday.",
        "Perfect, you're on the schedule for Wednesday morning.",
        "Your tune-up is on the calendar for Thursday.",
        "I've got you down for tomorrow morning.",
        "When the technician arrives tomorrow, they'll check the furnace.",
    ],
)
def test_booking_claims_without_a_booking_are_flagged(text):
    assert false_claims(text, has_booking=False, has_callback=True)


@pytest.mark.parametrize(
    "text",
    [
        "The office will call you back within the hour.",
        "The office will reach out shortly.",
        "You'll hear from the office within the hour.",
        "Expect a call from our dispatcher in 30 minutes.",
        "Someone will follow up with you today.",
        "The office will contact you tomorrow morning.",
    ],
)
def test_callback_claims_without_a_callback_are_flagged(text):
    assert false_claims(text, has_booking=True, has_callback=False)


@pytest.mark.parametrize(
    "text",
    [
        "If you'd like, I can get you booked for tomorrow.",
        "Would you like me to schedule that?",
        "I wasn't able to book that window.",
        "If you want, the office can call you back.",
        "Please call nine-one-one once you're outside.",
    ],
)
def test_offers_and_refusals_are_not_claims(text):
    assert not false_claims(text, has_booking=False, has_callback=False)
