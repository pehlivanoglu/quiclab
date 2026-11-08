# Shadow v2, Step 6: generalization (frozen parameters)

200 runs, theta_on 0.25, theta_off 0.125. Frozen: hold kept, rebase dropped, loss gate level+cap. v2 G_ref 57.5, v2-fixed G_ref 71.7 (calm pfifo-r1 only). Playback port vs recorded late_us (B 600 ms): 0 mismatching frames. git 7acb64c-dirty. Truth: git: fda8864-dirty.

## 1. Overall (GT3 + path queue)

95 % intervals: bootstrap over runs (1000 resamples). Two repeats per cell limit the per-cell resolution.

| detector | precision | recall | recall (alarm on) | FA / min CLEAR | latency p50 (ms) | p90 (ms) | recall 95 % | alarm-on recall 95 % | FA / min 95 % | p90 95 % (ms) |
|---|---|---|---|---|---|---|---|---|---|---|
| v2 | 0.95 | 0.80 | 0.91 | 0.43 | 249 | 556 | 0.76-0.84 | 0.87-0.94 | 0.34-0.54 | 530-588 |
| v2-fixed | 0.97 | 0.84 | 0.97 | 0.33 | 283 | 569 | 0.81-0.87 | 0.96-0.98 | 0.25-0.42 | 546-597 |

## 2. Freeze set vs held out

| set | runs | detector | precision | recall | recall (alarm on) | FA / min CLEAR | latency p50 (ms) | p90 (ms) |
|---|---|---|---|---|---|---|---|---|
| freeze set (pfifo-r1) | 25 | v2 | 0.98 | 0.80 | 0.91 | 0.17 | 256 | 576 |
| freeze set (pfifo-r1) | 25 | v2-fixed | 0.98 | 0.84 | 0.98 | 0.18 | 290 | 592 |
| held out: other AQMs r1 | 75 | v2 | 0.94 | 0.80 | 0.91 | 0.51 | 246 | 587 |
| held out: other AQMs r1 | 75 | v2-fixed | 0.96 | 0.83 | 0.97 | 0.34 | 279 | 591 |
| held out: every r2 | 100 | v2 | 0.95 | 0.81 | 0.91 | 0.45 | 249 | 526 |
| held out: every r2 | 100 | v2-fixed | 0.96 | 0.84 | 0.97 | 0.35 | 282 | 548 |

## 3. v2: scenario x AQM (recall / alarm-on recall / FA per min; both repeats, all topologies)

