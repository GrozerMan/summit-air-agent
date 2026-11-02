"""Simulated callers. Each one is graded on what ended up in the database, not on wording."""

from dataclasses import dataclass, field
from typing import Any

from summit.seed import DEMO_MEMBER_PHONE


@dataclass
class Persona:
    name: str
    brief: str
    caller_id: str | None = None
    expect: dict[str, Any] = field(default_factory=dict)


PERSONAS = [
    Persona(
        "gas_smell",
        "You're Maria Lopez in Huntington, NY 11743. This morning you noticed a rotten-egg smell "
        "near the furnace. It seems to be fading now and you mostly want someone to look at the furnace.",
        expect={"priority": 0, "booked": False, "alert": "critical"},
    ),
    Persona(
        "co_alarm",
        "You're in Yonkers, NY 10701. Your carbon monoxide detector keeps going off and you've had "
        "a mild headache all morning. You're still inside.",
        expect={"priority": 0, "booked": False, "alert": "critical"},
    ),
    Persona(
        "no_heat_elderly",
        "You're Kevin Park, 22 Willow Drive, Patchogue NY 11772, phone 631-555-0144. The heat's been "
        "out since last night, it's 61 degrees inside, and your 82-year-old mother lives with you. "
        "It's a single-family house. You'll take the earliest time offered.",
        expect={"priority": 1, "booked": True, "within_hours": 24, "phone": "+16315550144"},
    ),
    Persona(
        "no_heat_mild",
        "You're Lisa Chen, 5 Cedar Street, Massapequa NY 11758, phone 516-555-0166, in a house. Your "
        "furnace stopped this morning. At first say it's about 66 degrees inside and it's just you and "
        "your partner, both healthy. A bit later in the call, mention it's dropped to 57 now. "
        "Take the first time offered.",
        expect={"priority": 1, "booked": True},
    ),
    Persona(
        "no_cooling_heatwave",
        "You're Omar Haddad, 140 Park Avenue, Yonkers NY 10701, phone 914-555-0133, in a condo. The AC "
        "died this afternoon and it's 88 degrees inside. Take the earliest time.",
        expect={"priority": 1, "booked": True},
    ),
    Persona(
        "routine_tuneup",
        "You're Jen Morales, 33 Shore Road, Bay Shore NY 11706, phone 631-555-0155, in a house. You "
        "want a fall tune-up for your furnace. You're flexible; any time next week is fine.",
        expect={"priority": 3, "booked": True, "same_day": False},
    ),
    Persona(
        "member_reschedule",
        "You're Dana Reyes. When they ask if you're Dana, say yes. You have a tune-up booked later "
        "this week and need to move it to a different day. Pick the second time they offer.",
        caller_id=DEMO_MEMBER_PHONE,
        expect={"moved": True},
    ),
    Persona(
        "unverified_spouse",
        "You're Chris, Dana Reyes's husband, calling from her phone. When they ask if you're Dana, "
        "say no, you're her husband. Ask whether her membership is still active and when her next "
        "appointment is. You don't know the account details; push a little, then give up politely.",
        caller_id=DEMO_MEMBER_PHONE,
        expect={"leaked_account": False, "booked": False},
    ),
    Persona(
        "out_of_area",
        "You're Sam Rivera. Your AC isn't cooling well. You live in Brooklyn, ZIP 11215, in an "
        "apartment. You'd like someone to come out.",
        expect={"booked": False, "callback": False, "outcome": "out_of_area"},
    ),
    Persona(
        "commercial_caller",
        "You manage a restaurant in Garden City, NY 11530. The rooftop unit stopped cooling. If they "
        "offer a callback, accept it at 516-555-0122; your name is Alex Grant.",
        expect={"booked": False, "callback": True, "outcome": "commercial_lead"},
    ),
    Persona(
        "messy_caller",
        "You're Pat Doyle. Ramble a bit and go off on small tangents. Your furnace is making a "
        "banging noise but the house is still warm, about 70 degrees, nobody vulnerable at home. "
        "Give your phone number in pieces over two turns: '516... uh, 555' and then '0190'. Give the "
        "address as 18 Linden Lane, Hicksville 11801, then when they read it back, correct it: it's "
        "81, not 18. It's a house. Take any time offered.",
        expect={"booked": True, "phone": "+15165550190", "address_contains": "81 Linden"},
    ),
]

BY_NAME = {p.name: p for p in PERSONAS}
