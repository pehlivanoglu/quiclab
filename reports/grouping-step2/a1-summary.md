# A1: detector recall (v2-owd) per event and per congested time

Unit: one (client, GT episode) in the client's link view (episodes of the egresses on its path, merged). Rules: *start* = an alarm starts in [t_on - 1 s, min(t_end, t_on + 10 s)] (the current figure); *overlap* = any alarm interval overlaps the episode; *time* = share of congested time covered by an alarm.

### GT1: by all

| group | episodes | recall (start) | recall (overlap) | recall (time) | share of all episodes |
|---|---|---|---|---|---|
| all | 33525 | 0.44 | 0.72 | 0.86 | 1.00 |

### GT1: by duration

| group | episodes | recall (start) | recall (overlap) | recall (time) | share of all episodes |
|---|---|---|---|---|---|
| 0.5-1 s | 3520 | 0.34 | 0.89 | 0.74 | 0.10 |
| 1-2 s | 6573 | 0.72 | 0.98 | 0.81 | 0.20 |
| < 0.5 s | 13752 | 0.07 | 0.36 | 0.34 | 0.41 |
| >= 2 s | 9680 | 0.82 | 0.98 | 0.92 | 0.29 |

### GT1: by scripted or not

| group | episodes | recall (start) | recall (overlap) | recall (time) | share of all episodes |
|---|---|---|---|---|---|
| in a planned window | 24702 | 0.57 | 0.92 | 0.89 | 0.74 |
| unscripted | 8823 | 0.08 | 0.16 | 0.18 | 0.26 |

### GT1: by severity u (planned capacity drops)

| group | episodes | recall (start) | recall (overlap) | recall (time) | share of all episodes |
|---|---|---|---|---|---|
| u=1.05 | 124 | 0.66 | 0.92 | 0.90 | 0.00 |
| u=1.1 | 3722 | 0.53 | 0.94 | 0.92 | 0.11 |
| u=1.2 | 156 | 0.39 | 1.00 | 0.96 | 0.00 |
| u=1.3 | 4006 | 0.51 | 0.94 | 0.93 | 0.12 |
| u=2.0 | 4327 | 0.51 | 0.96 | 0.94 | 0.13 |

### GT1: by scenario family

