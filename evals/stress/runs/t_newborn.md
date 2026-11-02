# t_newborn

Group: triage. Caller ID: none. Clock: Tue 2026-11-03 10:00 EST. Mode: scripted.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| P1 | PASS | PASS | PASS | 3/3 |
| record_complete | PASS | PASS | PASS | 3/3 |

## Run 1


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Our heat stopped working and we have a two-week-old baby. It's 64 inside.

> `assess_situation` {"description": "Heat stopped working", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": true, "no_cooling": null, "indoor_temp_f": 64, "vulnerable_occupant": true, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no heat with a vulnerable occupant). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** Thank you for sharing that. I understand your heat stopped working and you have a young baby at home. Can you please provide the ZIP code and type of property where the service is needed?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_newborn-1", "severity": "urgent", "summary": "P1 no heat with a vulnerable occupant: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no heat with a vulnerable occupant'] property=unknown area=None verified=None
**summary**: P1 urgent: no heat with a vulnerable occupant. Caller says: Heat stopped working. 64°F inside. Vulnerable occupant at home.

## Run 2


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Our heat stopped working and we have a two-week-old baby. It's 64 inside.

> `assess_situation` {"description": "Heat stopped working. 64 degrees inside. Baby two weeks old at home.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": true, "no_cooling": null, "indoor_temp_f": 64, "vulnerable_occupant": true, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no heat with a vulnerable occupant). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** I see the heat is out and you have a young baby at home, so this is urgent. Can you tell me the street address, ZIP code, and what kind of property it is?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_newborn-2", "severity": "urgent", "summary": "P1 no heat with a vulnerable occupant: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no heat with a vulnerable occupant'] property=unknown area=None verified=None
**summary**: P1 urgent: no heat with a vulnerable occupant. Caller says: Heat stopped working. 64 degrees inside. Baby two weeks old at home.. 64°F inside. Vulnerable occupant at home.

## Run 3


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Our heat stopped working and we have a two-week-old baby. It's 64 inside.

> `assess_situation` {"description": "heat stopped working", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": true, "no_cooling": null, "indoor_temp_f": 64, "vulnerable_occupant": true, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no heat with a vulnerable occupant). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** I understand your heat isn't working, and you have a young baby at home with the temperature at 64 degrees. May I have the ZIP code and type of property where the work is needed?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_newborn-3", "severity": "urgent", "summary": "P1 no heat with a vulnerable occupant: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no heat with a vulnerable occupant'] property=unknown area=None verified=None
**summary**: P1 urgent: no heat with a vulnerable occupant. Caller says: heat stopped working. 64°F inside. Vulnerable occupant at home.