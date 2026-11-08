"""How fast the agent answered, and how much speech and model it used, per call.

LiveKit reports metrics per component; this folds them into one summary that goes
into the call record, so the office (and the owner asking "what does a call cost?")
can see response times and usage without opening LiveKit's console.

Response latency for a turn is the usual voice-agent measure: the end-of-turn delay
(the caller stops talking until we decide they're done) plus the model's time to first
token plus the voice's time to first audio. Turns spoken from fixed text have no model
step, so theirs is shorter.
"""

from collections import defaultdict
from statistics import median
from typing import Any


class CallMetrics:
    def __init__(self) -> None:
        self._turns: dict[str, dict[str, float]] = defaultdict(dict)
        self.llm_prompt_tokens = 0
        self.llm_completion_tokens = 0
        self.stt_audio_seconds = 0.0
        self.tts_characters = 0
        self.tts_audio_seconds = 0.0

    def add(self, metrics: Any) -> None:
        """Takes LiveKit's metrics objects; duck-typed on their `type` field."""
        kind = getattr(metrics, "type", None)
        speech = getattr(metrics, "speech_id", None)
        if kind == "eou_metrics" and speech:
            self._turns[speech]["eou"] = metrics.end_of_utterance_delay
        elif kind == "llm_metrics":
            self.llm_prompt_tokens += metrics.prompt_tokens
            self.llm_completion_tokens += metrics.completion_tokens
            if speech and "ttft" not in self._turns[speech]:
                self._turns[speech]["ttft"] = metrics.ttft
        elif kind == "tts_metrics":
            self.tts_characters += metrics.characters_count
            self.tts_audio_seconds += metrics.audio_duration
            if speech and "ttfb" not in self._turns[speech]:
                self._turns[speech]["ttfb"] = metrics.ttfb
        elif kind == "stt_metrics":
            self.stt_audio_seconds += metrics.audio_duration

    def latencies(self) -> list[float]:
        """Seconds from the caller finishing to the agent's first audio, per answered turn."""
        return [
            t["eou"] + t.get("ttft", 0.0) + t["ttfb"]
            for t in self._turns.values()
            if "eou" in t and "ttfb" in t
        ]

    def summary(self) -> dict[str, Any]:
        latencies = sorted(self.latencies())
        result: dict[str, Any] = {
            "turns_measured": len(latencies),
            "llm_prompt_tokens": self.llm_prompt_tokens,
            "llm_completion_tokens": self.llm_completion_tokens,
            "stt_audio_seconds": round(self.stt_audio_seconds, 1),
            "tts_characters": self.tts_characters,
            "tts_audio_seconds": round(self.tts_audio_seconds, 1),
        }
        if latencies:
            p95 = latencies[min(len(latencies) - 1, round(0.95 * (len(latencies) - 1)))]
            result.update(
                latency_p50_s=round(median(latencies), 2),
                latency_p95_s=round(p95, 2),
                latency_max_s=round(latencies[-1], 2),
            )
        return result
