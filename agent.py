"""Summit Air inbound phone agent.

    uv run python agent.py console --text   type to it
    uv run python agent.py console          talk to it through your mic
    uv run python agent.py dev              take real calls on your LiveKit number

The model handles the conversation. Every decision that matters (priority,
eligibility, availability, price) comes back from summit/ through the tools below.
"""

import asyncio
import inspect
import logging
import os
import re
import uuid
from collections.abc import AsyncIterable, Awaitable, Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    ModelSettings,
    RunContext,
    ToolError,
    TurnHandlingOptions,
    UserStateChangedEvent,
    cli,
    function_tool,
    inference,
    llm,
    room_io,
)
from livekit.agents.beta import EndCallTool
from livekit.plugins import krisp

from summit import config
from summit.backend import ActionRefused, CallSession, caller_turn_to_screen, close_abandoned_calls
from summit.call_metrics import CallMetrics
from summit.claims import booking_claims, callback_claims
from summit.notify import Notifier
from summit.speech import plain_speech
from summit.store import Store
from summit.triage import Facts

load_dotenv(".env.local")

logger = logging.getLogger("summit-air")

# Must match the agent name in the LiveKit dispatch rule for the phone number. A laptop
# worker should set AGENT_NAME=summit-air-dev so it never takes calls meant for the deploy.
AGENT_NAME = os.getenv("AGENT_NAME", "summit-air")
PROMPT_PATH = Path(__file__).parent / "prompts" / "system_prompt.md"


def load_prompt() -> str:
    """Read for every call, so a prompt edit reaches the next call without restarting the worker."""
    return PROMPT_PATH.read_text().strip()


CHECK_INS = ["Are you still there?", "Sorry, I can't hear you. If you're still there, just say something."]
SILENT_GOODBYE = "I'll let you go for now. If you still need us, call back any time. Goodbye."

Transfer = Callable[[str], Awaitable[None]]


def build_llm() -> llm.LLM:
    # Falls over to the second model if the first errors or is slow to start answering.
    return llm.FallbackAdapter(
        [inference.LLM("openai/gpt-4.1-mini"), inference.LLM("google/gemini-2.5-flash")],
        attempt_timeout=4.0,
    )


def instructions_for(call: CallSession) -> str:
    now = call.now()
    time_of_day = now.strftime("%I:%M %p").lstrip("0")
    if config.office_open(call.cfg, now):
        office = "The office is open."
    else:
        # Stress finding H12: told only "the office is closed", the model invented "we don't do
        # night service" before triage, and a caller with a real P1 might hang up.
        office = (
            "The office is closed, but urgent problems are still handled: find out what's wrong first "
            "and let the tools say when someone can come."
        )
    number, _ = call.plan_transfer()
    # H7: the model said "I'll connect you" before the transfer tool answered.
    transfer = (
        "A live transfer to the office is possible right now (transfer_to_human)."
        if number
        else "There's no live transfer to a person right now: if they want one, offer a callback from the office."
    )
    return f"{load_prompt()}\n\n## Right now\nIt's {now:%A}, {now:%B} {now.day}, {time_of_day}. {office} {transfer}"


