# Part 0: campaign validity

## 0.1 Gate (9 runs)

Verdict: **PASS** (gate-report.md). Numbers per gate run:

| run | load / U | share / s | ECN marks | oversize skb | 4: lost, unmatched (targets), gaps within max(10 %, 15 us) min, 20 ms within 5 % min, CPU idle min | 5: non-video - planned (max abs) | 6: 1 / 30 Hz peak / median (max) |
|---|---|---|---|---|---|---|---|
| v3-G1-calm-legacy-pfifo-r1 | main 0.669 / 0.65 | 1.008 / 1.0 | 0 | 0 | 0, 0, 1.000, 1.000, 0.9362 | - | - |
| v3-G1-calm-s030u070-pfifo-r1 | main 0.706 / 0.7 | 0.308 / 0.3 | 0 | 0 | 0, 0, 1.000, 1.000, 0.9427 | - | 2.6 |
| v3-G2-calm-access-pfifo-r1 | main 0.706 / 0.7 | 0.308 / 0.3 | 0 | 0 | 0, 0, 0.999, 1.000, 0.8704 | - | 2.6 |
| v3-G2-calm-rev-pfifo-r1 | main 0.706 / 0.7 | 0.308 / 0.3 | 0 | 0 | 0, 0, 1.000, 1.000, 0.9045 | - | 2.6 |
| v3-G2-calm-split4-pfifo-r1 | up 0.706 / 0.7, a 0.708 / 0.7, b 0.707 / 0.7 | 0.308 / 0.3, 0.307 / 0.3, 0.308 / 0.3 | 0 | 0 | 0, 0, 0.999, 1.000, 0.8816 | - | 4.1 |
| v3-G2-calm-tree16-pfifo-r1 | root 0.708 / 0.7, X 0.711 / 0.7, Y 0.71 / 0.7, A 0.71 / 0.7, B 0.709 / 0.7, C 0.712 / 0.7, D 0.709 / 0.7 | 0.309 / 0.3, 0.308 / 0.3, 0.309 / 0.3, 0.309 / 0.3, 0.309 / 0.3, 0.308 / 0.3, 0.309 / 0.3 | 0 | 0 | 0, 2, 0.998, 1.000, 0.7869 | - | 5.4 |
| v3-G2-calm-uneven-pfifo-r1 | A 0.705 / 0.7, B 0.709 / 0.7, C 0.707 / 0.7 | 0.307 / 0.3, 0.307 / 0.3, 0.308 / 0.3 | 0 | 0 | 0, 0, 0.999, 1.000, 0.8967 | - | 5.1 |
| v3-G3-sburst-s030u070-fq_codel-r1 | main 0.713 / 0.7 | 0.316 / 0.3 | 0 | 0 | 0, 0, 1.000, 1.000, 0.9252 | 0.014 | 1.6 |
| v3-G3-sburst-s030u070-pfifo-r1 | main 0.71 / 0.7 | 0.312 / 0.3 | 0 | 0 | 0, 0, 1.000, 1.000, 0.938 | 0.014 | 1.6 |

## 0.2 Runs and time

