# Step 6 tables

Every row is one run. sync = phase 0 for all clients; stag = staggered phases. Pair counts are pair-closes (a wrong pair counted at every close at which it is decided SAME).

## Headline per run

| scenario | phase | rep | ECG final P / R / cov, tree | ECG events; GLOBAL share | h3 final P / R / cov; pooled P | ECG wrong pair-closes shared in that event | h3 wrong pair-closes shared |
|---|---|---|---|---|---|---|---|
| base calm065 | sync | 1 | - / - / 0.00, ok | 1; 0.00 | - | 0/0 (-) | - |
| base calm065 | sync | 2 | - / - / 0.00, ok | 9; 0.00 | - | 0/0 (-) | - |
| base calm065 | stag | 1 | - / - / 0.00, ok | 3; 0.00 | - | 0/0 (-) | - |
| base burstcap | sync | 1 | 1.00 / 1.00 / 0.60, ok | 24; 0.00 | 1.00 / 1.00 / 0.60; 1.00 | 0/0 (-) | 0/0 (-) |
| base burstcap | sync | 2 | 1.00 / 1.00 / 0.60, ok | 24; 0.00 | 1.00 / 1.00 / 0.60; 1.00 | 0/0 (-) | 0/0 (-) |
| base burstcap | stag | 1 | 1.00 / 1.00 / 0.60, ok | 22; 0.00 | 1.00 / 1.00 / 0.60; 1.00 | 0/0 (-) | 0/0 (-) |
| K1 hier | sync | 1 | 1.00 / 1.00 / 0.71, ok | 116; 0.20 | 1.00 / 1.00 / 0.71; 0.93 | 9/90 (0.10) | 48/63 (0.76) |
| K1 hier | sync | 2 | 1.00 / 1.00 / 0.71, ok | 93; 0.24 | 1.00 / 1.00 / 0.71; 0.93 | 81/117 (0.69) | 39/48 (0.81) |
| K1 hier | stag | 1 | 1.00 / 1.00 / 0.71, ok | 125; 0.21 | 1.00 / 1.00 / 0.71; 0.94 | 0/0 (-) | 26/52 (0.50) |
| K1 hier | stag | 2 | 1.00 / 1.00 / 0.71, ok | 131; 0.15 | 1.00 / 1.00 / 0.71; 0.99 | 38/225 (0.17) | 3/3 (1.00) |
| C1 burstlongsplit | sync | 1 | 1.00 / 1.00 / 0.05, no | 52; 0.17 | 0.75 / 1.00 / 0.71; 0.65 | 0/0 (-) | 99/124 (0.80) |
| C1 burstlongsplit | sync | 2 | 1.00 / 1.00 / 0.48, no | 44; 0.05 | 1.00 / 1.00 / 0.71; 0.75 | 111/159 (0.70) | 99/117 (0.85) |
| C1 burstlongsplit | sync | 3 | 0.40 / 1.00 / 0.71, no | 47; 0.00 | 1.00 / 1.00 / 0.71; 0.69 | 150/313 (0.48) | 79/100 (0.79) |
| C1 burstlongsplit | sync | 4 | 1.00 / 1.00 / 0.48, no | 44; 0.18 | 1.00 / 0.67 / 0.71; 0.70 | 0/0 (-) | 94/94 (1.00) |
| C1 burstlongsplit | stag | 1 | 1.00 / 1.00 / 0.48, no | 58; 0.14 | 1.00 / 1.00 / 0.71; 0.98 | 0/0 (-) | 3/6 (0.50) |
| C1 burstlongsplit | stag | 2 | 1.00 / 1.00 / 0.48, no | 56; 0.05 | 1.00 / 1.00 / 0.71; 0.90 | 24/153 (0.16) | 15/24 (0.62) |
| K6 depth | sync | 1 | 1.00 / 1.00 / 0.42, no | 132; 0.08 | 0.67 / 1.00 / 0.78; 0.44 | 40/56 (0.71) | 496/672 (0.74) |
| K6 depth | sync | 2 | 1.00 / 1.00 / 0.78, ok | 122; 0.10 | 0.36 / 1.00 / 0.78; 0.35 | 13/16 (0.81) | 644/849 (0.76) |
| K6 depth | sync | 3 | 1.00 / 1.00 / 0.78, ok | 126; 0.07 | 0.25 / 1.00 / 0.78; 0.38 | 0/0 (-) | 652/792 (0.82) |
| K6 depth | sync | 4 | 1.00 / 1.00 / 0.58, no | 135; 0.07 | 0.50 / 1.00 / 0.78; 0.46 | 112/142 (0.79) | 471/621 (0.76) |
| K6 depth | stag | 1 | 1.00 / 1.00 / 0.78, ok | 132; 0.08 | 1.00 / 1.00 / 0.78; 0.97 | 58/176 (0.33) | 14/16 (0.88) |
| K6 depth | stag | 2 | 0.50 / 1.00 / 0.78, no | 143; 0.06 | 1.00 / 1.00 / 0.78; 0.88 | 238/1634 (0.15) | 43/77 (0.56) |

