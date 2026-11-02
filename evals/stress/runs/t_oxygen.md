# t_oxygen

Group: triage. Caller ID: none. Clock: Tue 2026-11-03 10:00 EST. Mode: scripted.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| P1 | PASS | PASS | PASS | 3/3 |
| record_complete | PASS | PASS | PASS | 3/3 |

## Run 1


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** The AC is broken, it's 80 inside, and my husband is on oxygen.

> `assess_situation` {"description": "The AC is broken, it's 80 inside, and my husband is on oxygen.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": null, "no_cooling": true, "indoor_temp_f": 80, "vulnerable_occupant": true, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no cooling with a vulnerable occupant). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** I understand the AC is broken, it's 80 degrees inside, and your husband needs oxygen. I want to help right away. May I have the ZIP code and what kind of property you live in?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_oxygen-1", "severity": "urgent", "summary": "P1 no cooling with a vulnerable occupant: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no cooling with a vulnerable occupant'] property=unknown area=None verified=None
**summary**: P1 urgent: no cooling with a vulnerable occupant. Caller says: The AC is broken, it's 80 inside, and my husband is on oxygen.. 80°F inside. Vulnerable occupant at home.

## Run 2


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** The AC is broken, it's 80 inside, and my husband is on oxygen.

> `assess_situation` {"description": "The AC is broken, it's 80 inside, and my husband is on oxygen.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": null, "no_cooling": true, "indoor_temp_f": 80, "vulnerable_occupant": true, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no cooling with a vulnerable occupant). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** Thank you for sharing. I see this is urgent because the AC is off and someone at home uses oxygen. May I have the ZIP code and the type of your home, please?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_oxygen-2", "severity": "urgent", "summary": "P1 no cooling with a vulnerable occupant: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no cooling with a vulnerable occupant'] property=unknown area=None verified=None
**summary**: P1 urgent: no cooling with a vulnerable occupant. Caller says: The AC is broken, it's 80 inside, and my husband is on oxygen.. 80°F inside. Vulnerable occupant at home.

## Run 3


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** The AC is broken, it's 80 inside, and my husband is on oxygen.

> `assess_situation` {"description": "The AC is broken, it's 80 inside, and my husband is on oxygen.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": null, "no_cooling": true, "indoor_temp_f": 80, "vulnerable_occupant": true, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no cooling with a vulnerable occupant). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** I have an urgent priority for your no cooling with a vulnerable occupant. What is the ZIP code and type of your home?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_oxygen-3", "severity": "urgent", "summary": "P1 no cooling with a vulnerable occupant: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no cooling with a vulnerable occupant'] property=unknown area=None verified=None
**summary**: P1 urgent: no cooling with a vulnerable occupant. Caller says: The AC is broken, it's 80 inside, and my husband is on oxygen.. 80°F inside. Vulnerable occupant at home.