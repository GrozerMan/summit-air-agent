"""Deterministic attacks on summit/ with no LLM in the loop.

    uv run python -m evals.stress.backend_attacks            # all probes, markdown to stdout
    uv run python -m evals.stress.backend_attacks > evals/stress/runs/backend_attacks.md

Each probe builds a fresh in-memory store seeded exactly like the unit tests
(Tuesday 3 Nov 2026, 10:00 ET unless the probe sets its own clock), calls the
backend the way a misbehaving model could, and records what the backend did.
"PASS" means the backend did the safe/correct thing; "FAIL" is a finding.

Nothing here modifies summit/, config/, prompts/ or agent.py.
"""

import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from zoneinfo import ZoneInfo

from summit import config
from summit.backend import ActionRefused, CallSession
from summit.hazard_words import hazard_in
from summit.models import Pool, Priority
from summit.notify import Notifier
from summit.scheduling import Scheduler
from summit.seed import DEMO_MEMBER_PHONE, SHARED_HOUSEHOLD_PHONE, seed
from summit.service_area import check_town, check_zip, property_kind
from summit.speech import normalize_phone
from summit.store import Store
from summit.triage import Facts, assess

TZ = ZoneInfo("America/New_York")
TUE_10AM = datetime(2026, 11, 3, 10, 0, tzinfo=TZ)
CFG = config.load()

RESULTS: list[tuple[str, str, bool, str]] = []  # (section, probe, passed, evidence)


def record(section: str, probe: str, passed: bool, evidence: str) -> None:
    RESULTS.append((section, probe, passed, evidence))


def new_store(today=TUE_10AM) -> Store:
    s = Store(":memory:")
    seed(s, today=today.date())
    return s


def new_call(caller_id=None, now=TUE_10AM, store=None, call_id="stress", notifier=None) -> CallSession:
    store = store or new_store(now)
    call = CallSession(call_id, caller_id, store, CFG, notifier=notifier, clock=lambda: now)
    call.prefetch_caller()
    return call


def refused(fn, *a, **kw) -> tuple[bool, str]:
    try:
        return False, fn(*a, **kw)
    except ActionRefused as e:
        return True, str(e)


def first_option(call: CallSession) -> str:
    text = call.find_appointment_options()
    # The read-back the agent would say before booking; the backend now checks it was said (H5).
    # Probes that test a missing read-back clear this afterwards.
    call.agent_said += (
        " That's 631-555-0155 at 33 Shore Road, Bay Shore. And 516-555-0142 at 9 Other Street, Garden City."
        " And 516-555-0199 at 301 Maple Ave, Garden City. Is that right?"
    )
    return next(line.split(":")[0].strip("- ").strip() for line in text.splitlines() if line.startswith("- "))


BOOK = dict(
    first_name="Jen", last_name="Morales", phone="631-555-0155", address="33 Shore Road, Bay Shore",
    zip_code="11706", job_type="tune-up", notes="",
)


def ready_call(zip_code="11706", facts=None, **kw) -> CallSession:
    call = new_call(**kw)
    call.assess_situation(facts or Facts(request_type="tune_up", description="fall tune-up"))
    call.check_service_address(zip_code=zip_code, property_type="house")
    return call


# 1. Safety: hazard lexicon sweep -------------------------------------------------------------

GAS_SHOULD_FIRE = [
    "something smells like a skunk near the furnace",
    "I smelled gas earlier but it's gone now",
    "it smells kind of like natural gas in the basement",
    "there's a gas odor by the boiler",
    "the whole basement reeks of gas",
    "it smells like rotten eggs",
    "smells sulfury",
    # negation words that are not denials of the smell
    "It won't stop smelling like gas",
    "I can't stand the rotten egg smell in the basement",
    "I can't get rid of this gas smell",
    "We can't figure out where the gas smell is coming from",
    "The heat won't come on without a weird gas smell",
    # "gone now" said as a negation of the present plus an affirmation of the past
    "It doesn't smell like gas now, but it did this morning",
    "I don't smell gas anymore. I did earlier though",
    "There's no gas smell now but there was one an hour ago",
    # other natural phrasings
    "smells eggy down by the furnace",
    "there's like a sewer smell coming from the furnace room",
    "the pilot light went out and now there's a weird smell",
    "I think the gas is leaking",
    "I hear hissing from the gas pipe and it smells funny",
]
CO_SHOULD_FIRE = [
    "my CO alarm is beeping",
    "the carbon monoxide alarm went off last night",
    "my CO detector is going crazy",
    "the detector for carbon monoxide keeps beeping",
    "the alarm that says CO on it is going off",
    "carbon monoxide alarm",
    "we all have headaches and the kids are dizzy",
    "the whole family's been really sleepy and nauseous since the heat came on",
]
SHOULD_NOT_FIRE = [
    "my gas bill is high",
    "I need a gas furnace tune-up",
    "the new filter smells dusty",
    "no, I don't smell gas, it's dusty",
    "there's a skunk living under my porch and my AC is broken",  # documented false positive
    "my car's gas mileage is bad lately, anyway my AC is out",
]


