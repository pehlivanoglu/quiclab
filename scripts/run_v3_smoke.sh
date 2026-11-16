#!/usr/bin/env bash
# Suite v3 smoke test (spec 8.8): one 60 s CALM per topology (base, split4, tree16, uneven,
# access, rev) and one 90 s S-BURST with a single surge, pfifo, rep 1; then gate checks
# 1-4 and 6 -> <folder>/smoke-report.md. About 10 min of emulation, ~15-20 min wall.
#
#   bash scripts/run_v3_smoke.sh                 # T-TREE16 at s 0.30
#   TREE16_S=0.35 bash scripts/run_v3_smoke.sh   # the spec's fallback if T-TREE16 fails health
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-.venv/bin/python3}"
"$PY" -c 'import sys; assert sys.version_info >= (3, 12), sys.version' || { echo "need Python >= 3.12 at $PY"; exit 1; }
CAMPAIGN=".runs/$(date +%Y-%m-%d_%H%M)_v3-smoke"
mkdir -p "$CAMPAIGN"
echo "smoke: $CAMPAIGN"
"$PY" scripts/v3_suite.py --smoke --run --campaign "$CAMPAIGN" ${TREE16_S:+--tree16-s "$TREE16_S"} 2>&1 | tee "$CAMPAIGN/run.log"
