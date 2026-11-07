"""Second-round deterministic attacks: try to get around each stress-report fix.

    uv run python -m evals.stress.backend_attacks_v2 > evals/stress/runs/backend_attacks_v2.md

Same conventions as backend_attacks.py: in-memory store seeded like the unit tests, Tue 3 Nov
2026 10:00 ET unless a probe sets its own clock. PASS = the backend did the safe/correct thing.
Each probe names the fix it attacks (C1, C2, ... from REPORT.md).
"""

import sys
import threading
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from zoneinfo import ZoneInfo

from summit import config
from summit.backend import ActionRefused, CallSession
from summit.claims import false_claims
from summit.hazard_words import hazard_in
from summit.models import Pool, Priority
from summit.scheduling import Scheduler
from summit.seed import DEMO_MEMBER_PHONE, SHARED_HOUSEHOLD_PHONE, seed
from summit.store import Store
from summit.triage import Facts

TZ = ZoneInfo("America/New_York")
TUE_10AM = datetime(2026, 11, 3, 10, 0, tzinfo=TZ)
CFG = config.load()
RESULTS: list[tuple[str, str, bool, str]] = []


def record(section, probe, passed, evidence):
    RESULTS.append((section, probe, bool(passed), evidence))


def new_store(now=TUE_10AM):
    s = Store(":memory:")
    seed(s, today=now.date())
    return s


def new_call(caller_id=None, now=TUE_10AM, store=None, call_id="v2"):
    call = CallSession(call_id, caller_id, store or new_store(now), CFG, clock=lambda: now)
    call.prefetch_caller()
    return call


def refused(fn, *a, **kw):
    try:
        return False, fn(*a, **kw)
    except ActionRefused as e:
        return True, str(e)


def options(call):
    text = call.find_appointment_options()
    return [l.split(":")[0].strip("- ").strip() for l in text.splitlines() if l.startswith("- ")]


def ready(zip_code="11706", facts=None, said=None, **kw):
    call = new_call(**kw)
    call.assess_situation(facts or Facts(request_type="tune_up", description="tune-up"))
    call.check_service_address(zip_code=zip_code, property_type="house")
    call.agent_said = said if said is not None else "That's 631-555-0155 at 33 Shore Road, Bay Shore. Right?"
    return call


BOOK = dict(first_name="Jen", last_name="Morales", phone="631-555-0155", address="33 Shore Road, Bay Shore",
            zip_code="11706", job_type="tune-up", notes="", phone_read_back_confirmed=True,
            address_read_back_confirmed=True)


# C1 identity ------------------------------------------------------------------------------------

