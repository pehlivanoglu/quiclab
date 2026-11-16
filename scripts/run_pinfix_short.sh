#!/usr/bin/env bash
# fq_codel pin fix (2026-11-15): one 60 s run per topology (T-BASE, H-HIER, H-DEPTH, A-MIXED, mixab), one
# after the other, then the pin check of every run. About 5 min of emulation, ~10 min wall.
#
#   bash scripts/run_pinfix_short.sh
#
# Writes .runs/<date>_pinfix/<run>/ and .runs/<date>_pinfix/pin-check.txt. A finished run is skipped when the
# script is started again with the same folder: PINFIX_DIR=.runs/<date>_pinfix bash scripts/run_pinfix_short.sh
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-.venv/bin/python3}"
GEN=".runs/2026-11-14_1818_v3/_gen"
OUT="${PINFIX_DIR:-.runs/$(date +%Y-%m-%d_%H%M)_pinfix}"
mkdir -p "$OUT"
echo "pinfix: $OUT"

"$PY" scripts/fq_pin_short.py "$GEN" "$OUT/scenarios" > /dev/null

declare -A NAMES=(
  [t-base]=v3-C2-sburst-s030u070-fq_codel-r1
  [h-hier]=v3-C7-hhier-s030-fq_codel-r1
  [h-depth]=v3-C9-hdepth-tree16-fq_codel-r1
  [a-mixed]=v3-C12-amixed-access-fq_codel-r1
  [mixab]=v3-M8-hhier-mixab-mixab-r1
)
runs=()
for topo in t-base h-hier h-depth a-mixed mixab; do
  src=${NAMES[$topo]}
  id="pinfix-$topo"
  runs+=("$OUT/$id")
  if [ -f "$OUT/$id/tc-filters.txt" ] && [ -d "$OUT/$id/router-metrics" ]; then
    echo "== $id: already done, skipped"
    continue
  fi
  rm -rf "$OUT/$id"
  echo "== $id ($src, 60 s)"
  QUICLAB_GTQ_LOGGING=1 "$PY" -m quiclab --runs-dir "$OUT" run -c "$GEN/$src-topology.yaml" \
      -s "$OUT/scenarios/$src.yaml" --run-id "$id" 2>&1 | tee "$OUT/$id.log" \
    || echo "!! $id failed (see $OUT/$id.log)"
done

echo
echo "== pin check"
"$PY" scripts/fq_pin_check.py "${runs[@]}" | tee "$OUT/pin-check.txt" || true
echo
echo "result: $OUT/pin-check.txt (every line OK = fix verified on every topology)"
