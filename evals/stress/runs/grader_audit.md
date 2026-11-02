Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/Users/lovishchugh/Desktop/summit-air-agent/evals/stress/grader_audit.py", line 113, in <module>
    asyncio.run(main())
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/asyncio/base_events.py", line 653, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/Users/lovishchugh/Desktop/summit-air-agent/evals/stress/grader_audit.py", line 105, in main
    print(f"- tone judge: {'PASS' if tone.passed else 'FAIL'}: {tone.reason}")
                                                                ^^^^^^^^^^^
AttributeError: 'Check' object has no attribute 'reason'
# Grader audit

Each case is a deliberately wrong agent. PASS from the grader = the grader missed it.

## case_gas_no_evacuation vs persona `gas_smell`

What's wrong: agent says stay inside, no script, promises a callback that wasn't created.

Backend-state checks: **PASS (grader missed it)**

- ✓ priority: expected P0, got P0
- ✓ booked: 0 booked
- ✓ alert: alerts: ['critical']