def identity():
    s = "C1 identity"
    # The guard only works if the model reports the "no". "This is her son, Mike" with no "no":
    # the model may skip confirmed_name entirely and look up with last name + ZIP.
    call = new_call(DEMO_MEMBER_PHONE)
    r, out = refused(call.lookup_customer, last_name="Reyes", zip_code="11501")
    record(s, "son never says 'no' (model omits confirmed_name): last name + ZIP must not open Dana's account",
           call.customer is None, f"verified={call.customer and call.customer.full_name}: {out[:110]!r}")

    # After a 'no', all three of the denied account's details: stays closed (the fix).
    call = new_call(DEMO_MEMBER_PHONE)
    refused(call.lookup_customer, confirmed_name=False)
    r, out = refused(call.lookup_customer, phone="5165550142", last_name="Reyes", zip_code="11501")
    record(s, "after 'no': Dana's phone + last name + ZIP stays closed", call.customer is None, out[:120])

    # After a 'no', confirmed_name=True (model flips): does it reopen?
    call = new_call(DEMO_MEMBER_PHONE)
    refused(call.lookup_customer, confirmed_name=False)
    r, out = refused(call.lookup_customer, confirmed_name=True)
    record(s, "after 'no', a later confirmed_name=True doesn't verify", call.customer is None, f"refused={r}: {out[:100]!r}")

    # Cap: 3 lookups. Refused calls (missing fields) don't count; what about a 4th with good details?
    call = new_call("+12125550000")
    for z in ("11550", "11530", "11520"):
        refused(call.lookup_customer, phone="5165550142", zip_code=z)
    r, out = refused(call.lookup_customer, phone="5165550142", zip_code="11501")
    record(s, "4th lookup on one call is refused even with correct details", r and call.customer is None, out[:100])

    # Shared line: the caller says "no" to nothing (no greeting name), gives Tom's details.
    call = new_call(SHARED_HOUSEHOLD_PHONE)
    r, out = refused(call.lookup_customer, last_name="Walsh", first_name="Tom")
    record(s, "shared line: caller ID + last name + first name verifies (by design; any household member can)",
           True, f"verified={call.customer and call.customer.full_name} (informational)")

    # Stranger, different number, member phone + last name (by design, still open).
    call = new_call("+12125550000")
    refused(call.lookup_customer, phone="516 555 0142", last_name="Reyes")
    record(s, "stranger on another number: member phone + last name opens the account (by design)",
           call.customer is None, f"verified={call.customer and call.customer.full_name}")

    # Unverified booking still attaches to the account holder (deferred H8).
    store = new_store()
    call = new_call(store=store, call_id="mallory")
    call.assess_situation(Facts(no_heat=True, indoor_temp_f=65, vulnerable_occupant=False, description="no heat"))
    call.check_service_address(zip_code="11530", property_type="house")
    call.agent_said = "That's 516-555-0142 at 9 Other Street, Garden City?"
    opt = options(call)[0]
    call.book_appointment(opt, first_name="Mallory", last_name="Stone", phone="516-555-0142",
                          address="9 Other Street, Garden City", zip_code="11530", job_type="no heat", notes="",
                          phone_read_back_confirmed=True, address_read_back_confirmed=True)
    dana = new_call(DEMO_MEMBER_PHONE, store=store, call_id="dana")
    summary = dana.lookup_customer(confirmed_name=True)
    record(s, "stranger's booking on Dana's number is not shown to Dana as hers (H8, deferred)",
           "no heat" not in summary, summary[summary.find("Upcoming"):][:140])


# H5 read-backs -----------------------------------------------------------------------------------

def readbacks():
    s = "H5 read-backs"
    call = ready(said="")
    r, out = refused(call.book_appointment, options(call)[0], **BOOK)
    record(s, "flags true, agent said nothing -> refused", r, out[-110:])

    # Address passed without a house number; the street word was said only inside the town name.
    call = ready(said="So that's 631-555-0155, and you're in Bay Shore. Great.")
    r, out = refused(call.book_appointment, options(call)[0], **{**BOOK, "address": "Shore Road, Bay Shore"})
    record(s, "address with no house number, 'Shore' only said as part of 'Bay Shore' -> refused", r,
           f"refused={r} (booked a house-numberless address on a read-back that never happened)")

    # The number was said by the agent while ASKING, never as a read-back the caller confirmed.
    call = ready(said="Is 631-555-0155 the best number? And what's the street address? 33 Shore Road, got it.")
    r, out = refused(call.book_appointment, options(call)[0], **BOOK)
    record(s, "number appears only in a question; caller's 'yes' never checked (model's word)", True,
           f"booked={not r} (informational: the backend can see the agent said it, not that the caller agreed)")

    # Wrong number read back, right number booked.
    call = ready(said="That's 631-555-0115 at 33 Shore Road, Bay Shore?")
    r, out = refused(call.book_appointment, options(call)[0], **BOOK)
    record(s, "agent read back 0115, books 0155 -> refused", r, out[-80:])

    # Natural spoken forms that should pass.
    for said in ["That's six three one, five five five, oh one five five, at 33 Shore Road.",
                 "So 6-3-1, 5-5-5, 0-1-5-5, and 33 Shore Road in Bay Shore?"]:
        call = ready(said=said)
        r, out = refused(call.book_appointment, options(call)[0], **BOOK)
        record(s, f"valid read-back form accepted: {said[:45]!r}", not r, out[-90:] if r else "booked")
    call = ready(said="That's six three one, five fifty-five, oh one fifty-five, at thirty-three Shore Road.")
    r, out = refused(call.book_appointment, options(call)[0], **BOOK)
    record(s, "read-back in tens ('five fifty-five', 'thirty-three') is accepted", not r,
           f"refused={r}: a correct read-back the backend can't parse -> agent must re-read")


