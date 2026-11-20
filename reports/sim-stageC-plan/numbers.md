# Stage C numbers (extrapolated from the 300-client run; rules in simulation/simlab/stagec_numbers.py)

Grid: 42 runs, 9.84 M client-seconds.

## Per run (600 s)

| clients | layout | queue | U | runs | sampled f | raw output GB | zstd output GB | tick cache raw GB | sim min | health min | GT-Q min | detector min | SETS min | GT3 min | of which N^2 input min | peak GB: sim / health / GT-Q / detector / SETS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 | L10 | pfifo | U0.50 | 2 | 0.30 | 2.1 | 0.4 | 0.7 | 4-5 | 2 | 6 | 2 | 1 | 1 | 1 | 0.4 / 2.4 / 2.9 / 0.8 / 1.4 |
| 100 | L10 | codel | U0.50 | 2 | 0.30 | 2.1 | 0.4 | 0.7 | 4-5 | 2 | 6 | 2 | 1 | 1 | 1 | 0.4 / 2.4 / 2.9 / 0.8 / 1.4 |
| 100 | L50 | pfifo | U0.50 | 2 | 1.00 | 3.1 | 0.5 | 0.7 | 4-5 | 6 | 13 | 2 | 1 | 1 | 1 | 0.4 / 5.3 / 6.6 / 0.8 / 1.4 |
| 100 | L50 | codel | U0.50 | 2 | 1.00 | 3.1 | 0.5 | 0.7 | 4-5 | 6 | 13 | 2 | 1 | 1 | 1 | 0.4 / 5.3 / 6.6 / 0.8 / 1.4 |
| 100 | L100 | pfifo | U0.50 | 2 | 1.00 | 3.1 | 0.5 | 0.7 | 4-5 | 6 | 13 | 2 | 1 | 1 | 1 | 0.4 / 5.3 / 6.6 / 0.8 / 1.4 |
| 100 | L100 | codel | U0.50 | 2 | 1.00 | 3.1 | 0.5 | 0.7 | 4-5 | 6 | 13 | 2 | 1 | 1 | 1 | 0.4 / 5.3 / 6.6 / 0.8 / 1.4 |
| 100 | uneven | pfifo | U0.50 | 2 | 1.00 | 3.1 | 0.5 | 0.7 | 4-5 | 6 | 13 | 2 | 1 | 1 | 1 | 0.4 / 5.3 / 6.6 / 0.8 / 1.4 |
| 100 | uneven | codel | U0.50 | 2 | 1.00 | 3.1 | 0.5 | 0.7 | 4-5 | 6 | 13 | 2 | 1 | 1 | 1 | 0.4 / 5.3 / 6.6 / 0.8 / 1.4 |
| 300 | L10 | pfifo | U0.50 | 2 | 0.10 | 5.3 | 1.0 | 2.2 | 14-14 | 5 | 11 | 5 | 6 | 4 | 5 | 0.5 / 4.6 / 5.6 / 2.5 / 4.1 |
| 300 | L10 | codel | U0.50 | 2 | 0.10 | 5.3 | 1.0 | 2.2 | 14-14 | 5 | 11 | 5 | 6 | 4 | 5 | 0.5 / 4.6 / 5.6 / 2.5 / 4.1 |
| 300 | L50 | pfifo | U0.50 | 2 | 0.50 | 7.1 | 1.3 | 2.2 | 14-14 | 10 | 24 | 5 | 6 | 4 | 5 | 0.5 / 9.7 / 11.9 / 2.5 / 4.1 |
| 300 | L50 | codel | U0.50 | 2 | 0.50 | 7.1 | 1.3 | 2.2 | 14-14 | 10 | 24 | 5 | 6 | 4 | 5 | 0.5 / 9.7 / 11.9 / 2.5 / 4.1 |
| 300 | L100 | pfifo | U0.50 | 2 | 1.00 | 9.4 | 1.6 | 2.2 | 14-14 | 17 | 40 | 5 | 6 | 4 | 5 | 0.5 / 16.0 / 19.7 / 2.5 / 4.1 |
| 300 | L100 | codel | U0.50 | 2 | 1.00 | 9.4 | 1.6 | 2.2 | 14-14 | 17 | 40 | 5 | 6 | 4 | 5 | 0.5 / 16.0 / 19.7 / 2.5 / 4.1 |
| 300 | uneven | pfifo | U0.50 | 2 | 0.50 | 7.1 | 1.3 | 2.2 | 14-14 | 10 | 24 | 5 | 6 | 4 | 5 | 0.5 / 9.7 / 11.9 / 2.5 / 4.1 |
| 300 | uneven | codel | U0.50 | 2 | 0.50 | 7.1 | 1.3 | 2.2 | 14-14 | 10 | 24 | 5 | 6 | 4 | 5 | 0.5 / 9.7 / 11.9 / 2.5 / 4.1 |
| 1000 | L10 | pfifo | U0.50 | 2 | 0.00 | 12.5 | 2.7 | 7.4 | 47-63 | 0 | 0 | 18 | 39 | 33 | 57 | 0.9 / 0.0 / 0.0 / 8.4 / 13.7 |
| 1000 | L50 | pfifo | U0.50 | 2 | 0.00 | 12.5 | 2.7 | 7.4 | 47-63 | 0 | 0 | 18 | 39 | 33 | 57 | 0.9 / 0.0 / 0.0 / 8.4 / 13.7 |
| 1000 | L100 | pfifo | U0.50 | 2 | 0.00 | 12.5 | 2.7 | 7.4 | 47-63 | 0 | 0 | 18 | 39 | 33 | 57 | 0.9 / 0.0 / 0.0 / 8.4 / 13.7 |
| 1000 | uneven | pfifo | U0.50 | 2 | 0.00 | 12.5 | 2.7 | 7.4 | 47-63 | 0 | 0 | 18 | 39 | 33 | 57 | 0.9 / 0.0 / 0.0 / 8.4 / 13.7 |
| 1000 | L50 | pfifo | U0.70 | 2 | 0.00 | 12.5 | 2.7 | 7.4 | 66-88 | 0 | 0 | 18 | 39 | 33 | 57 | 0.9 / 0.0 / 0.0 / 8.4 / 13.7 |

