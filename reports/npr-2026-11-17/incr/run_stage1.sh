#!/bin/sh
# Incremental NPR-B stage 1 (user 2026-11-19): equivalence on the 263 development runs (2 cores), then, only if it
# passes, cost1000 repeated frozen vs incremental to 1000 events (1 core). Both guarded (batch_guard auto, nice 19).
cd /home/ubuntu/Research/Repos/multirelay/quiclab
D=reports/npr-2026-11-17/incr
# disk rule (user 2026-11-19): no start under 30 GB free; warn under 50 GB. Output of this batch: a few MB.
disk_ok() {
  free=$(df -BG --output=avail / | tail -1 | tr -dc 0-9)
  echo "$(date '+%F %T') disk free ${free} GB before $1 (expected use < 0.1 GB)" >> $D/stage1.log
  if [ "$free" -lt 30 ]; then echo "$(date '+%F %T') under 30 GB: $1 NOT started" >> $D/stage1.log; exit 3; fi
  if [ "$free" -lt 50 ]; then echo "$(date '+%F %T') WARNING under 50 GB" >> $D/stage1.log; fi
}
T="OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nice -n 19"
disk_ok equivalence
python3 reports/batch_guard.py auto --session npr-k5 --what "incr NPR-B equivalence (equiv.py)" --cores 2 --expect "+1.5h" \
  -- sh -c "$T .venv/bin/python3 $D/equiv.py rows --jobs 2 >> $D/equiv.log 2>&1; .venv/bin/python3 $D/equiv.py report > $D/equiv-report.log 2>&1; echo \$? > $D/equiv.exit; date '+%F %T' > $D/equiv.done" 2>> $D/guard-equiv.log
if [ "$(cat $D/equiv.exit 2>/dev/null)" != "0" ]; then echo "$(date '+%F %T') equivalence FAIL or incomplete: cost run not started" >> $D/stage1.log; exit 1; fi
disk_ok cost
python3 reports/batch_guard.py auto --session npr-k5 --what "incr NPR-B cost to 1000 events (cost_incr.py)" --cores 1 --expect "+5h" \
  -- sh -c "$T .venv/bin/python3 $D/cost_incr.py run 5 >> $D/cost-incr.log 2>&1; .venv/bin/python3 $D/cost_incr.py report > $D/cost-incr-report.log 2>&1; date '+%F %T' > $D/cost-incr.done" 2>> $D/guard-cost-incr.log
echo "$(date '+%F %T') stage 1 batch done" >> $D/stage1.log
