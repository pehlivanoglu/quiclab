# Step 8 part E: per-flow-queue egresses as a negative control

## E5. Which egresses are per-flow, per cell (qdiscs.txt)

| cell | egress (hop): AQM | ordinary (single-queue) shaped egresses | true sets |
|---|---|---|---|
| C10-hindep-s030-fq_codel | up (r1->r2): fq_codel, a (r2->switch-a): fq_codel, b (r2->switch-b): fq_codel | none | none (no group is correct) |
| C12-amixed-access-fq_codel | main (router->switch): fq_codel | none | none (no group is correct) |
| C7-hhier-s030-fq_codel | up (r1->r2): fq_codel, a (r2->switch-a): fq_codel, b (r2->switch-b): fq_codel | none | none (no group is correct) |
| C9-hdepth-tree16-fq_codel | root (rr->r0): fq_codel, X (r0->r1): fq_codel, Y (r0->r2): fq_codel, A (r1->switch-a): fq_codel, B (r1->switch-b): fq_codel, C (r2->switch-c): fq_codel, D (r2->switch-d): fq_codel | none | none (no group is correct) |
| M8-hhier-mixab-mixab | up (r1->r2): pfifo, a (r2->switch-a): pfifo, b (r2->switch-b): fq_codel | up, a | up {8}, a {4} |

## E1. False groupings per close (mean over the run) and at the end, onset source v2-owd; rep 1 / rep 2

| cell | method | closes | false groups / close | false pairs / close | mixed pairs / close (M8) | correct pairs / close | false groups at end | false pairs at end | mixed at end |
|---|---|---|---|---|---|---|---|---|---|
| C10-hindep-s030-fq_codel | ecg | 118 / 107 | 0.86 / 1.79 | 5.73 / 5.30 | 0.00 / 0.00 | 0.00 / 0.00 | 1 / 2 | 6 / 2 | 0 / 0 |
| C10-hindep-s030-fq_codel | h3 | 118 / 107 | 0.89 / 3.59 | 1.04 / 4.28 | 0.00 / 0.00 | 0.00 / 0.00 | 2 / 5 | 4 / 5 | 0 / 0 |
| C12-amixed-access-fq_codel | ecg | 32 / 30 | 0.25 / 0.80 | 1.16 / 3.07 | 0.00 / 0.00 | 0.00 / 0.00 | 1 / 1 | 6 / 3 | 0 / 0 |
| C12-amixed-access-fq_codel | h3 | 32 / 30 | 0.00 / 0.30 | 0.00 / 0.30 | 0.00 / 0.00 | 0.00 / 0.00 | 0 / 1 | 0 / 1 | 0 / 0 |
| C7-hhier-s030-fq_codel | ecg | 134 / 139 | 1.42 / 1.43 | 1.42 / 1.55 | 0.00 / 0.00 | 0.00 / 0.00 | 1 / 2 | 1 / 2 | 0 / 0 |
| C7-hhier-s030-fq_codel | h3 | 134 / 139 | 1.97 / 2.45 | 2.42 / 4.72 | 0.00 / 0.00 | 0.00 / 0.00 | 4 / 3 | 4 / 8 | 0 / 0 |
| C9-hdepth-tree16-fq_codel | ecg | 101 / 102 | 1.36 / 1.99 | 4.70 / 4.89 | 0.00 / 0.00 | 0.00 / 0.00 | 2 / 2 | 7 / 2 | 0 / 0 |
| C9-hdepth-tree16-fq_codel | h3 | 101 / 102 | 3.50 / 3.47 | 12.15 / 15.71 | 0.00 / 0.00 | 0.00 / 0.00 | 5 / 3 | 28 / 26 | 0 / 0 |
| M8-hhier-mixab-mixab | ecg | 94 / 88 | 0.43 / 0.62 | 0.40 / 0.59 | 0.09 / 0.14 | 5.33 / 5.49 | 1 / 1 | 0 / 1 | 4 / 0 |
| M8-hhier-mixab-mixab | h3 | 94 / 88 | 1.41 / 1.00 | 4.91 / 4.74 | 8.90 / 1.85 | 5.82 / 4.84 | 2 / 1 | 7 / 6 | 12 / 4 |

## E2. Lifetime of false groups (v2-owd): closes and seconds from the first to the last close in which the group holds a false or mixed pair; the stimulus active when it first did