## Item 1: wrong by the same-leaf truth, shared in that event or not

| scenario | phase | rep | ECG pair-closes: wrong / shared / not shared | ECG memberships: declared / wrong / shared / not | h3 pair-closes: wrong / shared / not | h3 memberships: declared / wrong / shared / not |
|---|---|---|---|---|---|---|
| base burstcap | sync | 1 | 0 / 0 / 0 | 5 / 0 / 0 / 0 | 0 / 0 / 0 | 4 / 0 / 0 / 0 |
| base burstcap | sync | 2 | 0 / 0 / 0 | 4 / 0 / 0 / 0 | 0 / 0 / 0 | 4 / 0 / 0 / 0 |
| base burstcap | stag | 1 | 0 / 0 / 0 | 4 / 0 / 0 / 0 | 0 / 0 / 0 | 4 / 0 / 0 / 0 |
| K1 hier | sync | 1 | 90 / 9 / 81 | 22 / 2 / 1 / 1 | 63 / 48 / 15 | 34 / 12 / 12 / 0 |
| K1 hier | sync | 2 | 117 / 81 / 36 | 16 / 6 / 0 / 6 | 48 / 39 / 9 | 20 / 10 / 4 / 6 |
| K1 hier | stag | 1 | 0 / 0 / 0 | 10 / 0 / 0 / 0 | 52 / 26 / 26 | 33 / 11 / 10 / 1 |
| K1 hier | stag | 2 | 225 / 38 / 187 | 23 / 7 / 3 / 4 | 3 / 3 / 0 | 7 / 1 / 1 / 0 |
| C1 burstlongsplit | sync | 1 | 0 / 0 / 0 | 15 / 0 / 0 / 0 | 124 / 99 / 25 | 39 / 14 / 14 / 0 |
| C1 burstlongsplit | sync | 2 | 159 / 111 / 48 | 24 / 6 / 4 / 2 | 117 / 99 / 18 | 40 / 13 / 13 / 0 |
| C1 burstlongsplit | sync | 3 | 313 / 150 / 163 | 11 / 7 / 5 / 2 | 100 / 79 / 21 | 48 / 13 / 13 / 0 |
| C1 burstlongsplit | sync | 4 | 0 / 0 / 0 | 27 / 0 / 0 / 0 | 94 / 94 / 0 | 41 / 17 / 17 / 0 |
| C1 burstlongsplit | stag | 1 | 0 / 0 / 0 | 21 / 0 / 0 / 0 | 6 / 3 / 3 | 9 / 1 / 1 / 0 |
| C1 burstlongsplit | stag | 2 | 153 / 24 / 129 | 22 / 5 / 1 / 4 | 24 / 15 / 9 | 14 / 4 / 4 / 0 |
| K6 depth | sync | 1 | 56 / 40 / 16 | 26 / 6 / 6 / 0 | 672 / 496 / 176 | 121 / 72 / 53 / 19 |
| K6 depth | sync | 2 | 16 / 13 / 3 | 28 / 6 / 5 / 1 | 849 / 644 / 205 | 121 / 71 / 49 / 22 |
| K6 depth | sync | 3 | 0 / 0 / 0 | 19 / 0 / 0 / 0 | 792 / 652 / 140 | 81 / 53 / 47 / 6 |
| K6 depth | sync | 4 | 142 / 112 / 30 | 30 / 5 / 5 / 0 | 621 / 471 / 150 | 126 / 78 / 60 / 18 |
| K6 depth | stag | 1 | 176 / 58 / 118 | 22 / 6 / 3 / 3 | 16 / 14 / 2 | 19 / 7 / 7 / 0 |
| K6 depth | stag | 2 | 1634 / 238 / 1396 | 33 / 25 / 12 / 13 | 77 / 43 / 34 | 45 / 23 / 14 / 9 |

