#!/usr/bin/env bash
# Overnight campaign 2026-11-14 (reviewer note "Overnight campaign"): one run per line, in
# priority order (P1 first; inside a level rep 1 before rep 2), synchronized phases unless the
# line says stag. Two tagged folders: <ts>_night-sync and <ts>_night-stag. After the queue, every
# run that did not finish is retried once (--skip-existing keeps finished runs). No reports.
#
#   tmux new -s night 'bash scripts/run_night_2026-11-14.sh'
#   bash scripts/run_night_2026-11-14.sh <ts>        # resume with the same timestamp prefix
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-.venv/bin/python3}"
"$PY" -c 'import sys; assert sys.version_info >= (3, 12), sys.version' || { echo "need Python >= 3.12 at $PY"; exit 1; }
TS="${1:-$(date +%Y-%m-%d_%H%M)}"
SYNC=".runs/${TS}_night-sync"; STAG=".runs/${TS}_night-stag"
mkdir -p "$SYNC" "$STAG"
LOG="$SYNC/run.log"
echo "campaign: $SYNC + $STAG (log: $LOG)" | tee -a "$LOG"

# level phase campaign type aqm rep
QUEUE=(
  "P1 sync K6 depth pfifo 3" "P1 sync C1 burstlongsplit pfifo 3" "P1 sync K6 depth pfifo 4" "P1 sync C1 burstlongsplit pfifo 4"
  "P2 stag K1 hier pfifo 2" "P2 stag K6 depth pfifo 2" "P2 stag C1 burstlongsplit pfifo 2"
  "P3 sync K6R depthroot2 pfifo 1" "P3 sync K6R depthroot2 pfifo 2"
  "P4 sync M1 burstcap codel 1" "P4 sync K1 hier codel 1" "P4 sync K6 depth codel 1" "P4 sync C1 burstlongsplit codel 1"
  "P4 sync M1 burstcap pie 1" "P4 sync K1 hier pie 1" "P4 sync K6 depth pie 1" "P4 sync C1 burstlongsplit pie 1"
  "P4 sync M1 burstcap codel 2" "P4 sync K1 hier codel 2" "P4 sync K6 depth codel 2" "P4 sync C1 burstlongsplit codel 2"
  "P4 sync M1 burstcap pie 2" "P4 sync K1 hier pie 2" "P4 sync K6 depth pie 2" "P4 sync C1 burstlongsplit pie 2"
  "P5 sync M6 indepfast pfifo 1" "P5 sync M6 indepslow pfifo 1" "P5 sync M6 indepfast pfifo 2" "P5 sync M6 indepslow pfifo 2"
  "P6 sync G0 randloss pfifo 1" "P6 sync G0 calmuneven pfifo 1" "P6 sync G0 randloss pfifo 2" "P6 sync G0 calmuneven pfifo 2"
  "P7 sync J1 hierjit20 pfifo 1" "P7 sync J1 hierjit20 pfifo 2"
)

run_one() {   # level phase k type aqm rep
  local dir="$SYNC"; [ "$2" = stag ] && dir="$STAG"
  echo "### $(date '+%F %T') $1 $2 $3 grp-$4-$5-r$6" | tee -a "$LOG"
  "$PY" scripts/grouping_campaign.py --campaign "$dir" --phase "$2" --skip-report --skip-existing \
    --ks "$3" --aqms "$5" --reps "$6" --only "grp-$4-$5-r$6" 2>&1 | tee -a "$LOG"
}

for pass in 1 2; do
  echo "### $(date '+%F %T') pass $pass" | tee -a "$LOG"
  for line in "${QUEUE[@]}"; do
    run_one $line
  done
done
echo "### $(date '+%F %T') campaign done" | tee -a "$LOG"
# list runs that still did not finish after the retry
"$PY" - "$SYNC" "$STAG" <<'EOF' | tee -a "$LOG"
import sys
from pathlib import Path
sys.path.insert(0, ".")
from quiclab.runtime import run_finished
bad = [str(r) for d in sys.argv[1:] for r in sorted(Path(d).glob("*/grp-*")) if r.is_dir() and not run_finished(r)]
print("unfinished after retry:", bad or "none")
EOF