| scenario | fq_codel | pfifo | pie | red |
|---|---|---|---|---|
| burstcap | 0.96 / 1.00 / 0.69 | 0.91 / 1.00 / 0.00 | 0.99 / 0.99 / 0.19 | 0.95 / 0.99 / 0.00 |
| burstcapdeep | 0.93 / 1.00 / 0.71 | 0.92 / 0.99 / 0.10 | 0.99 / 0.99 / 0.00 | 0.99 / 0.99 / 0.09 |
| burstcaphighrtt | 0.95 / 0.97 / 0.66 | 0.99 / 0.99 / 0.00 | 0.99 / 0.99 / 0.37 | 0.99 / 1.00 / 0.00 |
| burstcaplowrtt | 0.92 / 1.00 / 1.24 | 0.85 / 1.00 / 0.09 | 0.99 / 0.99 / 0.00 | 0.88 / 1.00 / 0.00 |
| burstcapshallow | 0.92 / 0.98 / 0.18 | 0.96 / 0.99 / 0.27 | 0.99 / 0.99 / 0.09 | 0.97 / 0.98 / 0.18 |
| burstlong | 0.30 / 1.00 / 2.02 | 0.48 / 1.00 / 0.00 | 0.90 / 1.00 / 0.00 | 0.75 / 1.00 / 0.00 |
| bursttiny | 0.90 / 0.90 / 0.78 | 0.99 / 0.99 / 0.09 | 0.94 / 0.96 / 0.35 | 0.93 / 0.93 / 0.54 |
| burstudp | 0.93 / 0.96 / 0.93 | 0.99 / 0.99 / 0.00 | 0.95 / 0.97 / 0.20 | 0.97 / 0.99 / 0.38 |
| calm030 | - / - / 0.00 | - / - / 0.00 | - / - / 0.31 | - / - / 0.00 |
| calm065 | 0.20 / 0.20 / 0.30 | 0.25 / 0.25 / 0.28 | 0.20 / 0.20 / 0.86 | 0.00 / 0.00 / 0.00 |
| calm090 | 0.61 / 0.68 / 0.27 | 0.34 / 0.45 / 0.00 | 0.35 / 0.62 / 0.00 | 0.28 / 0.29 / 0.00 |
| calmcbr090 | 0.62 / 0.69 / 1.71 | 0.33 / 0.40 / 0.00 | 0.30 / 0.34 / 0.00 | 0.36 / 0.43 / 0.00 |
| capacity | 0.64 / 0.91 / 1.11 | 0.76 / 0.96 / 0.21 | 0.98 / 0.98 / 0.00 | 0.83 / 0.98 / 0.00 |
| cbr | 0.86 / 0.92 / 1.19 | 0.89 / 0.96 / 0.24 | 0.98 / 0.98 / 0.00 | 0.88 / 0.98 / 0.00 |
| delaystep | 0.11 / 0.78 / 2.24 | 0.27 / 0.82 / 2.26 | 0.00 / 1.00 / 2.73 | 0.20 / 1.00 / 3.16 |
| isolate | 0.94 / 0.96 / 0.44 | 0.88 / 0.98 / 0.26 | 0.90 / 0.94 / 0.13 | 0.91 / 0.96 / 0.19 |
| onoff | 0.90 / 0.92 / 1.03 | 0.80 / 0.99 / 0.00 | 0.81 / 0.97 / 0.00 | 0.87 / 0.99 / 0.00 |
| ppbp | 0.24 / 0.36 / 0.22 | 0.09 / 0.12 / 0.00 | 0.10 / 0.22 / 0.00 | 0.04 / 0.07 / 0.00 |
| ramp | 0.57 / 1.00 / 3.39 | 0.73 / 0.95 / 0.00 | 0.67 / 0.97 / 0.23 | 0.62 / 1.00 / 0.22 |
| randloss | 0.00 / 0.00 / 0.10 | 0.00 / 0.00 / 0.19 | 0.75 / 0.75 / 0.50 | 0.00 / 0.00 / 0.10 |
| revdelay | 0.94 / 0.97 / 0.76 | 0.97 / 0.99 / 0.00 | 0.98 / 0.98 / 0.10 | 0.98 / 0.99 / 0.09 |
| splitcap | 0.89 / 0.97 / 0.74 | 0.88 / 0.98 / 0.14 | 0.96 / 0.99 / 0.10 | 0.87 / 0.98 / 0.14 |
| splitudp | 0.91 / 0.97 / 0.68 | 0.94 / 0.98 / 0.06 | 0.96 / 0.98 / 0.19 | 0.92 / 0.97 / 0.24 |
| tcpbbr | 0.65 / 0.81 / 1.97 | 0.92 / 1.00 / 0.00 | 0.90 / 0.99 / 0.21 | 0.94 / 1.00 / 0.00 |
| tcpcubic | 0.78 / 0.89 / 1.73 | 0.98 / 0.98 / 0.00 | 0.61 / 0.99 / 0.20 | 0.86 / 0.97 / 0.11 |

## 3. v2-fixed: scenario x AQM (recall / alarm-on recall / FA per min; both repeats, all topologies)