class SummitAgent(Agent):
    def __init__(
        self, call: CallSession, transfer: Transfer | None = None, tools: list | None = None
    ) -> None:
        super().__init__(instructions=instructions_for(call), tools=tools or [])
        self.call = call
        self._transfer = transfer

    async def on_enter(self) -> None:
        # A fixed line, so the caller hears us immediately instead of waiting on the LLM.
        self.session.say(self.call.greeting(), allow_interruptions=False)

    def llm_node(
        self, chat_ctx: llm.ChatContext, tools: list[llm.Tool], model_settings: ModelSettings
    ) -> Any:
        """Every reply goes through here, in voice and in text mode, before the model runs.

        The caller's words are checked for gas and CO first. On a hit the call becomes
        P0 in the backend and the safety script is spoken as fixed text: the model
        doesn't decide whether it's an emergency, and it doesn't get to word the answer.
        """
        caller_words, said = caller_turn_to_screen(chat_ctx.items)
        self.call.agent_said = said
        if caller_words is not None:
            try:
                fixed = self.call.screen_caller_turn(caller_words, said_so_far=said)
            except Exception:
                # The screen must never take the call down; the model and triage still run.
                logger.exception("hazard screen failed")
                fixed = None
            if fixed:
                return _speak(fixed)
        else:
            # The turn right after a tool. A hazard only the model reported has just made the
            # call P0: the script is spoken as fixed text, as on the word-screen path.
            script = self.call.unsaid_safety_script(said)
            if script:
                return _speak(script)
            # Or a booking or a move just went through: the confirmation is spoken from the
            # booking record instead of worded by the model.
            confirmation = self.call.take_announcement()
            if confirmation:
                return _speak(confirmation)

        note = self.call.emergency_note()
        if note:
            chat_ctx = chat_ctx.copy()
            chat_ctx.add_message(role="system", content=note)
        return self._hold_back_false_claims(Agent.default.llm_node(self, chat_ctx, tools, model_settings))

    async def _hold_back_false_claims(self, stream: Any) -> AsyncIterable[Any]:
        """The model's reply, a sentence at a time, minus any sentence claiming a booking or a
        callback the records don't show. In a live run the agent read the details back, heard
        "yes", and said "you're booked" without calling book_appointment again. The hang-up check
        caught it, but the caller had already heard it. Now the sentence is never spoken: the
        caller hears that we're putting it through, and the model is sent back to the tool."""
        if inspect.isawaitable(stream):
            stream = await stream
        held: list[str] = []
        pending = ""

        def checked(sentence: str) -> str | None:
            sentence = plain_speech(sentence)  # no spoken asterisks or "dash" bullets
            if booking_claims(sentence) and not self.call.has_booking():
                held.append(sentence.strip())
                return None
            if callback_claims(sentence) and not self.call.callbacks:
                held.append(sentence.strip())
                return None
            return sentence

        async for chunk in stream:
            if isinstance(chunk, str):
                text = chunk
            elif isinstance(chunk, llm.ChatChunk) and chunk.delta and chunk.delta.content:
                text = chunk.delta.content
                if chunk.delta.tool_calls:
                    yield llm.ChatChunk(
                        id=chunk.id,
                        delta=llm.ChoiceDelta(role=chunk.delta.role, tool_calls=chunk.delta.tool_calls),
                        usage=chunk.usage,
                    )
            else:
                yield chunk  # tool calls, usage, flush markers: untouched
                continue
            pending += text
            # Speak each finished sentence as soon as it's checked.
            while match := re.search(r"[.!?](?:\s+|$)(?=\S)", pending):
                sentence, pending = pending[: match.end()], pending[match.end() :]
                if (ok := checked(sentence)) is not None:
                    yield ok
        if pending and (ok := checked(pending)) is not None:
            yield ok
        if held:
            self.call.note("held back an unbacked claim: " + " | ".join(held)[:200])
            logger.warning("held back unbacked claim: %s", held)
            yield " One moment while I put that through."
            try:
                self.session.generate_reply(
                    instructions=(
                        "You were about to tell the caller something was booked or arranged, but no tool has "
                        "confirmed it. Call book_appointment (or request_callback) now with the details they "
                        "confirmed, and say only what the tool returns."
                    )
                )
            except RuntimeError:
                pass  # not in a live session (tests)

    def _run(self, tool: str, args: dict[str, Any], action: Callable[[], str]) -> str:
        try:
            result = action()
        except ActionRefused as refused:
            self.call.log_tool(tool, args, str(refused), refused=True)
            raise ToolError(str(refused)) from None
        self.call.log_tool(tool, args, result)
        return result

    @function_tool
    async def lookup_customer(
        self,
        context: RunContext,
        confirmed_name: bool | None = None,
        phone: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        zip_code: str | None = None,
    ) -> str:
        """Verify who's calling. Nothing about an account can be shared until this succeeds.

        Args:
            confirmed_name: True if they said yes to the name in the greeting, False if they said no
                (report a "no" even if they don't want anything from the account).
            phone: The phone number on their account. Required if they said no to the greeting name.
            first_name: Their first name. Only needed when several people share a number.
            last_name: Their last name.
            zip_code: The ZIP code of the address on their account. Required if they said no to
                the greeting name.
        """
        args = dict(
            confirmed_name=confirmed_name,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            zip_code=zip_code,
        )
        return self._run("lookup_customer", args, lambda: self.call.lookup_customer(**args))

    @function_tool
    async def assess_situation(
        self,
        context: RunContext,
        description: str,
        gas_smell: bool | None = None,
        co_alarm_or_symptoms: bool | None = None,
        smoke_sparks_or_flames: bool | None = None,
        burning_smell_persistent: bool | None = None,
        dusty_smell_first_use: bool | None = None,
        no_heat: bool | None = None,
        no_cooling: bool | None = None,
        indoor_temp_f: int | None = None,
        vulnerable_occupant: bool | None = None,
        active_leak: bool | None = None,
        minor_drip: bool | None = None,
        request_type: str | None = None,
        urgent_reason: str | None = None,
    ) -> str:
        """Report what the caller has described. Call it as soon as you know the problem and
        again whenever you learn something new. Leave anything you don't know empty; never guess.
        The result is the priority: relay it, don't second-guess it.

        Args:
            description: The caller's own words about the problem, as close to verbatim as you
                can. Don't summarize, soften or correct them: the exact words are checked for
                safety hazards.
            gas_smell: They smell or smelled gas, rotten eggs, sulfur or skunk, or anything they
                think could be gas, now or earlier, even if it has stopped. If in doubt, true.
            co_alarm_or_symptoms: A carbon monoxide alarm is sounding or went off, or people at
                home have headaches, dizziness or nausea. A detector that only chirps now and
                then is usually a low battery: ask which it is.
            smoke_sparks_or_flames: Smoke, sparks or flames from any equipment.
            burning_smell_persistent: A burning or electrical smell that hasn't gone away.
            dusty_smell_first_use: A dusty smell the first time the heat ran this season.
            no_heat: The heat isn't working.
            no_cooling: The air conditioning isn't working.
            indoor_temp_f: The temperature inside right now, in Fahrenheit.
            vulnerable_occupant: Someone elderly, an infant, or someone with a medical need is at home.
            active_leak: Water is actively leaking.
            minor_drip: A small drip only.
            request_type: For non-problems: tune_up, estimate, or other.
            urgent_reason: Only if waiting a day or more would be unsafe for a reason none of the
                fields above capture: the specific fact, in a few words ("water dripping onto the
                electrical panel", "he's on oxygen and it's 88 inside"). How badly the caller wants
                someone, or that they call it an emergency, is not a reason and is ignored.
        """
        args = dict(
            description=description, gas_smell=gas_smell, co_alarm_or_symptoms=co_alarm_or_symptoms,
            smoke_sparks_or_flames=smoke_sparks_or_flames, burning_smell_persistent=burning_smell_persistent,
            dusty_smell_first_use=dusty_smell_first_use, no_heat=no_heat, no_cooling=no_cooling,
            indoor_temp_f=indoor_temp_f, vulnerable_occupant=vulnerable_occupant, active_leak=active_leak,
            minor_drip=minor_drip, request_type=request_type, urgent_reason=urgent_reason,
        )  # fmt: skip
        return self._run("assess_situation", args, lambda: self.call.assess_situation(Facts(**args)))

    @function_tool
    async def check_service_address(
        self,
        context: RunContext,
        zip_code: str | None = None,
        town: str | None = None,
        property_type: str | None = None,
        heat_from_building: bool | None = None,
    ) -> str:
        """Check the address where the work is: that we serve it and that it's a home.

        Args:
            zip_code: ZIP code of the service address.
            town: Town, neighborhood or borough, if they don't know the ZIP or the tool asks for it.
            property_type: What the property is, in their words: house, condo, two-family, restaurant...
            heat_from_building: For an apartment, condo or co-op: True if the heat or cooling comes from
                the building's own system (a boiler for the whole building), False if it's their own unit.
        """
        args = dict(
            zip_code=zip_code, town=town, property_type=property_type, heat_from_building=heat_from_building
        )
        return self._run("check_service_address", args, lambda: self.call.check_service_address(**args))

    @function_tool
    async def find_appointment_options(
        self,
        context: RunContext,
        reschedule_appointment_id: int | None = None,
        caller_says_member: bool | None = None,
    ) -> str:
        """Get arrival windows to offer. For a new visit, call it after assess_situation and
        check_service_address. To move an existing appointment, pass its id.

        Args:
            reschedule_appointment_id: The id of the appointment being moved, if rescheduling.
            caller_says_member: For a caller who isn't verified: their answer when asked whether
                they're already a member. Leave empty until you've asked.
        """
        args = dict(
            reschedule_appointment_id=reschedule_appointment_id, caller_says_member=caller_says_member
        )
        return self._run("find_appointment_options", args, lambda: self.call.find_appointment_options(**args))

    @function_tool
    async def book_appointment(
        self,
        context: RunContext,
        option_id: str,
        first_name: str,
        last_name: str,
        phone: str,
        address: str,
        zip_code: str,
        job_type: str,
        notes: str,
        phone_read_back_confirmed: bool,
        address_read_back_confirmed: bool,
        equipment: str | None = None,
        access_notes: str | None = None,
        name_read_back_confirmed: bool | None = None,
    ) -> str:
        """Book the window the caller chose. Before calling, read their first and last name
        back (ask them to spell it if it's unusual or you're unsure), the phone number back
        digit by digit and the full address back, and hear them confirm each.

        Args:
            option_id: The option_id of the window they picked.
            first_name: Caller's first name.
            last_name: Caller's last name.
            phone: Best number to reach them.
            address: Street address of the service location, with the town.
            zip_code: ZIP code of the service location.
            job_type: What the visit is for, e.g. "no heat", "AC repair", "tune-up".
            notes: Anything the technician should know: access, pets, equipment, what they've tried.
            phone_read_back_confirmed: You read the number back out loud and they said it's right.
                The backend checks that you actually said it.
            address_read_back_confirmed: You read the address back out loud and they said it's right.
                The backend checks that you actually said it.
            equipment: The system, if they know: furnace, boiler, heat pump, central AC, mini-split; gas,
                oil or electric; roughly how old.
            access_notes: How the technician gets in: apartment number, gate or door code, pets, parking.
            name_read_back_confirmed: You read their first and last name back (or spelled them)
                and they said it's right. Not needed for a verified customer. The backend checks
                that you actually said it.
        """
        args = dict(
            option_id=option_id, first_name=first_name, last_name=last_name, phone=phone,
            address=address, zip_code=zip_code, job_type=job_type, notes=notes,
            phone_read_back_confirmed=phone_read_back_confirmed,
            address_read_back_confirmed=address_read_back_confirmed,
            equipment=equipment, access_notes=access_notes,
            name_read_back_confirmed=name_read_back_confirmed,
        )  # fmt: skip
        return self._run("book_appointment", args, lambda: self.call.book_appointment(**args))

    @function_tool
    async def change_appointment(self, context: RunContext, appointment_id: int, option_id: str) -> str:
        """Move an existing appointment to a window offered by find_appointment_options.

        Args:
            appointment_id: The appointment being moved.
            option_id: The new window they picked.
        """
        args = dict(appointment_id=appointment_id, option_id=option_id)
        return self._run("change_appointment", args, lambda: self.call.change_appointment(**args))

    @function_tool
    async def cancel_appointment(self, context: RunContext, appointment_id: int) -> str:
        """Cancel one of a verified caller's upcoming appointments, once they've said they want it cancelled.

        Args:
            appointment_id: The appointment to cancel.
        """
        args = dict(appointment_id=appointment_id)
        return self._run("cancel_appointment", args, lambda: self.call.cancel_appointment(**args))

    @function_tool
    async def request_callback(
        self, context: RunContext, phone: str, reason: str, urgent: bool = False, name: str | None = None
    ) -> str:
        """Have the office call the caller back. Tell them exactly what the result says.

        Args:
            phone: The number to call back. Read it back to them first.
            reason: What the callback is about, for the office.
            urgent: True for urgent problems that couldn't be booked in time.
            name: Who to ask for.
        """
        args = dict(phone=phone, reason=reason, urgent=urgent, name=name)
        return self._run("request_callback", args, lambda: self.call.request_callback(**args))

    @function_tool
    async def transfer_to_human(self, context: RunContext, reason: str) -> str:
        """The caller wants to talk to a person.

        Args:
            reason: Why, in a few words.
        """
        number, message = self.call.plan_transfer()
        if number and self._transfer:
            # Let the model say "connecting you now" first; the transfer starts once that's been heard.
            context.speech_handle.add_done_callback(lambda _: asyncio.create_task(self._transfer_to(number)))
            message = "Tell the caller, in one short sentence, that you're connecting them to the office now."
        elif number:
            number, message = None, "Live transfer isn't available here. Offer a callback from the office."
        self.call.log_tool("transfer_to_human", {"reason": reason}, message)
        return message

    async def _transfer_to(self, number: str) -> None:
        assert self._transfer
        try:
            await self._transfer(number)
        except Exception:
            logger.exception("transfer to %s failed", number)
            self.session.generate_reply(instructions=self.call.transfer_failed())
            return
        self.call.note("transferred to the office")
        self.call.outcome = self.call.outcome or "transferred"
        self.call.save()

    @function_tool
    async def get_pricing(self, context: RunContext, item: str) -> str:
        """Look up a price before quoting one. Never quote a price that didn't come from here.

        Args:
            item: What they asked about, in their words.
        """
        args = dict(item=item)
        return self._run("get_pricing", args, lambda: self.call.get_pricing(**args))


