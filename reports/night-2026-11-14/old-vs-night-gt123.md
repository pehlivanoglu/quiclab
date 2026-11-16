# Detectors vs GT1 / GT2 / GT3: old campaign (ip4-not-sync-keyframes-oldGT) vs night 2026-11-14

Both scored now with the same code and defaults (gt_tables.worker: gt1/gt2/gt3.Params(), gt_score rules). Ranked by F1 within each table. Sets: A old: all runs (222 runs); B old: cells also in night (13 runs); C night-sync: same cells (22 runs); D night-sync: all runs (32 runs); E night-stag: all runs (3 runs).

## GT1

### A old: all runs: 222 runs, 56590 episodes

| rank | detector | F1 | precision | recall | recall >= 2 s | latency p50 ms | FA / min CLEAR |
|---|---|---|---|---|---|---|---|
| 1 | loss_only | 0.59 | 0.92 | 0.44 | 0.85 | 453 | 0.34 |
| 2 | shadow | 0.58 | 0.96 | 0.41 | 0.85 | 357 | 0.15 |
| 3 | gcc | 0.55 | 0.91 | 0.39 | 0.83 | 916 | 0.39 |
| 4 | backlog_only | 0.53 | 0.93 | 0.37 | 0.81 | 643 | 0.26 |
| 5 | shadow_m4 | 0.53 | 0.97 | 0.36 | 0.81 | 829 | 0.11 |
| 6 | bbr | 0.51 | 0.83 | 0.37 | 0.75 | 788 | 0.71 |
| 7 | shadow_verified | 0.49 | 0.98 | 0.33 | 0.75 | 619 | 0.06 |
| 8 | gradient_only | 0.47 | 0.94 | 0.31 | 0.71 | 947 | 0.20 |
| 9 | offered_only | 0.45 | 0.99 | 0.29 | 0.66 | 782 | 0.04 |
| 10 | deficit_only | 0.43 | 0.92 | 0.28 | 0.70 | 1090 | 0.22 |

### B old: cells also in night: 13 runs, 8344 episodes

| rank | detector | F1 | precision | recall | recall >= 2 s | latency p50 ms | FA / min CLEAR |
|---|---|---|---|---|---|---|---|
| 1 | shadow | 0.60 | 0.90 | 0.45 | 0.92 | 362 | 0.59 |
| 2 | gcc | 0.58 | 0.81 | 0.45 | 0.91 | 904 | 1.28 |
| 3 | loss_only | 0.57 | 0.93 | 0.41 | 0.83 | 478 | 0.38 |
| 4 | shadow_m4 | 0.57 | 0.96 | 0.40 | 0.91 | 824 | 0.23 |
| 5 | bbr | 0.54 | 0.85 | 0.39 | 0.80 | 839 | 0.85 |
| 6 | shadow_verified | 0.54 | 0.99 | 0.37 | 0.84 | 616 | 0.04 |
| 7 | backlog_only | 0.53 | 0.80 | 0.40 | 0.88 | 616 | 1.23 |
| 8 | offered_only | 0.51 | 0.99 | 0.34 | 0.74 | 759 | 0.03 |
| 9 | gradient_only | 0.48 | 0.83 | 0.34 | 0.75 | 934 | 0.85 |
| 10 | deficit_only | 0.48 | 0.95 | 0.32 | 0.78 | 1116 | 0.19 |

### C night-sync: same cells: 22 runs, 30510 episodes

| rank | detector | F1 | precision | recall | recall >= 2 s | latency p50 ms | FA / min CLEAR |
|---|---|---|---|---|---|---|---|
| 1 | bbr | 0.41 | 0.92 | 0.26 | 0.72 | 148 | 0.98 |
| 2 | gcc | 0.35 | 0.95 | 0.21 | 0.91 | 860 | 0.46 |
| 3 | shadow | 0.35 | 0.97 | 0.21 | 0.91 | 345 | 0.24 |
| 4 | shadow_m4 | 0.31 | 0.99 | 0.19 | 0.89 | 794 | 0.12 |
| 5 | loss_only | 0.31 | 0.89 | 0.19 | 0.81 | 430 | 0.95 |
| 6 | backlog_only | 0.31 | 0.95 | 0.19 | 0.85 | 592 | 0.42 |
| 7 | shadow_verified | 0.28 | 0.99 | 0.16 | 0.81 | 586 | 0.06 |
| 8 | deficit_only | 0.26 | 0.95 | 0.15 | 0.75 | 952 | 0.34 |
| 9 | offered_only | 0.26 | 0.99 | 0.15 | 0.70 | 744 | 0.06 |
| 10 | gradient_only | 0.26 | 0.96 | 0.15 | 0.73 | 910 | 0.28 |

