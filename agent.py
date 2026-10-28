from dotenv import load_dotenv
from livekit.agents import Agent, AgentServer, AgentSession, JobContext, cli, inference

load_dotenv(".env.local")

INSTRUCTIONS = """\
You answer the phone for Summit Air, a residential heating and cooling company.
This is a phone call: keep replies to a sentence or two and ask one question at a time.
"""

GREETING = "Thanks for calling Summit Air, how can I help?"

server = AgentServer()


class SummitAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=INSTRUCTIONS)

    async def on_enter(self) -> None:
        # Spoken directly rather than generated, so the caller hears us with no LLM delay.
        self.session.say(GREETING)


# agent_name has to match the dispatch rule on the LiveKit phone number.
@server.rtc_session(agent_name="summit-air")
async def entrypoint(ctx: JobContext) -> None:
    session = AgentSession(
        stt=inference.STT(model="deepgram/nova-3"),
        llm=inference.LLM(model="openai/gpt-4.1-mini"),
        tts=inference.TTS(model="cartesia/sonic-3"),
    )
    await session.start(agent=SummitAgent(), room=ctx.room)
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)
