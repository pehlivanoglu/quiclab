# Part 2: keyframe queue

### T-BASE CALM, every s and U (C1a)

| cell | egress (level) | s | U | 0.121 s U ms | minus keyframe pacing spread ms (spread) | peak p50 r1 / r2 | p90 r1 / r2 | max r1 / r2 |
|---|---|---|---|---|---|---|---|---|
| C1a-calm-legacy-codel | main (leaf / single) | legacy | 0.65 | 78.7 | 73.6 (5.1 / 3.0) | 71.9 / 69.2 | 85.5 / 81.1 | 115.1 / 136.1 |
| C1a-calm-legacy-pfifo | main (leaf / single) | legacy | 0.65 | 78.7 | 57.8 (20.8 / 19.4) | 45.9 / 47.0 | 57.6 / 56.8 | 58.2 / 58.0 |
| C1a-calm-s010u070-codel | main (leaf / single) | 0.1 | 0.7 | 8.5 | 4.9 (3.5 / 3.9) | 6.3 / 5.9 | 8.2 / 7.3 | 9.6 / 11.3 |
| C1a-calm-s010u070-pfifo | main (leaf / single) | 0.1 | 0.7 | 8.5 | 5.0 (3.5 / 4.0) | 6.1 / 6.0 | 8.3 / 7.3 | 9.4 / 10.2 |
| C1a-calm-s010u085-codel | main (leaf / single) | 0.1 | 0.85 | 10.3 | 6.8 (3.5 / 3.3) | 8.8 / 9.0 | 11.7 / 10.9 | 15.9 / 16.3 |
| C1a-calm-s010u085-pfifo | main (leaf / single) | 0.1 | 0.85 | 10.3 | 6.3 (4.0 / 4.2) | 9.1 / 8.5 | 11.5 / 10.5 | 16.0 / 15.8 |
| C1a-calm-s030u050-codel | main (leaf / single) | 0.3 | 0.5 | 18.1 | 15.2 (3.0 / 3.3) | 13.7 / 13.4 | 17.4 / 15.9 | 25.4 / 21.2 |
| C1a-calm-s030u050-pfifo | main (leaf / single) | 0.3 | 0.5 | 18.1 | 14.3 (3.8 / 2.4) | 14.5 / 13.2 | 17.4 / 16.4 | 20.2 / 19.8 |
| C1a-calm-s030u070-codel | main (leaf / single) | 0.3 | 0.7 | 25.4 | 21.2 (4.2 / 3.5) | 21.8 / 21.2 | 26.7 / 25.4 | 34.3 / 33.2 |
| C1a-calm-s030u070-pfifo | main (leaf / single) | 0.3 | 0.7 | 25.4 | 21.6 (3.8 / 2.5) | 23.2 / 21.2 | 27.0 / 25.1 | 32.6 / 30.5 |
| C1a-calm-s030u085-codel | main (leaf / single) | 0.3 | 0.85 | 30.9 | 26.9 (4.0 / 2.5) | 28.3 / 27.9 | 34.1 / 33.6 | 42.1 / 52.0 |
| C1a-calm-s030u085-pfifo | main (leaf / single) | 0.3 | 0.85 | 30.9 | 27.1 (3.7 / 3.2) | 28.3 / 27.5 | 33.8 / 32.8 | 41.9 / 38.9 |
| C1a-calm-s065u050-codel | main (leaf / single) | 0.65 | 0.5 | 39.3 | 35.3 (4.1 / 3.4) | 35.7 / 32.5 | 41.3 / 38.5 | 52.3 / 48.1 |
| C1a-calm-s065u050-pfifo | main (leaf / single) | 0.65 | 0.5 | 39.3 | 35.8 (3.5 / 3.1) | 35.0 / 32.7 | 40.5 / 39.3 | 42.5 / 42.1 |
| C1a-calm-s065u070-codel | main (leaf / single) | 0.65 | 0.7 | 55.1 | 51.4 (3.6 / 3.7) | 52.0 / 48.5 | 59.9 / 57.6 | 73.2 / 69.0 |
| C1a-calm-s065u070-pfifo | main (leaf / single) | 0.65 | 0.7 | 55.1 | 35.4 (19.6 / 13.6) | 33.6 / 34.3 | 41.0 / 40.5 | 42.1 / 42.1 |
| C1a-calm-s065u085-codel | main (leaf / single) | 0.65 | 0.85 | 66.9 | 60.1 (6.7 / 6.0) | 53.7 / 59.2 | 69.5 / 70.4 | 92.5 / 103.1 |
| C1a-calm-s065u085-pfifo | main (leaf / single) | 0.65 | 0.85 | 66.9 | 3.2 (63.7 / 61.8) | 29.8 / 28.2 | 40.3 / 37.1 | 41.9 / 42.0 |

