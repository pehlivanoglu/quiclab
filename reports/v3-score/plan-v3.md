# Suite v3 plan

git d9ddc27-dirty; host CPU governor: {'governors': ['powersave'], 'set_performance': False, 'note': 'not set by the suite (needs root: sudo cpupower frequency-set -g performance)'}

## Gate: 9 runs, 0.42 h emulated

| block | runs | hours |
|---|---|---|
| G1 | 2 | 0.07 |
| G2 | 5 | 0.17 |
| G3 | 2 | 0.19 |

## Core: 132 runs, 12.82 h emulated

| block | runs | hours |
|---|---|---|
| C1a | 36 | 1.20 |
| C1b | 6 | 0.20 |
| C2 | 12 | 1.13 |
| C3a | 8 | 0.75 |
| C3b | 2 | 0.19 |
| C4 | 8 | 0.48 |
| C5 | 8 | 0.75 |
| C6 | 6 | 0.38 |
| C7 | 8 | 2.12 |
| C8 | 2 | 0.53 |
| C9 | 6 | 1.48 |
| C10 | 6 | 1.00 |
| C11 | 4 | 0.67 |
| C12 | 8 | 0.89 |
| C13 | 4 | 0.44 |
| C14 | 4 | 0.35 |
| C15 | 4 | 0.24 |

## Micro: 62 runs, 6.27 h emulated

| block | runs | hours |
|---|---|---|
| M1 | 4 | 0.38 |
| M2 | 4 | 0.38 |
| M3 | 8 | 0.75 |
| M4 | 6 | 0.57 |
| M5 | 8 | 0.75 |
| M6 | 4 | 0.26 |
| M7 | 2 | 0.38 |
| M8 | 2 | 0.53 |
| M9 | 4 | 0.26 |
| M10 | 4 | 0.38 |
| M11 | 6 | 0.57 |
| M12 | 4 | 0.38 |
| M13 | 4 | 0.38 |
| M14 | 2 | 0.32 |

**Total: 203 runs, 19.50 h emulated** (budget 20.5 h). Dropped micro blocks: none. T-TREE16 s override: none.

## Per-egress sizing (every topology and point)