## Item 2: ECG events by case

| scenario | phase | rep | events | A | B | C | D | SOLO | GLOBAL | GLOBAL with upstream/root congested | members per event p50 | upstream / root congested share of events | final coverage; members at the end |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base calm065 | sync | 1 | 1 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0/0 | 1 |  | 0.00; 0 |
| base calm065 | sync | 2 | 9 | 0.00 | 0.00 | 0.00 | 0.11 | 0.89 | 0.00 | 0/0 | 1 |  | 0.00; 0 |
| base calm065 | stag | 1 | 3 | 0.00 | 0.00 | 0.00 | 0.67 | 0.33 | 0.00 | 0/0 | 2 |  | 0.00; 0 |
| base burstcap | sync | 1 | 24 | 0.71 | 0.00 | 0.00 | 0.04 | 0.25 | 0.00 | 0/0 | 4 |  | 0.60; 4 |
| base burstcap | sync | 2 | 24 | 0.67 | 0.00 | 0.08 | 0.04 | 0.21 | 0.00 | 0/0 | 3 |  | 0.60; 4 |
| base burstcap | stag | 1 | 22 | 0.77 | 0.00 | 0.00 | 0.05 | 0.18 | 0.00 | 0/0 | 4 |  | 0.60; 4 |
| K1 hier | sync | 1 | 116 | 0.43 | 0.00 | 0.09 | 0.04 | 0.23 | 0.20 | 19/23 | 3 | r1->r2 0.46 | 0.71; 6 |
| K1 hier | sync | 2 | 93 | 0.56 | 0.00 | 0.10 | 0.01 | 0.10 | 0.24 | 17/22 | 3 | r1->r2 0.60 | 0.71; 6 |
| K1 hier | stag | 1 | 125 | 0.48 | 0.00 | 0.02 | 0.02 | 0.28 | 0.21 | 18/26 | 3 | r1->r2 0.20 | 0.71; 6 |
| K1 hier | stag | 2 | 131 | 0.42 | 0.00 | 0.10 | 0.02 | 0.31 | 0.15 | 14/20 | 3 | r1->r2 0.25 | 0.71; 6 |
| C1 burstlongsplit | sync | 1 | 52 | 0.35 | 0.00 | 0.00 | 0.06 | 0.42 | 0.17 | 9/9 | 2 | r1->r2 0.60 | 0.05; 2 |
| C1 burstlongsplit | sync | 2 | 44 | 0.39 | 0.00 | 0.25 | 0.02 | 0.30 | 0.05 | 2/2 | 3 | r1->r2 0.57 | 0.48; 5 |
| C1 burstlongsplit | sync | 3 | 47 | 0.23 | 0.00 | 0.38 | 0.02 | 0.36 | 0.00 | 0/0 | 3 | r1->r2 0.53 | 0.71; 6 |
| C1 burstlongsplit | sync | 4 | 44 | 0.41 | 0.00 | 0.05 | 0.07 | 0.30 | 0.18 | 8/8 | 3 | r1->r2 0.70 | 0.48; 5 |
| C1 burstlongsplit | stag | 1 | 58 | 0.43 | 0.00 | 0.00 | 0.03 | 0.40 | 0.14 | 8/8 | 2 | r1->r2 0.33 | 0.48; 5 |
| C1 burstlongsplit | stag | 2 | 56 | 0.38 | 0.00 | 0.14 | 0.02 | 0.41 | 0.05 | 3/3 | 2 | r1->r2 0.29 | 0.48; 5 |
| K6 depth | sync | 1 | 132 | 0.32 | 0.13 | 0.05 | 0.06 | 0.37 | 0.08 | 10/10 | 2 | r0->r1 0.33, r0->r2 0.42, rr->r0 0.57 | 0.42; 6 |
| K6 depth | sync | 2 | 122 | 0.27 | 0.15 | 0.07 | 0.05 | 0.37 | 0.10 | 10/12 | 2 | r0->r1 0.26, r0->r2 0.43, rr->r0 0.57 | 0.78; 8 |
| K6 depth | sync | 3 | 126 | 0.32 | 0.17 | 0.00 | 0.06 | 0.37 | 0.07 | 9/9 | 2 | r0->r1 0.26, r0->r2 0.52, rr->r0 0.74 | 0.78; 8 |
| K6 depth | sync | 4 | 135 | 0.31 | 0.08 | 0.07 | 0.07 | 0.41 | 0.07 | 9/9 | 2 | r0->r1 0.18, r0->r2 0.38, rr->r0 0.69 | 0.58; 7 |
| K6 depth | stag | 1 | 132 | 0.26 | 0.11 | 0.10 | 0.04 | 0.42 | 0.08 | 9/11 | 2 | r0->r1 0.20, r0->r2 0.27, rr->r0 0.11 | 0.78; 8 |
| K6 depth | stag | 2 | 143 | 0.17 | 0.01 | 0.28 | 0.01 | 0.47 | 0.06 | 8/9 | 2 | r0->r1 0.13, r0->r2 0.23, rr->r0 0.09 | 0.78; 8 |

