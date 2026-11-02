# t_pregnant

Group: triage. Caller ID: none. Clock: Tue 2026-11-03 10:00 EST. Mode: scripted.

> Policy call: is pregnancy 'vulnerable'? Recorded for consistency.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| P1_or_P2_recorded | PASS | PASS | PASS | 3/3 |
| record_complete | PASS | PASS | PASS | 3/3 |

## Run 1


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** The heat's not working, it's 64 inside, and I'm eight months pregnant.

> `assess_situation` {"description": "The heat's not working, it's 64 inside, and I'm eight months pregnant.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": true, "no_cooling": null, "indoor_temp_f": 64, "vulnerable_occupant": true, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no heat with a vulnerable occupant). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** Thank you for sharing that. Could I get the ZIP code and the type of home where the service is needed?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_pregnant-1", "severity": "urgent", "summary": "P1 no heat with a vulnerable occupant: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no heat with a vulnerable occupant'] property=unknown area=None verified=None
**summary**: P1 urgent: no heat with a vulnerable occupant. Caller says: The heat's not working, it's 64 inside, and I'm eight months pregnant.. 64°F inside. Vulnerable occupant at home.

## Run 2


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** The heat's not working, it's 64 inside, and I'm eight months pregnant.

> `assess_situation` {"description": "The heat's not working, it's 64 inside, and I'm eight months pregnant.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": true, "no_cooling": null, "indoor_temp_f": 64, "vulnerable_occupant": true, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no heat with a vulnerable occupant). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** Thanks for letting me know. Can you please give me the ZIP code and what type of property it is where the heat isn't working?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_pregnant-2", "severity": "urgent", "summary": "P1 no heat with a vulnerable occupant: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no heat with a vulnerable occupant'] property=unknown area=None verified=None
**summary**: P1 urgent: no heat with a vulnerable occupant. Caller says: The heat's not working, it's 64 inside, and I'm eight months pregnant.. 64°F inside. Vulnerable occupant at home.

## Run 3


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** The heat's not working, it's 64 inside, and I'm eight months pregnant.

> `assess_situation` {"description": "The heat's not working", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": true, "no_cooling": null, "indoor_temp_f": 64, "vulnerable_occupant": true, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no heat with a vulnerable occupant). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** I understand the heat is not working and it's 64 degrees inside with you eight months pregnant. Can you please give me the ZIP code and type of your property, like house or apartment?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_pregnant-3", "severity": "urgent", "summary": "P1 no heat with a vulnerable occupant: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no heat with a vulnerable occupant'] property=unknown area=None verified=None
**summary**: P1 urgent: no heat with a vulnerable occupant. Caller says: The heat's not working. 64°F inside. Vulnerable occupant at home.