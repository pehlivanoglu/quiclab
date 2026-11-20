# NPR v3 diagnosis (items 2a-2e; diag3.py)

Single-queue runs 227 (97 r1 / 89 r2); alpha 0.05. Errors: none.

Check against rows-v3: false-split share B r1 0.134 (v3 0.134); B r2 0.034 (v3 0.034); corr r1 0.008 (v3 0.008); corr r2 0.008 (v3 0.008); A-m0.20-f0.05 r1 0.017 (v3 0.017); A-m0.20-f0.05 r2 0.008 (v3 0.008); A-m0.10-f0.05 r1 0.017 (v3 0.017); A-m0.10-f0.05 r2 0.008 (v3 0.008). Pair vectors identical: True.

## 2a. V-B false splits (leaf alone, original order), r1 against r2

### B, r1: 16 false splits of 119 leaves (0.134)

Split-off part size: {1: 15, 3: 1}; split-off part holds a late responder: 8 / 16; runs with a false split: 16 (max 1 per run); from wide-RTT leaves (access-delay span > 20 ms): 0 / 16.

| cell | false splits / leaves |
|---|---|
| G1-sburst-pfifo | 2 / 5 |
| C11-huneven-pfifo | 1 / 3 |
| C12-amixed-codel | 1 / 1 |
| C12-amixed-pfifo | 1 / 1 |
| C12-amixed-pie | 1 / 1 |
| C4-sramp-pfifo | 1 / 1 |
| C6-sjoin-codel | 1 / 1 |
| C7-hhier-pie | 1 / 2 |
| G1-calm-pfifo | 1 / 1 |
| M2-sburst-codel | 1 / 1 |
| A4-hhier-codel | 1 / 2 |
| A4-hhier-pie | 1 / 2 |
| A7-amixed-codel | 1 / 1 |
| A7-amixed-pfifo | 1 / 1 |
| G2-gsize2-pfifo | 1 / 4 |

| run | leaf (size) | split at event / events | part size | split-off members (miss rate, onset-lag share) | access ms: split-off mean vs rest mean (rest range) | wide-RTT leaf | late responder |
|---|---|---|---|---|---|---|---|
| v3-C11-huneven-uneven-pfifo-r1 | C (9) | 12 / 27 | 3 | c6 miss 0.00 lag -, c7 miss 0.00 lag -, c9 miss 0.04 lag 1.00 | 8.3 vs 11.7 (5-20) | no (span 15) | no |
| v3-C12-amixed-access-codel-r1 | main (4) | 5 / 21 | 1 | sub-b miss 0.43 lag 0.00 | 7.5 vs 12.5 (5-20) | no (span 15) | yes |
| v3-C12-amixed-access-pfifo-r1 | main (4) | 5 / 21 | 1 | sub-b miss 0.43 lag 0.00 | 7.5 vs 12.5 (5-20) | no (span 15) | yes |
| v3-C12-amixed-access-pie-r1 | main (4) | 5 / 21 | 1 | sub-b miss 0.43 lag 0.00 | 7.5 vs 12.5 (5-20) | no (span 15) | yes |
| v3-C4-sramp-s030u070-pfifo-r1 | main (4) | 6 / 13 | 1 | sub-a miss 0.15 lag 1.00 | 5.0 vs 13.3 (7.5-20) | no (span 15) | yes |
| v3-C6-sjoin-s030u070-codel-r1 | main (4) | 4 / 16 | 1 | sub-d miss 0.08 lag 1.00 | 20.0 vs 8.3 (5-12.5) | no (span 15) | no |
| v3-C7-hhier-s030-pie-r1 | b (4) | 43 / 47 | 1 | b4 miss 0.02 lag 1.00 | 20.0 vs 8.3 (5-12.5) | no (span 15) | no |
| v3-G1-calm-legacy-pfifo-r1 | main (4) | 3 / 3 | 1 | sub-d miss 0.00 lag - | 20.0 vs 8.3 (5-12.5) | no (span 15) | no |
| v3-M2-sburst-capdrop-codel-r1 | main (4) | 3 / 20 | 1 | sub-d miss 0.05 lag 1.00 | 20.0 vs 8.3 (5-12.5) | no (span 15) | no |
| v4-A4-hhier-def-codel-r1 | b (4) | 35 / 45 | 1 | b1 miss 0.07 lag 1.00 | 5.0 vs 13.3 (7.5-20) | no (span 15) | yes |
| v4-A4-hhier-def-pie-r1 | b (4) | 34 / 46 | 1 | b3 miss 0.07 lag 1.00 | 12.5 vs 10.8 (5-20) | no (span 15) | yes |
| v4-A7-amixed-def-codel-r1 | main (4) | 5 / 21 | 1 | sub-b miss 0.43 lag 0.00 | 7.5 vs 12.5 (5-20) | no (span 15) | yes |
| v4-A7-amixed-def-pfifo-r1 | main (4) | 5 / 21 | 1 | sub-b miss 0.43 lag 0.00 | 7.5 vs 12.5 (5-20) | no (span 15) | yes |
| v4-G1-sburst-n24-pfifo-r1 | main (24) | 2 / 20 | 1 | sub-14 miss 0.05 lag 0.00 | 7.5 vs 11.4 (5-20) | no (span 15) | no |
| v4-G1-sburst-n40-pfifo-r1 | main (40) | 13 / 21 | 1 | sub-24 miss 0.00 lag - | 20.0 vs 11.0 (5-20) | no (span 15) | no |
| v4-G2-gsize2-n12-pfifo-r1 | a (12) | 2 / 20 | 1 | a6 miss 0.05 lag 0.00 | 7.5 vs 11.6 (5-20) | no (span 15) | no |