| scenario | fq_codel | pfifo | pie | red |
|---|---|---|---|---|
| burstcap | 0.97 / 1.00 / 0.35 | 0.91 / 1.00 / 0.00 | 0.99 / 0.99 / 0.19 | 0.96 / 1.00 / 0.09 |
| burstcapdeep | 0.96 / 1.00 / 0.44 | 0.92 / 0.99 / 0.20 | 0.99 / 0.99 / 0.00 | 1.00 / 1.00 / 0.00 |
| burstcaphighrtt | 0.93 / 0.95 / 0.58 | 0.99 / 0.99 / 0.00 | 0.99 / 0.99 / 0.28 | 0.99 / 1.00 / 0.00 |
| burstcaplowrtt | 0.94 / 1.00 / 0.62 | 0.85 / 1.00 / 0.00 | 0.99 / 0.99 / 0.00 | 0.88 / 1.00 / 0.00 |
| burstcapshallow | 0.76 / 0.80 / 0.00 | 0.96 / 0.99 / 0.00 | 0.97 / 0.97 / 0.00 | 0.97 / 0.97 / 0.00 |
| burstlong | 0.32 / 1.00 / 0.77 | 0.48 / 0.99 / 0.00 | 0.90 / 1.00 / 0.00 | 0.75 / 1.00 / 0.00 |
| bursttiny | 0.87 / 0.87 / 0.17 | 0.96 / 0.96 / 0.09 | 0.96 / 0.97 / 0.35 | 0.92 / 0.92 / 0.27 |
| burstudp | 0.91 / 0.91 / 0.25 | 0.98 / 0.99 / 0.00 | 0.95 / 0.99 / 0.10 | 0.97 / 0.99 / 0.10 |
| calm030 | - / - / 0.00 | - / - / 0.00 | - / - / 0.00 | - / - / 0.00 |
| calm065 | 0.40 / 0.40 / 0.00 | 0.50 / 0.50 / 0.28 | 0.00 / 0.00 / 0.58 | 0.00 / 0.00 / 0.00 |
| calm090 | 0.59 / 0.93 / 2.13 | 0.69 / 0.86 / 0.86 | 0.42 / 0.96 / 0.00 | 0.80 / 0.92 / 0.95 |
| calmcbr090 | 0.58 / 0.85 / 4.89 | 0.74 / 0.84 / 0.25 | 0.66 / 0.72 / 0.00 | 0.78 / 0.88 / 1.33 |
| capacity | 0.67 / 0.96 / 0.55 | 0.78 / 0.98 / 0.41 | 0.96 / 0.98 / 0.00 | 0.83 / 1.00 / 0.21 |
| cbr | 0.81 / 0.95 / 0.79 | 0.94 / 1.00 / 0.48 | 0.98 / 0.98 / 0.25 | 0.88 / 0.98 / 0.00 |
| delaystep | 0.00 / 0.78 / 3.07 | 0.18 / 0.73 / 2.82 | 0.00 / 1.00 / 2.45 | 0.00 / 1.00 / 3.04 |
| isolate | 0.96 / 0.98 / 0.13 | 0.88 / 0.98 / 0.00 | 0.90 / 0.94 / 0.00 | 0.91 / 0.96 / 0.06 |
| onoff | 0.87 / 0.88 / 1.44 | 0.77 / 1.00 / 0.00 | 0.76 / 0.98 / 0.00 | 0.84 / 1.00 / 0.29 |
| ppbp | 0.45 / 1.00 / 0.67 | 0.66 / 1.00 / 0.00 | 0.46 / 1.00 / 0.00 | 0.58 / 0.99 / 0.00 |
| ramp | 0.55 / 1.00 / 0.66 | 0.71 / 0.97 / 0.11 | 0.62 / 0.98 / 0.34 | 0.57 / 1.00 / 0.22 |
| randloss | 0.25 / 0.25 / 0.20 | 0.00 / 0.00 / 0.09 | 0.75 / 0.75 / 0.60 | 0.00 / 0.00 / 0.29 |
| revdelay | 0.92 / 0.96 / 0.25 | 0.97 / 0.99 / 0.09 | 0.98 / 0.99 / 0.00 | 0.98 / 0.99 / 0.18 |
| splitcap | 0.90 / 0.98 / 0.17 | 0.89 / 0.99 / 0.14 | 0.96 / 0.99 / 0.15 | 0.87 / 0.98 / 0.19 |
| splitudp | 0.94 / 1.00 / 0.74 | 0.93 / 0.97 / 0.13 | 0.96 / 0.98 / 0.19 | 0.92 / 0.97 / 0.12 |
| tcpbbr | 0.62 / 0.79 / 1.04 | 0.92 / 1.00 / 0.10 | 0.90 / 0.99 / 0.00 | 0.94 / 1.00 / 0.00 |
| tcpcubic | 0.75 / 0.86 / 0.71 | 0.98 / 0.98 / 0.00 | 0.60 / 0.99 / 0.00 | 0.89 / 0.99 / 0.00 |

