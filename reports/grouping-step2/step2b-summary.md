# Step 2b A: surrogate-calibrated split test

3547 events with windows, single-queue AQMs. Null: the event's single data class keeps its template; members' centred leave-one-out residuals are permuted among them (derangement); the split step runs on each surrogate. Accept the extra template when the observed G exceeds the 0.99 quantile of G* (200 surrogates; only the first extra template is tested).

| event class | events | exact | pair P | pair R | over-split | under-split | one-group events split | two-group events split | congested in class 0 |
|---|---|---|---|---|---|---|---|---|---|
| J1 hierjit10 | 162 | 0.42 | 0.64 | 0.83 | 6 | 54 | 0.06 (n 66) | 0.10 (n 96) | 0.19 |
| J1 hierjit20 | 162 | 0.36 | 0.64 | 0.77 | 11 | 51 | 0.06 (n 66) | 0.12 (n 96) | 0.25 |
| J1 hierjit5 | 162 | 0.43 | 0.61 | 0.88 | 2 | 62 | 0.05 (n 66) | 0.09 (n 96) | 0.14 |
| J1 hierrandphase | 162 | 0.26 | 0.57 | 0.88 | 2 | 65 | 0.35 (n 66) | 0.06 (n 96) | 0.15 |
| J1 hiersamephase | 162 | 0.29 | 0.59 | 0.82 | 3 | 55 | 0.36 (n 66) | 0.09 (n 96) | 0.19 |
| concurrent (K1 a+b, K6 A+C) | 36 | 0.00 | 0.39 | 0.98 | 0 | 34 | nan (n 0) | 0.00 (n 36) | 0.04 |
| nested (K1 a+up, K6 levels) | 27 | 0.11 | 0.43 | 0.98 | 0 | 23 | nan (n 0) | 0.11 (n 27) | 0.02 |
| overlapping (independent timing) | 344 | 0.10 | 0.52 | 0.68 | 6 | 150 | nan (n 0) | 0.11 (n 344) | 0.32 |
| single group | 2240 | 0.84 | 0.97 | 0.93 | 126 | 3 | 0.12 (n 2240) | nan (n 0) | 0.04 |
| two groups, shifted or overlapping windows | 90 | 0.04 | 0.48 | 0.68 | 0 | 44 | nan (n 0) | 0.07 (n 90) | 0.32 |
| all | 3547 | 0.62 | 0.79 | 0.88 | 156 | 541 | 0.13 (n 2570) | 0.10 (n 977) | 0.12 |

ROC area, two-group vs one-group events (events with a split attempt: 832 / 2413): raw G 0.855, surrogate p-value 0.489.

By class (two-group events of that class vs all one-group events):

| class | two-group events | AUC raw G | AUC p-value |
|---|---|---|---|
| J1 hierjit10 | 83 | 0.829 | 0.492 |
| J1 hierjit20 | 78 | 0.776 | 0.509 |
| J1 hierjit5 | 83 | 0.878 | 0.486 |
| J1 hierrandphase | 88 | 0.909 | 0.466 |
| J1 hiersamephase | 79 | 0.888 | 0.489 |
| concurrent (K1 a+b, K6 A+C) | 34 | 0.959 | 0.432 |
| nested (K1 a+up, K6 levels) | 27 | 0.880 | 0.488 |
| overlapping (independent timing) | 286 | 0.830 | 0.500 |
| two groups, shifted or overlapping windows | 74 | 0.885 | 0.473 |

Surrogate count on a subset (411 events, every 10th run):

| surrogates | one-group events split | two-group events split | decision changes vs 200 |
|---|---|---|---|
| 100 | 0.13 | 0.08 | 0 |
| 200 | 0.13 | 0.08 | 0 |
| 500 | 0.13 | 0.08 | 0 |
