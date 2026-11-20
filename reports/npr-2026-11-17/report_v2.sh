#!/bin/sh
# Writes the corrected-test (v2) tables once the chain is done; detached from any session.
cd /home/ubuntu/Research/Repos/multirelay/quiclab
R=reports/npr-2026-11-17
while [ ! -f $R/chain-v2.done ]; do sleep 60; done
for c in E1-0.5 E3 E1-1 E1-2; do nice -n 19 .venv/bin/python3 $R/step12.py report --cand $c > $R/tables-v2-$c.md 2>&1; done
nice -n 19 .venv/bin/python3 $R/step3.py report > $R/tables-step3-v2.md 2>&1
date '+%F %T' > $R/report-v2.done