## Disk for the grid, by component (GB)

| component | raw | zstd -3 |
|---|---|---|
| router-trace | 75.8 | 10.3 |
| publishers | 174.8 | 38.3 |
| rest | 36.0 | 7.3 |
| onsets+events | 0.0 | 0.0 |
| tick cache | 122.0 | 39.8 |
| **outputs (all but cache)** | **286.6** | **56.0** |

Largest single run in flight: 1000 clients L10: raw output 12.5 GB + its tick cache 7.4 GB raw (outside quiclab/).

## Time for the grid (hours)

| part | hours | how it runs |
|---|---|---|
| simulation | 13.5 - 16.1 core-h | in parallel |
| heavy scoring (health, GT-Q, detector) | 18.8 | one at a time |
| light scoring (SETS, GT3) | 15.1 core-h | beside the heavy queue |
| of which the N^2 input reading (det_eval.Run per flow) | 11.0 core-h | inside SETS and GT3 |

N^2 input reading by size: 100: 0.2 h, 300: 1.4 h, 1000: 9.5 h.
Light scoring at 1000 clients: 12.0 core-h, heavy at 1000: 3.1 h.

## 10,000 clients, no router trace, per 100 simulated seconds (run length not planned)

| quantity | per 100 s simulated |
|---|---|
| raw output / zstd | 20.9 / 4.5 GB |
| tick cache raw / zstd | 12.4 / 4.0 GB |
| simulation | 1.3 - 3.0 h, peak 5.8 GB |
| detector | 31 min, <= 14.0 GB |
| SETS step | 15.7 h (of which N^2 input 15.2 h, pair loop 0.2 h), <= 22.8 GB |
| GT3 step | 15.3 h (of which N^2 input 15.2 h) |
| health | light check only (not written) |
| GT-Q | not run (user) |
