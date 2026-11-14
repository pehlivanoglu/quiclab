# J1: real per-client jitter and keyframe phases (template evidence, step 1c score)

Jitter: forward, on every access link a1-b3 after the shared bottleneck, netem normal law with the order-keeping `rate` method; the realised spread is lower than the nominal value (probe: 4.0 / 7.1 / 12.6 ms sd for 5 / 10 / 20 ms). Runs per variant: K1 pfifo, no jitter 1, jitter nominal 5 ms (realised sd 4.0 ms) 2, jitter nominal 10 ms (realised sd 7.1 ms) 2, jitter nominal 20 ms (realised sd 12.6 ms) 2, same keyframe phases 2, random keyframe phases 2.

## CONCURRENT (a+b)

| variant | n | L p10 / p50 / p90 | > 11.5 | < 2 | own preferred | n_eff p50 | ratio centred p50 | ratio uncentred p50 |
|---|---|---|---|---|---|---|---|---|
| K1 pfifo, no jitter | 54 | 78.2 / 152.2 / 263.7 | 1.00 | 0.00 | 1.00 | 82 | 6.67 | 6.78 |
| jitter nominal 5 ms (realised sd 4.0 ms) | 108 | 13.1 / 51.0 / 113.3 | 0.91 | 0.02 | 0.98 | 67 | 2.19 | 1.83 |
| jitter nominal 10 ms (realised sd 7.1 ms) | 108 | 5.8 / 32.0 / 102.3 | 0.82 | 0.05 | 0.96 | 66 | 1.77 | 1.43 |
| jitter nominal 20 ms (realised sd 12.6 ms) | 108 | 1.5 / 15.7 / 49.9 | 0.64 | 0.11 | 0.94 | 52 | 1.38 | 1.13 |
| same keyframe phases | 108 | 3.6 / 102.3 / 294.2 | 0.87 | 0.09 | 0.91 | 98 | 3.17 | 3.26 |
| random keyframe phases | 108 | 49.8 / 139.9 / 259.5 | 1.00 | 0.00 | 1.00 | 80 | 5.68 | 5.87 |

Injected noise on the K1 pfifo curves (step 1c, same cell):

| noise | n | L p10 / p50 / p90 | > 11.5 | < 2 | own preferred | n_eff p50 | ratio centred p50 |
|---|---|---|---|---|---|---|---|
| clean | 54 | 78.2 / 152.2 / 263.7 | 1.00 | 0.00 | 1.00 | 82 | 6.67 |
| iid5 | 54 | 53.1 / 98.3 / 163.1 | 1.00 | 0.00 | 1.00 | 90 | 3.26 |
| iid10 | 54 | 20.4 / 51.3 / 100.6 | 0.98 | 0.00 | 1.00 | 85 | 1.97 |
| iid20 | 54 | 3.3 / 19.0 / 48.0 | 0.74 | 0.09 | 0.93 | 91 | 1.26 |
| rw5 | 54 | 6.5 / 12.6 / 43.2 | 0.59 | 0.00 | 1.00 | 10 | 3.59 |
| rw10 | 54 | 2.5 / 6.1 / 18.8 | 0.15 | 0.06 | 1.00 | 9 | 2.09 |
| rw20 | 54 | -0.0 / 4.7 / 10.6 | 0.09 | 0.28 | 0.89 | 9 | 1.73 |

## NESTED (a+up)

| variant | n | L p10 / p50 / p90 | > 11.5 | < 2 | own preferred | n_eff p50 | ratio centred p50 | ratio uncentred p50 |
|---|---|---|---|---|---|---|---|---|
| K1 pfifo, no jitter | 27 | 43.5 / 126.0 / 295.7 | 1.00 | 0.00 | 1.00 | 68 | 5.73 | 5.96 |
| jitter nominal 5 ms (realised sd 4.0 ms) | 54 | 14.0 / 47.2 / 99.2 | 0.91 | 0.04 | 0.96 | 63 | 2.02 | 1.58 |
| jitter nominal 10 ms (realised sd 7.1 ms) | 54 | 3.3 / 42.5 / 83.6 | 0.87 | 0.09 | 0.91 | 64 | 1.91 | 1.44 |
| jitter nominal 20 ms (realised sd 12.6 ms) | 54 | 4.0 / 21.9 / 43.8 | 0.76 | 0.09 | 0.94 | 59 | 1.45 | 1.12 |
| same keyframe phases | 54 | 24.8 / 143.3 / 235.1 | 0.94 | 0.04 | 0.96 | 88 | 4.30 | 4.73 |
| random keyframe phases | 54 | 18.3 / 100.9 / 245.7 | 0.93 | 0.00 | 1.00 | 75 | 5.60 | 5.91 |

## Detector per variant (v2-owd; numbers only)

| variant | runs | false alarms / min p50 | alarm precision p50 | onset spread p50 / p90 ms (median over runs) | measured calm OWD spread ms, jittered clients p50 |
|---|---|---|---|---|---|
| K1 pfifo, no jitter | 1 | 2.24 | 0.90 | 66 / 165 | 1.4 |
| jitter nominal 5 ms (realised sd 4.0 ms) | 2 | 0.73 | 0.96 | 66 / 182 | 5.2 |
| jitter nominal 10 ms (realised sd 7.1 ms) | 2 | 0.70 | 0.97 | 99 / 248 | 9.3 |
| jitter nominal 20 ms (realised sd 12.6 ms) | 2 | 1.06 | 0.95 | 132 / 330 | 16.1 |
| same keyframe phases | 2 | 1.49 | 0.93 | 66 / 198 | 1.9 |
| random keyframe phases | 2 | 1.76 | 0.92 | 66 / 314 | 2.2 |