### Hierarchies CALM, per level (C1b)

| cell | egress (level) | s | U | 0.121 s U ms | minus keyframe pacing spread ms (spread) | peak p50 r1 / r2 | p90 r1 / r2 | max r1 / r2 |
|---|---|---|---|---|---|---|---|---|
| C1b-calm-split4-pfifo | a (leaf / single) | 0.3 | 0.7 | 25.4 | 21.1 (4.3 / 3.6) | 11.0 / 11.1 | 14.1 / 14.5 | 20.1 / 23.6 |
| C1b-calm-split4-pfifo | b (leaf / single) | 0.3 | 0.7 | 25.4 | 21.1 (4.3 / 3.5) | 11.5 / 10.7 | 14.2 / 14.5 | 24.5 / 27.7 |
| C1b-calm-split4-pfifo | up (upstream) | 0.3 | 0.7 | 25.4 | 21.1 (4.3 / 3.6) | 22.7 / 20.8 | 26.4 / 24.2 | 29.6 / 31.3 |
| C1b-calm-tree16-pfifo | A (leaf / single) | 0.3 | 0.7 | 25.4 | 21.1 (4.3 / 4.2) | 7.3 / 6.6 | 10.6 / 10.6 | 17.8 / 12.9 |
| C1b-calm-tree16-pfifo | B (leaf / single) | 0.3 | 0.7 | 25.4 | 21.2 (4.2 / 4.2) | 7.4 / 7.0 | 12.0 / 11.1 | 28.7 / 20.4 |
| C1b-calm-tree16-pfifo | C (leaf / single) | 0.3 | 0.7 | 25.4 | 20.9 (4.5 / 4.4) | 7.2 / 6.4 | 10.9 / 10.1 | 17.0 / 15.9 |
| C1b-calm-tree16-pfifo | D (leaf / single) | 0.3 | 0.7 | 25.4 | 20.4 (5.0 / 4.0) | 7.0 / 6.9 | 10.6 / 10.3 | 22.5 / 15.3 |
| C1b-calm-tree16-pfifo | X (upstream) | 0.3 | 0.7 | 25.4 | 21.1 (4.3 / 4.2) | 12.0 / 10.9 | 15.0 / 13.5 | 19.3 / 18.1 |
| C1b-calm-tree16-pfifo | Y (upstream) | 0.3 | 0.7 | 25.4 | 20.4 (5.0 / 4.1) | 10.8 / 11.1 | 13.7 / 14.0 | 19.0 / 17.4 |
| C1b-calm-tree16-pfifo | root (root) | 0.3 | 0.7 | 25.4 | 20.9 (4.5 / 4.1) | 21.5 / 21.1 | 25.8 / 25.4 | 28.9 / 33.6 |
| C1b-calm-uneven-pfifo | A (leaf / single) | 0.3 | 0.7 | 25.4 | 21.2 (4.2 / 3.3) | 22.1 / 21.4 | 27.9 / 26.2 | 35.4 / 33.9 |
| C1b-calm-uneven-pfifo | B (leaf / single) | 0.3 | 0.7 | 25.4 | 21.6 (3.8 / 3.7) | 21.9 / 21.1 | 25.7 / 24.6 | 35.2 / 29.8 |
| C1b-calm-uneven-pfifo | C (leaf / single) | 0.3 | 0.7 | 25.4 | 20.7 (4.8 / 3.6) | 21.5 / 21.1 | 25.4 / 24.7 | 30.3 / 31.0 |

### Hierarchies with stimuli, calm time only, pfifo (C7 s 0.30, C8 s 0.65, C9, C11)

