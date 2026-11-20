#!/bin/sh
# Queued after the v2 chain (user, 2026-11-18): NPR variants V-A / V-B / V-C on E1-0.5; detached from any session.
cd /home/ubuntu/Research/Repos/multirelay/quiclab
R=reports/npr-2026-11-17
while [ ! -f $R/chain-v2.done ]; do sleep 60; done
python3 reports/batch_guard.py auto --session npr-k5 --what "NPR variants V-A/V-B/V-C (E1-0.5)" --cores 2 --expect "+2h" \
  -- sh -c "nice -n 19 .venv/bin/python3 $R/step12v.py rows --jobs 2 > $R/rows-v3.log 2>&1; nice -n 19 .venv/bin/python3 $R/step12v.py report > $R/tables-v3.md 2>&1" 2> $R/guard-v3.log
date '+%F %T' > $R/chain-v3.done