Coverage over ECG closes (every 10th close):

- C1 burstlongsplit sync r1: 0.00 0.05 0.48 0.29 0.05 0.05 | last 0.05
- C1 burstlongsplit sync r2: 0.00 0.71 0.71 0.71 0.48 | last 0.48
- C1 burstlongsplit sync r3: 0.00 0.71 0.71 0.71 0.71 | last 0.71
- C1 burstlongsplit sync r4: 0.00 0.71 0.48 0.71 0.71 | last 0.48
- C1 burstlongsplit stag r1: 0.00 0.48 0.71 0.71 0.29 0.29 | last 0.48
- C1 burstlongsplit stag r2: 0.00 0.14 0.71 0.71 0.48 0.48 | last 0.48
- K6 depth sync r1: 0.00 0.03 0.03 0.17 0.42 0.17 0.42 0.28 0.58 0.42 0.58 0.42 0.42 0.42 | last 0.42
- K6 depth sync r2: 0.00 0.08 0.17 0.17 0.78 0.78 0.78 0.58 0.58 0.78 0.78 0.78 0.78 | last 0.78
- K6 depth sync r3: 0.00 0.00 0.03 0.17 0.78 0.78 0.78 0.78 0.78 0.78 0.78 0.78 0.78 | last 0.78
- K6 depth sync r4: 0.00 0.17 0.08 0.08 0.17 0.17 0.58 0.58 0.78 0.78 0.78 0.78 0.78 0.78 | last 0.58
- K6 depth stag r1: 0.00 0.00 0.00 0.42 0.78 0.58 0.58 0.78 0.78 0.78 0.78 0.78 0.78 0.78 | last 0.78
- K6 depth stag r2: 0.00 0.78 0.78 0.78 0.78 0.78 0.78 0.78 0.78 0.78 0.78 0.78 0.78 0.78 0.78 | last 0.78