### B, r2: 4 false splits of 118 leaves (0.034)

Split-off part size: {1: 4}; split-off part holds a late responder: 4 / 4; runs with a false split: 4 (max 1 per run); from wide-RTT leaves (access-delay span > 20 ms): 0 / 4.

| cell | false splits / leaves |
|---|---|
| C4-sramp-codel | 1 / 1 |
| C5-stcp-codel | 1 / 1 |
| M8-hhier-mixab | 1 / 2 |
| G2-gsize2-pfifo | 1 / 4 |

| run | leaf (size) | split at event / events | part size | split-off members (miss rate, onset-lag share) | access ms: split-off mean vs rest mean (rest range) | wide-RTT leaf | late responder |
|---|---|---|---|---|---|---|---|
| v3-C4-sramp-s030u070-codel-r2 | main (4) | 5 / 11 | 1 | sub-c miss 0.18 lag 1.00 | 12.5 vs 10.8 (5-20) | no (span 15) | yes |
| v3-C5-stcp-s030u070-codel-r2 | main (4) | 6 / 19 | 1 | sub-d miss 0.11 lag 0.50 | 20.0 vs 8.3 (5-12.5) | no (span 15) | yes |
| v3-M8-hhier-mixab-mixab-r2 | b (3) | 16 / 50 | 1 | b2 miss 0.54 lag 0.04 | 7.5 vs 16.2 (12.5-20) | no (span 12.5) | yes |
| v4-G2-gsize2-n12-pfifo-r2 | b (12) | 17 / 20 | 1 | b6 miss 0.10 lag 0.50 | 7.5 vs 11.6 (5-20) | no (span 15) | yes |

Cells whose count of B false splits differs between r1 and r2: A4-hhier-codel 1 / 0; A4-hhier-pie 1 / 0; A7-amixed-codel 1 / 0; A7-amixed-pfifo 1 / 0; C11-huneven-pfifo 1 / 0; C12-amixed-codel 1 / 0; C12-amixed-pfifo 1 / 0; C12-amixed-pie 1 / 0; C4-sramp-codel 0 / 1; C4-sramp-pfifo 1 / 0; C5-stcp-codel 0 / 1; C6-sjoin-codel 1 / 0; C7-hhier-pie 1 / 0; G1-calm-pfifo 1 / 0; G1-sburst-pfifo 2 / 0; M2-sburst-codel 1 / 0; M8-hhier-mixab 0 / 1

| rep | leaves with a late responder / leaves | false splits in those leaves | in leaves without |
|---|---|---|---|
| r1 | 24 / 119 | 12 / 24 | 4 / 95 |
| r2 | 26 / 118 | 4 / 26 | 0 / 92 |

Leaf-alone false splits, other readers and SETS (r1 / r2): corr 1 / 1; A-m0.20-f0.05 2 / 1; A-m0.10-f0.05 2 / 1.

## 2b. False merges behind pair precision (corr, V-A, and B for reference)

