# f_p1_hangs_up_early

Group: records. Caller ID: +16315550111. Clock: Tue 2026-11-03 10:00 EST. Mode: scripted.

> Caller drops right after triage, before giving an address.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| callback_for_P1 | **FAIL** | **FAIL** | **FAIL** | 0/3 |
| P1 | PASS | PASS | PASS | 3/3 |
| record_complete | PASS | PASS | PASS | 3/3 |

## Run 1

- ✗ **callback_for_P1**: 0 callbacks

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Our heat is out and we have a newborn. It's 60 in here.

> `assess_situation` {"description": "Our heat is out and we have a newborn. It's 60 in here.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": true, "no_cooling": null, "indoor_temp_f": 60, "vulnerable_occupant": true, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no heat with a vulnerable occupant). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** I'm sorry you're dealing with no heat, especially with a newborn at home. We'll get someone to help as soon as possible. May I have the ZIP code and what type of property you live in?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-f_p1_hangs_up_early-1", "severity": "urgent", "summary": "P1 no heat with a vulnerable occupant: unknown caller (631-555-0111).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no heat with a vulnerable occupant'] property=unknown area=None verified=None
**summary**: P1 urgent: no heat with a vulnerable occupant. Caller says: Our heat is out and we have a newborn. It's 60 in here.. 60°F inside. Vulnerable occupant at home. Caller 631-555-0111 (not verified).

## Run 2

- ✗ **callback_for_P1**: 0 callbacks

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Our heat is out and we have a newborn. It's 60 in here.

> `assess_situation` {"description": "Heat is out. It's 60 degrees inside. We have a newborn at home.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": true, "no_cooling": null, "indoor_temp_f": 60, "vulnerable_occupant": true, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no heat with a vulnerable occupant). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** I understand the heat is out, it's 60 degrees inside, and you have a newborn at home. Let me check when we can get someone to you earliest. What's the ZIP code and property type of where you need service?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-f_p1_hangs_up_early-2", "severity": "urgent", "summary": "P1 no heat with a vulnerable occupant: unknown caller (631-555-0111).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no heat with a vulnerable occupant'] property=unknown area=None verified=None
**summary**: P1 urgent: no heat with a vulnerable occupant. Caller says: Heat is out. It's 60 degrees inside. We have a newborn at home.. 60°F inside. Vulnerable occupant at home. Caller 631-555-0111 (not verified).

## Run 3

- ✗ **callback_for_P1**: 0 callbacks

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Our heat is out and we have a newborn. It's 60 in here.

> `assess_situation` {"description": "Our heat is out and we have a newborn. It's 60 in here.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": true, "no_cooling": null, "indoor_temp_f": 60, "vulnerable_occupant": true, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no heat with a vulnerable occupant). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** I understand your heat is out and you have a newborn at home, so we will treat this as urgent. What is the ZIP code and property type for where the work is needed?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-f_p1_hangs_up_early-3", "severity": "urgent", "summary": "P1 no heat with a vulnerable occupant: unknown caller (631-555-0111).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no heat with a vulnerable occupant'] property=unknown area=None verified=None
**summary**: P1 urgent: no heat with a vulnerable occupant. Caller says: Our heat is out and we have a newborn. It's 60 in here.. 60°F inside. Vulnerable occupant at home. Caller 631-555-0111 (not verified).