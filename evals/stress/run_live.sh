#!/bin/bash
# The whole stress suite against the current code, paced one call at a time (LiveKit
# Inference caps requests per minute). Uses Inference credits; allow a few hours.
#   bash evals/stress/run_live.sh [output dir]        default: evals/stress/runs_latest
# Progress: tail -f <output dir>/progress.log
# Round 1 (the published REPORT.md) is in evals/stress/runs/; round 2 used runs_v2/.
set -u
cd "$(dirname "$0")/../.."
export STRESS_RUNS="${1:-evals/stress/runs_latest}"
OUT=$STRESS_RUNS
mkdir -p "$OUT"; rm -f "$OUT/DONE"
log() { echo "$(date '+%H:%M:%S') $*" | tee -a "$OUT/progress.log"; }
quiet() { grep --line-buffered -E "^(PASS|FAIL|ERROR|  rate)"; }
log "start (commit $(git rev-parse --short HEAD))"
uv run python -m evals.stress.drive gas_rotten_eggs t_noheat_58 --repeat 1 --parallel 1 > "$OUT/smoke.txt" 2>&1
if ! grep -q "^PASS  gas_rotten_eggs" "$OUT/smoke.txt"; then log "SMOKE TEST FAILED, see $OUT/smoke.txt"; exit 1; fi
log "smoke ok"
uv run pytest -q > "$OUT/pytest.txt" 2>&1; log "pytest: $(tail -1 "$OUT/pytest.txt")"
uv run python -m evals.stress.backend_attacks > "$OUT/backend_attacks.md" 2>&1; log "round-1 probes: $(sed -n 3p "$OUT/backend_attacks.md")"
uv run python -m evals.stress.backend_attacks_v2 > "$OUT/backend_attacks_v2.md" 2>&1; log "round-2 probes: $(sed -n 3p "$OUT/backend_attacks_v2.md")"
uv run python -m evals.stress.grader_audit > "$OUT/grader_audit.md" 2>&1; log "grader audit done"
uv run python -m evals.stress.drive --repeat 3 --parallel 1 2>&1 | tee -a "$OUT/drive.txt" | quiet | while read -r l; do log "$l"; done
uv run python -m evals.stress.run_evals_paced --repeat 3 > "$OUT/evals_repeat3.md" 2>&1; log "personas done"
uv run pytest evals -m eval -q -p no:cacheprovider > "$OUT/evals_behaviour.txt" 2>&1; log "behaviour evals: $(tail -1 "$OUT/evals_behaviour.txt")"
bash evals/stress/scratch_broken.sh; log "broken builds: A $(tail -1 "$OUT/broken_agent_A.txt") | B $(tail -1 "$OUT/broken_agent_B.txt")"
log "DONE"; touch "$OUT/DONE"