| cell | method | rep | false groups | life p50 closes (max) | life p50 s (max) | created during (count) |
|---|---|---|---|---|---|---|
| C10-hindep-s030-fq_codel | ecg | 1 | 2 | 54 (104) | 258 (505) | leaf+up (b+up) 1; up (up) 1 |
| C10-hindep-s030-fq_codel | ecg | 2 | 4 | 50 (69) | 258 (385) | up (up) 2; leaf (b) 2 |
| C10-hindep-s030-fq_codel | h3 | 1 | 2 | 58 (88) | 275 (433) | up (up) 2 |
| C10-hindep-s030-fq_codel | h3 | 2 | 6 | 59 (99) | 314 (523) | up (up) 6 |
| C12-amixed-access-fq_codel | ecg | 1 | 1 | 20 (20) | 206 (206) | leaf (main) 1 |
| C12-amixed-access-fq_codel | ecg | 2 | 1 | 24 (24) | 278 (278) | leaf (main) 1 |
| C12-amixed-access-fq_codel | h3 | 1 | 0 | - | - | - |
| C12-amixed-access-fq_codel | h3 | 2 | 1 | 9 (9) | 141 (141) | leaf (main) 1 |
| C7-hhier-s030-fq_codel | ecg | 1 | 4 | 68 (107) | 498 (764) | leaf (a+b) 2; leaf (a) 1; leaf (b) 1 |
| C7-hhier-s030-fq_codel | ecg | 2 | 7 | 32 (83) | 234 (572) | leaf (b) 2; leaf (a) 2; leaf (a+b) 1; up (up) 1 |
| C7-hhier-s030-fq_codel | h3 | 1 | 5 | 99 (104) | 704 (719) | none 2; up (up) 2; leaf (a+b) 1 |
| C7-hhier-s030-fq_codel | h3 | 2 | 3 | 106 (128) | 731 (870) | leaf+up (a+up) 2; leaf (a+b) 1 |
| C9-hdepth-tree16-fq_codel | ecg | 1 | 3 | 48 (93) | 407 (807) | root (root) 2; mid (X) 1 |
| C9-hdepth-tree16-fq_codel | ecg | 2 | 4 | 54 (97) | 465 (823) | root (root) 2; leaf (D) 1; leaf (A+C) 1 |
| C9-hdepth-tree16-fq_codel | h3 | 1 | 10 | 36 (96) | 288 (836) | mid (X) 3; root (root) 3; leaf (A+C) 2; mid (Y) 1 |
| C9-hdepth-tree16-fq_codel | h3 | 2 | 6 | 79 (90) | 659 (744) | leaf (A+C) 2; none 2; root (root) 1; mid (Y) 1 |
| M8-hhier-mixab-mixab | ecg | 1 | 2 | 40 (77) | 386 (772) | leaf (a+b) 1; up (up) 1 |
| M8-hhier-mixab-mixab | ecg | 2 | 4 | 20 (27) | 184 (310) | leaf (a+b) 3; leaf (b) 1 |
| M8-hhier-mixab-mixab | h3 | 1 | 4 | 28 (76) | 260 (746) | leaf (a) 2; up (up) 1; leaf+up (a+up) 1 |
| M8-hhier-mixab-mixab | h3 | 2 | 3 | 43 (69) | 406 (731) | leaf (b) 1; up (up) 1; leaf+up (a+up) 1 |

## E3. Recurring observed sets (v2-owd): every set of >= 2 clients that is not a true set is a false set

