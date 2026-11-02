# fp_dusty_filter

Group: safety. Caller ID: none. Clock: Tue 2026-11-03 10:00 EST. Mode: scripted.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| not_P0 | PASS | PASS | PASS | 3/3 |
| no_critical | PASS | PASS | PASS | 3/3 |
| record_complete | PASS | PASS | PASS | 3/3 |

## Run 1


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** I just put in a new filter and it smells kind of dusty when the heat runs. Is that normal? Maybe I should get a tune-up.

> `assess_situation` {"description": "I just put in a new filter and it smells kind of dusty when the heat runs.", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": true, "no_heat": null, "no_cooling": null, "indoor_temp_f": null, "vulnerable_occupant": null, "active_leak": null, "minor_drip": null, "request_type": "tune_up"}  
> → Priority is P3 routine (dusty smell on first use of the season, normal). Next, check the service address.

**Agent:** A dusty smell when the heat runs the first time is normal. Would you like me to check if we can schedule a tune-up at your home? If yes, can you tell me your ZIP code and what kind of property it is?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=3 outcome=info_only reasons=['dusty smell on first use of the season, normal'] property=unknown area=None verified=None
**summary**: P3 routine: dusty smell on first use of the season, normal. Caller says: I just put in a new filter and it smells kind of dusty when the heat runs..

## Run 2


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** I just put in a new filter and it smells kind of dusty when the heat runs. Is that normal? Maybe I should get a tune-up.

> `assess_situation` {"description": "It smells kind of dusty when the heat runs after putting in a new filter", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": true, "no_heat": null, "no_cooling": null, "indoor_temp_f": null, "vulnerable_occupant": null, "active_leak": null, "minor_drip": null, "request_type": "tune_up"}  
> → Priority is P3 routine (dusty smell on first use of the season, normal). Next, check the service address.

**Agent:** A dusty smell when the heat runs the first time this season is normal. Should I check if we serve your address for a tune-up? What type of property do you have?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=3 outcome=info_only reasons=['dusty smell on first use of the season, normal'] property=unknown area=None verified=None
**summary**: P3 routine: dusty smell on first use of the season, normal. Caller says: It smells kind of dusty when the heat runs after putting in a new filter.

## Run 3


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** I just put in a new filter and it smells kind of dusty when the heat runs. Is that normal? Maybe I should get a tune-up.

> `assess_situation` {"description": "new filter, smells kind of dusty when the heat runs", "gas_smell": null, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": true, "no_heat": null, "no_cooling": null, "indoor_temp_f": null, "vulnerable_occupant": null, "active_leak": null, "minor_drip": null, "request_type": "tune_up"}  
> → Priority is P3 routine (dusty smell on first use of the season, normal). Next, check the service address.

**Agent:** A dusty smell with a new filter on the first heat run can be normal. What kind of property is the service address? Could you give me the ZIP code too?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=3 outcome=info_only reasons=['dusty smell on first use of the season, normal'] property=unknown area=None verified=None
**summary**: P3 routine: dusty smell on first use of the season, normal. Caller says: new filter, smells kind of dusty when the heat runs.