### D night-sync: all runs: 32 runs, 54106 episodes

| rank | detector | F1 | precision | recall | recall >= 2 s | latency p50 ms | FA / min CLEAR |
|---|---|---|---|---|---|---|---|
| 1 | bbr | 0.42 | 0.91 | 0.27 | 0.74 | 130 | 1.04 |
| 2 | gcc | 0.31 | 0.96 | 0.18 | 0.94 | 857 | 0.30 |
| 3 | shadow | 0.30 | 0.98 | 0.18 | 0.93 | 329 | 0.18 |
| 4 | loss_only | 0.30 | 0.92 | 0.18 | 0.86 | 437 | 0.62 |
| 5 | shadow_m4 | 0.28 | 0.98 | 0.16 | 0.91 | 799 | 0.12 |
| 6 | backlog_only | 0.28 | 0.96 | 0.16 | 0.89 | 603 | 0.25 |
| 7 | shadow_verified | 0.25 | 0.99 | 0.14 | 0.84 | 587 | 0.08 |
| 8 | deficit_only | 0.24 | 0.94 | 0.14 | 0.78 | 931 | 0.35 |
| 9 | gradient_only | 0.23 | 0.97 | 0.13 | 0.76 | 900 | 0.18 |
| 10 | offered_only | 0.22 | 0.99 | 0.12 | 0.71 | 774 | 0.05 |

### E night-stag: all runs: 3 runs, 2317 episodes

| rank | detector | F1 | precision | recall | recall >= 2 s | latency p50 ms | FA / min CLEAR |
|---|---|---|---|---|---|---|---|
| 1 | gcc | 0.60 | 0.96 | 0.43 | 1.00 | 932 | 0.17 |
| 2 | loss_only | 0.59 | 1.00 | 0.42 | 0.96 | 548 | 0.01 |
| 3 | shadow | 0.58 | 1.00 | 0.41 | 0.99 | 366 | 0.01 |
| 4 | bbr | 0.56 | 0.87 | 0.42 | 0.84 | 882 | 0.64 |
| 5 | backlog_only | 0.56 | 0.99 | 0.39 | 0.98 | 674 | 0.04 |
| 6 | shadow_m4 | 0.55 | 0.99 | 0.38 | 0.98 | 885 | 0.03 |
| 7 | gradient_only | 0.54 | 0.98 | 0.37 | 0.94 | 1023 | 0.07 |
| 8 | shadow_verified | 0.52 | 1.00 | 0.36 | 0.95 | 706 | 0.02 |
| 9 | deficit_only | 0.46 | 0.99 | 0.30 | 0.81 | 1170 | 0.02 |
| 10 | offered_only | 0.40 | 1.00 | 0.25 | 0.65 | 794 | 0.00 |

## GT2

### A old: all runs: 222 runs, 61590 episodes

| rank | detector | F1 | precision | recall | recall >= 2 s | latency p50 ms | FA / min CLEAR |
|---|---|---|---|---|---|---|---|
| 1 | loss_only | 0.52 | 0.92 | 0.36 | 0.87 | 464 | 0.29 |
| 2 | shadow | 0.50 | 0.96 | 0.34 | 0.84 | 351 | 0.13 |
| 3 | gcc | 0.48 | 0.91 | 0.32 | 0.83 | 924 | 0.31 |
| 4 | backlog_only | 0.47 | 0.93 | 0.32 | 0.82 | 639 | 0.24 |
| 5 | bbr | 0.46 | 0.83 | 0.32 | 0.76 | 808 | 0.62 |
| 6 | shadow_m4 | 0.46 | 0.97 | 0.30 | 0.80 | 843 | 0.08 |
| 7 | shadow_verified | 0.43 | 0.98 | 0.28 | 0.75 | 648 | 0.05 |
| 8 | gradient_only | 0.42 | 0.94 | 0.27 | 0.72 | 949 | 0.16 |
| 9 | offered_only | 0.38 | 0.99 | 0.24 | 0.66 | 806 | 0.03 |
| 10 | deficit_only | 0.37 | 0.94 | 0.23 | 0.72 | 1155 | 0.13 |

