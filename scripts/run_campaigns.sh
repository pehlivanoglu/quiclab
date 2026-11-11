#!/usr/bin/env bash
# Run every pending campaign back to back (start it in tmux):
#   1. unit tests (abort if they fail)
#   2. detector: new event scenarios on the base topology (det_matrix, ~5-6 h)
#   3. detector: split / serial topology (det_matrix --topology split, ~1.5-2 h)
#   4. grouping: K1, K2, K3, K5, K6 (grouping_campaign.py, ~10.5 h + setup)
# A failed campaign is logged and the next one still starts. Resume a cut
# campaign by hand: det_matrix.py / grouping_campaign.py --campaign <dir> --skip-existing.
#
#   scripts/run_campaigns.sh            # all steps
#   scripts/run_campaigns.sh 3          # start at step 3
set -uo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
START=${1:-1}
LOG=.runs/$(date +%Y-%m-%d_%H%M)_all-campaigns.log
mkdir -p .runs
declare -a SUMMARY=()

step() {  # step <n> <name> <command...>
    local n=$1 name=$2; shift 2
    (( n < START )) && return 0
    echo "=== [$n] $name: $(date '+%F %T')  $*" | tee -a "$LOG"
    "$@" 2>&1 | tee -a "$LOG"
    local rc=${PIPESTATUS[0]}
    SUMMARY+=("[$n] $name: exit $rc ($(date '+%F %T'))")
    echo "=== [$n] $name finished: exit $rc" | tee -a "$LOG"
    return "$rc"
}

step 1 unit-tests $PY -m pytest -q tests/unit || { echo "unit tests failed, nothing started" | tee -a "$LOG"; exit 1; }

step 2 detector-newscn $PY scripts/det_matrix.py --reps 2 --name newscn-v2 \
    --scenarios calm030,calm065,calm090,calmcbr090,randloss,revdelay,burstlong,burstcapshallow,burstcapdeep,onoff

step 3 detector-split $PY scripts/det_matrix.py --topology split --reps 2 --name split-v1 \
    --scenarios splitcap,splitudp

step 4 grouping $PY scripts/grouping_campaign.py --ks K1,K2,K3,K5,K6 --reps 3

echo | tee -a "$LOG"
printf '%s\n' "${SUMMARY[@]}" | tee -a "$LOG"
echo "log: $LOG"
