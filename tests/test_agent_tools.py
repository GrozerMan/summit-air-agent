"""The agent's tools are thin wrappers; check they line up with the backend.

Needs livekit-agents installed (uv sync), but no credentials: nothing here talks to a model.
"""

import inspect

import pytest

pytest.importorskip("livekit.agents")

from livekit.agents import ToolError

from agent import SummitAgent, instructions_for
from summit.backend import CallSession

TOOLS = [
    "lookup_customer", "assess_situation", "check_service_address", "find_appointment_options",
    "book_appointment", "change_appointment", "request_callback", "transfer_to_human", "get_pricing",
]  # fmt: skip


def test_every_tool_is_exposed(member_call):
    agent = SummitAgent(member_call)
    assert set(TOOLS) <= {tool.id for tool in agent.tools}


@pytest.mark.parametrize(
    "tool",
    ["lookup_customer", "check_service_address", "book_appointment", "request_callback", "get_pricing"],
)
def test_tool_arguments_match_the_backend(tool):
    agent_params = list(inspect.signature(getattr(SummitAgent, tool)).parameters)[2:]
    backend_params = list(inspect.signature(getattr(CallSession, tool)).parameters)[1:]
    assert agent_params == backend_params


def test_instructions_include_the_time_and_office_status(member_call):
    text = instructions_for(member_call)
    assert "Tuesday, November 3" in text and "office is open" in text


async def test_refusals_reach_the_model_as_tool_errors(member_call):
    agent = SummitAgent(member_call)
    with pytest.raises(ToolError, match="assess_situation"):
        await agent.find_appointment_options(None)
    assert member_call.tool_log[-1]["refused"] is True


async def _reply(agent, user_text):
    from livekit.agents import ModelSettings, llm

    ctx = llm.ChatContext()
    ctx.add_message(role="system", content="instructions")
    ctx.add_message(role="user", content=user_text)
    return "".join([chunk async for chunk in agent.llm_node(ctx, [], ModelSettings())])


async def test_gas_words_get_the_script_without_the_model(make_call):
    # Test call P0-01. No LLM is configured, so any reply here came from the fixed path.
    from summit.models import Priority

    call = make_call(None)
    said = await _reply(
        SummitAgent(call), "It's kinda like a skunk. It happened earlier today. But now it's gone."
    )
    assert "leave the house now" in said and "nine-one-one" in said
    assert call.priority == Priority.P0
