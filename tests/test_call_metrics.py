from types import SimpleNamespace as M

from summit.call_metrics import CallMetrics


def test_latency_is_end_of_turn_plus_first_token_plus_first_audio():
    metrics = CallMetrics()
    metrics.add(M(type="eou_metrics", speech_id="a", end_of_utterance_delay=0.5))
    metrics.add(M(type="llm_metrics", speech_id="a", ttft=0.4, prompt_tokens=900, completion_tokens=20))
    metrics.add(M(type="tts_metrics", speech_id="a", ttfb=0.2, characters_count=60, audio_duration=3.0))
    # A fixed-text turn (the safety script): no model step.
    metrics.add(M(type="eou_metrics", speech_id="b", end_of_utterance_delay=0.6))
    metrics.add(M(type="tts_metrics", speech_id="b", ttfb=0.3, characters_count=200, audio_duration=12.0))
    metrics.add(M(type="stt_metrics", speech_id=None, audio_duration=30.0))

    assert [round(x, 2) for x in sorted(metrics.latencies())] == [0.9, 1.1]
    summary = metrics.summary()
    assert summary["turns_measured"] == 2 and summary["latency_max_s"] == 1.1
    assert summary["llm_prompt_tokens"] == 900 and summary["tts_characters"] == 260
    assert summary["stt_audio_seconds"] == 30.0


def test_a_call_with_no_metrics_still_summarizes():
    assert CallMetrics().summary()["turns_measured"] == 0
