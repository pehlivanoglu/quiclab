# Synchronized keyframes, mini campaign: per-scenario comparison

sync = `.runs/2026-11-13_2238_grp-sync` (pfifo, phase 0 for all, r1 + r2); stag = `.runs/2026-11-10_1946_v2` (staggered phases, r1 only). ECG event intervals for Step 4 / 5. eps measured here (B1 O-- / OX-, all sync runs) = 0.0098.

## base calm065

| | stag r1 | sync r1 | sync r2 |
|---|---|---|---|
| keyframe spread ms, p50\|max: scheduled / written / packet | 750.3|752 / 750.3|768 / 750.3|768 | 0.6|1 / 0.6|161 / 0.6|161 | 0.7|2 / 0.7|321 / 0.7|321 |
| detector v2-owd vs GT1 | R 0.25 P 1.00 FA/min 0.00 lat 0 ms | R 0.00 P - FA/min 0.00 lat - ms | R 0.05 P 0.40 FA/min 0.56 lat 257 ms |
| GT1 episodes per min by egress | router->switch 2.61 | router->switch 6.78 | router->switch 5.22 |
| alarms per client-min; share within 200 ms after a keyframe (unrelated: 0.20) | 0.522 ; 0.00 | 0.104 ; 0.00 | 1.043 ; 0.60 |
| queue peaks >= 5 ms (step 2b C) | 1234 peaks, 644/min, peak p50/p90 9.7/20.5 ms, behind together 0.76 | 1019 peaks, 532/min, peak p50/p90 12.5/41.7 ms, behind together 1.00 | 1035 peaks, 540/min, peak p50/p90 12.3/38.9 ms, behind together 1.00 |

## base burstcap

| | stag r1 | sync r1 | sync r2 |
|---|---|---|---|
| keyframe spread ms, p50\|max: scheduled / written / packet | 750.1|751 / 750.2|1685 / 750.3|1693 | 0.6|2 / 0.7|939 / 0.8|955 | 0.5|1 / 0.5|944 / 0.6|954 |
| detector v2-owd vs GT1 | R 0.60 P 1.00 FA/min 0.00 lat 247 ms | R 0.26 P 1.00 FA/min 0.00 lat 380 ms | R 0.28 P 1.00 FA/min 0.00 lat 295 ms |
| ECG v1.2 (final) | P 1.00 R 1.00 cov 0.60 fp 0 tree ok mem-ev 2 | P 1.00 R 1.00 cov 0.60 fp 0 tree ok mem-ev 2 | P 1.00 R 1.00 cov 0.60 fp 0 tree ok mem-ev 2 |
| Step 4 h3 (ECG intervals) | last P/R/cov 1.00/1.00/0.60, closes P 1.00, false memb decl/close 0/0 of 4, one-leaf false splits 0/1 tested | last P/R/cov 1.00/1.00/0.60, closes P 1.00, false memb decl/close 0/0 of 4, one-leaf false splits 0/1 tested | last P/R/cov 1.00/1.00/0.60, closes P 1.00, false memb decl/close 0/0 of 4, one-leaf false splits 0/1 tested |
| GT1 episodes per min by egress | router->switch 6.62 | router->switch 15.16 | router->switch 13.99 |
| alarms per client-min; share within 200 ms after a keyframe (unrelated: 0.20) | 3.203 ; 0.23 | 3.117 ; 0.30 | 3.011 ; 0.28 |
| onset spread same burst p50 / p90 ms (ECG) | 66 / 165 | 132 / 231 | 99 / 264 |

