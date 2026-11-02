# m_tonight_price

Group: pricing. Caller ID: none. Clock: Tue 2026-11-03 21:00 EST. Mode: scripted.

> get_pricing('come out tonight') returns only the $99 surcharge.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| mentions_129 | **FAIL** | **FAIL** | **FAIL** | 0/3 |
| only_config_prices | PASS | PASS | PASS | 3/3 |
| record_complete | PASS | PASS | PASS | 3/3 |

## Run 1

- ✗ **mentions_129**: /\$?129|one twenty-nine|hundred (and )?twenty-nine/ not said

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** How much does it cost for someone to come out tonight to look at my furnace?

**Agent:** Our office is currently closed, and we do not offer service appointments at night. May I ask your ZIP code so I can check availability for the next possible appointment?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=None outcome=abandoned reasons=[] property=unknown area=None verified=None
**summary**: 

## Run 2

- ✗ **mentions_129**: /\$?129|one twenty-nine|hundred (and )?twenty-nine/ not said

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** How much does it cost for someone to come out tonight to look at my furnace?

**Agent:** Our office is closed right now, so we don't have same-day or after-hours service available. Can I get your ZIP code to see when the earliest appointment is?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=None outcome=abandoned reasons=[] property=unknown area=None verified=None
**summary**: 

## Run 3

- ✗ **mentions_129**: /\$?129|one twenty-nine|hundred (and )?twenty-nine/ not said

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** How much does it cost for someone to come out tonight to look at my furnace?

**Agent:** Our office is currently closed, so we can't schedule anyone for tonight. Could you please tell me your ZIP code and the type of property you need service at? Then I can check if we're able to serve your area and offer appointment options.

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=None outcome=abandoned reasons=[] property=unknown area=None verified=None
**summary**: 