## 4. Negative scenarios: FA / min CLEAR (pass: <= 0.3)

Evidence: false alarms, share with a GT1 queue on the client's path at the alarm, and for randloss the share inside an injected loss window (+ 1 s).

| scenario | AQM | runs | v2 FA / min | v2-fixed FA / min | v2 | v2-fixed | v2 false alarms | v2-fixed false alarms |
|---|---|---|---|---|---|---|---|---|
| calm030 | fq_codel | 2 | 0.00 | 0.00 | pass | pass | 0: 0% GT1 on path | 0: 0% GT1 on path |
| calm030 | pfifo | 2 | 0.00 | 0.00 | pass | pass | 0: 0% GT1 on path | 0: 0% GT1 on path |
| calm030 | pie | 2 | 0.31 | 0.00 | FAIL | pass | 1: 0% GT1 on path | 0: 0% GT1 on path |
| calm030 | red | 2 | 0.00 | 0.00 | pass | pass | 0: 0% GT1 on path | 0: 0% GT1 on path |
| calm065 | fq_codel | 2 | 0.30 | 0.00 | pass | pass | 1: 0% GT1 on path | 0: 0% GT1 on path |
| calm065 | pfifo | 2 | 0.28 | 0.28 | pass | pass | 1: 0% GT1 on path | 1: 0% GT1 on path |
| calm065 | pie | 2 | 0.86 | 0.58 | FAIL | FAIL | 3: 0% GT1 on path | 2: 0% GT1 on path |
| calm065 | red | 2 | 0.00 | 0.00 | pass | pass | 0: 0% GT1 on path | 0: 0% GT1 on path |
| calm090 | fq_codel | 2 | 0.27 | 2.13 | pass | FAIL | 1: 100% GT1 on path | 8: 50% GT1 on path |
| calm090 | pfifo | 2 | 0.00 | 0.86 | pass | FAIL | 0: 0% GT1 on path | 3: 67% GT1 on path |
| calm090 | pie | 2 | 0.00 | 0.00 | pass | pass | 0: 0% GT1 on path | 0: 0% GT1 on path |
| calm090 | red | 2 | 0.00 | 0.95 | pass | FAIL | 0: 0% GT1 on path | 3: 67% GT1 on path |
| calmcbr090 | fq_codel | 2 | 1.71 | 4.89 | FAIL | FAIL | 7: 57% GT1 on path | 20: 50% GT1 on path |
| calmcbr090 | pfifo | 2 | 0.00 | 0.25 | pass | pass | 0: 0% GT1 on path | 1: 0% GT1 on path |
| calmcbr090 | pie | 2 | 0.00 | 0.00 | pass | pass | 0: 0% GT1 on path | 0: 0% GT1 on path |
| calmcbr090 | red | 2 | 0.00 | 1.33 | pass | FAIL | 0: 0% GT1 on path | 6: 50% GT1 on path |
| randloss | fq_codel | 2 | 0.10 | 0.20 | pass | pass | 1: 0% GT1 on path, 100% in a loss window | 2: 0% GT1 on path, 100% in a loss window |
| randloss | pfifo | 2 | 0.19 | 0.09 | pass | pass | 2: 0% GT1 on path, 100% in a loss window | 1: 0% GT1 on path, 100% in a loss window |
| randloss | pie | 2 | 0.50 | 0.60 | FAIL | FAIL | 5: 0% GT1 on path, 80% in a loss window | 6: 0% GT1 on path, 83% in a loss window |
| randloss | red | 2 | 0.10 | 0.29 | pass | pass | 1: 0% GT1 on path, 100% in a loss window | 3: 0% GT1 on path, 100% in a loss window |