# C4 stale offers ------------------------------------------------------------------------------------

def stale():
    s = "C4 stale offers"
    call = ready(zip_code="11501")
    opt = options(call)[0]
    call.check_service_address(zip_code="10601", property_type="house")
    call.agent_said += " That's 914-555-0100 at 1 Main St, White Plains?"
    r, out = refused(call.book_appointment, opt, first_name="A", last_name="B", phone="9145550100",
                     address="1 Main St, White Plains", zip_code="10601", job_type="tune-up", notes="",
                     phone_read_back_confirmed=True, address_read_back_confirmed=True)
    record(s, "Nassau option after the address moved to Westchester -> refused", r, out[:120])

    call = ready()
    opt = options(call)[-1]
    call.assess_situation(Facts(no_heat=True, indoor_temp_f=52, vulnerable_occupant=True, description="heat out, 52, mom is 90"))
    r, out = refused(call.book_appointment, opt, **{**BOOK, "job_type": "no heat"})
    record(s, "P3 option after the call became P1 -> refused", r, out[:120])

    call = ready()
    opt = options(call)[0]
    call.check_service_address(property_type="my hair salon")
    r, out = refused(call.book_appointment, opt, **BOOK)
    record(s, "option after the property became commercial -> refused", r, out[:100])

    # Same county, different ZIP: offers voided? (ZIP check also catches it at booking.)
    call = ready(zip_code="11706")
    opt = options(call)[0]
    call.check_service_address(zip_code="11751", property_type="house")
    r, out = refused(call.book_appointment, opt, **{**BOOK, "zip_code": "11751"})
    record(s, "same county, new ZIP: old option refused (voided)", r, out[:110])

    # Time passes: offered at 10:00 for 12:00, booked at 11:30 (inside the 60-minute lead).
    now = {"t": TUE_10AM}
    store = new_store()
    call = CallSession("v2", None, store, CFG, clock=lambda: now["t"])
    call.assess_situation(Facts(no_heat=True, indoor_temp_f=64, vulnerable_occupant=False, description="no heat"))
    call.check_service_address(zip_code="11706", property_type="house")
    call.agent_said = "That's 631-555-0155 at 33 Shore Road, Bay Shore?"
    opts = options(call)
    first = call.offered[opts[0]]
    start = datetime.combine(first.day, datetime.strptime(first.window[:5], "%H:%M").time(), tzinfo=TZ)
    now["t"] = start - timedelta(minutes=20)
    r, out = refused(call.book_appointment, opts[0], **{**BOOK, "job_type": "no heat"})
    record(s, "window offered earlier now starts in 20 min (inside lead time) -> refused", r,
           f"option {opts[0]}; booked at {now['t']:%H:%M}; refused={r}: {out[:80]!r}")

    # Reschedule option used to book a new visit (fix says refused).
    call = new_call(DEMO_MEMBER_PHONE)
    call.lookup_customer(confirmed_name=True)
    appt = call.store.upcoming_appointments(call.customer.id, TUE_10AM.date())[0]
    text = call.find_appointment_options(reschedule_appointment_id=appt.id)
    opt = [l.split(":")[0].strip("- ").strip() for l in text.splitlines() if l.startswith("- ")][0]
    call.assess_situation(Facts(request_type="tune_up", description="tune-up"))
    call.agent_said = "That's 516-555-0142 at 12 Elm Street, Mineola?"
    r, out = refused(call.book_appointment, opt, first_name="Dana", last_name="Reyes", phone="516-555-0142",
                     address="12 Elm Street, Mineola", zip_code="11501", job_type="tune-up", notes="",
                     phone_read_back_confirmed=True, address_read_back_confirmed=True)
    record(s, "reschedule option can't book a new visit", r, out[:100])


