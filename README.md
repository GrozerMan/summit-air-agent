# Summit Air AI phone agent

An inbound phone agent for Summit Air, a residential HVAC company. It answers the
phone, works out what the caller needs, handles safety emergencies first, checks
membership and service eligibility, collects what a technician needs, and books
a real arrival window, leaving a clean call record for the office.

**The design in one line:** the voice layer is bought, the business logic is
owned. LiveKit handles telephony, speech and turn-taking; every decision that
matters to Summit Air (urgency, eligibility, scheduling, pricing, escalation)
is plain, tested Python in `summit/` that the LLM can only reach through tools.

```
Caller ── PSTN ──> LiveKit phone number ──> LiveKit Agents worker (agent.py)
                                              │  Deepgram Nova-3 STT
                                              │  GPT-4.1-mini (fallback: Gemini 2.5 Flash)
                                              │  Cartesia Sonic-3 TTS
                                              │  audio turn detector, Krisp noise cancellation
                                              ▼ function tools
                                      summit/ (deterministic business logic)
                                      ├─ triage.py        P0-P3 rules, safety scripts
                                      ├─ service_area.py  3 counties, residential check
                                      ├─ scheduling.py    arrival windows, capacity pools
                                      ├─ backend.py       per-call state + guardrails
                                      └─ store.py         SQLite system of record
                                              ▼
                       dashboard (calls, alerts, callbacks, bookings)  +  optional Slack alerts
```

More detail: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · why things are the way they are:
[docs/DECISIONS.md](docs/DECISIONS.md) · demo runbook: [docs/DEMO.md](docs/DEMO.md)

## Setup (macOS)

```bash
brew install uv livekit-cli
uv sync                               # Python 3.11+, livekit-agents 1.8.9
cp .env.example .env.local            # add your LiveKit Cloud URL, key and secret
                                      #   (or: lk cloud auth && lk app env -w)
uv run python agent.py download-files
uv run python -m summit.seed --member-phone +1YOURCELL --member-name "Your Name"
uv run pytest                         # 101 unit tests, no keys needed
```

A free LiveKit Cloud project covers agent minutes, LiveKit Inference credits (so no
separate OpenAI, Deepgram or Cartesia keys) and a US phone number.

## Talk to it

| How | Command |
|---|---|
| Typed, in the terminal | `uv run python agent.py console --text` |
| Voice, laptop mic | `uv run python agent.py console` |
| Real phone call | `uv run python agent.py dev`, then dial your LiveKit number (see below) |
| Watch calls live | `uv run python -m dashboard.server` → http://localhost:8765 |

Console mode has no caller ID. Set `DEMO_CALLER_ID=+1YOURCELL` in `.env.local` to be
greeted as the seeded member.

For real calls: LiveKit dashboard → Telephony → Phone Numbers → buy a number, then
create a dispatch rule (type Individual) that dispatches the agent named `summit-air`.

## Test it

```bash
uv run pytest                                      # triage, area, scheduling, guardrails, booking race, dashboard
uv run python -m evals.run                         # 11 simulated callers end to end (needs LiveKit creds)
uv run python -m evals.run gas_smell messy_caller --repeat 3
uv run pytest evals -m eval                        # targeted single-turn behaviour checks
```

`evals.run` has an LLM play each caller against the real agent and prompt, then
grades on what the backend recorded (booked? what priority? alert raised? booking
moved? any account details leaked?) plus an LLM judge for tone. Every eval call
happens at the same fixed time, so the calendar is identical from run to run.
Transcripts land in `evals/results/`.

## Changing the business rules

Prices, hours, service-area ZIPs and towns, gas utility numbers, triage
thresholds, capacity, callback timing and the transfer number all live in
[`config/business.toml`](config/business.toml). The prompt is
[`prompts/system_prompt.md`](prompts/system_prompt.md). Triage rules are in
[`summit/triage.py`](summit/triage.py), deliberately short enough to read with the owner.

## Assumptions

The brief leaves these open; each is a config value, not hard-coded.

- **Service area:** Nassau, Suffolk and Westchester counties (NY), via a curated ZIP and town list. A ZIP that looks local but isn't on the list gets a "which town?" rather than a guess.
- **Residential:** houses, condo/apartment units and 2-4 family homes. Businesses and building-wide plants are commercial: no booking, a callback lead for the office.
- **Membership:** "Summit Comfort Club": no diagnostic fee, two tune-ups a year, priority capacity. Verified by caller ID plus name confirmation, or phone plus last name/ZIP.
- **Prices quoted:** diagnostic $129 (members $0), tune-up $159, after-hours +$99, free replacement estimates. Repairs are never estimated by phone.
- **Scheduling:** 2-hour arrival windows, 2 jobs per window per county, plus a daily emergency reserve (P1 only) and member-priority capacity. The calendar is a mock with a seeded, deterministic existing load; production would call ServiceTitan / Housecall Pro through the same `Store` surface.
- **Hours:** office Mon-Fri 7-7, Sat 8-2. The agent answers 24/7 and alerts on-call for urgent calls after hours. Only urgent work is booked on Sundays.
- **Human transfer:** off by default (no second line); requests become honest callbacks. Set `HUMAN_TRANSFER_NUMBER` to enable live transfer during office hours (SIP REFER; your number's trunk has to allow call transfer).
- **Gas emergency numbers:** National Grid (Long Island) 1-800-490-0045 and Con Edison (Westchester) 1-800-752-6633, from each utility's own page, always alongside 911.

## Environment variables

| Variable | Needed for | |
|---|---|---|
| `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` | everything except unit tests | from your LiveKit Cloud project |
| `DEMO_CALLER_ID` | console mode | pretend to call from this number |
| `HUMAN_TRANSFER_NUMBER` | live transfers | E.164, e.g. `+15165550100` |
| `SLACK_WEBHOOK_URL` | Slack copies of alerts | optional; the dashboard always has them |
| `SUMMIT_DB_PATH` | | defaults to `data/summit.db` |
