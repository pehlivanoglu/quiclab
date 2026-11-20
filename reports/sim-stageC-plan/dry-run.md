# Stage C dry run (2026-11-19 18:33): nothing is simulated, scored, deleted or compressed

Runs: 42; run folders /home/ubuntu/Research/Repos/multirelay/quiclab/simulation/runs/stageC/<block>/<run>; plans /home/ubuntu/Research/Repos/multirelay/quiclab/simulation/runs/stageC/plans/<run>; tick cache /home/ubuntu/simcache-stageC/<block>/<run> (one run at a time); state /home/ubuntu/Research/Repos/multirelay/quiclab/simulation/runs/stageC/state.json

## Leaves per layout (leaf name: clients; sampled = traced leaves under 'sample')

- 100 clients, L10: l01: 10, l02: 10, l03: 10, l04: 10, l05: 10, l06: 10, l07: 10, l08: 10, l09: 10, l10: 10; sampled (C1/C2): l01, l02, l03
- 100 clients, L50: l01: 50, l02: 50; sampled (C1/C2): l01, l02
- 100 clients, L100: l01: 100; sampled (C1/C2): l01
- 100 clients, uneven: l01: 2, l02: 3, l03: 5, l04: 8, l05: 12, l06: 20, l07: 50; sampled (C1/C2): l01, l02, l03
- 300 clients, L10: 30 leaves of 10; sampled (C1/C2): l01, l11, l21
- 300 clients, L50: l01: 50, l02: 50, l03: 50, l04: 50, l05: 50, l06: 50; sampled (C1/C2): l01, l02, l03
- 300 clients, L100: l01: 100, l02: 100, l03: 100; sampled (C1/C2): l01, l02, l03
- 300 clients, uneven: l01: 2, l02: 3, l03: 5, l04: 8, l05: 12, l06: 20, l07: 50, l08: 200; sampled (C1/C2): l01, l02, l03
- 1000 clients, L10: 100 leaves of 10; sampled (none: no trace at 1000): -
- 1000 clients, L50: 20 leaves of 50; sampled (none: no trace at 1000): -
- 1000 clients, L100: l01: 100, l02: 100, l03: 100, l04: 100, l05: 100, l06: 100, l07: 100, l08: 100, l09: 100, l10: 100; sampled (none: no trace at 1000): -
- 1000 clients, uneven: l01: 2, l02: 3, l03: 5, l04: 8, l05: 12, l06: 20, l07: 50, l08: 100, l09: 200, l10: 2, l11: 3, l12: 5, l13: 8, l14: 12, l15: 20, l16: 50, l17: 100, l18: 200, l19: 200; sampled (none: no trace at 1000): -

## Run list (expected per run, extrapolated: stagec_numbers.py)