## Item 3: subtracting the common component (sync K1, C1, K6)

Per event: congested = not class 0 after the Part 1 procedure; leaf truth = participants whose leaf egress has a GT1 episode in the event. P / R = congested vs leaf truth over all events; exact = share of events where the two sets are equal.

| scenario | rep | before: congested p50 / leaf truth p50, P / R, exact | after: congested p50, P / R, exact | B1 own before: O-- / OX- / --U (votes) | B1 own after: O-- / OX- / --U (votes) |
|---|---|---|---|---|---|
| K1 hier | 1 | 6 / 6, 0.78 / 1.00, 0.64 | 0, 0.81 / 0.48, 0.20 | 1.00 (30) / 1.00 (315) / 0.50 (48) | 1.00 (24) / 1.00 (153) / - (0) |
| K1 hier | 2 | 6 / 6, 0.77 / 1.00, 0.62 | 0, 0.71 / 0.45, 0.17 | 1.00 (33) / 1.00 (154) / 0.62 (42) | 1.00 (30) / 1.00 (54) / - (0) |
| C1 burstlongsplit | 1 | 6 / 3, 0.56 / 0.99, 0.37 | 6, 0.65 / 0.76, 0.27 | 1.00 (32) / 1.00 (53) / 0.29 (78) | 1.00 (32) / 1.00 (40) / - (0) |
| C1 burstlongsplit | 2 | 6 / 3, 0.63 / 0.99, 0.45 | 4, 0.72 / 0.67, 0.27 | 1.00 (21) / 1.00 (65) / 0.13 (53) | 1.00 (21) / 1.00 (52) / - (0) |
| C1 burstlongsplit | 3 | 6 / 3, 0.52 / 0.99, 0.32 | 6, 0.70 / 0.83, 0.32 | 1.00 (30) / 1.00 (66) / 0.33 (78) | 1.00 (24) / 1.00 (59) / - (0) |
| C1 burstlongsplit | 4 | 6 / 3, 0.49 / 1.00, 0.27 | 6, 0.62 / 0.87, 0.32 | 1.00 (18) / 1.00 (42) / 0.36 (75) | 1.00 (18) / 1.00 (42) / - (0) |
| K6 depth | 1 | 8 / 4, 0.46 / 0.97, 0.06 | 5, 0.49 / 0.64, 0.14 | 0.98 (290) / 0.99 (212) / 0.65 (504) | 0.99 (184) / 1.00 (144) / 0.74 (144) |
| K6 depth | 2 | 8 / 4, 0.39 / 0.98, 0.06 | 6, 0.42 / 0.72, 0.14 | 0.98 (260) / 0.98 (164) / 0.57 (684) | 1.00 (146) / 0.97 (136) / 0.52 (232) |
| K6 depth | 3 | 8 / 4, 0.45 / 1.00, 0.10 | 6, 0.48 / 0.68, 0.15 | 0.97 (146) / 1.00 (88) / 0.71 (700) | 1.00 (116) / 1.00 (76) / 0.73 (212) |
| K6 depth | 4 | 8 / 4, 0.48 / 0.99, 0.07 | 5, 0.48 / 0.61, 0.05 | 1.00 (198) / 0.97 (144) / 0.67 (564) | 1.00 (134) / 1.00 (92) / 0.73 (136) |

## Item 4: keyframe queue peaks (calm time)

Peak = maximum egress queueing delay in [T, T + 0.5 s] after each keyframe time T; model = load x 4/33 s.