def lexicon_sweep() -> None:
    for text in GAS_SHOULD_FIRE:
        got = hazard_in(text)
        record("1 safety lexicon (gas)", text, got == "gas", f"hazard_in -> {got!r}")
    for text in CO_SHOULD_FIRE:
        got = hazard_in(text)
        record("1 safety lexicon (CO)", text, got == "co", f"hazard_in -> {got!r}")
    for text in SHOULD_NOT_FIRE:
        got = hazard_in(text)
        record("1 safety lexicon (false positive)", text, got is None, f"hazard_in -> {got!r}")


def safety_backend() -> None:
    # Gas then calm description: must stay P0.
    call = new_call()
    call.assess_situation(Facts(gas_smell=True, description="smelled gas"))
    call.assess_situation(Facts(gas_smell=False, no_heat=True, indoor_temp_f=68, description="actually just a noisy furnace"))
    record("1 safety backend", "gas then 'it's nothing, just noisy' stays P0",
           call.priority == Priority.P0, f"priority={call.priority!r}")

    # The model's own description words can force P0 (false positive that blocks booking for the call).
    call = new_call()
    call.assess_situation(Facts(no_heat=True, indoor_temp_f=64,
                                description="Asked if it smells like gas or rotten eggs; caller said it's just dusty"))
    record("1 safety backend", "model paraphrase 'asked if it smells like gas ... said dusty' does NOT go P0",
           call.priority != Priority.P0, f"priority={call.priority!r}, reasons={call.assessment.reasons}")

    # Gas after booking: is the existing appointment touched?
    call = ready_call()
    opt = first_option(call)
    call.book_appointment(opt, **BOOK, phone_read_back_confirmed=True, address_read_back_confirmed=True)
    call.screen_caller_turn("oh and by the way there was a rotten egg smell in the basement this morning")
    appt = call.store.conn.execute("SELECT id, status, priority, notes FROM appointments WHERE call_id='stress'").fetchone()
    alerts = call.store.alerts_for_call("stress")
    record("1 safety backend", "gas reported AFTER booking: booking flagged/cancelled, appointment shows P0",
           appt["status"] != "booked" or appt["priority"] == 0,
           f"appointment row: id={appt['id']} status={appt['status']} priority=P{appt['priority']}; "
           f"alerts={[a['severity'] for a in alerts]}; outcome={call.outcome}")

    # Script for an unknown caller before the address is known: no utility number.
    call = new_call()
    script = call.screen_caller_turn("it smells like gas in here")
    # Decided (C5): no question during an evacuation; with no location the script says "your gas company".
    record("1 safety backend", "unknown caller, gas before address: script gives a second number alongside 911",
           any(w in (script or "") for w in ("National Grid", "Con Edison", "your gas company")), f"script={script!r}")
    call = new_call()
    script = call.screen_caller_turn("I'm in Yonkers, 10701, and I smell gas by the boiler.")
    record("1 safety backend", "town + ZIP in the same sentence as the gas: script names Con Edison",
           "Con Edison" in (script or ""), f"script={script!r}")

    # CO symptoms only reach P0 if the model sets the flag; the lexicon doesn't see them.
    call = new_call()
    call.screen_caller_turn("we've all got headaches and feel dizzy since the furnace came on")
    record("1 safety backend", "CO symptoms without the word 'alarm' reach P0 without the model",
           call.priority == Priority.P0, f"priority after screen={call.priority!r}")


# 2. Triage boundaries ---------------------------------------------------------------------------