async def _speak(text: str) -> AsyncIterable[str]:
    yield text


def transcript_of(history: llm.ChatContext) -> list[dict[str, str]]:
    lines = []
    for item in history.items:
        if item.type == "message" and item.role in ("user", "assistant") and item.text_content:
            lines.append({"role": item.role, "text": item.text_content})
        elif item.type == "function_call":
            lines.append({"role": "tool", "text": f"{item.name} {item.arguments}"})
    return lines


def watch_for_silence(
    session: AgentSession, call: CallSession, hang_up: Callable[[], Awaitable[None]]
) -> None:
    """Check in when the caller goes quiet, and hang up politely if they never come back.

    The session marks the user "away" after `user_away_timeout` seconds of silence
    and only flips back once they speak, so one task covers a whole quiet spell.
    """
    seconds = call.cfg["silence"]["check_in_seconds"]
    check_ins = CHECK_INS[: call.cfg["silence"]["max_check_ins"]]
    pending: asyncio.Task | None = None

    async def check_in() -> None:
        for line in check_ins:
            session.say(line)
            await asyncio.sleep(seconds)
        call.note("caller went silent")
        await session.say(SILENT_GOODBYE, allow_interruptions=False).wait_for_playout()
        await hang_up()

    @session.on("user_state_changed")
    def _on_user_state(event: UserStateChangedEvent) -> None:
        nonlocal pending
        if event.new_state == "away" and pending is None:
            pending = asyncio.create_task(check_in())
        elif event.new_state != "away" and pending is not None:
            pending.cancel()
            pending = None


