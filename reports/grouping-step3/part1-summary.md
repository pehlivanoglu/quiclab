# Part 1: fixed step 2 procedure (class 0 start, split while gain > 0)

147 runs, 3547 events with windows, 244 negative events. Reference only for Part 2. Columns 'step2 x0' / 'step2 x1' = the old procedure (initial median of all participants) with penalty 0 / 1 on the same events.

### All events

| group | events | fixed exact | fixed pair P | fixed pair R | fixed over | fixed under | fixed quiet in 0 | fixed congested in 0 | step2 x0 exact | step2 x0 pair P | step2 x0 pair R | step2 x0 over | step2 x0 under | step2 x0 quiet in 0 | step2 x0 congested in 0 | step2 x1 exact | step2 x1 pair P | step2 x1 pair R | step2 x1 over | step2 x1 under | step2 x1 quiet in 0 | step2 x1 congested in 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 3547 | 0.74 | 0.94 | 0.84 | 575 | 55 | 0.82 | 0.00 | 0.74 | 0.94 | 0.83 | 581 | 59 | 0.82 | 0.00 | 0.67 | 0.79 | 0.89 | 118 | 606 | 0.99 | 0.13 |

### By event class

| group | events | fixed exact | fixed pair P | fixed pair R | fixed over | fixed under | fixed quiet in 0 | fixed congested in 0 | step2 x0 exact | step2 x0 pair P | step2 x0 pair R | step2 x0 over | step2 x0 under | step2 x0 quiet in 0 | step2 x0 congested in 0 | step2 x1 exact | step2 x1 pair P | step2 x1 pair R | step2 x1 over | step2 x1 under | step2 x1 quiet in 0 | step2 x1 congested in 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| J1 hierjit10 | 162 | 0.91 | 0.97 | 0.93 | 8 | 3 | 0.97 | 0.00 | 0.91 | 0.97 | 0.93 | 8 | 3 | 0.97 | 0.00 | 0.38 | 0.61 | 0.83 | 8 | 64 | 1.00 | 0.19 |
| J1 hierjit20 | 162 | 0.83 | 0.94 | 0.87 | 21 | 12 | 0.99 | 0.00 | 0.82 | 0.93 | 0.86 | 23 | 14 | 0.99 | 0.01 | 0.33 | 0.61 | 0.76 | 13 | 59 | 1.00 | 0.27 |
| J1 hierjit5 | 162 | 0.90 | 0.97 | 0.89 | 12 | 2 | 0.96 | 0.00 | 0.89 | 0.97 | 0.88 | 13 | 3 | 0.96 | 0.00 | 0.40 | 0.58 | 0.87 | 7 | 71 | 1.00 | 0.15 |
| J1 hierrandphase | 162 | 0.64 | 0.86 | 0.83 | 19 | 3 | 0.63 | 0.00 | 0.64 | 0.86 | 0.83 | 19 | 3 | 0.63 | 0.00 | 0.38 | 0.59 | 0.86 | 6 | 69 | 1.00 | 0.16 |
| J1 hiersamephase | 162 | 0.69 | 0.88 | 0.84 | 18 | 3 | 0.69 | 0.00 | 0.69 | 0.88 | 0.84 | 18 | 3 | 0.69 | 0.00 | 0.43 | 0.62 | 0.83 | 4 | 57 | 1.00 | 0.20 |
| concurrent (K1 a+b, K6 A+C) | 36 | 0.86 | 0.96 | 1.00 | 0 | 0 | 0.78 | 0.00 | 0.86 | 0.96 | 1.00 | 0 | 0 | 0.78 | 0.00 | 0.14 | 0.44 | 0.98 | 0 | 29 | 1.00 | 0.04 |
| nested (K1 a+up, K6 levels) | 27 | 0.93 | 0.94 | 0.98 | 1 | 2 | 1.00 | 0.00 | 0.93 | 0.94 | 0.98 | 1 | 2 | 1.00 | 0.00 | 0.00 | 0.40 | 0.98 | 0 | 26 | 1.00 | 0.02 |
| overlapping (independent timing) | 344 | 0.89 | 0.92 | 0.98 | 8 | 29 | 1.00 | 0.01 | 0.89 | 0.92 | 0.98 | 7 | 28 | 1.00 | 0.01 | 0.01 | 0.48 | 0.65 | 24 | 179 | 1.00 | 0.34 |
| single group | 2240 | 0.68 | 0.94 | 0.79 | 488 | 0 | 0.79 | 0.00 | 0.68 | 0.94 | 0.79 | 490 | 0 | 0.79 | 0.00 | 0.92 | 0.99 | 0.96 | 54 | 5 | 0.99 | 0.04 |
| two groups, shifted or overlapping windows | 90 | 0.99 | 0.98 | 1.00 | 0 | 1 | 1.00 | 0.00 | 0.97 | 0.98 | 0.98 | 2 | 3 | 1.00 | 0.01 | 0.03 | 0.47 | 0.66 | 2 | 47 | 1.00 | 0.33 |

