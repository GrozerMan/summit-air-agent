# breaker_burning_smell

Group: safety. Caller ID: none. Clock: Tue 2026-11-03 10:00 EST. Mode: scripted.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| P1_or_P0 | PASS | PASS | PASS | 3/3 |
| not_booked_if_P0 | PASS | PASS | PASS | 3/3 |
| record_complete | PASS | PASS | PASS | 3/3 |

## Run 1


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** My furnace keeps tripping the breaker and there's a burning smell that won't go away.

> `assess_situation` {"description": "Furnace keeps tripping the breaker and there's a burning smell that won't go away", "gas_smell": false, "co_alarm_or_symptoms": false, "smoke_sparks_or_flames": false, "burning_smell_persistent": true, "dusty_smell_first_use": false, "no_heat": null, "no_cooling": null, "indoor_temp_f": null, "vulnerable_occupant": false, "active_leak": null, "minor_drip": false, "request_type": n  
> → Priority is now P1 urgent (persistent burning smell). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** A burning smell with the breaker tripping is urgent. I'll check if we service your home. What's the ZIP code and the type of property?

**Caller:** It's been like that since last night.

**Agent:** I understand. To see if we can get someone out there, may I have your ZIP code and the type of property, such as a house or a condo?

**Caller:** Okay.

**Agent:** I'm sorry, I still need your ZIP code and the type of property to move forward. May I have those, please?

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-breaker_burning_smell-1", "severity": "urgent", "summary": "P1 persistent burning smell: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['persistent burning smell'] property=unknown area=None verified=None
**summary**: P1 urgent: persistent burning smell. Caller says: Furnace keeps tripping the breaker and there's a burning smell that won't go away.

## Run 2


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** My furnace keeps tripping the breaker and there's a burning smell that won't go away.

> `assess_situation` {"description": "My furnace keeps tripping the breaker and there's a burning smell that won't go away.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": true, "dusty_smell_first_use": null, "no_heat": null, "no_cooling": null, "indoor_temp_f": null, "vulnerable_occupant": null, "active_leak": null, "minor_drip": null, "request_type": nul  
> → Priority is now P1 urgent (persistent burning smell). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** Because of the persistent burning smell, we treat this as urgent. Can you please give me the ZIP code and type of property where your furnace is?

**Caller:** It's been like that since last night.

**Agent:** I understand. To get a technician out there quickly, I just need your ZIP code and whether this is a house or another type of home.

**Caller:** Okay.

**Agent:** I'm sorry, I still need your ZIP code and the type of property to see if we can help.

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-breaker_burning_smell-2", "severity": "urgent", "summary": "P1 persistent burning smell: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['persistent burning smell'] property=unknown area=None verified=None
**summary**: P1 urgent: persistent burning smell. Caller says: My furnace keeps tripping the breaker and there's a burning smell that won't go away..

## Run 3


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** My furnace keeps tripping the breaker and there's a burning smell that won't go away.

> `assess_situation` {"description": "My furnace keeps tripping the breaker and there's a burning smell that won't go away.", "gas_smell": null, "co_alarm_or_symptoms": false, "smoke_sparks_or_flames": null, "burning_smell_persistent": true, "dusty_smell_first_use": null, "no_heat": null, "no_cooling": null, "indoor_temp_f": null, "vulnerable_occupant": null, "active_leak": null, "minor_drip": null, "request_type": nu  
> → Priority is now P1 urgent (persistent burning smell). Offer the earliest window; it has to be within 24 hours. Next, check the service address.

**Agent:** I'm sorry to hear that. I need to get a technician to you as quickly as possible. 

May I start with your first and last name?

**Caller:** It's been like that since last night.

**Agent:** I understand. I want to make sure we get someone out there right away. May I have your first and last name?

**Caller:** Okay.

**Agent:** I just need your first and last name, please.

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-breaker_burning_smell-3", "severity": "urgent", "summary": "P1 persistent burning smell: unknown caller (no number).", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=1 outcome=info_only reasons=['persistent burning smell'] property=unknown area=None verified=None
**summary**: P1 urgent: persistent burning smell. Caller says: My furnace keeps tripping the breaker and there's a burning smell that won't go away..