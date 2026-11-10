#!/usr/bin/env bash
# Record the whole detector matrix (run it in tmux; about 13.5 h at 2 reps):
#   base   every event scenario + capacity, cbr, ppbp on detector.yaml
#   access isolate (private bottlenecks) on detector-access.yaml
#   split  splitcap, splitudp on detector-split.yaml
#
#   scripts/run_detector_matrix.sh [TAG]      # TAG default: today, YYYY-MM-DD
#   REPS=3 AQMS=pfifo,fq_codel scripts/run_detector_matrix.sh
#   OUT=ip4 scripts/run_detector_matrix.sh    # campaigns under .runs/ip4/
#
# Resume after any stop: run it again with the same TAG. Finished runs are kept,
# an interrupted run starts over. A run that fails is recorded in matrix.yaml and
# the matrix goes on; running the script again retries it.
#
# Without shadow/build/moqx_shadow_replay (README "Usage") the runs are recorded but not
# scored. Afterwards: .venv/bin/python scripts/det_eval.py score .runs/<TAG>_det-*/det-*
set -euo pipefail
cd "$(dirname "$0")/.."

TAG="${1:-$(date +%F)}"
REPS="${REPS:-2}"
OUT="${OUT:-}"
PREFIX="${OUT:+${OUT%/}/}"
AQMS="${AQMS:-pfifo,red,pie,fq_codel}"
BASE="capacity,cbr,ppbp,burstcap,burstudp,bursttiny,ramp,tcpcubic,tcpbbr,burstcaplowrtt,burstcaphighrtt,burstlong,burstcapshallow,burstcapdeep,onoff,revdelay,calm030,calm065,calm090,calmcbr090,randloss"

[ -x .venv/bin/python ] || { echo "missing .venv: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2; exit 1; }
[ -x qvideo/build/qvideo-server ] || { echo "missing qvideo: .venv/bin/python -m quiclab build qvideo" >&2; exit 1; }
docker image inspect quiclab:latest >/dev/null 2>&1 || { echo "missing image: .venv/bin/python -m quiclab build image" >&2; exit 1; }

matrix() {  # topology scenarios
    echo "=== $1 ($(date +%T)) ==="
    .venv/bin/python scripts/det_matrix.py --topology "$1" --scenarios "$2" --aqms "$AQMS" --reps "$REPS" \
        --campaign "${PREFIX}${TAG}_det-$1" --skip-existing
}

matrix base "$BASE"
matrix access isolate
matrix split splitcap,splitudp
echo "=== finished $(date +%T): .runs/${PREFIX}${TAG}_det-{base,access,split}/matrix.yaml ==="
grep -h "failed" .runs/"${PREFIX}${TAG}"_det-*/matrix.yaml || echo "no failed runs"