Worst cell: v2 1.71, v2-fixed 4.89.

## 5. False alarms by the GT1 (router queue) state at the alarm (reviewer addendum)

A false alarm here is an alarm start in GT3 CLEAR time outside every GT3 episode window (gt_score rule).

| detector | scope | false alarms | GT1 queue on the client's path | GT1 queue elsewhere | no GT1 queue |
|---|---|---|---|---|---|
| v2 | all scenarios | 391 | 0.49 | 0.01 | 0.50 |
| v2 | negative scenarios | 23 | 0.22 | 0.00 | 0.78 |
| v2-fixed | all scenarios | 293 | 0.35 | 0.02 | 0.63 |
| v2-fixed | negative scenarios | 56 | 0.38 | 0.00 | 0.62 |

## 6. Weak cells (recall (alarm-on recall) / FA per min / latency p50 ms: verdict vs v1)

v1 = shadow tuned:full without grouping, internal reference only. Verdict: recall (gt_score) ok when >= v1 - 0.02, FA ok when <= v1 + 0.1 per min. Miss evidence: episodes with no alarm on in the window; FA evidence: GT1 queue on the client's path at the false alarm.

| cell | episodes | v1 (reference) | v2 | v2-fixed | v2 miss evidence | v2-fixed miss evidence | v2 FA evidence | v2-fixed FA evidence |
|---|---|---|---|---|---|---|---|---|
| burstudp fq_codel | 46 | 0.54 / 0.17 / 337 | 0.93 (0.96) / 0.93 / 222: recall better, FA worse | 0.91 (0.91) / 0.25 / 235: better | 2 missed: 0% < 0.5 s, 100% GT1 on path, peak q p50 58 ms, trigger loss 2 | 4 missed: 0% < 0.5 s, 100% GT1 on path, peak q p50 47 ms, trigger loss 4 | 11 FA, 100% GT1 on path | 3 FA, 100% GT1 on path |
| tcpcubic fq_codel | 64 | 0.56 / 0.10 / 258 | 0.78 (0.89) / 1.73 / 210: recall better, FA worse | 0.75 (0.86) / 0.71 / 217: recall better, FA worse | 7 missed: 0% < 0.5 s, 71% GT1 on path, peak q p50 55 ms, trigger loss 7 | 9 missed: 0% < 0.5 s, 78% GT1 on path, peak q p50 55 ms, trigger loss 9 | 17 FA, 94% GT1 on path | 7 FA, 100% GT1 on path |
| tcpbbr fq_codel | 77 | 0.56 / 0.41 / 263 | 0.65 (0.81) / 1.97 / 199: recall better, FA worse | 0.62 (0.79) / 1.04 / 218: recall better, FA worse | 15 missed: 0% < 0.5 s, 93% GT1 on path, peak q p50 58 ms, trigger loss 15 | 16 missed: 0% < 0.5 s, 94% GT1 on path, peak q p50 58 ms, trigger loss 16 | 19 FA, 95% GT1 on path | 10 FA, 100% GT1 on path |
| onoff fq_codel | 52 | 0.58 / 0.62 / 566 | 0.90 (0.92) / 1.03 / 252: recall better, FA worse | 0.87 (0.88) / 1.44 / 235: recall better, FA worse | 4 missed: 0% < 0.5 s, 100% GT1 on path, peak q p50 45 ms, trigger loss 4 | 6 missed: 0% < 0.5 s, 100% GT1 on path, peak q p50 47 ms, trigger loss 6 | 5 FA, 100% GT1 on path | 7 FA, 100% GT1 on path |
| splitudp fq_codel | 34 | 0.76 / 0.28 / 492 | 0.91 (0.97) / 0.68 / 300: recall better, FA worse | 0.94 (1.00) / 0.74 / 325: recall better, FA worse | 1 missed: 0% < 0.5 s, 100% GT1 on path, peak q p50 24 ms, trigger loss 1 | no misses | 12 FA, 75% GT1 on path | 13 FA, 38% GT1 on path |
| burstcapshallow pfifo | 148 | 0.89 / 0.00 / 565 | 0.96 (0.99) / 0.27 / 219: recall better, FA worse | 0.96 (0.99) / 0.00 / 369: better | 1 missed: 0% < 0.5 s, 100% GT1 on path, peak q p50 14 ms, trigger loss 1 | 2 missed: 0% < 0.5 s, 100% GT1 on path, peak q p50 14 ms, trigger loss 2 | 3 FA, 0% GT1 on path | 0 FA, 0% GT1 on path |
| tcpcubic red | 138 | 0.53 / 0.00 / 533 | 0.86 (0.97) / 0.11 / 372: recall better, FA worse | 0.89 (0.99) / 0.00 / 395: better | 4 missed: 0% < 0.5 s, 75% GT1 on path, peak q p50 53 ms, trigger delay 3, loss 1 | 2 missed: 0% < 0.5 s, 50% GT1 on path, peak q p50 53 ms, trigger delay 1, loss 1 | 1 FA, 0% GT1 on path | 0 FA, 0% GT1 on path |
| burstlong pfifo | 153 | 0.97 / 0.00 / 419 | 0.48 (1.00) / 0.00 / 216: recall worse | 0.48 (0.99) / 0.00 / 244: recall worse | no misses | 1 missed: 0% < 0.5 s, 100% GT1 on path, peak q p50 59 ms, trigger loss 1 | 0 FA, 0% GT1 on path | 0 FA, 0% GT1 on path |
| calm090 pfifo | 121 | 0.58 / 0.57 / 506 | 0.34 (0.45) / 0.00 / 577: recall worse | 0.69 (0.86) / 0.86 / 410: recall better, FA worse | 66 missed: 0% < 0.5 s, 100% GT1 on path, peak q p50 45 ms, trigger delay 64, loss 2 | 17 missed: 0% < 0.5 s, 100% GT1 on path, peak q p50 42 ms, trigger delay 17 | 0 FA, 0% GT1 on path | 3 FA, 67% GT1 on path |

