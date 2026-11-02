# Backend attacks (no LLM)

Run 2026-11-02 00:24. 59/130 probes held; 71 findings.


## 1 safety lexicon (gas)

| | probe | evidence |
|---|---|---|
| PASS | something smells like a skunk near the furnace | hazard_in -> 'gas' |
| PASS | I smelled gas earlier but it's gone now | hazard_in -> 'gas' |
| PASS | it smells kind of like natural gas in the basement | hazard_in -> 'gas' |
| PASS | there's a gas odor by the boiler | hazard_in -> 'gas' |
| PASS | the whole basement reeks of gas | hazard_in -> 'gas' |
| PASS | it smells like rotten eggs | hazard_in -> 'gas' |
| PASS | smells sulfury | hazard_in -> 'gas' |
| **FAIL** | It won't stop smelling like gas | hazard_in -> None |
| **FAIL** | I can't stand the rotten egg smell in the basement | hazard_in -> None |
| PASS | I can't get rid of this gas smell | hazard_in -> 'gas' |
| PASS | We can't figure out where the gas smell is coming from | hazard_in -> 'gas' |
| **FAIL** | The heat won't come on without a weird gas smell | hazard_in -> None |
| **FAIL** | It doesn't smell like gas now, but it did this morning | hazard_in -> None |
| **FAIL** | I don't smell gas anymore. I did earlier though | hazard_in -> None |
| **FAIL** | There's no gas smell now but there was one an hour ago | hazard_in -> None |
| **FAIL** | smells eggy down by the furnace | hazard_in -> None |
| **FAIL** | there's like a sewer smell coming from the furnace room | hazard_in -> None |
| **FAIL** | the pilot light went out and now there's a weird smell | hazard_in -> None |
| **FAIL** | I think the gas is leaking | hazard_in -> None |
| PASS | I hear hissing from the gas pipe and it smells funny | hazard_in -> 'gas' |

## 1 safety lexicon (CO)

| | probe | evidence |
|---|---|---|
| PASS | my CO alarm is beeping | hazard_in -> 'co' |
| PASS | the carbon monoxide alarm went off last night | hazard_in -> 'co' |
| **FAIL** | my CO detector is going crazy | hazard_in -> None |
| **FAIL** | the detector for carbon monoxide keeps beeping | hazard_in -> None |
| **FAIL** | the alarm that says CO on it is going off | hazard_in -> None |
| **FAIL** | carbon monoxide alarm | hazard_in -> None |
| **FAIL** | we all have headaches and the kids are dizzy | hazard_in -> None |
| **FAIL** | the whole family's been really sleepy and nauseous since the heat came on | hazard_in -> None |

## 1 safety lexicon (false positive)

| | probe | evidence |
|---|---|---|
| PASS | my gas bill is high | hazard_in -> None |
| PASS | I need a gas furnace tune-up | hazard_in -> None |
| PASS | the new filter smells dusty | hazard_in -> None |
| PASS | no, I don't smell gas, it's dusty | hazard_in -> None |
| **FAIL** | there's a skunk living under my porch and my AC is broken | hazard_in -> 'gas' |
| PASS | my car's gas mileage is bad lately, anyway my AC is out | hazard_in -> None |

## 1 safety backend

| | probe | evidence |
|---|---|---|
| PASS | gas then 'it's nothing, just noisy' stays P0 | priority=<Priority.P0: 0> |
| **FAIL** | model paraphrase 'asked if it smells like gas ... said dusty' does NOT go P0 | priority=<Priority.P0: 0>, reasons=["gas smell reported (caller's words)"] |
| **FAIL** | gas reported AFTER booking: booking flagged/cancelled, appointment shows P0 | appointment row: id=2 status=booked priority=P3; alerts=['critical']; outcome=safety_emergency |
| **FAIL** | unknown caller, gas before address: script names a gas utility | script="This could be a gas leak, so please leave the house now and take everyone with you. Don't touch light switches, appliances or phones on your way out. Once you're outside and away from the house, call nine-one-one. Don't go back in until they tell you it's safe." |
| **FAIL** | CO symptoms without the word 'alarm' reach P0 without the model | priority after screen=None |

## 2 triage

| | probe | evidence |
|---|---|---|
| PASS | no heat at 57°F -> P1 | P1 |
| PASS | no heat at 58°F -> P1 | P1 |
| PASS | no heat at 59°F -> P2 | P2 |
| PASS | no cooling at 84°F -> P2 | P2 |
| PASS | no cooling at 85°F -> P1 | P1 |
| PASS | no cooling at 86°F -> P1 | P1 |
| PASS | no heat 64°F + vulnerable -> P1 | P1 |
| PASS | persistent burning beats first-use dusty | P1 |
| PASS | same facts -> same priority (1000 runs) | {<Priority.P1: 1>} |
| PASS | 'it's an emergency' tune-up stays P3 | P3 |
| PASS | tune-up + vulnerable occupant stays P3 (vulnerable only matters with no heat/cool) | P3 |

