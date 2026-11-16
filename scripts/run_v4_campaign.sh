#!/usr/bin/env bash
# Suite v4 campaign K1, K2 or K3 (spec 6): gate block first (one CALM per topology of the
# campaign and one run per new stimulus; stops with exit 3 and gate-report.md on a failed
# check), then the campaign, all seed 1 in block order, then seed 2, and so on. Run in tmux.
#
#   NMAX=<n> bash scripts/run_v4_campaign.sh K1        # n_max from <smoke>/nmax.json
#   bash scripts/run_v4_campaign.sh K2
#   bash scripts/run_v4_campaign.sh K3
#   bash scripts/run_v4_campaign.sh K2 .runs/<ts>_v4-K2   # resume: finished runs kept, a passed gate not rerun
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-.venv/bin/python3}"
"$PY" -c 'import sys; assert sys.version_info >= (3, 12), sys.version' || { echo "need Python >= 3.12 at $PY"; exit 1; }
SET="${1:?usage: run_v4_campaign.sh K1|K2|K3 [campaign folder]}"
if [ "$SET" = K1 ] && [ -z "${NMAX:-}" ]; then echo "K1 needs NMAX=<n> (from the smoke's nmax.json)"; exit 1; fi
CAMPAIGN="${2:-.runs/$(date +%Y-%m-%d_%H%M)_v4-$SET}"
mkdir -p "$CAMPAIGN"
echo "campaign $SET: $CAMPAIGN"
"$PY" scripts/v4_suite.py --set "$SET" --run --campaign "$CAMPAIGN" ${NMAX:+--nmax "$NMAX"} 2>&1 | tee -a "$CAMPAIGN/run.log"