| # | run | trace | raw GB | zstd GB | cache GB | sim min | scoring min | largest step GB |
|---|---|---|---|---|---|---|---|---|
| 1 | sim-C-C1-L10-n100-pfifo-r1 | sample | 2.1 | 0.4 | 0.7 | 4-5 | 12 | 2.9 |
| 2 | sim-C-C1-L10-n100-pfifo-r2 | sample | 2.1 | 0.4 | 0.7 | 4-5 | 12 | 2.9 |
| 3 | sim-C-C1-L10-n100-codel-r1 | sample | 2.1 | 0.4 | 0.7 | 4-5 | 12 | 2.9 |
| 4 | sim-C-C1-L10-n100-codel-r2 | sample | 2.1 | 0.4 | 0.7 | 4-5 | 12 | 2.9 |
| 5 | sim-C-C1-L50-n100-pfifo-r1 | sample | 3.1 | 0.5 | 0.7 | 4-5 | 23 | 6.6 |
| 6 | sim-C-C1-L50-n100-pfifo-r2 | sample | 3.1 | 0.5 | 0.7 | 4-5 | 23 | 6.6 |
| 7 | sim-C-C1-L50-n100-codel-r1 | sample | 3.1 | 0.5 | 0.7 | 4-5 | 23 | 6.6 |
| 8 | sim-C-C1-L50-n100-codel-r2 | sample | 3.1 | 0.5 | 0.7 | 4-5 | 23 | 6.6 |
| 9 | sim-C-C1-L100-n100-pfifo-r1 | sample | 3.1 | 0.5 | 0.7 | 4-5 | 23 | 6.6 |
| 10 | sim-C-C1-L100-n100-pfifo-r2 | sample | 3.1 | 0.5 | 0.7 | 4-5 | 23 | 6.6 |
| 11 | sim-C-C1-L100-n100-codel-r1 | sample | 3.1 | 0.5 | 0.7 | 4-5 | 23 | 6.6 |
| 12 | sim-C-C1-L100-n100-codel-r2 | sample | 3.1 | 0.5 | 0.7 | 4-5 | 23 | 6.6 |
| 13 | sim-C-C1-uneven-n100-pfifo-r1 | sample | 3.1 | 0.5 | 0.7 | 4-5 | 23 | 6.6 |
| 14 | sim-C-C1-uneven-n100-pfifo-r2 | sample | 3.1 | 0.5 | 0.7 | 4-5 | 23 | 6.6 |
| 15 | sim-C-C1-uneven-n100-codel-r1 | sample | 3.1 | 0.5 | 0.7 | 4-5 | 23 | 6.6 |
| 16 | sim-C-C1-uneven-n100-codel-r2 | sample | 3.1 | 0.5 | 0.7 | 4-5 | 23 | 6.6 |
| 17 | sim-C-C2-L10-n300-pfifo-r1 | sample | 5.3 | 1.0 | 2.2 | 14-14 | 31 | 5.6 |
| 18 | sim-C-C2-L10-n300-pfifo-r2 | sample | 5.3 | 1.0 | 2.2 | 14-14 | 31 | 5.6 |
| 19 | sim-C-C2-L10-n300-codel-r1 | sample | 5.3 | 1.0 | 2.2 | 14-14 | 31 | 5.6 |
| 20 | sim-C-C2-L10-n300-codel-r2 | sample | 5.3 | 1.0 | 2.2 | 14-14 | 31 | 5.6 |
| 21 | sim-C-C2-L50-n300-pfifo-r1 | sample | 7.1 | 1.3 | 2.2 | 14-14 | 49 | 11.9 |
| 22 | sim-C-C2-L50-n300-pfifo-r2 | sample | 7.1 | 1.3 | 2.2 | 14-14 | 49 | 11.9 |
| 23 | sim-C-C2-L50-n300-codel-r1 | sample | 7.1 | 1.3 | 2.2 | 14-14 | 49 | 11.9 |
| 24 | sim-C-C2-L50-n300-codel-r2 | sample | 7.1 | 1.3 | 2.2 | 14-14 | 49 | 11.9 |
| 25 | sim-C-C2-L100-n300-pfifo-r1 | sample | 9.4 | 1.6 | 2.2 | 14-14 | 72 | 19.7 |
| 26 | sim-C-C2-L100-n300-pfifo-r2 | sample | 9.4 | 1.6 | 2.2 | 14-14 | 72 | 19.7 |
| 27 | sim-C-C2-L100-n300-codel-r1 | sample | 9.4 | 1.6 | 2.2 | 14-14 | 72 | 19.7 |
| 28 | sim-C-C2-L100-n300-codel-r2 | sample | 9.4 | 1.6 | 2.2 | 14-14 | 72 | 19.7 |
| 29 | sim-C-C2-uneven-n300-pfifo-r1 | sample | 7.1 | 1.3 | 2.2 | 14-14 | 49 | 11.9 |
| 30 | sim-C-C2-uneven-n300-pfifo-r2 | sample | 7.1 | 1.3 | 2.2 | 14-14 | 49 | 11.9 |
| 31 | sim-C-C2-uneven-n300-codel-r1 | sample | 7.1 | 1.3 | 2.2 | 14-14 | 49 | 11.9 |
| 32 | sim-C-C2-uneven-n300-codel-r2 | sample | 7.1 | 1.3 | 2.2 | 14-14 | 49 | 11.9 |
| 33 | sim-C-C3-L10-n1000-pfifo-r1 | none | 12.5 | 2.7 | 7.4 | 47-63 | 91 | 13.7 |
| 34 | sim-C-C3-L10-n1000-pfifo-r2 | none | 12.5 | 2.7 | 7.4 | 47-63 | 91 | 13.7 |
| 35 | sim-C-C3-L50-n1000-pfifo-r1 | none | 12.5 | 2.7 | 7.4 | 47-63 | 91 | 13.7 |
| 36 | sim-C-C3-L50-n1000-pfifo-r2 | none | 12.5 | 2.7 | 7.4 | 47-63 | 91 | 13.7 |
| 37 | sim-C-C3-L100-n1000-pfifo-r1 | none | 12.5 | 2.7 | 7.4 | 47-63 | 91 | 13.7 |
| 38 | sim-C-C3-L100-n1000-pfifo-r2 | none | 12.5 | 2.7 | 7.4 | 47-63 | 91 | 13.7 |
| 39 | sim-C-C3-uneven-n1000-pfifo-r1 | none | 12.5 | 2.7 | 7.4 | 47-63 | 91 | 13.7 |
| 40 | sim-C-C3-uneven-n1000-pfifo-r2 | none | 12.5 | 2.7 | 7.4 | 47-63 | 91 | 13.7 |
| 41 | sim-C-C4-L50-n1000-pfifo-r1 | none | 12.5 | 2.7 | 7.4 | 66-88 | 91 | 13.7 |
| 42 | sim-C-C4-L50-n1000-pfifo-r2 | none | 12.5 | 2.7 | 7.4 | 66-88 | 91 | 13.7 |