def triage_boundaries() -> None:
    for temp, want in [(57, 1), (58, 1), (59, 2)]:
        got = assess(Facts(no_heat=True, indoor_temp_f=temp), CFG).priority
        record("2 triage", f"no heat at {temp}°F -> P{want}", got == want, f"P{int(got)}")
    for temp, want in [(84, 2), (85, 1), (86, 1)]:
        got = assess(Facts(no_cooling=True, indoor_temp_f=temp), CFG).priority
        record("2 triage", f"no cooling at {temp}°F -> P{want}", got == want, f"P{int(got)}")
    got = assess(Facts(no_heat=True, indoor_temp_f=64, vulnerable_occupant=True), CFG).priority
    record("2 triage", "no heat 64°F + vulnerable -> P1", got == 1, f"P{int(got)}")
    got = assess(Facts(burning_smell_persistent=True, dusty_smell_first_use=True), CFG).priority
    record("2 triage", "persistent burning beats first-use dusty", got == 1, f"P{int(got)}")
    # Determinism: identical facts, 1000 runs.
    outs = {assess(Facts(no_heat=True, indoor_temp_f=58), CFG).priority for _ in range(1000)}
    record("2 triage", "same facts -> same priority (1000 runs)", len(outs) == 1, f"{outs}")
    # Exaggeration: tune-up + 'emergency' carries no fact that triage sees.
    got = assess(Facts(request_type="tune_up", description="it's an emergency, I need a tune-up today"), CFG)
    record("2 triage", "'it's an emergency' tune-up stays P3", got.priority == 3, f"P{int(got.priority)}")
    # Exaggeration that works: vulnerable_occupant is the model's call.
    got = assess(Facts(request_type="tune_up", vulnerable_occupant=True), CFG)
    record("2 triage", "tune-up + vulnerable occupant stays P3 (vulnerable only matters with no heat/cool)",
           got.priority == 3, f"P{int(got.priority)}")


# 3. Identity and privacy ----------------------------------------------------------------------

def identity() -> None:
    # Says "no, I'm her husband", then gives her last name: verified as Dana.
    call = new_call(DEMO_MEMBER_PHONE)
    refused(call.lookup_customer, confirmed_name=False)  # model reports the "no"; tool asks for more
    was_refused, out = refused(call.lookup_customer, last_name="Reyes")
    record("3 identity", "caller says he is NOT Dana, then gives last name 'Reyes' -> must not verify as Dana",
           call.customer is None, f"verified={call.customer and call.customer.full_name}; result={out[:160]!r}")

    # Stranger on any phone with a member's number + last name (both semi-public).
    call = new_call("+12125550000")
    was_refused, out = refused(call.lookup_customer, phone="516 555 0142", last_name="Reyes")
    record("3 identity", "stranger from another number: member phone + last name -> full account",
           call.customer is None, f"verified={call.customer and call.customer.full_name}; result={out[:200]!r}")

    # Unlimited ZIP guessing.
    call = new_call("+12125550000")
    attempts = 0
    for z in CFG["service_area"]["zips"]["Nassau"]:
        attempts += 1
        refused(call.lookup_customer, phone="5165550142", zip_code=z)
        if call.customer:
            break
    record("3 identity", "repeated ZIP guesses are cut off", call.customer is None,
           f"verified after {attempts} lookup_customer attempts (no attempt limit)")

    # Right ZIP, wrong last name -> OR check.
    call = new_call("+12125550000")
    refused(call.lookup_customer, phone="5165550142", last_name="Smith", zip_code="11501")
    record("3 identity", "wrong last name + right ZIP is refused", call.customer is None,
           f"verified={call.customer and call.customer.full_name}")

    # Unverified member claim -> non-member price (code).
    call = new_call()
    price = call.get_pricing("diagnostic visit, I'm a member")
    record("3 identity", "unverified 'I'm a member' gets no $0 diagnostic", "$0" not in price and "free for members" not in price.split(";")[0],
           f"get_pricing -> {price!r}")

    # Unverified booking on a member's number attaches to her record and shows up in her account.
    store = new_store()
    call = new_call(store=store, call_id="mallory")
    call.assess_situation(Facts(no_heat=True, indoor_temp_f=65, vulnerable_occupant=False, description="no heat"))
    call.check_service_address(zip_code="11530", property_type="house")
    opt = first_option(call)
    call.book_appointment(opt, first_name="Mallory", last_name="Stone", phone="516-555-0142",
                          address="9 Other Street, Garden City", zip_code="11530", job_type="no heat", notes="",
                          phone_read_back_confirmed=True, address_read_back_confirmed=True)
    dana = store.customers_by_phone(DEMO_MEMBER_PHONE)[0]
    row = store.conn.execute("SELECT customer_id, contact_name, service_address FROM appointments WHERE call_id='mallory'").fetchone()
    dana_call = new_call(DEMO_MEMBER_PHONE, store=store, call_id="dana")
    summary = dana_call.lookup_customer(confirmed_name=True)
    record("3 identity", "unverified booking leaves Dana's customer row untouched",
           dana.address == "12 Elm Street, Mineola", f"customers row: {dana.address}")
    record("3 identity", "a stranger's booking on Dana's number does not appear as Dana's appointment",
           f"#{row and store.conn.execute('SELECT id FROM appointments WHERE call_id=?', ('mallory',)).fetchone()[0]}" not in summary,
           f"appointment customer_id={row['customer_id']} (Dana is {dana.id}), contact={row['contact_name']}, "
           f"address={row['service_address']}; Dana's verified summary: {summary!r}")
    # ...and Dana (or anyone verifying as Dana) can now move the stranger's appointment.
    appt_id = store.conn.execute("SELECT id FROM appointments WHERE call_id='mallory'").fetchone()[0]
    was_refused, out = refused(dana_call.find_appointment_options, reschedule_appointment_id=appt_id)
    record("3 identity", "Dana cannot reschedule Mallory's booking", was_refused, f"refused={was_refused}: {out[:120]!r}")

    # Shared household line, unverified booking -> attached to Tom (first row), not Ann.
    store = new_store()
    call = new_call(SHARED_HOUSEHOLD_PHONE, store=store, call_id="ann")
    call.assess_situation(Facts(request_type="tune_up", description="tune-up"))
    call.check_service_address(zip_code="11530", property_type="house")
    opt = first_option(call)
    call.book_appointment(opt, first_name="Ann", last_name="Walsh", phone="516-555-0199",
                          address="301 Maple Ave, Garden City", zip_code="11530", job_type="tune-up", notes="",
                          phone_read_back_confirmed=True, address_read_back_confirmed=True)
    cid = store.conn.execute("SELECT customer_id FROM appointments WHERE call_id='ann'").fetchone()[0]
    who = store.get_customer(cid)
    record("3 identity", "Ann's unverified booking on the shared line attaches to Ann",
           who.first_name == "Ann", f"attached to customer #{cid} {who.full_name}")


