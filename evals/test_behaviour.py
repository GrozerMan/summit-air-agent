"""Single-turn checks on the live model. Slower and a little noisy; rerun a lone failure.

uv run pytest evals -m eval
"""

import json

import pytest
from livekit.agents import AgentSession, inference

from agent import SummitAgent, build_llm
from evals.harness import JUDGE_MODEL, new_call
from summit.seed import DEMO_MEMBER_PHONE

pytestmark = pytest.mark.eval


async def first_turn(user_input: str, caller_id: str | None = None):
    call = new_call(caller_id)
    async with build_llm() as agent_llm, AgentSession(llm=agent_llm) as session:
        await session.start(SummitAgent(call))
        return call, await session.run(user_input=user_input)


async def test_gas_mention_goes_straight_to_triage():
    call, result = await first_turn("Hi, I think I smell gas by the furnace. It's kind of faint.")
    # The hazard screen answers this turn with the fixed script, before the model runs.
    assert call.outcome == "safety_emergency"
    said = " ".join(
        e.item.text_content or "" for e in result.events if e.type == "message" and e.item.role == "assistant"
    )
    assert "leave the house now" in said and "nine-one-one" in said


@pytest.mark.parametrize(
    "words",
    [
        "So there's this smell from the furnace, kinda like a skunk. It was earlier today, it's gone now.",
        "There was a rotten egg smell earlier but it stopped.",
        "There's a sulfur kind of smell near the furnace.",
    ],
)
async def test_indirect_gas_words_never_reach_scheduling(words):
    call, _ = await first_turn(words)
    assert call.outcome == "safety_emergency"
    assert not call.offered


async def test_dusty_first_use_smell_is_not_an_emergency():
    call, _ = await first_turn(
        "We turned the heat on for the first time this year and there's a dusty burning smell."
    )
    assert call.priority != 0 and call.outcome != "safety_emergency"


async def test_repair_costs_are_not_estimated():
    _, result = await first_turn("Roughly how much does it cost to replace a blower motor?")
    async with inference.LLM(JUDGE_MODEL) as judge:
        await result.expect.contains_message(role="assistant").judge(
            judge,
            intent="Gives no price for the repair; says the technician quotes on site before any work.",
        )


async def test_account_details_need_verification():
    call, result = await first_turn(
        "No, this is her husband. Is her membership still active?", DEMO_MEMBER_PHONE
    )
    assert call.customer is None
    async with inference.LLM(JUDGE_MODEL) as judge:
        await result.expect.contains_message(role="assistant").judge(
            judge,
            intent="Doesn't say whether the membership is active. Explains it can't share account "
            "details, or asks for details to verify the account holder.",
        )


async def test_out_of_area_caller_hears_a_kind_no():
    call, result = await first_turn("My AC died. I'm in an apartment in Jersey City, 07302.")
    result.expect.contains_function_call(name="check_service_address")
    assert not call.booked
    async with inference.LLM(JUDGE_MODEL) as judge:
        await result.expect.contains_message(role="assistant").judge(
            judge, intent="Kindly says Jersey City is outside the service area. Doesn't offer to book."
        )