| cell | rep | events | false sets >= 2 / >= 3 / >= 4 | true sets >= 2 | most frequent sets (count) |
|---|---|---|---|---|---|
| C10-hindep-s030-fq_codel | 1 | 118 | 9 / 6 / 5 | 0 of 0 | {b3,b4} 6, {a3,b3} 5, {a3,a4,b2,b3,b4} 5, {a4,b2,b4} 4, {a3,a4} 4, {a4,b2} 3 |
| C10-hindep-s030-fq_codel | 2 | 107 | 10 / 5 / 3 | 0 of 0 | {b3,b4} 12, {a3,a4,b3,b4} 11, {a3,a4} 7, {a4,b4} 3, {a3,b3} 3, {a3,a4,b4} 2 |
| C12-amixed-access-fq_codel | 1 | 32 | 2 / 2 / 0 | 0 of 0 | {sub-b,sub-c,sub-d} 3, {sub-a,sub-b,sub-c,sub-d} 3, {sub-b,sub-c} 1 |
| C12-amixed-access-fq_codel | 2 | 30 | 3 / 3 / 0 | 0 of 0 | {sub-b,sub-c} 3, {sub-b,sub-c,sub-d} 3, {sub-a,sub-b,sub-c,sub-d} 3, {sub-c,sub-d} 1 |
| C7-hhier-s030-fq_codel | 1 | 134 | 9 / 7 / 6 | 0 of 0 | {a3,a4} 12, {b3,b4} 12, {a3,a4,b3,b4} 10, {a4,b4} 5, {a3,b3} 4, {a1,a2} 4 |
| C7-hhier-s030-fq_codel | 2 | 139 | 10 / 7 / 7 | 0 of 0 | {b3,b4} 12, {a3,a4} 11, {a3,b3} 8, {b1,b2} 6, {a4,b4} 6, {a3,a4,b3,b4} 6 |
| C9-hdepth-tree16-fq_codel | 1 | 101 | 9 / 4 / 1 | 0 of 0 | {a4,b4} 6, {c2,c4,d4} 3, {a4,c4} 3, {a2,a3} 3, {c2,c3} 2, {c4,d4} 2 |
| C9-hdepth-tree16-fq_codel | 2 | 102 | 9 / 6 / 4 | 0 of 0 | {a4,c4} 5, {a4,b4} 5, {c2,c3} 4, {c4,d4} 4, {a4,b4,c4,d4} 3, {d2,d3} 3 |
| M8-hhier-mixab-mixab | 1 | 94 | 6 / 2 / 2 | 2 of 2 | **{a1,a2,a3,a4}** 20, {b3,b4} 12, **{a1,a2,a3,a4,b1,b2,b3,b4}** 9, {b1,b2} 4, {a1,a2,a3,a4,b2,b3,b4} 2, {a1,a2,a3,a4,b1,b2,b3} 2 |
| M8-hhier-mixab-mixab | 2 | 88 | 5 / 3 / 2 | 2 of 2 | **{a1,a2,a3,a4}** 18, {b3,b4} 12, **{a1,a2,a3,a4,b1,b2,b3,b4}** 12, {b1,b2} 4, {a1,a2,a3,a4,b3,b4} 3, {b2,b4} 2 |

## E1. False groupings per close (mean over the run) and at the end, onset source truth; rep 1 / rep 2

| cell | method | closes | false groups / close | false pairs / close | mixed pairs / close (M8) | correct pairs / close | false groups at end | false pairs at end | mixed at end |
|---|---|---|---|---|---|---|---|---|---|
| C10-hindep-s030-fq_codel | ecg | 55 / 58 | 1.58 / 1.40 | 4.33 / 4.16 | 0.00 / 0.00 | 0.00 / 0.00 | 2 / 2 | 4 / 2 | 0 / 0 |
| C10-hindep-s030-fq_codel | h3 | 55 / 58 | 1.07 / 1.67 | 2.27 / 1.67 | 0.00 / 0.00 | 0.00 / 0.00 | 2 / 2 | 4 / 2 | 0 / 0 |
| C12-amixed-access-fq_codel | ecg | 21 / 21 | 0.57 / 0.76 | 1.43 / 2.29 | 0.00 / 0.00 | 0.00 / 0.00 | 1 / 1 | 3 / 3 | 0 / 0 |
| C12-amixed-access-fq_codel | h3 | 21 / 21 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0 / 0 | 0 / 0 | 0 / 0 |
| C7-hhier-s030-fq_codel | ecg | 63 / 63 | 1.75 / 1.87 | 1.75 / 1.87 | 0.00 / 0.00 | 0.00 / 0.00 | 2 / 2 | 2 / 2 | 0 / 0 |
| C7-hhier-s030-fq_codel | h3 | 63 / 63 | 1.05 / 1.03 | 1.05 / 1.03 | 0.00 / 0.00 | 0.00 / 0.00 | 2 / 2 | 2 / 2 | 0 / 0 |
| C9-hdepth-tree16-fq_codel | ecg | 48 / 48 | 0.90 / 0.48 | 4.12 / 0.60 | 0.00 / 0.00 | 0.00 / 0.00 | 1 / 0 | 6 / 0 | 0 / 0 |
| C9-hdepth-tree16-fq_codel | h3 | 48 / 48 | 0.56 / 0.67 | 2.52 / 1.69 | 0.00 / 0.00 | 0.00 / 0.00 | 2 / 1 | 7 / 6 | 0 / 0 |
| M8-hhier-mixab-mixab | ecg | 63 / 63 | 0.87 / 0.97 | 0.87 / 0.97 | 0.00 / 0.00 | 5.43 / 5.62 | 1 / 1 | 1 / 1 | 0 / 0 |
| M8-hhier-mixab-mixab | h3 | 63 / 63 | 1.10 / 0.97 | 1.70 / 4.49 | 8.19 / 1.37 | 6.06 / 5.10 | 1 / 1 | 1 / 6 | 0 / 4 |

