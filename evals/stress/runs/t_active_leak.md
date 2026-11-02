# t_active_leak

Group: triage. Caller ID: none. Clock: Tue 2026-11-03 10:00 EST. Mode: scripted.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| P1 | PASS | PASS | PASS | 3/3 |
| record_complete | PASS | PASS | PASS | 3/3 |

## Run 1


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Water is pouring out of the AC unit in the attic and dripping through the ceiling.

> `assess_situation` {"description": "Water is pouring out of the AC unit in the attic and dripping through the ceiling.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": null, "no_cooling": null, "indoor_temp_f": null, "vulnerable_occupant": null, "active_leak": true, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (active water leak). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** That sounds urgent with water pouring inside. Can you please give me the ZIP code and what kind of property it is? For example, a house, condo, or something else.

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_active_leak-1", "severity": "urgent", "summary": "P1 active water leak: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['active water leak'] property=unknown area=None verified=None
**summary**: P1 urgent: active water leak. Caller says: Water is pouring out of the AC unit in the attic and dripping through the ceiling..

## Run 2


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Water is pouring out of the AC unit in the attic and dripping through the ceiling.

> `assess_situation` {"description": "Water is pouring out of the AC unit in the attic and dripping through the ceiling.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": null, "no_cooling": null, "indoor_temp_f": null, "vulnerable_occupant": null, "active_leak": true, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (active water leak). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** That leak sounds urgent, we'll try for the earliest available tomorrow. Can you tell me the ZIP code and what kind of property it is? For example, a house or condo?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_active_leak-2", "severity": "urgent", "summary": "P1 active water leak: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['active water leak'] property=unknown area=None verified=None
**summary**: P1 urgent: active water leak. Caller says: Water is pouring out of the AC unit in the attic and dripping through the ceiling..

## Run 3


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Water is pouring out of the AC unit in the attic and dripping through the ceiling.

> `assess_situation` {"description": "Water is pouring out of the AC unit in the attic and dripping through the ceiling.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": null, "no_cooling": null, "indoor_temp_f": null, "vulnerable_occupant": null, "active_leak": true, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (active water leak). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** I understand water is pouring out of your AC unit in the attic and dripping through the ceiling, which is urgent. Can you please tell me the ZIP code and what kind of property this is? For example, a house or condo.

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_active_leak-3", "severity": "urgent", "summary": "P1 active water leak: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['active water leak'] property=unknown area=None verified=None
**summary**: P1 urgent: active water leak. Caller says: Water is pouring out of the AC unit in the attic and dripping through the ceiling..