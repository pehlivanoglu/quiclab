# Shadow v2, Step 3: single-feature CUSUM and G_ref

100 r1 runs; G_ref fitted on det-calm030-pfifo-r1, det-calm065-pfifo-r1 only. T 33 ms, delta 2, z_max 4, EWMA tau 60 s, floors {'F1': 0.4713, 'F2': 0.628, 'F3': 0.0066}, F3 W_g 30 ticks, s_freeze 0.25. git 7eb1419-dirty.

Fixed (global) scale for the fixed variants, pooled calm ticks of the calm pfifo-r1 runs: F1 mu 3.819 sigma 5.86, F2 mu -0.05271 sigma 7.296, F3 mu -0.008931 sigma 0.05885, L mu 0.001082 sigma 0.01657

## 1. G_ref from the calm pfifo-r1 runs (theta_on 0.5)

| feature | probe_rtt | max G on calm runs | G_ref | G_ref / max G | FA per min at G_ref = multiple x max G |
|---|---|---|---|---|---|
| fuse d: s1+s2+s3+sL | keep | 42.2 | 52.8 | 1.25 | x1: 1.23, x1.25: 0.00, x1.5: 0.31, x2: 0.00, x3: 0.00, x4: 0.00, x6: 0.00, x8: 0.00, x12: 0.00 |
| fuse d fixed | keep | 43.5 | 65.2 | 1.50 | x1: 1.85, x1.25: 2.16, x1.5: 0.00, x2: 0.00, x3: 0.00, x4: 0.00, x6: 0.00, x8: 0.00, x12: 0.00 |

Theory check (independent Gaussian ticks): mean run length to a false alarm ~ e^h ticks with h = theta_on G_ref in log-likelihood units: fuse d: s1+s2+s3+sL/keep h=26.4 -> e^h = 285775195054 ticks = 157176357.3 min, fuse d fixed/keep h=32.6 -> e^h = 145277018206557 ticks = 79902360013.6 min. Measured spacing is in table 2.

## 2. Operating curves, pfifo-r1 (freeze set) (truth GT3 with a GT1 / GT2 queue on the path)

