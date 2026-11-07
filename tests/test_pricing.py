import pytest


@pytest.mark.parametrize(
    "question, expected",
    [
        # Whole words only: "apartment" isn't "part", "infant" isn't "fan", "totally" isn't "total".
        ("how much is the diagnostic visit for my apartment", "$129"),
        ("how much is a service call, I have an infant at home", "$129"),
        ("is the visit totally free for members", "$129"),
        ("how much is a visit, the furnace is making a fan noise", "$129"),
        ("what's the cost for the latest appointment you have", "$129"),
        ("how much for a new furnace", "free"),
        ("how much is a tune-up", "$159"),
    ],
)
def test_price_answers(make_call, question, expected):
    assert expected in make_call(None).get_pricing(question)


@pytest.mark.parametrize(
    "question",
    ["how much to replace a capacitor", "how much is a replacement capacitor", "how much to fix my AC"],
)
def test_repairs_and_parts_get_no_figure(make_call, question):
    assert "$" not in make_call(None).get_pricing(question)


def test_a_pricing_only_call_leaves_a_summary(make_call):
    call = make_call(None)
    call.get_pricing("how much is a tune-up")
    assert "pricing" in call.technician_summary()