| scenario | phase | rep | egress | load | model ms | peak p50 / p90 / max ms | peak / model (p50) | sample ms |
|---|---|---|---|---|---|---|---|---|
| base calm065 | sync | 1 | router->switch | 0.67 | 81 | 53.2 / 56.9 / 58.0 | 0.66 | 25.0 |
| base calm065 | sync | 2 | router->switch | 0.67 | 81 | 51.6 / 55.0 / 57.9 | 0.64 | 25.0 |
| base calm065 | stag | 1 | router->switch | 0.67 | 81 | 14.2 / 23.1 / 37.6 | 0.18 | 25.0 |
| K1 hier | sync | 1 | r1->r2 | 0.68 | 82 | 36.8 / 48.1 / 59.9 | 0.45 | 5.0 |
| K1 hier | sync | 1 | r2->switch-a | 0.68 | 82 | 6.8 / 15.4 / 60.4 | 0.08 | 5.0 |
| K1 hier | sync | 1 | r2->switch-b | 0.68 | 83 | 7.0 / 18.1 / 60.4 | 0.08 | 5.0 |
| K1 hier | sync | 2 | r1->r2 | 0.68 | 82 | 36.9 / 47.6 / 59.4 | 0.45 | 5.0 |
| K1 hier | sync | 2 | r2->switch-a | 0.68 | 82 | 6.8 / 14.2 / 59.8 | 0.08 | 5.0 |
| K1 hier | sync | 2 | r2->switch-b | 0.68 | 83 | 6.8 / 16.3 / 60.4 | 0.08 | 5.0 |
| K1 hier | stag | 1 | r1->r2 | 0.68 | 82 | 4.1 / 5.8 / 49.2 | 0.05 | 5.0 |
| K1 hier | stag | 1 | r2->switch-a | 0.68 | 82 | 7.7 / 12.1 / 60.4 | 0.09 | 5.0 |
| K1 hier | stag | 1 | r2->switch-b | 0.68 | 82 | 8.0 / 11.9 / 59.6 | 0.10 | 5.0 |
| K1 hier | stag | 2 | r1->r2 | 0.68 | 82 | 3.9 / 6.0 / 60.1 | 0.05 | 5.0 |
| K1 hier | stag | 2 | r2->switch-a | 0.68 | 82 | 7.7 / 11.4 / 58.8 | 0.09 | 5.0 |
| K1 hier | stag | 2 | r2->switch-b | 0.68 | 82 | 7.5 / 10.9 / 60.4 | 0.09 | 5.0 |
| K6 depth | sync | 1 | r0->r1 | 0.67 | 82 | 6.9 / 15.2 / 53.5 | 0.08 | 5.0 |
| K6 depth | sync | 1 | r0->r2 | 0.67 | 82 | 8.6 / 17.9 / 50.2 | 0.10 | 5.0 |
| K6 depth | sync | 1 | r1->switch-a | 0.67 | 82 | 6.8 / 14.6 / 73.7 | 0.08 | 5.0 |
| K6 depth | sync | 1 | r1->switch-b | 0.67 | 82 | 6.8 / 14.2 / 72.8 | 0.08 | 5.0 |
| K6 depth | sync | 1 | r2->switch-c | 0.67 | 82 | 7.8 / 24.6 / 73.7 | 0.10 | 5.0 |
| K6 depth | sync | 1 | r2->switch-d | 0.67 | 82 | 8.5 / 30.5 / 72.7 | 0.10 | 5.0 |
| K6 depth | sync | 1 | rr->r0 | 0.67 | 82 | 28.2 / 40.2 / 73.6 | 0.35 | 5.0 |
| K6 depth | sync | 2 | r0->r1 | 0.68 | 82 | 6.5 / 13.1 / 62.7 | 0.08 | 5.0 |
| K6 depth | sync | 2 | r0->r2 | 0.67 | 82 | 8.1 / 15.3 / 67.8 | 0.10 | 5.0 |
| K6 depth | sync | 2 | r1->switch-a | 0.68 | 82 | 6.8 / 12.7 / 66.0 | 0.08 | 5.0 |
| K6 depth | sync | 2 | r1->switch-b | 0.68 | 82 | 6.3 / 12.4 / 73.7 | 0.08 | 5.0 |
| K6 depth | sync | 2 | r2->switch-c | 0.68 | 82 | 7.6 / 16.3 / 73.7 | 0.09 | 5.0 |
| K6 depth | sync | 2 | r2->switch-d | 0.67 | 82 | 7.7 / 16.6 / 73.7 | 0.09 | 5.0 |
| K6 depth | sync | 2 | rr->r0 | 0.68 | 82 | 27.4 / 36.5 / 73.3 | 0.33 | 5.0 |
| K6 depth | sync | 3 | r0->r1 | 0.67 | 82 | 7.3 / 15.5 / 48.8 | 0.09 | 5.0 |
| K6 depth | sync | 3 | r0->r2 | 0.67 | 82 | 9.2 / 18.2 / 57.0 | 0.11 | 5.0 |
| K6 depth | sync | 3 | r1->switch-a | 0.68 | 82 | 6.8 / 18.7 / 72.9 | 0.08 | 5.0 |
| K6 depth | sync | 3 | r1->switch-b | 0.67 | 82 | 6.8 / 18.2 / 72.0 | 0.08 | 5.0 |
| K6 depth | sync | 3 | r2->switch-c | 0.68 | 82 | 7.3 / 21.7 / 73.7 | 0.09 | 5.0 |
| K6 depth | sync | 3 | r2->switch-d | 0.67 | 81 | 7.9 / 21.1 / 73.7 | 0.10 | 5.0 |
| K6 depth | sync | 3 | rr->r0 | 0.68 | 82 | 28.1 / 38.7 / 71.0 | 0.34 | 5.0 |
| K6 depth | sync | 4 | r0->r1 | 0.67 | 82 | 7.5 / 13.9 / 41.6 | 0.09 | 5.0 |
| K6 depth | sync | 4 | r0->r2 | 0.67 | 82 | 9.2 / 16.3 / 52.9 | 0.11 | 5.0 |
| K6 depth | sync | 4 | r1->switch-a | 0.68 | 82 | 6.9 / 23.8 / 66.8 | 0.08 | 5.0 |
| K6 depth | sync | 4 | r1->switch-b | 0.67 | 82 | 6.8 / 26.8 / 73.0 | 0.08 | 5.0 |
| K6 depth | sync | 4 | r2->switch-c | 0.68 | 82 | 8.6 / 26.1 / 73.7 | 0.10 | 5.0 |
| K6 depth | sync | 4 | r2->switch-d | 0.67 | 81 | 9.5 / 24.5 / 73.7 | 0.12 | 5.0 |
| K6 depth | sync | 4 | rr->r0 | 0.68 | 82 | 28.7 / 43.1 / 70.5 | 0.35 | 5.0 |
| K6 depth | stag | 1 | r0->r1 | 0.67 | 82 | 6.0 / 12.0 / 31.9 | 0.07 | 5.0 |
| K6 depth | stag | 1 | r0->r2 | 0.67 | 82 | 4.5 / 7.3 / 32.4 | 0.06 | 5.0 |
| K6 depth | stag | 1 | r1->switch-a | 0.68 | 82 | 16.6 / 25.4 / 73.7 | 0.20 | 5.0 |
| K6 depth | stag | 1 | r1->switch-b | 0.67 | 82 | 17.6 / 25.1 / 72.8 | 0.22 | 5.0 |
| K6 depth | stag | 1 | r2->switch-c | 0.68 | 82 | 9.4 / 17.6 / 73.7 | 0.12 | 5.0 |
| K6 depth | stag | 1 | r2->switch-d | 0.67 | 82 | 4.6 / 8.2 / 73.7 | 0.06 | 5.0 |
| K6 depth | stag | 1 | rr->r0 | 0.68 | 82 | 9.8 / 16.7 / 28.2 | 0.12 | 5.0 |
| K6 depth | stag | 2 | r0->r1 | 0.67 | 82 | 5.6 / 8.6 / 48.8 | 0.07 | 5.0 |
| K6 depth | stag | 2 | r0->r2 | 0.67 | 82 | 4.3 / 6.4 / 60.5 | 0.05 | 5.0 |
| K6 depth | stag | 2 | r1->switch-a | 0.68 | 82 | 15.2 / 22.2 / 73.7 | 0.18 | 5.0 |
| K6 depth | stag | 2 | r1->switch-b | 0.67 | 82 | 16.2 / 22.8 / 72.8 | 0.20 | 5.0 |
| K6 depth | stag | 2 | r2->switch-c | 0.68 | 82 | 8.8 / 16.3 / 73.5 | 0.11 | 5.0 |
| K6 depth | stag | 2 | r2->switch-d | 0.67 | 82 | 4.3 / 8.7 / 73.7 | 0.05 | 5.0 |
| K6 depth | stag | 2 | rr->r0 | 0.68 | 82 | 9.0 / 10.1 / 41.8 | 0.11 | 5.0 |