| cell | egress (level) | s | U | 0.121 s U ms | minus keyframe pacing spread ms (spread) | peak p50 r1 / r2 | p90 r1 / r2 | max r1 / r2 |
|---|---|---|---|---|---|---|---|---|
| C11-huneven-uneven-pfifo | A (leaf / single) | 0.3 | 0.7 | 25.4 | -8.4 (33.8 / 32.7) | 8.2 / 7.7 | 13.3 / 12.4 | 27.4 / 26.3 |
| C11-huneven-uneven-pfifo | B (leaf / single) | 0.3 | 0.7 | 25.4 | -4.0 (29.4 / 30.3) | 9.2 / 9.3 | 12.8 / 13.2 | 26.7 / 24.0 |
| C11-huneven-uneven-pfifo | C (leaf / single) | 0.3 | 0.7 | 25.4 | -2.5 (27.9 / 27.3) | 10.4 / 9.8 | 13.9 / 13.1 | 25.7 / 23.6 |
| C7-hhier-s030-pfifo | a (leaf / single) | 0.3 | 0.7 | 25.4 | -3.9 (29.3 / 29.8) | 5.2 / 5.4 | 8.4 / 9.3 | 13.4 / 19.1 |
| C7-hhier-s030-pfifo | b (leaf / single) | 0.3 | 0.7 | 25.4 | -3.8 (29.3 / 29.9) | 5.6 / 5.1 | 8.7 / 9.3 | 14.7 / 24.9 |
| C7-hhier-s030-pfifo | up (upstream) | 0.3 | 0.7 | 25.4 | -3.9 (29.3 / 29.9) | 8.8 / 8.6 | 12.2 / 12.3 | 17.6 / 26.0 |
| C8-hhier-s065-pfifo | a (leaf / single) | 0.65 | 0.7 | 55.1 | 17.5 (37.6 / 35.7) | 8.8 / 9.8 | 15.1 / 17.9 | 41.2 / 41.8 |
| C8-hhier-s065-pfifo | b (leaf / single) | 0.65 | 0.7 | 55.1 | 19.5 (35.6 / 34.8) | 8.7 / 9.0 | 15.1 / 15.7 | 41.1 / 30.9 |
| C8-hhier-s065-pfifo | up (upstream) | 0.65 | 0.7 | 55.1 | 19.1 (36.0 / 35.2) | 24.7 / 25.3 | 31.8 / 32.5 | 42.4 / 42.2 |
| C9-hdepth-tree16-pfifo | A (leaf / single) | 0.3 | 0.7 | 25.4 | -1.7 (27.1 / 26.6) | 5.3 / 5.1 | 9.4 / 8.9 | 22.5 / 15.0 |
| C9-hdepth-tree16-pfifo | B (leaf / single) | 0.3 | 0.7 | 25.4 | -1.8 (27.3 / 27.1) | 5.2 / 5.3 | 9.9 / 9.4 | 18.7 / 18.5 |
| C9-hdepth-tree16-pfifo | C (leaf / single) | 0.3 | 0.7 | 25.4 | -2.6 (28.0 / 26.8) | 5.5 / 5.5 | 9.5 / 10.2 | 15.7 / 16.2 |
| C9-hdepth-tree16-pfifo | D (leaf / single) | 0.3 | 0.7 | 25.4 | -1.0 (26.4 / 25.7) | 5.5 / 5.3 | 9.6 / 9.1 | 16.5 / 21.8 |
| C9-hdepth-tree16-pfifo | X (upstream) | 0.3 | 0.7 | 25.4 | -1.8 (27.3 / 26.6) | 6.2 / 6.1 | 10.3 / 9.8 | 15.8 / 17.4 |
| C9-hdepth-tree16-pfifo | Y (upstream) | 0.3 | 0.7 | 25.4 | -2.2 (27.6 / 26.0) | 6.0 / 6.4 | 9.5 / 9.8 | 14.7 / 15.8 |
| C9-hdepth-tree16-pfifo | root (root) | 0.3 | 0.7 | 25.4 | -1.9 (27.3 / 26.0) | 10.6 / 11.1 | 14.6 / 15.1 | 21.8 / 25.7 |

### Staggered phases (M6), noroot (M7), the default point (C2 pfifo) and s 0.10 / 0.65 (C3a)

