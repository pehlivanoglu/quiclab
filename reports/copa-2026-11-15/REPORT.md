# Copa runs: detector and grouping (2026-11-15)

**What was run.** Block M13 of the v3 campaign:
- the video uses **Copa** as its congestion control instead of BBR;
- everything else is the default T-BASE point: one leaf of 4 clients behind `router->switch`, s 0.30, U 0.70, BG-CBR, the sburst grid (u 1.05 / 1.15 / 1.3 × d 2 / 5 / 10 s);
- pfifo and codel, 2 reps, so 4 runs.

**Comparison.** Each Copa cell sits next to the same point with BBR: C2 sburst s030u070 under pfifo and codel, also 4 runs. Every value is rep 1 / rep 2.

**Method.** Measurement only. The frozen Shadow v2 detector, ECG v1.2, h3 and SETS (Step 9) are used unchanged.
- ECG output for the 4 Copa runs and C2 codel was produced with the existing `score_v3.ecg_one`.
- The rest are the Step 8 and Step 9 scorers.

**Files** (in this folder): driver `copa.py`, rows `rows-copa.jsonl`, full tables `tables.md`.

## 1. Detector: Copa changes nothing

**v2-owd, recall / precision / median latency:**

| cell | GT3 | GT1 | GT2 | false alarms in CLEAR time |
|---|---|---|---|---|
| Copa pfifo | 1.00 / 1.00, 208–223 ms | 0.86 / 1.00 recall, P 1.00, 272–284 ms | 0.95 / 1.00, P 1.00 | 0 |
| BBR pfifo | 1.00 / 0.97, 165–212 ms | 1.00 / 1.00, P 1.00, 190–232 ms | 1.00 / 1.00 | 0 |
| Copa codel | 1.00 / 1.00, 206–212 ms | 1.00 / 1.00, P 1.00, 255–279 ms | 1.00 / 1.00 | 0 |
| BBR codel | 1.00 / 1.00, 175–190 ms | 0.95 / 1.00, P 1.00, 203–224 ms | 0.90 / 1.00 | 0 |

- **Precision is 1.00 everywhere,** with no false alarms in calm time and the alarm on during every episode (0.95–1.00).
- **Every stimulus window is detected:** all 4 clients alarm within [start − 1 s, start + 10 s] in every one of the 72 Copa windows (9 cells × 2 windows × 2 AQMs × 2 reps).
- **GT-Q / GT-H** (valid in all 8 runs):

  | cell | GT-Q precision | harmful episodes (GT-H 600) | alarm started before harm |
  |---|---|---|---|
  | Copa | 1.00 | 39–51 per run | 1.00 |
  | BBR | 1.00 | 57–62 per run | 0.95–1.00 |

- **Small differences:**
  - Copa's GT1 / GT2 latency is ~40–60 ms higher (median 255–284 ms against 190–232 ms).
  - Copa pfifo rep 1 has GT1 recall 0.86 against 1.00 in rep 2, with no known cause (not reliable).
  - Copa produces fewer GT3 episodes under pfifo (119–121 against 175–191) and fewer harmful episodes.
- v2-fixed-owd gives the same picture (`tables.md`).

## 2. How the video reacts (context, not a detector result)

Video load during a stimulus window relative to its calm rate (median), at u = 1.3:

| AQM | Copa | BBR |
|---|---|---|
| pfifo | **1.33–1.42** (u 1.05: 1.00–1.23) | 0.34–0.82 |
| codel | 0.42–0.60 | 0.33–0.71 |

- **Under pfifo the Copa video does not back off during overload.** It sends 1.2–1.55× its calm rate, and the more so the larger u is. BBR falls to about half.
- Why is not measured here. A catch-up of queued frames after the queue builds is one candidate.
- This may explain why Copa pfifo has fewer GT3 episodes and fewer harmful ones.

## 3. Grouping: one true set, found by every method

Only one leaf here, so the test is small: are the 4 clients put into one group, and nothing else?

**v2-owd onsets:**

| cell | ECG events | event observes all 4 | SETS k2 F1 | SETS k3 F1 | ECG F1 | h3 F1 | spurious groups per close (SETS k3 / ECG / h3) |
|---|---|---|---|---|---|---|---|
| Copa pfifo | 19 / 20 | 0.89 / 0.80 | 0.95 / 0.95 | 0.89 / 0.90 | 0.95 / 0.95 | 0.89 / 0.76 | 0 / 0 / 0; 0.05 / 0 / 0.40 |
| BBR pfifo | 22 / 19 | 0.64 / 0.89 | 0.95 / 0.95 | 0.90 / 0.89 | 0.91 / 0.95 | 0.68 / 0.89 | 0 / 0 / 0.73; 0.26 / 0 / 0 |
| Copa codel | 21 / 18 | 0.71 / 1.00 | 0.95 / 0.94 | 0.90 / 0.89 | 0.95 / 0.94 | 0.78 / 0.64 | 0.19 / 0 / 0.57; 0 / 0 / 0.78 |
| BBR codel | 22 / 18 | 0.64 / 1.00 | 0.95 / 0.94 | 0.91 / 0.89 | 0.95 / 0.94 | 0.91 / 0.78 | 0.14 / 0 / 0; 0 / 0 / 0.83 |

- **SETS (k2) and ECG** reach F1 ≥ 0.9 after 2 events in every run and keep it. Pair precision is 1.00 and recall 0.86–1.00.
- **h3 is the weak one**, under both Copa and BBR:
  - F1 0.64–0.91;
  - up to 0.8 spurious groups per close;
  - pair recall down to 0.42–0.69, because it splits the leaf.
- **With truth onsets** every event observes all 4 clients, and SETS / ECG score 0.94 identically for Copa and BBR.
- When an event misses clients, it misses 2 (median), the same under Copa and BBR.

**Reading.** Copa makes no difference to grouping. With a single leaf this only shows that the true set is recovered; it cannot show anything about hierarchies.

## What these runs cannot tell us

- **No hierarchy.** M13 is a single leaf, so Copa under hierarchies (C7–C13) and under fq_codel or pie was not run.
- **Seeds and AQMs.** 2 seeds; pfifo and codel only.
- **Copa's behaviour.** Why the Copa video does not back off under pfifo overload is not measured. Neither is whether that changes with BG-BURSTY / BG-MIX background.
- **Rep disagreement.** The rep difference in Copa pfifo GT1 recall (0.86 / 1.00) has no known cause, so it is marked not reliable.