## E2. Lifetime of false groups (truth): closes and seconds from the first to the last close in which the group holds a false or mixed pair; the stimulus active when it first did

| cell | method | rep | false groups | life p50 closes (max) | life p50 s (max) | created during (count) |
|---|---|---|---|---|---|---|
| C10-hindep-s030-fq_codel | ecg | 1 | 4 | 18 (47) | 175 (488) | leaf (b) 3; leaf+up (b+up) 1 |
| C10-hindep-s030-fq_codel | ecg | 2 | 3 | 24 (33) | 214 (335) | leaf (b) 2; leaf (a) 1 |
| C10-hindep-s030-fq_codel | h3 | 1 | 2 | 30 (43) | 260 (418) | up (up) 2 |
| C10-hindep-s030-fq_codel | h3 | 2 | 2 | 48 (52) | 454 (490) | up (up) 2 |
| C12-amixed-access-fq_codel | ecg | 1 | 1 | 12 (12) | 206 (206) | leaf (main) 1 |
| C12-amixed-access-fq_codel | ecg | 2 | 1 | 16 (16) | 278 (278) | leaf (main) 1 |
| C12-amixed-access-fq_codel | h3 | 1 | 0 | - | - | - |
| C12-amixed-access-fq_codel | h3 | 2 | 0 | - | - | - |
| C7-hhier-s030-fq_codel | ecg | 1 | 2 | 58 (61) | 861 (914) | leaf (a) 1; leaf (a+b) 1 |
| C7-hhier-s030-fq_codel | ecg | 2 | 2 | 60 (62) | 874 (892) | leaf (b) 1; leaf (a) 1 |
| C7-hhier-s030-fq_codel | h3 | 1 | 2 | 34 (46) | 460 (649) | up (up) 2 |
| C7-hhier-s030-fq_codel | h3 | 2 | 2 | 32 (34) | 515 (538) | leaf+up (a+up) 1; up (up) 1 |
| C9-hdepth-tree16-fq_codel | ecg | 1 | 1 | 45 (45) | 804 (804) | root (root) 1 |
| C9-hdepth-tree16-fq_codel | ecg | 2 | 3 | 4 (18) | 57 (322) | mid (Y) 1; leaf (A+C) 1; leaf (C) 1 |
| C9-hdepth-tree16-fq_codel | h3 | 1 | 2 | 18 (26) | 320 (473) | root (root) 1; leaf (A+C) 1 |
| C9-hdepth-tree16-fq_codel | h3 | 2 | 2 | 16 (27) | 264 (449) | leaf (A+C) 1; mid (Y) 1 |
| M8-hhier-mixab-mixab | ecg | 1 | 1 | 55 (55) | 808 (808) | leaf (a+b) 1 |
| M8-hhier-mixab-mixab | ecg | 2 | 1 | 62 (62) | 892 (892) | leaf (b) 1 |
| M8-hhier-mixab-mixab | h3 | 1 | 2 | 34 (56) | 489 (811) | up (up) 1; leaf (a+b) 1 |
| M8-hhier-mixab-mixab | h3 | 2 | 2 | 30 (55) | 453 (810) | leaf (b) 1; leaf (a+b) 1 |

## E3. Recurring observed sets (truth): every set of >= 2 clients that is not a true set is a false set

