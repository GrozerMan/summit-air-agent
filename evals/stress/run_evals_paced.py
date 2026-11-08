"""evals.run with pacing and retry on the inference gateway's rate limit, plus a flakiness table.

    uv run python -m evals.stress.run_evals_paced --repeat 3 > evals/stress/runs/evals_repeat3.md

Uses evals.harness.run_persona unchanged; only the loop around it differs from evals.run.
"""

import argparse
import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(".env.local")

from evals.harness import run_persona  # noqa: E402
from evals.personas import BY_NAME, PERSONAS  # noqa: E402

OUT = Path(os.getenv("STRESS_RUNS", str(Path(__file__).parent / "runs"))) / "evals_repeat3"
LIMITED = ("429", "rate limit", "QuotaStatusExceeded")


async def one(persona, judge):
    for attempt in range(4):
        try:
            return await run_persona(persona, judge=judge)
        except Exception as e:  # noqa: BLE001
            if not any(m in str(e) or m in repr(e.__cause__) for m in LIMITED) or attempt == 3:
                raise
            await asyncio.sleep(60)


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("names", nargs="*")
    p.add_argument("--repeat", type=int, default=3)
    p.add_argument("--no-judge", action="store_true")
    a = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    personas = [BY_NAME[n] for n in a.names] if a.names else PERSONAS
    rows = []
    print("# evals.run personas, repeated\n\n| persona | " + " | ".join(f"run {i}" for i in range(1, a.repeat + 1)) + " | pass rate | failed checks |")
    print("|---|" + "---|" * (a.repeat + 2))
    for persona in personas:
        cells, fails = [], []
        for i in range(1, a.repeat + 1):
            try:
                r = await one(persona, not a.no_judge)
                (OUT / f"{persona.name}-{i}.json").write_text(json.dumps(r.to_dict(), indent=2))
                cells.append("PASS" if r.passed else "**FAIL**")
                fails += [f"{c.name}: {c.detail}" for c in [*r.checks, *([r.tone] if r.tone else [])] if not c.passed]
            except Exception as e:  # noqa: BLE001
                cells.append("ERROR")
                fails.append(f"error: {str(e)[:120]}")
            await asyncio.sleep(2)
        rate = sum(c == "PASS" for c in cells)
        print(f"| {persona.name} | " + " | ".join(cells) + f" | {rate}/{a.repeat} | " + "; ".join(fails).replace("|", "/")[:600] + " |", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
