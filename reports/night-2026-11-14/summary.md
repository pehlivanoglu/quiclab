# Night campaign 2026-11-14: run health, all ground truths, detector results

Campaigns: `.runs/2026-11-14_0240_night-sync` (31 runs) + `night-stag` (4 runs) = 35 runs.

## Run health
- 35/35 done, none retried, grouping per-run check `ok` on all 35; every events.csv ends with `end`, no event errors, every QUIC session `closed`.
- GT-Q logging: 0 lost tracer events, rows written = kernel counters on every interface. 32/35 runs marked
  `gt_q_invalid` by the strict identity: enqueue pairing off by 1-111 packets per interface (median 2.5e-5,
  max 2.1e-4 of packets; 4.9 k of 171 M). GT-Q/GT-H produced for all 35 with the explicit
  `gtq.py score --tolerate 5e-4` (recorded in each run's truth/gtq-status.csv); default stays strict.
- Tracer logs: harmless `tar: xz: Cannot exec` (bpftrace looks for kernel headers, falls back to BTF).

## Ground truths (per-client episodes)
| truth | episodes | notes |
|---|---|---|
| GT1 | 56 423 | 77 % < 0.5 s |
| GT2 | 76 366 | 86 % < 0.5 s |
| GT3 | 9 787 | 61 % >= 2 s |
| GT-Q | 220 297 (forward, non-gray) | mostly keyframe queues lasting > W; gray intervals not counted |
| GT-H (600 ms) | 13 055 (5.9 % of GT-Q) | 300 / 1000 ms columns in the CSV |

## Detectors (overall, 35 runs)
| detector | GT-Q precision [CI] | GT-H600 recall [CI] | GT-Q recall | L_obs p50 GT-H (ms) | lead p50 (ms) | alarm before harm | GT1 P/R | GT2 P/R | GT3 P/R (lat ms) |
|---|---|---|---|---|---|---|---|---|---|
| shadow | 0.99 [0.98, 1.00] | 0.61 [0.58, 0.63] | 0.05 | 272 | +496 | 0.52 | 0.98 / 0.19 | 0.96 / 0.11 | 0.99 / 0.75 (340) |
| shadow_verified | 0.99 [0.99, 1.00] | 0.59 [0.56, 0.61] | 0.04 | 507 | +324 | 0.47 | 0.99 / 0.15 | 0.99 / 0.09 | 0.99 / 0.63 (718) |
| shadow_m4 | 0.99 [0.98, 0.99] | 0.56 [0.53, 0.59] | 0.04 | 751 | +147 | 0.39 | 0.98 / 0.17 | 0.98 / 0.10 | 0.99 / 0.69 (875) |
| gcc | 0.95 [0.90, 0.99] | 0.60 [0.56, 0.64] | 0.05 | 833 | -45 | 0.27 | 0.96 / 0.20 | 0.93 / 0.12 | 0.98 / 0.81 (890) |
| bbr | 0.97 [0.96, 0.98] | 0.41 [0.37, 0.45] | 0.13 | 886 | -29 | 0.20 | 0.91 / 0.28 | 0.92 / 0.22 | 0.64 / 0.60 (836) |

Full tables: `gt123-detector-tables.{md,csv}` (GT1/GT2/GT3, gt_tables.py), `gtq-detector-table.{md,csv}`
(GT-Q/GT-H per AQM and group, gtq_score.py).

## Diagnostic (added after the results; GT-Q itself unchanged): GT-Q recall without keyframe-aligned episodes
Keyframe-aligned = onset t0 within W after a keyframe arrival at the resource (sender write time +
propagation to the resource) of any video flow through it, and no scripted stimulus near the onset.
78.9 % of GT-Q episodes are keyframe-aligned (31.7 % of the GT-H 600 episodes are too).

| detector | GT-Q recall (all 220 297) | GT-Q recall without keyframe-aligned (46 515) |
|---|---|---|
| shadow | 0.054 | 0.190 |
| shadow_verified | 0.040 | 0.149 |
| shadow_m4 | 0.042 | 0.159 |
| gcc | 0.052 | 0.189 |
| bbr | 0.126 | 0.214 |
| loss_only | 0.063 | 0.201 |

The remaining episodes are still mostly short: of the 46 515, 36 108 last < 0.5 s (shadow recall 0.04);
0.5-1 s 2 441 (0.14); 1-2 s 2 808 (0.71); >= 2 s 5 158 (0.96). gcc: 0.02 / 0.26 / 0.84 / 0.98;
bbr: 0.13 / 0.13 / 0.43 / 0.73. Per AQM / group: gtq-keyframe-diagnostic.csv.
