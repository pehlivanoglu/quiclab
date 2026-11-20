#!/bin/sh
# This session's slot (2 cores), in order: K5 build check (needed before K3 ends), then diag3. Both guarded, nice 19.
cd /home/ubuntu/Research/Repos/multirelay/quiclab
python3 reports/batch_guard.py auto --session npr-k5 --what "K5 build check into qvideo/build-k5 + selftest + unit tests" \
  --cores 2 --expect "+0.5h" -- nice -n 19 sh reports/k5-start/build_k5.sh 2>> reports/k5-start/guard-build.log
sh reports/npr-2026-11-17/run_diag3.sh
