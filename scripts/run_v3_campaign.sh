#!/usr/bin/env bash
# Suite v3 campaign: gate block (stops the campaign and writes gate-report.md if a gate check
# fails), then core C1a-C15 (all rep 1, then all rep 2), then micro M1-M14 (same order).
# ~19.5 h emulated, ~21-23 h wall. Run inside tmux.
#
#   bash scripts/run_v3_campaign.sh                          # new folder .runs/<ts>_v3
#   bash scripts/run_v3_campaign.sh .runs/<ts>_v3            # resume: finished runs are kept,
#                                                            # a half-written run is redone
#   TREE16_S=0.35 bash scripts/run_v3_campaign.sh [...]      # T-TREE16 at the fallback s
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-.venv/bin/python3}"
"$PY" -c 'import sys; assert sys.version_info >= (3, 12), sys.version' || { echo "need Python >= 3.12 at $PY"; exit 1; }
CAMPAIGN="${1:-.runs/$(date +%Y-%m-%d_%H%M)_v3}"
mkdir -p "$CAMPAIGN"
echo "campaign: $CAMPAIGN"
"$PY" scripts/v3_suite.py --run --campaign "$CAMPAIGN" ${TREE16_S:+--tree16-s "$TREE16_S"} 2>&1 | tee -a "$CAMPAIGN/run.log"
