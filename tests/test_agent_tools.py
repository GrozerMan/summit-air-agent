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


async def test_booking_confirmation_is_spoken_without_the_model(make_call):
    # Stress report C2. The turn after book_appointment comes from the booking record;
    # no LLM is configured, so any words here came from the fixed path.
    from livekit.agents import ModelSettings, llm

    from summit.triage import Facts

    call = make_call(None)
    agent = SummitAgent(call)
    call.assess_situation(Facts(request_type="tune_up", description="tune-up"))
    call.check_service_address(zip_code="11706", property_type="house")
    call.find_appointment_options(caller_says_member=False)
    option_id = next(iter(call.offered))
    call.agent_said = "That's Jen Morales, 631-555-0155, at 33 Shore Road, Bay Shore. Is that right?"
    result = await agent.book_appointment(
        None, option_id, "Jen", "Morales", "631-555-0155", "33 Shore Road, Bay Shore", "11706",
        "tune-up", "", True, True,
    )  # fmt: skip

    ctx = llm.ChatContext()
    ctx.add_message(role="user", content="The first one.")
    ctx.insert(llm.FunctionCall(call_id="c1", name="book_appointment", arguments="{}"))
    ctx.insert(llm.FunctionCallOutput(call_id="c1", name="book_appointment", output=result, is_error=False))
    said = "".join([chunk async for chunk in agent.llm_node(ctx, [], ModelSettings())])
    assert said.startswith("You're booked.") and "33 Shore Road, Bay Shore" in said and "$159" in said


async def test_a_hazard_only_the_model_reported_is_still_spoken_as_fixed_text(make_call):
    # Review finding 8: the word screen misses "a weird odor", the model reports gas_smell=true.
    # The turn after that tool call must be the fixed script, not the model's rewording of it.
    from livekit.agents import ModelSettings, llm

    from summit.triage import Facts

    call = make_call(None)
    agent = SummitAgent(call)
    result = call.assess_situation(Facts(gas_smell=True, description="a weird odor by the furnace"))
    ctx = llm.ChatContext()
    ctx.add_message(role="user", content="There's a weird odor by the furnace.")
    ctx.insert(llm.FunctionCall(call_id="c1", name="assess_situation", arguments="{}"))
    ctx.insert(llm.FunctionCallOutput(call_id="c1", name="assess_situation", output=result, is_error=False))
    said = "".join([chunk async for chunk in agent.llm_node(ctx, [], ModelSettings())])
    assert said == call.safety_script()


async def _collect(agent, pieces):
    async def stream():
        for piece in pieces:
            yield piece

    return "".join([chunk async for chunk in agent._hold_back_false_claims(stream())])


async def test_a_booking_claim_with_nothing_booked_is_never_spoken(make_call):
    # Live round 3: read-backs confirmed, then "booked" without calling book_appointment again.
    call = make_call(None)
    agent = SummitAgent(call)
    said = await _collect(
        agent, ["Thanks, Omar. ", "Your appointment is booked for tomorrow ", "between 10 and noon."]
    )
    assert "booked" not in said and said.startswith("Thanks, Omar.")
    assert "put that through" in said
    assert any("held back" in note for note in call.notes)


async def test_ordinary_replies_and_real_bookings_pass_through(make_call, seeded):
    call = make_call(None)
    agent = SummitAgent(call)
    text = "Which of these works for you? I can get you booked for tomorrow if you like."
    assert await _collect(agent, [text]) == text
    call.booked.append(1)
    assert "booked" in await _collect(agent, ["You're booked for tomorrow."])
