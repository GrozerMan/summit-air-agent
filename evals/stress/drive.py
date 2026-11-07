"""Drive scripted or adaptive callers against the real agent in text mode.

    uv run python -m evals.stress.drive                          # every scenario, 3 runs each
    uv run python -m evals.stress.drive gas_negated_now co_symptoms --repeat 5
    uv run python -m evals.stress.drive --list
    uv run python -m evals.stress.drive --group safety --parallel 2

Same construction as evals/harness.py: the production SummitAgent, prompt and
models (build_llm), one CallSession per run with a fixed clock. Differences:

* Each run gets its own SQLite file under evals/stress/runs/db/, so the backend
  state can be inspected afterwards with sqlite3 (it is the source of truth).
* Scripted scenarios send fixed caller lines; adaptive ones use the evals'
  LLM-caller rules with a new brief.
* Every turn records the agent's words, every function call with arguments and
  output (from LiveKit's RunResult) and the backend's own tool log (which also
  shows the hazard screen, which isn't a function call).

Results: evals/stress/runs/<scenario>.md (all runs, transcript + tool log + DB
rows) and evals/stress/runs/summary.json (pass rates).
"""

import argparse
import asyncio
import json
import os
import re
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv

load_dotenv(".env.local")

from livekit.agents import AgentSession, ChatContext, inference, llm  # noqa: E402

from agent import SummitAgent, build_llm  # noqa: E402
from evals.harness import CALLER_MODEL, CALLER_RULES, EVAL_NOW, HANGUP  # noqa: E402
from summit import config  # noqa: E402
from summit.backend import CallSession  # noqa: E402
from summit.seed import seed  # noqa: E402
from summit.store import Store  # noqa: E402

HERE = Path(__file__).parent
RUNS = Path(os.getenv("STRESS_RUNS", str(HERE / "runs")))
DBS = RUNS / "db"


@dataclass
class Turn:
    caller: str
    agent: str
    calls: list[dict[str, Any]]  # function calls/outputs seen by LiveKit
    backend: list[dict[str, Any]]  # new CallSession.tool_log entries


@dataclass
class Run:
    scenario: str
    n: int
    call: CallSession
    greeting: str
    turns: list[Turn] = field(default_factory=list)
    error: str | None = None

    # helpers for checks -------------------------------------------------------------
    @property
    def store(self) -> Store:
        return self.call.store

    def agent_text(self) -> str:
        return " ".join([self.greeting] + [t.agent for t in self.turns])

    def booked(self) -> list[dict]:
        return [a for a in self.store.appointments_for_call(self.call.call_id) if a["status"] == "booked"]

    def alerts(self) -> list[str]:
        return [a["severity"] for a in self.store.alerts_for_call(self.call.call_id)]

    def callbacks(self) -> list[dict]:
        return self.store.callbacks_for_call(self.call.call_id)

    def tools(self, name: str | None = None) -> list[dict]:
        return [t for t in self.call.tool_log if name is None or t["tool"] == name]


Check = Callable[[Run], tuple[bool, str]]


@dataclass
class Scenario:
    name: str
    group: str
    checks: dict[str, Check]
    turns: list[str] | None = None  # scripted caller lines
    brief: str | None = None  # adaptive caller
    caller_id: str | None = None
    now: datetime = EVAL_NOW
    max_turns: int = 16
    llm_factory: Callable[[], llm.LLM] | None = None
    note: str = ""


def _items(result) -> tuple[str, list[dict[str, Any]]]:
    said, calls = [], []
    for ev in result.events:
        if ev.type == "message" and ev.item.role == "assistant" and ev.item.text_content:
            said.append(ev.item.text_content)
        elif ev.type == "function_call":
            calls.append({"call": ev.item.name, "args": ev.item.arguments})
        elif ev.type == "function_call_output":
            calls.append({"output_of": ev.item.name, "is_error": ev.item.is_error, "output": ev.item.output})
    return " ".join(said), calls


def new_call(sc: Scenario, n: int) -> CallSession:
    DBS.mkdir(parents=True, exist_ok=True)
    path = DBS / f"{sc.name}-{n}.db"
    for suffix in ("", "-wal", "-shm"):
        Path(str(path) + suffix).unlink(missing_ok=True)
    store = Store(path)
    seed(store, today=sc.now.date())
    now = sc.now
    call = CallSession(f"stress-{sc.name}-{n}", sc.caller_id, store, config.load(), clock=lambda: now)
    call.prefetch_caller()
    call.save()
    return call


PACE = 1.5  # seconds between model turns; LiveKit Inference limits requests per minute
RATE_LIMITED = ("429", "rate limit", "QuotaStatusExceeded")


