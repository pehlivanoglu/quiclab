# Step 2: grouping inside one event without labels

147 runs, 3547 events with windows, 244 negative events (G0, ECG event intervals).

### All events (penalty x1)

| group | events | exact | pair P | pair R | over-split | under-split | quiet in class 0 | congested in class 0 |
|---|---|---|---|---|---|---|---|---|
| all | 3547 | 0.67 | 0.79 | 0.89 | 119 | 606 | 0.99 | 0.13 |

### By event class (penalty x1)

| group | events | exact | pair P | pair R | over-split | under-split | quiet in class 0 | congested in class 0 |
|---|---|---|---|---|---|---|---|---|
| J1 hierjit10 | 162 | 0.38 | 0.61 | 0.83 | 8 | 64 | 1.00 | 0.19 |
| J1 hierjit20 | 162 | 0.33 | 0.61 | 0.76 | 13 | 59 | 1.00 | 0.27 |
| J1 hierjit5 | 162 | 0.40 | 0.58 | 0.87 | 7 | 71 | 1.00 | 0.15 |
| J1 hierrandphase | 162 | 0.38 | 0.59 | 0.86 | 6 | 69 | 1.00 | 0.16 |
| J1 hiersamephase | 162 | 0.43 | 0.62 | 0.83 | 4 | 57 | 1.00 | 0.20 |
| concurrent (K1 a+b, K6 A+C) | 36 | 0.14 | 0.44 | 0.98 | 0 | 29 | 1.00 | 0.04 |
| nested (K1 a+up, K6 levels) | 27 | 0.00 | 0.40 | 0.98 | 0 | 26 | 1.00 | 0.02 |
| overlapping (independent timing) | 344 | 0.01 | 0.48 | 0.65 | 24 | 179 | 1.00 | 0.34 |
| single group | 2240 | 0.92 | 0.99 | 0.96 | 55 | 5 | 0.99 | 0.04 |
| two groups, shifted or overlapping windows | 90 | 0.03 | 0.47 | 0.66 | 2 | 47 | 1.00 | 0.33 |

### Single group: group size 2 vs 3+

| group | events | exact | pair P | pair R | over-split | under-split | quiet in class 0 | congested in class 0 |
|---|---|---|---|---|---|---|---|---|
| group sizes 2 | 81 | 0.51 | 0.87 | 0.51 | 0 | 0 | 0.99 | 0.49 |
| group sizes 3+ | 2159 | 0.93 | 1.00 | 0.96 | 55 | 5 | 0.99 | 0.03 |

### Congested clients placed in class 0, by client bitrate (penalty x1)

| bitrate kb/s | congested (event, client) | in class 0 |
|---|---|---|
| 1000 | 4821 | 0.13 |
| 2500 | 5968 | 0.12 |
| 5000 | 4496 | 0.14 |
| 8000 | 273 | 0.00 |
| 12000 | 69 | 0.00 |

### By AQM

| group | events | exact | pair P | pair R | over-split | under-split | quiet in class 0 | congested in class 0 |
|---|---|---|---|---|---|---|---|---|
| codel | 541 | 0.80 | 0.88 | 0.93 | 10 | 52 | 0.99 | 0.08 |
| pfifo | 1670 | 0.57 | 0.72 | 0.87 | 70 | 412 | 1.00 | 0.15 |
| pie | 668 | 0.76 | 0.85 | 0.94 | 23 | 83 | 0.99 | 0.07 |
| red | 668 | 0.72 | 0.88 | 0.87 | 16 | 59 | 1.00 | 0.16 |

### Penalty sensitivity (all events with windows)

| penalty | exact | over-split | under-split | negatives: events with a data template | negatives: clients outside class 0 |
|---|---|---|---|---|---|
| x1 | 0.67 | 119 | 606 | 239 / 244 | 1182 |
| x0.5 | 0.68 | 168 | 518 | 239 / 244 | 1237 |
| x2 | 0.67 | 91 | 625 | 239 / 244 | 1182 |
| x0 | 0.74 | 582 | 59 | 241 / 244 | 1591 |