| feature | probe_rtt | theta_on | episodes | precision | recall | FA / min CLEAR | latency p50 after t_on (ms) | latency p90 | measured ticks between FAs |
|---|---|---|---|---|---|---|---|---|---|
| fuse d: s1+s2+s3+sL | keep | 0.1 | 1383 | 0.70 | 0.89 | 4.83 | 162 | 422 | 377 |
| fuse d: s1+s2+s3+sL | keep | 0.15 | 1383 | 0.80 | 0.88 | 2.77 | 172 | 474 | 656 |
| fuse d: s1+s2+s3+sL | keep | 0.2 | 1383 | 0.89 | 0.87 | 1.36 | 188 | 504 | 1338 |
| fuse d: s1+s2+s3+sL | keep | 0.25 | 1383 | 0.92 | 0.86 | 0.91 | 195 | 564 | 2001 |
| fuse d: s1+s2+s3+sL | keep | 0.3 | 1383 | 0.94 | 0.86 | 0.70 | 207 | 596 | 2606 |
| fuse d: s1+s2+s3+sL | keep | 0.35 | 1383 | 0.95 | 0.86 | 0.55 | 220 | 621 | 3301 |
| fuse d: s1+s2+s3+sL | keep | 0.4 | 1383 | 0.97 | 0.85 | 0.32 | 236 | 653 | 5659 |
| fuse d: s1+s2+s3+sL | keep | 0.45 | 1383 | 0.98 | 0.85 | 0.25 | 251 | 679 | 7336 |
| fuse d: s1+s2+s3+sL | keep | 0.5 | 1383 | 0.99 | 0.85 | 0.13 | 260 | 698 | 14148 |
| fuse d: s1+s2+s3+sL | keep | 0.55 | 1383 | 0.99 | 0.84 | 0.14 | 270 | 720 | 13205 |
| fuse d: s1+s2+s3+sL | keep | 0.6 | 1383 | 0.99 | 0.84 | 0.13 | 288 | 752 | 14148 |
| fuse d: s1+s2+s3+sL | keep | 0.65 | 1383 | 0.99 | 0.83 | 0.11 | 296 | 774 | 16506 |
| fuse d: s1+s2+s3+sL | keep | 0.7 | 1383 | 0.99 | 0.83 | 0.06 | 315 | 786 | 28295 |
| fuse d: s1+s2+s3+sL | keep | 0.75 | 1383 | 0.99 | 0.82 | 0.07 | 326 | 801 | 24759 |
| fuse d: s1+s2+s3+sL | keep | 0.8 | 1383 | 0.99 | 0.82 | 0.06 | 339 | 820 | 28295 |
| fuse d: s1+s2+s3+sL | keep | 0.85 | 1383 | 0.99 | 0.82 | 0.06 | 352 | 838 | 33011 |
| fuse d: s1+s2+s3+sL | keep | 0.9 | 1383 | 1.00 | 0.82 | 0.03 | 366 | 852 | 66023 |
| fuse d: s1+s2+s3+sL | keep | 0.95 | 1383 | 1.00 | 0.81 | 0.03 | 378 | 863 | 66023 |
| fuse d: s1+s2+s3+sL | keep | 1.0 | 1383 | 1.00 | 0.81 | 0.04 | 392 | 905 | 49517 |
| fuse d fixed | keep | 0.1 | 1383 | 0.74 | 0.91 | 4.16 | 154 | 324 | 437 |
| fuse d fixed | keep | 0.15 | 1383 | 0.83 | 0.92 | 2.47 | 174 | 382 | 736 |
| fuse d fixed | keep | 0.2 | 1383 | 0.87 | 0.92 | 1.72 | 184 | 419 | 1059 |
| fuse d fixed | keep | 0.25 | 1383 | 0.92 | 0.92 | 0.98 | 198 | 465 | 1851 |
| fuse d fixed | keep | 0.3 | 1383 | 0.95 | 0.91 | 0.66 | 219 | 521 | 2751 |
| fuse d fixed | keep | 0.35 | 1383 | 0.96 | 0.91 | 0.47 | 233 | 562 | 3884 |
| fuse d fixed | keep | 0.4 | 1383 | 0.97 | 0.91 | 0.39 | 251 | 592 | 4716 |
| fuse d fixed | keep | 0.45 | 1383 | 0.98 | 0.90 | 0.26 | 265 | 620 | 7074 |
| fuse d fixed | keep | 0.5 | 1383 | 0.99 | 0.90 | 0.17 | 283 | 644 | 11004 |
| fuse d fixed | keep | 0.55 | 1383 | 0.99 | 0.89 | 0.13 | 299 | 698 | 14148 |
| fuse d fixed | keep | 0.6 | 1383 | 0.99 | 0.89 | 0.11 | 309 | 721 | 16506 |
| fuse d fixed | keep | 0.65 | 1383 | 1.00 | 0.88 | 0.06 | 330 | 731 | 33011 |
| fuse d fixed | keep | 0.7 | 1383 | 0.99 | 0.88 | 0.06 | 342 | 755 | 28295 |
| fuse d fixed | keep | 0.75 | 1383 | 1.00 | 0.87 | 0.02 | 364 | 785 | 99034 |
| fuse d fixed | keep | 0.8 | 1383 | 0.99 | 0.87 | 0.08 | 381 | 812 | 22008 |
| fuse d fixed | keep | 0.85 | 1383 | 0.99 | 0.87 | 0.12 | 394 | 819 | 15236 |
| fuse d fixed | keep | 0.9 | 1383 | 0.99 | 0.86 | 0.07 | 408 | 848 | 24759 |
| fuse d fixed | keep | 0.95 | 1383 | 0.99 | 0.86 | 0.06 | 422 | 854 | 28295 |
| fuse d fixed | keep | 1.0 | 1383 | 0.99 | 0.86 | 0.06 | 435 | 887 | 33011 |

