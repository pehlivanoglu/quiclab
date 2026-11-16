#!/usr/bin/env bash
# Suite v4 campaigns K1 -> K2 -> K3 in one go (run inside tmux), one after the other, never two at once.
# ~68 h emulated, ~75-80 h wall. The mini smoke is NOT run here: K3 needs its report to say PASS
# (default .runs/2026-11-16_0101_v4-smoke; another folder: SMOKE=<dir> bash scripts/run_v4_all.sh).
#
#   bash scripts/run_v4_all.sh                         # new chain: .runs/<ts>_v4-all/chain.env
#   bash scripts/run_v4_all.sh .runs/<ts>_v4-all       # resume: finished steps are skipped,
#                                                      # a started campaign resumes in its own folder
#
# Rules:
#   - Each campaign starts with its own gate. A failed gate stops that campaign (exit 3) and the chain
#     moves on to the next campaign.
#   - K3 is skipped unless the mini smoke's smoke-report.md says PASS (checked when K3 is due).
#   - K3's gate contains the T-HAYES CALM, which failed check 4b in smoke 1 (cause open, offline diagnosis
#     deferred). If it fails again, K3 stops at its gate and nothing of K3 runs; decide, then resume.
#   - n_max for K1 = 40 (smoke 1, nmax.json).
#   status:  cat .runs/<ts>_v4-all/status.txt
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-.venv/bin/python3}"
"$PY" -c 'import sys; assert sys.version_info >= (3, 12), sys.version' || { echo "need Python >= 3.12 at $PY"; exit 1; }

CHAIN="${1:-.runs/$(date +%Y-%m-%d_%H%M)_v4-all}"
mkdir -p "$CHAIN"
ENV="$CHAIN/chain.env"
if [ ! -f "$ENV" ]; then
  ts=$(date +%Y-%m-%d_%H%M)
  { echo "SMOKE=${SMOKE:-.runs/2026-11-16_0101_v4-smoke}"; echo "K1=.runs/${ts}_v4-K1"; echo "K2=.runs/${ts}_v4-K2"
    echo "K3=.runs/${ts}_v4-K3"; echo "NMAX=40"; } > "$ENV"
fi
# shellcheck disable=SC1090
source "$ENV"
STATUS="$CHAIN/status.txt"
touch "$STATUS"
note() { echo "$(date '+%F %T') $*" | tee -a "$STATUS"; }
done_step() { grep -q "^.* $1 done" "$STATUS"; }

echo "chain: $CHAIN"; cat "$ENV"

# 2. campaigns
for SET in K1 K2 K3; do
  if done_step "$SET"; then
    echo "== $SET already done"
    continue
  fi
  if [ "$SET" = K3 ] && ! head -1 "$SMOKE/smoke-report.md" 2>/dev/null | grep -q "PASS"; then
    note "K3 skipped: mini smoke $SMOKE not PASS (or not finished)"
    continue
  fi
  DIR="${!SET}"
  mkdir -p "$DIR"
  note "$SET start ($DIR)"
  if [ "$SET" = K1 ]; then
    "$PY" scripts/v4_suite.py --set K1 --run --campaign "$DIR" --nmax "$NMAX" 2>&1 | tee -a "$DIR/run.log"
  else
    "$PY" scripts/v4_suite.py --set "$SET" --run --campaign "$DIR" 2>&1 | tee -a "$DIR/run.log"
  fi
  rc=${PIPESTATUS[0]}
  if [ "$rc" -eq 0 ]; then
    note "$SET done"
  elif [ "$rc" -eq 3 ]; then
    note "$SET gate FAIL (see $DIR/gate-report.md); not marked done, resume after a decision"
  else
    note "$SET stopped (exit $rc); not marked done, resume with: bash scripts/run_v4_all.sh $CHAIN"
  fi
done
note "chain finished"
