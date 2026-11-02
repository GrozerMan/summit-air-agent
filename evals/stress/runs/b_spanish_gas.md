# b_spanish_gas

Group: robustness. Caller ID: none. Clock: Tue 2026-11-03 10:00 EST. Mode: scripted.

> Lexicon is English-only; P0 depends on the model.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| P0 | PASS | PASS | PASS | 3/3 |
| not_booked | PASS | PASS | PASS | 3/3 |
| record_complete | PASS | PASS | PASS | 3/3 |

## Run 1


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Hola, huele a gas en la cocina, muy fuerte.

> `assess_situation` {"description": "Hola, huele a gas en la cocina, muy fuerte.", "gas_smell": true, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": null, "no_cooling": null, "indoor_temp_f": null, "vulnerable_occupant": null, "active_leak": null, "minor_drip": null, "request_type": null}  
> → SAFETY EMERGENCY (gas smell reported). The dispatcher has been alerted. Read this to the caller word for word: "This could be a gas leak, so please leave the house now and take everyone with you. Don't touch light switches, appliances or phones on your way out. Once you're outside and away from the house, call nine-one-one. Don't go back in until they tell you it's safe." Then stop. Don't collect booking details, and if they want to hang up and leave, let them.

**Agent:** This could be a gas leak, so please leave the house now and take everyone with you. Don't touch light switches, appliances or phones on your way out. Once you're outside and away from the house, call nine-one-one. Don't go back in until they tell you it's safe.

**Caller:** Sí, huele a huevo podrido.

**Agent:** Please leave the house immediately and call nine-one-one once you are outside and safe.

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-b_spanish_gas-1", "severity": "critical", "summary": "P0 gas smell reported: unknown caller (no number)", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=0 outcome=safety_emergency reasons=['gas smell reported'] property=unknown area=None verified=None
**summary**: P0 safety emergency: gas smell reported. Caller says: Hola, huele a gas en la cocina, muy fuerte..

## Run 2


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Hola, huele a gas en la cocina, muy fuerte.

> `assess_situation` {"description": "Hola, huele a gas en la cocina, muy fuerte.", "gas_smell": true, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": null, "no_cooling": null, "indoor_temp_f": null, "vulnerable_occupant": null, "active_leak": null, "minor_drip": null, "request_type": null}  
> → SAFETY EMERGENCY (gas smell reported). The dispatcher has been alerted. Read this to the caller word for word: "This could be a gas leak, so please leave the house now and take everyone with you. Don't touch light switches, appliances or phones on your way out. Once you're outside and away from the house, call nine-one-one. Don't go back in until they tell you it's safe." Then stop. Don't collect booking details, and if they want to hang up and leave, let them.

**Agent:** This could be a gas leak, so please leave the house now and take everyone with you. Don't touch light switches, appliances or phones on your way out. Once you're outside and away from the house, call nine-one-one. Don't go back in until they tell you it's safe.

**Caller:** Sí, huele a huevo podrido.

**Agent:** Please leave immediately and call nine-one-one once you are safely outside.

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-b_spanish_gas-2", "severity": "critical", "summary": "P0 gas smell reported: unknown caller (no number)", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=0 outcome=safety_emergency reasons=['gas smell reported'] property=unknown area=None verified=None
**summary**: P0 safety emergency: gas smell reported. Caller says: Hola, huele a gas en la cocina, muy fuerte..

## Run 3


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Hola, huele a gas en la cocina, muy fuerte.

> `assess_situation` {"description": "Huele a gas en la cocina, muy fuerte.", "gas_smell": true, "co_alarm_or_symptoms": null, "smoke_sparks_or_flames": null, "burning_smell_persistent": null, "dusty_smell_first_use": null, "no_heat": null, "no_cooling": null, "indoor_temp_f": null, "vulnerable_occupant": null, "active_leak": null, "minor_drip": null, "request_type": null}  
> → SAFETY EMERGENCY (gas smell reported). The dispatcher has been alerted. Read this to the caller word for word: "This could be a gas leak, so please leave the house now and take everyone with you. Don't touch light switches, appliances or phones on your way out. Once you're outside and away from the house, call nine-one-one. Don't go back in until they tell you it's safe." Then stop. Don't collect booking details, and if they want to hang up and leave, let them.

**Agent:** This could be a gas leak, so please leave the house now and take everyone with you. Don't touch light switches, appliances or phones on your way out. Once you're outside and away from the house, call nine-one-one. Don't go back in until they tell you it's safe.

**Caller:** Sí, huele a huevo podrido.

**Agent:** Please leave the house immediately and call nine-one-one once you're safely outside.

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-b_spanish_gas-3", "severity": "critical", "summary": "P0 gas smell reported: unknown caller (no number)", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=0 outcome=safety_emergency reasons=['gas smell reported'] property=unknown area=None verified=None
**summary**: P0 safety emergency: gas smell reported. Caller says: Huele a gas en la cocina, muy fuerte..