v1 single-signal variants and baselines on the same runs and truth (grouping none):

| detector | v2 counterpart | episodes | precision | recall | FA / min | latency p50 | p90 |
|---|---|---|---|---|---|---|---|
| shadow | fuse | 1383 | 0.99 | 0.89 | 0.11 | 367 | 794 |
| gcc | - | 1383 | 0.99 | 0.83 | 0.16 | 927 | 1265 |
| bbr | - | 1383 | 0.76 | 0.67 | 2.71 | 829 | 2232 |

## 2. Operating curves, all r1 (held-out AQMs included) (truth GT3 with a GT1 / GT2 queue on the path)

| feature | probe_rtt | theta_on | episodes | precision | recall | FA / min CLEAR | latency p50 after t_on (ms) | latency p90 | measured ticks between FAs |
|---|---|---|---|---|---|---|---|---|---|
| fuse d: s1+s2+s3+sL | keep | 0.1 | 4855 | 0.60 | 0.90 | 6.61 | 158 | 406 | 275 |
| fuse d: s1+s2+s3+sL | keep | 0.15 | 4855 | 0.70 | 0.89 | 4.15 | 169 | 441 | 439 |
| fuse d: s1+s2+s3+sL | keep | 0.2 | 4855 | 0.80 | 0.89 | 2.38 | 184 | 474 | 762 |
| fuse d: s1+s2+s3+sL | keep | 0.25 | 4855 | 0.85 | 0.88 | 1.75 | 190 | 511 | 1037 |
| fuse d: s1+s2+s3+sL | keep | 0.3 | 4855 | 0.88 | 0.87 | 1.31 | 202 | 547 | 1386 |
| fuse d: s1+s2+s3+sL | keep | 0.35 | 4855 | 0.90 | 0.87 | 1.00 | 217 | 584 | 1824 |
| fuse d: s1+s2+s3+sL | keep | 0.4 | 4855 | 0.93 | 0.86 | 0.73 | 227 | 622 | 2507 |
| fuse d: s1+s2+s3+sL | keep | 0.45 | 4855 | 0.94 | 0.86 | 0.58 | 240 | 667 | 3114 |
| fuse d: s1+s2+s3+sL | keep | 0.5 | 4855 | 0.95 | 0.86 | 0.45 | 253 | 690 | 4028 |
| fuse d: s1+s2+s3+sL | keep | 0.55 | 4855 | 0.96 | 0.85 | 0.41 | 264 | 721 | 4473 |
| fuse d: s1+s2+s3+sL | keep | 0.6 | 4855 | 0.96 | 0.85 | 0.37 | 276 | 742 | 4907 |
| fuse d: s1+s2+s3+sL | keep | 0.65 | 4855 | 0.97 | 0.84 | 0.30 | 286 | 768 | 6088 |
| fuse d: s1+s2+s3+sL | keep | 0.7 | 4855 | 0.97 | 0.84 | 0.26 | 298 | 787 | 6920 |
| fuse d: s1+s2+s3+sL | keep | 0.75 | 4855 | 0.97 | 0.84 | 0.24 | 315 | 811 | 7711 |
| fuse d: s1+s2+s3+sL | keep | 0.8 | 4855 | 0.98 | 0.83 | 0.20 | 325 | 843 | 9098 |
| fuse d: s1+s2+s3+sL | keep | 0.85 | 4855 | 0.98 | 0.83 | 0.18 | 334 | 848 | 10249 |
| fuse d: s1+s2+s3+sL | keep | 0.9 | 4855 | 0.98 | 0.82 | 0.14 | 351 | 864 | 13274 |
| fuse d: s1+s2+s3+sL | keep | 0.95 | 4855 | 0.99 | 0.82 | 0.12 | 361 | 880 | 15571 |
| fuse d: s1+s2+s3+sL | keep | 1.0 | 4855 | 0.99 | 0.81 | 0.11 | 372 | 914 | 17227 |
| fuse d fixed | keep | 0.1 | 4855 | 0.67 | 0.93 | 4.91 | 154 | 338 | 371 |
| fuse d fixed | keep | 0.15 | 4855 | 0.77 | 0.94 | 3.11 | 171 | 382 | 585 |
| fuse d fixed | keep | 0.2 | 4855 | 0.82 | 0.93 | 2.25 | 183 | 418 | 809 |
| fuse d fixed | keep | 0.25 | 4855 | 0.87 | 0.93 | 1.52 | 195 | 457 | 1200 |
| fuse d fixed | keep | 0.3 | 4855 | 0.90 | 0.93 | 1.09 | 214 | 497 | 1663 |
| fuse d fixed | keep | 0.35 | 4855 | 0.93 | 0.92 | 0.79 | 229 | 548 | 2313 |
| fuse d fixed | keep | 0.4 | 4855 | 0.94 | 0.92 | 0.63 | 245 | 586 | 2902 |
| fuse d fixed | keep | 0.45 | 4855 | 0.95 | 0.92 | 0.48 | 258 | 618 | 3801 |
| fuse d fixed | keep | 0.5 | 4855 | 0.96 | 0.91 | 0.38 | 275 | 657 | 4820 |
| fuse d fixed | keep | 0.55 | 4855 | 0.97 | 0.91 | 0.29 | 290 | 687 | 6375 |
| fuse d fixed | keep | 0.6 | 4855 | 0.98 | 0.90 | 0.24 | 302 | 714 | 7639 |
| fuse d fixed | keep | 0.65 | 4855 | 0.98 | 0.90 | 0.16 | 321 | 731 | 11567 |
| fuse d fixed | keep | 0.7 | 4855 | 0.98 | 0.89 | 0.15 | 334 | 756 | 12268 |
| fuse d fixed | keep | 0.75 | 4855 | 0.99 | 0.89 | 0.14 | 347 | 783 | 13059 |
| fuse d fixed | keep | 0.8 | 4855 | 0.99 | 0.88 | 0.14 | 364 | 809 | 12651 |
| fuse d fixed | keep | 0.85 | 4855 | 0.98 | 0.88 | 0.15 | 377 | 830 | 12268 |
| fuse d fixed | keep | 0.9 | 4855 | 0.99 | 0.87 | 0.11 | 391 | 848 | 15876 |
| fuse d fixed | keep | 0.95 | 4855 | 0.99 | 0.87 | 0.08 | 404 | 868 | 21883 |
| fuse d fixed | keep | 1.0 | 4855 | 0.99 | 0.87 | 0.09 | 419 | 891 | 20761 |

