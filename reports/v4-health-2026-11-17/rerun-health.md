# Health of the 12 re-run / I1 runs (2026-11-19, .runs/2026-11-19_2030_v4-rerun)

Binary: qvideo/build (2026-11-15, the K2 / K3 binary; rebuild not yet done). 12 / 12 finished (v3-checks.json).
Checks as for every K3 run (the runner's v3 checks 1-6 and v4 checks), plus tracer health from gtq-health.csv.

| run | v3 checks 1-6 | v4 checks | tracer: lost events | note |
|---|---|---|---|---|
| v4-T2-sburst-jit5-pfifo-r2 | ok ok ok ok ok ok | - | 0 | re-run; passes |
| v4-L2-fbcross-x80-codel-r2 | FAIL ok ok ok FAIL - | - | 0 | re-run; check 4 now passes (original: FAIL, lost tracer events). Checks 1 and 5 fail in every L2 x80 run (K3 codel r1 / r2, pie r1 / r2): the cell's design (FlowBot cross load at x80), not this run |
| v4-L11-spause-def-pfifo-r2 | ok ok ok ok ok ok | pause ok | 0 | re-run; passes |
| v4-C1-sjoin-copa-pfifo-r2 | ok ok ok ok - ok | - | 0 | re-run; passes (check 5 not applicable, as the original) |
| v4-I1-calm-ip1p2-pfifo-r1 / r2 | ok ok ok ok - ok | - | 0 | passes (calm: no check 5) |
| v4-I1-hhier-ip1p2-pfifo-r1 / r2 | ok x 6 | - | 0 | passes |
| v4-I1-sburst-ip1p2-codel-r1 / r2 | ok x 6 | - | 0 | passes |
| v4-I1-sburst-ip1p2-pfifo-r1 / r2 | ok x 6 | - | 0 | passes |

Batch overlap (rule 3): every batch guard was paused during the 12 runs (all match the no-batch pattern; guard
states paused from 20:56; the simulation session's 20:23 job was a light 1-core read). Host CPU idle during the runs:
median 0.92-0.97, minimum 0.90-0.93 (L2 x80 0.75, its own FlowBot load). No run fails or newly flags a check under
overlap: no new re-run entry.

Result: the 8 I1 runs (ip1p2 ids) are valid for A.4 under the a4-rules.md mapping; the 4 re-runs pass their reason
for re-running (L2 x80: check 4 now ok; its checks 1 / 5 are the cell's, as in every L2 x80 run).