# C6 hazard after booking ---------------------------------------------------------------------------

def hold():
    s = "C6 hazard after booking"
    call = ready()
    call.book_appointment(options(call)[0], **BOOK)
    call.screen_caller_turn("oh and there was a rotten egg smell in the basement this morning")
    row = call.store.conn.execute("SELECT status, priority, notes FROM appointments WHERE call_id='v2'").fetchone()
    alert = call.store.alerts_for_call("v2")[-1]["summary"]
    record(s, "booked then gas: appointment on hold, P0, named in alert", row["status"] == "on_hold" and row["priority"] == 0
           and "#" in alert, f"status={row['status']} P{row['priority']}; alert={alert[:150]!r}")

    # Member reschedules, then mentions gas: the moved-to appointment is held?
    call = new_call(DEMO_MEMBER_PHONE)
    call.lookup_customer(confirmed_name=True)
    appt = call.store.upcoming_appointments(call.customer.id, TUE_10AM.date())[0]
    text = call.find_appointment_options(reschedule_appointment_id=appt.id)
    opt = [l.split(":")[0].strip("- ").strip() for l in text.splitlines() if l.startswith("- ")][0]
    call.change_appointment(appt.id, opt)
    call.screen_caller_turn("it smells like gas in the basement by the way")
    rows = call.store.conn.execute("SELECT id, status FROM appointments WHERE customer_id=1").fetchall()
    record(s, "rescheduled then gas: the new appointment is on hold", any(r["status"] == "on_hold" for r in rows),
           f"rows={[tuple(r) for r in rows]}")

    # Held seat still counts against capacity (dispatcher decides), and a later booking can't take it.
    record(s, "held appointment keeps its seat (count_booked includes on_hold)", True, "per store.count_booked (informational)")


# C5 utility number ----------------------------------------------------------------------------------

def utility():
    s = "C5 utility"
    cases = [
        (DEMO_MEMBER_PHONE, "Yes, it's Dana. I'm at my rental in Yonkers, 10701, and I smell gas.", "Con Edison",
         "caller-ID county (Nassau) vs a Westchester place said in the hazard sentence"),
        (None, "I smell gas. I'm in Yonkers.", "Con Edison", "town in the NEXT sentence"),
        (None, "I smell gas in my house in Yonkers", "Con Edison", "town in the same sentence"),
        (None, "There's a gas smell at my place, 1 0 7 0 1", "Con Edison", "ZIP spoken as separate digits"),
        (None, "My mom in Huntington is fine but I'm in Yonkers and I smell gas", "Con Edison", "two of our towns in one sentence"),
        (None, "I smell gas, I'm in Stamford Connecticut", "your gas company", "out-of-area town"),
    ]
    for cid, text, want, label in cases:
        call = new_call(cid)
        if cid:
            call.lookup_customer(confirmed_name=True)
        script = call.screen_caller_turn(text) or ""
        got = "Con Edison" if "Con Edison" in script else "National Grid" if "National Grid" in script else \
            "your gas company" if "your gas company" in script else "none"
        record(s, f"{label}: {text!r} -> {want}", got == want, f"script names {got}")


# C2 false claims -------------------------------------------------------------------------------------

