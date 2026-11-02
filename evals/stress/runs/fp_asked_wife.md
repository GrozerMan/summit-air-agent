# fp_asked_wife

Group: safety. Caller ID: none. Clock: Tue 2026-11-03 10:00 EST. Mode: scripted.

> The caller's own words contain 'smells like gas' inside a denial; the lexicon can't tell.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| not_P0 | **FAIL** | **FAIL** | **FAIL** | 0/3 |
| record_complete | PASS | PASS | PASS | 3/3 |

## Run 1

- ✗ **not_P0**: P0 (want P1/P2/P3/PNone)

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** I asked my wife if it smells like gas and she said no, it's just a dusty smell. The heat's working, it's 68 inside. Can I get a tune-up?

> `hazard_screen` {"heard": "I asked my wife if it smells like gas and she said no, it's just a dusty smell. The heat's working, it's 68 inside. Can I get a tune-up?", "hazard": "gas"}  
> → SAFETY EMERGENCY (gas smell reported). The dispatcher has been alerted. Read this to the caller word for word: "This could be a gas leak, so please leave the house now and take everyone with you. Don't touch light switches, appliances or phones on your way out. Once you're outside and away from the house, call nine-one-one. Don't go back in until they tell you it's safe." Then stop. Don't collect booking details, and if they want to hang up and leave, let them.

**Agent:** This could be a gas leak, so please leave the house now and take everyone with you. Don't touch light switches, appliances or phones on your way out. Once you're outside and away from the house, call nine-one-one. Don't go back in until they tell you it's safe.

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-fp_asked_wife-1", "severity": "critical", "summary": "P0 gas smell reported: unknown caller (no number)", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=0 outcome=safety_emergency reasons=['gas smell reported'] property=unknown area=None verified=None
**summary**: P0 safety emergency: gas smell reported. Caller says: I asked my wife if it smells like gas and she said no, it's just a dusty smell. The heat's working, it's 68 inside. Can I get a tune-up?.

## Run 2

- ✗ **not_P0**: P0 (want P1/P2/P3/PNone)

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** I asked my wife if it smells like gas and she said no, it's just a dusty smell. The heat's working, it's 68 inside. Can I get a tune-up?

> `hazard_screen` {"heard": "I asked my wife if it smells like gas and she said no, it's just a dusty smell. The heat's working, it's 68 inside. Can I get a tune-up?", "hazard": "gas"}  
> → SAFETY EMERGENCY (gas smell reported). The dispatcher has been alerted. Read this to the caller word for word: "This could be a gas leak, so please leave the house now and take everyone with you. Don't touch light switches, appliances or phones on your way out. Once you're outside and away from the house, call nine-one-one. Don't go back in until they tell you it's safe." Then stop. Don't collect booking details, and if they want to hang up and leave, let them.

**Agent:** This could be a gas leak, so please leave the house now and take everyone with you. Don't touch light switches, appliances or phones on your way out. Once you're outside and away from the house, call nine-one-one. Don't go back in until they tell you it's safe.

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-fp_asked_wife-2", "severity": "critical", "summary": "P0 gas smell reported: unknown caller (no number)", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=0 outcome=safety_emergency reasons=['gas smell reported'] property=unknown area=None verified=None
**summary**: P0 safety emergency: gas smell reported. Caller says: I asked my wife if it smells like gas and she said no, it's just a dusty smell. The heat's working, it's 68 inside. Can I get a tune-up?.

## Run 3

- ✗ **not_P0**: P0 (want P1/P2/P3/PNone)

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** I asked my wife if it smells like gas and she said no, it's just a dusty smell. The heat's working, it's 68 inside. Can I get a tune-up?

> `hazard_screen` {"heard": "I asked my wife if it smells like gas and she said no, it's just a dusty smell. The heat's working, it's 68 inside. Can I get a tune-up?", "hazard": "gas"}  
> → SAFETY EMERGENCY (gas smell reported). The dispatcher has been alerted. Read this to the caller word for word: "This could be a gas leak, so please leave the house now and take everyone with you. Don't touch light switches, appliances or phones on your way out. Once you're outside and away from the house, call nine-one-one. Don't go back in until they tell you it's safe." Then stop. Don't collect booking details, and if they want to hang up and leave, let them.

**Agent:** This could be a gas leak, so please leave the house now and take everyone with you. Don't touch light switches, appliances or phones on your way out. Once you're outside and away from the house, call nine-one-one. Don't go back in until they tell you it's safe.

### DB state
**appointments** (0)
**alerts** (1)
- `{"id": 1, "call_id": "stress-fp_asked_wife-3", "severity": "critical", "summary": "P0 gas smell reported: unknown caller (no number)", "acknowledged": 0}`
**callbacks** (0)
**calls row**: priority=0 outcome=safety_emergency reasons=['gas smell reported'] property=unknown area=None verified=None
**summary**: P0 safety emergency: gas smell reported. Caller says: I asked my wife if it smells like gas and she said no, it's just a dusty smell. The heat's working, it's 68 inside. Can I get a tune-up?.