## Steps per run, in this order

- health (expected peak 2.4 GB for sim-C-C1-L10-n100-pfifo-r1)
- health-lite (expected peak 1.0 GB for sim-C-C1-L10-n100-pfifo-r1)
- detector (expected peak 0.8 GB for sim-C-C1-L10-n100-pfifo-r1)
- sets (expected peak 1.4 GB for sim-C-C1-L10-n100-pfifo-r1)
- events (expected peak 1.4 GB for sim-C-C1-L10-n100-pfifo-r1)
- gt1 (expected peak 1.0 GB for sim-C-C1-L10-n100-pfifo-r1)
- gt3 (expected peak 0.8 GB for sim-C-C1-L10-n100-pfifo-r1)
- gtq (expected peak 2.9 GB for sim-C-C1-L10-n100-pfifo-r1)
- check outputs complete -> delete the run's tick cache (W2) -> compress and verify (W1, manifest)

## Plan check (each run's plan built in a temporary folder outside quiclab/, then removed)

- sim-C-C1-L10-n100-pfifo-r1: ok, 973 plan records; ports 'route': highest port block end on one route 4245 of 35536 available
- sim-C-C1-L10-n100-pfifo-r2: ok, 974 plan records; ports 'route': highest port block end on one route 3530 of 35536 available
- sim-C-C1-L10-n100-codel-r1: ok, 973 plan records; ports 'route': highest port block end on one route 4245 of 35536 available
- sim-C-C1-L10-n100-codel-r2: ok, 974 plan records; ports 'route': highest port block end on one route 3530 of 35536 available
- sim-C-C1-L50-n100-pfifo-r1: ok, 638 plan records; ports 'route': highest port block end on one route 3294 of 35536 available
- sim-C-C1-L50-n100-pfifo-r2: ok, 639 plan records; ports 'route': highest port block end on one route 3653 of 35536 available
- sim-C-C1-L50-n100-codel-r1: ok, 638 plan records; ports 'route': highest port block end on one route 3294 of 35536 available
- sim-C-C1-L50-n100-codel-r2: ok, 639 plan records; ports 'route': highest port block end on one route 3653 of 35536 available
- sim-C-C1-L100-n100-pfifo-r1: ok, 594 plan records; ports 'route': highest port block end on one route 3564 of 35536 available
- sim-C-C1-L100-n100-pfifo-r2: ok, 595 plan records; ports 'route': highest port block end on one route 4092 of 35536 available
- sim-C-C1-L100-n100-codel-r1: ok, 594 plan records; ports 'route': highest port block end on one route 3564 of 35536 available
- sim-C-C1-L100-n100-codel-r2: ok, 595 plan records; ports 'route': highest port block end on one route 4092 of 35536 available
- sim-C-C1-uneven-n100-pfifo-r1: ok, 868 plan records; ports 'route': highest port block end on one route 4339 of 35536 available
- sim-C-C1-uneven-n100-pfifo-r2: ok, 861 plan records; ports 'route': highest port block end on one route 3577 of 35536 available
- sim-C-C1-uneven-n100-codel-r1: ok, 868 plan records; ports 'route': highest port block end on one route 4339 of 35536 available
- sim-C-C1-uneven-n100-codel-r2: ok, 861 plan records; ports 'route': highest port block end on one route 3577 of 35536 available
- sim-C-C2-L10-n300-pfifo-r1: ok, 2797 plan records; ports 'route': highest port block end on one route 11782 of 35536 available
- sim-C-C2-L10-n300-pfifo-r2: ok, 2780 plan records; ports 'route': highest port block end on one route 14041 of 35536 available
- sim-C-C2-L10-n300-codel-r1: ok, 2797 plan records; ports 'route': highest port block end on one route 11782 of 35536 available
- sim-C-C2-L10-n300-codel-r2: ok, 2780 plan records; ports 'route': highest port block end on one route 14041 of 35536 available
- sim-C-C2-L50-n300-pfifo-r1: ok, 1794 plan records; ports 'route': highest port block end on one route 11474 of 35536 available
- sim-C-C2-L50-n300-pfifo-r2: ok, 1805 plan records; ports 'route': highest port block end on one route 11134 of 35536 available
- sim-C-C2-L50-n300-codel-r1: ok, 1794 plan records; ports 'route': highest port block end on one route 11474 of 35536 available
- sim-C-C2-L50-n300-codel-r2: ok, 1805 plan records; ports 'route': highest port block end on one route 11134 of 35536 available
- sim-C-C2-L100-n300-pfifo-r1: ok, 1671 plan records; ports 'route': highest port block end on one route 9183 of 35536 available
- sim-C-C2-L100-n300-pfifo-r2: ok, 1681 plan records; ports 'route': highest port block end on one route 12402 of 35536 available
- sim-C-C2-L100-n300-codel-r1: ok, 1671 plan records; ports 'route': highest port block end on one route 9183 of 35536 available
- sim-C-C2-L100-n300-codel-r2: ok, 1681 plan records; ports 'route': highest port block end on one route 12402 of 35536 available
- sim-C-C2-uneven-n300-pfifo-r1: ok, 1902 plan records; ports 'route': highest port block end on one route 12133 of 35536 available
- sim-C-C2-uneven-n300-pfifo-r2: ok, 1889 plan records; ports 'route': highest port block end on one route 9820 of 35536 available
- sim-C-C2-uneven-n300-codel-r1: ok, 1902 plan records; ports 'route': highest port block end on one route 12133 of 35536 available
- sim-C-C2-uneven-n300-codel-r2: ok, 1889 plan records; ports 'route': highest port block end on one route 9820 of 35536 available
- sim-C-C3-L10-n1000-pfifo-r1: ok, 9193 plan records; ports 'reuse': highest port block end on one route 2369 of 35536 available
- sim-C-C3-L10-n1000-pfifo-r2: ok, 9154 plan records; ports 'reuse': highest port block end on one route 2369 of 35536 available
- sim-C-C3-L50-n1000-pfifo-r1: ok, 5868 plan records; ports 'reuse': highest port block end on one route 2369 of 35536 available
- sim-C-C3-L50-n1000-pfifo-r2: ok, 5889 plan records; ports 'reuse': highest port block end on one route 2369 of 35536 available
- sim-C-C3-L100-n1000-pfifo-r1: ok, 5473 plan records; ports 'reuse': highest port block end on one route 2369 of 35536 available
- sim-C-C3-L100-n1000-pfifo-r2: ok, 5455 plan records; ports 'reuse': highest port block end on one route 2369 of 35536 available
- sim-C-C3-uneven-n1000-pfifo-r1: ok, 5850 plan records; ports 'reuse': highest port block end on one route 2366 of 35536 available
- sim-C-C3-uneven-n1000-pfifo-r2: ok, 5853 plan records; ports 'reuse': highest port block end on one route 2366 of 35536 available
- sim-C-C4-L50-n1000-pfifo-r1: ok, 5868 plan records; ports 'reuse': highest port block end on one route 1604 of 35536 available
- sim-C-C4-L50-n1000-pfifo-r2: ok, 5889 plan records; ports 'reuse': highest port block end on one route 1604 of 35536 available

## Disk check

free now 236 GB; outputs kept (compressed) 56 GB; peak extra while running (largest raw run + its cache) 20 GB per running 1000-client run; expected free at the end 180 GB (from today's free space)