async def run_once(sc: Scenario, n: int) -> Run:
    """One call. A run that dies on the gateway's rate limit is retried after a pause:
    a 429 says nothing about the agent."""
    for attempt in range(4):
        run = await _run_once(sc, n)
        if not (run.error and any(m in run.error for m in RATE_LIMITED)):
            return run
        print(f"  rate limited: {sc.name} run {n}, retry {attempt + 1} in 60s", flush=True)
        await asyncio.sleep(60)
    return run


async def _run_once(sc: Scenario, n: int) -> Run:
    call = new_call(sc, n)
    run = Run(sc.name, n, call, call.greeting())
    caller_ctx = None
    caller_llm = None
    try:
        agent_llm = sc.llm_factory() if sc.llm_factory else build_llm()
        async with agent_llm, AgentSession(llm=agent_llm) as session:
            await session.start(SummitAgent(call))
            if sc.brief:
                caller_llm = inference.LLM(CALLER_MODEL)
                caller_ctx = ChatContext()
                caller_ctx.add_message(role="system", content=CALLER_RULES.format(brief=sc.brief))
                caller_ctx.add_message(role="user", content=run.greeting)
            lines = iter(sc.turns or [])
            for _ in range(sc.max_turns):
                if sc.brief:
                    said = (await caller_llm.chat(chat_ctx=caller_ctx).collect()).text.strip()
                    if not said or HANGUP in said:
                        break
                    caller_ctx.add_message(role="assistant", content=said)
                else:
                    said = next(lines, None)
                    if said is None:
                        break
                seen = len(call.tool_log)
                await asyncio.sleep(PACE)
                result = await asyncio.wait_for(session.run(user_input=said), timeout=90)
                reply, calls = _items(result)
                reply = reply.replace(run.greeting, "").strip()
                run.turns.append(Turn(said, reply, calls, call.tool_log[seen:]))
                if caller_ctx is not None:
                    caller_ctx.add_message(role="user", content=reply or "(no answer)")
            if caller_llm:
                await caller_llm.aclose()
    except Exception:
        run.error = traceback.format_exc()[-1500:]
    transcript = [{"role": "assistant", "text": run.greeting}]
    for t in run.turns:
        transcript += [{"role": "user", "text": t.caller}, {"role": "assistant", "text": t.agent}]
    call.finalize(transcript)
    return run


def grade(sc: Scenario, run: Run) -> dict[str, tuple[bool, str]]:
    out = {}
    if run.error:
        out["no_crash"] = (False, run.error.splitlines()[-1])
    for name, check in sc.checks.items():
        try:
            out[name] = check(run)
        except Exception as e:
            out[name] = (False, f"check crashed: {e!r}")
    # Round 2: anything the agent said that sounds like a booking or a callback must be backed by a row.
    # Deliberately looser than summit/claims.py, which this suite also tests.
    text = " ".join(t.agent for t in run.turns)
    booking_words = re.search(r"you'?re (all )?(booked|set for|scheduled|on the schedule|confirmed)|"
                              r"(technician|tech|someone) will (be there|arrive|come|stop by)|see you (tomorrow|today|on)|"
                              r"got you down|on the calendar|appointment is (set|booked|confirmed|scheduled)", text, re.I)
    rows = [a for a in run.store.appointments_for_call(run.call.call_id) if a["status"] in ("booked", "on_hold")]
    moved = run.call.outcome == "rescheduled"
    if booking_words and not rows and not moved:
        out["no_unbacked_booking_claim"] = (False, f"said {booking_words.group(0)!r} with no appointment row; "
                                            f"backend flagged={bool(run.call.false_claims)}")
    else:
        out["no_unbacked_booking_claim"] = (True, "")
    call_words = re.search(r"(will|'ll) (call|ring|contact|reach out to|get back to) you|you'?ll (get|receive|hear)|"
                           r"expect a call|follow up with you|be in touch", text, re.I)
    if call_words and not run.callbacks():
        out["no_unbacked_callback_claim"] = (False, f"said {call_words.group(0)!r} with no callback row; "
                                             f"backend flagged={bool(run.call.false_claims)}")
    else:
        out["no_unbacked_callback_claim"] = (True, "")
    # Every call leaves a complete record.
    row = run.store.get_call(run.call.call_id)
    complete = bool(row and row["outcome"] and row["ended_at"] and row["transcript"]
                    and (row["summary"] or not run.call.tool_log))
    out["record_complete"] = (complete, f"outcome={row and row['outcome']} summary={bool(row and row['summary'])}")
    return out


def _db_state(run: Run) -> str:
    cid = run.call.call_id
    lines = []
    for title, rows in [
        ("appointments", run.store.appointments_for_call(cid)),
        ("alerts", run.store.alerts_for_call(cid)),
        ("callbacks", run.store.callbacks_for_call(cid)),
    ]:
        lines.append(f"**{title}** ({len(rows)})")
        for r in rows:
            r = {k: v for k, v in r.items() if k not in ("created_at",)}
            lines.append(f"- `{json.dumps(r, default=str)}`")
    row = run.store.get_call(cid)
    if row:
        rec = row["record"]
        lines.append(
            f"**calls row**: priority={row['priority']} outcome={row['outcome']} "
            f"reasons={rec.get('reasons')} property={rec.get('property')} "
            f"area={rec.get('service_area')} verified={rec.get('verified_customer_id')}"
        )
        lines.append(f"**summary**: {row['summary']}")
    return "\n".join(lines)


