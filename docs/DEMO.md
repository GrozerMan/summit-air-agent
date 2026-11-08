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
uv run python -m summit.seed --reset --member-phone +1YOURCELL --member-name "Your Name"
bash scripts/run_local.sh                     # terminal 1
uv run python -m dashboard.server             # terminal 2, http://localhost:8765
```

Call the number once from your cell: you should be greeted by name.

## Script

Each call shows something different. Keep the dashboard on screen.

1. **The owner's own example.** From your cell: confirm your name, "furnace won't
   kick on, my mother's 82 and lives with me". P1 (heating season, vulnerable
   occupant), an urgent alert on the dashboard, a same-day window,
   phone and address read back, fixed confirmation.
2. **Safety.** "I smell gas near the furnace, it's faint now." The safety script
   with the county's utility (say the town in the same sentence from an unknown
   phone, or it says "your gas company"), no booking, a critical alert with your words.
3. **Routine, new caller, NYC.** From another phone: a tune-up in Astoria or Park
   Slope. It asks once whether you're a member, asks what kind of system and how
   to get in, won't book until it has read your number and address back, one
   mention of the club.
4. **Edges.** A restaurant (callback lead), a renter whose heat is the building's
   (landlord / 311), a Jersey City ZIP (kind no), "can I talk to a person" (honest
   callback: no transfer line is configured).
5. **Reschedule or cancel.** From your cell: "I need to move my tune-up". The old
   window is released on the dashboard.

Open a call on the dashboard to show the transcript, the reasons behind its
priority, response times, and every tool call with its result.

## If something breaks

- **No answer on the phone:** is `scripts/run_local.sh` still running (see
  `data/agent.log`), and does the dispatch rule name `summit-air`? Fall back to `uv run python agent.py console`.
- **Slow or odd answers:** the fallback LLM takes over by itself; carry on.
- **Calendar looks full:** re-seed with `--reset`.
