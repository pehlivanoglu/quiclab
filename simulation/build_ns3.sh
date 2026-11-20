#!/usr/bin/env bash
# Configure and build ns-3.48 with only the modules quicsim needs, plus quicsim itself.
# Launch it through the batch guard (it needs a CPU slot), from quiclab/:
#
#   python3 reports/batch_guard.py auto --session sim --what "ns-3 build" \
#       --cores 1 --expect HH:MM -- nice -n 19 bash simulation/build_ns3.sh
#
# JOBS (default 1) is the number of compiler jobs; it must match --cores.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
NS3="$HERE/third_party/ns-3.48"
JOBS="${JOBS:-1}"

free_gb=$(df -BG --output=avail / | tail -1 | tr -dc 0-9)
if (( free_gb < 30 )); then
  echo "free disk ${free_gb} GB < 30 GB: not building" >&2
  exit 1
fi

# Our program lives in simulation/ns3/quicsim; ns-3 builds it as a scratch subdirectory.
ln -sfn ../../../ns3/quicsim "$NS3/scratch/quicsim"

# The changes to ns-3 (patches/README.md): applied once, idempotent; the build refuses an unpatched tree.
# patches/dropped/ is not applied (patch 2, mvfst drain mark: no effect, dropped 2026-11-19).
for P in "$HERE"/patches/*.patch; do
  if patch -d "$NS3" -p1 -N --dry-run -s < "$P" > /dev/null 2>&1; then patch -d "$NS3" -p1 -N -s < "$P"; fi
done
grep -q "quiclab simulation patch: check application-limited BEFORE" "$NS3/src/internet/model/tcp-socket-base.cc" \
  || { echo "ns-3 app-limited patch not applied" >&2; exit 1; }
! grep -q "quiclab simulation patch 2" "$NS3/src/internet/model/tcp-socket-base.cc" \
  || { echo "dropped patch 2 is still applied: reverse it (patch -R) first" >&2; exit 1; }

cd "$NS3"
# nix-vector-routing: on-demand routes (item 5, scale); global routing's all-pairs tables grow with N^2.
MODULES="internet;point-to-point;traffic-control;nix-vector-routing"
if [[ ! -f cmake-cache/CMakeCache.txt ]] || ! grep -qx "NS3_ENABLED_MODULES:STRING=$MODULES" cmake-cache/CMakeCache.txt; then
  ./ns3 configure --build-profile=optimized --disable-examples --disable-tests --disable-python \
    --enable-modules="$MODULES"
fi
./ns3 build -j "$JOBS" quicsim
ls -l build/scratch/quicsim/ns3.48-quicsim-optimized