### NPR-corr a0.05

| rep | pair P | different-leaf pairs together: before the root's first split / after | runs never split (2+ leaves) | their share of different-leaf pairs |
|---|---|---|---|---|
| r1 | 0.930 | 2664 / 3751 (0.42 before) | 0 | 0.00 |
| r2 | 0.871 | 10671 / 2008 (0.84 before) | 2 | 0.03 |

r1: cells by false-merge pairs (share of all different-leaf pairs together; cell pair P):
| cell | share | cell pair P | top leaf pairs (count) |
|---|---|---|---|
| G2-gsize2-pfifo | 0.30 | 0.727 | a|b 1952 |
| C9-hdepth-codel | 0.22 | 0.441 | A|C 752, A|D 144, C|D 144 |
| C9-hdepth-pfifo | 0.19 | 0.485 | A|B 304, A|C 213, A|D 192 |
| M8-hhier-mixab | 0.07 | 0.526 | -|b 264, a|b 80, -|a 68 |
| C8-hhier-pfifo | 0.03 | 0.815 | a|b 192 |
| C11-huneven-pfifo | 0.03 | 0.948 | A|C 90, B|C 45, A|B 40 |
| A6-huneven-pfifo | 0.03 | 0.939 | A|C 90, B|C 45, A|B 40 |
| M7-hhier-pfifo | 0.02 | 0.784 | a|b 160 |

Cells with their own pair P < 0.9: C7-hhier-pie, C8-hhier-pfifo, C9-hdepth-codel, C9-hdepth-pfifo, G2-gsize2-pfifo, M7-hhier-pfifo, M8-hhier-mixab. Pair P with them 0.930, without them 0.988 (for understanding only).

r2: cells by false-merge pairs (share of all different-leaf pairs together; cell pair P):
| cell | share | cell pair P | top leaf pairs (count) |
|---|---|---|---|
| G2-gsize2-pfifo | 0.29 | 0.611 | a|b 3680 |
| C9-hdepth-pfifo | 0.12 | 0.433 | C|D 752, A|B 164, A|C 144 |
| C9-hdepth-codel | 0.08 | 0.529 | C|D 208, A|B 164, B|C 164 |
| C11-huneven-pfifo | 0.07 | 0.789 | B|C 450, A|C 360, A|B 90 |
| C11-huneven-codel | 0.06 | 0.836 | B|C 450, A|C 162, A|B 90 |
| A5-hindep-pfifo | 0.05 | 0.500 | a|b 672 |
| C10-hindep-pfifo | 0.05 | 0.515 | a|b 656 |
| A6-huneven-codel | 0.05 | 0.850 | B|C 405, A|C 144, A|B 80 |

Cells with their own pair P < 0.9: A5-hindep-codel, A5-hindep-pfifo, A6-huneven-codel, A6-huneven-pfifo, C10-hindep-codel, C10-hindep-pfifo, C11-huneven-codel, C11-huneven-pfifo, C13-llong-codel, C13-llong-pfifo, C9-hdepth-codel, C9-hdepth-pfifo, G2-gsize2-pfifo, M7-hhier-pfifo, M8-hhier-mixab. Pair P with them 0.871, without them 0.999 (for understanding only).

r2: slowest 10 % of leaves (s from first stimulus >= 296 s): 11 / 11 are in runs with 2+ leaves; cells A5-hindep-pfifo 2, C10-hindep-pfifo 2, A5-hindep-codel 2, C10-hindep-codel 2, M7-hhier-pfifo 2, G2-gsize2-pfifo 1.

### NPR-A-m0.20-f0.05 a0.05

| rep | pair P | different-leaf pairs together: before the root's first split / after | runs never split (2+ leaves) | their share of different-leaf pairs |
|---|---|---|---|---|
| r1 | 0.958 | 1929 / 1769 (0.52 before) | 0 | 0.00 |
| r2 | 0.919 | 5979 / 1564 (0.79 before) | 2 | 0.05 |