- stag r1: B1 own O-- - (0), OX- - (0), --U - (0); eps - | B2 one-leaf own 0.48 (60 votes), members outside [0.3,0.7] 0.00 (n 4; fair 0.10), all-own events 2/16 vs 0.5^n 1.3 | B3 one-leaf (one/two/undecided): eps here 0.0098 1/0/0; eps 0.05 1/0/0; eps 0.1 1/0/0; eps 0.2 1/0/0
- sync r1: B1 own O-- - (0), OX- - (0), --U - (0); eps - | B2 one-leaf own 0.50 (82 votes), members outside [0.3,0.7] 1.00 (n 4; fair 0.10), all-own events 1/21 vs 0.5^n 1.5 | B3 one-leaf (one/two/undecided): eps here 0.0098 1/0/0; eps 0.05 1/0/0; eps 0.1 1/0/0; eps 0.2 1/0/0
- sync r2: B1 own O-- - (0), OX- - (0), --U - (0); eps - | B2 one-leaf own 0.27 (82 votes), members outside [0.3,0.7] 0.50 (n 4; fair 0.10), all-own events 1/21 vs 0.5^n 1.5 | B3 one-leaf (one/two/undecided): eps here 0.0098 1/0/0; eps 0.05 1/0/0; eps 0.1 1/0/0; eps 0.2 1/0/0

## K1 hier

| | stag r1 | sync r1 | sync r2 |
|---|---|---|---|
| keyframe spread ms, p50\|max: scheduled / written / packet | 750.0|751 / 750.1|1567 / 750.1|1585 | 0.7|2 / 0.9|993 / 1.1|1016 | 0.7|1 / 0.8|989 / 0.9|1019 |
| detector v2-owd vs GT1 | R 0.50 P 0.99 FA/min 0.06 lat 239 ms | R 0.20 P 1.00 FA/min 0.02 lat 336 ms | R 0.19 P 1.00 FA/min 0.00 lat 304 ms |
| ECG v1.2 (final) | P 1.00 R 1.00 cov 0.71 fp 0 tree ok mem-ev 5 | P 1.00 R 1.00 cov 0.71 fp 0 tree ok mem-ev 4 | P 1.00 R 1.00 cov 0.71 fp 0 tree ok mem-ev 2 |
| Step 4 h3 (ECG intervals) | last P/R/cov 1.00/1.00/0.71, closes P 0.94, false memb decl/close 11/23 of 33, one-leaf false splits 0/0 tested | last P/R/cov 1.00/1.00/0.71, closes P 0.93, false memb decl/close 12/21 of 34, one-leaf false splits 0/0 tested | last P/R/cov 1.00/1.00/0.71, closes P 0.93, false memb decl/close 10/16 of 20, one-leaf false splits 0/0 tested |
| GT1 episodes per min by egress | r1->r2 1.63, r2->switch-a 6.96, r2->switch-b 6.53 | r1->r2 13.12, r2->switch-a 6.96, r2->switch-b 8.17 | r1->r2 14.42, r2->switch-a 7.42, r2->switch-b 7.18 |
| alarms per client-min; share within 200 ms after a keyframe (unrelated: 0.20) | 3.137 ; 0.22 | 2.972 ; 0.23 | 2.86 ; 0.24 |
| onset spread same burst p50 / p90 ms (ECG) | 66 / 165 | 99 / 429 | 66 / 198 |

- stag r1: B1 own O-- 1.00 (48), OX- 1.00 (381), --U 0.68 (41); eps 0.0000
- sync r1: B1 own O-- 1.00 (30), OX- 1.00 (315), --U 0.50 (48); eps 0.0000
- sync r2: B1 own O-- 1.00 (33), OX- 1.00 (154), --U 0.62 (42); eps 0.0000

## C1 burstlongsplit

