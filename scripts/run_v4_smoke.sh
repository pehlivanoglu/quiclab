#!/usr/bin/env bash
# Suite v4 smoke test (spec 7.2): a 60 s CALM per new topology, the n_max search (90 s CALM
# on T-LEAFn at n 24 / 32 / 40), a 90 s run per new stimulus (persist, shorttcp, pause), the
# 45 s FB-COLD run and a 90 s BG-ONOFF run; pfifo, seed 1. Then v3 gate checks 1-4 and 6 plus
# the v4 checks (T-HAYES path, pause window, salvo connections) -> <folder>/smoke-report.md,
# and <folder>/nmax.json (n_max for campaign K1). ~29 min of emulation, ~35-40 min wall.
#
#   bash scripts/run_v4_smoke.sh                     # new folder .runs/<ts>_v4-smoke
#   bash scripts/run_v4_smoke.sh .runs/<ts>_v4-smoke # resume (finished runs are kept)
#   ONLY=g-shorttcp,onoff,fbcold bash scripts/run_v4_smoke.sh   # only these runs (substrings), new folder
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-.venv/bin/python3}"
"$PY" -c 'import sys; assert sys.version_info >= (3, 12), sys.version' || { echo "need Python >= 3.12 at $PY"; exit 1; }
CAMPAIGN="${1:-.runs/$(date +%Y-%m-%d_%H%M)_v4-smoke}"
mkdir -p "$CAMPAIGN"
echo "smoke: $CAMPAIGN"
"$PY" scripts/v4_suite.py --smoke --run --campaign "$CAMPAIGN" ${ONLY:+--only "$ONLY"} 2>&1 | tee -a "$CAMPAIGN/run.log"