## 3 identity

| | probe | evidence |
|---|---|---|
| **FAIL** | caller says he is NOT Dana, then gives last name 'Reyes' -> must not verify as Dana | verified=Dana Reyes; result='Verified. Dana Reyes, 12 Elm Street, Mineola, ZIP 11501 (Nassau County). Active Summit Comfort Club member: thank them for being a member. Upcoming: appointment' |
| **FAIL** | stranger from another number: member phone + last name -> full account | verified=Dana Reyes; result='Verified. Dana Reyes, 12 Elm Street, Mineola, ZIP 11501 (Nassau County). Active Summit Comfort Club member: thank them for being a member. Upcoming: appointment #1, tune-up, Thursday, November 5, betw' |
| **FAIL** | repeated ZIP guesses are cut off | verified after 8 lookup_customer attempts (no attempt limit) |
| PASS | wrong last name + right ZIP is refused | verified=None |
| PASS | unverified 'I'm a member' gets no $0 diagnostic | get_pricing -> 'Summit Comfort Club: no diagnostic fee, two tune-ups a year, priority scheduling. The office can go over membership pricing.' |
| PASS | unverified booking leaves Dana's customer row untouched | customers row: 12 Elm Street, Mineola |
| **FAIL** | a stranger's booking on Dana's number does not appear as Dana's appointment | appointment customer_id=1 (Dana is 1), contact=Mallory Stone, address=9 Other Street, Garden City, 11530; Dana's verified summary: "Verified. Dana Reyes, 12 Elm Street, Mineola, ZIP 11501 (Nassau County). Active Summit Comfort Club member: thank them for being a member. Upcoming: appointment #2, no heat, today, Tuesday, between 4 and 6 PM. Upcoming: appointment #1, tune-up, Thursday, November 5, between 10 AM and noon. If the work is at this address you don't need to check the address again." |
| **FAIL** | Dana cannot reschedule Mallory's booking | refused=False: 'Offer these arrival windows, earliest first. The technician arrives within the window.\n- NAS-1103-1200-M: today, Tuesday' |
| **FAIL** | Ann's unverified booking on the shared line attaches to Ann | attached to customer #4 Tom Walsh |

## 4 area

