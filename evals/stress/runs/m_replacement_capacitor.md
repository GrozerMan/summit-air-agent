# m_replacement_capacitor

Group: pricing. Caller ID: none. Clock: Tue 2026-11-03 10:00 EST. Mode: scripted.

> get_pricing returns 'Replacement estimates are free.' for this wording.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| no_price_or_free | PASS | PASS | PASS | 3/3 |
| not_free | PASS | PASS | **FAIL** | 2/3 |
| record_complete | **FAIL** | PASS | **FAIL** | 1/3 |

## Run 1

- ✗ **record_complete**: outcome=info_only summary=False

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** How much is a replacement capacitor?

> `get_pricing` {"item": "replacement capacitor"}  
> → Replacement estimates are free.

**Agent:** I can check the pricing for a replacement capacitor for you. One moment please. We don't charge to estimate a replacement capacitor. If you'd like, I can help set up a visit for an estimate. Would you want to book that?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=None outcome=info_only reasons=[] property=unknown area=None verified=None
**summary**: 

## Run 2


**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** How much is a replacement capacitor?

**Agent:** I can look up the price for a replacement capacitor. Could you please tell me what type of equipment or system it's for?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=None outcome=abandoned reasons=[] property=unknown area=None verified=None
**summary**: 

## Run 3

- ✗ **not_free**: said 'free'
- ✗ **record_complete**: outcome=info_only summary=False

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** How much is a replacement capacitor?

> `get_pricing` {"item": "replacement capacitor"}  
> → Replacement estimates are free.

**Agent:** Let me check the price for a replacement capacitor for you. One moment, please. A replacement estimate for a capacitor is free. Would you like me to schedule a technician to come out and provide an estimate for the replacement?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=None outcome=info_only reasons=[] property=unknown area=None verified=None
**summary**: 