# 4. Service area and eligibility --------------------------------------------------------------

REAL_NASSAU_ZIPS = {
    "11003": "Elmont", "11096": "Inwood", "11709": "Bayville", "11507": "Albertson",
    "11514": "Carle Place", "11509": "Atlantic Beach", "11042": "New Hyde Park",
}
TOWNS_ONLY = ["East Meadow", "Merrick", "Bellmore", "Syosset", "Port Washington", "Massapequa Park",
              "Rockville Center", "Mt. Vernon", "Port Chester", "Hastings-on-Hudson", "Long Beach"]


def service_area() -> None:
    for z, town in REAL_NASSAU_ZIPS.items():
        first = check_zip(z, CFG)
        second = check_town(town, CFG, zip_code=z) if first.ask_town else first
        record("4 area", f"{town} ({z}, Nassau) is accepted", second.in_area,
               f"check_zip: ask_town={first.ask_town}; then check_town('{town}') -> in_area={second.in_area}, "
               f"outside={second.outside}: {second.message[:90]!r}")
    for town in TOWNS_ONLY:
        c = check_town(town, CFG)
        expect = town not in ("Port Chester", "Hastings-on-Hudson") or True
        record("4 area", f"town only: '{town}'", c.in_area, f"in_area={c.in_area} outside={c.outside} county={c.county}")
    for z, label in [("11001", "Floral Park (spans Queens/Nassau)"), ("10467", "Bronx"), ("11215", "Brooklyn")]:
        c = check_zip(z, CFG)
        record("4 area", f"{label} {z}", (z == "11001" and c.in_area) or (z != "11001" and c.outside),
               f"in_area={c.in_area} ask_town={c.ask_town} outside={c.outside} county={c.county}")
    for desc, want in [
        ("12-unit apartment building I own", "commercial"),
        ("the boiler for the whole apartment building", "commercial"),
        ("restaurant", "commercial"),
        ("my dental office", "not residential"),
        ("two-family house", "residential"),
        ("condo unit", "residential"),
        ("4 family home", "residential"),
        ("apartment above a store", "residential"),
    ]:
        got = property_kind(desc)
        ok = got != "residential" if want == "not residential" else got == want
        record("4 area", f"property_kind({desc!r}) -> {want}", ok, f"got {got!r}")
    record("4 area", "home business: 'I run a daycare out of my house' (policy call, not graded)", True,
           f"property_kind -> {property_kind('I run a daycare out of my house')!r}; "
           f"'my home business office' -> {property_kind('my home business office')!r}")

    # Commercial after options were offered: does book_appointment re-check?
    call = ready_call()
    opt = first_option(call)
    call.check_service_address(property_type="it's actually my restaurant")
    was_refused, out = refused(call.book_appointment, opt, **BOOK, phone_read_back_confirmed=True,
                               address_read_back_confirmed=True)
    record("4 area", "booking refused after property turns out commercial", was_refused,
           f"property={call.property}; book_appointment refused={was_refused}: {out[:120]!r}")

    # Verified member asking about a different (commercial) property: area/property pre-filled residential.
    call = new_call(DEMO_MEMBER_PHONE)
    call.lookup_customer(confirmed_name=True)
    call.assess_situation(Facts(no_cooling=True, indoor_temp_f=80, vulnerable_occupant=False,
                                description="the AC at my restaurant stopped"))
    was_refused, out = refused(call.find_appointment_options)
    record("4 area", "verified member: 'AC at my restaurant' -> options refused until address checked",
           was_refused, f"property={call.property} area={call.area and call.area.zip}; refused={was_refused}")

    # Address changes county after options are offered.
    call = ready_call(zip_code="11501")  # Nassau
    opt = first_option(call)
    call.check_service_address(zip_code="10601", property_type="house")  # Westchester
    was_refused, out = refused(call.book_appointment, opt, first_name="A", last_name="B", phone="9145550100",
                               address="1 Main St, White Plains", zip_code="10601", job_type="tune-up", notes="",
                               phone_read_back_confirmed=True, address_read_back_confirmed=True)
    row = call.store.conn.execute("SELECT county, service_address FROM appointments WHERE call_id='stress'").fetchone()
    record("4 area", "Nassau option can't be booked for a Westchester address", was_refused,
           f"option {opt}; refused={was_refused}; row={dict(row) if row else None}")


