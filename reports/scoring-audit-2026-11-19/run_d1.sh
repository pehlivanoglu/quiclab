#!/bin/sh
# D1 old-vs-new GT-L window comparison (user 2026-11-19): v3 runs, then K1 default cells, then the report.
# Guarded (batch_guard auto, nice 19, 2 cores). Disk rule: no start under 30 GB, warn under 50 GB.
cd /home/ubuntu/Research/Repos/multirelay/quiclab
D=reports/scoring-audit-2026-11-19
free=$(df -BG --output=avail / | tail -1 | tr -dc 0-9)
echo "$(date '+%F %T') disk free ${free} GB (expected use ~7 GB of K1 tick files in $D/k1/farm)" >> $D/d1.log
if [ "$free" -lt 30 ]; then echo "$(date '+%F %T') under 30 GB: not started" >> $D/d1.log; exit 3; fi
[ "$free" -lt 50 ] && echo "$(date '+%F %T') WARNING under 50 GB" >> $D/d1.log
T="OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nice -n 19"
python3 reports/batch_guard.py auto --session npr-k5 --what "D1 GT-L window old vs new (v3 + K1 def)" --cores 2 --expect "+3h" \
  -- sh -c "$T .venv/bin/python3 $D/d1_window.py rows --set v3 --jobs 2 >> $D/d1.log 2>&1; $T .venv/bin/python3 $D/d1_window.py rows --set k1 --jobs 2 >> $D/d1.log 2>&1; .venv/bin/python3 $D/d1_window.py report > $D/d1-report.log 2>&1; date '+%F %T' > $D/d1.done" 2>> $D/guard-d1.log