| cell | rep | events | false sets >= 2 / >= 3 / >= 4 | true sets >= 2 | most frequent sets (count) |
|---|---|---|---|---|---|
| C10-hindep-s030-fq_codel | 1 | 55 | 5 / 4 / 4 | 0 of 0 | {b3,b4} 16, {a3,a4,b2,b3,b4} 13, {a3,a4} 10, {a3,a4,b2} 4, {b2,b3,b4} 2, {a4,b2,b3,b4} 1 |
| C10-hindep-s030-fq_codel | 2 | 58 | 4 / 3 / 3 | 0 of 0 | {b3,b4} 19, {a3,a4,b3,b4} 17, {a3,a4} 16, {a3,a4,b1,b3,b4} 2, {a2,a3,a4,b3,b4} 1, {a4,b4} 1 |
| C12-amixed-access-fq_codel | 1 | 21 | 1 / 1 / 1 | 0 of 0 | {sub-b,sub-c,sub-d} 7, {sub-b,sub-c} 1, {sub-a,sub-b,sub-c,sub-d} 1 |
| C12-amixed-access-fq_codel | 2 | 21 | 1 / 1 / 1 | 0 of 0 | {sub-b,sub-c,sub-d} 9 |
| C7-hhier-s030-fq_codel | 1 | 63 | 3 / 3 / 3 | 0 of 0 | {a3,a4} 21, {b3,b4} 21, {a3,a4,b3,b4} 19, {a3,a4,b4} 1, {a4,b4} 1 |
| C7-hhier-s030-fq_codel | 2 | 63 | 3 / 3 / 3 | 0 of 0 | {b3,b4} 21, {a3,a4} 21, {a3,a4,b3,b4} 18, {a3,a4,b1,b3,b4} 1, {a4,b3,b4} 1, {a1,a3,a4,b3,b4} 1 |
| C9-hdepth-tree16-fq_codel | 1 | 48 | 4 / 3 / 3 | 0 of 0 | {a4,c4} 5, {c2,c4,d4} 5, {a4,b4} 5, {a4,b4,c4,d4} 2, {a4,b4,c2,c4,d4} 1, {c1,c2,c4,d4} 1 |
| C9-hdepth-tree16-fq_codel | 2 | 48 | 4 / 4 / 3 | 0 of 0 | {a4,c4} 6, {c4,d4} 5, {a4,b4} 5, {a4,b4,c4,d4} 3, {a4,b4,c4,d3,d4} 1, {a2,a4,b2,b4} 1 |
| M8-hhier-mixab-mixab | 1 | 63 | 2 / 2 / 2 | 2 of 2 | **{a1,a2,a3,a4}** 21, {b3,b4} 21, **{a1,a2,a3,a4,b1,b2,b3,b4}** 15, {a1,a2,a3,a4,b3,b4} 6 |
| M8-hhier-mixab-mixab | 2 | 63 | 2 / 2 / 2 | 2 of 2 | **{a1,a2,a3,a4}** 21, {b3,b4} 20, **{a1,a2,a3,a4,b1,b2,b3,b4}** 15, {a1,a2,a3,a4,b3,b4} 5, {a1,a2,a3,a4,b2,b3,b4} 1, {b2,b3,b4} 1 |

## Ea. Sub-queue pinning check (every fq_codel and mixab run; truth/gtq-params.csv)

Runs checked: 20; egresses where two instrumented clients share a sub-queue index: 0. Other 5-tuples found in a client's sub-queue: {'same client (other 5-tuple to it)': 529, 'other traffic': 34}.