# 5. Scheduling and capacity -------------------------------------------------------------------

def _filler(scheduler, option, n="filler"):
    return scheduler.book(option, customer_id=1, call_id=n, job_type="x", priority=Priority.P3,
                          service_address="x", contact_name="x", contact_phone="+15165550000")


def scheduling() -> None:
    # Race the last seat 50 times on a file DB with separate connections.
    wins = []
    with TemporaryDirectory() as d:
        for i in range(50):
            path = Path(d) / f"race{i}.db"
            seed(Store(path), today=TUE_10AM.date())
            sch = Scheduler(Store(path), CFG)
            opt = next(o for o in sch.find_options("Suffolk", Priority.P3, False, TUE_10AM, limit=20) if o.pool == Pool.REGULAR)
            while sch.seats_left(opt.county, opt.day, opt.window, opt.pool) > 1:
                _filler(sch, opt)
            res, bar = [], threading.Barrier(4)

            def go(k):
                own = Scheduler(Store(path), CFG)
                bar.wait()
                try:
                    res.append(_filler(own, opt, f"r{k}"))
                except Exception as e:  # database is locked etc.
                    res.append(f"error {type(e).__name__}: {e}")

            ts = [threading.Thread(target=go, args=(k,)) for k in range(4)]
            [t.start() for t in ts]
            [t.join() for t in ts]
            wins.append(sum(isinstance(r, int) for r in res))
            errs = [r for r in res if isinstance(r, str)]
            if errs:
                record("5 scheduling", f"race run {i}: errors", False, str(errs))
    record("5 scheduling", "4 sessions race for the last seat, 50 runs -> exactly one winner each time",
           all(w == 1 for w in wins), f"winners per run: {sorted(set(wins))}")

    # Two sessions move the same appointment concurrently.
    doubles = 0
    with TemporaryDirectory() as d:
        for i in range(30):
            path = Path(d) / f"mv{i}.db"
            seed(Store(path), today=TUE_10AM.date())
            sessions = []
            for k in range(2):
                c = CallSession(f"mv{k}", DEMO_MEMBER_PHONE, Store(path), CFG, clock=lambda: TUE_10AM)
                c.prefetch_caller()
                c.lookup_customer(confirmed_name=True)
                appt_id = c.store.upcoming_appointments(c.customer.id, TUE_10AM.date())[0].id
                text = c.find_appointment_options(reschedule_appointment_id=appt_id)
                opts = [l.split(":")[0].strip("- ").strip() for l in text.splitlines() if l.startswith("- ")]
                sessions.append((c, appt_id, opts[k]))
            bar = threading.Barrier(2)

            def mv(c, a, o):
                bar.wait()
                try:
                    c.change_appointment(a, o)
                except ActionRefused:
                    pass

            ts = [threading.Thread(target=mv, args=s) for s in sessions]
            [t.start() for t in ts]
            [t.join() for t in ts]
            n = Store(path).conn.execute(
                "SELECT count(*) FROM appointments WHERE customer_id=1 AND status='booked'").fetchone()[0]
            doubles += n > 1
    record("5 scheduling", "two sessions move the same appointment at once -> one booked row (30 runs)",
           doubles == 0, f"{doubles}/30 runs left TWO booked appointments for one original")

    # Stale option after priority goes up: options offered while P3, then the call becomes P1.
    call = new_call()
    call.assess_situation(Facts(request_type="tune_up", description="tune-up"))
    call.check_service_address(zip_code="11706", property_type="house")
    call.find_appointment_options()
    late = max(call.offered.values(), key=lambda o: (o.day, o.window))
    call.assess_situation(Facts(no_heat=True, indoor_temp_f=52, vulnerable_occupant=True,
                                description="actually the heat is out now, 52 inside, my mom is 90"))
    start = datetime.combine(late.day, datetime.strptime(late.window[:5], "%H:%M").time(), tzinfo=TZ)
    was_refused, out = refused(call.book_appointment, late.option_id, **{**BOOK, "job_type": "no heat"},
                               phone_read_back_confirmed=True, address_read_back_confirmed=True)
    record("5 scheduling", "P1 call can't be booked into a window offered while it was P3 (>24h out)",
           was_refused or (start - TUE_10AM) <= timedelta(hours=24),
           f"offered while P3: {sorted(call.offered)}; booked {late.option_id} = {(start - TUE_10AM).total_seconds()/3600:.0f}h out "
           f"as priority P{int(call.priority)}; refused={was_refused}: {out[:80]!r}")

    # P2 must be within 72h (config p2_within_hours=72): fill the next 3 days and look.
    store = new_store()
    sch = Scheduler(store, CFG)
    for _ in range(200):
        opts = [o for o in sch.find_options("Nassau", Priority.P2, False, TUE_10AM, limit=50)
                if datetime.combine(o.day, datetime.min.time(), tzinfo=TZ) < TUE_10AM + timedelta(hours=96)]
        if not opts:
            break
        _filler(sch, opts[0])
    found = sch.find_options("Nassau", Priority.P2, False, TUE_10AM)
    if found:
        start = datetime.combine(found[0].day, datetime.strptime(found[0].window[:5], "%H:%M").time(), tzinfo=TZ)
        hours = (start - TUE_10AM).total_seconds() / 3600
        record("5 scheduling", "P2 with no capacity in 72h -> refused/escalated, not offered day 5+",
               hours <= 72, f"first P2 option {found[0].option_id} starts {hours:.0f}h out")
    else:
        call = new_call(store=store, call_id="p2full")
        call.assess_situation(Facts(no_heat=True, indoor_temp_f=64, vulnerable_occupant=False, description="no heat"))
        call.check_service_address(zip_code="11501", property_type="house")
        out = call.find_appointment_options()
        record("5 scheduling", "P2 with no capacity in 72h -> refused/escalated, not offered day 5+",
               "dispatcher has been alerted" in out, f"no P2 option within 72h; find_appointment_options -> {out[:120]!r}")

    # Thanksgiving.
    wed = datetime(2026, 11, 25, 15, 0, tzinfo=TZ)
    opts = Scheduler(new_store(wed), CFG).find_options("Nassau", Priority.P3, False, wed, limit=10)
    thanks = [o for o in opts if o.day.isoformat() == "2026-11-26"]
    record("5 scheduling", "routine work is not offered on Thanksgiving (Thu Nov 26)", not thanks,
           f"{len(thanks)} Thanksgiving windows offered to a P3 caller: {[o.option_id for o in thanks]} after_hours={[o.after_hours for o in thanks]}")

    # Saturday after close, Sunday, near midnight.
    for label, now, prio in [
        ("Sat 1:30pm P3", datetime(2026, 11, 7, 13, 30, tzinfo=TZ), Priority.P3),
        ("Sat 3pm P2", datetime(2026, 11, 7, 15, 0, tzinfo=TZ), Priority.P2),
        ("Sun 11am P3", datetime(2026, 11, 8, 11, 0, tzinfo=TZ), Priority.P3),
        ("Sun 11am P1", datetime(2026, 11, 8, 11, 0, tzinfo=TZ), Priority.P1),
        ("Mon 11:55pm P3", datetime(2026, 11, 2, 23, 55, tzinfo=TZ), Priority.P3),
        ("Tue 12:05am P3", datetime(2026, 11, 3, 0, 5, tzinfo=TZ), Priority.P3),
        ("Fri 6pm P3", datetime(2026, 11, 6, 18, 0, tzinfo=TZ), Priority.P3),
    ]:
        opts = Scheduler(new_store(now), CFG).find_options("Nassau", prio, False, now)
        from summit.scheduling import say_day
        desc = [f"{say_day(o.day, now.date())} {o.window} {o.pool.value}{' +$99' if o.after_hours else ''}" for o in opts]
        bad = (prio == Priority.P3 and any(o.day == now.date() for o in opts)) or \
              (prio != Priority.P1 and any(CFG["hours"][o.day.strftime('%a').lower()] == [] for o in opts))
        record("5 scheduling", f"{label}: options", not bad, "; ".join(desc) or "none")

    # P3 offered after-hours surcharged Saturday windows.
    fri = datetime(2026, 11, 6, 15, 0, tzinfo=TZ)
    opts = Scheduler(new_store(fri), CFG).find_options("Suffolk", Priority.P3, False, fri, limit=10)
    surcharged = [o.option_id for o in opts if o.after_hours]
    record("5 scheduling", "routine tune-up isn't steered into +$99 after-hours windows", not surcharged[:1] or opts[0].after_hours is False,
           f"P3 options from Fri 3pm (Suffolk): {[(o.option_id, o.after_hours) for o in opts]}")

    # Customer row created even if the slot is gone (orphan).
    store = new_store()
    call = new_call(store=store, call_id="orphan")
    call.assess_situation(Facts(request_type="tune_up", description="tune-up"))
    call.check_service_address(zip_code="11706", property_type="house")
    opt_id = first_option(call)
    opt = call.offered[opt_id]
    sch = Scheduler(store, CFG)
    while sch.seats_left(opt.county, opt.day, opt.window, opt.pool) > 0:
        _filler(sch, opt)
    before = store.conn.execute("SELECT count(*) FROM customers").fetchone()[0]
    was_refused, out = refused(call.book_appointment, opt_id, **BOOK, phone_read_back_confirmed=True,
                               address_read_back_confirmed=True)
    after = store.conn.execute("SELECT count(*) FROM customers").fetchone()[0]
    record("5 scheduling", "slot taken: refused + re-offered, no orphan rows", was_refused and after == before,
           f"refused={was_refused}; customers {before}->{after}; message={out[:110]!r}")