| | probe | evidence |
|---|---|---|
| **FAIL** | Elmont (11003, Nassau) is accepted | check_zip: ask_town=True; then check_town('Elmont') -> in_area=False, outside=True: 'Elmont is outside our service area (Nassau, Suffolk, Westchester counties). Let them know ' |
| **FAIL** | Inwood (11096, Nassau) is accepted | check_zip: ask_town=True; then check_town('Inwood') -> in_area=False, outside=True: 'Inwood is outside our service area (Nassau, Suffolk, Westchester counties). Let them know ' |
| **FAIL** | Bayville (11709, Nassau) is accepted | check_zip: ask_town=True; then check_town('Bayville') -> in_area=False, outside=True: 'Bayville is outside our service area (Nassau, Suffolk, Westchester counties). Let them kno' |
| **FAIL** | Albertson (11507, Nassau) is accepted | check_zip: ask_town=True; then check_town('Albertson') -> in_area=False, outside=True: 'Albertson is outside our service area (Nassau, Suffolk, Westchester counties). Let them kn' |
| **FAIL** | Carle Place (11514, Nassau) is accepted | check_zip: ask_town=True; then check_town('Carle Place') -> in_area=False, outside=True: 'Carle Place is outside our service area (Nassau, Suffolk, Westchester counties). Let them ' |
| **FAIL** | Atlantic Beach (11509, Nassau) is accepted | check_zip: ask_town=True; then check_town('Atlantic Beach') -> in_area=False, outside=True: 'Atlantic Beach is outside our service area (Nassau, Suffolk, Westchester counties). Let th' |
| **FAIL** | New Hyde Park (11042, Nassau) is accepted | check_zip: ask_town=True; then check_town('New Hyde Park') -> in_area=False, outside=True: 'New Hyde Park is outside our service area (Nassau, Suffolk, Westchester counties). Let the' |
| **FAIL** | town only: 'East Meadow' | in_area=False outside=True county=None |
| **FAIL** | town only: 'Merrick' | in_area=False outside=True county=None |
| **FAIL** | town only: 'Bellmore' | in_area=False outside=True county=None |
| **FAIL** | town only: 'Syosset' | in_area=False outside=True county=None |
| **FAIL** | town only: 'Port Washington' | in_area=False outside=True county=None |
| **FAIL** | town only: 'Massapequa Park' | in_area=False outside=True county=None |
| **FAIL** | town only: 'Rockville Center' | in_area=False outside=True county=None |
| **FAIL** | town only: 'Mt. Vernon' | in_area=False outside=True county=None |
| **FAIL** | town only: 'Port Chester' | in_area=False outside=True county=None |
| **FAIL** | town only: 'Hastings-on-Hudson' | in_area=False outside=True county=None |
| PASS | town only: 'Long Beach' | in_area=True outside=False county=Nassau |
| PASS | Floral Park (spans Queens/Nassau) 11001 | in_area=True ask_town=False outside=False county=Nassau |
| PASS | Bronx 10467 | in_area=False ask_town=False outside=True county=None |
| PASS | Brooklyn 11215 | in_area=False ask_town=False outside=True county=None |
| **FAIL** | property_kind('12-unit apartment building I own') -> commercial | got 'residential' |
| **FAIL** | property_kind('the boiler for the whole apartment building') -> commercial | got 'residential' |
| PASS | property_kind('restaurant') -> commercial | got 'commercial' |
| PASS | property_kind('my dental office') -> not residential | got 'unknown' |
| PASS | property_kind('two-family house') -> residential | got 'residential' |
| PASS | property_kind('condo unit') -> residential | got 'residential' |
| PASS | property_kind('4 family home') -> residential | got 'residential' |
| **FAIL** | property_kind('apartment above a store') -> residential | got 'commercial' |
| PASS | home business: 'I run a daycare out of my house' (policy call, not graded) | property_kind -> 'residential'; 'my home business office' -> 'commercial' |
| **FAIL** | booking refused after property turns out commercial | property=commercial; book_appointment refused=False: 'Booked: appointment #2, tomorrow, Wednesday, between noon and 2 PM, at 33 Shore Road, Bay Shore. Tune-up: $159. Confirm ' |
| **FAIL** | verified member: 'AC at my restaurant' -> options refused until address checked | property=residential area=11501; refused=False |
| **FAIL** | Nassau option can't be booked for a Westchester address | option NAS-1104-0800-R; refused=False; row={'county': 'Nassau', 'service_address': '1 Main St, White Plains, 10601'} |

## 5 scheduling

| | probe | evidence |
|---|---|---|
| PASS | 4 sessions race for the last seat, 50 runs -> exactly one winner each time | winners per run: [1] |
| **FAIL** | two sessions move the same appointment at once -> one booked row (30 runs) | 30/30 runs left TWO booked appointments for one original |
| **FAIL** | P1 call can't be booked into a window offered while it was P3 (>24h out) | offered while P3: ['SUF-1104-1200-R', 'SUF-1104-1600-R', 'SUF-1105-0800-R']; booked SUF-1105-0800-R = 46h out as priority P1; refused=False: 'Booked: appointment #2, Thursday, November 5, between 8 and 10 AM, at 33 Shore R' |
| **FAIL** | P2 with no capacity in 72h -> refused/escalated, not offered day 5+ | first P2 option NAS-1109-1000-R starts 144h out; p2_within_hours is never read by code |
| **FAIL** | routine work is not offered on Thanksgiving (Thu Nov 26) | 2 Thanksgiving windows offered to a P3 caller: ['NAS-1126-0800-R', 'NAS-1126-1000-R'] after_hours=[False, False] |
| PASS | Sat 1:30pm P3: options | Monday, November 9 10:00-12:00 regular; Monday, November 9 16:00-18:00 regular; Tuesday, November 10 08:00-10:00 regular |
| PASS | Sat 3pm P2: options | today, Saturday 16:00-18:00 regular +$99; Monday, November 9 10:00-12:00 regular; Monday, November 9 16:00-18:00 regular |
| PASS | Sun 11am P3: options | tomorrow, Monday 10:00-12:00 regular; tomorrow, Monday 16:00-18:00 regular; Tuesday, November 10 08:00-10:00 regular |
| PASS | Sun 11am P1: options | today, Sunday 12:00-14:00 regular +$99; today, Sunday 14:00-16:00 regular +$99; today, Sunday 16:00-18:00 emergency +$99 |
| PASS | Mon 11:55pm P3: options | tomorrow, Tuesday 16:00-18:00 regular; Wednesday, November 4 08:00-10:00 regular; Wednesday, November 4 10:00-12:00 regular |
| PASS | Tue 12:05am P3: options | tomorrow, Wednesday 08:00-10:00 regular; tomorrow, Wednesday 10:00-12:00 regular; tomorrow, Wednesday 12:00-14:00 regular |
| PASS | Fri 6pm P3: options | tomorrow, Saturday 08:00-10:00 regular; tomorrow, Saturday 14:00-16:00 regular +$99; tomorrow, Saturday 16:00-18:00 regular +$99 |
| PASS | routine tune-up isn't steered into +$99 after-hours windows | P3 options from Fri 3pm (Suffolk): [('SUF-1107-0800-R', False), ('SUF-1107-1000-R', False), ('SUF-1107-1200-R', False), ('SUF-1109-1400-R', False), ('SUF-1109-1600-R', False), ('SUF-1111-0800-R', False), ('SUF-1111-1000-R', False), ('SUF-1111-1600-R', False), ('SUF-1112-0800-R', False), ('SUF-1112-1000-R', False)] |
| **FAIL** | slot taken: refused + re-offered, no orphan rows | refused=True; customers 5->6; message='That window was just taken by another booking. Apologize, then offer these instead. Offer these arrival window' |

