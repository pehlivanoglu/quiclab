#!/bin/sh
# B.b item b: waits for diag3 (this session's 2 cores), then frozen NPR-B / NPR-A on 1000 synthetic clients, guarded.
cd /home/ubuntu/Research/Repos/multirelay/quiclab
R=reports/npr-2026-11-17
while [ ! -f $R/diag3.done ]; do sleep 60; done
python3 reports/batch_guard.py auto --session npr-k5 --what "B.b 1000-client NPR cost (cost1000.py)" --cores 1 --expect "+2h" \
  -- sh -c "OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nice -n 19 .venv/bin/python3 $R/cost1000.py run 5 >> $R/cost1000.log 2>&1 && .venv/bin/python3 $R/cost1000.py report > $R/cost1000.md 2>&1 && date '+%F %T' > $R/cost1000.done" 2>> $R/guard-cost1000.log