v1 single-signal variants and baselines on the same runs and truth (grouping none):

| detector | v2 counterpart | episodes | precision | recall | FA / min | latency p50 | p90 |
|---|---|---|---|---|---|---|---|
| shadow | fuse | 4855 | 0.98 | 0.86 | 0.22 | 366 | 850 |
| gcc | - | 4855 | 0.98 | 0.76 | 0.15 | 910 | 1324 |
| bbr | - | 4855 | 0.73 | 0.71 | 2.91 | 792 | 2043 |

## 3. Pass check on the freeze set: v2 feature at the v1 counterpart's false-alarm rate

| feature | probe_rtt | v1 counterpart | v1: FA/min / recall / lat p50 / p90 | theta | v2: FA/min / recall / lat p50 / p90 | recall diff | p90 diff (ms) | verdict (recall >= v1 - 0.02 and p90 <= v1) |
|---|---|---|---|---|---|---|---|---|
| fuse d: s1+s2+s3+sL | keep | shadow | 0.11 / 0.89 / 367 / 794 | 0.65 | 0.11 / 0.83 / 296 / 774 | -0.06 | -21 | FAIL |
| fuse d fixed | keep | shadow | 0.11 / 0.89 / 367 / 794 | 0.6 | 0.11 / 0.89 / 309 / 721 | -0.00 | -73 | PASS |