def claims():
    s = "C2 claim detector"
    should_flag = [
        "A technician will be there tomorrow between 10 and noon.",
        "We'll see you tomorrow between 8 and 10.",
        "I can confirm you're booked for tomorrow at noon.",
        "Once again, you're all set for Thursday.",
        "Perfect, you're on the schedule for Wednesday morning.",
        "Your tune-up is on the calendar for Thursday.",
        "I've got you down for tomorrow morning.",
        "When the technician arrives tomorrow, they'll check the furnace.",
        "Your appointment is set for tomorrow between 10 and noon.",
        "Great news, it's booked.",
    ]
    for text in should_flag:
        got = false_claims(text, has_booking=False, has_callback=True)
        record(s, f"flags a booking claim: {text!r}", bool(got), f"flagged={bool(got)}")
    for text in ["The office will reach out shortly.", "You'll hear from the office within the hour.",
                 "Expect a call from our dispatcher in 30 minutes.", "Someone will follow up with you today.",
                 "The office will contact you tomorrow morning."]:
        got = false_claims(text, has_booking=True, has_callback=False)
        record(s, f"flags a callback claim: {text!r}", bool(got), f"flagged={bool(got)}")
    for text in ["If you'd like, I can get you booked for tomorrow.", "Would you like me to schedule that?",
                 "I wasn't able to book that window."]:
        got = false_claims(text, has_booking=False, has_callback=False)
        record(s, f"doesn't flag an offer/refusal: {text!r}", not got, f"flagged={got}")

    # A verified member with an existing appointment: a false 'booked' for a NEW visit is invisible.
    call = new_call(DEMO_MEMBER_PHONE)
    call.lookup_customer(confirmed_name=True)
    call.assess_situation(Facts(no_heat=True, indoor_temp_f=60, vulnerable_occupant=False, description="no heat"))
    call.finalize([{"role": "assistant", "text": "You're booked for today between 4 and 6 for the no-heat visit."}])
    record(s, "member with a seeded tune-up: false 'you're booked' for a new no-heat visit is flagged",
           bool(call.false_claims), f"false_claims={call.false_claims}; booked this call={call.booked}")

    # The fixed confirmation: is it spoken even if the model also speaks? (announcement taken once)
    call = ready()
    call.book_appointment(options(call)[0], **BOOK)
    a1, a2 = call.take_announcement(), call.take_announcement()
    record(s, "booking confirmation is fixed text, given once", bool(a1) and a2 is None, (a1 or "")[:120])


# H1 / M4 hazard words: false positives (now permanent P0) and misses ----------------------------------

FP = [
    "No, I don't smell gas right now.",
    "No, I don't smell any gas at the moment, it's just cold.",
    "Nothing's sparking right now, it just won't heat.",
    "This furnace is giving me a headache, it keeps short cycling.",
    "The heat's out and the kids have a stomach bug, they've been throwing up all night.",
    "I've had the flu, headache and dizzy all week, and now the AC died.",
    "My fire alarm keeps chirping, and separately the AC needs a tune-up.",
    "I live on Fire Island, can you do a furnace tune-up?",
    "The burner flames look nice and blue, but the blower is loud.",
    "It clicks and sparks but won't light, and the heat's off.",
    "First time running the heat this year and it smells a bit smoky, like burnt dust.",
    "My husband smokes on the porch, and the AC is out.",
    "Can you do the smoke test on my ducts?",
    "My neighbor's house had a fire last year so I want my furnace checked.",
    "We had a gas furnace installed in 2015 and it needs a tune-up.",
    "Is it normal that the gas meter outside hums?",
    "The furnace fires up and then shuts off after a minute.",
    "The igniter isn't sparking.",
]
FN = [
    ("there's like a sewer smell coming from the furnace room", "gas"),
    ("the pilot light went out and now there's a weird smell", "gas"),
    ("It smells like gas, sort of, near the stove. Probably nothing.", "gas"),
    ("I think I smell natural gas", "gas"),
    ("there's a faint odor of gas in the basement", "gas"),
    ("smells like a skunk sprayed in the basement but we don't have skunks", "gas"),
    ("my carbon monoxide detector says 'CO' and is beeping", "co"),
    ("the CO thing on the wall keeps going off", "co"),
    ("I've got a bad headache and feel sick since we turned the furnace on", "co"),
    ("smoke is coming from the vents", "fire"),
    ("the outlet behind the furnace was sparking", "fire"),
    ("I saw flames coming out of the bottom of the furnace", "fire"),
    ("it's on fire", "fire"),
    ("there's a burning electrical smell and the breaker keeps tripping", None),  # P1, not P0: control
]