(x0 = accept any positive gain: a diagnostic upper bound of the split step, not a proposal.)

### By event class, penalty x0 (diagnostic)

| group | events | exact | pair P | pair R | over-split | under-split | quiet in class 0 | congested in class 0 |
|---|---|---|---|---|---|---|---|---|
| J1 hierjit10 | 162 | 0.91 | 0.97 | 0.93 | 8 | 3 | 0.97 | 0.00 |
| J1 hierjit20 | 162 | 0.82 | 0.93 | 0.86 | 23 | 14 | 0.99 | 0.01 |
| J1 hierjit5 | 162 | 0.89 | 0.97 | 0.88 | 13 | 3 | 0.96 | 0.00 |
| J1 hierrandphase | 162 | 0.64 | 0.86 | 0.83 | 19 | 3 | 0.63 | 0.00 |
| J1 hiersamephase | 162 | 0.69 | 0.88 | 0.84 | 18 | 3 | 0.69 | 0.00 |
| concurrent (K1 a+b, K6 A+C) | 36 | 0.86 | 0.96 | 1.00 | 0 | 0 | 0.78 | 0.00 |
| nested (K1 a+up, K6 levels) | 27 | 0.93 | 0.94 | 0.98 | 1 | 2 | 1.00 | 0.00 |
| overlapping (independent timing) | 344 | 0.89 | 0.92 | 0.98 | 7 | 28 | 1.00 | 0.01 |
| single group | 2240 | 0.68 | 0.94 | 0.79 | 491 | 0 | 0.79 | 0.00 |
| two groups, shifted or overlapping windows | 90 | 0.97 | 0.98 | 0.98 | 2 | 3 | 1.00 | 0.01 |

### G of the first extra-template attempt (penalty x1)

First attempt = the second data template (the first comes from step 2's initial median).

| truth | events | G p10 / p50 / p90 | penalty p50 | accepted |
|---|---|---|---|---|
| one group | 2561 | -24.3 / 0.0 / 91.3 | 420.9 | 0.02 |
| two groups | 977 | 19.9 / 68.2 / 176.6 | 373.1 | 0.02 |
| negatives | 231 | -3.6 / 0.0 / 89.4 | 284.7 | 0.00 |

### Nested events: what the procedure outputs

- two-hop clients share a class with one-hop clients: 232 events
- two-hop clients form their own class: 137 events

### Negatives (G0, single-queue)

244 ECG event intervals; 239 got at least one data template; 1182 client placements outside class 0 in total. By type:

| type | events | events with a data template | clients outside class 0 | ECG events with >= 2 members | data template peak ms p10 / p50 / p90 |
|---|---|---|---|---|---|
| calm065 | 15 | 15 | 60 | 4 | 37.6 / 56.3 / 58.2 |
| calm090 | 36 | 36 | 144 | 20 | 61.5 / 76.5 / 80.6 |
| calmcbr090 | 39 | 39 | 156 | 22 | 45.2 / 55.6 / 57.3 |
| calmsplit | 37 | 37 | 166 | 13 | 52.5 / 74.7 / 109.7 |
| calmtree8 | 45 | 44 | 164 | 4 | 91.4 / 132.0 / 149.1 |
| calmuneven | 54 | 52 | 428 | 17 | 35.6 / 49.0 / 53.6 |
| randloss | 18 | 16 | 64 | 9 | 25.0 / 52.6 / 58.5 |

For comparison, single-group events with windows: data template peak ms p10 / p50 / p90 60.3 / 109.1 / 178.7.

### Cost

- iterations per assignment pass: {1: 3056, 2: 408, 3: 48, 4: 26, 5: 5, 6: 1, 7: 1, 10: 29} (cap 10)
- template comparisons per event p10 / p50 / p90: 37 / 47 / 71; participants per event p50: 6