### By event class and group size (smallest true group in the event: 2 vs 3 and more)

| group | events | fixed exact | fixed pair P | fixed pair R | fixed over | fixed under | fixed quiet in 0 | fixed congested in 0 | step2 x0 exact | step2 x0 pair P | step2 x0 pair R | step2 x0 over | step2 x0 under | step2 x0 quiet in 0 | step2 x0 congested in 0 | step2 x1 exact | step2 x1 pair P | step2 x1 pair R | step2 x1 over | step2 x1 under | step2 x1 quiet in 0 | step2 x1 congested in 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| J1 hierjit10 / smallest true group 2 | 6 | 1.00 | 1.00 | 1.00 | 0 | 0 | 1.00 | 0.00 | 1.00 | 1.00 | 1.00 | 0 | 0 | 1.00 | 0.00 | 0.00 | 0.38 | 0.94 | 0 | 5 | 1.00 | 0.08 |
| J1 hierjit10 / smallest true group 3+ | 156 | 0.91 | 0.97 | 0.92 | 8 | 3 | 0.97 | 0.00 | 0.91 | 0.97 | 0.92 | 8 | 3 | 0.97 | 0.00 | 0.40 | 0.61 | 0.83 | 8 | 59 | 1.00 | 0.19 |
| J1 hierjit20 / smallest true group 2 | 7 | 1.00 | 1.00 | 1.00 | 0 | 0 | 1.00 | 0.00 | 0.71 | 0.86 | 0.60 | 2 | 2 | 1.00 | 0.21 | 0.00 | 0.38 | 0.45 | 3 | 5 | 1.00 | 0.39 |
| J1 hierjit20 / smallest true group 3+ | 155 | 0.83 | 0.93 | 0.87 | 21 | 12 | 0.99 | 0.00 | 0.83 | 0.93 | 0.87 | 21 | 12 | 0.99 | 0.00 | 0.35 | 0.62 | 0.77 | 10 | 54 | 1.00 | 0.26 |
| J1 hierjit5 / smallest true group 2 | 10 | 1.00 | 1.00 | 1.00 | 0 | 0 | 1.00 | 0.00 | 1.00 | 1.00 | 1.00 | 0 | 0 | 1.00 | 0.00 | 0.10 | 0.47 | 0.74 | 0 | 5 | 1.00 | 0.30 |
| J1 hierjit5 / smallest true group 3+ | 152 | 0.89 | 0.97 | 0.89 | 12 | 2 | 0.96 | 0.00 | 0.88 | 0.97 | 0.88 | 13 | 3 | 0.96 | 0.01 | 0.42 | 0.59 | 0.87 | 7 | 66 | 1.00 | 0.14 |
| J1 hierrandphase / smallest true group 2 | 10 | 1.00 | 1.00 | 1.00 | 0 | 0 | 1.00 | 0.00 | 1.00 | 1.00 | 1.00 | 0 | 0 | 1.00 | 0.00 | 0.00 | 0.42 | 0.91 | 0 | 7 | 1.00 | 0.14 |
| J1 hierrandphase / smallest true group 3+ | 152 | 0.62 | 0.86 | 0.83 | 19 | 3 | 0.61 | 0.00 | 0.62 | 0.86 | 0.83 | 19 | 3 | 0.61 | 0.00 | 0.40 | 0.60 | 0.86 | 6 | 62 | 1.00 | 0.16 |
| J1 hiersamephase / smallest true group 2 | 8 | 1.00 | 1.00 | 1.00 | 0 | 0 | 1.00 | 0.00 | 1.00 | 1.00 | 1.00 | 0 | 0 | 1.00 | 0.00 | 0.38 | 0.60 | 0.75 | 0 | 2 | 1.00 | 0.23 |
| J1 hiersamephase / smallest true group 3+ | 154 | 0.67 | 0.88 | 0.84 | 18 | 3 | 0.67 | 0.00 | 0.67 | 0.88 | 0.84 | 18 | 3 | 0.67 | 0.00 | 0.43 | 0.62 | 0.83 | 4 | 55 | 1.00 | 0.20 |
| concurrent (K1 a+b, K6 A+C) / smallest true group 2 | 9 | 0.44 | 0.69 | 1.00 | 0 | 0 | 0.64 | 0.00 | 0.44 | 0.69 | 1.00 | 0 | 0 | 0.64 | 0.00 | 0.00 | 0.33 | 0.78 | 0 | 7 | 1.00 | 0.22 |
| concurrent (K1 a+b, K6 A+C) / smallest true group 3+ | 27 | 1.00 | 1.00 | 1.00 | 0 | 0 | 1.00 | 0.00 | 1.00 | 1.00 | 1.00 | 0 | 0 | 1.00 | 0.00 | 0.19 | 0.45 | 1.00 | 0 | 22 | 1.00 | 0.00 |
| nested (K1 a+up, K6 levels) / smallest true group 2 | 5 | 0.60 | 0.65 | 0.85 | 1 | 2 | 1.00 | 0.00 | 0.60 | 0.65 | 0.85 | 1 | 2 | 1.00 | 0.00 | 0.00 | 0.40 | 1.00 | 0 | 5 | 1.00 | 0.00 |
| nested (K1 a+up, K6 levels) / smallest true group 3+ | 22 | 1.00 | 1.00 | 1.00 | 0 | 0 | 1.00 | 0.00 | 1.00 | 1.00 | 1.00 | 0 | 0 | 1.00 | 0.00 | 0.00 | 0.41 | 0.98 | 0 | 21 | 1.00 | 0.02 |
| overlapping (independent timing) / smallest true group 2 | 74 | 0.85 | 0.87 | 0.95 | 2 | 8 | 1.00 | 0.03 | 0.86 | 0.88 | 0.96 | 1 | 7 | 1.00 | 0.03 | 0.03 | 0.46 | 0.75 | 10 | 48 | 1.00 | 0.24 |
| overlapping (independent timing) / smallest true group 3+ | 270 | 0.90 | 0.93 | 0.99 | 6 | 21 | 1.00 | 0.01 | 0.90 | 0.93 | 0.99 | 6 | 21 | 1.00 | 0.01 | 0.00 | 0.48 | 0.63 | 14 | 131 | 1.00 | 0.36 |
| single group / smallest true group 2 | 81 | 0.53 | 0.44 | 1.00 | 0 | 0 | 0.58 | 0.00 | 0.53 | 0.44 | 1.00 | 0 | 0 | 0.58 | 0.00 | 0.51 | 0.87 | 0.51 | 0 | 0 | 0.99 | 0.49 |
| single group / smallest true group 3+ | 2159 | 0.68 | 0.95 | 0.79 | 488 | 0 | 0.81 | 0.00 | 0.68 | 0.95 | 0.79 | 490 | 0 | 0.81 | 0.00 | 0.93 | 1.00 | 0.96 | 54 | 5 | 0.99 | 0.03 |
| two groups, shifted or overlapping windows / smallest true group 2 | 13 | 1.00 | 1.00 | 1.00 | 0 | 0 | 1.00 | 0.00 | 0.92 | 0.97 | 0.90 | 1 | 1 | 1.00 | 0.05 | 0.08 | 0.45 | 0.81 | 1 | 9 | 1.00 | 0.18 |
| two groups, shifted or overlapping windows / smallest true group 3+ | 77 | 0.99 | 0.98 | 1.00 | 0 | 1 | 1.00 | 0.00 | 0.97 | 0.98 | 0.99 | 1 | 2 | 1.00 | 0.01 | 0.03 | 0.47 | 0.65 | 1 | 38 | 1.00 | 0.35 |