## 3b. Cell: ppbp (all AQMs) (4 runs, all reps in the campaigns given)

| detector | theta_on | episodes | precision | recall | FA / min | latency p50 | p90 |
|---|---|---|---|---|---|---|---|
| fuse d: s1+s2+s3+sL | 0.3 | 216 | 0.88 | 0.13 | 0.86 | 2196 | 7173 |
| fuse d: s1+s2+s3+sL | 0.5 | 216 | 0.95 | 0.09 | 0.22 | 2753 | 7207 |
| fuse d: s1+s2+s3+sL | 0.8 | 216 | 1.00 | 0.06 | 0.00 | 2701 | 7423 |
| fuse d: s1+s2+s3+sL | 1.0 | 216 | 1.00 | 0.06 | 0.00 | 2767 | 8089 |
| fuse d fixed | 0.3 | 216 | 0.94 | 0.86 | 2.37 | 303 | 823 |
| fuse d fixed | 0.5 | 216 | 0.99 | 0.85 | 0.43 | 386 | 1069 |
| fuse d fixed | 0.8 | 216 | 0.99 | 0.84 | 0.22 | 476 | 1079 |
| fuse d fixed | 1.0 | 216 | 0.99 | 0.83 | 0.22 | 515 | 1156 |
| v1 shadow | - | 216 | 0.99 | 0.85 | 0.22 | 440 | 974 |
| v1 gcc | - | 216 | 0.99 | 0.88 | 0.22 | 840 | 1034 |
| v1 bbr | - | 216 | 0.89 | 0.64 | 3.66 | 1213 | 3594 |

## 3b. Cell: calm090 (all AQMs) (4 runs, all reps in the campaigns given)

| detector | theta_on | episodes | precision | recall | FA / min | latency p50 | p90 |
|---|---|---|---|---|---|---|---|
| fuse d: s1+s2+s3+sL | 0.3 | 166 | 0.93 | 0.39 | 0.82 | 441 | 789 |
| fuse d: s1+s2+s3+sL | 0.5 | 166 | 0.98 | 0.28 | 0.16 | 537 | 1008 |
| fuse d: s1+s2+s3+sL | 0.8 | 166 | 0.97 | 0.23 | 0.16 | 642 | 1185 |
| fuse d: s1+s2+s3+sL | 1.0 | 166 | 1.00 | 0.17 | 0.00 | 730 | 1133 |
| fuse d fixed | 0.3 | 166 | 0.83 | 0.90 | 5.06 | 335 | 511 |
| fuse d fixed | 0.5 | 166 | 0.93 | 0.76 | 1.47 | 394 | 644 |
| fuse d fixed | 0.8 | 166 | 0.96 | 0.60 | 0.65 | 477 | 795 |
| fuse d fixed | 1.0 | 166 | 0.98 | 0.53 | 0.33 | 541 | 940 |
| v1 shadow | - | 166 | 0.93 | 0.60 | 1.14 | 480 | 728 |
| v1 gcc | - | 166 | 0.95 | 0.55 | 0.82 | 828 | 1061 |
| v1 bbr | - | 166 | 0.85 | 0.37 | 1.80 | 642 | 1689 |

## 3b. Cell: calmcbr090 (all AQMs) (4 runs, all reps in the campaigns given)