| | stag r1 | sync r1 | sync r2 |
|---|---|---|---|
| keyframe spread ms, p50\|max: scheduled / written / packet | 750.0|752 / 859.5|1623 / 866.0|1634 | 0.9|2 / 557.4|1000 / 576.1|1091 | 0.7|1 / 555.9|999 / 576.9|1159 |
| detector v2-owd vs GT1 | R 0.22 P 0.94 FA/min 0.11 lat 237 ms | R 0.09 P 0.99 FA/min 0.02 lat 344 ms | R 0.09 P 0.98 FA/min 0.04 lat 343 ms |
| ECG v1.2 (final) | P 1.00 R 1.00 cov 0.48 fp 0 tree no mem-ev 3 | P 1.00 R 1.00 cov 0.05 fp 0 tree no mem-ev 4 | P 1.00 R 1.00 cov 0.48 fp 0 tree no mem-ev 2 |
| Step 4 h3 (ECG intervals) | last P/R/cov 1.00/1.00/0.71, closes P 0.98, false memb decl/close 1/4 of 9, one-leaf false splits 0/0 tested | last P/R/cov 0.75/1.00/0.71, closes P 0.65, false memb decl/close 14/32 of 39, one-leaf false splits 0/0 tested | last P/R/cov 1.00/1.00/0.71, closes P 0.75, false memb decl/close 13/27 of 40, one-leaf false splits 0/0 tested |
| GT1 episodes per min by egress | r1->r2 1.51, r2->switch-a 3.45, r2->switch-b 3.93 | r1->r2 5.54, r2->switch-a 6.96, r2->switch-b 8.09 | r1->r2 4.88, r2->switch-a 7.37, r2->switch-b 6.85 |
| alarms per client-min; share within 200 ms after a keyframe (unrelated: 0.20) | 0.973 ; 0.27 | 0.879 ; 0.20 | 0.855 ; 0.15 |
| onset spread same burst p50 / p90 ms (ECG) | 66 / 495 | 99 / 561 | 99 / 297 |

- stag r1: B1 own O-- 1.00 (21), OX- 1.00 (81), --U 0.87 (54); eps 0.0000
- sync r1: B1 own O-- 1.00 (32), OX- 1.00 (53), --U 0.29 (78); eps 0.0000
- sync r2: B1 own O-- 1.00 (21), OX- 1.00 (65), --U 0.13 (53); eps 0.0000

## K6 depth

| | stag r1 | sync r1 | sync r2 |
|---|---|---|---|
| keyframe spread ms, p50\|max: scheduled / written / packet | 800.0|801 / 800.0|1555 / 800.0|1581 | 0.8|2 / 0.9|999 / 1.1|1011 | 1.1|2 / 1.3|998 / 1.4|1034 |
| detector v2-owd vs GT1 | R 0.29 P 0.99 FA/min 0.05 lat 272 ms | R 0.14 P 1.00 FA/min 0.02 lat 256 ms | R 0.12 P 1.00 FA/min 0.02 lat 274 ms |
| ECG v1.2 (final) | P 1.00 R 1.00 cov 0.78 fp 0 tree ok mem-ev 6 | P 1.00 R 1.00 cov 0.42 fp 0 tree no mem-ev 6 | P 1.00 R 1.00 cov 0.78 fp 0 tree ok mem-ev 4 |
| Step 4 h3 (ECG intervals) | last P/R/cov 1.00/1.00/0.78, closes P 0.97, false memb decl/close 7/17 of 19, one-leaf false splits 0/0 tested | last P/R/cov 0.67/1.00/0.78, closes P 0.44, false memb decl/close 72/104 of 121, one-leaf false splits 0/0 tested | last P/R/cov 0.36/1.00/0.78, closes P 0.35, false memb decl/close 71/103 of 121, one-leaf false splits 0/0 tested |
| GT1 episodes per min by egress | r0->r1 1.44, r0->r2 2.16, r1->switch-a 5.82, r1->switch-b 6.04, r2->switch-c 6.82, r2->switch-d 6.32, rr->r0 0.61 | r0->r1 3.05, r0->r2 5.43, r1->switch-a 4.44, r1->switch-b 4.1, r2->switch-c 4.94, r2->switch-d 10.04, rr->r0 11.2 | r0->r1 2.46, r0->r2 4.59, r1->switch-a 4.31, r1->switch-b 3.53, r2->switch-c 5.43, r2->switch-d 6.94, rr->r0 13.77 |
| alarms per client-min; share within 200 ms after a keyframe (unrelated: 0.20) | 1.898 ; 0.26 | 1.935 ; 0.24 | 1.859 ; 0.30 |
| onset spread same burst p50 / p90 ms (ECG) | 33 / 198 | 33 / 297 | 66 / 264 |

- stag r1: B1 own O-- 0.99 (334), OX- 1.00 (660), --U 0.82 (192); eps 0.0020
- sync r1: B1 own O-- 0.98 (290), OX- 0.99 (212), --U 0.65 (504); eps 0.0159
- sync r2: B1 own O-- 0.98 (260), OX- 0.98 (164), --U 0.57 (684); eps 0.0189