### B old: cells also in night: 13 runs, 8537 episodes

| rank | detector | F1 | precision | recall | recall >= 2 s | latency p50 ms | FA / min CLEAR |
|---|---|---|---|---|---|---|---|
| 1 | loss_only | 0.53 | 0.93 | 0.37 | 0.97 | 491 | 0.29 |
| 2 | gcc | 0.51 | 0.79 | 0.38 | 0.99 | 900 | 1.08 |
| 3 | shadow | 0.51 | 0.87 | 0.36 | 0.97 | 357 | 0.57 |
| 4 | shadow_m4 | 0.49 | 0.95 | 0.33 | 0.97 | 853 | 0.18 |
| 5 | bbr | 0.48 | 0.83 | 0.34 | 0.84 | 848 | 0.77 |
| 6 | backlog_only | 0.48 | 0.77 | 0.35 | 0.97 | 607 | 1.18 |
| 7 | shadow_verified | 0.47 | 0.99 | 0.31 | 0.93 | 639 | 0.02 |
| 8 | gradient_only | 0.47 | 0.83 | 0.32 | 0.90 | 927 | 0.75 |
| 9 | deficit_only | 0.41 | 0.97 | 0.26 | 0.86 | 1192 | 0.09 |
| 10 | offered_only | 0.41 | 0.99 | 0.25 | 0.78 | 795 | 0.02 |

### C night-sync: same cells: 22 runs, 32673 episodes

| rank | detector | F1 | precision | recall | recall >= 2 s | latency p50 ms | FA / min CLEAR |
|---|---|---|---|---|---|---|---|
| 1 | bbr | 0.34 | 0.90 | 0.21 | 0.79 | 113 | 0.65 |
| 2 | gcc | 0.27 | 0.90 | 0.16 | 0.99 | 863 | 0.50 |
| 3 | loss_only | 0.27 | 0.85 | 0.16 | 0.96 | 440 | 0.78 |
| 4 | shadow | 0.25 | 0.94 | 0.14 | 0.96 | 338 | 0.23 |
| 5 | backlog_only | 0.25 | 0.88 | 0.14 | 0.95 | 586 | 0.52 |
| 6 | gradient_only | 0.23 | 0.92 | 0.13 | 0.88 | 903 | 0.30 |
| 7 | shadow_m4 | 0.23 | 0.98 | 0.13 | 0.95 | 840 | 0.07 |
| 8 | shadow_verified | 0.21 | 0.99 | 0.12 | 0.90 | 642 | 0.03 |
| 9 | deficit_only | 0.19 | 0.96 | 0.10 | 0.84 | 1152 | 0.13 |
| 10 | offered_only | 0.17 | 0.99 | 0.09 | 0.72 | 825 | 0.02 |

### D night-sync: all runs: 32 runs, 72446 episodes

| rank | detector | F1 | precision | recall | recall >= 2 s | latency p50 ms | FA / min CLEAR |
|---|---|---|---|---|---|---|---|
| 1 | bbr | 0.35 | 0.92 | 0.21 | 0.78 | 63 | 0.60 |
| 2 | loss_only | 0.21 | 0.90 | 0.12 | 0.96 | 443 | 0.46 |
| 3 | gcc | 0.20 | 0.93 | 0.11 | 0.99 | 863 | 0.29 |
| 4 | shadow | 0.19 | 0.96 | 0.11 | 0.96 | 324 | 0.15 |
| 5 | backlog_only | 0.18 | 0.92 | 0.10 | 0.96 | 595 | 0.29 |
| 6 | shadow_m4 | 0.17 | 0.98 | 0.10 | 0.95 | 829 | 0.06 |
| 7 | gradient_only | 0.17 | 0.95 | 0.09 | 0.87 | 897 | 0.17 |
| 8 | shadow_verified | 0.16 | 0.99 | 0.09 | 0.90 | 632 | 0.03 |
| 9 | deficit_only | 0.15 | 0.95 | 0.08 | 0.85 | 1069 | 0.14 |
| 10 | offered_only | 0.12 | 0.99 | 0.07 | 0.71 | 841 | 0.02 |