r1: cells by false-merge pairs (share of all different-leaf pairs together; cell pair P):
| cell | share | cell pair P | top leaf pairs (count) |
|---|---|---|---|
| G2-gsize2-pfifo | 0.40 | 0.778 | a|b 1488 |
| C9-hdepth-pfifo | 0.16 | 0.664 | A|B 288, A|C 101, A|D 48 |
| C9-hdepth-codel | 0.14 | 0.687 | A|C 304, A|B 64, B|C 64 |
| M8-hhier-mixab | 0.09 | 0.611 | -|b 178, -|- 59, a|b 56 |
| C8-hhier-pfifo | 0.04 | 0.855 | a|b 144 |
| C11-huneven-codel | 0.03 | 0.962 | A|C 126 |
| A6-huneven-codel | 0.03 | 0.963 | A|C 126 |
| C11-huneven-pfifo | 0.02 | 0.972 | A|C 90 |

Cells with their own pair P < 0.9: C8-hhier-pfifo, C9-hdepth-codel, C9-hdepth-pfifo, G2-gsize2-pfifo, M7-hhier-pfifo, M8-hhier-mixab. Pair P with them 0.958, without them 0.993 (for understanding only).

r2: cells by false-merge pairs (share of all different-leaf pairs together; cell pair P):
| cell | share | cell pair P | top leaf pairs (count) |
|---|---|---|---|
| G2-gsize2-pfifo | 0.40 | 0.659 | a|b 2992 |
| C9-hdepth-pfifo | 0.08 | 0.657 | C|D 384, A|B 84, A|C 32 |
| A5-hindep-pfifo | 0.07 | 0.575 | a|b 496 |
| C10-hindep-pfifo | 0.06 | 0.592 | a|b 480 |
| C10-hindep-codel | 0.06 | 0.604 | a|b 448 |
| A5-hindep-codel | 0.06 | 0.596 | a|b 448 |
| C9-hdepth-codel | 0.05 | 0.748 | C|D 176, A|B 80, A|C 33 |
| M7-hhier-pfifo | 0.04 | 0.622 | a|b 336 |

Cells with their own pair P < 0.9: A5-hindep-codel, A5-hindep-pfifo, C10-hindep-codel, C10-hindep-pfifo, C13-llong-codel, C13-llong-pfifo, C9-hdepth-codel, C9-hdepth-pfifo, G2-gsize2-pfifo, M7-hhier-pfifo, M8-hhier-mixab. Pair P with them 0.919, without them 0.988 (for understanding only).

r2: slowest 10 % of leaves (s from first stimulus >= 276 s): 11 / 11 are in runs with 2+ leaves; cells C9-hdepth-pfifo 2, A5-hindep-pfifo 2, C10-hindep-pfifo 2, C10-hindep-codel 2, A5-hindep-codel 2, M7-hhier-pfifo 1.

### NPR-A-m0.10-f0.05 a0.05

| rep | pair P | different-leaf pairs together: before the root's first split / after | runs never split (2+ leaves) | their share of different-leaf pairs |
|---|---|---|---|---|
| r1 | 0.967 | 1519 / 1367 (0.53 before) | 0 | 0.00 |
| r2 | 0.933 | 5035 / 1150 (0.81 before) | 0 | 0.00 |

r1: cells by false-merge pairs (share of all different-leaf pairs together; cell pair P):
| cell | share | cell pair P | top leaf pairs (count) |
|---|---|---|---|
| G2-gsize2-pfifo | 0.40 | 0.819 | a|b 1152 |
| C9-hdepth-pfifo | 0.17 | 0.696 | A|B 208, A|C 101, A|D 48 |
| C9-hdepth-codel | 0.12 | 0.761 | A|C 224, A|B 64, B|C 64 |
| M8-hhier-mixab | 0.07 | 0.727 | -|b 74, -|- 59, a|b 40 |
| C8-hhier-pfifo | 0.04 | 0.883 | a|b 112 |
| C11-huneven-codel | 0.04 | 0.967 | A|C 108 |
| A6-huneven-codel | 0.04 | 0.968 | A|C 108 |
| C11-huneven-pfifo | 0.03 | 0.972 | A|C 90 |

Cells with their own pair P < 0.9: C8-hhier-pfifo, C9-hdepth-codel, C9-hdepth-pfifo, G2-gsize2-pfifo, M7-hhier-pfifo, M8-hhier-mixab. Pair P with them 0.967, without them 0.994 (for understanding only).

