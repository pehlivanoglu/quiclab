# Per-client GT1 on fq_codel / cake (development set)

37 runs, 3779 (window, expected client) pairs on pinned egresses.

## Labels: per-client vs aggregate GT1

| AQM | pairs | aggregate says congested | per-client says congested | dropped by per-client | added |
|---|---|---|---|---|---|
| cake | 2400 | 2385 | 1558 | 827 | 0 |
| fq_codel | 1271 | 1259 | 884 | 375 | 0 |
| mixab | 108 | 108 | 71 | 37 | 0 |

## Is the label consistent with the client's own queue and its own OWD?

| AQM | label | pairs | own max backlog kB p10 / p50 / p90 | GT3 (own OWD) episode |
|---|---|---|---|---|
| cake | congested | 1558 | 25.3 / 71.7 / 233.1 | 0.80 |
| cake | not congested | 842 | 5.1 / 11.5 / 26.3 | 0.11 |
| fq_codel | congested | 884 | 32.8 / 71.2 / 113.4 | 0.78 |
| fq_codel | not congested | 387 | 6.9 / 12.7 / 28.3 | 0.03 |
| mixab | congested | 71 | 31.5 / 68.8 / 95.5 | 0.75 |
| mixab | not congested | 37 | 5.1 / 8.9 / 27.8 | 0.00 |

## Share of windows a client is labelled congested, by client bitrate

| AQM | bitrate kb/s | pairs | per-client | aggregate |
|---|---|---|---|---|
| cake | 1000 | 692 | 0.21 | 0.99 |
| cake | 2500 | 998 | 0.76 | 0.99 |
| cake | 5000 | 620 | 0.92 | 0.99 |
| cake | 8000 | 72 | 0.99 | 1.00 |
| cake | 12000 | 18 | 1.00 | 1.00 |
| fq_codel | 1000 | 293 | 0.13 | 0.99 |
| fq_codel | 2500 | 559 | 0.78 | 0.99 |
| fq_codel | 5000 | 419 | 0.98 | 0.99 |
| mixab | 1000 | 36 | 0.14 | 1.00 |
| mixab | 2500 | 36 | 0.83 | 1.00 |
| mixab | 5000 | 36 | 1.00 | 1.00 |

## By campaign

| campaign | AQM | pairs | per-client congested share | aggregate share |
|---|---|---|---|---|
| C1 | fq_codel | 108 | 0.74 | 1.00 |
| K1 | fq_codel | 351 | 0.61 | 1.00 |
| K1 | mixab | 108 | 0.66 | 1.00 |
| K2 | fq_codel | 272 | 0.66 | 1.00 |
| K3 | fq_codel | 216 | 0.73 | 1.00 |
| K5 | fq_codel | 72 | 0.58 | 0.83 |
| K6 | fq_codel | 252 | 0.84 | 1.00 |
| M1 | cake | 648 | 0.57 | 1.00 |
| M2 | cake | 360 | 0.70 | 1.00 |
| M3 | cake | 216 | 0.71 | 1.00 |
| M4 | cake | 144 | 0.71 | 1.00 |
| M5 | cake | 216 | 0.81 | 1.00 |
| M6 | cake | 816 | 0.62 | 0.98 |
