# b_human_office_hours

Group: robustness. Caller ID: none. Clock: Tue 2026-11-03 10:00 EST. Mode: scripted.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| no_fake_transfer | PASS | PASS | PASS | 3/3 |
| callback | PASS | PASS | **FAIL** | 2/3 |
| record_complete | **FAIL** | **FAIL** | **FAIL** | 0/3 |

## Run 1

- ✗ **record_complete**: outcome=callback summary=False

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** I'd like to speak to a person, please.

> `transfer_to_human` {"reason": "Caller wants to speak to a person"}  
> → There's no live transfer line. Tell the caller you can't put them through right now and offer a callback from the office.

**Agent:** I'm not able to transfer you to a person right now, but I can arrange for the office to call you back. Can I get the best phone number to reach you?

**Caller:** Okay, a callback is fine. 516-555-0123, my name is Lee.

> `request_callback` {"phone": "516-555-0123", "reason": "Caller wants to speak to a person", "urgent": false, "name": "Lee"}  
> → Callback set: the office will call 516-555-0123 by 12 PM today, Tuesday. Tell the caller exactly that.

**Agent:** The office will call you back at 516-555-0123 by 12 PM today, Tuesday. Is there anything else I can help you with?

**Caller:** Yes, that's right.

**Agent:** Thanks for confirming. If you think of anything else, just call us back. Have a good day.

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (1)
- `{"id": 1, "call_id": "stress-b_human_office_hours-1", "phone": "+15165550123", "name": "Lee", "reason": "Caller wants to speak to a person", "urgent": 0, "due_at": "2026-11-03T12:00:00-05:00", "status": "open"}`
**calls row**: priority=None outcome=callback reasons=[] property=unknown area=None verified=None
**summary**: 

## Run 2

- ✗ **record_complete**: outcome=callback summary=False

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** I'd like to speak to a person, please.

> `transfer_to_human` {"reason": "Caller requested to speak to a person"}  
> → There's no live transfer line. Tell the caller you can't put them through right now and offer a callback from the office.

**Agent:** I can't put you through to a person right now, but I can have the office call you back. Can I get your phone number to arrange that?

**Caller:** Okay, a callback is fine. 516-555-0123, my name is Lee.

> `request_callback` {"phone": "5165550123", "reason": "Caller requested to speak to a person", "urgent": false, "name": "Lee"}  
> → Callback set: the office will call 516-555-0123 by 12 PM today, Tuesday. Tell the caller exactly that.

**Agent:** The office will call you back today by 12 PM, Tuesday, at 516-555-0123. Is there anything else I can help you with?

**Caller:** Yes, that's right.

**Agent:** Thanks, Lee. If you need anything else, just call us back. Have a good day.

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (1)
- `{"id": 1, "call_id": "stress-b_human_office_hours-2", "phone": "+15165550123", "name": "Lee", "reason": "Caller requested to speak to a person", "urgent": 0, "due_at": "2026-11-03T12:00:00-05:00", "status": "open"}`
**calls row**: priority=None outcome=callback reasons=[] property=unknown area=None verified=None
**summary**: 

## Run 3

- ✗ **callback**: 0 callbacks
- ✗ **record_complete**: outcome=info_only summary=False

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** I'd like to speak to a person, please.

> `transfer_to_human` {"reason": "Caller requested to speak to a person"}  
> → There's no live transfer line. Tell the caller you can't put them through right now and offer a callback from the office.

**Agent:** I don't have a live transfer line to a person right now. Would you like the office to call you back? If so, please tell me the best phone number to reach you and what it's about.

**Caller:** Okay, a callback is fine. 516-555-0123, my name is Lee.

**Agent:** Thank you, Lee. What is the callback regarding so I can share that with the office?

**Caller:** Yes, that's right.

**Agent:** Could you please tell me what the callback is regarding?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=None outcome=info_only reasons=[] property=unknown area=None verified=None
**summary**: 