r2: cells by false-merge pairs (share of all different-leaf pairs together; cell pair P):
| cell | share | cell pair P | top leaf pairs (count) |
|---|---|---|---|
| G2-gsize2-pfifo | 0.36 | 0.723 | a|b 2208 |
| C9-hdepth-pfifo | 0.08 | 0.688 | C|D 304, A|B 84, A|C 32 |
| A5-hindep-pfifo | 0.08 | 0.575 | a|b 496 |
| C10-hindep-pfifo | 0.08 | 0.592 | a|b 480 |
| C10-hindep-codel | 0.07 | 0.604 | a|b 448 |
| A5-hindep-codel | 0.07 | 0.613 | a|b 416 |
| C9-hdepth-codel | 0.05 | 0.772 | C|D 128, A|B 80, A|C 33 |
| M7-hhier-pfifo | 0.04 | 0.697 | a|b 240 |

Cells with their own pair P < 0.9: A5-hindep-codel, A5-hindep-pfifo, C10-hindep-codel, C10-hindep-pfifo, C13-llong-codel, C13-llong-pfifo, C9-hdepth-codel, C9-hdepth-pfifo, G2-gsize2-pfifo, M7-hhier-pfifo, M8-hhier-mixab. Pair P with them 0.933, without them 0.992 (for understanding only).

r2: slowest 10 % of leaves (s from first stimulus >= 299 s): 11 / 11 are in runs with 2+ leaves; cells A5-hindep-pfifo 2, C13-llong-codel 2, C13-llong-pfifo 2, C10-hindep-pfifo 2, C10-hindep-codel 2, C9-hdepth-pfifo 1.

### NPR-B a0.05

| rep | pair P | different-leaf pairs together: before the root's first split / after | runs never split (2+ leaves) | their share of different-leaf pairs |
|---|---|---|---|---|
| r1 | 0.981 | 753 / 821 (0.48 before) | 0 | 0.00 |
| r2 | 0.969 | 1816 / 897 (0.67 before) | 0 | 0.00 |

r1: cells by false-merge pairs (share of all different-leaf pairs together; cell pair P):
| cell | share | cell pair P | top leaf pairs (count) |
|---|---|---|---|
| G2-gsize2-pfifo | 0.33 | 0.894 | a|b 520 |
| C9-hdepth-pfifo | 0.20 | 0.782 | A|C 94, A|D 64, C|D 64 |
| M8-hhier-mixab | 0.13 | 0.723 | -|- 59, a|b 56, -|b 45 |
| C8-hhier-pfifo | 0.11 | 0.828 | a|b 176 |
| C9-hdepth-codel | 0.10 | 0.875 | A|C 64, A|B 32, B|C 32 |
| M7-hhier-pfifo | 0.04 | 0.893 | a|b 64 |
| C11-huneven-codel | 0.01 | 0.994 | A|B 20 |
| A6-huneven-codel | 0.01 | 0.994 | A|B 20 |

Cells with their own pair P < 0.9: C8-hhier-pfifo, C9-hdepth-codel, C9-hdepth-pfifo, G2-gsize2-pfifo, M7-hhier-pfifo, M8-hhier-mixab. Pair P with them 0.981, without them 0.998 (for understanding only).

r2: cells by false-merge pairs (share of all different-leaf pairs together; cell pair P):
| cell | share | cell pair P | top leaf pairs (count) |
|---|---|---|---|
| G2-gsize2-pfifo | 0.15 | 0.931 | a|b 416 |
| C10-hindep-codel | 0.12 | 0.671 | a|b 336 |
| C10-hindep-pfifo | 0.12 | 0.685 | a|b 320 |
| A5-hindep-codel | 0.11 | 0.696 | a|b 288 |
| C11-huneven-codel | 0.09 | 0.934 | B|C 180, A|C 54, A|B 20 |
| A5-hindep-pfifo | 0.09 | 0.737 | a|b 240 |
| M8-hhier-mixab | 0.06 | 0.766 | -|b 74, a|b 60, -|a 20 |
| C11-huneven-pfifo | 0.05 | 0.962 | B|C 90, A|C 36 |

Cells with their own pair P < 0.9: A5-hindep-codel, A5-hindep-pfifo, C10-hindep-codel, C10-hindep-pfifo, C13-llong-codel, C13-llong-pfifo, M7-hhier-pfifo, M8-hhier-mixab. Pair P with them 0.969, without them 0.985 (for understanding only).

