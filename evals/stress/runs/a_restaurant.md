# a_restaurant

Group: area. Caller ID: none. Clock: Tue 2026-11-03 10:00 EST. Mode: scripted.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| lead | PASS | **FAIL** | PASS | 2/3 |
| callback | PASS | **FAIL** | PASS | 2/3 |
| not_booked | PASS | PASS | PASS | 3/3 |
| record_complete | **FAIL** | **FAIL** | **FAIL** | 0/3 |

## Run 1

- ✗ **record_complete**: outcome=callback summary=False

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** I manage a restaurant in Garden City, 11530, and the AC in the dining room is out.

**Agent:** I want to make sure we're clear: we only service homes, not businesses. Would you like me to have the office call you back about this?

**Caller:** Sure, call me back at 516-555-0122, it's Alex Grant.

> `request_callback` {"phone": "5165550122", "reason": "restaurant AC is out", "urgent": false, "name": "Alex Grant"}  
> → Callback set: the office will call 516-555-0122 by 12 PM today, Tuesday. Tell the caller exactly that.

**Agent:** The office will call you at 516-555-0122 by noon today, Tuesday. Is there anything else I can do for you?

**Caller:** Thanks.

**Agent:** You're welcome. Have a good day!

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (1)
- `{"id": 1, "call_id": "stress-a_restaurant-1", "phone": "+15165550122", "name": "Alex Grant", "reason": "restaurant AC is out", "urgent": 0, "due_at": "2026-11-03T12:00:00-05:00", "status": "open"}`
**calls row**: priority=None outcome=callback reasons=[] property=unknown area=None verified=None
**summary**: 

## Run 2

- ✗ **lead**: outcome=info_only
- ✗ **callback**: 0 callbacks
- ✗ **record_complete**: outcome=info_only summary=False

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** I manage a restaurant in Garden City, 11530, and the AC in the dining room is out.

**Agent:** I want to make sure we're safe and prepared—have you noticed any gas smells, smoke, sparks, flames, or carbon monoxide alarms?

**Caller:** Sure, call me back at 516-555-0122, it's Alex Grant.

> `lookup_customer` {"confirmed_name": false, "phone": "5165550122", "first_name": "Alex", "last_name": "Grant", "zip_code": "11530"}  
> → No account matches those details. Carry on as a new customer and don't share anything about existing accounts.

**Agent:** Thanks, Alex. You said the AC is out in the dining room at your restaurant in Garden City, zip 11530. Did you notice any unusual smells like gas or anything else dangerous?

**Caller:** Thanks.

**Agent:** I want to be sure—did you smell gas, rotten eggs, sulfur, or anything like that, or see smoke, sparks, or flames?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=None outcome=info_only reasons=[] property=unknown area=None verified=None
**summary**: 

## Run 3

- ✗ **record_complete**: outcome=callback summary=False

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** I manage a restaurant in Garden City, 11530, and the AC in the dining room is out.

**Agent:** We only service homes for heating and cooling. Would you like me to have the office call you back about it? If so, what's the best number to reach you?

**Caller:** Sure, call me back at 516-555-0122, it's Alex Grant.

> `request_callback` {"phone": "5165550122", "reason": "AC not working in the dining room of a restaurant", "urgent": false, "name": "Alex Grant"}  
> → Callback set: the office will call 516-555-0122 by 12 PM today, Tuesday. Tell the caller exactly that.

**Agent:** The office will call you back at 516-555-0122 by noon today, Tuesday. Is there anything else I can assist with?

**Caller:** Thanks.

**Agent:** You're welcome. Have a good day.

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (1)
- `{"id": 1, "call_id": "stress-a_restaurant-3", "phone": "+15165550122", "name": "Alex Grant", "reason": "AC not working in the dining room of a restaurant", "urgent": 0, "due_at": "2026-11-03T12:00:00-05:00", "status": "open"}`
**calls row**: priority=None outcome=callback reasons=[] property=unknown area=None verified=None
**summary**: 