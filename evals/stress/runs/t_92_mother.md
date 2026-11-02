# t_92_mother

Group: triage. Caller ID: none. Clock: Tue 2026-11-03 10:00 EST. Mode: scripted.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| P1 | PASS | PASS | PASS | 3/3 |
| record_complete | PASS | PASS | PASS | 3/3 |

## Run 1


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** The furnace quit. It's 63 in here and my 92-year-old mother lives with me.

> `assess_situation` {"description": "The furnace quit. It's 63 in here and my 92-year-old mother lives with me.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": true, "no_cooling": null, "indoor_temp_f": 63, "vulnerable_occupant": true, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no heat with a vulnerable occupant). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** I'm sorry to hear the furnace quit, especially with your 92-year-old mother at home. Could you please tell me the ZIP code and what kind of property this is? (For example, house, condo, etc.)

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_92_mother-1", "severity": "urgent", "summary": "P1 no heat with a vulnerable occupant: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no heat with a vulnerable occupant'] property=unknown area=None verified=None
**summary**: P1 urgent: no heat with a vulnerable occupant. Caller says: The furnace quit. It's 63 in here and my 92-year-old mother lives with me.. 63°F inside. Vulnerable occupant at home.

## Run 2


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** The furnace quit. It's 63 in here and my 92-year-old mother lives with me.

> `assess_situation` {"description": "The furnace quit. It's 63 degrees inside, and a 92-year-old mother lives with the caller.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": true, "no_cooling": null, "indoor_temp_f": 63, "vulnerable_occupant": true, "active_leak": null, "minor_drip": null, "request_type": n  
> → Priority is now P1 urgent (no heat with a vulnerable occupant). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** I'm sorry to hear your furnace quit, especially with your elderly mother at home. Can you please provide the ZIP code and what kind of property it is? For example, a house, condo, or something else.

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_92_mother-2", "severity": "urgent", "summary": "P1 no heat with a vulnerable occupant: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no heat with a vulnerable occupant'] property=unknown area=None verified=None
**summary**: P1 urgent: no heat with a vulnerable occupant. Caller says: The furnace quit. It's 63 degrees inside, and a 92-year-old mother lives with the caller.. 63°F inside. Vulnerable occupant at home.

## Run 3


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** The furnace quit. It's 63 in here and my 92-year-old mother lives with me.

> `assess_situation` {"description": "The furnace quit. It's 63 in here and my 92-year-old mother lives with me.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": true, "no_cooling": null, "indoor_temp_f": 63, "vulnerable_occupant": true, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no heat with a vulnerable occupant). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** I understand the heat is out and you have a vulnerable person at home. Could you please tell me your ZIP code and what kind of property this is?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_92_mother-3", "severity": "urgent", "summary": "P1 no heat with a vulnerable occupant: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no heat with a vulnerable occupant'] property=unknown area=None verified=None
**summary**: P1 urgent: no heat with a vulnerable occupant. Caller says: The furnace quit. It's 63 in here and my 92-year-old mother lives with me.. 63°F inside. Vulnerable occupant at home.