#!/usr/bin/env bash
# One short test run: base calm065, pfifo, synchronized phases, rep 1 (120 s of emulation,
# about 2-3 min wall). Own folder (.runs/<ts>_try-sync), so nothing mixes with the campaigns.
#
#   bash scripts/run_one_try.sh
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-.venv/bin/python3}"
"$PY" -c 'import sys; assert sys.version_info >= (3, 12), sys.version' || { echo "need Python >= 3.12 at $PY"; exit 1; }
CAMPAIGN=".runs/$(date +%Y-%m-%d_%H%M)_try-sync"
mkdir -p "$CAMPAIGN"
echo "campaign: $CAMPAIGN"
"$PY" scripts/grouping_campaign.py --campaign "$CAMPAIGN" --phase sync --skip-report \
  --ks G0 --aqms pfifo --reps 1 --only grp-calm065-pfifo-r1 2>&1 | tee "$CAMPAIGN/run.log"