server = AgentServer()


@server.rtc_session(agent_name=AGENT_NAME)
async def entrypoint(ctx: JobContext) -> None:
    cfg = config.load()
    store = Store()
    try:
        close_abandoned_calls(store, cfg, datetime.now(config.timezone(cfg)))
    except Exception:
        logger.exception("couldn't close abandoned calls")  # never worth failing a live call over
    call_id = uuid.uuid4().hex[:12]
    ctx.log_context_fields = {"room": ctx.room.name, "call_id": call_id}

    await ctx.connect()
    if ctx.is_fake_job():
        # Console mode has no phone line, so caller ID comes from the environment.
        participant = None
        caller_id = os.getenv("DEMO_CALLER_ID")
    else:
        participant = await ctx.wait_for_participant()
        caller_id = participant.attributes.get("sip.phoneNumber")

    call = CallSession(call_id, caller_id, store, cfg, notifier=Notifier(store))
    call.prefetch_caller()
    call.save()

    async def transfer(number: str) -> None:
        # Needs call transfer (SIP REFER) enabled on the number's trunk.
        assert participant is not None
        await ctx.transfer_sip_participant(participant, number)

    session = AgentSession(
        stt=inference.STT("deepgram/nova-3", language="en"),
        llm=build_llm(),
        tts=inference.TTS("cartesia/sonic-3"),
        turn_handling=TurnHandlingOptions(
            # Audio turn detection waits through "my number is 516... 555..." without
            # making short answers like "yes" feel laggy. Falls back to a local model.
            turn_detection=inference.TurnDetector(),
            preemptive_generation={"enabled": True},
        ),
        max_tool_steps=5,
        user_away_timeout=cfg["silence"]["check_in_seconds"],
    )

    call_metrics = CallMetrics()
    session.on("metrics_collected", lambda event: call_metrics.add(event.metrics))

    # The session's close event and the job's shutdown can both fire; finalize once.
    finished = False

    def finish() -> None:
        nonlocal finished
        if not finished:
            finished = True
            call.metrics = call_metrics.summary()
            logger.info("call metrics: %s", call.metrics)
            call.finalize(transcript_of(session.history))

    def save_transcript(_event: Any) -> None:
        if not finished:
            call.save(transcript=transcript_of(session.history))

    session.on("conversation_item_added", save_transcript)
    session.on("close", lambda _event: finish())

    async def on_shutdown() -> None:
        finish()
        store.close()

    async def hang_up() -> None:
        session.shutdown()
        await ctx.delete_room()  # disconnects the phone caller too

    ctx.add_shutdown_callback(on_shutdown)
    watch_for_silence(session, call, hang_up)

    # Krisp needs a real room; console mode just uses the mic as-is.
    noise_cancellation = None if ctx.is_fake_job() else krisp.voice_isolation_telephony()
    end_call = EndCallTool(
        ignore_on_enter=True,
        end_instructions="Say a short, warm goodbye.",
        extra_description="Only once the caller's need is handled and they've said goodbye.",
    )

    await session.start(
        agent=SummitAgent(call, transfer=transfer if participant else None, tools=[end_call]),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(noise_cancellation=noise_cancellation),
        ),
    )


if __name__ == "__main__":
    cli.run_app(server)
