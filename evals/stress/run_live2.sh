#!/bin/bash
# Resume after the rate-limited first attempt: paced, one call at a time, retries on 429.
#   bash ~/Desktop/summit-air-agent/evals/stress/run_live2.sh
set -u
cd "$(dirname "$0")/../.."
OUT=evals/stress/runs
rm -f "$OUT/DONE"
log() { echo "$(date '+%H:%M:%S') $*" | tee -a "$OUT/progress.log"; }
log "resume (paced)"
uv run python -m evals.stress.drive sparks_outdoor_unit gas_late_negated --repeat 3 --parallel 1 2>&1 | tee -a "$OUT/drive.txt" | grep --line-buffered -E "^(PASS|FAIL|ERROR|  rate)" | while read -r l; do log "$l"; done
uv run python -m evals.stress.drive --from fp_gas_bill --repeat 3 --parallel 1 2>&1 | tee -a "$OUT/drive.txt" | grep --line-buffered -E "^(PASS|FAIL|ERROR|  rate)" | while read -r l; do log "$l"; done
uv run python -m evals.stress.grader_audit > "$OUT/grader_audit.md" 2>&1; log "grader audit done"
uv run python -m evals.stress.run_evals_paced --repeat 3 > "$OUT/evals_repeat3.md" 2>&1; log "evals personas done"
uv run pytest evals -m eval -q -p no:cacheprovider > "$OUT/evals_behaviour.txt" 2>&1; log "behaviour evals: $(tail -1 $OUT/evals_behaviour.txt)"
bash evals/stress/scratch_broken.sh; log "broken agents: A $(tail -1 $OUT/broken_agent_A.txt) | B $(tail -1 $OUT/broken_agent_B.txt)"
log "DONE"; touch "$OUT/DONE"
