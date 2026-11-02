"""Simulated end-to-end calls. Needs LiveKit credentials in .env.local.

    uv run python -m evals.run                                 every persona once
    uv run python -m evals.run gas_smell messy_caller --repeat 3

Transcripts and grades are written to evals/results/.
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from evals.harness import run_persona
from evals.personas import BY_NAME, PERSONAS

RESULTS = Path(__file__).parent / "results"


async def main() -> int:
    parser = argparse.ArgumentParser(description="Run simulated callers against the agent.")
    parser.add_argument("names", nargs="*", help=f"personas to run (default: all): {', '.join(BY_NAME)}")
    parser.add_argument("--repeat", type=int, default=1, help="runs per persona; LLM calls vary")
    parser.add_argument("--no-judge", action="store_true", help="skip the tone judge")
    args = parser.parse_args()
    unknown = [n for n in args.names if n not in BY_NAME]
    if unknown:
        parser.error(f"unknown persona {', '.join(unknown)}")

    load_dotenv(".env.local")
    personas = [BY_NAME[n] for n in args.names] if args.names else PERSONAS
    run_dir = RESULTS / datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)

    failures = 0
    for persona in personas:
        for attempt in range(1, args.repeat + 1):
            result = await run_persona(persona, judge=not args.no_judge)
            (run_dir / f"{persona.name}-{attempt}.json").write_text(json.dumps(result.to_dict(), indent=2))
            failures += not result.passed

            status = "PASS" if result.passed else "FAIL"
            print(f"{status}  {persona.name} #{attempt}")
            for check in [*result.checks, *([result.tone] if result.tone else [])]:
                if not check.passed:
                    print(f"      ✗ {check.name}: {check.detail}")

    total = len(personas) * args.repeat
    print(f"\n{total - failures}/{total} passed. Transcripts in {run_dir}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
