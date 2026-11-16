#!/usr/bin/env bash
# Synchronized-keyframe mini campaign (2026-11-13): pfifo, 2 reps, phase 0 for every client.
# One scenario at a time, both reps before the next: base calm065 (rep 1 = check A), base
# burstcap, K1 hier, C1 burstlongsplit, K6 depth. No grouping report inside the campaign
# (--skip-report); the per-scenario reports are made afterwards from the run folders.
#
#   tmux new -s sync 'bash scripts/run_sync_mini.sh'          # start
#   bash scripts/run_sync_mini.sh .runs/<existing>_grp-sync    # resume (finished runs are kept)
set -euo pipefail
cd "$(dirname "$0")/.."
# The repo's venv (Python 3.12, pandas, quiclab); a different python3 on PATH broke the first start.
PY="${PY:-.venv/bin/python3}"
"$PY" -c 'import sys; assert sys.version_info >= (3, 12), sys.version' || { echo "need Python >= 3.12 at $PY"; exit 1; }
CAMPAIGN="${1:-.runs/$(date +%Y-%m-%d_%H%M)_grp-sync}"
mkdir -p "$CAMPAIGN"
LOG="$CAMPAIGN/run.log"
echo "campaign: $CAMPAIGN (log: $LOG)"
for spec in "G0 calm065-pfifo" "M1 burstcap-pfifo" "K1 hier-pfifo" "C1 burstlongsplit-pfifo" "K6 depth-pfifo"; do
  set -- $spec
  echo "### $(date '+%F %T') $1 $2" | tee -a "$LOG"
  "$PY" scripts/grouping_campaign.py --campaign "$CAMPAIGN" --phase sync --skip-report --skip-existing \
    --reps 2 --ks "$1" --only "$2" 2>&1 | tee -a "$LOG"
  echo "### $(date '+%F %T') $1 $2 done" | tee -a "$LOG"
done
echo "### $(date '+%F %T') campaign done" | tee -a "$LOG"
