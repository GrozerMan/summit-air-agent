# t_15_outside

Group: triage. Caller ID: none. Clock: Tue 2026-11-03 10:00 EST. Mode: scripted.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| P2_until_indoor_known | **FAIL** | **FAIL** | **FAIL** | 0/3 |
| asks_indoor | PASS | PASS | **FAIL** | 2/3 |
| record_complete | PASS | PASS | PASS | 3/3 |

## Run 1

- ✗ **P2_until_indoor_known**: PNone (want P2)

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** My heat's out and it's 15 degrees outside. Nobody vulnerable here.

**Agent:** Thank you for letting me know. Can you tell me what the temperature is inside right now?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=None outcome=abandoned reasons=[] property=unknown area=None verified=None
**summary**: 

## Run 2

- ✗ **P2_until_indoor_known**: PNone (want P2)

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** My heat's out and it's 15 degrees outside. Nobody vulnerable here.

**Agent:** Can you tell me what your indoor temperature is right now? Also, are you smelling anything unusual like gas or burning?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=None outcome=abandoned reasons=[] property=unknown area=None verified=None
**summary**: 

## Run 3

- ✗ **P2_until_indoor_known**: PNone (want P2)
- ✗ **asks_indoor**: /inside|indoor/ not said

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** My heat's out and it's 15 degrees outside. Nobody vulnerable here.

**Agent:** I hear your heat is out. Could you tell me the ZIP code and what kind of home it is? Also, what's your address and the best phone number to reach you?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=None outcome=abandoned reasons=[] property=unknown area=None verified=None
**summary**: 