def render(sc: Scenario, runs: list[Run], grades: list[dict]) -> str:
    out = [f"# {sc.name}\n", f"Group: {sc.group}. Caller ID: {sc.caller_id or 'none'}. "
           f"Clock: {sc.now:%a %Y-%m-%d %H:%M %Z}. Mode: {'adaptive' if sc.brief else 'scripted'}.\n"]
    if sc.note:
        out.append(f"> {sc.note}\n")
    if sc.brief:
        out.append(f"Brief: {sc.brief}\n")
    names = list(grades[0]) if grades else []
    out.append("| check | " + " | ".join(f"run {r.n}" for r in runs) + " | pass rate |")
    out.append("|---|" + "---|" * (len(runs) + 1))
    for name in names:
        cells = ["PASS" if g.get(name, (False,))[0] else "**FAIL**" for g in grades]
        rate = sum(g.get(name, (False,))[0] for g in grades)
        out.append(f"| {name} | " + " | ".join(cells) + f" | {rate}/{len(grades)} |")
    for run, g in zip(runs, grades):
        out.append(f"\n## Run {run.n}\n")
        for name, (ok, detail) in g.items():
            if not ok:
                out.append(f"- ✗ **{name}**: {detail}")
        out.append(f"\n**Agent:** {run.greeting}\n")
        for t in run.turns:
            out.append(f"**Caller:** {t.caller}\n")
            for c in t.backend:
                flag = " (REFUSED)" if c["refused"] else ""
                out.append(f"> `{c['tool']}{flag}` {json.dumps(c['args'], default=str)[:400]}  \n"
                           f"> → {c['result'][:500]}\n")
            for c in t.calls:
                if "call" in c and c["call"] not in {b["tool"] for b in t.backend}:
                    out.append(f"> `{c['call']}` {c['args'][:300]}\n")
            out.append(f"**Agent:** {t.agent}\n")
        if run.error:
            out.append(f"```\n{run.error}\n```")
        out.append("### DB state\n" + _db_state(run))
    return "\n".join(out)


async def run_scenario(sc: Scenario, repeat: int, sem: asyncio.Semaphore) -> dict:
    async def one(n):
        async with sem:
            return await run_once(sc, n)

    runs = await asyncio.gather(*(one(n) for n in range(1, repeat + 1)))
    grades = [grade(sc, r) for r in runs]
    (RUNS / f"{sc.name}.md").write_text(render(sc, runs, grades))
    summary = {name: sum(g[name][0] for g in grades if name in g) for name in grades[0]}
    status = "PASS" if all(v == len(runs) for v in summary.values()) else "FAIL"
    print(f"{status}  {sc.name}: " + ", ".join(f"{k} {v}/{len(runs)}" for k, v in summary.items()), flush=True)
    return {"scenario": sc.name, "group": sc.group, "runs": len(runs), "checks": summary}


async def main() -> int:
    global PACE
    from evals.stress.scenarios import SCENARIOS

    by_name = {s.name: s for s in SCENARIOS}
    p = argparse.ArgumentParser()
    p.add_argument("names", nargs="*")
    p.add_argument("--repeat", type=int, default=3)
    p.add_argument("--parallel", type=int, default=3)
    p.add_argument("--group")
    p.add_argument("--from", dest="start", help="skip scenarios before this one")
    p.add_argument("--pace", type=float, default=1.5)
    p.add_argument("--list", action="store_true")
    a = p.parse_args()
    if a.list:
        for s in SCENARIOS:
            print(f"{s.group:12} {s.name}")
        return 0
    chosen = [by_name[n] for n in a.names] if a.names else SCENARIOS
    if a.group:
        chosen = [s for s in chosen if s.group == a.group]
    if a.start:
        names = [s.name for s in chosen]
        chosen = chosen[names.index(a.start):]
    PACE = a.pace
    RUNS.mkdir(parents=True, exist_ok=True)
    sem = asyncio.Semaphore(a.parallel)
    results = []
    for sc in chosen:  # scenarios in order; runs of one scenario in parallel
        try:
            results.append(await run_scenario(sc, a.repeat, sem))
        except Exception:
            print(f"ERROR {sc.name}\n{traceback.format_exc()}", flush=True)
    path = RUNS / "summary.json"
    old = json.loads(path.read_text()) if path.exists() else {}
    old.update({r["scenario"]: r for r in results})
    path.write_text(json.dumps(old, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