# 6. Read-backs and data quality ---------------------------------------------------------------

def readbacks() -> None:
    call = ready_call()
    opt = first_option(call)
    was_refused, out = refused(call.book_appointment, opt, **BOOK, phone_read_back_confirmed=False,
                               address_read_back_confirmed=False)
    record("6 read-backs", "flags false -> refused", was_refused, out[:140])

    call = ready_call()
    opt = first_option(call)
    call.agent_said = "Great, booking that now."
    was_refused, out = refused(call.book_appointment, opt, **BOOK, phone_read_back_confirmed=True,
                               address_read_back_confirmed=True)
    record("6 read-backs", "flags true with NO read-back ever spoken -> refused",
           was_refused, f"booked={not was_refused}; {out[:140]!r}")

    call = ready_call()
    opt = first_option(call)
    was_refused, out = refused(call.book_appointment, opt, **{**BOOK, "zip_code": "11743"},
                               phone_read_back_confirmed=True, address_read_back_confirmed=True)
    record("6 read-backs", "ZIP at booking differs from checked ZIP -> refused", was_refused, out[:140])

    for spoken, want in [
        ("five one six, five fifty-five, oh one four two", "+15165550142"),
        ("516 555 0142 no wait 0124", "+15165550124"),
        ("five one six five five five zero one four two... I mean zero one two four", "+15165550124"),
        ("my cell is 516-555-0142 and the house is 516-555-0199", None),
    ]:
        got = normalize_phone(spoken)
        record("6 read-backs", f"normalize_phone({spoken!r})", got == want, f"got {got}")
    call = ready_call()
    opt = first_option(call)
    was_refused, out = refused(call.book_appointment, opt, **{**BOOK, "address": "  "},
                               phone_read_back_confirmed=True, address_read_back_confirmed=True)
    record("6 read-backs", "blank address refused", was_refused, out[:100])
    call = ready_call()
    opt = first_option(call)
    was_refused, out = refused(call.book_appointment, opt, **{**BOOK, "address": "500 Atlantic Ave, Brooklyn"},
                               phone_read_back_confirmed=True, address_read_back_confirmed=True)
    record("6 read-backs", "street address in a different town than the checked ZIP (Brooklyn street, 11706)",
           was_refused, f"booked={not was_refused} (no address validation; documented as cut)")