- planned 203 runs; run folders 203; finished (events.csv `end`) 203; manifest: {'done': 203}; failed 0; extra run starts in run.log (retries) 0.
- dropped to fit the budget: none; planned 19.5 h emulated.
- emulated time (sum of the runs' scenario durations): 19.50 h.
- wall clock: started 2026-11-14T18:18:13, finished 2026-11-15T16:24:37 (includes the stop after the first gate failure on check 5 until the resume).
- GT-Q invalid by the health file (`gt_q_invalid`): 2 runs: ['v3-C13-llong-s030-pfifo-r1', 'v3-M8-hhier-mixab-mixab-r1'].

## 0.3 Calm load and video share per core run (tolerance +-0.03)

- core + gate bottleneck egresses: 255; load - U: median +0.010, min -0.010, max +0.028; share - s: median +0.009, min -0.008, max +0.016.
- off target: none.
- microbenchmarks off target (kept, flagged): ['v3-M11-sburst-bw4x1-pfifo-r1: main load 0.73 share 0.664', 'v3-M3-sburst-bgbursty-codel-r1: main load 0.651 share 0.338', 'v3-M3-sburst-bgbursty-pfifo-r1: main load 0.65 share 0.338'].

Stimulus intensity: background + stimulus arriving at the target vs planned U(1 - s) + (u - U) (surges; v3-stimuli.csv):

| block | surge windows | measured - planned: median / min / max | outside +-0.05 |
|---|---|---|---|
| C2 | 216 | -0.001 / -0.009 / +0.014 | 0 |
| C3a | 144 | -0.000 / -0.019 / +0.025 | 0 |
| C7 | 600 | -0.001 / -0.017 / +0.024 | 0 |
| C8 | 150 | -0.000 / -0.027 / +0.031 | 0 |
| C9 | 324 | -0.001 / -0.030 / +0.034 | 0 |
| C10 | 423 | +0.000 / -0.020 / +0.016 | 0 |
| C11 | 308 | +0.001 / -0.035 / +0.025 | 0 |
| C12 | 72 | -0.004 / -0.015 / +0.012 | 0 |
| C13 | 48 | -0.000 / -0.007 / +0.007 | 0 |
| C14 | 36 | +0.002 / -0.012 / +0.021 | 0 |
| G3 | 36 | -0.002 / -0.009 / +0.014 | 0 |
| M1 | 72 | -0.001 / -0.009 / +0.014 | 0 |
| M3 | 144 | -0.060 / -0.205 / +0.130 | 90 |
| M4 | 108 | -0.001 / -0.009 / +0.014 | 0 |
| M5 | 144 | -0.001 / -0.009 / +0.014 | 0 |
| M6 | 36 | -0.001 / -0.009 / +0.014 | 0 |
| M7 | 108 | +0.001 / -0.032 / +0.022 | 0 |
| M8 | 150 | -0.001 / -0.017 / +0.024 | 0 |
| M9 | 64 | -0.005 / -0.065 / +0.040 | 4 |
| M10 | 72 | -0.001 / -0.009 / +0.014 | 0 |
| M11 | 108 | -0.001 / -0.058 / +0.029 | 1 |
| M12 | 72 | -0.001 / -0.009 / +0.014 | 0 |
| M13 | 72 | -0.001 / -0.009 / +0.014 | 0 |
| M14 | 18 | +0.001 / -0.018 / +0.009 | 0 |

## 0.4 Worst cases over all 203 runs

- ECN marks: 0 on every egress of every run; AQM leaves configured with `ecn`: 0.
- skb larger than the MTU at a traced egress: 0; offloads not off: 0.
- CPU idle, worst second: 0.694 (v3-C9-hdepth-tree16-fq_codel-r1).
- inter-dequeue gaps within max(10 %, 15 us), worst target egress: 0.7792 (v3-C12-amixed-access-codel-r2 ra->sub-a); 20 ms windows within 5 %, worst: 0.0012 (v3-C12-amixed-access-codel-r2 ra->sub-a).
- unmatched packets, worst target egress: 2 (v3-M6-sburst-stag-pfifo-r2 router->switch); bpftrace lost events max 0.

Runs with a check flagged (kept): 4_health: 12 (v3-C12-amixed-access-codel-r1, v3-C12-amixed-access-codel-r2, v3-C12-amixed-access-fq_codel-r1, v3-C12-amixed-access-fq_codel-r2, v3-C12-amixed-access-pfifo-r1, v3-C12-amixed-access-pfifo-r2, v3-C12-amixed-access-pie-r1, v3-C12-amixed-access-pie-r2, v3-C13-llong-s030-pfifo-r1, v3-M11-sburst-bw4x1-pfifo-r1, v3-M11-sburst-bw4x1-pfifo-r2, v3-M8-hhier-mixab-mixab-r1); 1_load_share: 3 (v3-M11-sburst-bw4x1-pfifo-r1, v3-M3-sburst-bgbursty-codel-r1, v3-M3-sburst-bgbursty-pfifo-r1); 5_surge: 13 (v3-M11-sburst-bw4x1-pfifo-r2, v3-M3-sburst-bgbursty-codel-r1, v3-M3-sburst-bgbursty-codel-r2, v3-M3-sburst-bgbursty-pfifo-r1, v3-M3-sburst-bgbursty-pfifo-r2, v3-M3-sburst-bgmix-codel-r1, v3-M3-sburst-bgmix-codel-r2, v3-M3-sburst-bgmix-pfifo-r1, v3-M3-sburst-bgmix-pfifo-r2, v3-M9-sstress-s030u070-codel-r1, v3-M9-sstress-s030u070-codel-r2, v3-M9-sstress-s030u070-pfifo-r1, v3-M9-sstress-s030u070-pfifo-r2); 6_phase: 2 (v3-M3-sburst-bgmix-codel-r2, v3-M3-sburst-bgmix-pfifo-r2)

## 0.6 Isolation cells, pinned classes, optional features

- fq_codel / cake stimulus cells: 11; cells where no instrumented flow was ever constrained (no GT3 episode in either rep): none; fewest: C2-sburst-s030u070-cake 5, C6-sjoin-s030u070-fq_codel 13, C5-stcp-s030u070-fq_codel 85, C14-rrev-rev-fq_codel 128 GT3 episodes (both reps).
- background in pinned fq_codel classes: 97 traced fq_codel egresses checked; verifiable (skb hash in the trace) 74; packets in a pinned class: 941474 of 96727521 unpinned dequeues; unverifiable on 23 (no hash).
- Copa (M13): ran, cc_algo ['copa'] on 4 runs. I/P ratio (M10): ran, [2.0, 8.0] on 4 runs. S-JOIN (C6): ran, 6 runs (ASV key / P spread 5.85 / 1.16 ms).