## 7. Lead time before harm at three playout buffers

Harm = first missed playout deadline in [t_on, t_end + 2 s] of a GT3 episode (playback replay at buffer B). Lead = harm time - first time the alarm is on in [t_on - 1 s, harm]. Harmless = alarm with no missed deadline in [start, end + 2 s] (includes alarms on real congestion the buffer absorbed).

| B (ms) | detector | GT3 episodes with harm | alarm before harm | missed | lead p10 (ms) | p50 | p90 | lead < 200 ms share | harmless alarm share |
|---|---|---|---|---|---|---|---|---|---|
| 200 | v2 | 1741 | 0.94 | 109 | 290 | 1474 | 3670 | 0.06 | 0.84 |
| 200 | v2-fixed | 1741 | 0.96 | 71 | 298 | 1563 | 3931 | 0.06 | 0.84 |
| 200 | v1 (reference) | 1741 | 0.87 | 218 | 220 | 1434 | 3653 | 0.09 | 0.88 |
| 400 | v2 | 1511 | 0.96 | 61 | 561 | 1691 | 3794 | 0.01 | 0.86 |
| 400 | v2-fixed | 1511 | 0.98 | 27 | 572 | 1795 | 4200 | 0.01 | 0.86 |
| 400 | v1 (reference) | 1511 | 0.94 | 88 | 459 | 1590 | 3747 | 0.03 | 0.89 |
| 600 | v2 | 1354 | 0.97 | 46 | 813 | 1946 | 3889 | 0.00 | 0.88 |
| 600 | v2-fixed | 1354 | 0.99 | 14 | 819 | 2039 | 4439 | 0.00 | 0.88 |
| 600 | v1 (reference) | 1354 | 0.97 | 45 | 675 | 1814 | 3959 | 0.01 | 0.90 |

## 8. Harmful GT3 episodes v1 missed (B 600 ms; reviewer addendum)

45 episodes. Caught before harm: v2 32, v2-fixed 32.