| topology | variant | s | U | egress | hop | D_e | C_e | BG_e | BG flows | pfifo limit pkts | keyframe peak ref ms | constraints |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | s030u070 | 0.3 | 0.7 | main | router->switch | 11.330 | 53.95 | 26.437 | 11 | 225 | 25.4 | ok |
| base | legacy | legacy | 0.65 | main | router->switch | 11.330 | 17.5 | 0 | 0 | 100 | - | sub-d 5.15 Mb/s = 29.4% of main 17.5 Mb/s (> 25%) |
| split4 | split4 | 0.3 | 0.7 | up | r1->r2 | 19.570 | 93.19 | 45.663 | 18 | 389 | 25.4 | ok |
| split4 | split4 | 0.3 | 0.7 | a | r2->switch-a | 9.785 | 46.6 | 22.832 | 9 | 195 | 25.4 | ok |
| split4 | split4 | 0.3 | 0.7 | b | r2->switch-b | 9.785 | 46.6 | 22.832 | 9 | 195 | 25.4 | ok |
| tree16 | tree16 | 0.3 | 0.7 | root | rr->r0 | 20.600 | 98.1 | 48.067 | 19 | 409 | 25.4 | ok |
| tree16 | tree16 | 0.3 | 0.7 | X | r0->r1 | 10.300 | 49.05 | 24.033 | 10 | 205 | 25.4 | ok |
| tree16 | tree16 | 0.3 | 0.7 | Y | r0->r2 | 10.300 | 49.05 | 24.033 | 10 | 205 | 25.4 | ok |
| tree16 | tree16 | 0.3 | 0.7 | A | r1->switch-a | 5.150 | 24.52 | 12.017 | 5 | 103 | 25.4 | ok |
| tree16 | tree16 | 0.3 | 0.7 | B | r1->switch-b | 5.150 | 24.52 | 12.017 | 5 | 103 | 25.4 | ok |
| tree16 | tree16 | 0.3 | 0.7 | C | r2->switch-c | 5.150 | 24.52 | 12.017 | 5 | 103 | 25.4 | ok |
| tree16 | tree16 | 0.3 | 0.7 | D | r2->switch-d | 5.150 | 24.52 | 12.017 | 5 | 103 | 25.4 | ok |
| uneven | uneven | 0.3 | 0.7 | up | r1->r2 | 35.020 | 1000 (unshaped) | 0 | 0 | - | - | ok |
| uneven | uneven | 0.3 | 0.7 | A | r2->switch-a | 7.725 | 36.79 | 18.025 | 7 | 154 | 25.4 | ok |
| uneven | uneven | 0.3 | 0.7 | B | r2->switch-b | 10.300 | 49.05 | 24.033 | 10 | 205 | 25.4 | ok |
| uneven | uneven | 0.3 | 0.7 | C | r2->switch-c | 16.995 | 80.93 | 39.655 | 16 | 338 | 25.4 | ok |
| access | access | 0.3 | 0.7 | main | router->switch | 11.330 | 53.95 | 26.437 | 11 | 225 | 25.4 | ok |
| rev | rev | 0.3 | 0.7 | main | r1->switch | 11.330 | 53.95 | 26.437 | 11 | 225 | 25.4 | ok |
| base | s030u070 | 0.3 | 0.7 | main | router->switch | 11.330 | 53.95 | 26.437 | 11 | 225 | 25.4 | ok |
| base | s030u050 | 0.3 | 0.5 | main | router->switch | 11.330 | 75.53 | 26.437 | 11 | 315 | 18.1 | ok |
| base | s030u085 | 0.3 | 0.85 | main | router->switch | 11.330 | 44.43 | 26.437 | 11 | 186 | 30.9 | ok |
| base | s065u050 | 0.65 | 0.5 | main | router->switch | 11.330 | 34.86 | 6.101 | 4 | 146 | 39.3 | ok |
| base | s065u070 | 0.65 | 0.7 | main | router->switch | 11.330 | 24.9 | 6.101 | 4 | 104 | 55.1 | ok |
| base | s065u085 | 0.65 | 0.85 | main | router->switch | 11.330 | 20.51 | 6.101 | 4 | 86 | 66.9 | sub-d 5.15 Mb/s = 25.1% of main 20.51 Mb/s (> 25%) |
| base | s010u070 | 0.1 | 0.7 | main | router->switch | 5.150 | 73.57 | 46.35 | 19 | 307 | 8.5 | ok |
| base | s010u085 | 0.1 | 0.85 | main | router->switch | 5.150 | 60.59 | 46.35 | 19 | 253 | 10.3 | ok |
| split4 | s030 | 0.3 | 0.7 | up | r1->r2 | 19.570 | 93.19 | 45.663 | 18 | 389 | 25.4 | ok |
| split4 | s030 | 0.3 | 0.7 | a | r2->switch-a | 9.785 | 46.6 | 22.832 | 9 | 195 | 25.4 | ok |
| split4 | s030 | 0.3 | 0.7 | b | r2->switch-b | 9.785 | 46.6 | 22.832 | 9 | 195 | 25.4 | ok |
| split4 | s065 | 0.65 | 0.7 | up | r1->r2 | 19.570 | 43.01 | 10.538 | 4 | 180 | 55.1 | ok |
| split4 | s065 | 0.65 | 0.7 | a | r2->switch-a | 9.785 | 21.51 | 5.269 | 4 | 90 | 55.1 | ok |
| split4 | s065 | 0.65 | 0.7 | b | r2->switch-b | 9.785 | 21.51 | 5.269 | 4 | 90 | 55.1 | ok |
| base | q100 | 0.3 | 0.7 | main | router->switch | 11.330 | 53.95 | 26.437 | 11 | 450 | 25.4 | ok |
| base | q300 | 0.3 | 0.7 | main | router->switch | 11.330 | 53.95 | 26.437 | 11 | 1349 | 25.4 | ok |
| base | capdrop | 0.3 | 0.7 | main | router->switch | 11.330 | 53.95 | 26.437 | 11 | 225 | 25.4 | ok |
| base | bgbursty | 0.3 | 0.7 | main | router->switch | 11.330 | 53.95 | 26.437 | 11 | 225 | 25.4 | ok |
| base | bgmix | 0.3 | 0.7 | main | router->switch | 11.330 | 53.95 | 26.437 | 11 | 225 | 25.4 | ok |
| base | rttx05 | 0.3 | 0.7 | main | router->switch | 11.330 | 53.95 | 26.437 | 11 | 113 | 25.4 | ok |
| base | rttx4 | 0.3 | 0.7 | main | router->switch | 11.330 | 53.95 | 26.437 | 11 | 900 | 25.4 | ok |
| base | rttwide | 0.3 | 0.7 | main | router->switch | 11.330 | 53.95 | 26.437 | 11 | 450 | 25.4 | ok |
| base | fps15 | 0.3 | 0.7 | main | router->switch | 11.330 | 53.95 | 26.437 | 11 | 225 | 25.4 | ok |
| base | fps60 | 0.3 | 0.7 | main | router->switch | 11.330 | 53.95 | 26.437 | 11 | 225 | 25.4 | ok |
| base | stag | 0.3 | 0.7 | main | router->switch | 11.330 | 53.95 | 26.437 | 11 | 225 | 25.4 | ok |
| split4 | noroot | 0.3 | 0.7 | up | r1->r2 | 19.570 | 1000 (unshaped) | 0 | 0 | - | - | ok |
| split4 | noroot | 0.3 | 0.7 | a | r2->switch-a | 9.785 | 46.6 | 22.832 | 9 | 195 | 25.4 | ok |
| split4 | noroot | 0.3 | 0.7 | b | r2->switch-b | 9.785 | 46.6 | 22.832 | 9 | 195 | 25.4 | ok |
| split4 | mixab | 0.3 | 0.7 | up | r1->r2 | 19.570 | 93.19 | 45.663 | 18 | 389 | 25.4 | ok |
| split4 | mixab | 0.3 | 0.7 | a | r2->switch-a | 9.785 | 46.6 | 22.832 | 9 | 195 | 25.4 | ok |
| split4 | mixab | 0.3 | 0.7 | b | r2->switch-b | 9.785 | 46.6 | 22.832 | 9 | 195 | 25.4 | ok |
| base | ip2 | 0.3 | 0.7 | main | router->switch | 11.330 | 53.95 | 26.437 | 11 | 225 | 25.4 | ok |
| base | ip8 | 0.3 | 0.7 | main | router->switch | 11.330 | 53.95 | 26.437 | 11 | 225 | 25.4 | ok |
| base | bw4x1 | 0.65 | 0.7 | main | router->switch | 4.120 | 9.05 | 2.218 | 4 | 38 | 55.1 | ok |
| base | bw4x8 | 0.65 | 0.7 | main | router->switch | 32.960 | 72.44 | 17.748 | 7 | 302 | 55.1 | ok |
| base | bw4x12 | 0.65 | 0.7 | main | router->switch | 21.115 | 46.41 | 11.37 | 5 | 194 | 55.1 | sub-d 12.36 Mb/s = 26.6% of main 46.41 Mb/s (> 25%) |
| base | jitfwd | 0.3 | 0.7 | main | router->switch | 11.330 | 53.95 | 26.437 | 11 | 225 | 25.4 | ok |
| base | jitrev | 0.3 | 0.7 | main | router->switch | 11.330 | 53.95 | 26.437 | 11 | 225 | 25.4 | ok |
| base | copa | 0.3 | 0.7 | main | router->switch | 11.330 | 53.95 | 26.437 | 11 | 225 | 25.4 | ok |

