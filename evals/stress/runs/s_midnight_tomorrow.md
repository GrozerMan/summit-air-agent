# s_midnight_tomorrow

Group: scheduling. Caller ID: none. Clock: Mon 2026-11-02 23:55 EST. Mode: scripted.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| says_tuesday | **FAIL** | **FAIL** | **FAIL** | 0/3 |
| no_same_day_P3 | PASS | PASS | PASS | 3/3 |
| record_complete | PASS | PASS | PASS | 3/3 |

## Run 1

- ✗ **says_tuesday**: /tuesday/ not said

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Hi, can you come tomorrow for a furnace tune-up? Bay Shore, 11706, a house.

**Agent:** I can help with that. First, may I have your name, please?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=None outcome=abandoned reasons=[] property=unknown area=None verified=None
**summary**: 

## Run 2

- ✗ **says_tuesday**: /tuesday/ not said

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Hi, can you come tomorrow for a furnace tune-up? Bay Shore, 11706, a house.

**Agent:** I can check availability for a furnace tune-up tomorrow in Bay Shore, 11706. May I have your first and last name, please?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=None outcome=abandoned reasons=[] property=unknown area=None verified=None
**summary**: 

## Run 3

- ✗ **says_tuesday**: /tuesday/ not said

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Hi, can you come tomorrow for a furnace tune-up? Bay Shore, 11706, a house.

**Agent:** Can you please tell me your first and last name for the appointment?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=None outcome=abandoned reasons=[] property=unknown area=None verified=None
**summary**: 