### E night-stag: all runs: 3 runs, 3920 episodes

| rank | detector | F1 | precision | recall | recall >= 2 s | latency p50 ms | FA / min CLEAR |
|---|---|---|---|---|---|---|---|
| 1 | gcc | 0.40 | 0.97 | 0.25 | 1.00 | 933 | 0.12 |
| 2 | bbr | 0.40 | 0.86 | 0.26 | 0.83 | 824 | 0.61 |
| 3 | loss_only | 0.40 | 1.00 | 0.25 | 0.95 | 554 | 0.00 |
| 4 | shadow | 0.40 | 1.00 | 0.25 | 0.98 | 354 | 0.00 |
| 5 | backlog_only | 0.38 | 0.99 | 0.23 | 0.97 | 658 | 0.03 |
| 6 | shadow_m4 | 0.37 | 1.00 | 0.23 | 0.96 | 868 | 0.01 |
| 7 | gradient_only | 0.37 | 0.99 | 0.23 | 0.93 | 991 | 0.03 |
| 8 | shadow_verified | 0.35 | 1.00 | 0.21 | 0.95 | 696 | 0.00 |
| 9 | deficit_only | 0.30 | 0.99 | 0.18 | 0.83 | 1173 | 0.03 |
| 10 | offered_only | 0.26 | 1.00 | 0.15 | 0.64 | 791 | 0.00 |

## GT3

### A old: all runs: 222 runs, 25235 episodes

| rank | detector | F1 | precision | recall | recall >= 2 s | latency p50 ms | FA / min CLEAR |
|---|---|---|---|---|---|---|---|
| 1 | gcc | 0.88 | 0.99 | 0.79 | 0.93 | 921 | 0.13 |
| 2 | shadow | 0.87 | 0.99 | 0.77 | 0.91 | 348 | 0.10 |
| 3 | backlog_only | 0.85 | 0.99 | 0.74 | 0.89 | 643 | 0.13 |
| 4 | loss_only | 0.84 | 0.91 | 0.78 | 0.91 | 462 | 0.95 |
| 5 | shadow_m4 | 0.81 | 0.99 | 0.69 | 0.88 | 865 | 0.05 |
| 6 | gradient_only | 0.79 | 1.00 | 0.66 | 0.83 | 958 | 0.04 |
| 7 | shadow_verified | 0.77 | 1.00 | 0.63 | 0.82 | 685 | 0.04 |
| 8 | bbr | 0.75 | 0.88 | 0.66 | 0.81 | 826 | 1.16 |
| 9 | offered_only | 0.70 | 1.00 | 0.54 | 0.72 | 841 | 0.00 |
| 10 | deficit_only | 0.68 | 0.98 | 0.52 | 0.73 | 1155 | 0.16 |

### B old: cells also in night: 13 runs, 4520 episodes

| rank | detector | F1 | precision | recall | recall >= 2 s | latency p50 ms | FA / min CLEAR |
|---|---|---|---|---|---|---|---|
| 1 | gcc | 0.83 | 0.99 | 0.72 | 0.89 | 903 | 0.16 |
| 2 | backlog_only | 0.79 | 1.00 | 0.66 | 0.84 | 645 | 0.06 |
| 3 | shadow | 0.78 | 1.00 | 0.64 | 0.83 | 384 | 0.04 |
| 4 | gradient_only | 0.76 | 1.00 | 0.61 | 0.81 | 960 | 0.04 |
| 5 | loss_only | 0.72 | 0.95 | 0.58 | 0.76 | 580 | 0.61 |
| 6 | shadow_m4 | 0.71 | 1.00 | 0.56 | 0.77 | 926 | 0.04 |
| 7 | bbr | 0.68 | 0.89 | 0.54 | 0.74 | 904 | 1.30 |
| 8 | shadow_verified | 0.67 | 1.00 | 0.50 | 0.72 | 797 | 0.01 |
| 9 | deficit_only | 0.59 | 0.99 | 0.42 | 0.64 | 1356 | 0.08 |
| 10 | offered_only | 0.58 | 1.00 | 0.41 | 0.60 | 915 | 0.00 |