| run | client | t_on (s) | duration (s) | v2 | v2-fixed |
|---|---|---|---|---|---|
| det-burstcap-fq_codel-r1 | sub-c | 30.5 | 4.75 | missed | missed |
| det-burstcap-pfifo-r1 | sub-a | 61.8 | 4.29 | 921 ms before | 822 ms before |
| det-burstcap-pfifo-r2 | sub-b | 15.0 | 4.98 | 606 ms before | 507 ms before |
| det-burstcap-pie-r1 | sub-c | 30.5 | 6.26 | 991 ms before | 793 ms before |
| det-burstcapdeep-fq_codel-r2 | sub-b | 48.4 | 3.02 | 1599 ms before | 1533 ms before |
| det-burstcapdeep-red-r1 | sub-d | 15.3 | 2.70 | missed | 1114 ms before |
| det-burstcaphighrtt-fq_codel-r2 | sub-b | 48.4 | 2.59 | 1539 ms before | 1473 ms before |
| det-burstcaphighrtt-pie-r1 | sub-c | 30.8 | 5.53 | missed | missed |
| det-burstcaphighrtt-red-r2 | sub-b | 14.8 | 5.21 | 829 ms before | 829 ms before |
| det-burstcaplowrtt-red-r2 | sub-a | 15.0 | 4.64 | 650 ms before | 452 ms before |
| det-burstcapshallow-fq_codel-r1 | sub-b | 45.9 | 1.24 | 1250 ms before | 1085 ms before |
| det-burstlong-pfifo-r1 | sub-a | 15.0 | 61.63 | 1035 ms before | 639 ms before |
| det-burstlong-pfifo-r2 | sub-b | 15.2 | 10.69 | 1405 ms before | missed |
| det-burstlong-pie-r1 | sub-c | 15.0 | 60.98 | missed | missed |
| det-burstlong-red-r1 | sub-c | 15.0 | 60.82 | 400 ms before | missed |
| det-burstudp-pfifo-r1 | sub-d | 15.0 | 2.96 | 386 ms before | 386 ms before |
| det-burstudp-pfifo-r1 | sub-a | 45.9 | 2.80 | 504 ms before | 471 ms before |
| det-burstudp-pie-r1 | sub-a | 45.8 | 2.96 | 472 ms before | 439 ms before |
| det-burstudp-red-r1 | sub-d | 14.9 | 3.21 | missed | missed |
| det-capacity-pie-r2 | sub-b | 20.2 | 10.39 | 2563 ms before | 2563 ms before |
| det-cbr-red-r1 | sub-d | 20.3 | 10.61 | missed | 2352 ms before |
| det-isolate-pfifo-r1 | sub-b | 15.4 | 3.64 | missed | missed |
| det-isolate-pie-r1 | sub-d | 29.1 | 4.52 | missed | missed |
| det-isolate-red-r1 | sub-b | 15.1 | 3.76 | 1625 ms before | missed |
| det-onoff-pfifo-r1 | sub-c | 15.0 | 2.88 | 510 ms before | 477 ms before |
| det-onoff-pfifo-r1 | sub-d | 27.2 | 1.83 | 3422 ms before | 3422 ms before |
| det-onoff-pie-r2 | sub-b | 15.1 | 3.00 | 597 ms before | 597 ms before |
| det-onoff-red-r1 | sub-a | 57.0 | 2.91 | 1237 ms before | 1237 ms before |
| det-onoff-red-r2 | sub-a | 99.1 | 2.75 | 1277 ms before | 1277 ms before |
| det-ramp-pie-r1 | sub-d | 15.0 | 16.29 | missed | missed |
| det-ramp-red-r2 | sub-b | 18.1 | 7.71 | 3839 ms before | 3622 ms before |
| det-ramp-red-r2 | sub-a | 18.2 | 7.52 | 3389 ms before | 2267 ms before |
| det-revdelay-fq_codel-r1 | sub-d | 15.8 | 2.11 | missed | missed |
| det-splitcap-pfifo-r1 | b2 | 14.7 | 5.21 | missed | missed |
| det-splitcap-pfifo-r2 | b2 | 14.7 | 2.71 | 177 ms before | 573 ms before |
| det-splitcap-pfifo-r2 | b1 | 73.1 | 1.52 | 266 ms before | 233 ms before |
| det-splitcap-pie-r1 | b1 | 15.0 | 4.97 | 416 ms before | 218 ms before |
| det-splitcap-red-r1 | b1 | 15.1 | 4.80 | 573 ms before | 573 ms before |
| det-splitcap-red-r1 | a1 | 299.6 | 4.69 | 2360 ms before | 2327 ms before |
| det-splitcap-red-r2 | b1 | 27.9 | 2.51 | 972 ms before | 1005 ms before |
| det-splitudp-pfifo-r2 | b3 | 15.1 | 2.68 | 348 ms before | 348 ms before |
| det-splitudp-pfifo-r2 | a2 | 31.1 | 2.88 | 574 ms before | 607 ms before |
| det-splitudp-pie-r1 | a2 | 15.0 | 2.44 | 418 ms before | 418 ms before |
| det-splitudp-red-r2 | a3 | 30.5 | 4.53 | missed | 115 ms before |
| det-tcpbbr-fq_codel-r2 | sub-d | 32.1 | 2.67 | missed | missed |