Keyframe hand-over (sync r1 of each scenario): keyframe size, transmit time from the first packet after the write until its bytes have left (p50 / p90), pacing rate p50:

- base calm065: sub-a 1000 kb/s, 15.0 kB, 3.2 / 4.9 ms, 31.75 Mb/s; sub-b 2500 kb/s, 38.0 kB, 4.9 / 38.4 ms, 73.21 Mb/s; sub-c 2500 kb/s, 38.0 kB, 5.9 / 8.4 ms, 53.76 Mb/s; sub-ctrl 2500 kb/s, 38.0 kB, 4.7 / 7.7 ms, 61.05 Mb/s; sub-d 5000 kb/s, 76.2 kB, 9.6 / 41.8 ms, 70.97 Mb/s
- K1 hier: a1 1000 kb/s, 14.9 kB, 29.0 / 54.7 ms, 2.61 Mb/s; a2 2500 kb/s, 37.5 kB, 37.0 / 60.7 ms, 6.69 Mb/s; a3 5000 kb/s, 74.2 kB, 48.3 / 66.9 ms, 11.93 Mb/s; b1 1000 kb/s, 14.9 kB, 27.7 / 51.2 ms, 2.94 Mb/s; b2 2500 kb/s, 37.4 kB, 38.4 / 56.3 ms, 6.73 Mb/s; b3 5000 kb/s, 74.2 kB, 47.7 / 66.4 ms, 12.44 Mb/s; sub-ctrl 2500 kb/s, 37.4 kB, 2.4 / 3.7 ms, 109.11 Mb/s
- K6 depth: a1 2500 kb/s, 37.5 kB, 56.2 / 81.6 ms, 4.9 Mb/s; a2 5000 kb/s, 74.3 kB, 54.5 / 82.8 ms, 9.64 Mb/s; b1 2500 kb/s, 37.5 kB, 47.2 / 82.4 ms, 5.57 Mb/s; b2 5000 kb/s, 74.3 kB, 52.8 / 73.9 ms, 10.0 Mb/s; c1 2500 kb/s, 37.5 kB, 42.9 / 77.1 ms, 5.81 Mb/s; c2 5000 kb/s, 74.3 kB, 50.5 / 68.3 ms, 10.83 Mb/s; d1 2500 kb/s, 37.5 kB, 37.2 / 54.1 ms, 7.73 Mb/s; d2 5000 kb/s, 74.3 kB, 50.0 / 67.9 ms, 11.72 Mb/s; sub-ctrl 2500 kb/s, 37.5 kB, 3.5 / 4.8 ms, 91.34 Mb/s