## 6 read-backs

| | probe | evidence |
|---|---|---|
| PASS | flags false -> refused | Not booked yet: read the phone number back digit by digit and get a yes; read the full address back and get a yes. |
| **FAIL** | flags true with NO read-back ever spoken -> backend can't tell; booked | booked=True; the backend never sees the agent's words, so the flag is the model's say-so |
| PASS | ZIP at booking differs from checked ZIP -> refused | Not booked yet: ZIP 11743 doesn't match the ZIP checked for the service area (11706); confirm the address and run check_service_address agai |
| **FAIL** | normalize_phone('five one six, five fifty-five, oh one four two') | got None |
| **FAIL** | normalize_phone('516 555 0142 no wait 0124') | got None |
| **FAIL** | normalize_phone('five one six five five five zero one four two... I mean zero one two four') | got None |
| PASS | normalize_phone('my cell is 516-555-0142 and the house is 516-555-0199') | got None |
| PASS | blank address refused | Not booked yet: missing street address. |
| **FAIL** | street address in a different town than the checked ZIP (Brooklyn street, 11706) | booked=True (no address validation; documented as cut) |

## 7 pricing

| | probe | evidence |
|---|---|---|
| PASS | get_pricing('how much to replace a capacitor?') gives no number | -> "Don't estimate repairs. The technician quotes on site before any work starts." |
| **FAIL** | get_pricing('how much is a replacement capacitor') gives no number | -> 'Replacement estimates are free.' |
| **FAIL** | get_pricing('replacement blower motor price') gives no number | -> 'Replacement estimates are free.' |
| **FAIL** | get_pricing('install a new thermostat') gives no number | -> 'Replacement estimates are free.' |
| **FAIL** | get_pricing('how much for a new furnace') gives free estimate | -> "Don't estimate repairs. The technician quotes on site before any work starts." |
| **FAIL** | get_pricing('how much is it to come out tonight') gives diagnostic + surcharge | -> 'After-hours visits add $99.' |
| **FAIL** | get_pricing("what's the cost for a visit on Saturday afternoon") gives diagnostic + surcharge | -> 'After-hours visits add $99.' |
| **FAIL** | get_pricing('how much is a tune-up after hours') gives tune-up + surcharge | -> 'A tune-up is $159. Members get two a year included.' |
| PASS | get_pricing('how much is the diagnostic') gives diagnostic | -> "The diagnostic visit is $129; it's free for Summit Comfort Club members." |
| PASS | get_pricing('can you waive the after-hours fee') gives surcharge | -> 'After-hours visits add $99.' |

## 9 records

| | probe | evidence |
|---|---|---|
| **FAIL** | P1 caller (newborn, no heat) drops before the address check -> callback created | outcome=info_only; callbacks=[]; alerts=['urgent'] |
| **FAIL** | P2 caller drops before the address check -> callback (lead not lost) | outcome=info_only; callbacks=0 |
| **FAIL** | worker killed mid-call: partial record saved AND the unbooked P1 still gets followed up | row saved: priority=P1 outcome=None ended_at=None tools=2; no callback, outcome stays NULL -> 'in progress' forever |
| PASS | Slack unreachable: call not delayed, alert still in DB | screen took 0 ms; alerts=[('critical', 'P0 gas smell reported: unknown caller (no number)')] |
| **FAIL** | after-hours P1: something other than a DB row/optional Slack reaches on-call | alert row: 'P1 no heat, 54°F inside: unknown caller (no number). After hours: page on-call.'; the only 'page' is that text. Model told: 'e address. The office is closed, so the on-call technician has been alerted too.' |
