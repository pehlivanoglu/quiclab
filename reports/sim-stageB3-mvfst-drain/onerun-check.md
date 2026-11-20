testbed `v4-A1-calm-base-pfifo-r1`; simulation runs: `matched/sim-B-A1-calm-base-pfifo-r1`, `mvfst/sim-B-A1-calm-base-pfifo-r1`

| client | rate Mb/s | testbed: bw/rate, app-lim, ProbeBW / STARTUP, key spread ms | sim matched: bw/rate, app-lim, ProbeBW / STARTUP, key spread ms | sim mvfst: bw/rate, app-lim, ProbeBW / STARTUP, key spread ms |
|---|---|---|---|---|
| sub-a | 1 | 5.21 x, 1.0, 0.0 / 0.992, 2.3 | 5.58 x, 0.999, 0.0 / 1.0, 7.5 | 5.58 x, 0.999, 0.0 / 1.0, 7.5 |
| sub-b | 2.5 | 6.13 x, 0.999, 0.0 / 0.992, 2.3 | 8.44 x, 0.999, 0.0 / 0.98, 5.4 | 8.44 x, 0.999, 0.0 / 0.98, 5.4 |
| sub-c | 2.5 | 4.95 x, 0.999, 0.0 / 0.981, 3.6 | 7.36 x, 0.998, 0.0 / 0.98, 6.4 | 7.36 x, 0.998, 0.0 / 0.98, 6.4 |
| sub-d | 5 | 4.79 x, 0.998, 0.0 / 0.981, 4.8 | 6.78 x, 0.997, 0.0 / 0.98, 6.7 | 6.78 x, 0.997, 0.0 / 0.98, 6.7 |

Keyframe queue peak in calm time, p50 / p90 ms per egress (v3_gate.keyframe_peaks):

- testbed: main 14.1 / 16.9
- sim matched: main 12.6 / 14.9
- sim mvfst: main 12.6 / 14.9
