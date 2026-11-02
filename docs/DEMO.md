# Demo runbook

## The day before

- [ ] `uv sync` and `uv run pytest` are green.
- [ ] `uv run python -m evals.run --repeat 2` passes; skim a couple of transcripts in `evals/results/`.
- [ ] The phone number's dispatch rule sends calls to the agent named `summit-air`.
- [ ] The gas emergency numbers in `config/business.toml` still match the utilities' sites.

## Right before

```bash
uv run python -m summit.seed --reset --member-phone +1YOURCELL --member-name "Your Name"
uv run python agent.py dev               # terminal 1
uv run python -m dashboard.server        # terminal 2, open http://localhost:8765
```

Call the number once from your cell: you should be greeted by name.

## Script

Each call shows something different. Keep the dashboard on screen.

1. **Member, urgent.** From your cell: confirm your name, "no heat, my mother's
   82 and it's 60 in here". Watch it go P1, offer a same-day window, read back the
   address and book. The dashboard shows the urgent alert and the booking.
2. **Safety.** From your cell: "I smell gas near the furnace, it's faint now." The
   safety script with the county's gas utility (from another phone, say the town in
   the same sentence, or it says "your gas company"), no booking, a critical alert
   with your words on the dashboard.
3. **Routine, new caller.** From another phone (or `console --text`): a tune-up.
   Same-day isn't offered; the booking is refused until the agent has actually read
   the number and address back; the confirmation is fixed text; one mention of the club.
4. **Edges.** A restaurant (callback lead), a Brooklyn ZIP (kind no), "can I talk
   to a person" (honest callback, because no transfer line is configured).
5. **Reschedule.** From your cell: "I need to move my tune-up". The old window is
   released on the dashboard.

Open a call on the dashboard to show the transcript, the reasons behind its
priority, and every tool call with its result.

## If something breaks

- **No answer on the phone:** is `agent.py dev` still running, and does the dispatch
  rule name `summit-air`? Fall back to `uv run python agent.py console`.
- **Slow or odd answers:** the fallback LLM takes over by itself; carry on.
- **Calendar looks full:** re-seed with `--reset`.