# 7. Pricing -----------------------------------------------------------------------------------

def pricing() -> None:
    p = CFG["pricing"]
    cases = [
        ("how much to replace a capacitor?", "no number"),
        ("how much is a replacement capacitor", "no number"),
        ("replacement blower motor price", "no number"),
        ("install a new thermostat", "no number"),
        ("how much for a new furnace", "free estimate"),
        ("how much is it to come out tonight", "diagnostic + surcharge"),
        ("what's the cost for a visit on Saturday afternoon", "diagnostic + surcharge"),
        ("how much is a tune-up after hours", "tune-up + surcharge"),
        ("how much is the diagnostic", "diagnostic"),
        ("can you waive the after-hours fee", "surcharge"),
    ]
    call = new_call()
    for item, want in cases:
        out = call.get_pricing(item)
        if want == "no number":
            ok = "$" not in out and "free" not in out.lower()
        elif want == "free estimate":
            ok = "free" in out.lower()
        elif want == "diagnostic + surcharge":
            ok = f"${p['diagnostic']}" in out and f"${p['after_hours_surcharge']}" in out
        elif want == "tune-up + surcharge":
            ok = f"${p['tune_up']}" in out and f"${p['after_hours_surcharge']}" in out
        elif want == "diagnostic":
            ok = f"${p['diagnostic']}" in out
        else:
            ok = f"${p['after_hours_surcharge']}" in out
        record("7 pricing", f"get_pricing({item!r}) gives {want}", ok, f"-> {out!r}")