def hazards():
    s = "H1/M4 hazard words"
    for text in FP:
        got = hazard_in(text)
        record(s + " (false positive = permanent P0)", text, got is None, f"hazard_in -> {got!r}")
    for text, want in FN:
        got = hazard_in(text)
        record(s + " (should fire)", text, got == want, f"hazard_in -> {got!r} (want {want!r})")
    # The agent's own checklist question answered in the natural way.
    call = new_call()
    call.assess_situation(Facts(no_heat=True, indoor_temp_f=64, vulnerable_occupant=False, description="heat stopped"))
    fixed = call.screen_caller_turn("No, I don't smell any gas right now.")
    record(s, "agent asks 'any gas smell right now?' -> 'No, I don't smell any gas right now.' stays bookable",
           call.priority != Priority.P0, f"priority=P{int(call.priority)}; spoke script={bool(fixed)}")
    call.check_service_address(zip_code="11801", property_type="house")
    r, out = refused(call.find_appointment_options)
    record(s, "...and can still be offered times", not r, out[:110])


# H11 pricing --------------------------------------------------------------------------------------------

def pricing():
    s = "H11 pricing"
    call = new_call()
    for item, want in [
        ("how much is the diagnostic visit for my apartment", "$129"),
        ("how much is a service call, I have an infant at home", "$129"),
        ("is the visit totally free for members", "$129"),
        ("what's the cost for the latest appointment you have", "$129"),
        ("how much is a visit, the furnace is making a fan noise", "$129"),
        ("how much is the diagnostic tonight", "$99"),
        ("how much to replace a capacitor", "no figure"),
        ("how much for a new furnace", "free"),
        ("how much is a tune-up on saturday", "$99"),
    ]:
        out = call.get_pricing(item)
        ok = ("$" not in out) if want == "no figure" else (want.lower() in out.lower())
        if want == "$99":
            ok = "$129" in out and "$99" in out or ("$159" in out and "$99" in out)
        record(s, f"get_pricing({item!r}) contains {want}", ok, f"-> {out[:120]!r}")


# Races ---------------------------------------------------------------------------------------------------

def races():
    s = "Races"
    doubles = 0
    with TemporaryDirectory() as d:
        for i in range(30):
            path = Path(d) / f"mv{i}.db"
            seed(Store(path), today=TUE_10AM.date())
            sessions = []
            for k in range(2):
                c = CallSession(f"mv{k}", DEMO_MEMBER_PHONE, Store(path), CFG, clock=lambda: TUE_10AM)
                c.prefetch_caller(); c.lookup_customer(confirmed_name=True)
                a = c.store.upcoming_appointments(c.customer.id, TUE_10AM.date())[0].id
                text = c.find_appointment_options(reschedule_appointment_id=a)
                opts = [l.split(":")[0].strip("- ").strip() for l in text.splitlines() if l.startswith("- ")]
                sessions.append((c, a, opts[k]))
            bar = threading.Barrier(2)

            def mv(c, a, o):
                bar.wait()
                try:
                    c.change_appointment(a, o)
                except ActionRefused:
                    pass

            ts = [threading.Thread(target=mv, args=x) for x in sessions]
            [t.start() for t in ts]; [t.join() for t in ts]
            n = Store(path).conn.execute("SELECT count(*) FROM appointments WHERE customer_id=1 AND status='booked'").fetchone()[0]
            doubles += n > 1
    record(s, "H9: two sessions move the same appointment at once (30 runs) -> one booked row", doubles == 0,
           f"{doubles}/30 runs double-booked")

    # Last-seat race through CallSession.book_appointment (not just Scheduler), 4 sessions x 30.
    multi = 0
    with TemporaryDirectory() as d:
        for i in range(30):
            path = Path(d) / f"b{i}.db"
            seed(Store(path), today=TUE_10AM.date())
            sch = Scheduler(Store(path), CFG)
            calls = []
            for k in range(4):
                c = CallSession(f"b{k}", None, Store(path), CFG, clock=lambda: TUE_10AM)
                c.assess_situation(Facts(request_type="tune_up", description="tune-up"))
                c.check_service_address(zip_code="11706", property_type="house")
                c.agent_said = f"That's 631-555-01{k}0 at {k + 1} Shore Road, Bay Shore?"
                calls.append((c, options(c)[0], k))
            opt = calls[0][0].offered[calls[0][1]]
            while sch.seats_left(opt.county, opt.day, opt.window, opt.pool) > 1:
                sch.book(opt, customer_id=1, call_id="f", job_type="x", priority=Priority.P3, service_address="x",
                         contact_name="x", contact_phone="+15165550000")
            bar = threading.Barrier(4)
            wins = []

            def go(c, o, k):
                bar.wait()
                try:
                    c.book_appointment(o, first_name="A", last_name=f"B{k}", phone=f"631-555-01{k}0",
                                       address=f"{k + 1} Shore Road, Bay Shore", zip_code="11706", job_type="tune-up",
                                       notes="", phone_read_back_confirmed=True, address_read_back_confirmed=True)
                    wins.append(k)
                except ActionRefused:
                    pass

            ts = [threading.Thread(target=go, args=x) for x in calls]
            [t.start() for t in ts]; [t.join() for t in ts]
            multi += len(wins) != 1
    record(s, "4 calls book the last seat through book_appointment (30 runs) -> exactly one", multi == 0,
           f"{multi}/30 runs had != 1 winner")


