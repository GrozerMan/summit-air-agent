#!/bin/bash
# Everything that needs the live model, in one go. Run from anywhere:
#   bash ~/Desktop/summit-air-agent/evals/stress/run_live.sh
# Progress: tail -f evals/stress/runs/progress.log      (~60-90 min; uses LiveKit Inference credits)
set -u
cd "$(dirname "$0")/../.."
OUT=evals/stress/runs
mkdir -p "$OUT"
rm -f "$OUT/DONE"
log() { echo "$(date '+%H:%M:%S') $*" | tee -a "$OUT/progress.log"; }
log "start"
uv run python -m evals.stress.drive gas_rotten_eggs t_noheat_58 --repeat 1 > "$OUT/smoke.txt" 2>&1
if grep -q "Traceback\|no_crash" "$OUT/smoke.txt" "$OUT"/gas_rotten_eggs.md 2>/dev/null; then log "SMOKE TEST FAILED, see $OUT/smoke.txt"; exit 1; fi
log "smoke ok: $(cat $OUT/smoke.txt | tr '\n' ' ')"
uv run pytest -q > "$OUT/pytest.txt" 2>&1; log "pytest: $(tail -1 $OUT/pytest.txt)"
uv run pytest -q --collect-only > "$OUT/pytest_collect.txt" 2>&1
uv run python -m evals.stress.backend_attacks > "$OUT/backend_attacks_mac.md" 2>&1; log "backend attacks: $(sed -n 3p $OUT/backend_attacks_mac.md)"
uv run python -m evals.stress.grader_audit > "$OUT/grader_audit.md" 2>&1; log "grader audit done"
uv run python -m evals.stress.drive --repeat 3 --parallel 3 2>&1 | tee "$OUT/drive.txt" | while read -r l; do log "$l"; done
uv run python -m evals.run --repeat 3 > "$OUT/evals_repeat3.txt" 2>&1; log "evals.run: $(tail -1 $OUT/evals_repeat3.txt)"
uv run pytest evals -m eval -q -p no:cacheprovider > "$OUT/evals_behaviour.txt" 2>&1; log "behaviour evals: $(tail -1 $OUT/evals_behaviour.txt)"
bash evals/stress/scratch_broken.sh; log "broken agents: A $(tail -1 $OUT/broken_agent_A.txt) | B $(tail -1 $OUT/broken_agent_B.txt)"
log "DONE"; touch "$OUT/DONE"
