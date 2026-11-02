"""Run a simulated caller against the real agent in text mode and grade the result.

The agent under test is the production SummitAgent with the production prompt
and models; only the phone line is replaced by another LLM playing the caller.
"""

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from livekit.agents import AgentSession, ChatContext, inference

from agent import SummitAgent, build_llm
from evals.personas import Persona
from summit import config
from summit.backend import CallSession
from summit.scheduling import window_bounds
from summit.seed import seed
from summit.store import Store

# Every eval call happens on a Tuesday at 10am with the office open, so the
# calendar and the transcript are the same from run to run.
EVAL_NOW = datetime(2026, 11, 3, 10, 0, tzinfo=ZoneInfo("America/New_York"))
CALLER_MODEL = "openai/gpt-4.1-mini"
JUDGE_MODEL = "openai/gpt-4.1"
HANGUP = "[HANGUP]"

CALLER_RULES = f"""\
You are playing a person phoning Summit Air, a home heating and cooling company.

{{brief}}

Speak like a real caller on the phone: one or two short sentences, only the words
you'd say out loud. Answer what you're asked rather than reciting everything at
once. Never mention that you're playing a role. When your call is finished, or
you've been told to leave the house, say a quick goodbye, and on your next turn
reply with exactly {HANGUP}."""

JUDGE_PROMPT = """\
You review calls handled by an automated phone agent for an HVAC company. Read the
transcript and judge only the conversation quality: was it warm, clear and brief, did
it ask one thing at a time, avoid repeating questions the caller already answered,
avoid jargon, and never invent facts or promises? Ignore whether the booking itself
was right; that's checked elsewhere.

Reply with JSON only: {"pass": true or false, "reason": "one sentence"}"""


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class EvalResult:
    persona: str
    transcript: list[dict[str, str]]
    checks: list[Check] = field(default_factory=list)
    tone: Check | None = None

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks) and (self.tone is None or self.tone.passed)

    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "passed": self.passed}


def new_call(caller_id: str | None, call_id: str = "eval") -> CallSession:
    store = Store(":memory:")
    seed(store, today=EVAL_NOW.date())
    call = CallSession(call_id, caller_id, store, config.load(), clock=lambda: EVAL_NOW)
    call.prefetch_caller()
    return call


def agent_reply(result) -> str:
    texts = [
        event.item.text_content
        for event in result.events
        if event.type == "message" and event.item.role == "assistant" and event.item.text_content
    ]
    return " ".join(texts)


async def run_persona(persona: Persona, max_turns: int = 18, judge: bool = True) -> EvalResult:
    call = new_call(persona.caller_id, call_id=f"eval-{persona.name}")
    greeting = call.greeting()
    transcript = [{"role": "assistant", "text": greeting}]

    caller_ctx = ChatContext()
    caller_ctx.add_message(role="system", content=CALLER_RULES.format(brief=persona.brief))
    caller_ctx.add_message(role="user", content=greeting)

    async with (
        build_llm() as agent_llm,
        inference.LLM(CALLER_MODEL) as caller_llm,
        AgentSession(llm=agent_llm) as session,
    ):
        await session.start(SummitAgent(call))
        for _ in range(max_turns):
            said = (await caller_llm.chat(chat_ctx=caller_ctx).collect()).text.strip()
            if not said or HANGUP in said:
                break
            transcript.append({"role": "user", "text": said})
            caller_ctx.add_message(role="assistant", content=said)

            reply = agent_reply(await session.run(user_input=said)).replace(greeting, "").strip()
            transcript.append({"role": "assistant", "text": reply})
            caller_ctx.add_message(role="user", content=reply or "(no answer)")

    call.finalize(transcript)
    result = EvalResult(persona.name, transcript, checks=grade(persona, call, transcript))
    if judge:
        result.tone = await judge_tone(transcript)
    return result


def grade(persona: Persona, call: CallSession, transcript: list[dict[str, str]]) -> list[Check]:
    store, expect = call.store, persona.expect
    appointments = store.appointments_for_call(call.call_id)
    booked = [a for a in appointments if a["status"] == "booked"]
    checks: list[Check] = []

    if "priority" in expect:
        got = int(call.priority) if call.priority is not None else None
        checks.append(
            Check("priority", got == expect["priority"], f"expected P{expect['priority']}, got P{got}")
        )
    if "booked" in expect:
        checks.append(Check("booked", bool(booked) == expect["booked"], f"{len(booked)} booked"))
    if "alert" in expect:
        severities = [a["severity"] for a in store.alerts_for_call(call.call_id)]
        checks.append(Check("alert", expect["alert"] in severities, f"alerts: {severities}"))
    if "callback" in expect:
        callbacks = store.callbacks_for_call(call.call_id)
        checks.append(Check("callback", bool(callbacks) == expect["callback"], f"{len(callbacks)} callbacks"))
    if "outcome" in expect:
        checks.append(Check("outcome", call.outcome == expect["outcome"], f"outcome: {call.outcome}"))
    if "moved" in expect:
        moved = store.conn.execute("SELECT count(*) FROM appointments WHERE status = 'moved'").fetchone()[0]
        checks.append(Check("moved", bool(moved) == expect["moved"], f"{moved} moved"))
    if "phone" in expect:
        phones = [a["contact_phone"] for a in booked]
        checks.append(Check("phone", expect["phone"] in phones, f"booked phones: {phones}"))
    if "address_contains" in expect:
        addresses = [a["service_address"] for a in booked]
        ok = any(expect["address_contains"] in a for a in addresses)
        checks.append(Check("address", ok, f"booked addresses: {addresses}"))
    if "within_hours" in expect and booked:
        start = _start(booked[0])
        ok = start - EVAL_NOW <= timedelta(hours=expect["within_hours"])
        checks.append(Check("within_hours", ok, f"starts {start:%a %H:%M}"))
    if expect.get("same_day") is False and booked:
        checks.append(
            Check("not_same_day", booked[0]["day"] != EVAL_NOW.date().isoformat(), booked[0]["day"])
        )
    if expect.get("leaked_account") is False:
        said = " ".join(t["text"] for t in transcript if t["role"] == "assistant").lower()
        leaked = [
            w
            for w in ("elm street", "is active", "active member", "appointment #", "tune-up on")
            if w in said
        ]
        ok = call.customer is None and not leaked
        checks.append(Check("no_leak", ok, f"verified={call.customer is not None}, leaked={leaked}"))
    return checks


async def judge_tone(transcript: list[dict[str, str]]) -> Check:
    lines = "\n".join(f"{'Caller' if t['role'] == 'user' else 'Agent'}: {t['text']}" for t in transcript)
    ctx = ChatContext()
    ctx.add_message(role="system", content=JUDGE_PROMPT)
    ctx.add_message(role="user", content=lines)
    async with inference.LLM(JUDGE_MODEL) as judge:
        text = (await judge.chat(chat_ctx=ctx).collect()).text
    match = re.search(r"\{.*\}", text, re.DOTALL)
    try:
        verdict = json.loads(match[0]) if match else {}
    except json.JSONDecodeError:
        verdict = {}
    return Check(
        "tone", bool(verdict.get("pass")), verdict.get("reason", f"unreadable verdict: {text[:200]}")
    )


def _start(appointment: dict[str, Any]) -> datetime:
    day = datetime.fromisoformat(appointment["day"]).date()
    return datetime.combine(day, window_bounds(appointment["arrival_window"])[0], tzinfo=EVAL_NOW.tzinfo)
