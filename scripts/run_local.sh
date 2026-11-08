#!/bin/bash
# Take real calls from this laptop for as long as it runs:
#   bash scripts/run_local.sh
# Keeps the Mac awake (caffeinate) and restarts the agent if it exits or crashes.
# Leave the lid open and the charger in; stop with Ctrl+C twice.
cd "$(dirname "$0")/.."
mkdir -p data
while true; do
  echo "$(date '+%F %T') starting agent" | tee -a data/agent.log
  caffeinate -dimsu uv run python agent.py start 2>&1 | tee -a data/agent.log
  echo "$(date '+%F %T') agent exited; restarting in 5s" | tee -a data/agent.log
  sleep 5
done