| group | episodes | recall (start) | recall (overlap) | recall (time) | share of all episodes |
|---|---|---|---|---|---|
| C1 burstlongsplit | 3126 | 0.14 | 0.80 | 0.97 | 0.09 |
| J1 hierjit10 | 1566 | 0.44 | 0.68 | 0.79 | 0.05 |
| J1 hierjit20 | 1767 | 0.40 | 0.66 | 0.75 | 0.05 |
| J1 hierjit5 | 1560 | 0.45 | 0.66 | 0.81 | 0.05 |
| J1 hierrandphase | 1671 | 0.43 | 0.63 | 0.82 | 0.05 |
| J1 hiersamephase | 1518 | 0.47 | 0.67 | 0.83 | 0.05 |
| K1 hier | 2295 | 0.48 | 0.69 | 0.81 | 0.07 |
| K2 part105 | 112 | 0.68 | 0.88 | 0.90 | 0.00 |
| K2 part110 | 112 | 0.65 | 0.81 | 0.92 | 0.00 |
| K2 part115 | 112 | 0.64 | 0.79 | 0.93 | 0.00 |
| K2 part130 | 108 | 0.63 | 0.83 | 0.95 | 0.00 |
| K3 revasym | 92 | 0.78 | 0.86 | 0.84 | 0.00 |
| K3 revcross | 48 | 0.10 | 0.10 | 0.05 | 0.00 |
| K3 revcrossmix | 172 | 0.45 | 0.55 | 0.81 | 0.01 |
| K3 revjit10 | 144 | 0.51 | 0.81 | 0.87 | 0.00 |
| K5 mixed | 667 | 0.45 | 0.65 | 0.81 | 0.02 |
| K6 depth | 1032 | 0.29 | 0.42 | 0.73 | 0.03 |
| M1 burstcap | 512 | 0.60 | 0.83 | 0.86 | 0.02 |
| M1 burstlong | 1000 | 0.15 | 0.96 | 0.99 | 0.03 |
| M1 bursttiny | 456 | 0.63 | 0.64 | 0.52 | 0.01 |
| M1 burstudp | 412 | 0.70 | 0.83 | 0.86 | 0.01 |
| M1 ppbp | 692 | 0.06 | 0.16 | 0.20 | 0.02 |
| M1 ramp | 988 | 0.35 | 0.68 | 0.90 | 0.03 |
| M1 tcpbbr | 320 | 0.75 | 0.85 | 0.94 | 0.01 |
| M1 tcpcubic | 280 | 0.88 | 0.88 | 0.93 | 0.01 |
| M2 burstcaphighrtt | 440 | 0.68 | 0.83 | 0.83 | 0.01 |
| M2 burstcaplowrtt | 448 | 0.65 | 0.92 | 0.90 | 0.01 |
| M2 burstcapq05 | 480 | 0.64 | 0.82 | 0.85 | 0.01 |
| M2 burstcapq15 | 520 | 0.57 | 0.82 | 0.85 | 0.02 |
| M2 burstcapq20 | 516 | 0.59 | 0.82 | 0.86 | 0.02 |
| M3 revjit10 | 564 | 0.54 | 0.83 | 0.86 | 0.02 |
| M3 revjit20 | 580 | 0.55 | 0.83 | 0.85 | 0.02 |
| M3 revjit5 | 504 | 0.59 | 0.80 | 0.85 | 0.02 |
| M4 fps15 | 576 | 0.50 | 0.74 | 0.75 | 0.02 |
| M4 fps60 | 460 | 0.67 | 0.85 | 0.89 | 0.01 |
| M5 bw1 | 396 | 0.74 | 0.98 | 0.89 | 0.01 |
| M5 bw8 | 452 | 0.65 | 0.90 | 0.88 | 0.01 |
| M5 bwmix | 668 | 0.49 | 0.66 | 0.80 | 0.02 |
| M6 gapfast | 420 | 0.68 | 0.94 | 0.88 | 0.01 |
| M6 gapslow | 1092 | 0.30 | 0.43 | 0.75 | 0.03 |
| M6 indepfast | 3117 | 0.49 | 0.84 | 0.87 | 0.09 |
| M6 indepslow | 1530 | 0.40 | 0.58 | 0.77 | 0.05 |

### GT2: by all

| group | episodes | recall (start) | recall (overlap) | recall (time) | share of all episodes |
|---|---|---|---|---|---|
| all | 36710 | 0.39 | 0.55 | 0.83 | 1.00 |

### GT2: by duration

| group | episodes | recall (start) | recall (overlap) | recall (time) | share of all episodes |
|---|---|---|---|---|---|
| 0.5-1 s | 4835 | 0.32 | 0.60 | 0.49 | 0.13 |
| 1-2 s | 5601 | 0.76 | 0.94 | 0.77 | 0.15 |
| < 0.5 s | 17076 | 0.03 | 0.18 | 0.18 | 0.47 |
| >= 2 s | 9198 | 0.87 | 0.98 | 0.91 | 0.25 |

### GT2: by scripted or not

| group | episodes | recall (start) | recall (overlap) | recall (time) | share of all episodes |
|---|---|---|---|---|---|
| in a planned window | 21180 | 0.66 | 0.89 | 0.88 | 0.58 |
| unscripted | 15530 | 0.03 | 0.09 | 0.13 | 0.42 |

### GT2: by severity u (planned capacity drops)

| group | episodes | recall (start) | recall (overlap) | recall (time) | share of all episodes |
|---|---|---|---|---|---|
| u=1.05 | 76 | 0.87 | 0.97 | 0.82 | 0.00 |
| u=1.1 | 2995 | 0.64 | 0.90 | 0.91 | 0.08 |
| u=1.2 | 96 | 0.67 | 1.00 | 0.93 | 0.00 |
| u=1.3 | 3100 | 0.64 | 0.90 | 0.93 | 0.08 |
| u=2.0 | 3326 | 0.66 | 0.92 | 0.94 | 0.09 |

### GT2: by scenario family

