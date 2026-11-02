# t_burning_persistent

Group: triage. Caller ID: none. Clock: Tue 2026-11-03 10:00 EST. Mode: scripted.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| P1 | PASS | PASS | PASS | 3/3 |
| record_complete | PASS | PASS | PASS | 3/3 |

## Run 1


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** There's a burning smell from the furnace that's been going for two days. It's not dusty, it's like hot electrical.

> `assess_situation` {"description": "There's a burning smell from the furnace that's been going for two days. It's not dusty, it's like hot electrical.", "gas_smell": false, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": false, "burning_smell_persistent": true, "dusty_smell_first_use": false, "no_heat": null, "no_cooling": null, "indoor_temp_f": null, "vulnerable_occupant": null, "active_leak": null, "minor_  
> → Priority is now P1 urgent (persistent burning smell). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** Thank you for sharing that. I need to check the service address to see if we cover your area. Could you tell me your ZIP code and what kind of property this is (like a house or condo)?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_burning_persistent-1", "severity": "urgent", "summary": "P1 persistent burning smell: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['persistent burning smell'] property=unknown area=None verified=None
**summary**: P1 urgent: persistent burning smell. Caller says: There's a burning smell from the furnace that's been going for two days. It's not dusty, it's like hot electrical..

## Run 2


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** There's a burning smell from the furnace that's been going for two days. It's not dusty, it's like hot electrical.

> `assess_situation` {"description": "burning smell from the furnace that's been going for two days, like hot electrical", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": true, "dusty_smell_first_use": false, "no_heat": null, "no_cooling": null, "indoor_temp_f": null, "vulnerable_occupant": null, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (persistent burning smell). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** Your burning smell sounds urgent and we want to get it looked at as soon as possible, within 24 hours. What is the address where the furnace is? Please include your ZIP code and what kind of property it is.

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_burning_persistent-2", "severity": "urgent", "summary": "P1 persistent burning smell: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['persistent burning smell'] property=unknown area=None verified=None
**summary**: P1 urgent: persistent burning smell. Caller says: burning smell from the furnace that's been going for two days, like hot electrical.

## Run 3


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** There's a burning smell from the furnace that's been going for two days. It's not dusty, it's like hot electrical.

> `assess_situation` {"description": "There's a burning smell from the furnace that's been going for two days. It's not dusty, it's like hot electrical.", "gas_smell": false, "co_alarm_or_symptoms": false, "smoke_sparks_or_flames": false, "burning_smell_persistent": true, "dusty_smell_first_use": false, "no_heat": null, "no_cooling": null, "indoor_temp_f": null, "vulnerable_occupant": null, "active_leak": null, "minor  
> → Priority is now P1 urgent (persistent burning smell). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** A persistent burning smell like that is urgent for your safety. Can you please tell me the ZIP code and what kind of property it is—like a house or condo?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_burning_persistent-3", "severity": "urgent", "summary": "P1 persistent burning smell: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['persistent burning smell'] property=unknown area=None verified=None
**summary**: P1 urgent: persistent burning smell. Caller says: There's a burning smell from the furnace that's been going for two days. It's not dusty, it's like hot electrical..