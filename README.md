# Summit Air phone agent

Inbound phone agent for Summit Air, a residential HVAC company, built on
[LiveKit Agents](https://docs.livekit.io/agents/).

## Setup

```bash
brew install uv livekit-cli
uv sync
cp .env.example .env.local
uv run python agent.py download-files
```

Fill in `.env.local` with your LiveKit Cloud project's URL, API key and secret
(or run `lk cloud auth && lk app env -w`). Speech, LLM and TTS go through
LiveKit Inference, so no other API keys are needed.

## Running

```bash
uv run python agent.py console --text   # type to the agent
uv run python agent.py console          # talk through your mic
uv run python agent.py dev              # take real calls on your LiveKit number
```

## Tests

```bash
uv run pytest
```