- v3-C10-hindep-s030-fq_codel-r1: r1->r2: 8 clients, indices 768-775, shared indices none
- v3-C10-hindep-s030-fq_codel-r1: r2->switch-a: 4 clients, indices 768-771, shared indices none
- v3-C10-hindep-s030-fq_codel-r1: r2->switch-b: 4 clients, indices 772-775, shared indices none
- v3-C10-hindep-s030-fq_codel-r2: r1->r2: 8 clients, indices 768-775, shared indices none
- v3-C10-hindep-s030-fq_codel-r2: r2->switch-a: 4 clients, indices 768-771, shared indices none
- v3-C10-hindep-s030-fq_codel-r2: r2->switch-b: 4 clients, indices 772-775, shared indices none
- v3-C12-amixed-access-fq_codel-r1: router->switch: 4 clients, indices 768-772, shared indices none
- v3-C12-amixed-access-fq_codel-r1: ra->sub-a: 1 clients, indices 768-768, shared indices none
- v3-C12-amixed-access-fq_codel-r1: rb->sub-b: 1 clients, indices 769-769, shared indices none
- v3-C12-amixed-access-fq_codel-r1: rc->sub-c: 1 clients, indices 770-770, shared indices none
- v3-C12-amixed-access-fq_codel-r1: rd->sub-d: 1 clients, indices 772-772, shared indices none
- v3-C12-amixed-access-fq_codel-r2: router->switch: 4 clients, indices 768-772, shared indices none
- v3-C12-amixed-access-fq_codel-r2: ra->sub-a: 1 clients, indices 768-768, shared indices none
- v3-C12-amixed-access-fq_codel-r2: rb->sub-b: 1 clients, indices 769-769, shared indices none
- v3-C12-amixed-access-fq_codel-r2: rc->sub-c: 1 clients, indices 770-770, shared indices none
- v3-C12-amixed-access-fq_codel-r2: rd->sub-d: 1 clients, indices 772-772, shared indices none
- v3-C14-rrev-rev-fq_codel-r1: r0->r1: 4 clients, indices 768-772, shared indices none
- v3-C14-rrev-rev-fq_codel-r1: r1->switch: 4 clients, indices 768-772, shared indices none
- v3-C14-rrev-rev-fq_codel-r2: r0->r1: 4 clients, indices 768-772, shared indices none
- v3-C14-rrev-rev-fq_codel-r2: r1->switch: 4 clients, indices 768-772, shared indices none
- v3-C2-sburst-s030u070-fq_codel-r1: router->switch: 4 clients, indices 768-772, shared indices none
- v3-C2-sburst-s030u070-fq_codel-r2: router->switch: 4 clients, indices 768-772, shared indices none
- v3-C4-sramp-s030u070-fq_codel-r1: router->switch: 4 clients, indices 768-772, shared indices none
- v3-C4-sramp-s030u070-fq_codel-r2: router->switch: 4 clients, indices 768-772, shared indices none
- v3-C5-stcp-s030u070-fq_codel-r1: router->switch: 4 clients, indices 768-772, shared indices none
- v3-C5-stcp-s030u070-fq_codel-r2: router->switch: 4 clients, indices 768-772, shared indices none
- v3-C6-sjoin-s030u070-fq_codel-r1: router->switch: 4 clients, indices 768-772, shared indices none
- v3-C6-sjoin-s030u070-fq_codel-r2: router->switch: 4 clients, indices 768-772, shared indices none
- v3-C7-hhier-s030-fq_codel-r1: r1->r2: 8 clients, indices 768-775, shared indices none
- v3-C7-hhier-s030-fq_codel-r1: r2->switch-a: 4 clients, indices 768-771, shared indices none
- v3-C7-hhier-s030-fq_codel-r1: r2->switch-b: 4 clients, indices 772-775, shared indices none
- v3-C7-hhier-s030-fq_codel-r2: r1->r2: 8 clients, indices 768-775, shared indices none
- v3-C7-hhier-s030-fq_codel-r2: r2->switch-a: 4 clients, indices 768-771, shared indices none
- v3-C7-hhier-s030-fq_codel-r2: r2->switch-b: 4 clients, indices 772-775, shared indices none
- v3-C9-hdepth-tree16-fq_codel-r1: rr->r0: 16 clients, indices 768-783, shared indices none
- v3-C9-hdepth-tree16-fq_codel-r1: r0->r1: 8 clients, indices 768-775, shared indices none
- v3-C9-hdepth-tree16-fq_codel-r1: r0->r2: 8 clients, indices 776-783, shared indices none
- v3-C9-hdepth-tree16-fq_codel-r1: r1->switch-a: 4 clients, indices 768-771, shared indices none
- v3-C9-hdepth-tree16-fq_codel-r1: r1->switch-b: 4 clients, indices 772-775, shared indices none
- v3-C9-hdepth-tree16-fq_codel-r1: r2->switch-c: 4 clients, indices 776-779, shared indices none
- v3-C9-hdepth-tree16-fq_codel-r1: r2->switch-d: 4 clients, indices 780-783, shared indices none
- v3-C9-hdepth-tree16-fq_codel-r2: rr->r0: 16 clients, indices 768-783, shared indices none
- v3-C9-hdepth-tree16-fq_codel-r2: r0->r1: 8 clients, indices 768-775, shared indices none
- v3-C9-hdepth-tree16-fq_codel-r2: r0->r2: 8 clients, indices 776-783, shared indices none
- v3-C9-hdepth-tree16-fq_codel-r2: r1->switch-a: 4 clients, indices 768-771, shared indices none
- v3-C9-hdepth-tree16-fq_codel-r2: r1->switch-b: 4 clients, indices 772-775, shared indices none
- v3-C9-hdepth-tree16-fq_codel-r2: r2->switch-c: 4 clients, indices 776-779, shared indices none
- v3-C9-hdepth-tree16-fq_codel-r2: r2->switch-d: 4 clients, indices 780-783, shared indices none
- v3-G3-sburst-s030u070-fq_codel-r1: router->switch: 4 clients, indices 768-772, shared indices none
- v3-M8-hhier-mixab-mixab-r1: no gtq-params (GT-Q invalid)
- v3-M8-hhier-mixab-mixab-r2: r2->switch-b: 4 clients, indices 772-775, shared indices none