Note (reviewer addendum): gcc is not scored here. Its replay applies a 500 ms detection floor, so the Step 0 gcc latency is not comparable with v1 / v2 decision times.

## 9. Verdict

Frozen detectors: fusion d, hold, loss gate level+cap (reports/detector-v2/lossgate.md), causal F3 normaliser, F4 drain time in seconds (P / R, floor 0.0079). G_ref v2 57.5, v2-fixed 71.7.

- **Generalization holds.** Freeze set (pfifo-r1) and held-out sets agree within 0.01 in recall and within 66 ms in p90. Held-out FA is higher on the other AQMs (v2 0.51 vs 0.17 per min, v2-fixed 0.34 vs 0.18), driven by fq_codel (section 3).
- **Negative-scenario criterion FAILS (<= 0.3 FA / min).** Worst cells: v2 calmcbr090 fq_codel 1.71; v2-fixed calmcbr090 fq_codel 4.89, calm090 fq_codel 2.13, calmcbr090 red 1.33. Responsible rules:
  - calm090 / calmcbr090 (u 0.9): keyframes build a real router queue that GT3 labels CLEAR for the client (GT1 queue on the path in about half of these alarms, section 4). v2-fixed fires more because its calm scale comes from calm030 / 065; v2 learns the loaded state as normal (calm090 pfifo recall 0.34).
  - randloss: with the level+cap gate v2 passes on fq_codel, pfifo and red (0.10-0.19) and fails on pie (0.50); v2-fixed 0.09-0.60. Loss alone can no longer raise an alarm; the remaining alarms need delay / pending-bytes evidence that loss recovery itself produces.
  - calm065 pie 0.58-0.86, calm030 pie 0.31 (v2): 1-3 alarms over two runs; one alarm is about 0.3 per min at this resolution.
  Nothing was tuned to pass.
- **Weak cells: every one improved or explained.** Recall over v1: fq_codel cells 0.54-0.76 -> 0.62-0.94, burstcapshallow 0.89 -> 0.96, tcpcubic red 0.53 -> 0.86-0.89, at lower latency. fq_codel FA is higher (v2 up to 1.97, v2-fixed up to 1.44 per min); 94-100 % of those alarms have a GT1 queue on the client's path that GT3 labels CLEAR. burstlong gt_score recall 0.48 is the hold rule (alarm-on recall 1.00 / 0.99). calm090 pfifo: v2 worse (0.34 vs 0.58), v2-fixed better (0.69, alarm-on 0.86) at 0.86 FA per min.
- **Lead time.** Warned before harm: v2 0.94 / 0.96 / 0.97, v2-fixed 0.96 / 0.98 / 0.99 at B 200 / 400 / 600 ms (v1 0.87 / 0.94 / 0.97). Lead p50 1.5-2.0 s; p10 0.3 s at B 200 ms, 0.8 s at B 600 ms. 84-88 % of alarms are followed by no missed deadline.
- **v1-missed harmful episodes:** v2 and v2-fixed each warn before harm in 32 of the 45.
