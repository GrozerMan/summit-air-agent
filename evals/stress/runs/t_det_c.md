# t_det_c

Group: triage. Caller ID: none. Clock: Tue 2026-11-03 10:00 EST. Mode: scripted.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| P1 | PASS | PASS | PASS | 3/3 |
| record_complete | PASS | PASS | PASS | 3/3 |

## Run 1


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** No heat. 56 degrees. Elderly dad at home.

> `assess_situation` {"description": "No heat. 56 degrees. Elderly dad at home.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": true, "no_cooling": null, "indoor_temp_f": 56, "vulnerable_occupant": true, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no heat with a vulnerable occupant, no heat, 56°F inside). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** Thank you. Is your dad at home now? May I have the address where the heat is out?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_det_c-1", "severity": "urgent", "summary": "P1 no heat with a vulnerable occupant, no heat, 56\u00b0F inside: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no heat with a vulnerable occupant', 'no heat, 56°F inside'] property=unknown area=None verified=None
**summary**: P1 urgent: no heat with a vulnerable occupant, no heat, 56°F inside. Caller says: No heat. 56 degrees. Elderly dad at home.. 56°F inside. Vulnerable occupant at home.

## Run 2


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** No heat. 56 degrees. Elderly dad at home.

> `assess_situation` {"description": "No heat. 56 degrees. Elderly dad at home.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": true, "no_cooling": null, "indoor_temp_f": 56, "vulnerable_occupant": true, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no heat with a vulnerable occupant, no heat, 56°F inside). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** I'm sorry to hear that your heat isn't working and that your dad is vulnerable at home. Can you please give me the ZIP code and the type of property where you need service?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_det_c-2", "severity": "urgent", "summary": "P1 no heat with a vulnerable occupant, no heat, 56\u00b0F inside: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no heat with a vulnerable occupant', 'no heat, 56°F inside'] property=unknown area=None verified=None
**summary**: P1 urgent: no heat with a vulnerable occupant, no heat, 56°F inside. Caller says: No heat. 56 degrees. Elderly dad at home.. 56°F inside. Vulnerable occupant at home.

## Run 3


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** No heat. 56 degrees. Elderly dad at home.

> `assess_situation` {"description": "No heat. 56 degrees. Elderly dad at home.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": true, "no_cooling": null, "indoor_temp_f": 56, "vulnerable_occupant": true, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no heat with a vulnerable occupant, no heat, 56°F inside). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** I understand there's no heat and it's 56 degrees inside with your elderly dad at home, which is urgent. Can you tell me your address's ZIP code and what kind of property it is?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_det_c-3", "severity": "urgent", "summary": "P1 no heat with a vulnerable occupant, no heat, 56\u00b0F inside: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no heat with a vulnerable occupant', 'no heat, 56°F inside'] property=unknown area=None verified=None
**summary**: P1 urgent: no heat with a vulnerable occupant, no heat, 56°F inside. Caller says: No heat. 56 degrees. Elderly dad at home.. 56°F inside. Vulnerable occupant at home.