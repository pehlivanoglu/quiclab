#!/usr/bin/env bash
# Re-run the multi-queue cells of a grouping campaign with the per-client queue
# counters (docs/per-flow-queue-counters.md), then the codel microbenchmarks.
#
#   scripts/rerun_perflow.sh [CAMPAIGN] [--dry]      # default CAMPAIGN .runs/2026-11-10_1946_v2
#
# 1. Archive: every finished fq_codel / cake / mixab run of CAMPAIGN (aggregate
#    GT1 only) moves to .runs/old/<campaign>-aggregate-gt1/<K>/, kept for comparison.
# 2. Re-run them in place, one rep (--skip-existing leaves every other run alone):
#    fq_codel, then cake, then mixab (K1; its b egress is fq_codel).
# 3. The codel microbenchmarks (M1-M6, 25 runs).
# Each step logs to CAMPAIGN/rerun-perflow.log. --dry lists the moves and the
# planned runs without touching anything. Run it in tmux; Ctrl-C stops after the
# current run (the next call of the script skips what finished).
set -euo pipefail
cd "$(dirname "$0")/.."

CAMPAIGN=.runs/2026-11-10_1946_v2
DRY=0
for arg in "$@"; do
  case $arg in
    --dry) DRY=1 ;;
    *) CAMPAIGN=${arg%/} ;;
  esac
done
[ -d "$CAMPAIGN" ] || { echo "no campaign dir $CAMPAIGN" >&2; exit 2; }
ARCHIVE=.runs/old/$(basename "$CAMPAIGN")-aggregate-gt1
LOG=$CAMPAIGN/rerun-perflow.log
PY=.venv/bin/python
GC=scripts/grouping_campaign.py

echo "== $(date '+%F %T') rerun_perflow: campaign $CAMPAIGN, archive $ARCHIVE$([ $DRY = 1 ] && echo ' (dry)')" | tee -a "$LOG"

# 1. archive the old multi-queue runs (only finished ones that are not archived yet)
moved=0
for run in "$CAMPAIGN"/*/grp-*-fq_codel-r* "$CAMPAIGN"/*/grp-*-cake-r* "$CAMPAIGN"/*/grp-*-mixab-r*; do
  [ -d "$run" ] || continue
  k=$(basename "$(dirname "$run")")
  dest=$ARCHIVE/$k/$(basename "$run")
  if [ -e "$dest" ]; then
    echo "skip (already archived): $run" | tee -a "$LOG"
    continue
  fi
  if [ ! -f "$run/router-metrics/flow-ids.json" ]; then     # old run: no per-flow counters
    echo "archive: $run -> $dest" | tee -a "$LOG"
    if [ $DRY = 0 ]; then mkdir -p "$ARCHIVE/$k" && mv "$run" "$dest"; fi
    moved=$((moved + 1))
  fi
done
echo "archived $moved run(s)" | tee -a "$LOG"

# 2. + 3. runs, one after the other (each call keeps finished runs)
step() {   # $1 = label, rest = grouping_campaign.py arguments
  local label=$1; shift
  echo "== $(date '+%F %T') $label: $GC --campaign $CAMPAIGN $*" | tee -a "$LOG"
  if [ $DRY = 1 ]; then
    $PY $GC --campaign "$CAMPAIGN" "$@" --plan 2>&1 | tail -3 | tee -a "$LOG"
  else
    $PY $GC --campaign "$CAMPAIGN" --skip-existing "$@" 2>&1 | tee -a "$LOG"
  fi
}
step "fq_codel cells"     --reps 1 --only fq_codel
step "cake cells"         --reps 1 --only cake
step "mixab cell (K1)"    --reps 1 --only mixab --ks K1
step "codel micro"        --reps 1 --only codel --ks M1,M2,M3,M4,M5,M6
echo "== $(date '+%F %T') rerun_perflow done; check the per-flow pins column of each <K>/infra.md" | tee -a "$LOG"
