# Decisions and trade-offs

## 1. LiveKit Agents, not Vapi/Retell, and not a hand-built pipeline
**Chose:** LiveKit Agents (open source, Python) on LiveKit Cloud, with a LiveKit phone number and LiveKit Inference for STT/LLM/TTS.
**Why:** the agent lives in our repo, so every behaviour is a code change we can test and debug live, and tools are in-process function calls rather than webhooks to a server we'd also have to host. One vendor account covers the phone number, models, turn detection and noise cancellation, which keeps a demo's moving parts to one. LiveKit ships a text-mode test harness, which made a real eval suite cheap.
**Gave up:** Vapi/Retell get to a first live call faster and include a no-code dashboard. A hand-built Twilio Media Streams pipeline gives total control but would spend the week on barge-in and endpointing instead of Summit Air's problems.
**Twilio:** not required. LiveKit sells numbers directly; an existing Twilio number can be pointed at LiveKit via SIP trunk with no code change.

## 2. The LLM never decides urgency, eligibility, availability or price
The model extracts facts (`gas_smell`, `no_heat`, `indoor_temp_f`, `vulnerable_occupant`...) and `summit/triage.py` applies ordered rules. Same facts, same answer, every time; each call records which rules fired, so the owner can read *why* a call was P1. Thresholds are config.
The same pattern holds for booking: the backend refuses rather than trusting the prompt. Prompt rules are for tone; code rules are for anything that costs money or safety.

## 3. Safety is conservative and short
Gas, CO and smoke/fire are P0 regardless of anything else, including "the smell went away": once a hazard is reported on a call, a later "no" doesn't clear it. The script is fixed text (get out, don't touch switches or phones inside, call nine-one-one or the county's gas utility from outside), taken from National Grid and Con Edison's own guidance. The agent doesn't collect booking details first, and lets a caller who is still inside hang up. Priority never goes down within a call, so a calmer second description can't undo a gas report.

## 4. Identity before account details
Caller ID alone is not proof (shared phones, spouses, spoofing). The greeting asks "Am I speaking with Dana?"; membership, address and history are only disclosed after that, or after phone plus last name or ZIP. A household number shared by several customers isn't greeted by name at all. Unverified callers get non-member pricing, and an unverified booking attaches to the existing customer without overwriting their record; the contact details live on the appointment.

## 5. Arrival windows and capacity pools
Real HVAC dispatch books 2-hour arrival windows, not appointments. Capacity has three pools: regular, a daily emergency reserve only P1 calls can use (so an urgent call never hears "next Thursday"), and a member-priority pool (a concrete benefit to sell). Routine work never takes same-day capacity. Pre-existing load is simulated deterministically so demos and tests are repeatable.

## 6. Read-backs are enforced, not suggested
Phone number and address are the two fields that waste a truck roll when wrong. `book_appointment` requires `phone_read_back_confirmed` and `address_read_back_confirmed`, and rejects a ZIP that differs from the one checked against the service area. When something's missing it lists everything at once, so the agent asks once rather than three times.

## 7. Honest fallbacks over pretend capability
No live transfer line? The agent says so and creates a callback with a due time. No urgent capacity? Dispatcher alert plus a 30-minute callback, said plainly. Tool results tell the model exactly what to say, and the system never claims something happened that didn't.

## 8. Commercial callers become leads, not rejections
Summit Air is residential-only, so no booking, but a commercial caller is still revenue the owner may want; the agent offers a callback rather than a dead end. Out-of-area callers get a kind no with a suggestion, and no callback unless asked.

## 9. Membership revenue, lightly
Active members are thanked and get their benefits, lapsed members get one gentle renewal mention after their problem is handled, and non-members hear about the club at most once, after booking.

## 10. Evals that grade outcomes, not wording
Scripted multi-turn tests break whenever the model asks things in a different order. The eval harness has an LLM play a caller persona against the real agent and grades primarily on backend state (was it booked, at what priority, was the dispatcher alerted, was the booking moved, did account details leak), with an LLM judge only for tone. Eval calls run at a fixed time on a fixed calendar, so a failure is the model's doing, not the clock's.

## 11. SQLite, one connection per call, `BEGIN IMMEDIATE` for bookings
Each call has its own connection; the seat check and the insert happen inside one immediate transaction, so two callers racing for the last seat can't both get it. There's a test that proves this fails without the lock. SQLite is right for a demo and wrong for production (see below).

## 12. The model is not the only way into P0
**Found by test call P0-01.** The caller said the furnace smelled "kinda like a skunk... earlier today, but now it's gone". The model called `assess_situation` with `gas_smell=false` (the description it passed even said "skunk-like"), triage scored P3, and the agent offered three appointment windows. It escalated only after the caller asked "do you not care that it might be a gas leak? It smells like rotten eggs." Decision 2 held: the LLM didn't decide urgency. But the LLM did decide the *input* to the rule, so the guarantee was only as good as one non-deterministic extraction.
**Chose:** a deterministic hazard lexicon (`summit/hazard_words.py`: rotten eggs, sulfur, skunk, smell-words near gas/propane, a sounding CO alarm) at three layers, any of which reaches P0 on its own:
1. **Before the model:** `SummitAgent.llm_node` screens each caller turn. On a hit, the backend goes to P0 (alert, outcome, offered windows voided) and the safety script is spoken as fixed text without an LLM call. `llm_node` rather than an STT event so it works for phone calls, `console --text` and the evals alike.
2. **In triage:** `assess()` runs the lexicon on the model's `description`, so `gas_smell=false` with "skunk-like" in the description is still P0.
3. **In the backend:** finding, booking, moving and rescheduling all refuse on P0. Refusal is checked in one place.
**Also:** spoken scripts say "nine-one-one" and spell the utility number group by group (the model had said "nine hundred and eleven"). "I can't / don't feel safe leaving" after the script gets a fixed answer rather than an improvised one, and for the rest of a P0 call every model turn carries a standing system note. Alerts for unverified callers say "caller ID matches X" rather than naming X as the caller.
**Gave up:** some false positives. A caller who mentions a skunk under the porch gets told to leave. Plain same-clause negation ("I don't smell gas") is excluded; hedges ("not sure, but it smells like gas") are not. A dusty first-use smell, or "gas furnace", doesn't fire, and those are pinned as negative-control tests. Smoke/sparks/flames are still model-extracted: "fire" is too ambiguous in HVAC speech ("the furnace won't fire") for a word list.

## Cut for time (and what I'd do next)
- **System of record:** real ServiceTitan / Housecall Pro integration behind `Store` (customer, location, job type, capacity, booking, notes).
- **SMS:** booking confirmation and "tech is on the way" texts; SMS as a second inbound channel.
- **Cancellations** by phone (today they'd go to a callback).
- **Weather-aware triage:** outdoor temperature from a forecast API to sharpen P1 (no heat at 15°F outside vs 55°F).
- **Spanish:** STT/TTS and the turn detector support it; needs prompt and safety-script translation reviewed by a native speaker.
- **Postgres + hosted agent:** SQLite and a laptop worker are right for a demo, wrong for production.
- **Call recording + QA sampling:** LiveKit session reports and recordings exist; wire a weekly review of P0/P1 calls.
- **Real address validation:** a geocoder instead of a curated ZIP/town list.