| detector | theta_on | episodes | precision | recall | FA / min | latency p50 | p90 |
|---|---|---|---|---|---|---|---|
| fuse d: s1+s2+s3+sL | 0.3 | 118 | 0.81 | 0.51 | 1.66 | 430 | 625 |
| fuse d: s1+s2+s3+sL | 0.5 | 118 | 0.90 | 0.38 | 0.59 | 463 | 623 |
| fuse d: s1+s2+s3+sL | 0.8 | 118 | 0.97 | 0.26 | 0.12 | 507 | 718 |
| fuse d: s1+s2+s3+sL | 1.0 | 118 | 1.00 | 0.19 | 0.00 | 573 | 832 |
| fuse d fixed | 0.3 | 118 | 0.77 | 0.86 | 3.56 | 325 | 481 |
| fuse d fixed | 0.5 | 118 | 0.86 | 0.74 | 1.66 | 397 | 625 |
| fuse d fixed | 0.8 | 118 | 0.93 | 0.54 | 0.59 | 463 | 609 |
| fuse d fixed | 1.0 | 118 | 0.96 | 0.42 | 0.24 | 518 | 617 |
| v1 shadow | - | 118 | 0.84 | 0.42 | 1.07 | 465 | 641 |
| v1 gcc | - | 118 | 0.92 | 0.47 | 0.59 | 799 | 983 |
| v1 bbr | - | 118 | 0.66 | 0.33 | 2.37 | 466 | 1018 |

## 3b. Cell: tcpcubic red (1 runs, all reps in the campaigns given)

| detector | theta_on | episodes | precision | recall | FA / min | latency p50 | p90 |
|---|---|---|---|---|---|---|---|
| fuse d: s1+s2+s3+sL | 0.3 | 71 | 0.96 | 0.99 | 0.64 | 286 | 1053 |
| fuse d: s1+s2+s3+sL | 0.5 | 71 | 1.00 | 0.99 | 0.00 | 387 | 1355 |
| fuse d: s1+s2+s3+sL | 0.8 | 71 | 0.98 | 0.87 | 0.21 | 595 | 2064 |
| fuse d: s1+s2+s3+sL | 1.0 | 71 | 1.00 | 0.75 | 0.00 | 593 | 2093 |
| fuse d fixed | 0.3 | 71 | 0.97 | 0.96 | 0.43 | 287 | 878 |
| fuse d fixed | 0.5 | 71 | 1.00 | 0.96 | 0.00 | 400 | 1167 |
| fuse d fixed | 0.8 | 71 | 1.00 | 0.89 | 0.00 | 740 | 2167 |
| fuse d fixed | 1.0 | 71 | 1.00 | 0.76 | 0.00 | 801 | 2488 |
| v1 shadow | - | 71 | 1.00 | 0.55 | 0.00 | 629 | 2616 |
| v1 gcc | - | 71 | 1.00 | 0.45 | 0.00 | 845 | 1396 |
| v1 bbr | - | 71 | 0.95 | 0.80 | 0.64 | 925 | 1932 |

## 3b. Cell: fq_codel competition (5 runs, all reps in the campaigns given)

| detector | theta_on | episodes | precision | recall | FA / min | latency p50 | p90 |
|---|---|---|---|---|---|---|---|
| fuse d: s1+s2+s3+sL | 0.3 | 136 | 0.55 | 0.90 | 3.71 | 188 | 1001 |
| fuse d: s1+s2+s3+sL | 0.5 | 136 | 0.72 | 0.89 | 1.80 | 211 | 1029 |
| fuse d: s1+s2+s3+sL | 0.8 | 136 | 0.89 | 0.82 | 0.52 | 255 | 1153 |
| fuse d: s1+s2+s3+sL | 1.0 | 136 | 0.91 | 0.77 | 0.41 | 302 | 1192 |
| fuse d fixed | 0.3 | 136 | 0.69 | 0.88 | 1.98 | 180 | 904 |
| fuse d fixed | 0.5 | 136 | 0.83 | 0.85 | 0.90 | 228 | 1133 |
| fuse d fixed | 0.8 | 136 | 0.92 | 0.76 | 0.34 | 276 | 1180 |
| fuse d fixed | 1.0 | 136 | 0.95 | 0.74 | 0.19 | 345 | 1206 |
| v1 shadow | - | 136 | 0.89 | 0.57 | 0.37 | 304 | 1163 |
| v1 gcc | - | 136 | 0.98 | 0.38 | 0.04 | 798 | 1706 |
| v1 bbr | - | 136 | 0.76 | 0.79 | 1.27 | 516 | 1448 |

