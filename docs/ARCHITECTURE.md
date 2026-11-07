# Architecture

## Layers

| Layer | What it owns | Where |
|---|---|---|
| Telephony + media | Phone number, SIP, audio transport, noise cancellation | LiveKit Cloud |
| Conversation | STT, LLM turn-taking, interruptions, TTS, tool calling | `agent.py` (LiveKit Agents 1.8.9) |
| Business logic | Triage, eligibility, membership, scheduling, pricing, escalation, records | `summit/` (plain Python, no LLM) |
| Configuration | Prices, hours, holidays, thresholds, capacity; every served ZIP | `config/business.toml`, `config/service_area.csv` |
| Operations | Live board of calls, alerts, callbacks, bookings; Slack alerts | `dashboard/`, `summit/notify.py` |

The LLM understands and talks. It never decides priority, availability,
eligibility or price; those come back from tools as facts it must relay.

```
summit/
  config.py        loads business.toml and the ZIP table; office hours and holidays
  models.py        Priority, Pool, Membership, Customer, Appointment, ActionRefused
  speech.py        spoken digits ("five fifty-five", corrections) -> phone/ZIP, and back
  hazard_words.py  gas / CO / fire in the caller's own words, no model involved
  triage.py        Facts -> Assessment (P0-P3 + reasons), heating season, safety scripts
  service_area.py  ZIP/town/neighborhood -> county (fuzzy for STT), residential vs commercial
  scheduling.py    arrival windows, capacity pools, booking under a lock
  pricing.py       what may be quoted, from config
  claims.py        "you're booked" / "someone will call" in the agent's words
  store.py         schema and queries; SQLite locally, Postgres when DATABASE_URL is set
  backend.py       CallSession: per-call state; scheduling, addresses, escalation
  identity.py        mixin: caller ID as a hint, verification rules
  call_triage.py     mixin: hazard screen, P0 path, priority changes
  records.py         mixin: call record, hang-up, recovery of calls a dead worker left open
  call_metrics.py  response latency and STT/LLM/TTS usage per call
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
| `lookup_customer` | Account details only after caller-ID name confirmation; if the greeting asked a name, nothing is looked up until the answer is reported. From caller ID's own number: last name or ZIP (+ first name for shared numbers). From any other number, or after a "no" to the greeting name: account phone + last name + ZIP, and a denied account stays closed. Three lookups per call. Memberships past their expiry count as lapsed |
| `assess_situation` | Deterministic P0-P3. Reported hazards stay reported and priority never goes down within a call. P0 raises a critical alert (with the caller's words and any location they gave), puts any booking from this call on hold, and returns the script to read word for word; P1 raises an urgent alert (flagged for on-call after hours). A priority change voids times already offered |
| `check_service_address` | ZIP → county from the full table (a definite yes or no); a town, neighborhood or borough is normalized and fuzzy-matched, and an unknown or ambiguous one asks for the ZIP instead of turning the caller away. Residential only (building owners of 5+ units are commercial leads); heat supplied by the building is the landlord's job (311 in NYC), no booking. A new county, ZIP, property type or building flag voids times already offered |
| `find_appointment_options` | Refuses before triage, on P0, out of area, for commercial or building-supplied heat, or before the property type is known. Asks once whether an unknown caller is already a member, and reminds the agent to get the system type and access details. P1 must start within 24h and may use the emergency reserve; P2 within 72h; members may use member capacity; routine work never goes same-day. No P1 capacity → dispatcher alert + urgent callback; no P2 capacity → dispatcher alert + callback |
| `book_appointment` | Lists every missing field at once; the agent must actually have said the phone digits and the house number and street (checked against its own transcript, not just the model's flags); ZIP must match the checked ZIP; the option must have been offered on this call for a new visit *and* still fit the call as it is now (county, residential, priority's time limit and capacity pool); the address needs a house number; the seat is re-checked under the write lock. An unverified caller gets their own customer record (provisional if the number matches an account, with a "possible match" note for the office), never someone else's. Equipment and access notes go on the ticket. The confirmation the caller hears is fixed text from the booking |
| `change_appointment` | Verified callers only, their own appointment only, an option offered for that appointment; the old appointment is checked as still booked and released in the same transaction, so two calls can't both move it |
| `cancel_appointment` | Verified callers only, their own upcoming appointment only; fixed confirmation |
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
   transcript are saved, and a triaged caller who didn't get booked gets a callback,
   whether or not they got as far as giving an address. If the agent said something
   was booked or that someone will call, and the records don't show it, the call is
   flagged: an urgent alert, an urgent callback, and a REVIEW note.

## Data model (SQLite at `data/summit.db`; Postgres via `DATABASE_URL` when deployed)

| Table | Holds |
|---|---|
| `customers`, `memberships` | who we know (`confirmed=0` for provisional records from unverified bookings) and their membership status and expiry |
| `appointments` | county, day, arrival window, capacity pool, job type, priority, service address, contact name/phone, notes, status (`booked`/`on_hold`/`moved`/`cancelled`) |
| `calls` | caller ID, priority, outcome, technician summary, the full record (facts, reasons, tool log, latency and usage) and transcript as JSON |
| `alerts` | critical / urgent / info, with an acknowledged flag |
| `callbacks` | number, reason, urgency, due time, open/done |

Appointments carry their own contact fields, and an unverified caller's booking gets
its own customer record, so nobody's account shows or lets them move a stranger's visit. In
production this surface maps onto the field-service platform (customer → location →
job type → capacity → arrival window → notes).

## Triage rules

| Priority | Fires when | Effect |
|---|---|---|
| P0 safety | gas smell (even if "gone now"), CO alarm or symptoms, smoke/sparks/flames, from the model's report or the caller's own words | No booking; a booking made earlier on the call goes on hold. Safety script (get out, then 911 and the county's gas utility, or "your gas company"). Critical alert. |
| P1 urgent | no heat during the heating season (Oct 1 to May 31) unless it's ≥65°F inside; no heat + (vulnerable occupant or ≤58°F inside); no cooling + (vulnerable or ≥85°F); persistent burning smell; active leak | Urgent alert (flagged for on-call after hours); a window starting within 24h, emergency reserve allowed |
| P2 soon | no heat / no cooling otherwise; minor drip | A window starting within 72h; asks for indoor temperature and who's home, since either can make it P1 |
| P3 routine | tune-ups, estimates, non-urgent repairs, first-use dusty smell | Any window from tomorrow, never on a holiday |

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
| Worker killed mid-call | The record is saved as the call goes; the next call to start closes it, and a triaged caller who wasn't booked gets their callback |
| Model ignores a rule | For identity, priority, eligibility, scheduling, booking, read-backs and the booking confirmation, the backend refuses or speaks fixed text. Tone and how the model words a transfer request are still prompt-only |

## Deployment

The agent runs on LiveKit Cloud from the repo's `Dockerfile` (`lk agent create`, then
`lk agent deploy`). The container's disk doesn't survive a restart, so the deployed
agent's records live in Postgres (`DATABASE_URL`, e.g. Neon in us-east); bookings
serialize on a transaction-scoped advisory lock, the Postgres counterpart of SQLite's
`BEGIN IMMEDIATE`. `SUMMIT_TEST_POSTGRES=1 uv run pytest` runs the whole suite on a
throwaway Postgres. The dashboard runs anywhere with the same `DATABASE_URL`. A laptop
worker sets `AGENT_NAME=summit-air-dev` so it can't take calls meant for the deploy.
