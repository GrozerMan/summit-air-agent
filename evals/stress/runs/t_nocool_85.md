# t_nocool_85

Group: triage. Caller ID: none. Clock: Tue 2026-11-03 10:00 EST. Mode: scripted.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| P1 | PASS | PASS | PASS | 3/3 |
| record_complete | PASS | PASS | PASS | 3/3 |

## Run 1


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** My AC died. It's 85 inside. Nobody vulnerable, just me.

> `assess_situation` {"description": "My AC died. It's 85 inside.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": null, "no_cooling": true, "indoor_temp_f": 85, "vulnerable_occupant": false, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no cooling, 85°F inside). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** I'm sorry to hear about your AC. May I have the ZIP code and property type (like house or condo) where you need service?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_nocool_85-1", "severity": "urgent", "summary": "P1 no cooling, 85\u00b0F inside: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no cooling, 85°F inside'] property=unknown area=None verified=None
**summary**: P1 urgent: no cooling, 85°F inside. Caller says: My AC died. It's 85 inside.. 85°F inside.

## Run 2


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** My AC died. It's 85 inside. Nobody vulnerable, just me.

> `assess_situation` {"description": "My AC died. It's 85 inside.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": null, "no_cooling": true, "indoor_temp_f": 85, "vulnerable_occupant": false, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no cooling, 85°F inside). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** I understand your AC is not working and it's 85 degrees inside. May I have the ZIP code and type of property you need service at?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_nocool_85-2", "severity": "urgent", "summary": "P1 no cooling, 85\u00b0F inside: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no cooling, 85°F inside'] property=unknown area=None verified=None
**summary**: P1 urgent: no cooling, 85°F inside. Caller says: My AC died. It's 85 inside.. 85°F inside.

## Run 3


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** My AC died. It's 85 inside. Nobody vulnerable, just me.

> `assess_situation` {"description": "My AC died. It's 85 inside. Nobody vulnerable, just me.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": null, "no_cooling": true, "indoor_temp_f": 85, "vulnerable_occupant": false, "active_leak": null, "minor_drip": null, "request_type": null}  
> → Priority is now P1 urgent (no cooling, 85°F inside). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** I'm sorry to hear that your AC went out and it's 85 degrees in your home. May I have the ZIP code and type of property where our technician would be coming to?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-t_nocool_85-3", "severity": "urgent", "summary": "P1 no cooling, 85\u00b0F inside: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['no cooling, 85°F inside'] property=unknown area=None verified=None
**summary**: P1 urgent: no cooling, 85°F inside. Caller says: My AC died. It's 85 inside. Nobody vulnerable, just me.. 85°F inside.