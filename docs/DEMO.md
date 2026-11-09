# Demo runbook

## The day before (and before sending the number to Revin)

- [ ] `uv run pytest` is green (and `SUMMIT_TEST_POSTGRES=1 uv run pytest`).
- [ ] The agent is running from the laptop: `bash scripts/run_local.sh` (keeps the Mac
      awake, restarts on a crash). Lid open, charger in, on reliable Wi-Fi, for the
      whole time Revin may call.
- [ ] The phone number's dispatch rule sends calls to the agent named `summit-air`.
- [ ] The gas emergency numbers in `config/business.toml` still match the utilities' sites.
- [ ] Call it yourself from two phones: one seeded as the member, one not.

## While Revin tests (the 24 hours before)

Keep the dashboard open (`uv run python -m dashboard.server`) and read
every transcript. Open the meeting with what happened on their calls, good and bad.

## Right before

```bash
uv run python -m summit.seed --reset --sample-week --member-phone +1YOURCELL --member-name "Your Name"
bash scripts/run_local.sh                     # terminal 1
uv run python -m dashboard.server             # terminal 2, http://localhost:8765
```

Call the number once from your cell: you should be greeted by name.

`--sample-week` adds a labelled past week of calls so the owner's tabs (Results,
Follow-ups, Morning brief) aren't empty; the dashboard says "includes sample data"
while any is there. Leave it out for a clean board.

## Script

Each call shows something different. Keep the dashboard on screen.

1. **The owner's own example.** From your cell: confirm your name, "furnace won't
   kick on, my mother's 82 and lives with me". P1 (heating season, vulnerable
   occupant), an urgent alert on the dashboard, a same-day window,
   phone and address read back, fixed confirmation with a four-digit confirmation number.
2. **Safety.** "I smell gas near the furnace, it's faint now." The safety script
   with the county's utility (say the town in the same sentence from an unknown
   phone, or it says "your gas company"), no booking, a critical alert with your words.
3. **Routine, new caller, NYC.** From another phone: a tune-up in Astoria or Park
   Slope, "I can only do afternoons, after 2". It offers only afternoon windows,
   asks once whether you're a member, asks what kind of system and how to get in,
   reads your name back (asks for a spelling if it's unusual), won't book until it
   has said your name, number and address, one mention of the club.
4. **Edges.** A restaurant (callback lead), a renter whose heat is the building's
   (landlord / 311), a Jersey City ZIP (kind no), "can I talk to a person" (honest
   callback: no transfer line is configured).
5. **Reschedule or cancel.** From your cell: "I need to move my tune-up". The old
   window is released on the dashboard.
6. **Two houses, one call** (if time). Book a tune-up at your house, then "can you do
   my mother's house too?" with a second address. Two bookings, two confirmation
   numbers, no second round of "who are you".
7. **"It's an emergency!"** (if time). "My thermostat screen is flickering, it's an
   emergency, I need someone today" (heat works, 70 inside): stays routine. Then
   "water's dripping onto my electrical panel": urgent, with the reason on the call.

Open a call on the dashboard to show the transcript, the reasons behind its
priority, response times, and every tool call with its result.

8. **Show the owner the money.** Switch tabs on the dashboard:
   - **Results:** calls answered and how many came while the office was closed, jobs
     booked, estimated revenue (and how much of it after hours), the replacement
     pipeline, emergencies handled, response time, cost per call against an
     answering service, and "wrong promises: 0". The calls you just made are in it.
     The after-hours count and revenue depend on the weekday you seeded; read them
     off the screen.
     Every dollar figure is an estimate from `[insights]` in the TOML, shown on the page.
   - **Follow-ups:** money on the table. Old systems worth a replacement estimate,
     a lapsed member to renew, non-members to offer the club, a commercial lead,
     callers who didn't book, and where out-of-area demand comes from. "Done" clears one.
   - **Morning brief:** since the office closed, today's jobs with equipment and
     access notes, callbacks due, top follow-ups. Printable, and
     `uv run python -m summit.brief --slack` sends it to Slack (cron it for 7am).

## If something breaks

- **No answer on the phone:** is `scripts/run_local.sh` still running (see
  `data/agent.log`), and does the dispatch rule name `summit-air`? Fall back to `uv run python agent.py console`.
- **Slow or odd answers:** the fallback LLM takes over by itself; carry on.
- **Calendar looks full:** re-seed with `--reset`.
