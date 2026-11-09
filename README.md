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
                                      ├─ hazard_words.py  gas/CO/fire in the caller's words
                                      ├─ triage.py        P0-P3 rules, safety scripts
                                      ├─ service_area.py  NYC + Long Island + Westchester
                                      ├─ scheduling.py    arrival windows, capacity pools
                                      ├─ backend.py       per-call state + guardrails
                                      └─ store.py         SQLite locally, Postgres deployed
                                              ▼
           dashboard: dispatch board + owner views (insights.py)  +  optional Slack alerts
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
uv run pytest                         # unit tests, no keys needed (SUMMIT_TEST_POSTGRES=1: on Postgres)
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
| Owner's morning brief | `uv run python -m summit.brief` (add `--slack` to post it) |

The dashboard has four tabs: **Dispatch** (alerts, callbacks, calls, upcoming
bookings), and for the owner **Results** (calls answered, after hours, jobs and estimated
revenue, emergencies, response time, cost per call), **Follow-ups** (replacement
leads, renewals, commercial leads, callers who didn't book) and **Morning brief**.
`summit.seed --sample-week` adds a labelled sample week so those aren't empty in a demo.

Console mode has no caller ID. Set `DEMO_CALLER_ID=+1YOURCELL` in `.env.local` to be
greeted as the seeded member.

For real calls: LiveKit dashboard → Telephony → Phone Numbers → buy a number, then
create a dispatch rule (type Individual) that dispatches the agent named `summit-air`.

## Test it

```bash
uv run pytest                                      # triage, area, scheduling, guardrails, booking race, dashboard
uv run python -m evals.run                         # every simulated caller end to end (needs LiveKit creds)
uv run python -m evals.run gas_smell messy_caller --repeat 3
uv run pytest evals -m eval                        # targeted single-turn behaviour checks
```

`evals.run` has an LLM play each caller against the real agent and prompt, then
grades on what the backend recorded (booked? what priority? alert raised? booking
moved?) and on what the caller actually heard: on a P0 call, the safety script
word for word with nothing reassuring alongside it; for an unverified caller, none
of the account's own details (street, town, ZIP, membership status, appointment
day or window); on every call, no claim of a booking or a callback the records
don't show. An LLM judge grades tone. Every eval call happens at the same fixed
time, so the calendar is identical from run to run. Transcripts land in
`evals/results/`. `uv run python -m evals.stress.grader_audit --no-judge` checks
the grader itself: four deliberately wrong agents must fail, three correct ones pass.

## Deploying (LiveKit Cloud)

```bash
# Postgres for the call records (e.g. a free Neon project in us-east; keep ?sslmode=require)
DATABASE_URL=postgresql://... uv run python -m summit.seed --reset --member-phone +1YOURCELL --member-name "Your Name"
lk agent create --secrets DATABASE_URL=postgresql://... --secrets SLACK_WEBHOOK_URL=https://hooks.slack.com/...
lk agent deploy                        # later code changes
lk agent logs                          # live worker logs
DATABASE_URL=postgresql://... uv run python -m dashboard.server   # the office board, from anywhere
```

The phone number's dispatch rule must name the agent `summit-air`. Stop any laptop
worker, or run it with `AGENT_NAME=summit-air-dev`, so it can't answer calls meant
for the deploy.

## Test accounts

Seeded by `summit.seed`. From your own phone you're a new caller; to test the member
paths, verify with the account's phone number, last name and ZIP.

| Who | Phone on the account | Last name | ZIP | What it shows |
|---|---|---|---|---|
| Dana Reyes (or the name you seed) | the `--member-phone` you seed (default 516-555-0142) | Reyes | 11501 | active member, a tune-up to move or cancel |
| Robert Klein | 914-555-0188 | Klein | 10601 | lapsed member (one gentle renewal mention) |
| Priya Shah | 631-555-0177 | Shah | 11743 | customer, not a member |
| Tom / Ann Walsh | 516-555-0199 | Walsh | 11530 | two people on one landline: asks which one |

## Changing the business rules