### By AQM

| group | events | fixed exact | fixed pair P | fixed pair R | fixed over | fixed under | fixed quiet in 0 | fixed congested in 0 | step2 x0 exact | step2 x0 pair P | step2 x0 pair R | step2 x0 over | step2 x0 under | step2 x0 quiet in 0 | step2 x0 congested in 0 | step2 x1 exact | step2 x1 pair P | step2 x1 pair R | step2 x1 over | step2 x1 under | step2 x1 quiet in 0 | step2 x1 congested in 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| codel | 541 | 0.75 | 0.95 | 0.83 | 97 | 6 | 0.87 | 0.00 | 0.75 | 0.95 | 0.84 | 96 | 6 | 0.87 | 0.00 | 0.80 | 0.88 | 0.93 | 10 | 52 | 0.99 | 0.08 |
| pfifo | 1670 | 0.73 | 0.93 | 0.83 | 261 | 30 | 0.80 | 0.00 | 0.73 | 0.93 | 0.83 | 264 | 33 | 0.80 | 0.00 | 0.57 | 0.72 | 0.87 | 69 | 412 | 1.00 | 0.15 |
| pie | 668 | 0.72 | 0.93 | 0.85 | 105 | 14 | 0.81 | 0.01 | 0.72 | 0.93 | 0.85 | 108 | 15 | 0.81 | 0.01 | 0.76 | 0.85 | 0.94 | 23 | 83 | 0.99 | 0.07 |
| red | 668 | 0.75 | 0.95 | 0.84 | 112 | 5 | 0.86 | 0.01 | 0.75 | 0.95 | 0.84 | 113 | 5 | 0.86 | 0.00 | 0.72 | 0.88 | 0.87 | 16 | 59 | 1.00 | 0.16 |

### Negatives (G0)

244 events; with a data template: fixed 222, step2 x0 241; client placements outside class 0: fixed 1338.

Cost: iterations per assignment pass {1: 315, 2: 5281, 3: 180, 4: 33, 5: 4, 6: 6, 9: 1, 10: 19} (cap 10); template comparisons per event p10 / p50 / p90 50 / 77 / 125; data templates per event {0: 41, 1: 1866, 2: 1760, 3: 49, 4: 69, 5: 6}.
