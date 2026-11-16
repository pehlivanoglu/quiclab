# Where v2-owd misses

## 1. Stimulus windows: concurrent vs alone (share of expected clients alarming)

| block | AQM | alone: clients alarming (n) | concurrent: clients alarming (n) |
|---|---|---|---|
| C7 | codel | 1.00 (288) | 1.00 (432) |
| C7 | fq_codel | 0.61 (288) | 0.67 (432) |
| C7 | pfifo | 1.00 (288) | 1.00 (432) |
| C7 | pie | 1.00 (288) | 1.00 (432) |
| C8 | pfifo | 1.00 (288) | 1.00 (432) |
| C9 | codel | 1.00 (576) | 1.00 (96) |
| C9 | fq_codel | 0.47 (576) | 0.42 (96) |
| C9 | pfifo | 1.00 (576) | 1.00 (96) |
| C10 | codel | 0.98 (188) | 0.76 (584) |
| C10 | fq_codel | 0.62 (188) | 0.54 (584) |
| C10 | pfifo | 0.99 (188) | 0.78 (584) |
| C11 | codel | 0.99 (179) | 1.00 (636) |
| C11 | pfifo | 0.99 (179) | 0.99 (636) |
| M7 | pfifo | 1.00 (144) | 1.00 (288) |
| M8 | mixab | 0.90 (288) | 0.88 (432) |

## 2. GT-H 600 harmful episodes: hit / missed by AQM and resource

| AQM | resource | harmful episodes | detected | missed: duration p50 / p90 s |
|---|---|---|---|---|
| codel | bottleneck / access egress | 5424 | 0.69 | 0.06 / 2.79 |
| fq_codel | bottleneck / access egress | 5662 | 0.20 | 0.38 / 1.68 |
| mixab | bottleneck / access egress | 485 | 0.51 | 0.30 / 1.58 |
| pfifo | bottleneck / access egress | 7453 | 0.78 | 0.07 / 2.39 |
| pie | bottleneck / access egress | 1369 | 0.52 | 0.09 / 2.79 |
| red | bottleneck / access egress | 65 | 1.00 | - |