Prices, hours, holidays, gas utility numbers, triage thresholds and the heating
season, capacity, callback timing, the transfer number and the owner board's revenue
and cost estimates (`[insights]`) all live in
[`config/business.toml`](config/business.toml). Served ZIPs are in
[`config/service_area.csv`](config/service_area.csv), generated from GeoNames by
[`scripts/build_service_area.py`](scripts/build_service_area.py) for the counties listed in the TOML. The prompt is
[`prompts/system_prompt.md`](prompts/system_prompt.md). Triage rules are in
[`summit/triage.py`](summit/triage.py), deliberately short enough to read with the owner.

## Assumptions

The brief leaves these open; each is a config value, not hard-coded.

- **Service area:** the brief says an NYC company covering "three counties"; the agent serves the five boroughs plus Nassau, Suffolk and Westchester, every ZIP in those counties. A town or neighborhood it doesn't recognise, or one in two counties (Floral Park, Inwood), gets "what's the ZIP?" rather than a no. Narrowing it is one line in the TOML and a re-run of the script.
- **Residential:** houses, condo/co-op/apartment units and 2-4 family homes. Businesses, building owners of 5+ units and building-wide plants are commercial: no booking, a callback lead for the office. A renter whose heat comes from the building is pointed to the landlord or super (and 311 in NYC).
- **Urgency:** the owner's rule that no heat in winter is urgent applies from Oct 1 to May 31 (NYC's heat season) unless it's at least 65°F inside. Every such call may use the emergency reserve, so in a cold snap that reserve runs out sooner and callers get an urgent dispatcher callback; the reserve size is config.
- **Membership:** "Summit Comfort Club": no diagnostic fee, two tune-ups a year, priority capacity. Verified by caller ID plus name confirmation; from another number, the account's phone, last name *and* ZIP. A caller who says no to the greeting name can't be verified as the person they said they aren't. Three lookups per call at most. An unknown caller is asked once, before times are offered, whether they're already a member.
- **Prices quoted:** diagnostic $129 (members $0), tune-up $159, after-hours +$99, free replacement estimates. Repairs are never estimated by phone.
- **Scheduling:** 2-hour arrival windows, 2 jobs per window per county, plus a daily emergency reserve (P1 only) and member-priority capacity. Windows are narrowed to when the caller says they can be home; one call can book more than one request (a second problem or a second address); each booking ends with a confirmation number. The calendar is a mock with a seeded, deterministic existing load; production would call ServiceTitan / Housecall Pro through the same `Store` surface.
- **Hours:** office Mon-Fri 7-7, Sat 8-2, closed on listed holidays. The agent answers 24/7; urgent calls after hours raise an urgent alert flagged for the on-call technician (dashboard, and Slack if configured; there's no SMS or phone paging yet). Only urgent work is booked on Sundays and holidays.
- **Human transfer:** off by default (no second line); requests become honest callbacks. Set `HUMAN_TRANSFER_NUMBER` to enable live transfer during office hours (SIP REFER; your number's trunk has to allow call transfer).
- **Gas emergency numbers:** National Grid Long Island 1-800-490-0045 (Nassau, Suffolk), National Grid NYC 718-643-4050 (Brooklyn, Staten Island) and Con Edison 1-800-752-6633 (Manhattan, the Bronx, Westchester), from each utility's own page. Queens is split between utilities, so a Queens caller hears "nine-one-one or your gas company". The safety script always gives a second number alongside 911: the county's utility when we know where the caller is (a checked address, a place or ZIP they say they're at, the account's address, caller ID), otherwise "your gas company". The dispatcher alert carries the caller's own words.

## Environment variables

| Variable | Needed for | |
|---|---|---|
| `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` | everything except unit tests | from your LiveKit Cloud project |
| `DEMO_CALLER_ID` | console mode | pretend to call from this number |
| `HUMAN_TRANSFER_NUMBER` | live transfers | E.164, e.g. `+15165550100` |
| `SLACK_WEBHOOK_URL` | Slack copies of alerts | optional; the dashboard always has them |
| `SUMMIT_DB_PATH` | | defaults to `data/summit.db` |
| `DATABASE_URL` | the deployed agent | Postgres; when set, used instead of SQLite |
| `AGENT_NAME` | a laptop worker next to the deploy | e.g. `summit-air-dev`; default `summit-air` |