r2: slowest 10 % of leaves (s from first stimulus >= 42 s): 11 / 11 are in runs with 2+ leaves; cells C10-hindep-codel 2, A5-hindep-codel 2, C10-hindep-pfifo 2, M7-hhier-pfifo 2, A5-hindep-pfifo 2, M8-hhier-mixab 1.

## 2c. Column meanings

- false-split share r1 / r2: share of true leaves (each run alone through the reader, events in their recorded order) with at least one accepted split; the value in brackets is the same share averaged over 20 random orders of each leaf's events (both seeds pooled), i.e. how the share behaves when the event order is exchangeable as the e-value guarantee assumes.
- first correct group s p50 / p90: per leaf, seconds from the leaf's first own stimulus (windows.json) to the first close at which some group has F1 >= F1_OK with that leaf; the p50 of 1 means half of the leaves are grouped correctly at the close of their first event (E1-0.5 closes 0.5 s after the first onset, plus the onset delay; the table rounds to whole seconds). Format in tables-v3.md: r1 p50 / p90 / r2 p50 / p90.

## 2d / 2e. NPR rows and SETS reference rows, same runs and scorer, 95 % bootstrap intervals

Pair P interval: percentile bootstrap over runs within a seed (2000 resamples).

| method | pair P r1 [95 %] | pair P r2 [95 %] | pair R r1 / r2 | leaf F1 r1 / r2 | leaf-alone false splits r1 / r2 | root split lag (2-leaf) p50 / p90 (never) | first correct group s p50 / p90 r1 ; r2 | late joiner joined / released r1 ; r2 |
|---|---|---|---|---|---|---|---|---|
| NPR-B a0.05 | 0.981 [0.958, 0.993] | 0.969 [0.939, 0.985] | 0.957 / 0.988 | 0.962 / 0.959 | 0.134 / 0.034 | 2 / 9 (0) | 1 / 43 ; 1 / 24 | 113 / 113 ; 112 / 112 |
| NPR-corr a0.05 | 0.930 [0.856, 0.974] | 0.871 [0.777, 0.936] | 0.993 / 0.996 | 0.952 / 0.934 | 0.008 / 0.008 | 5 / 26 (2) | 1 / 70 ; 1 / 269 | 111 / 111 ; 105 / 105 |
| NPR-A-m0.20-f0.05 a0.05 | 0.958 [0.915, 0.985] | 0.919 [0.843, 0.963] | 0.992 / 0.994 | 0.958 / 0.943 | 0.017 / 0.008 | 3 / 18 (2) | 1 / 71 ; 1 / 266 | 113 / 113 ; 108 / 108 |
| NPR-A-m0.10-f0.05 a0.05 | 0.967 [0.933, 0.988] | 0.933 [0.872, 0.968] | 0.992 / 0.994 | 0.960 / 0.946 | 0.017 / 0.008 | 3 / 15 (0) | 1 / 71 ; 1 / 289 | 113 / 113 ; 108 / 110 |
| SETS@E1-0.5 k2 | 0.990 [0.975, 0.999] | 0.993 [0.982, 0.998] | 0.955 / 0.938 | 0.872 / 0.886 | - / - | 4 / 5 (0) | 25 / 107 ; 20 / 85 | 111 / 113 ; 111 / 112 |
| SETS@E1-0.5 k3 | 0.980 [0.953, 0.995] | 0.971 [0.936, 0.991] | 0.961 / 0.946 | 0.814 / 0.825 | - / - | 6 / 8 (0) | 47 / 171 ; 42 / 210 | - ; - |
| SETS@E0 k2 | 0.996 [0.987, 1.000] | 0.977 [0.933, 0.997] | 0.903 / 0.923 | 0.858 / 0.863 | - / - | (E0 events) 4 / 7 (0) | 32 / 124 ; 32 / 98 | 110 / 113 ; 111 / 111 |
| SETS@E0 k3 | 0.988 [0.970, 0.997] | 0.971 [0.926, 0.993] | 0.961 / 0.956 | 0.807 / 0.808 | - / - | (E0 events) 7 / 10 (0) | 50 / 182 ; 48 / 211 | - ; - |

SETS has no split test and no tree (it reports observed sets, which may nest inside one leaf), so a leaf-alone false-split share is not defined for it ('-'); its root split lag is the first close with two or more groups. SETS@E0 root split lag is counted in E0 events against the E1-0.5 first separating event, so it is not comparable with the other rows.

