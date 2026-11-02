# f_llm_fallback

Group: records. Caller ID: none. Clock: Tue 2026-11-03 10:00 EST. Mode: scripted.

> Primary model replaced by a non-existent one; FallbackAdapter should use Gemini.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| answered | PASS | PASS | PASS | 3/3 |
| P2 | PASS | PASS | PASS | 3/3 |
| record_complete | PASS | PASS | PASS | 3/3 |

## Run 1


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** My heat stopped working. It's 64 inside and nobody vulnerable.

> `assess_situation` {"description": "My heat stopped working. It's 64 inside and nobody vulnerable.", "gas_smell": false, "co_alarm_or_symptoms": false, "smoke_sparks_or_flames": false, "burning_smell_persistent": false, "dusty_smell_first_use": false, "no_heat": true, "no_cooling": false, "indoor_temp_f": 64, "vulnerable_occupant": false, "active_leak": false, "minor_drip": false, "request_type": null}  
> → Priority is P2 soon (no heat). Next, check the service address.

**Agent:** I'm sorry to hear your heat is out. What is the ZIP code and the type of property you're at?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=2 outcome=info_only reasons=['no heat'] property=unknown area=None verified=None
**summary**: P2 soon: no heat. Caller says: My heat stopped working. It's 64 inside and nobody vulnerable.. 64°F inside.

## Run 2


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** My heat stopped working. It's 64 inside and nobody vulnerable.

> `assess_situation` {"description": "My heat stopped working.", "gas_smell": false, "co_alarm_or_symptoms": false, "smoke_sparks_or_flames": false, "burning_smell_persistent": false, "dusty_smell_first_use": false, "no_heat": true, "no_cooling": false, "indoor_temp_f": 64, "vulnerable_occupant": false, "active_leak": false, "minor_drip": false, "request_type": null}  
> → Priority is P2 soon (no heat). Next, check the service address.

**Agent:** I'm sorry to hear your heat is out. What is the ZIP code and the type of property where the work is needed?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=2 outcome=info_only reasons=['no heat'] property=unknown area=None verified=None
**summary**: P2 soon: no heat. Caller says: My heat stopped working.. 64°F inside.

## Run 3


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** My heat stopped working. It's 64 inside and nobody vulnerable.

> `assess_situation` {"description": "My heat stopped working. It's 64 inside and nobody vulnerable.", "gas_smell": false, "co_alarm_or_symptoms": false, "smoke_sparks_or_flames": false, "burning_smell_persistent": false, "dusty_smell_first_use": false, "no_heat": true, "no_cooling": false, "indoor_temp_f": 64, "vulnerable_occupant": false, "active_leak": false, "minor_drip": false, "request_type": null}  
> → Priority is P2 soon (no heat). Next, check the service address.

**Agent:** I'm sorry your heat is out. What is the ZIP code for the property?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=2 outcome=info_only reasons=['no heat'] property=unknown area=None verified=None
**summary**: P2 soon: no heat. Caller says: My heat stopped working. It's 64 inside and nobody vulnerable.. 64°F inside.