## 3b. Cell: burstcapshallow pfifo (1 runs, all reps in the campaigns given)

| detector | theta_on | episodes | precision | recall | FA / min | latency p50 | p90 |
|---|---|---|---|---|---|---|---|
| fuse d: s1+s2+s3+sL | 0.3 | 71 | 0.96 | 1.00 | 0.55 | 163 | 528 |
| fuse d: s1+s2+s3+sL | 0.5 | 71 | 0.99 | 1.00 | 0.18 | 203 | 528 |
| fuse d: s1+s2+s3+sL | 0.8 | 71 | 1.00 | 0.99 | 0.00 | 323 | 676 |
| fuse d: s1+s2+s3+sL | 1.0 | 71 | 1.00 | 0.99 | 0.00 | 403 | 775 |
| fuse d fixed | 0.3 | 71 | 0.99 | 1.00 | 0.18 | 198 | 582 |
| fuse d fixed | 0.5 | 71 | 1.00 | 0.99 | 0.00 | 315 | 684 |
| fuse d fixed | 0.8 | 71 | 1.00 | 0.97 | 0.00 | 485 | 843 |
| fuse d fixed | 1.0 | 71 | 1.00 | 0.93 | 0.00 | 536 | 965 |
| v1 shadow | - | 71 | 1.00 | 0.86 | 0.00 | 606 | 1122 |
| v1 gcc | - | 71 | 1.00 | 0.54 | 0.00 | 961 | 1570 |
| v1 bbr | - | 71 | 0.79 | 0.79 | 2.74 | 425 | 1577 |

## 3b. Cell: burstlong (all AQMs) (4 runs, all reps in the campaigns given)

| detector | theta_on | episodes | precision | recall | FA / min | latency p50 | p90 |
|---|---|---|---|---|---|---|---|
| fuse d: s1+s2+s3+sL | 0.3 | 260 | 0.90 | 0.80 | 1.54 | 230 | 2006 |
| fuse d: s1+s2+s3+sL | 0.5 | 260 | 0.94 | 0.83 | 0.96 | 286 | 1630 |
| fuse d: s1+s2+s3+sL | 0.8 | 260 | 0.97 | 0.85 | 0.45 | 338 | 1612 |
| fuse d: s1+s2+s3+sL | 1.0 | 260 | 0.99 | 0.85 | 0.19 | 404 | 1627 |
| fuse d fixed | 0.3 | 260 | 0.93 | 0.81 | 1.09 | 210 | 2522 |
| fuse d fixed | 0.5 | 260 | 0.98 | 0.83 | 0.26 | 262 | 2142 |
| fuse d fixed | 0.8 | 260 | 0.99 | 0.84 | 0.19 | 321 | 1472 |
| fuse d fixed | 1.0 | 260 | 0.99 | 0.86 | 0.19 | 360 | 1607 |
| v1 shadow | - | 260 | 0.98 | 0.95 | 0.26 | 337 | 922 |
| v1 gcc | - | 260 | 0.99 | 0.84 | 0.19 | 946 | 1509 |
| v1 bbr | - | 260 | 0.85 | 0.76 | 2.25 | 1229 | 3389 |

## 4. Keyframe peak score in calm periods (pfifo-r1) and mean score on calm runs (all r1)

| feature | probe_rtt | keyframes | peak score p50 | p99 | mean score calm065 | mean score calm090 | max flow mean calm090 |
|---|---|---|---|---|---|---|---|
| fuse d: s1+s2+s3+sL | keep | 603 | 0.00 | 0.23 | 0.01 | 0.02 | 0.06 |
| fuse d fixed | keep | 603 | 0.00 | 0.22 | 0.01 | 0.14 | 0.40 |

Decision 5: a keyframe p99 above 0.5 makes the min-filter on F3 / F4 mandatory. Decision 2: calm090 shows the price of a level feature (F1).

Plot: step3/curves.png.
