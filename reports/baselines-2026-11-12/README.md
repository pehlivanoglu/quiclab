# Reference numbers on the development set (2026-11-12)

Read-only; engine and detector unchanged; N1–N5 not scored. Code:
`scripts/baseline_scores.py`. Files: `detector-rows.jsonl.gz`,
`detector-summary.md`, `ecg-rows.jsonl.gz`, `ecg-summary.md` (outputs of the ECG
pass in `<run>/grouping-d150-v2-owd/`).

**Detector** (frozen Shadow v2, RTT ticks vs OWD ticks; gt_score against GT1 / GT2
link views), 206 development runs:

| AQM family | source | GT1 recall / precision / FA per min | GT2 recall / precision / FA per min |
|---|---|---|---|
| pfifo / red / pie / codel (152 runs) | RTT | 0.42 / 0.97 / 0.11 | 0.39 / 0.97 / 0.10 |
| | OWD | 0.42 / 0.98 / 0.09 | 0.39 / 0.98 / 0.07 |
| cake (33) | RTT | 0.31 / 0.98 / 0.08 | 0.33 / 0.97 / 0.08 |
| | OWD | 0.32 / 0.98 / 0.07 | 0.34 / 0.98 / 0.07 |
| fq_codel (20) | RTT / OWD | 0.26 / 0.95 / 0.14 | 0.16 / 0.96 / 0.09 |

RTT and OWD agree except where the ACK path is disturbed: K3 (reverse delays /
cross traffic / jitter) GT2 precision 0.74, FA 0.72 / min on RTT vs 0.95, 0.10 on OWD.
Episode recall counts every GT1 / GT2 episode, keyframe-scale ones included;
latency p50 about 250 ms. Per campaign in `detector-summary.md`.

**ECG v1.2, delta 0.150 s, v2-owd onsets, GT1 truth** (per-client GT1 on fq_codel / cake):

| set | runs | leaf P | leaf R | coverage p50 | final tree correct | false SAME pairs |
|---|---|---|---|---|---|---|
| pfifo / pie / red, K / C1 / M | 93 | 1.00 | 1.00 | 0.60 | 83 / 93 | 0 |
| codel, M | 25 | 1.00 | 1.00 | 0.60 | 24 / 25 | 0 |
| J1 | 10 | 1.00 | 1.00 | 0.71 | 9 / 10 | 0 |
| cake, M and G0 | 33 | 0.95 | 1.00 | 0.30 | 19 / 33 | 5 (M1) |
| fq_codel | 20 | 0.93 | 1.00 | 0.09 | 10 / 20 | 2 (C1) |
| G0 pfifo / pie / red (negatives) | 24 | – | – | – | 14 / 24 no group | 25 |

Events to membership (events a flow took part in before it became a member,
evidence-free SOLO / GLOBAL events included): p50 2–3 on the microbenchmarks, 3–6
on K1–K6, 10 on K5 pie and K6 fq_codel. Per campaign × AQM in `ecg-summary.md`.
The 5 false SAME pairs on cake (M1) are new with the per-client truth: clients
whose own queue did not stand are no longer expected, so grouping them with the
others now counts as wrong.

## Reading the two false-alarm numbers and the recall (2026-11-12)

`fa_reconcile.py` → `fa_reconcile.md` (same alarms, both definitions, on K1 pfifo
r1, the J1 runs, M2 q05 and K2 part110).

- **e2e** (grouping reports, J1 detector table): an alarm is false when it starts
  outside a *planned* window the client is expected in (+ 2 s); per minute of run,
  all clients summed. Most of these alarms sit in real GT1 queue episodes the plan
  did not script (K1 pfifo r1: 32 of 37). Jitter lowers this number because the
  detector then misses more of those short unscripted queues (alarms 363 → ~340),
  not because it is better.
- **gt_score** (baseline table): an alarm is false only in GT1 CLEAR time; per
  minute of CLEAR time summed over clients (CLEAR is ~0.65–0.73 of client time).
  Same runs: 0.01–0.08 per minute, no trend with jitter.
- **GT1 episode recall 0.42** counts every GT1 episode once per client on its path,
  short ones included: 44 % of the FIFO episodes last < 0.5 s (recall 0.07),
  0.5–1 s 0.33, 1–2 s 0.72, ≥ 2 s 0.82. Planned-window recall (an expected client
  alarms in a shared window) is 0.99–1.00 on the same runs.

## FlowBot's ground truth on our runs (2026-11-12)

`scripts/gt_flowbot.py` ports FlowBot's labelling (flowbot/src/siamese/preprocess.py,
`get_double_queues`): per router egress, the queue length averaged over the last
50 ms (FlowBot: rolling 10 samples at 5 ms); a client is congested while that
average is >= 50 packets on any egress of its path; no minimum duration, no
ambiguous band, total queue length on fq_codel / cake. 5 ms queue CSV where the
topology records it (split, tree8, uneven), else 25 ms. Column "FlowBot GT" in
`detector-summary.md` / `detector-runs.md`.

| AQM | truth | episodes | recall | precision | FA / CLEAR min | latency p50 / p90 ms |
|---|---|---|---|---|---|---|
| pfifo / red / pie / codel | GT1 | 36 359 | 0.42 | 0.98 | 0.09 | 256 / 552 |
| | FlowBot GT | 49 896 | 0.34 | 0.91 | 0.31 | 113 / 259 |
| cake | FlowBot GT | 9 717 | 0.20 | 0.91 | 0.26 | 165 / 721 |
| fq_codel | FlowBot GT | 11 293 | 0.16 | 0.87 | 0.35 | 0 / 359 |

The 50-packet threshold is absolute: it is about 34 ms of queue at 17.5 Mb/s, a
full queue on the 0.5 BDP runs (limit 50: hardly ever reached) and well above the
whole queue of low-rate cells (M5 bw1), where every alarm counts as false (M5:
precision 0.72, FA 1.04 / min). With no persistence or hysteresis the label flickers
around the threshold: more and shorter episodes (G0 calm065 pfifo: 28 episodes,
p50 38 ms), and alarms that start in a short CLEAR gap inside a congestion count
as false. Latency is shorter (113 ms) because an episode starts only once 50
packets have built up, later than GT1's 5 ms.