## Constraint flags

- kept (listed by the spec; user decision 2026-11-14): legacy: sub-d 5.15 Mb/s = 29 % of 17.5 Mb/s (> 25 %)
- kept (listed by the spec; user decision 2026-11-14): s065u085: sub-d 5.15 Mb/s = 25.1 % of 20.5 Mb/s (> 25 %)
- kept (listed by the spec; user decision 2026-11-14): bw4x12: 12000 kb/s client = 27 % of 46.4 Mb/s (> 25 %)

## Runs

| # | run | duration s |
|---|---|---|
| 1 | v3-G1-calm-s030u070-pfifo-r1 | 120 |
| 2 | v3-G1-calm-legacy-pfifo-r1 | 120 |
| 3 | v3-G2-calm-split4-pfifo-r1 | 120 |
| 4 | v3-G2-calm-tree16-pfifo-r1 | 120 |
| 5 | v3-G2-calm-uneven-pfifo-r1 | 120 |
| 6 | v3-G2-calm-access-pfifo-r1 | 120 |
| 7 | v3-G2-calm-rev-pfifo-r1 | 120 |
| 8 | v3-G3-sburst-s030u070-pfifo-r1 | 335 |
| 9 | v3-G3-sburst-s030u070-fq_codel-r1 | 335 |
| 10 | v3-C1a-calm-s030u070-pfifo-r1 | 120 |
| 11 | v3-C1a-calm-s030u070-codel-r1 | 120 |
| 12 | v3-C1a-calm-s030u050-pfifo-r1 | 120 |
| 13 | v3-C1a-calm-s030u050-codel-r1 | 120 |
| 14 | v3-C1a-calm-s030u085-pfifo-r1 | 120 |
| 15 | v3-C1a-calm-s030u085-codel-r1 | 120 |
| 16 | v3-C1a-calm-s065u050-pfifo-r1 | 120 |
| 17 | v3-C1a-calm-s065u050-codel-r1 | 120 |
| 18 | v3-C1a-calm-s065u070-pfifo-r1 | 120 |
| 19 | v3-C1a-calm-s065u070-codel-r1 | 120 |
| 20 | v3-C1a-calm-s065u085-pfifo-r1 | 120 |
| 21 | v3-C1a-calm-s065u085-codel-r1 | 120 |
| 22 | v3-C1a-calm-s010u070-pfifo-r1 | 120 |
| 23 | v3-C1a-calm-s010u070-codel-r1 | 120 |
| 24 | v3-C1a-calm-s010u085-pfifo-r1 | 120 |
| 25 | v3-C1a-calm-s010u085-codel-r1 | 120 |
| 26 | v3-C1a-calm-legacy-pfifo-r1 | 120 |
| 27 | v3-C1a-calm-legacy-codel-r1 | 120 |
| 28 | v3-C1b-calm-split4-pfifo-r1 | 120 |
| 29 | v3-C1b-calm-tree16-pfifo-r1 | 120 |
| 30 | v3-C1b-calm-uneven-pfifo-r1 | 120 |
| 31 | v3-C2-sburst-s030u070-pfifo-r1 | 335 |
| 32 | v3-C2-sburst-s030u070-codel-r1 | 335 |
| 33 | v3-C2-sburst-s030u070-pie-r1 | 335 |
| 34 | v3-C2-sburst-s030u070-fq_codel-r1 | 335 |
| 35 | v3-C2-sburst-s030u070-red-r1 | 335 |
| 36 | v3-C2-sburst-s030u070-cake-r1 | 335 |
| 37 | v3-C3a-sburst-s010u070-pfifo-r1 | 335 |
| 38 | v3-C3a-sburst-s010u070-codel-r1 | 335 |
| 39 | v3-C3a-sburst-s065u070-pfifo-r1 | 335 |
| 40 | v3-C3a-sburst-s065u070-codel-r1 | 335 |
| 41 | v3-C3b-sburst-legacy-pfifo-r1 | 335 |
| 42 | v3-C4-sramp-s030u070-pfifo-r1 | 223 |
| 43 | v3-C4-sramp-s030u070-codel-r1 | 223 |
| 44 | v3-C4-sramp-s030u070-pie-r1 | 223 |
| 45 | v3-C4-sramp-s030u070-fq_codel-r1 | 223 |
| 46 | v3-C5-stcp-s030u070-pfifo-r1 | 342 |
| 47 | v3-C5-stcp-s030u070-codel-r1 | 342 |
| 48 | v3-C5-stcp-s030u070-pie-r1 | 342 |
| 49 | v3-C5-stcp-s030u070-fq_codel-r1 | 342 |
| 50 | v3-C6-sjoin-s030u070-pfifo-r1 | 226 |
| 51 | v3-C6-sjoin-s030u070-codel-r1 | 226 |
| 52 | v3-C6-sjoin-s030u070-fq_codel-r1 | 226 |
| 53 | v3-C7-hhier-s030-pfifo-r1 | 969 |
| 54 | v3-C7-hhier-s030-codel-r1 | 969 |
| 55 | v3-C7-hhier-s030-pie-r1 | 969 |
| 56 | v3-C7-hhier-s030-fq_codel-r1 | 969 |
| 57 | v3-C8-hhier-s065-pfifo-r1 | 969 |
| 58 | v3-C9-hdepth-tree16-pfifo-r1 | 883 |
| 59 | v3-C9-hdepth-tree16-codel-r1 | 883 |
| 60 | v3-C9-hdepth-tree16-fq_codel-r1 | 883 |
| 61 | v3-C10-hindep-s030-pfifo-r1 | 600 |
| 62 | v3-C10-hindep-s030-codel-r1 | 600 |
| 63 | v3-C10-hindep-s030-fq_codel-r1 | 600 |
| 64 | v3-C11-huneven-uneven-pfifo-r1 | 600 |
| 65 | v3-C11-huneven-uneven-codel-r1 | 600 |
| 66 | v3-C12-amixed-access-pfifo-r1 | 401 |
| 67 | v3-C12-amixed-access-codel-r1 | 401 |
| 68 | v3-C12-amixed-access-pie-r1 | 401 |
| 69 | v3-C12-amixed-access-fq_codel-r1 | 401 |
| 70 | v3-C13-llong-s030-pfifo-r1 | 397 |
| 71 | v3-C13-llong-s030-codel-r1 | 397 |
| 72 | v3-C14-rrev-rev-pfifo-r1 | 311 |
| 73 | v3-C14-rrev-rev-fq_codel-r1 | 311 |
| 74 | v3-C15-nloss-s030u070-pfifo-r1 | 216 |
| 75 | v3-C15-nloss-s030u070-codel-r1 | 216 |
| 76 | v3-C1a-calm-s030u070-pfifo-r2 | 120 |
| 77 | v3-C1a-calm-s030u070-codel-r2 | 120 |
| 78 | v3-C1a-calm-s030u050-pfifo-r2 | 120 |
| 79 | v3-C1a-calm-s030u050-codel-r2 | 120 |
| 80 | v3-C1a-calm-s030u085-pfifo-r2 | 120 |
| 81 | v3-C1a-calm-s030u085-codel-r2 | 120 |
| 82 | v3-C1a-calm-s065u050-pfifo-r2 | 120 |
| 83 | v3-C1a-calm-s065u050-codel-r2 | 120 |
| 84 | v3-C1a-calm-s065u070-pfifo-r2 | 120 |
| 85 | v3-C1a-calm-s065u070-codel-r2 | 120 |
| 86 | v3-C1a-calm-s065u085-pfifo-r2 | 120 |
| 87 | v3-C1a-calm-s065u085-codel-r2 | 120 |
| 88 | v3-C1a-calm-s010u070-pfifo-r2 | 120 |
| 89 | v3-C1a-calm-s010u070-codel-r2 | 120 |
| 90 | v3-C1a-calm-s010u085-pfifo-r2 | 120 |
| 91 | v3-C1a-calm-s010u085-codel-r2 | 120 |
| 92 | v3-C1a-calm-legacy-pfifo-r2 | 120 |
| 93 | v3-C1a-calm-legacy-codel-r2 | 120 |
| 94 | v3-C1b-calm-split4-pfifo-r2 | 120 |
| 95 | v3-C1b-calm-tree16-pfifo-r2 | 120 |
| 96 | v3-C1b-calm-uneven-pfifo-r2 | 120 |
| 97 | v3-C2-sburst-s030u070-pfifo-r2 | 344 |
| 98 | v3-C2-sburst-s030u070-codel-r2 | 344 |
| 99 | v3-C2-sburst-s030u070-pie-r2 | 344 |
| 100 | v3-C2-sburst-s030u070-fq_codel-r2 | 344 |
| 101 | v3-C2-sburst-s030u070-red-r2 | 344 |
| 102 | v3-C2-sburst-s030u070-cake-r2 | 344 |
| 103 | v3-C3a-sburst-s010u070-pfifo-r2 | 344 |
| 104 | v3-C3a-sburst-s010u070-codel-r2 | 344 |
| 105 | v3-C3a-sburst-s065u070-pfifo-r2 | 344 |
| 106 | v3-C3a-sburst-s065u070-codel-r2 | 344 |
| 107 | v3-C3b-sburst-legacy-pfifo-r2 | 344 |
| 108 | v3-C4-sramp-s030u070-pfifo-r2 | 211 |
| 109 | v3-C4-sramp-s030u070-codel-r2 | 211 |
| 110 | v3-C4-sramp-s030u070-pie-r2 | 211 |
| 111 | v3-C4-sramp-s030u070-fq_codel-r2 | 211 |
| 112 | v3-C5-stcp-s030u070-pfifo-r2 | 337 |
| 113 | v3-C5-stcp-s030u070-codel-r2 | 337 |
| 114 | v3-C5-stcp-s030u070-pie-r2 | 337 |
| 115 | v3-C5-stcp-s030u070-fq_codel-r2 | 337 |
| 116 | v3-C6-sjoin-s030u070-pfifo-r2 | 224 |
| 117 | v3-C6-sjoin-s030u070-codel-r2 | 224 |
| 118 | v3-C6-sjoin-s030u070-fq_codel-r2 | 224 |
| 119 | v3-C7-hhier-s030-pfifo-r2 | 942 |
| 120 | v3-C7-hhier-s030-codel-r2 | 942 |
| 121 | v3-C7-hhier-s030-pie-r2 | 942 |
| 122 | v3-C7-hhier-s030-fq_codel-r2 | 942 |
| 123 | v3-C8-hhier-s065-pfifo-r2 | 942 |
| 124 | v3-C9-hdepth-tree16-pfifo-r2 | 893 |
| 125 | v3-C9-hdepth-tree16-codel-r2 | 893 |
| 126 | v3-C9-hdepth-tree16-fq_codel-r2 | 893 |
| 127 | v3-C10-hindep-s030-pfifo-r2 | 600 |
| 128 | v3-C10-hindep-s030-codel-r2 | 600 |
| 129 | v3-C10-hindep-s030-fq_codel-r2 | 600 |
| 130 | v3-C11-huneven-uneven-pfifo-r2 | 600 |
| 131 | v3-C11-huneven-uneven-codel-r2 | 600 |
| 132 | v3-C12-amixed-access-pfifo-r2 | 402 |
| 133 | v3-C12-amixed-access-codel-r2 | 402 |
| 134 | v3-C12-amixed-access-pie-r2 | 402 |
| 135 | v3-C12-amixed-access-fq_codel-r2 | 402 |
| 136 | v3-C13-llong-s030-pfifo-r2 | 401 |
| 137 | v3-C13-llong-s030-codel-r2 | 401 |
| 138 | v3-C14-rrev-rev-pfifo-r2 | 326 |
| 139 | v3-C14-rrev-rev-fq_codel-r2 | 326 |
| 140 | v3-C15-nloss-s030u070-pfifo-r2 | 214 |
| 141 | v3-C15-nloss-s030u070-codel-r2 | 214 |
| 142 | v3-M1-sburst-q100-pfifo-r1 | 335 |
| 143 | v3-M1-sburst-q300-pfifo-r1 | 335 |
| 144 | v3-M2-sburst-capdrop-pfifo-r1 | 335 |
| 145 | v3-M2-sburst-capdrop-codel-r1 | 335 |
| 146 | v3-M3-sburst-bgbursty-pfifo-r1 | 335 |
| 147 | v3-M3-sburst-bgbursty-codel-r1 | 335 |
| 148 | v3-M3-sburst-bgmix-pfifo-r1 | 335 |
| 149 | v3-M3-sburst-bgmix-codel-r1 | 335 |
| 150 | v3-M4-sburst-rttx05-pfifo-r1 | 335 |
| 151 | v3-M4-sburst-rttx4-pfifo-r1 | 335 |
| 152 | v3-M4-sburst-rttwide-pfifo-r1 | 335 |
| 153 | v3-M5-sburst-fps15-pfifo-r1 | 335 |
| 154 | v3-M5-sburst-fps15-codel-r1 | 335 |
| 155 | v3-M5-sburst-fps60-pfifo-r1 | 335 |
| 156 | v3-M5-sburst-fps60-codel-r1 | 335 |
| 157 | v3-M6-sburst-stag-pfifo-r1 | 335 |
| 158 | v3-M6-calm-stag-pfifo-r1 | 120 |
| 159 | v3-M7-hhier-noroot-pfifo-r1 | 684 |
| 160 | v3-M8-hhier-mixab-mixab-r1 | 969 |
| 161 | v3-M9-sstress-s030u070-pfifo-r1 | 232 |
| 162 | v3-M9-sstress-s030u070-codel-r1 | 232 |
| 163 | v3-M10-sburst-ip2-pfifo-r1 | 335 |
| 164 | v3-M10-sburst-ip8-pfifo-r1 | 335 |
| 165 | v3-M11-sburst-bw4x1-pfifo-r1 | 335 |
| 166 | v3-M11-sburst-bw4x8-pfifo-r1 | 335 |
| 167 | v3-M11-sburst-bw4x12-pfifo-r1 | 335 |
| 168 | v3-M12-sburst-jitfwd-pfifo-r1 | 335 |
| 169 | v3-M12-sburst-jitrev-pfifo-r1 | 335 |
| 170 | v3-M13-sburst-copa-pfifo-r1 | 335 |
| 171 | v3-M13-sburst-copa-codel-r1 | 335 |
| 172 | v3-M14-ssparse-s030u070-pfifo-r1 | 565 |
| 173 | v3-M1-sburst-q100-pfifo-r2 | 344 |
| 174 | v3-M1-sburst-q300-pfifo-r2 | 344 |
| 175 | v3-M2-sburst-capdrop-pfifo-r2 | 344 |
| 176 | v3-M2-sburst-capdrop-codel-r2 | 344 |
| 177 | v3-M3-sburst-bgbursty-pfifo-r2 | 344 |
| 178 | v3-M3-sburst-bgbursty-codel-r2 | 344 |
| 179 | v3-M3-sburst-bgmix-pfifo-r2 | 344 |
| 180 | v3-M3-sburst-bgmix-codel-r2 | 344 |
| 181 | v3-M4-sburst-rttx05-pfifo-r2 | 344 |
| 182 | v3-M4-sburst-rttx4-pfifo-r2 | 344 |
| 183 | v3-M4-sburst-rttwide-pfifo-r2 | 344 |
| 184 | v3-M5-sburst-fps15-pfifo-r2 | 344 |
| 185 | v3-M5-sburst-fps15-codel-r2 | 344 |
| 186 | v3-M5-sburst-fps60-pfifo-r2 | 344 |
| 187 | v3-M5-sburst-fps60-codel-r2 | 344 |
| 188 | v3-M6-sburst-stag-pfifo-r2 | 344 |
| 189 | v3-M6-calm-stag-pfifo-r2 | 120 |
| 190 | v3-M7-hhier-noroot-pfifo-r2 | 671 |
| 191 | v3-M8-hhier-mixab-mixab-r2 | 942 |
| 192 | v3-M9-sstress-s030u070-pfifo-r2 | 244 |
| 193 | v3-M9-sstress-s030u070-codel-r2 | 244 |
| 194 | v3-M10-sburst-ip2-pfifo-r2 | 344 |
| 195 | v3-M10-sburst-ip8-pfifo-r2 | 344 |
| 196 | v3-M11-sburst-bw4x1-pfifo-r2 | 344 |
| 197 | v3-M11-sburst-bw4x8-pfifo-r2 | 344 |
| 198 | v3-M11-sburst-bw4x12-pfifo-r2 | 344 |
| 199 | v3-M12-sburst-jitfwd-pfifo-r2 | 344 |
| 200 | v3-M12-sburst-jitrev-pfifo-r2 | 344 |
| 201 | v3-M13-sburst-copa-pfifo-r2 | 344 |
| 202 | v3-M13-sburst-copa-codel-r2 | 344 |
| 203 | v3-M14-ssparse-s030u070-pfifo-r2 | 569 |
