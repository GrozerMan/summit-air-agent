# Architecture

## Layers

| Layer | What it owns | Where |
|---|---|---|
| Telephony + media | Phone number, SIP, audio transport, noise cancellation | LiveKit Cloud |
| Conversation | STT, LLM turn-taking, interruptions, TTS, tool calling | `agent.py` (LiveKit Agents 1.8.9) |
| Business logic | Triage, eligibility, membership, scheduling, pricing, escalation, records | `summit/` (plain Python, no LLM) |
| Configuration | Prices, hours, ZIPs, thresholds, capacity | `config/business.toml` |
| Operations | Live board of calls, alerts, callbacks, bookings; Slack alerts | `dashboard/`, `summit/notify.py` |

The LLM understands and talks. It never decides priority, availability,
eligibility or price; those come back from tools as facts it must relay.

```
summit/
  config.py        loads business.toml; office hours
  models.py        Priority, Pool, Membership, Customer, Appointment
  speech.py        spoken digits -> phone/ZIP, and back again for read-backs
  triage.py        Facts -> Assessment (P0-P3 + reasons), safety scripts
  service_area.py  ZIP/town -> county, residential vs commercial
  scheduling.py    arrival windows, capacity pools, booking under a lock
  store.py         SQLite schema and queries
  backend.py       CallSession: per-call state and every guardrail
  notify.py        alerts table + optional Slack
  seed.py          demo customers
```

## A call, step by step

1. **Ring.** LiveKit's dispatch rule puts the caller in a room and the worker joins.
   `agent.py` reads caller ID (`sip.phoneNumber`), creates a `CallSession` and looks
   the number up before saying anything. A number shared by several customers
   matches nobody, so we never greet the wrong person by name.
2. **Greeting.** A fixed string through `session.say`, with no LLM round-trip, so the
   caller hears us straight away. If caller ID matched: "Am I speaking with Dana?"
   That yes is the identity check.
3. **Conversation.** The model follows `prompts/system_prompt.md`: goals and rules,
   not a script, so it can take details in whatever order the caller gives them.
   The current time and whether the office is open are appended to the prompt.
4. **Tools at checkpoints**, each a thin wrapper over a `CallSession` method that
   returns a short instruction for the model:

| Tool | Guardrail enforced in code |
|---|---|
| `lookup_customer` | Account details only after caller-ID name confirmation, or phone + last name/ZIP (+ first name for shared numbers) |
| `assess_situation` | Deterministic P0-P3. Reported hazards stay reported and priority never goes down within a call. P0 raises a critical alert and returns the script to read word for word; P1 raises an urgent alert (and pages on-call after hours) |
| `check_service_address` | ZIP/town → county; residential only; a local-looking ZIP that isn't on the list asks for the town instead of guessing |
| `find_appointment_options` | Refuses before triage, on P0, out of area, for commercial, or before the property type is known. P1 must start within 24h and may use the emergency reserve; members may use member capacity; routine work never goes same-day. No P1 capacity → dispatcher alert + urgent callback |
| `book_appointment` | Lists every missing field at once; phone and address read-backs required; ZIP must match the checked ZIP; option must have been offered on this call; the seat is re-checked inside `BEGIN IMMEDIATE` |
| `change_appointment` | Verified callers only, their own appointment only; old window released in the same transaction |
| `request_callback` | Needs a valid number; urgent ones alert the dispatcher; due time is computed from office hours |
| `transfer_to_human` | Live transfer only during office hours with a configured number, after the agent has said it's connecting them; a failed transfer becomes an urgent callback |
| `get_pricing` | Config figures only; anything repair-shaped returns "don't estimate" |
| `end_call` | LiveKit's `EndCallTool`, hidden during the greeting |

   A refusal raises `ActionRefused`, which the agent turns into a LiveKit `ToolError`
   so the model hears exactly what's missing and asks for it.

5. **During the call** every tool call (arguments, result, refused or not) and every
   new transcript line is saved, so the dashboard shows calls in progress and a
   crashed worker loses nothing.
6. **Hang-up.** The session's close event and the job's shutdown callback both run
   `finalize` (whichever comes first): the outcome, a technician summary and the
   transcript are saved, and a triaged caller who didn't get booked gets a callback.

## Data model (SQLite, `data/summit.db`)

| Table | Holds |
|---|---|
| `customers`, `memberships` | who we know and their membership status |
| `appointments` | county, day, arrival window, capacity pool, job type, priority, service address, contact name/phone, notes, status (`booked`/`moved`/`cancelled`) |
| `calls` | caller ID, priority, outcome, technician summary, the full record (facts, reasons, tool log) and transcript as JSON |
| `alerts` | critical / urgent / info, with an acknowledged flag |
| `callbacks` | number, reason, urgency, due time, open/done |

Appointments carry their own contact fields so a booking by an unverified caller
can attach to an existing customer without overwriting that customer's record. In
production this surface maps onto the field-service platform (customer → location →
job type → capacity → arrival window → notes).

## Triage rules

| Priority | Fires when | Effect |
|---|---|---|
| P0 safety | gas smell (even if "gone now"), CO alarm or symptoms, smoke/sparks/flames | No booking. Safety script (get out, then 911 / the county's gas utility). Critical alert. |
| P1 urgent | no heat + (vulnerable occupant or ≤58°F inside); no cooling + (vulnerable or ≥85°F); persistent burning smell; active leak | Urgent alert (on-call after hours); a window starting within 24h, emergency reserve allowed |
| P2 soon | no heat / no cooling otherwise; minor drip | Earliest window; asks for indoor temperature and who's home, since either can make it P1 |
| P3 routine | tune-ups, estimates, non-urgent repairs, first-use dusty smell | Any window from tomorrow |

## Capacity

Per county, per day:

- **Regular:** 2 jobs per 2-hour window, minus a seeded "already booked" load.
- **Emergency reserve:** 2 jobs a day, P1 only.
- **Member priority:** 2 jobs a day, active members only.

Options are offered earliest first, one per window, taking regular capacity before
dipping into a reserve. Only P1 work goes out on days the office is closed.

## Latency choices

- Fixed greeting (no LLM before first audio).
- `gpt-4.1-mini` with preemptive generation. Tools are local function calls with no
  webhook hop, so a tool step costs one LLM round-trip and nothing else.
- LiveKit's audio turn detector waits through "my number is 516... 555..." pauses
  without making short answers ("yes", "Thursday") feel laggy.
- `max_tool_steps=5` so lookup → triage → address → options can chain in one turn.

## Failure handling

| Failure | Behaviour |
|---|---|
| Primary LLM down or slow to start | `FallbackAdapter` switches to Gemini 2.5 Flash |
| Turn detector service unavailable | Falls back to the local `v1-mini` model |
| Caller goes silent | Check-in after 12s, another 12s later, then a polite goodbye and hang-up; a triaged, unbooked caller gets a callback |
| No urgent capacity | Dispatcher alerted; urgent callback within 30 minutes, said honestly |
| Slot taken between offer and booking | Re-checked under the DB write lock; agent apologizes and re-offers |
| Slack down | Alert is still on the dashboard; Slack is posted from a background thread so the call never waits |
| Transfer fails | Urgent callback instead, and the caller is told |
| Model ignores a rule | The backend refuses; the prompt is not the safety net |
