#!/bin/sh
# K5 start preparation: build the current tree's qvideo-server and qvideo-selftest into qvideo/build-k5 WITHOUT touching
# the campaign's qvideo/build (K3 runs from it). The compile and link commands are qvideo/build's own (ninja -t commands,
# print only); only the outputs are redirected, the dependency libraries in qvideo/build are read, never written.
# Then: selftest, the server's K5 flags, the K5 unit tests. Output: reports/k5-start/build-k5.log, build-k5.done.
set -eu
cd /home/ubuntu/Research/Repos/multirelay/quiclab
Q=$PWD/qvideo
K=$Q/build-k5
L=$PWD/reports/k5-start/build-k5.log
mkdir -p "$K"
cd "$Q/build"
before=$(md5sum build.ninja .ninja_log | md5sum)
{
  echo "== $(date '+%F %T') build into $K (sources: $(md5sum ../src/Server.cpp ../src/SelfTest.cpp ../src/Adapt.h ../src/SendQueue.h | md5sum | cut -c1-16))"
  srv_c=$(ninja -t commands qvideo-server | grep -F "src/Server.cpp" | grep -F -- " -c ")
  srv_l=$(ninja -t commands qvideo-server | tail -1)
  st_c=$(ninja -t commands qvideo-selftest | grep -F "src/SelfTest.cpp" | grep -F -- " -c ")
  st_l=$(ninja -t commands qvideo-selftest | tail -1)
  # redirect object, dep file and binary into build-k5
  r() { echo "$1" | sed -e "s# -o CMakeFiles/qvideo-server.dir/src/Server.cpp.o# -o $K/Server.cpp.o#" \
      -e "s# -MF CMakeFiles/qvideo-server.dir/src/Server.cpp.o.d# -MF $K/Server.cpp.o.d#" \
      -e "s# -MT CMakeFiles/qvideo-server.dir/src/Server.cpp.o# -MT $K/Server.cpp.o#" \
      -e "s# -o CMakeFiles/qvideo-selftest.dir/src/SelfTest.cpp.o# -o $K/SelfTest.cpp.o#" \
      -e "s# -MF CMakeFiles/qvideo-selftest.dir/src/SelfTest.cpp.o.d# -MF $K/SelfTest.cpp.o.d#" \
      -e "s# -MT CMakeFiles/qvideo-selftest.dir/src/SelfTest.cpp.o# -MT $K/SelfTest.cpp.o#" \
      -e "s# CMakeFiles/qvideo-server.dir/src/Server.cpp.o -o qvideo-server # $K/Server.cpp.o -o $K/qvideo-server #" \
      -e "s# CMakeFiles/qvideo-selftest.dir/src/SelfTest.cpp.o -o qvideo-selftest # $K/SelfTest.cpp.o -o $K/qvideo-selftest #"; }
  for c in "$(r "$st_c")" "$(r "$srv_c")" "$(r "$st_l")" "$(r "$srv_l")"; do
    case "$c" in *"$K"*) ;; *) echo "command not redirected: $c" | cut -c1-300; exit 1 ;; esac
    sh -c "$c"
  done
  after=$(md5sum build.ninja .ninja_log | md5sum)
  [ "$before" = "$after" ] && echo "qvideo/build untouched (build.ninja, .ninja_log)" || { echo "qvideo/build CHANGED"; exit 1; }
  ls -la "$K/qvideo-server" "$K/qvideo-selftest" "$Q/build/qvideo-server"
  echo "== selftest"; "$K/qvideo-selftest"
  echo "== server flags"; "$K/qvideo-server" --helpfull 2>&1 | grep -E "send_buffer_ms|adapt_x|adapt_floor" || true
  echo "== campaign binary (qvideo/build) flags, for comparison"; "$Q/build/qvideo-server" --helpfull 2>&1 | grep -E "send_buffer_ms|adapt_x|adapt_floor" || true
  cd "$Q/.."
  echo "== unit tests"; .venv/bin/python3 -m pytest -q tests/unit/test_k5_adapt.py 2>&1 | tail -5
  echo "== K5 plan (scratch, plan only)"
  .venv/bin/python3 scripts/k5_suite.py --plan-only --set K5 --campaign "$K/plan-check" 2>&1 | tail -8
  date '+%F %T' > reports/k5-start/build-k5.done
} >> "$L" 2>&1
