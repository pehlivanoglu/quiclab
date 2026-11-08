# Shadow v2, Step 1: feature quality

100 r1 runs (2026-11-05_det-base, 2026-11-05_det-split, 2026-11-05_det-access); freeze set = 25 pfifo-r1 runs. Tick 33 ms, W_g 2 ticks, hold 2 ticks. git 7eb1419. Truth: git: fda8864-dirty.

## Verification (spec section 14)

1. Per-ACK dump: inflight_bytes, stream_buffer_bytes, newly_lost, sent_mono_us, bytes_acked_total, phase, app_limited, mask present; onSent = publishers/<pub>/<sub>-sent.csv (QUIC writes with bytes). OK.
2. Realtime-monotonic offset: det_eval.Run epoch_mono_ns / epoch_unix_ns from events.csv. OK.
3. rendition_bps: topology subscribers rate_kbps (x 1.03 wire). OK.
4. relay_saturated: 0 in all 11 461 661 ACK rows of the 200 runs. OK.

## Ambiguities and resolutions

- Step 1 is specified on pfifo-r1 but the weak-cell hypotheses need fq_codel / red cells: features are computed for every r1 run; calm statistics and floors below are from pfifo-r1 only.
- base: running minimum of the tick min RTT, no rebase (section 7 needs z-scores, Step 2); after a forward delay step F1 stays elevated, which is the delaystep hypothesis itself.
- d_k is frozen while GT3 labels the client CONGESTED (the detector's own score does not exist yet).
- n_k = sent bytes / 1200 (the sent log records writes, not packets); l_k = newly_lost over the tick's ACKs.
- calm tick = GT3 CLEAR, unmasked, has data, >= 1 s away from any GT3 episode of the flow, after warm-up.

## 1. Calm distribution per feature (pfifo-r1; F1, F2 in ms, F3 dimensionless, F4 in s)

| feature | rate Mb/s | calm ticks | median | MAD sigma | std | p1 | p99 | per-flow sigma median | min | max |
|---|---|---|---|---|---|---|---|---|---|---|
| F1 | 1 | 20967 | 2.308 | 2.408 | 6.590 | 0.096 | 37.531 | 2.352 | 0.470 | 5.736 |
| F1 | 2.5 | 93909 | 1.436 | 1.666 | 5.382 | 0.048 | 24.720 | 1.367 | 0.181 | 6.976 |
| F1 | 5 | 55484 | 2.862 | 2.126 | 5.555 | 0.058 | 27.155 | 1.984 | 0.989 | 6.136 |
| F2 | 1 | 20967 | -0.009 | 3.116 | 6.582 | -22.712 | 18.241 | 3.223 | 1.000 | 10.015 |
| F2 | 2.5 | 93890 | 0.000 | 1.312 | 4.725 | -16.923 | 13.241 | 1.760 | 0.251 | 9.386 |
| F2 | 5 | 55437 | 0.000 | 2.758 | 5.335 | -18.776 | 13.850 | 2.738 | 1.631 | 8.350 |
| F3 | 1 | 20967 | 0.000 | 0.421 | 1.122 | -2.835 | 4.451 | 0.442 | 0.075 | 0.537 |
| F3 | 2.5 | 93909 | 0.006 | 0.411 | 1.365 | -3.080 | 4.775 | 0.412 | 0.219 | 0.612 |
| F3 | 5 | 55484 | -0.023 | 0.416 | 1.345 | -1.909 | 4.432 | 0.409 | 0.300 | 1.026 |
| F4 | 1 | 20967 | 0.230 | 0.151 | 0.535 | -0.020 | 2.668 | 0.137 | 0.000 | 0.230 |
| F4 | 2.5 | 93909 | 0.459 | 0.234 | 1.148 | 0.070 | 3.875 | 0.184 | 0.110 | 0.378 |
| F4 | 5 | 55484 | 0.801 | 0.380 | 2.583 | 0.177 | 10.549 | 0.268 | 0.162 | 3.495 |

floor_i candidate = 10 % of the median per-flow MAD sigma (section 6): F1 0.1870, F2 0.2485, F3 0.0415, F4 0.0188

Calm loss p0 (pfifo-r1 pooled): 0.00074 (1400 lost / 1889752 sent); ticks with any loss: 0.45 %.

## 2. Autocorrelation of calm ticks (median over pfifo-r1 flows)

| feature | lag 1 (33 ms) | lag 2 (66 ms) | lag 3 (99 ms) | lag 6 (198 ms) | lag 15 (495 ms) | lag 30 (990 ms) |
|---|---|---|---|---|---|---|
| F1 | 0.46 | 0.17 | 0.05 | 0.02 | 0.08 | 0.30 |
| F2 | 0.26 | -0.37 | -0.19 | -0.02 | 0.04 | 0.22 |
| F3 | 0.40 | -0.35 | -0.15 | -0.00 | -0.02 | 0.70 |
| F4 | 0.58 | 0.23 | 0.09 | -0.00 | -0.09 | 0.58 |

## 3. Cross-correlation of calm ticks (pfifo-r1 pooled)

|  | F1 | F2 | F3 | F4 |
|---|---|---|---|---|
| F1 | 1.00 | 0.39 | -0.08 | -0.02 |
| F2 | 0.39 | 1.00 | -0.05 | 0.00 |
| F3 | -0.08 | -0.05 | 1.00 | 0.27 |
| F4 | -0.02 | 0.00 | 0.27 | 1.00 |

## 4. Keyframe-aligned response in calm periods (pfifo-r1; z in calm MAD units)

| feature | rate Mb/s | peak mean z | at (ms after send) | keyframes |
|---|---|---|---|---|
| F1 | 1 | 1.83 | 330 | 2025 |
| F2 | 1 | 1.25 | 330 | 2025 |
| F3 | 1 | 6.38 | 0 | 2025 |
| F4 | 1 | 9.44 | 0 | 1898 |
| F1 | 2.5 | 2.47 | 396 | 8461 |
| F2 | 2.5 | 1.44 | 396 | 8461 |
| F3 | 2.5 | 8.16 | 33 | 8461 |
| F4 | 2.5 | 8.60 | 33 | 8461 |
| F1 | 5 | 2.94 | 198 | 3892 |
| F2 | 5 | 1.70 | 198 | 3890 |
| F3 | 5 | 7.56 | 33 | 3892 |
| F4 | 5 | 5.84 | 66 | 3892 |

Plot: step1/keyframe-response.png. A peak above delta/2 = 1 means a lone keyframe already scores.

## 5. AUC, calm ticks vs the first 100 / 200 / 300 ms after a GT3 onset (GT3-positive clients)

| cell | GT3 episodes | F1 @100 | F2 @100 | F3 @100 | F4 @100 | l @100 | F1 @200 | F2 @200 | F3 @200 | F4 @200 | l @200 | F1 @300 | F2 @300 | F3 @300 | F4 @300 | l @300 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all fq_codel | 791 | 0.78 | 0.61 | 0.57 | 0.81 | 0.53 | 0.85 | 0.68 | 0.49 | 0.80 | 0.59 | 0.87 | 0.67 | 0.49 | 0.80 | 0.62 |
| all pfifo | 1390 | 0.74 | 0.64 | 0.56 | 0.57 | 0.50 | 0.84 | 0.75 | 0.56 | 0.62 | 0.52 | 0.89 | 0.76 | 0.56 | 0.66 | 0.55 |
| all pie | 1311 | 0.76 | 0.66 | 0.57 | 0.56 | 0.51 | 0.85 | 0.76 | 0.57 | 0.61 | 0.53 | 0.89 | 0.75 | 0.58 | 0.65 | 0.56 |
| all red | 1428 | 0.74 | 0.63 | 0.56 | 0.56 | 0.50 | 0.84 | 0.74 | 0.55 | 0.61 | 0.53 | 0.89 | 0.72 | 0.55 | 0.65 | 0.56 |
| fq_codel competition | 138 | 0.81 | 0.58 | 0.55 | 0.90 | 0.54 | 0.87 | 0.65 | 0.40 | 0.86 | 0.61 | 0.87 | 0.62 | 0.39 | 0.82 | 0.63 |
| burstcapshallow pfifo | 71 | 0.78 | 0.69 | 0.54 | 0.53 | 0.52 | 0.83 | 0.66 | 0.50 | 0.56 | 0.63 | 0.84 | 0.59 | 0.52 | 0.58 | 0.64 |
| tcpcubic red | 71 | 0.75 | 0.48 | 0.50 | 0.51 | 0.51 | 0.86 | 0.65 | 0.52 | 0.55 | 0.51 | 0.90 | 0.61 | 0.52 | 0.58 | 0.54 |
| burstlong pfifo | 72 | 0.79 | 0.65 | 0.55 | 0.74 | 0.50 | 0.88 | 0.78 | 0.56 | 0.78 | 0.51 | 0.92 | 0.80 | 0.56 | 0.80 | 0.53 |
| calm090 pfifo | 56 | 0.56 | 0.56 | 0.55 | 0.53 | 0.50 | 0.72 | 0.71 | 0.53 | 0.58 | 0.50 | 0.80 | 0.68 | 0.51 | 0.60 | 0.51 |
| burstcap pfifo 1 Mb/s | 20 | 0.86 | 0.82 | 0.60 | 0.61 | 0.50 | 0.93 | 0.87 | 0.65 | 0.72 | 0.50 | 0.95 | 0.82 | 0.64 | 0.76 | 0.52 |
| burstcap pfifo 2.5 Mb/s | 38 | 0.77 | 0.67 | 0.56 | 0.62 | 0.50 | 0.88 | 0.81 | 0.59 | 0.70 | 0.50 | 0.92 | 0.81 | 0.61 | 0.75 | 0.52 |
| burstcap pfifo 5 Mb/s | 19 | 0.68 | 0.56 | 0.50 | 0.57 | 0.50 | 0.80 | 0.72 | 0.51 | 0.61 | 0.50 | 0.87 | 0.77 | 0.50 | 0.64 | 0.51 |

0.5 = no separation; F4 and F1 are level features (expected to rise later), F2 / F3 growth, l = lost packets in the tick.

## 6. Hypotheses

### 6a. burstlong: share of ticks with z >= 1, first 0.5 s / after BBR adapted (3 s to end - 1 s)

| aqm | episodes >= 8 s | F1 | F2 | F3 | F4 |
|---|---|---|---|---|---|
| pfifo | 61 | 0.92 / 0.99 | 0.66 / 0.33 | 0.37 / 0.32 | 0.90 / 0.99 |
| red | 42 | 0.91 / 0.98 | 0.60 / 0.35 | 0.36 / 0.32 | 0.83 / 0.99 |
| pie | 41 | 0.90 / 0.78 | 0.59 / 0.32 | 0.29 / 0.23 | 0.73 / 0.83 |
| fq_codel | 19 | 0.86 / 0.92 | 0.49 / 0.43 | 0.39 / 0.41 | 0.84 / 1.00 |

Hold hypothesis holds if F1 / F4 stay high after adaptation while F2 / F3 fall.

### 6b. tcpcubic red: F2 and F3 crossings (z >= 2) within GT3 episodes

episodes 71; both features ever cross: 71; first-crossing offset F3 - F2 p10/p50/p90 -0.20 / 0.16 / 0.69 s; episodes where they cross within the same 66 ms window: 71; within 500 ms: 71.

### 6b. tcpcubic pfifo: F2 and F3 crossings (z >= 2) within GT3 episodes

episodes 61; both features ever cross: 61; first-crossing offset F3 - F2 p10/p50/p90 -0.36 / 0.16 / 0.66 s; episodes where they cross within the same 66 ms window: 61; within 500 ms: 61.

### 6b. tcpcubic pie: F2 and F3 crossings (z >= 2) within GT3 episodes

episodes 103; both features ever cross: 103; first-crossing offset F3 - F2 p10/p50/p90 -0.33 / 0.16 / 0.66 s; episodes where they cross within the same 66 ms window: 95; within 500 ms: 103.

### 6b. tcpcubic fq_codel: F2 and F3 crossings (z >= 2) within GT3 episodes

episodes 34; both features ever cross: 34; first-crossing offset F3 - F2 p10/p50/p90 -0.11 / 0.23 / 0.42 s; episodes where they cross within the same 66 ms window: 31; within 500 ms: 34.

### 6c. delaystep: 0.3-1.3 s after each step, all clients, all AQMs (medians)

| direction | step | client x steps | z1 median | F1 std / calm sigma | max |z3| median | share max |z3| < 1 | lost pkts |
|---|---|---|---|---|---|---|---|
| forward | +20ms | 60 | 5.2 | 1.25 | 9.6 | 0.00 | 224 |
| forward | +50ms | 60 | 12.8 | 0.98 | 9.1 | 0.00 | 230 |
| reverse | +20ms | 60 | 5.0 | 0.84 | 8.7 | 0.00 | 8 |
| reverse | +50ms | 60 | 12.9 | 1.10 | 8.4 | 0.00 | 5 |

Rebase precondition (section 7): z1 >= 1 on every tick, F1 std < calm sigma (ratio < 1), |z3| < 1, no loss. RTT input: reverse steps raise F1 as much as forward ones.

### 6d. Weak cells at 200 ms: does loss separate where delay does not?

| cell | F1 | F2 | F3 | F4 | l (lost pkts) | l / n |
|---|---|---|---|---|---|---|
| fq_codel competition | 0.87 | 0.65 | 0.40 | 0.86 | 0.61 | 0.61 |
| burstcapshallow pfifo | 0.83 | 0.66 | 0.50 | 0.56 | 0.63 | 0.63 |
| all pfifo | 0.84 | 0.75 | 0.56 | 0.62 | 0.52 | 0.52 |

## 7. Verdicts (reading of the tables above; checks run after the main script are quoted with their numbers)

| Hypothesis (spec section 12, Step 1) | Verdict | Evidence |
|---|---|---|
| F2 / F3 are the onset features, F1 / F4 the hold features | **Partly refuted.** F1 is the best early feature; F3 at W_g = 2 does not separate at all | AUC @200 ms, all pfifo: F1 0.84, F2 0.75, F3 0.56, F4 0.62; same order on every AQM |
| F3 (pending growth) carries onset information | **Refuted at W_g = 2 ticks**, recoverable with a longer window | calm MAD of F3 is 0.41 of the demand per 66 ms (frame arrivals are discrete); keyframe peak z 6-8 at the send tick. Extra check: W_g 10 / 30 ticks gives AUC @200 ms 0.61 / 0.68 and keyframe peak z 3.2 / 1.3 |
| F1 / F4 stay elevated after BBR adapts while F2 / F3 return to zero (hold rule) | **Confirmed** | burstlong pfifo share of ticks with z >= 1, first 0.5 s / adapted: F1 0.92 / 0.99, F4 0.90 / 0.99, F2 0.66 / 0.33, F3 0.37 / 0.32; same on red, pie, fq_codel |
| tcpcubic-red: F2 and F3 cross non-simultaneously (the mechanism that defeats v1's 2-of-4) | **Not testable with F3 at W_g = 2**: F3 crosses z >= 2 at every keyframe, so "both cross within 66 ms" is always true (71/71). Needs the smoothed F3 of Step 2 | first-crossing offset F3 - F2 p50 +0.16 s, p90 +0.69 s |
| F5 (loss) separates fq_codel competition and burstcapshallow where F1-F4 fail | **Refuted.** F1 and F4 separate those cells; loss adds a weaker, complementary signal | fq_codel competition @200 ms: F1 0.87, F4 0.86, l 0.61; burstcapshallow pfifo: F1 0.83, l 0.63. v1's miss there is therefore not a missing signal but its absolute floor (`residual_floor_ms` 50) that fq_codel's 5-20 ms queues never reach |
| delaystep: F1 steps up and stays flat, F3 unchanged, no loss (rebase precondition) | **Elevated yes, flat borderline, F3 and no-loss fail** | z1 median 5-13; F1 std / calm sigma 0.84-1.25 (criterion < 1 fails on half the cells); max abs z3 median 8-10 because of keyframe spikes (0 % of cells below 1); forward steps are followed by real loss: sender newly_lost 579, receiver never-timestamped 638, router->switch drops 509 in [step, +1.5 s] over 24 steps (reverse: 87 / 23 / 182). The scenario comment "nothing queues" is wrong for forward steps; mechanism not yet identified (sub-d is still in BBR startup, app-limited, cwnd 577 kB) |
| keyframes: a lone keyframe stays below delta/2 | **Refuted for F3 / F4 at W_g = 2, and F1 at 5 Mb/s** | calm-period keyframe peak mean z: F3 6.4-8.2, F4 5.8-9.4 at 0-33 ms; F1 1.8-2.9 at 200-400 ms; F2 1.3-1.7 |
| calm statistics are stable enough for per-flow normalization | **Yes, with the floor** | per-flow MAD sigma spans 0.18-7 ms (F1) and 0.25-10 ms (F2); F4 min 0.000 s at 1 Mb/s needs the floor (0.019 s); GOP periodicity: lag-30 (990 ms) autocorrelation F3 0.70, F4 0.58 |

Consequences carried into Step 2 (deviations from the spec that need a written reason, listed for decision):

1. F3's window: the spec sweep (1 / 2 / 3 ticks) cannot fix the frame-grid noise; propose adding 10 and 30 ticks (330 / 990 ms, one GOP) to the W_g sweep for F3 only, keeping W_g = 2 for F2.
2. F1 as an onset feature: the spec keeps F1 out of S_k; the AUC says F1 is the earliest and strongest signal on every AQM. Propose fusion variants with and without F1 in Step 4.
3. Rebase precondition on F3 and loss: with the raw F3 and real post-step losses the rule in section 7 never fires; needs the smoothed F3 and a loss tolerance, or a different flatness test.
4. The keyframe response bounds G_ref from below (section 10 already includes keyframes in the calm runs); clipping at z_max = 4 is what keeps a 5 Mb/s keyframe from scoring more than a few ticks.
5. delaystep forward steps cause real router drops in this testbed; before Step 5 the mechanism should be understood (BBR startup / app-limited burst after an RTT jump is the first suspect).

Pass criterion ("onset / hold roles confirmed or refuted with numbers"): met. Hold confirmed; onset roles revised as above.
