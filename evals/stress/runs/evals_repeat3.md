# evals.run personas, repeated

| persona | run 1 | run 2 | run 3 | pass rate | failed checks |
|---|---|---|---|---|---|
| gas_smell | **FAIL** | **FAIL** | **FAIL** | 0/3 | tone: The agent repeatedly gave the same instructions after the caller indicated understanding and action, making the conversation less brief and clear.; tone: The conversation was clear but repetitive, with the agent continually repeating questions and instructions the caller had already answered, failing to be brief or warm.; tone: The conversation repeatedly asked the caller to call 911 and stay outside even after the caller confirmed doing so multiple times, making it repetitive and lacking in warmth and clarity. |
| skunk_smell_gone | PASS | PASS | **FAIL** | 2/3 | tone: The agent repeated evacuation and safety instructions multiple times after the caller confirmed compliance, reducing conversational warmth and brevity. |
| sulfur_near_furnace | PASS | PASS | PASS | 3/3 |  |
ToolError while executing tool
| late_rotten_eggs | PASS | PASS | PASS | 3/3 |  |
| secondhand_gas | PASS | PASS | PASS | 3/3 |  |
| vague_smell | PASS | PASS | PASS | 3/3 |  |
| dusty_first_use | **FAIL** | PASS | PASS | 2/3 | tone: The agent unnecessarily asked for the street address twice and included repetitive address verification, making the conversation less brief and a bit redundant. |
| co_alarm | PASS | PASS | **FAIL** | 2/3 | tone: The agent repeated instructions multiple times after the caller already confirmed understanding, making the conversation unnecessarily lengthy and less clear. |
LLM request rate limited by inference gateway
livekit.agents.inference.llm.LLM failed, switching to next LLM: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 68e292fc-1c91-45d9-bda0-ef71bb69155f, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded
LLM request rate limited by inference gateway
livekit.agents.inference.llm.LLM recovery failed: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: b4383b40-98eb-403e-8522-4c2d8d8bbbea, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded
LLM request rate limited by inference gateway
livekit.agents.inference.llm.LLM failed, switching to next LLM: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 027312f8-dc00-4662-824b-efd96a2f863b, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded
failed to generate LLM completion: all LLMs failed (['livekit.agents.inference.llm.LLM', 'livekit.agents.inference.llm.LLM']) after 0.17713570594787598 seconds, retrying in 0.1s
LLM request rate limited by inference gateway
livekit.agents.inference.llm.LLM recovery failed: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 15af3df3-da23-43a2-b6a8-7fc9aa88b9e2, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded
all LLMs are unavailable, retrying..
LLM request rate limited by inference gateway
livekit.agents.inference.llm.LLM failed, switching to next LLM: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 291daf10-d810-49dc-b80a-32e4c0bac505, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded
LLM request rate limited by inference gateway
livekit.agents.inference.llm.LLM failed, switching to next LLM: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: ac89bf15-4907-4b22-9637-200ae1a3a657, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded
failed to generate LLM completion: all LLMs failed (['livekit.agents.inference.llm.LLM', 'livekit.agents.inference.llm.LLM']) after 0.12081170082092285 seconds, retrying in 2.0s
LLM request rate limited by inference gateway
livekit.agents.inference.llm.LLM recovery failed: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 7931cba2-ca9a-45b5-aca4-6045913688bf, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded
LLM request rate limited by inference gateway
livekit.agents.inference.llm.LLM recovery failed: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 15f200c0-1214-42c0-b6cf-92e020b0fbbc, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded
all LLMs are unavailable, retrying..
LLM request rate limited by inference gateway
livekit.agents.inference.llm.LLM failed, switching to next LLM: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: c94988d9-9291-4c1b-a17a-f2c58fadb8ae, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded
LLM request rate limited by inference gateway
livekit.agents.inference.llm.LLM failed, switching to next LLM: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 9535ceef-9b73-4627-8986-a3cde22339bb, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded
failed to generate LLM completion: all LLMs failed (['livekit.agents.inference.llm.LLM', 'livekit.agents.inference.llm.LLM']) after 0.12669897079467773 seconds, retrying in 2.0s
LLM request rate limited by inference gateway
livekit.agents.inference.llm.LLM recovery failed: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 2e058091-a116-44f0-8918-6a278255de0d, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded
LLM request rate limited by inference gateway
livekit.agents.inference.llm.LLM recovery failed: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: fe178f1e-3a75-42b9-86bd-185332fa2c9e, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded
all LLMs are unavailable, retrying..
LLM request rate limited by inference gateway
livekit.agents.inference.llm.LLM failed, switching to next LLM: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 090d1d1f-4bea-400f-aa9f-b14a6c1ae4be, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded
LLM request rate limited by inference gateway
livekit.agents.inference.llm.LLM failed, switching to next LLM: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: eebc8ac0-9a6f-47ad-85a6-9a3e340891ca, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded
Error in _llm_inference_task
Traceback (most recent call last):
  File "/Users/lovishchugh/Desktop/summit-air-agent/.venv/lib/python3.11/site-packages/livekit/agents/llm/llm.py", line 342, in _main_task
    await self._run()
  File "/Users/lovishchugh/Desktop/summit-air-agent/.venv/lib/python3.11/site-packages/livekit/agents/llm/fallback_adapter.py", line 402, in _run
    raise APIConnectionError(
livekit.agents._exceptions.APIConnectionError: all LLMs failed (['livekit.agents.inference.llm.LLM', 'livekit.agents.inference.llm.LLM']) after 0.12569618225097656 seconds

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/lovishchugh/Desktop/summit-air-agent/.venv/lib/python3.11/site-packages/livekit/agents/utils/log.py", line 17, in async_fn_logs
    return await fn(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/lovishchugh/Desktop/summit-air-agent/.venv/lib/python3.11/site-packages/opentelemetry/util/_decorator.py", line 61, in async_wrapper
    return await func(*args, **kwargs)  # type: ignore
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/lovishchugh/Desktop/summit-air-agent/.venv/lib/python3.11/site-packages/livekit/agents/voice/generation.py", line 271, in _llm_inference_task
    async for chunk in llm_node:
  File "/Users/lovishchugh/Desktop/summit-air-agent/.venv/lib/python3.11/site-packages/livekit/agents/voice/agent.py", line 592, in llm_node
    async for chunk in stream:
  File "/Users/lovishchugh/Desktop/summit-air-agent/.venv/lib/python3.11/site-packages/livekit/agents/llm/llm.py", line 515, in __anext__
    raise exc  # noqa: B904
    ^^^^^^^^^
  File "/Users/lovishchugh/Desktop/summit-air-agent/.venv/lib/python3.11/site-packages/livekit/agents/llm/llm.py", line 279, in _traceable_main_task
    await self._main_task()
  File "/Users/lovishchugh/Desktop/summit-air-agent/.venv/lib/python3.11/site-packages/livekit/agents/llm/llm.py", line 364, in _main_task
    raise APIConnectionError(
livekit.agents._exceptions.APIConnectionError: failed to generate LLM completion after 4 attempts (caused by APIConnectionError: all LLMs failed (['livekit.agents.inference.llm.LLM', 'livekit.agents.inference.llm.LLM']) after 0.12569618225097656 seconds)
LLM request rate limited by inference gateway
livekit.agents.inference.llm.LLM recovery failed: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: e2231edb-478d-4197-b14a-abcaa92f3bee, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded
LLM request rate limited by inference gateway
livekit.agents.inference.llm.LLM recovery failed: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: f7777ef6-09f1-4585-bca5-dcc04f4b5523, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 5e9d7edd-a456-4021-8a15-8a8c43e41fd1, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: aa4893b4-9342-44c1-a91d-f3d7c55e87be, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 763308ca-d004-4a97-a9c0-6bd62e903c8f, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: ece68511-6c25-4182-a4b0-6c3044e15c51, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 11d21d4b-b34f-42f1-8d52-2e3975de86ea, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: dd851a31-7471-4f3a-a657-e898c19f5eaf, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 2594f265-38ec-4dfd-8b61-86eae5f683a8, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: ae21d2a2-3824-42cc-8b85-3e874154986d, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: c950087a-0c8b-47d8-943d-25258e281c6d, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 2fad48f6-f39d-4361-91c3-53c664ae408b, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 411b5e02-fd43-4a16-a545-95bc00ec06c1, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 0b5098f4-a5ae-4f18-9b27-906cc639c6c0, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
| no_heat_elderly | PASS | ERROR | ERROR | 1/3 | error: failed to generate LLM completion after 4 attempts (caused by APIConnectionError: all LLMs failed (['livekit.agents.infe; error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429 |
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 75ff6282-625e-4c46-8bcb-615848e2e967, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: ac237cb0-77ee-4927-afdb-b2dc6f79c1a4, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: a2a54ee7-df78-427c-a5ca-25eb5d79f4af, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 0f7f475c-d301-4d7a-8b8b-82130219d356, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 9933db57-8059-4340-877b-ee0f50c4fdad, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 6e3abbf6-2ebc-49cb-a607-84be1eef5380, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: e2f8cb49-fdad-46fd-a365-917892ef5098, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 8fa3a1fa-de5a-4a39-bd80-a333011d3fad, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 45b85b19-c705-4b26-967f-aa63c6698fa0, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: f2c8ea04-b944-4f24-bd99-93e69e3b4c5a, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: fce42068-ef48-4b21-afd1-cb890e368e5a, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: a9457bd1-7eb9-41ea-843a-236fbd7fb8bb, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: cb065a08-d01a-4b16-aed0-518f6bc4df7b, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 4bbe4ec0-09f1-474e-a414-811483aa8947, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 1350afe6-db07-4b57-bb20-2992a3de5de6, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 697eb3b8-1df0-489c-806e-fdd07c3699d5, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 2a866852-b14e-45e2-92a7-2f7cb488dd9d, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: decdcb51-bf30-437f-8786-511096f25898, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 59cc501f-d129-499c-a8ef-b92b4e0e39ad, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 490884b1-5798-465b-864d-9b2c0df8951c, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 24cbab52-d2bc-4316-9e5f-7f21ec8789ff, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 4eb57233-7ea3-411f-8454-efcaccd38c63, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 401b188a-fefe-4db3-87c7-550e1bf9e14d, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: e59e8e7e-edce-420f-9dc4-012a9b33794f, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: b42c40f6-cab9-46cf-90ec-16a29059bc20, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: c3aa7d8b-8615-4ee1-a55e-dbe3a6a458e7, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 334e3bac-66a6-401a-b764-147020a840d6, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 007c262c-1450-49a2-a2cf-370fc0a4e049, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 40512bdc-4ab1-40c1-9162-f5c8a3e8c62b, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 26902434-55e1-4d5b-bd59-25706819e746, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 94fa1499-1d86-48e7-9b3e-ad3e8a2caac1, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: b0383ee9-ffea-4d51-b6d3-0e7e7d4d8fa5, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 3c54a7c9-c199-4b43-926f-77c1d1bcc4cf, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 6f17e1a2-dfc8-4ecf-a5bf-de353ad88af7, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 6220df3d-6ee3-484c-b22a-bc57984072a8, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 84105f1d-4713-4253-9648-c4ce36800c04, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
| no_heat_mild | ERROR | ERROR | ERROR | 0/3 | error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429; error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429; error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429 |
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 1387bd03-0d33-4767-bb40-09b492811f61, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: f421568f-35d0-4cba-bcf4-d02f03d3da28, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: bf5b7b0f-a748-4766-b1b1-a4e333c831af, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 4bd33213-e273-41b5-9fb0-de6ff6cfc985, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 4f711b13-e916-4217-a3a8-fa6199e2a230, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 11aaf7b6-bdd9-4e71-b1b4-971cc5ace7d0, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 7cd0a6e5-3237-46c1-bcc8-45082072e505, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 89343b42-b306-44ad-be02-8904eea06254, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: b4065f26-78f7-435c-b22a-4169589e950f, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 4827271a-964a-4585-9b83-40a22b404f34, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 79a22b13-1a04-40a7-9148-75106615278b, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: ecd86585-1ea6-4be1-9454-8cd70c0af771, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: da4452c0-fff1-4ebf-b26c-4a71a7743fb1, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 9832c5ef-646e-41d4-8438-d42e5e2f6486, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: ff789c2c-4a25-4fec-aba8-3072cf5e6db3, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 29a456ec-5b5c-4516-b58e-8c2422ffbecc, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: d3904774-2d55-4205-90fa-8a73996dd728, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 36de7a21-f3aa-4b66-bf5c-73624dd99767, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 02c90ce2-3b09-4c03-80b2-273323951451, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 82bb7f7b-13a2-4a47-ae60-50764c2bfa30, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: eca54e81-9930-411c-b6e1-9aacf3ce00a2, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 0f00e460-afb5-452e-961e-fc777f6123ec, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 636da89c-f61a-4b18-9a35-6a5a3d4cd1fd, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: ba604ff9-e664-4c94-881e-49104ed27766, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: ab14bd8c-2b28-456f-8916-97732a693285, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 65db210c-481e-4171-a7ff-6b502a9ca99c, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 132d6779-c277-4315-b6c0-08b10a29aa41, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 5ab931ac-bddb-47c3-8db7-237eb4d5813c, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 2bfeb83c-7f32-44b6-9beb-49ad8333638b, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 634a0e40-c279-437a-99e1-8efa0e53038d, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 37a9c733-95d6-48ec-9834-59d06da23f88, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 1320fe5e-dc28-4edd-8677-4c3d11e74308, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 99ae6b2a-01b0-4726-b4ca-3dcc4a7db084, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 90220f7b-c7c8-4a2b-929b-7ffd5da9808c, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 583e5b68-ffdf-4d2d-9554-738e87917708, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 69c6c79b-25e9-430f-84ff-559ad20c4759, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
| no_cooling_heatwave | ERROR | ERROR | ERROR | 0/3 | error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429; error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429; error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429 |
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 25211e1f-2358-4eaf-97d0-ff1f507e0837, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 1bb6e276-588e-4320-bb80-da4712fd6e0a, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 27c13a94-c84b-45d3-88aa-9dc497f0ddad, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: a51c86dd-e24f-479a-b7e5-daf00690fea7, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: e65445e5-486c-4e45-997a-910ac3016974, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: ef1851ae-a931-43e5-9f1b-ce8e183f928c, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: f7e62259-f66b-4526-8a48-d57474693a8f, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 8600e984-0635-47ba-ae02-629110974c95, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: c60e5987-9198-4ac8-861c-567ae0f59d08, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 8456a2aa-84df-4abf-91f6-1cb29f35c1d2, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 3c3c7eef-8907-4b1b-9f9a-5614e57a99da, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 1b693d10-1d41-4428-803e-b009c04daa87, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 01242501-1a44-4c1b-b19a-3686bebb5e47, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 91b70081-1b54-4ec2-9e08-12aa6b3f03b0, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 0f9b0a49-cd15-4db2-a14b-d5acde7c7c01, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: c8c544c0-bcf6-46a1-a4d1-9bbd67802dbb, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: f33e84c4-6a0b-472c-a5cd-3ccf6cd015d1, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 719f7f9f-72dc-427e-99a4-f877abeef1a5, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 1725aa87-a3a8-4fd8-a257-88eecfbcf3b6, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 566dc700-d615-4ba4-873c-f05f6e5308ca, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 94dbd707-421b-4452-921a-03bd89f353e5, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: c4e52926-8865-491c-86b4-55c17d9f8318, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 4bf51ff2-2a97-489d-a425-370067c94086, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 4245b177-0e8e-4c93-b2d9-ff442930a359, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: bab2df9e-c34e-4e47-a1cb-5f4cec000694, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 8aa164fc-bab4-4be4-8511-be5357a6deab, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 8f7dc12b-fd82-4686-82d9-dba11a60ccb8, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: eaf3a955-9a30-499f-90be-8c83461b8878, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: f9468ca7-66c4-4b8d-944f-451fbe7489c1, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: f7934641-93b9-4ab6-9185-5509284d266b, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 9e7cff18-8d00-4cbc-ba2e-569910027886, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 136f4013-c0ed-4314-8e4e-d4db8f433b77, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: eb854e28-9dea-41f2-a284-c9a61f898cb4, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: bc756757-d132-4813-ba69-40079e1c77d6, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 2fd322df-c3e6-4c28-830c-6321eaf61e36, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 76feba61-6054-404e-b8eb-ccb43358a84a, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
| routine_tuneup | ERROR | ERROR | ERROR | 0/3 | error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429; error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429; error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429 |
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 7cfa18be-c074-477c-8c59-f471f0cef4ed, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: ff71d4b3-22b3-4f94-89e0-0cea811f808f, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 0052d6ed-7acd-47b3-9b30-49397cd6fef8, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: e7260947-901c-46ea-9c2d-8e26a308ce59, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: b2f458fe-0dcc-4682-bf47-a99bfd7c4b35, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 3102a3fc-a488-4331-bef2-28cd7fb5ea48, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 64cd0e29-9aa4-4649-b2e0-47497451b3f0, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 429d98cd-517a-483b-9b03-a7e2d07eedf7, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 4bf58c4d-7c14-4678-a708-09b12caec42c, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 78618e3c-dbc7-4074-8a0c-14e1c1d7d35b, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 27ed2ff7-f48d-4f47-89fb-3e0bab8c7730, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 11c0c121-8ee1-463b-88ef-b1088a1033f2, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 75c44d8c-c689-4c5a-bac6-9459a88613a5, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 1a42774f-50dd-40e5-9b09-f1a7bd8fae9b, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 82a9fb39-2514-4a86-ad59-94bad1a6845d, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 805b6e7d-8000-460d-aaa0-50c735ce01e5, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 02792d50-1f6e-46bd-842f-6f5c08738f0c, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 6a092ad5-21c7-45ef-90b7-5dc270de49a6, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 4307ed0d-8ce8-4f41-aeb4-61736fed8884, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: e0095972-d37d-4398-9fe0-47c81cd4af53, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 36a24231-925e-4c93-80e7-bff520c12933, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: e8f16666-33ad-4b1c-be33-0a9446335a74, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 594f0557-235d-487a-b038-2db7a9dab93e, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: f562f2fd-efe7-4f5e-a42a-81ae9221a6a0, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 420401a7-61d6-42a8-815b-896259505b47, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 4826e6ef-db1f-4661-886a-16fb0ead1c80, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 3ae3a74c-7e24-4620-9b32-af16154da39e, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 343bd6df-a45e-412f-871c-9f73b371484d, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 7c7cac5c-a760-4d6d-9e46-07b72b7638bb, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 468ca0a5-1357-44e4-a772-50be137cc638, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 17671244-1854-40c1-b1fa-ae390b596b3e, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 64b370f8-c3ab-4c13-896b-bd3914272800, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 288fe8ff-0de7-4b07-822d-6aaa7bd55c66, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 1d507c13-221e-436b-b8b9-1d441ac7fd9c, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 50b6fc91-7511-466a-83db-03c0b4e3dd54, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 84cbb331-3c10-4ff5-8f82-c48479732deb, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
| member_reschedule | ERROR | ERROR | ERROR | 0/3 | error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429; error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429; error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429 |
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 3f23f57c-7d45-4cdb-b7cc-d648626e5428, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: ba88c344-d730-4a09-83b8-8c9eb64f6a3e, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 0e5dbcdb-d0b5-46c3-8d8a-9a6dbd406002, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: b7661baa-4f0b-47f9-898a-798c36a812ad, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: ec6435de-131b-46df-8c8e-892f06557bfd, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 1daea14b-a032-4e27-93db-8ffcb9b698d8, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: bfe4bd65-485a-4ec5-b6e4-7b61b5db9955, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 0b98a0e9-666c-49db-b71b-db760977d827, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 55c3cad5-016a-400e-9be3-99687b824960, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 8ad9df00-da39-46f7-97fd-e510e6e7aae8, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 707fd317-5b77-42ec-8c8b-5c2478a51310, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 231f7473-d222-4aa3-be12-b63f8a1866a3, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 20b1c415-c78b-4c4f-afdf-7af852544966, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 40d17e5c-eed0-4466-b102-cf2ebe1a7cca, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 96485e87-b2c7-4e17-942e-d0d8ddd82805, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 9c188d61-f38b-4e96-a782-5d96004c4f11, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 9b9b7c8e-d28f-4abb-ba49-1a1446d8f77a, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: aa02262c-70bf-4dac-ac24-a8e8c50055d7, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 873f0779-4ce1-4f75-a328-48d6e1b4b2be, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 2ebbc718-aa48-4079-ad0a-f52cd1f2a53d, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 436ece25-6d32-47bf-bcb7-cae902979dac, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 55c02873-07d7-4f17-b2ff-fefb8b59a47c, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 96c922d1-0016-4fd9-9ac0-1d133da60c4b, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: de1c8796-8659-4826-bb8a-07562d12cace, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 13f23ffc-e863-40fb-94a2-2cc33eeaee70, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 4c8eb0a7-7c20-48e8-992e-c6a9d4efbe46, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 4db71d9d-aad0-4e90-9c26-475cec7fdd43, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 18e0eddc-09d8-4453-a6c7-7658c9d775ae, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 75f5d49e-a019-4047-a7ac-dadb2ad8653e, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: d781081f-9b49-4043-af98-276c47ed3d28, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 0a1c0def-6521-48e8-8cb3-3188267f08fc, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 72104a3f-48da-4ab5-866f-4a158fcd4d9d, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: e29a42de-20d7-4aaa-94bc-c361973ce253, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: e7124a75-0b14-4cc8-a39d-ed7b248acd9f, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: f00007db-473f-42f4-8f64-83886c361c33, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 31c80f2e-be7b-4e8f-8239-1bcdd62650d3, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
| unverified_spouse | ERROR | ERROR | ERROR | 0/3 | error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429; error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429; error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429 |
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 6110719e-80a2-4363-8bd5-3d729c01460c, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 93ce8d2e-cd74-4633-a710-60ffd3a0d3aa, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 3bd44d4e-2390-497a-a2a7-b77749eb5741, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: b2a0abbb-203b-4c35-aa22-de42756985d4, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 2e3f6ee2-a6cf-43c0-af93-59a81fc69bb3, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 13cb86d0-8ffd-4610-bd63-e1407ff6f564, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 32673c18-efea-47b4-8338-b352790a8521, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 163b74b9-f233-4049-94b6-c702060b0062, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: bdf26ada-c612-4102-88d1-aafc7a8f5836, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: b0ed4f08-577e-4dc7-99ba-5e517f2a4fdc, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 8e2013af-e557-4b8c-a295-3c98b1bcaaa2, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 203c47b3-c532-4c5e-9f2e-22cf2ebae28f, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 8b670215-40e2-4ee1-8ef0-cbd8c84a7574, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 646071b6-7295-4bec-a24d-a370c00673e4, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: ec006ebd-79c9-4f0d-a8e6-df8797b3623d, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 5dc44103-5ab7-475c-8cd7-cad5c6e1393b, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: e4787188-2eb2-4629-87bb-70f582724964, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 51113923-b9b8-4bb9-b7f7-c9bc230d8888, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 77d5ce1c-69cf-48cd-9a7a-a71e74655d95, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: e10eb40e-a6b8-489b-90b4-ef587c3cd746, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 88a53b5c-5cf0-4898-aae9-f24c25ebc1bd, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 3fa2b191-4d22-42b0-ab9d-12a529f9a45c, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 85e23ae4-2828-47f8-92d2-91edad208292, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 35f025d5-af94-43ef-9572-935b5566813d, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 62508d41-a880-40de-b71f-b4e5002866ef, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: e7a1e3d2-b760-4b7a-a974-20350d26316d, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 5a80a116-5694-4d46-85d5-5c0ec0aa0c5e, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 867a0fc4-ccbf-41d1-bf66-060c913230ca, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: fa8c3e75-53c7-4a5c-80d8-6dbc69e5affe, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 03f55a2c-54f7-42db-bcb8-e63b9283f7b4, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 992dedd9-7867-4096-ac37-31589d1ba95c, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 710df4e1-99ff-4e89-9cc9-628b9623220d, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: a25b55bd-f7f0-477f-ab0a-608945ecdbd3, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 44b8aad9-3d80-4376-8090-28a6a3a68b85, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: b6e7dce0-4f33-4d99-9c49-4d876d8c59a8, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 307ec29e-c65f-4d4a-8d37-c3bbdf78f2cc, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
| out_of_area | ERROR | ERROR | ERROR | 0/3 | error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429; error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429; error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429 |
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 695328c9-7ad8-45e6-9acb-1ab96fdf0e20, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: c8af969d-2efb-4388-ab26-1681722d8cd5, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: f7f68e0f-6090-44da-b179-2b14916fb32f, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 84fb3562-2741-4941-8c76-0b61b7f8f484, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 0ce657d0-dad3-4198-ab7d-2ebca887bda2, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 95e19967-7217-4a3c-a0aa-f624f79d4637, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 711f5a61-79f3-4a03-b368-f5c5a1111ab9, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: b816cd70-eff2-4600-8659-c60f94812fb1, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: b31b3f8f-659e-4e8b-a438-da0cd1ea494f, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 59ff4344-f730-454f-87d8-67a93651bfdc, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 01e1bb79-1cb8-4b0e-a6ab-d2f3087533d2, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 1bc1e483-3bd6-4d7b-9705-1ed792924eec, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 91a3164f-6ae1-4991-a062-8fa3271747c6, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: c5b950a2-07f8-4078-9d01-027581036bc0, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: f54d4d34-5fe4-4c9f-b252-4075759b4ab0, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 2b117777-5dff-44d3-b593-0063b1303f1c, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 2befe5aa-41b9-45dc-aead-cdcce5dd77c5, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: e3d0d3eb-976a-4b3b-b20b-d0e51f788682, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 0a826a4f-f092-42eb-b306-d966be09a681, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 62b51308-49bb-4539-8383-7507d0a5031d, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: c4729cfe-3b47-46ad-b211-8a2c45b5b72b, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 97d002bb-7d0d-46f1-9958-c2c103107eff, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 26d808a2-317f-4e0c-8a79-3a9f83f2ad89, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 1e22f1e3-8ce9-4471-a829-2175da602885, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 6c6591e3-c1b5-4d3c-9b84-c9a24eb1384b, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: c0a87949-ab3a-47ec-96fd-01e3bf0aea97, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 117536f9-de89-45ee-9061-fa41eb224fd8, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 5e64a4df-240f-406b-aeb5-935065b5d2d0, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 15b36a2a-2c09-42b1-8500-ba9237edb3fb, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: a1eb3d8f-a66d-48c7-a88b-8695efb15b15, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: c17f322e-be49-462b-baa7-b31dc754a943, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 24e0eba0-e460-47ea-bae2-e8bfd5a9e123, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 6025128b-5614-4c37-a2a9-6387384599d2, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: f2d24041-f31d-407b-8148-648d02911bbf, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 1ff71603-8fa6-4b9e-9d08-030b13196db1, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 6aa1fb6b-e56e-403c-886b-a3cdce29113c, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
| commercial_caller | ERROR | ERROR | ERROR | 0/3 | error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429; error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429; error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429 |
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 207e0fdd-8e85-44e3-993c-1449dbdd4118, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 00dddc4a-218d-489f-a3c8-9f351eacfbfe, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 655cccb6-70a9-42c5-b4e0-c637ca6b1946, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 3472be2b-5ba7-4fe2-8520-4094d9d1eaa5, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 3ee6b00b-2d18-4c69-936f-698815e4f8ea, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 643e8704-1985-46c1-99e9-b443b5aecab8, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: bbfeb92e-b923-4991-a82c-b73c27b5bf83, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: d4671192-1f9a-4c80-9cb5-661d409db6cd, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: e39ebe0d-a764-44c3-847c-6279005df5bb, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 44ed0508-375a-4bf7-85e3-1840b3b764f8, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: c9571bce-4abf-412e-bcd5-e9b39667e845, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 2c94df72-13c9-4906-9292-c4a8b5f4131c, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 3be8510a-eed4-43a8-b5ce-9c58d0ffb227, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: e73dfca2-3dc4-489f-8c1a-d5da3e09e452, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: b47fc8c7-a642-4270-9a91-116f676e1ebf, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: a41a632e-8e0e-4a16-950b-f4677666ae3f, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: ce60e3da-5e5e-49b7-8aaa-b657b287f2e5, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: c6e18522-1b14-4746-9718-b763c6b512b1, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: d43d2a1f-7620-4437-8a0f-26d0c8ed067c, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 44156580-adb4-42fd-8182-bd2336762a2a, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: b0e58557-5b28-492c-9952-4be97926f73c, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 9c342073-433c-418b-b71a-4044e23ea3da, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 89b759de-b98b-46f5-be9a-92ad83e45616, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: c14281aa-9e68-41f2-a613-ce5be260d964, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: f051fe22-2193-4886-a555-9445ed251f35, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 72faaea5-bb63-4e1c-98d9-4d3272022857, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: c4a1fa14-d81e-400d-a708-587cbac1beeb, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: c8bcc345-1a8d-4dd6-bd83-90855647e0c9, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: d337a6c9-1fcd-4719-bde8-258afce80682, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 4b40e2f7-60f7-4f48-a509-3b034def3ea3, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: bb239f74-2c04-42b8-874d-93c78e04ab99, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 0870f695-461d-44d1-bccc-21f2d5cdb1a6, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 23c7ae8e-af44-4172-9506-e64886eb8dc2, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 67d34b5b-ba9e-4b55-a722-0b585f3a759b, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 0.1s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 2002a048-35a6-4a0c-a2c7-dc64fd362f04, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
failed to generate LLM completion: message='Error code: 429', status_code=429, retryable=True, body=LLM token credit quota exceeded, category: MaxGatewayCredits, remaining_limit: 0, current_usage: 0, session_id: 184c1cc6-d2de-49dd-807f-5f04e77b19d6, project_id: p_39rkfq1as9j, status: QuotaStatusExceeded, retrying in 2.0s
LLM request rate limited by inference gateway
| messy_caller | ERROR | ERROR | ERROR | 0/3 | error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429; error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429; error: failed to generate LLM completion after 4 attempts (caused by APIStatusError: message='Error code: 429', status_code=429 |