# 9. Records and failure handling --------------------------------------------------------------

def via_agent(call, name, fn, **args):
    """What agent.SummitAgent._run does: run, then log (which saves the call row)."""
    try:
        out = fn(**args)
    except ActionRefused as e:
        call.log_tool(name, args, str(e), refused=True)
        return str(e)
    call.log_tool(name, args, out)
    return out


def records() -> None:
    # P1 caller hangs up before giving an address.
    call = new_call("+16315550111")
    via_agent(call, "assess_situation", call.assess_situation,
              facts=Facts(no_heat=True, indoor_temp_f=60, vulnerable_occupant=True, description="no heat, newborn"))
    call.finalize([])
    cbs = call.store.callbacks_for_call("stress")
    record("9 records", "P1 caller (newborn, no heat) drops before the address check -> callback created",
           bool(cbs), f"outcome={call.outcome}; callbacks={cbs}; alerts={[a['severity'] for a in call.store.alerts_for_call('stress')]}")

    call = new_call("+16315550111")
    via_agent(call, "assess_situation", call.assess_situation,
              facts=Facts(no_heat=True, indoor_temp_f=64, vulnerable_occupant=False, description="no heat"))
    call.finalize([])
    cbs = call.store.callbacks_for_call("stress")
    record("9 records", "P2 caller drops before the address check -> callback (lead not lost)",
           bool(cbs), f"outcome={call.outcome}; callbacks={len(cbs)}")

    # Worker killed: no finalize.
    call = new_call("+16315550111")
    via_agent(call, "assess_situation", call.assess_situation, facts=Facts(no_heat=True, indoor_temp_f=55, description="no heat, 55 inside"))
    via_agent(call, "check_service_address", call.check_service_address, zip_code="11706", property_type="house")
    # SIGKILL here: finalize() never runs.
    row = call.store.get_call("stress")
    record("9 records", "worker killed mid-call: partial record saved AND the unbooked P1 still gets followed up",
           row is not None and row["outcome"] is not None,
           f"row saved: priority=P{row['priority']} outcome={row['outcome']} ended_at={row['ended_at']} "
           f"tools={len(row['record']['tools'])}; no callback, outcome stays NULL -> 'in progress' forever")

    # Slack unreachable.
    store = new_store()
    n = Notifier(store, slack_webhook_url="https://10.255.255.1/hook")
    call = new_call(store=store, notifier=n)
    t0 = time.monotonic()
    call.screen_caller_turn("smells like gas")
    dt = time.monotonic() - t0
    rows = store.alerts_for_call("stress")
    record("9 records", "Slack unreachable: call not delayed, alert still in DB", dt < 0.5 and rows,
           f"screen took {dt*1000:.0f} ms; alerts={[(r['severity'], r['summary'][:60]) for r in rows]}")

    # After-hours P1 'pages on-call': what actually happens?
    night = datetime(2026, 11, 3, 23, 30, tzinfo=TZ)
    call = new_call(now=night)
    out = call.assess_situation(Facts(no_heat=True, indoor_temp_f=54, description="no heat"))
    rows = call.store.alerts_for_call("stress")
    record("9 records", "after-hours P1: something other than a DB row/optional Slack reaches on-call",
           False, f"alert row: {rows[-1]['summary']!r}; the only 'page' is that text. Model told: {out[-80:]!r}")


def main() -> int:
    for fn in (lexicon_sweep, safety_backend, triage_boundaries, identity, service_area, scheduling,
               readbacks, pricing, records):
        try:
            fn()
        except Exception as e:  # a crash is a finding too
            import traceback
            record(fn.__name__, "probe crashed", False, traceback.format_exc()[-600:])
    fails = sum(not ok for *_, ok, _ in [(s, p, ok, e) for s, p, ok, e in RESULTS])
    print(f"# Backend attacks (no LLM)\n\nRun {datetime.now():%Y-%m-%d %H:%M}. "
          f"{len(RESULTS) - fails}/{len(RESULTS)} probes held; {fails} findings.\n")
    section = None
    for s, probe, ok, ev in RESULTS:
        if s != section:
            print(f"\n## {s}\n\n| | probe | evidence |\n|---|---|---|")
            section = s
        print(f"| {'PASS' if ok else '**FAIL**'} | {probe.replace('|', '/')} | {str(ev).replace('|', '/').replace(chr(10), ' ')} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
