Runs: testbed 60 (B2 counterparts + cached K1 G1-G3), simulation 22 (stageB2-applimited/matched). Late = onset > first onset + 0.5 s.

## Spread per stimulus by leaf size (ms)

| leaf size | side | runs | stimuli (>= 2 onsets) | p50 | p90 | p98 | max | stimuli > 0.5 s | late members per such stimulus (mean) | lateness p50 / max ms | missed members |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 | testbed | 16 | 456 | 66 | 132 | 396 | 957 | 5 | 1.6 | 776 / 957 | 0 |
| 4 | sim | 10 | 348 | 33 | 99 | 297 | 495 | 0 | 0.0 | nan / nan | 0 |
| 8 | testbed | 13 | 222 | 66 | 231 | 448 | 1122 | 4 | 2.8 | 858 / 1122 | 0 |
| 8 | sim | 4 | 60 | 33 | 165 | 324 | 396 | 0 | 0.0 | nan / nan | 0 |
| 12 | testbed | 3 | 54 | 99 | 264 | 520 | 792 | 2 | 2.0 | 759 / 792 | 0 |
| 16 | testbed | 15 | 243 | 165 | 323 | 500 | 858 | 5 | 2.8 | 561 / 858 | 32 |
| 16 | sim | 2 | 36 | 66 | 314 | 548 | 594 | 2 | 1.5 | 528 / 594 | 0 |
| 24 | testbed | 9 | 135 | 99 | 297 | 572 | 759 | 4 | 5.0 | 528 / 759 | 0 |
| 24 | sim | 2 | 36 | 99 | 379 | 469 | 561 | 1 | 3.0 | 561 / 561 | 0 |
| 40 | testbed | 6 | 108 | 165 | 439 | 556 | 1023 | 5 | 8.6 | 660 / 1023 | 0 |

## Who is late: share of a client's stimuli in which it is late, by attribute (pooled over runs)


### access delay ms

| leaf size | side | access delay ms: late / member-stimuli (share) |
|---|---|---|
| 4 | testbed | 5.0: 2 / 5 (0.40), 7.5: 1 / 5 (0.20), 12.5: 3 / 5 (0.60), 20.0: 2 / 5 (0.40) |
| 8 | testbed | 5.0: 0 / 8 (0.00), 7.5: 4 / 8 (0.50), 12.5: 4 / 8 (0.50), 20.0: 3 / 8 (0.38) |
| 12 | testbed | 5.0: 1 / 6 (0.17), 7.5: 1 / 6 (0.17), 12.5: 1 / 6 (0.17), 20.0: 1 / 6 (0.17) |
| 16 | testbed | 5.0: 1 / 11 (0.09), 7.5: 0 / 8 (0.00), 11.0: 0 / 3 (0.00), 12.5: 1 / 8 (0.12), 17.0: 0 / 3 (0.00), 20.0: 1 / 8 (0.12), 23.0: 0 / 3 (0.00), 29.0: 0 / 3 (0.00), 35.0: 0 / 3 (0.00), 41.0: 0 / 3 (0.00), 47.0: 0 / 3 (0.00), 53.0: 1 / 3 (0.33), 59.0: 1 / 3 (0.33), 65.0: 0 / 3 (0.00), 71.0: 1 / 3 (0.33), 77.0: 2 / 3 (0.67), 83.0: 1 / 3 (0.33), 89.0: 3 / 3 (1.00), 95.0: 2 / 3 (0.67) |
| 16 | sim | 5.0: 0 / 8 (0.00), 7.5: 0 / 8 (0.00), 12.5: 0 / 8 (0.00), 20.0: 3 / 8 (0.38) |
| 24 | testbed | 5.0: 3 / 24 (0.12), 7.5: 4 / 24 (0.17), 12.5: 7 / 24 (0.29), 20.0: 6 / 24 (0.25) |
| 24 | sim | 5.0: 0 / 6 (0.00), 7.5: 0 / 6 (0.00), 12.5: 1 / 6 (0.17), 20.0: 2 / 6 (0.33) |
| 40 | testbed | 5.0: 10 / 50 (0.20), 7.5: 10 / 50 (0.20), 12.5: 9 / 50 (0.18), 20.0: 14 / 50 (0.28) |

### bitrate kb/s

| leaf size | side | bitrate kb/s: late / member-stimuli (share) |
|---|---|---|
| 4 | testbed | 500: 4 / 13 (0.31), 1000: 2 / 3 (0.67), 2500: 1 / 3 (0.33), 5000: 1 / 1 (1.00) |
| 8 | testbed | 500: 11 / 32 (0.34) |
| 12 | testbed | 500: 4 / 24 (0.17) |
| 16 | testbed | 500: 14 / 80 (0.17) |
| 16 | sim | 500: 3 / 32 (0.09) |
| 24 | testbed | 500: 20 / 96 (0.21) |
| 24 | sim | 500: 3 / 24 (0.12) |
| 40 | testbed | 500: 43 / 200 (0.21) |

### position in leaf (0 = first)

| leaf size | side | position in leaf (0 = first): late / member-stimuli (share) |
|---|---|---|
| 4 | testbed | quarter 0: 2 / 5 (0.40), quarter 1: 1 / 5 (0.20), quarter 2: 3 / 5 (0.60), quarter 3: 2 / 5 (0.40) |
| 8 | testbed | quarter 0: 3 / 8 (0.38), quarter 1: 3 / 8 (0.38), quarter 2: 1 / 8 (0.12), quarter 3: 4 / 8 (0.50) |
| 12 | testbed | quarter 0: 0 / 6 (0.00), quarter 1: 0 / 6 (0.00), quarter 2: 3 / 6 (0.50), quarter 3: 1 / 6 (0.17) |
| 16 | testbed | quarter 0: 1 / 20 (0.05), quarter 1: 1 / 20 (0.05), quarter 2: 4 / 20 (0.20), quarter 3: 8 / 20 (0.40) |
| 16 | sim | quarter 0: 2 / 8 (0.25), quarter 1: 0 / 8 (0.00), quarter 2: 1 / 8 (0.12), quarter 3: 0 / 8 (0.00) |
| 24 | testbed | quarter 0: 5 / 24 (0.21), quarter 1: 7 / 24 (0.29), quarter 2: 3 / 24 (0.12), quarter 3: 5 / 24 (0.21) |
| 24 | sim | quarter 0: 0 / 6 (0.00), quarter 1: 2 / 6 (0.33), quarter 2: 0 / 6 (0.00), quarter 3: 1 / 6 (0.17) |
| 40 | testbed | quarter 0: 9 / 50 (0.18), quarter 1: 11 / 50 (0.22), quarter 2: 11 / 50 (0.22), quarter 3: 12 / 50 (0.24) |

## Repeat offenders: clients late in >= 3 stimuli of one run

| side | run | client (late count / stimuli; access ms, kb/s, position) |
|---|---|---|