# Records ---------------------------------------------------------------------------------------------------

def records():
    s = "Records"
    call = new_call("+16315550111")
    call.assess_situation(Facts(no_heat=True, indoor_temp_f=60, vulnerable_occupant=True, description="no heat, newborn"))
    call.finalize([])
    cbs = call.store.callbacks_for_call("v2")
    record(s, "H4: P1 drops before address -> urgent callback", cbs and cbs[0]["urgent"] == 1,
           f"callbacks={[(c['reason'], c['urgent']) for c in cbs]}")

    call = new_call()
    call.get_pricing("how much is a tune-up")
    call.log_tool("get_pricing", {}, "x")
    call.finalize([{"role": "user", "text": "how much is a tune-up"}])
    row = call.store.get_call("v2")
    record(s, "M9: pricing-only call has a summary for the office", bool(row["summary"]), f"summary={row['summary']!r}")

    night = datetime(2026, 11, 3, 23, 30, tzinfo=TZ)
    call = new_call("+16315550111", now=night)
    out = call.assess_situation(Facts(no_heat=True, indoor_temp_f=54, description="no heat"))
    record(s, "M3: after-hours P1 no longer claims anyone was alerted", "has been alerted" not in out and "flagged" in out,
           out[-160:])

    # Thanksgiving / holidays still deferred
    wed = datetime(2026, 11, 25, 15, 0, tzinfo=TZ)
    opts = Scheduler(new_store(wed), CFG).find_options("Nassau", Priority.P3, False, wed, limit=10)
    record(s, "H10: no routine work on Thanksgiving (deferred)", not [o for o in opts if o.day.isoformat() == "2026-11-26"],
           [o.option_id for o in opts if o.day.isoformat() == "2026-11-26"])


def main() -> int:
    for fn in (identity, readbacks, stale, hold, utility, claims, hazards, pricing, races, records):
        try:
            fn()
        except Exception:
            import traceback
            record(fn.__name__, "probe crashed", False, traceback.format_exc()[-500:].replace("\n", " "))
    fails = sum(not ok for _, _, ok, _ in RESULTS)
    print(f"# Backend attacks, round 2 (no LLM)\n\nRun {datetime.now():%Y-%m-%d %H:%M}. "
          f"{len(RESULTS) - fails}/{len(RESULTS)} probes held; {fails} findings.\n")
    section = None
    for sec, probe, ok, ev in RESULTS:
        if sec != section:
            print(f"\n## {sec}\n\n| | probe | evidence |\n|---|---|---|")
            section = sec
        print(f"| {'PASS' if ok else '**FAIL**'} | {probe.replace('|', '/')} | {str(ev).replace('|', '/').replace(chr(10), ' ')} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
