#!/bin/sh
# NPR v3 diagnosis 2a-2e (diag3.py), guarded batch, 2 cores, nice 19. Detached by the caller.
cd /home/ubuntu/Research/Repos/multirelay/quiclab
R=reports/npr-2026-11-17
python3 reports/batch_guard.py auto --session npr-k5 --what "NPR v3 diagnosis 2a-2e (diag3.py)" --cores 2 --expect "+0.5h" \
  -- sh -c "nice -n 19 .venv/bin/python3 $R/diag3.py rows --jobs 2 >> $R/diag3-rows.log 2>&1 && nice -n 19 .venv/bin/python3 $R/diag3.py report > $R/diag3.md 2>&1 && date '+%F %T' > $R/diag3.done" 2>> $R/guard-diag3.log
