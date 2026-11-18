## 1.2 Drop windows without a harmful GT-H 600 episode

| AQM group | rep | drop windows (GT-Q valid) | without a harmful episode | share |
|---|---|---|---|---|
| single-queue | r1 | 1027 | 0 | 0.000 |
| single-queue | r2 | 1049 | 1 | 0.001 |
| fq_codel / cake | r1 | 227 | 0 | 0.000 |
| fq_codel / cake | r2 | 235 | 0 | 0.000 |
| all | r1 | 1254 | 0 | 0.000 |
| all | r2 | 1345 | 1 | 0.001 |

## 1.4 Alarm against drop (windows with at least one GOP drop)

#### Single-queue AQM

| detector | drop windows | alarm before the first drop | lead to first drop p10 / p50 / p90 s | drop events | alarm on at the drop | no alarm before the drop |
|---|---|---|---|---|---|---|
| v2-owd | 1039 / 1049 | 0.98 / 0.97 | 1.29 / 2.01 / 4.18 ; 1.25 / 2.00 / 4.00 | 12899 / 13605 | 1.00 / 1.00 | 0.03 / 0.04 |
| D1-bw | 1039 / 1049 | 0.96 / 0.95 | 1.00 / 1.86 / 4.16 ; 0.99 / 1.85 / 4.04 | 12899 / 13605 | 0.85 / 0.85 | 0.10 / 0.09 |
| D2-gcc | 1039 / 1049 | 0.99 / 0.98 | 1.23 / 2.01 / 4.21 ; 1.17 / 2.00 / 4.03 | 12899 / 13605 | 0.01 / 0.01 | 0.01 / 0.01 |
| D3-10ms-200ms | 1039 / 1049 | 0.99 / 0.98 | 1.21 / 1.98 / 4.24 ; 1.15 / 1.96 / 3.99 | 12899 / 13605 | 0.83 / 0.83 | 0.01 / 0.02 |

#### fq_codel / cake

| detector | drop windows | alarm before the first drop | lead to first drop p10 / p50 / p90 s | drop events | alarm on at the drop | no alarm before the drop |
|---|---|---|---|---|---|---|
| v2-owd | 227 / 235 | 0.97 / 0.92 | 1.50 / 1.92 / 3.94 ; 1.48 / 1.86 / 4.01 | 1434 / 1455 | 1.00 / 1.00 | 0.10 / 0.15 |
| D1-bw | 227 / 235 | 0.96 / 0.93 | 0.96 / 1.53 / 3.00 ; 0.99 / 1.34 / 3.35 | 1434 / 1455 | 0.69 / 0.69 | 0.05 / 0.10 |
| D2-gcc | 227 / 235 | 1.00 / 0.97 | 1.39 / 1.89 / 4.10 ; 1.33 / 1.77 / 4.03 | 1434 / 1455 | 0.07 / 0.04 | 0.02 / 0.03 |
| D3-10ms-200ms | 227 / 235 | 0.99 / 0.99 | 1.40 / 1.87 / 4.03 ; 1.38 / 1.76 / 3.91 | 1434 / 1455 | 0.30 / 0.27 | 0.01 / 0.01 |

#### Copa (M13)

| detector | drop windows | alarm before the first drop | lead to first drop p10 / p50 / p90 s | drop events | alarm on at the drop | no alarm before the drop |
|---|---|---|---|---|---|---|
| v2-owd | 26 / 29 | 1.00 / 1.00 | 1.72 / 1.97 / 4.05 ; 1.73 / 2.01 / 3.46 | 223 / 230 | 1.00 / 1.00 | 0.00 / 0.00 |
| D1-bw | 26 / 29 | 0.00 / 0.00 | - / - / - ; - / - / - | 223 / 230 | 0.00 / 0.00 | 1.00 / 1.00 |
| D2-gcc | 26 / 29 | 1.00 / 1.00 | 1.54 / 1.82 / 3.84 ; 1.53 / 1.85 / 3.40 | 223 / 230 | 0.00 / 0.01 | 0.00 / 0.00 |
| D3-10ms-200ms | 26 / 29 | 1.00 / 1.00 | 1.67 / 1.93 / 4.21 ; 1.65 / 1.96 / 3.75 | 223 / 230 | 0.89 / 0.89 | 0.00 / 0.00 |

#### Lead of v2-owd over the first drop by AQM and intensity, pooled reps (p50 s; windows)

| AQM | u 1.05 | u 1.15 | u 1.3 |
|---|---|---|---|
| pfifo | 4.29 (137) | 2.17 (489) | 1.43 (623) |
| codel | 4.38 (82) | 2.81 (246) | 1.95 (326) |
| pie | - | 3.84 (9) | 2.74 (84) |
| red | - | 3.29 (2) | 2.79 (8) |
| fq_codel | 2.49 (66) | 1.85 (173) | 1.79 (188) |

