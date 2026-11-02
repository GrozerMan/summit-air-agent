# b_human_after_hours

Group: robustness. Caller ID: none. Clock: Tue 2026-11-03 21:00 EST. Mode: scripted.

| check | run 1 | run 2 | run 3 | pass rate |
|---|---|---|---|---|
| no_fake_transfer | PASS | PASS | PASS | 3/3 |
| callback | PASS | PASS | **FAIL** | 2/3 |
| record_complete | **FAIL** | **FAIL** | PASS | 1/3 |

## Run 1

- ✗ **record_complete**: outcome=callback summary=False

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Can I talk to someone real?

> `transfer_to_human` {"reason": "Caller requested to speak with a person"}  
> → There's no live transfer line. Tell the caller you can't put them through right now and offer a callback from the office.

**Agent:** Sure, I'll connect you to a person. One moment please. I'm sorry, we can't put you through to a person right now. Would you like the office to call you back? If so, please provide your name and phone number.

**Caller:** Fine, have someone call me. 516-555-0123, it's Lee.

> `request_callback` {"phone": "5165550123", "reason": "Caller requested to speak with a person", "urgent": false, "name": "Lee"}  
> → Callback set: the office will call 516-555-0123 by 7 AM tomorrow, Wednesday. Tell the caller exactly that.

**Agent:** The office will call you at 516-555-0123 by 7 in the morning tomorrow, Wednesday. Is there anything else I can help you with?

**Caller:** Yes.

**Agent:** Please tell me what you need help with.

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (1)
- `{"id": 1, "call_id": "stress-b_human_after_hours-1", "phone": "+15165550123", "name": "Lee", "reason": "Caller requested to speak with a person", "urgent": 0, "due_at": "2026-11-04T07:00:00-05:00", "status": "open"}`
**calls row**: priority=None outcome=callback reasons=[] property=unknown area=None verified=None
**summary**: 

## Run 2

- ✗ **record_complete**: outcome=callback summary=False

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Can I talk to someone real?

**Agent:** I’m the automated assistant. If you want to speak to a person, I can see if one is available to call you back. What’s the reason?

**Caller:** Fine, have someone call me. 516-555-0123, it's Lee.

> `request_callback` {"phone": "516-555-0123", "reason": "Caller requested to speak to a person", "urgent": false, "name": "Lee"}  
> → Callback set: the office will call 516-555-0123 by 7 AM tomorrow, Wednesday. Tell the caller exactly that.

**Agent:** Someone will call you at 516-555-0123 by 7 AM tomorrow, Wednesday. Is there anything else?

**Caller:** Yes.

**Agent:** What else can I help you with?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (1)
- `{"id": 1, "call_id": "stress-b_human_after_hours-2", "phone": "+15165550123", "name": "Lee", "reason": "Caller requested to speak to a person", "urgent": 0, "due_at": "2026-11-04T07:00:00-05:00", "status": "open"}`
**calls row**: priority=None outcome=callback reasons=[] property=unknown area=None verified=None
**summary**: 

## Run 3

- ✗ **callback**: 0 callbacks

**Agent:** Thanks for calling Summit Air, you've reached our automated assistant. How can I help?

**Caller:** Can I talk to someone real?

**Agent:** I'm the automated assistant here to help you as best as I can. If you want to talk to a person, I can connect you. What do you need help with?

**Caller:** Fine, have someone call me. 516-555-0123, it's Lee.

**Agent:** Thank you, Lee. Can you please tell me briefly what the callback is about?

**Caller:** Yes.

**Agent:** I need to know what your problem or request is to pass it along for the callback. What should I say?

### DB state
**appointments** (0)
**alerts** (0)
**callbacks** (0)
**calls row**: priority=None outcome=abandoned reasons=[] property=unknown area=None verified=None
**summary**: 