### C night-sync: same cells: 22 runs, 5984 episodes

| rank | detector | F1 | precision | recall | recall >= 2 s | latency p50 ms | FA / min CLEAR |
|---|---|---|---|---|---|---|---|
| 1 | gcc | 0.86 | 0.99 | 0.75 | 0.92 | 898 | 0.14 |
| 2 | backlog_only | 0.83 | 1.00 | 0.71 | 0.90 | 624 | 0.05 |
| 3 | shadow | 0.81 | 0.99 | 0.68 | 0.87 | 368 | 0.06 |
| 4 | gradient_only | 0.79 | 1.00 | 0.65 | 0.83 | 965 | 0.03 |
| 5 | shadow_m4 | 0.76 | 1.00 | 0.61 | 0.82 | 910 | 0.05 |
| 6 | loss_only | 0.73 | 0.82 | 0.65 | 0.82 | 538 | 2.27 |
| 7 | shadow_verified | 0.72 | 1.00 | 0.56 | 0.77 | 767 | 0.03 |
| 8 | deficit_only | 0.66 | 0.98 | 0.50 | 0.71 | 1243 | 0.16 |
| 9 | bbr | 0.65 | 0.77 | 0.57 | 0.74 | 851 | 2.74 |
| 10 | offered_only | 0.60 | 1.00 | 0.43 | 0.61 | 926 | 0.00 |

### D night-sync: all runs: 32 runs, 8817 episodes

| rank | detector | F1 | precision | recall | recall >= 2 s | latency p50 ms | FA / min CLEAR |
|---|---|---|---|---|---|---|---|
| 1 | gcc | 0.88 | 0.98 | 0.80 | 0.94 | 888 | 0.14 |
| 2 | backlog_only | 0.86 | 1.00 | 0.75 | 0.93 | 621 | 0.04 |
| 3 | shadow | 0.85 | 0.99 | 0.74 | 0.91 | 340 | 0.07 |
| 4 | gradient_only | 0.82 | 1.00 | 0.69 | 0.86 | 933 | 0.02 |
| 5 | shadow_m4 | 0.80 | 0.99 | 0.68 | 0.87 | 874 | 0.06 |
| 6 | loss_only | 0.79 | 0.86 | 0.72 | 0.88 | 533 | 1.26 |
| 7 | shadow_verified | 0.76 | 0.99 | 0.62 | 0.82 | 719 | 0.04 |
| 8 | deficit_only | 0.72 | 0.96 | 0.57 | 0.78 | 1138 | 0.25 |
| 9 | offered_only | 0.64 | 1.00 | 0.47 | 0.65 | 910 | 0.00 |
| 10 | bbr | 0.60 | 0.62 | 0.58 | 0.74 | 822 | 3.92 |

### E night-stag: all runs: 3 runs, 970 episodes

| rank | detector | F1 | precision | recall | recall >= 2 s | latency p50 ms | FA / min CLEAR |
|---|---|---|---|---|---|---|---|
| 1 | gcc | 0.94 | 0.97 | 0.91 | 1.00 | 911 | 0.21 |
| 2 | shadow | 0.92 | 1.00 | 0.85 | 0.99 | 342 | 0.02 |
| 3 | loss_only | 0.91 | 1.00 | 0.85 | 0.96 | 555 | 0.04 |
| 4 | backlog_only | 0.90 | 0.99 | 0.82 | 0.98 | 663 | 0.04 |
| 5 | gradient_only | 0.88 | 0.99 | 0.79 | 0.94 | 980 | 0.06 |
| 6 | shadow_m4 | 0.88 | 0.99 | 0.78 | 0.98 | 885 | 0.05 |
| 7 | shadow_verified | 0.85 | 1.00 | 0.74 | 0.94 | 706 | 0.01 |
| 8 | deficit_only | 0.75 | 0.98 | 0.60 | 0.82 | 1174 | 0.09 |
| 9 | bbr | 0.75 | 0.79 | 0.71 | 0.87 | 924 | 1.65 |
| 10 | offered_only | 0.68 | 1.00 | 0.52 | 0.67 | 770 | 0.00 |

