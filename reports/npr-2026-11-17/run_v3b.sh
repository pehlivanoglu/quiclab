#!/bin/sh
# NPR variants V-A / V-B / V-C on E1-0.5, resumed under the guard with the proactive rule (2026-11-18 21:00).
cd /home/ubuntu/Research/Repos/multirelay/quiclab
R=reports/npr-2026-11-17
python3 reports/batch_guard.py auto --session npr-k5 --what "NPR variants V-A/V-B/V-C (E1-0.5)" --cores 2 --expect "+1.5h" \
  -- sh -c "nice -n 19 .venv/bin/python3 $R/step12v.py rows --jobs 2 >> $R/rows-v3.log 2>&1 && nice -n 19 .venv/bin/python3 $R/step12v.py report > $R/tables-v3.md 2>&1 && date '+%F %T' > $R/chain-v3.done" 2>> $R/guard-v3.log