| cell | egress (level) | s | U | 0.121 s U ms | minus keyframe pacing spread ms (spread) | peak p50 r1 / r2 | p90 r1 / r2 | max r1 / r2 |
|---|---|---|---|---|---|---|---|---|
| C2-sburst-s030u070-pfifo | main (leaf / single) | 0.3 | 0.7 | 25.4 | -6.2 (31.6 / 31.0) | 8.5 / 7.9 | 12.1 / 12.1 | 18.2 / 19.1 |
| C3a-sburst-s010u070-codel | main (leaf / single) | 0.1 | 0.7 | 8.5 | -21.4 (29.9 / 29.0) | 1.8 / 1.8 | 2.7 / 2.7 | 4.0 / 3.7 |
| C3a-sburst-s010u070-pfifo | main (leaf / single) | 0.1 | 0.7 | 8.5 | -21.3 (29.8 / 30.3) | 1.6 / 1.5 | 2.3 / 2.3 | 3.1 / 3.0 |
| C3a-sburst-s065u070-codel | main (leaf / single) | 0.65 | 0.7 | 55.1 | 14.8 (40.2 / 39.8) | 24.4 / 22.9 | 32.9 / 32.9 | 41.5 / 50.0 |
| C3a-sburst-s065u070-pfifo | main (leaf / single) | 0.65 | 0.7 | 55.1 | 17.2 (37.8 / 40.1) | 23.9 / 23.6 | 33.7 / 33.4 | 42.0 / 42.4 |
| M6-calm-stag-pfifo | main (leaf / single) | 0.3 | 0.7 | 25.4 | 21.6 (3.8 / 3.2) | 3.7 / 3.8 | 4.9 / 4.9 | 18.9 / 19.6 |
| M6-sburst-stag-pfifo | main (leaf / single) | 0.3 | 0.7 | 25.4 | -3.7 (29.1 / 28.6) | 1.9 / 1.8 | 2.6 / 2.5 | 3.5 / 3.4 |
| M7-hhier-noroot-pfifo | a (leaf / single) | 0.3 | 0.7 | 25.4 | -3.1 (28.5 / 28.0) | 9.2 / 9.0 | 12.9 / 12.8 | 18.9 / 18.9 |
| M7-hhier-noroot-pfifo | b (leaf / single) | 0.3 | 0.7 | 25.4 | -4.4 (29.9 / 29.3) | 8.9 / 8.7 | 13.2 / 13.2 | 16.7 / 18.1 |

## ECG events (v2-owd onsets) with an upstream / root egress congested (gt1 rule: a GT1 episode of the egress overlaps [t0 - 1 s, t0 + 2 s])