| group | episodes | recall (start) | recall (overlap) | recall (time) | share of all episodes |
|---|---|---|---|---|---|
| C1 burstlongsplit | 2124 | 0.20 | 0.49 | 0.96 | 0.06 |
| J1 hierjit10 | 1704 | 0.40 | 0.59 | 0.77 | 0.05 |
| J1 hierjit20 | 1818 | 0.39 | 0.57 | 0.74 | 0.05 |
| J1 hierjit5 | 1836 | 0.38 | 0.52 | 0.79 | 0.05 |
| J1 hierrandphase | 2793 | 0.25 | 0.35 | 0.76 | 0.08 |
| J1 hiersamephase | 2343 | 0.31 | 0.42 | 0.78 | 0.06 |
| K1 hier | 2907 | 0.37 | 0.51 | 0.78 | 0.08 |
| K2 part105 | 108 | 0.68 | 0.83 | 0.89 | 0.00 |
| K2 part110 | 96 | 0.73 | 0.77 | 0.92 | 0.00 |
| K2 part115 | 136 | 0.52 | 0.68 | 0.91 | 0.00 |
| K2 part130 | 112 | 0.61 | 0.80 | 0.92 | 0.00 |
| K3 revasym | 108 | 0.66 | 0.72 | 0.83 | 0.00 |
| K3 revcross | 36 | 0.00 | 0.00 | 0.00 | 0.00 |
| K3 revcrossmix | 192 | 0.41 | 0.49 | 0.83 | 0.01 |
| K3 revjit10 | 140 | 0.53 | 0.66 | 0.84 | 0.00 |
| K5 mixed | 726 | 0.38 | 0.49 | 0.76 | 0.02 |
| K6 depth | 1732 | 0.18 | 0.25 | 0.65 | 0.05 |
| M1 burstcap | 516 | 0.57 | 0.69 | 0.85 | 0.01 |
| M1 burstlong | 416 | 0.36 | 0.86 | 0.99 | 0.01 |
| M1 bursttiny | 520 | 0.51 | 0.52 | 0.53 | 0.01 |
| M1 burstudp | 468 | 0.60 | 0.75 | 0.84 | 0.01 |
| M1 ppbp | 344 | 0.10 | 0.19 | 0.19 | 0.01 |
| M1 ramp | 464 | 0.47 | 0.72 | 0.87 | 0.01 |
| M1 tcpbbr | 332 | 0.72 | 0.80 | 0.94 | 0.01 |
| M1 tcpcubic | 304 | 0.80 | 0.82 | 0.93 | 0.01 |
| M2 burstcaphighrtt | 472 | 0.61 | 0.74 | 0.83 | 0.01 |
| M2 burstcaplowrtt | 480 | 0.60 | 0.74 | 0.90 | 0.01 |
| M2 burstcapq05 | 512 | 0.59 | 0.71 | 0.83 | 0.01 |
| M2 burstcapq15 | 516 | 0.57 | 0.76 | 0.85 | 0.01 |
| M2 burstcapq20 | 516 | 0.59 | 0.77 | 0.87 | 0.01 |
| M3 revjit10 | 528 | 0.57 | 0.74 | 0.86 | 0.01 |
| M3 revjit20 | 564 | 0.53 | 0.74 | 0.85 | 0.02 |
| M3 revjit5 | 552 | 0.53 | 0.70 | 0.84 | 0.02 |
| M4 fps15 | 992 | 0.29 | 0.40 | 0.62 | 0.03 |
| M4 fps60 | 428 | 0.70 | 0.82 | 0.90 | 0.01 |
| M5 bw1 | 340 | 0.84 | 0.96 | 0.87 | 0.01 |
| M5 bw8 | 460 | 0.63 | 0.86 | 0.86 | 0.01 |
| M5 bwmix | 700 | 0.45 | 0.58 | 0.77 | 0.02 |
| M6 gapfast | 420 | 0.65 | 0.90 | 0.88 | 0.01 |
| M6 gapslow | 1372 | 0.24 | 0.31 | 0.63 | 0.04 |
| M6 indepfast | 3321 | 0.46 | 0.73 | 0.85 | 0.09 |
| M6 indepslow | 2262 | 0.27 | 0.39 | 0.72 | 0.06 |