| cell | s | egress | share of ECG events r1 / r2 | ECG events r1 / r2 | leaf egresses, share r1 / r2 |
|---|---|---|---|---|---|
| C10-hindep-s030-codel | 0.3 | r1->r2 | 0.517 / 0.5 | 60 / 66 | r2->switch-a 0.417, r2->switch-b 0.583 / r2->switch-a 0.47, r2->switch-b 0.545 |
| C10-hindep-s030-fq_codel | 0.3 | r1->r2 | 0.585 / 0.551 | 118 / 107 | r2->switch-a 0.432, r2->switch-b 0.619 / r2->switch-a 0.458, r2->switch-b 0.579 |
| C10-hindep-s030-pfifo | 0.3 | r1->r2 | 0.5 / 0.53 | 64 / 66 | r2->switch-a 0.422, r2->switch-b 0.578 / r2->switch-a 0.379, r2->switch-b 0.545 |
| C12-amixed-access-codel | 0.3 | router->switch | 0.5 / 0.478 | 24 / 23 | router->switch 0.5 / router->switch 0.478 |
| C12-amixed-access-fq_codel | 0.3 | router->switch | 0.594 / 0.6 | 32 / 30 | router->switch 0.594 / router->switch 0.6 |
| C12-amixed-access-pfifo | 0.3 | router->switch | 0.455 / 0.455 | 22 / 22 | router->switch 0.455 / router->switch 0.455 |
| C12-amixed-access-pie | 0.3 | router->switch | 0.455 / 0.478 | 22 / 23 | router->switch 0.455 / router->switch 0.478 |
| C13-llong-s030-codel | 0.3 | r1->r2 | 0.308 / 0.333 | 13 / 12 | r2->switch-a 0.308, r2->switch-b 0.385 / r2->switch-a 0.333, r2->switch-b 0.333 |
| C13-llong-s030-pfifo | 0.3 | r1->r2 | 0.286 / 0.333 | 14 / 12 | r2->switch-a 0.286, r2->switch-b 0.429 / r2->switch-a 0.333, r2->switch-b 0.333 |
| C7-hhier-s030-codel | 0.3 | r1->r2 | 0.247 / 0.25 | 73 / 68 | r2->switch-a 0.658, r2->switch-b 0.575 / r2->switch-a 0.691, r2->switch-b 0.588 |
| C7-hhier-s030-fq_codel | 0.3 | r1->r2 | 0.291 / 0.295 | 134 / 139 | r2->switch-a 0.679, r2->switch-b 0.522 / r2->switch-a 0.698, r2->switch-b 0.59 |
| C7-hhier-s030-pfifo | 0.3 | r1->r2 | 0.254 / 0.257 | 71 / 70 | r2->switch-a 0.704, r2->switch-b 0.606 / r2->switch-a 0.714, r2->switch-b 0.6 |
| C7-hhier-s030-pie | 0.3 | r1->r2 | 0.227 / 0.246 | 75 / 69 | r2->switch-a 0.68, r2->switch-b 0.56 / r2->switch-a 0.71, r2->switch-b 0.58 |
| C8-hhier-s065-pfifo | 0.65 | r1->r2 | 0.429 / 0.373 | 84 / 83 | r2->switch-a 0.798, r2->switch-b 0.667 / r2->switch-a 0.735, r2->switch-b 0.614 |
| C9-hdepth-tree16-codel | 0.3 | rr->r0 | 0.176 / 0.13 | 51 / 54 | r1->switch-a 0.235, r1->switch-b 0.118, r2->switch-c 0.235, r2->switch-d 0.118 / r1->switch-a 0.241, r1->switch-b 0.13, r2->switch-c 0.241, r2->switch-d 0.111 |
| C9-hdepth-tree16-codel | 0.3 | r0->r1 | 0.118 / 0.13 | 51 / 54 | r1->switch-a 0.235, r1->switch-b 0.118, r2->switch-c 0.235, r2->switch-d 0.118 / r1->switch-a 0.241, r1->switch-b 0.13, r2->switch-c 0.241, r2->switch-d 0.111 |
| C9-hdepth-tree16-codel | 0.3 | r0->r2 | 0.118 / 0.111 | 51 / 54 | r1->switch-a 0.235, r1->switch-b 0.118, r2->switch-c 0.235, r2->switch-d 0.118 / r1->switch-a 0.241, r1->switch-b 0.13, r2->switch-c 0.241, r2->switch-d 0.111 |
| C9-hdepth-tree16-fq_codel | 0.3 | rr->r0 | 0.149 / 0.157 | 101 / 102 | r1->switch-a 0.287, r1->switch-b 0.069, r2->switch-c 0.277, r2->switch-d 0.129 / r1->switch-a 0.225, r1->switch-b 0.098, r2->switch-c 0.216, r2->switch-d 0.118 |
| C9-hdepth-tree16-fq_codel | 0.3 | r0->r1 | 0.119 / 0.137 | 101 / 102 | r1->switch-a 0.287, r1->switch-b 0.069, r2->switch-c 0.277, r2->switch-d 0.129 / r1->switch-a 0.225, r1->switch-b 0.098, r2->switch-c 0.216, r2->switch-d 0.118 |
| C9-hdepth-tree16-fq_codel | 0.3 | r0->r2 | 0.139 / 0.137 | 101 / 102 | r1->switch-a 0.287, r1->switch-b 0.069, r2->switch-c 0.277, r2->switch-d 0.129 / r1->switch-a 0.225, r1->switch-b 0.098, r2->switch-c 0.216, r2->switch-d 0.118 |
| C9-hdepth-tree16-pfifo | 0.3 | rr->r0 | 0.158 / 0.132 | 57 / 53 | r1->switch-a 0.298, r1->switch-b 0.105, r2->switch-c 0.281, r2->switch-d 0.105 / r1->switch-a 0.226, r1->switch-b 0.113, r2->switch-c 0.226, r2->switch-d 0.132 |
| C9-hdepth-tree16-pfifo | 0.3 | r0->r1 | 0.123 / 0.132 | 57 / 53 | r1->switch-a 0.298, r1->switch-b 0.105, r2->switch-c 0.281, r2->switch-d 0.105 / r1->switch-a 0.226, r1->switch-b 0.113, r2->switch-c 0.226, r2->switch-d 0.132 |
| C9-hdepth-tree16-pfifo | 0.3 | r0->r2 | 0.105 / 0.151 | 57 / 53 | r1->switch-a 0.298, r1->switch-b 0.105, r2->switch-c 0.281, r2->switch-d 0.105 / r1->switch-a 0.226, r1->switch-b 0.113, r2->switch-c 0.226, r2->switch-d 0.132 |
| M8-hhier-mixab-mixab | 0.3 | r1->r2 | 0.234 / 0.205 | 94 / 88 | r2->switch-a 0.66, r2->switch-b 0.649 / r2->switch-a 0.739, r2->switch-b 0.648 |
