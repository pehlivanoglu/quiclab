# Suite v3 campaign: scoring report (2026-11-15)

Campaign `.runs/2026-11-14_1818_v3`, 203 runs, 2 reps. Measurement only: existing scripts and functions called unchanged; the detector (frozen Shadow v2, ip4 values), ECG v1.2 and h3 not changed. GT1 / GT2 / GT3 are the yardstick; GT-Q / GT-H appear only in `reports/v3-detector/` and only where valid. Tables (reps side by side) are in this folder: `part0.md` … `part4.md`, `catalog-v3.md`, `rep-compare.md`, `run-checks.md`, `video-reaction.md`. Drivers: `score_v3.py`, `part0-4.py`.

## Summary first: the four predictions

| prediction | verdict | deciding numbers |
|---|---|---|
| keyframe peak at s 0.30 is a few ms; upstream no longer congested in most events | **partly held** | Upstream / root congested in **13–33 %** of ECG events at s 0.30 (C7 0.23–0.30, C9 root 0.13–0.18, C13 0.29–0.33), against 46–83 % in the old synchronized runs. The peak is a few ms only in runs with stimuli (5–11 ms in the calm time between them). In pure CALM runs it is 21–23 ms, as 0.121 s U − spread predicts. |
| h3 per-close precision returns to ~0.9 at s 0.30 | **held on two-level topologies; did not hold on T-TREE16** | h3 per-close P: H-HIER 0.84–0.96, H-UNEVEN 0.98–1.00, A-MIXED 1.00, L-LONG 0.86–0.88 (old C1 0.65–0.88), noroot 0.97–1.00. H-DEPTH 0.33–0.45. fq_codel 0.02–0.20. |
| ECG instability across reps remains and is worse on L-LONG | **held** | L-LONG final P 1.00 / 0.43 on both AQMs, tree no / no, siblings merged in r2. The truth onsets give the same result. H-DEPTH 1.00 / 0.33–0.60. Final values are stable on H-HIER, s 0.65, A-MIXED and noroot. |
| v2 is desensitised by the always-on background, more so at higher U; v2-fixed recovers recall at the cost of false alarms | **did not hold at U 0.7; U dependence cannot be decided** | GT3 overlap recall of v2 is ~1.00 in every stimulus cell. GT1 recall on ≥ 2 s episodes is 1.00 (except fq_codel / cake). v2's sensitivity does worsen with U (sustained queue for an alarm in 1 s: 4.3 / 7.8 / 13.7 ms at U 0.5 / 0.7 / 0.85, s 0.30), but stimuli exist only at U 0.7. v2-fixed adds no GT3 recall, costs up to 0.42 false alarms per client-minute in CALM under GT3 (1.7 under GT1) and fails under forward jitter. |
| (votes) bias inside one-leaf groups shrinks | **cannot be decided** | B2 own-vote rate in one-leaf groups is 0.55 (r1, 757 votes) / 0.47 (r2, 717), against 0.54 in Step 5. Per cell the reps disagree (C11 0.57 / 0.86, C12 0.83 / 0.34, C2 0.95 / 0.35): not reliable. |

## Rep against rep

- **Campaign headline:** the same in both reps.
  - Detector, all runs (`reports/v3-detector/report.md` 1c): GT3 R 0.92 / 0.93, FA 0.02 / 0.01 per min.
  - Calm load and share per egress differ by ≤ 0.007.
- **Flags** (rule: `*` when |r1 − r2| exceeds the largest rep difference of the other cells of the block):
  - 130 values in 54 rows of `part3.md`; 33 in 21 rows of `part4.md`; 32 in `rep-compare.md`.
  - Many are tiny where the other cells are identical (load 0.711 / 0.713).
  - The ones that matter, all **not reliable**, not used in a conclusion:
    - C2 pie GT3 recall;
    - C10 pfifo and C10 codel h3 per-close P (0.93 / 0.63, 0.98 / 0.74) and their share of closes with the correct tree;
    - C7 pfifo closes with correct tree (0.14 / 0.79);
    - every fq_codel cell's false-alarm rate;
    - every per-cell B2 rate.
- **Time to membership** is consistently longer in rep 1: C7 71 / 21 s, C13 138–191 / 34 s, C12 156 / 59–96 s. The cause is unknown: not reliable.
- **ECG final values:** their disagreement on L-LONG and H-DEPTH is the instability being tested, so it is reported, not used as a finding about anything else.

## Part 0: is the campaign valid — yes (`part0.md`)

1. **Gate:** PASS on all six checks. Load 0.669–0.713 against U; share 0.307–0.316 against s (legacy 1.008); ECN 0; oversize skb 0; lost events 0; unmatched packets on targets 0–2; backlogged gaps within max(10 %, 15 µs) ≥ 0.998; 20 ms windows 1.000; CPU idle ≥ 0.787; non-video − planned ≤ 0.014; phase-lock ratio ≤ 5.4 (limit 10).
2. **Runs:** 203 / 203 completed, 0 failed, 0 retried, nothing dropped.
   - 19.50 h emulated.
   - Wall clock 2026-11-14 18:18 → 2026-11-15 16:24. That includes the stop after the first gate failure (check 5, before the rule change) until the resume.
   - GT-Q invalid by the health file: 2 runs (C13 pfifo r1, M8 r1: one missing record each).
3. **Load and share:**
   - Core load − U: median +0.010, range −0.010 … +0.028. Share − s: +0.009, range −0.008 … +0.016. No core run off target.
   - Off target (kept): M3 BG-BURSTY load 0.65 (PPBP mean not reached within a run) and M11 bw4x1 r1 load 0.73.
   - Stimulus intensity (non-video at the target − planned): every core block within ±0.035. M3 is variable by design; M9 has 4 windows of 0.2 s; M11 has 1 window.
4. **Worst cases:**
   - ECN marks 0 and no AQM leaf with `ecn`; oversize skb 0; offloads all off.
   - CPU idle 0.694 (C9 fq_codel r1).
   - Inter-dequeue: worst target 0.78 within tolerance and 20 ms windows 0.001, both on C12 access egresses during capacity drops (~0.8 Mb/s, 1–2 packets per window: resolution, not service).
   - Unmatched packets ≤ 2; lost events 0.
5. **Deviations and decisions made on your behalf:** below (§ Deviations).
6. **Isolation and optional features:**
   - Every fq_codel / cake stimulus cell has GT3 episodes. The fewest are C2 cake (5 in both reps) and C6 fq_codel (13).
   - **Background in pinned classes:** 1.0 % of unpinned fq_codel dequeues land in a pinned client class (941 k of 96.7 M, 74 egresses verifiable; 23 have no skb hash): FLAG.
   - Copa (M13), I/P ratio 2 / 8 (M10) and S-JOIN (C6) all ran.

No block is unusable. fq_codel and cake grouping cells are scored, but they say little (§ Part 4).

## Part 1: standard outputs (spec 7)

- **Catalog for v3:** `catalog-v3.md`.
  - Measured calm load and share per egress for every run, reps side by side, via `scenario_catalog.calm_load`.
  - Stimulus-window loads.
  - Sizing in `plan-v3.md`.
- **Keyframe table:** `part2.md`. **Health summary:** `run-checks.md`, `part0.md`. **Rep 1 against rep 2:** `rep-compare.md`, plus the per-cell flags in parts 3 and 4.

## Part 2: keyframe queue (`part2.md`)

- **T-BASE CALM:** peak p50 follows 0.121 s U minus the keyframe pacing spread (3–5 ms in CALM).

  | s | U | peak p50 (ms) | 0.121 s U − spread (ms) |
  |---|---|---|---|
  | 0.10 | 0.70 / 0.85 | 5.9–6.3 / 8.5–9.1 | 4.9–5.0 / 6.3–6.8 |
  | 0.30 | 0.50 / 0.70 / 0.85 | 13.2–14.5 / 21.2–23.2 / 27.5–28.3 | 14.3–15.2 / 21.2–21.6 / 26.9–27.1 |
  | 0.65 (codel) | 0.50 / 0.70 / 0.85 | 32.5–35.7 / 48.5–52.0 / 53.7–59.2 | 35.3 / 51.4 / 60.1 |
  | legacy | | 46–47 (pfifo) / 69–72 (codel) | 57.8 / 73.6 |

  - At s 0.65, U ≥ 0.7 under pfifo, the peak is capped near 42 ms by the 50 ms limit; drops raise the spread to 14–64 ms.
- **Runs with stimuli, calm time between stimuli:** BBR's pacing rate stays lower after a stimulus. The keyframe spread grows to 26–40 ms and the peak falls:
  - s 0.30: C2 7.9–8.5 ms; C7 leaves 5.1–5.6, up 8.6–8.8; C9 leaves 5.1–5.5, X / Y 6.0–6.4, root 10.6–11.1.
  - s 0.10: 1.5–1.8 ms. s 0.65: 22.9–24.4 (C3a), up 24.7–25.3 (C8).
  - Staggered phases (M6): 1.8–3.8 ms.
- **Hierarchies:** the peak forms at the top level.
  - CALM: split up 20.8–22.7 vs leaves 10.7–11.5; tree root 21.1–21.5, X / Y 10.8–12.0, leaves 6.4–7.4.
  - With an unshaped upstream (T-UNEVEN, M7) the leaves carry it: 21–22 ms in CALM.
- **Upstream / root congested (gt1 rule) in ECG events, v2-owd onsets:**

  | topology / cell | s | share of ECG events |
  |---|---|---|
  | H-HIER (C7) | 0.30 | 0.23–0.30 |
  | L-LONG (C13) | 0.30 | 0.29–0.33 |
  | H-DEPTH (C9) root / X / Y | 0.30 | 0.13–0.18 / 0.11–0.15 |
  | H-INDEP (C10) | 0.30 | 0.50–0.59 (up is one of the three targets) |
  | M8 mixab | 0.30 | 0.21–0.23 |
  | H-HIER (C8) | 0.65 | 0.37–0.43 |
  | old synchronized K1 / C1 / K6 root | old | 0.46–0.73 / 0.53–0.83 / 0.57–0.74 |

## Part 3: detector (`part3.md`; v2-owd = "v2" there, v2-fixed-owd = "fixed")

Truth here as `ppbp.py` builds it: GT1, and GT3 from **source A**. Source A shares the ACK timestamps with the OWD mode (FLAG). Source B headline for all runs, from `reports/v3-detector`: P 1.00, R 0.93, alarm-on 0.98.

**a. Scores (v2):**
- **GT3:**
  - Overlap recall 1.00 in almost every stimulus cell (minimum 0.92, C14 fq_codel r1); recall on ≥ 2 s episodes 1.00; harmful episodes 1.00.
  - Precision ≥ 0.98, except fq_codel cells (0.77–0.98), cake (0) and C6 fq_codel.
- **CALM false alarms per client-minute:** 0.000 in every C1a / C1b row, except legacy codel r2 (0.105) and s065u085 pfifo r1 (0.211*).
- **GT1:** overlap recall lower where GT1 counts short keyframe or ramp queues:
  - s 0.65: 0.60–0.72 (C3a), 0.53–0.55 (C8);
  - legacy: 0.42–0.46;
  - ramp: 0.57–0.79;
  - fq_codel: 0.44–0.88.

  On ≥ 2 s episodes GT1 recall is 1.00, except fq_codel / cake.

**b. Learned baseline (v2):** the F1 level needed to alarm within 1 s grows with s and U. Background mode changes nothing.

| s | U | above queue-free (ms) | σ_F1 (ms) | sens 1 s (ms) |
|---|---|---|---|---|
| 0.10 | 0.70 / 0.85 | 0.9–1.0 / 1.5–1.6 | 0.8 / 1.4–1.5 | 2.1–2.3 / 3.8–3.9 |
| 0.30 | 0.50 / 0.70 / 0.85 | 2.1–2.2 / 3.7–4.0 / 5.9–6.1 | 1.1–1.3 / 2.5–2.7 / 5.0–5.3 | 4.1–4.5 / 7.7–8.0 / 13.4–14.0 |
| 0.65 | 0.50 / 0.70 / 0.85 | 5.3–5.7 / 7.6–9.5 / 9.6–14.7 | 3.6–3.9 / 6.0–7.6 / 7.8–13.8 | 10.8–12.2 / 16.9–21.1 / 22.2–36.0 |
| legacy | 0.65 | 10.8–12.9 | 8.5–11.4 | 24.0–30.0 |
| BG-BURSTY / BG-MIX vs CBR (S-BURST) | 0.70 | 2.4–2.8 vs 2.5–2.7 | | 6.1–7.2 vs 6.1–7.0 |

The ppbp diagnosis needed 43–73 ms on ppbp, so v3's background does not contaminate the baseline that way.

**c. v2-fixed side by side:**
- GT3 recall the same as v2.
- GT1 recall 0–0.25 higher on short episodes (CALM legacy 0.54 vs 0.04–0.07, fq_codel cells), but more false alarms per client-minute:
  - under GT3 in CALM: legacy pfifo 0.21 / 0.32, legacy codel 0.42 / 0.42, s065u070 pfifo 0.42*, tree16 0.12* (v2: 0 in these cells, except legacy codel r2 0.105);
  - under GT1: legacy codel 1.05 / 1.68, M11 bw4x1 0.88 / 0.85.
- Under forward access jitter (M12): GT3 overlap recall 0.50 / 0.71 (v2: 1.00).

**d. By stimulus (share of expected clients alarming, `reports/v3-detector/stim-pivot.md`, `part3.md` 3d):**

| stimulus | pfifo / codel / RED | PIE | fq_codel | cake |
|---|---|---|---|---|
| surge, u 1.05 / 1.15 / 1.3 | 1.00 / 1.00 / 1.00 | 0.97 | 0.75–1.00 | 0 (video untouched, 0.98–1.01 of calm) |
| ramp | 1.00 | 1.00 | 0.78 | |
| tcp | 1.00 | 1.00 | 0.50 (the video stays below its fair share) | |
| join (ASV) | pfifo 0.91 / codel 0.78 | | 0.22 | |
| capdrop (M2, C12 access) | 1.00 | 1.00 | 1.00 | |

- BG-CBR vs BG-BURSTY vs BG-MIX surges: 1.00 / 1.00 / 1.00 (pfifo, codel).
- v2-fixed matches these numbers except under jitter.

## Part 4: grouping (`part4.md`; ECG v1.2 δ 0.150 s and h3, onsets v2-owd / v2-fixed-owd / truth)

**a / b. v2-owd onsets:**
- **Two-level topologies are solved and stable.** H-HIER s 0.30 (pfifo, codel, PIE), s 0.65 (C8), H-UNEVEN pfifo, A-MIXED (all AQMs except fq_codel), noroot (M7):
  - ECG final P / R 1.00 / 1.00 and the tree correct in both reps;
  - per-close P 1.00 (r2 of C11 0.82);
  - no sibling merge;
  - 0 false memberships by the same-leaf truth.
- **The share of closes with the correct tree varies between reps** (C7 pfifo 0.14 / 0.79*, C10 pfifo 0.91 / 0.27*). Losses and regains are equal in number, so memberships flap and come back.
- **T-TREE16 (H-DEPTH) fails:**
  - ECG final P 1.00 / 0.33 (pfifo) and 1.00 / 0.60 (codel); tree yes / no; siblings merged in r2;
  - closes with the correct tree 0.00–0.02;
  - ECG false memberships 5 / 43 (pfifo) and 13 / 32 (codel); 5 / 25 and 13 / 16 by the strict per-event truth;
  - h3 per-close P 0.33–0.45.
- **L-LONG:** ECG final P 1.00 / 0.43, tree no / no, siblings merged in r2; h3 per-close P 0.86–0.88.
- **H-INDEP:** ECG final 1.00 / 1.00, but per-close P 1.00 / 0.52–0.53 and h3 per-close P 0.93 / 0.63* (not reliable).
- **fq_codel:** no correct tree in any hierarchy; coverage 0.17–0.58; h3 per-close P 0.02–0.20. Flows behind one leaf are rarely constrained together.
- **Time to membership:** 2–6 events, 12–227 s (p50), rep 1 longer (see Rep against rep).
- **Truth onsets give the same picture:** two-level solved; C9 1.00 / 0.60, closes correct 0.06 / 0.00; C13 1.00 / 0.43; fq_codel coverage 0.17. The failures on T-TREE16 and L-LONG and the instability are not caused by detection.
- **v2-fixed onsets:** the same, with more failures (C8 tree no / yes; C9 1.00 / 0.20*; C11 pfifo tree no / yes).

**c. Step 5 votes (v2-owd):**
- **B1** own-vote rate is ~1.00 whenever a leaf egress is congested (O--, -X-, OX-, -XU, O-U). It is 0.26–0.71 when only a shared upstream is congested (--U), which is close to a coin.
- **B2** in one-leaf groups: 0.55 / 0.47 pooled (Step 5: 0.54); per cell not reliable.

**d.** L-LONG and H-INDEP: see a / b. **e.** s 0.65 (C8) is as good as s 0.30 for ECG. Staggered phases (M6, single leaf) and noroot (M7) are solved: final 1.00, closes with the correct tree 0.83–0.94.

## Part 5: harm onset, GT-Q time coverage, fq_codel GT-H (`harm.md`, driver `harm.py`)

These numbers use GT-Q / GT-H, on the 201 runs whose health file says GT-Q is valid. They are a separate column, not the yardstick. Detector: v2-owd (v2-fixed-owd in `harm.md`, which gives the same picture). Values are rep 1 / rep 2.

**a. Alarm at harm onset.** For each GT-H 600 harmful episode, t_harm is the first missed 600 ms deadline (gtq.py).

| AQM | harmful | span overlaps episode (the "99 %") | start in collar (= GT-H recall) | on at t_harm | on, opened in this collar | on, held from earlier | off at t_harm | lead p50 s (p10–p90) |
|---|---|---|---|---|---|---|---|---|
| pfifo | 3735 / 3718 | 1.00 / 1.00 | 0.77 / 0.79 | 1.00 / 1.00 | 0.77 / 0.79 | 0.23 / 0.21 | 0.00 / 0.00 | 1.30 / 1.29 (0.6–6.8) |
| codel | 2797 / 2627 | 1.00 / 1.00 | 0.66 / 0.72 | 1.00 / 1.00 | 0.66 / 0.72 | 0.34 / 0.28 | 0.00 / 0.00 | 1.59 / 1.49 (0.8–6.4) |
| fq_codel | 2773 / 2889 | 0.96 / 0.97 | 0.21 / 0.19 | 0.98 / 0.99 | 0.20 / 0.19 | 0.78 / 0.80 | 0.02 / 0.01 | 3.85 / 4.04 (0.6–9.1) |
| pie | 698 / 671 | 1.00 / 0.99 | 0.52 / 0.52 | 1.00 / 0.99 | 0.52 / 0.52 | 0.48 / 0.47 | 0.00 / 0.01 | 1.35 / 1.30 (0.8–6.2) |
| all | 10038 / 10420 | 0.99 / 0.99 | 0.57 / 0.58 | 0.99 / 1.00 | 0.57 / 0.58 | 0.43 / 0.42 | 0.01 / 0.00 | 1.76 / 1.74 (0.7–8.0) |

The two report figures count different things. They do not contradict each other.
- **"99 %"** (`gth-alarm-on.md`) counts episodes where an alarm span overlaps [t0, t1] at any time. On at t_harm gives the same number: 0.99 / 1.00.
- **"0.57"** is gtq_score's GT-H recall: a new alarm **start** inside the episode's collar.
  - The "alarm before harm" column (0.56 / 0.57) adds one more condition: that first start must come before t_harm. It almost never fails, so the two figures are nearly equal.
  - The name "alarm before harm" is misleading. The 0.43 gap is not alarms that came after harm. It is alarms that were already on at harm but had opened before this episode's collar, during an earlier episode.
- **Lead time.** When the alarm is on at harm, it opened 1.7 s before t_harm (median), and never less than 0.2 s before.
  - Part of the lead is built in: t_harm is a deadline 600 ms after the frame was generated.
- **Comparison.** The alarm is on for only 0.25–0.31 of the flow time (0.13–0.14 under fq_codel; table b). If alarm-on time were unrelated to harm, it would be on at harm onset about that often. That figure is a rough bound only: harm clusters in stimulus periods.
- **Baseline for "on at t_harm"** (`harm.md` §D, asked after §a was seen). The detector's alarm-on share of time is 0.25–0.28 overall and 0.13–0.14 under fq_codel. Two baselines:
  - **Shift test.** Each flow keeps its own alarm spans; the harm instants are moved by a random circular offset (20 per flow, M). Result: 0.31–0.33 overall, 0.32–0.34 under fq_codel, against 0.99–1.00 / 0.98–0.99 observed.
  - **Queue-only alarm.** An alarm that is on exactly while a GT-Q queue exists, sampled at a random instant inside it. It is on in 0.79–0.82 of queue time for pfifo / codel / pie, and 0.16–0.18 for fq_codel.
  - Under pfifo / codel / pie, "on at harm" (1.00) is only modestly above "on while queued" (0.8). The sharp contrast is with time in general.
  - Under fq_codel the alarm is off for most queue time (0.16–0.18) yet on at 0.98–0.99 of harm onsets. So the 4.3 s holds are not an always-on alarm.
- **Definitions.** "On at harm onset" replaces "start in collar" after the results were seen. Both must be reported, together with why the definition changed.
- **Real misses** (off at t_harm): 105 of 20 458 episodes. About half of them get a late start inside the collar, with the median start 0.5–0.9 s after t_harm.

**b. GT-Q time coverage, and what precision a random alarm would get.**

Time is flow time after warm-up, with sub-ctrl excluded. A random alarm is placed uniformly in time and scored with the gtq_score rule: in a collar = TP, in gray only = ignored, else FP. Its precision = collar time / (time − gray outside collars). The alarm-weighted version spreads the detector's own per-flow alarm count at random over that flow's time.

| runs | AQM | GT-Q episode share of time | collar share | random precision (uniform) | random precision (alarm-weighted) | v2-owd precision | v2-owd on-share of time | episodes / flow-min |
|---|---|---|---|---|---|---|---|---|
| calm | pfifo / codel | 0.08 / 0.11 | 0.21 / 0.22 | 0.21 / 0.23 | 0.32–0.37 / 0.44–0.50 | 1.00 / 0.96–1.00 | 0.00 / 0.00–0.01 | 75–84 / 50 |
| stimulus | pfifo | 0.31 / 0.31 | 0.40 / 0.40 | 0.41 / 0.41 | 0.42 / 0.42 | 0.99 / 1.00 | 0.30 / 0.31 | 56.5 / 54.8 |
| stimulus | codel | 0.31 / 0.31 | 0.41 / 0.41 | 0.41 / 0.41 | 0.42 / 0.42 | 1.00 / 1.00 | 0.30 / 0.30 | 62.5 / 60.8 |
| stimulus | fq_codel | 0.56 / 0.57 | 0.74 / 0.76 | **0.82 / 0.83** | 0.78 / 0.80 | **0.98 / 0.98** | 0.14 / 0.13 | 108.7 / 112.5 |
| stimulus | pie | 0.32 / 0.32 | 0.41 / 0.42 | 0.42 / 0.42 | 0.42 / 0.43 | 0.98 / 1.00 | 0.31 / 0.32 | 62.9 / 61.6 |
| all | all | 0.33 / 0.34 | 0.44 / 0.45 | **0.45 / 0.46** | 0.46 / 0.46 | **0.99 / 1.00** | 0.25 / 0.26 | 68.8 / 66.9 |

- **Coverage.** GT-Q episodes cover a third of flow time. With collars, the share is 0.44; under fq_codel it is 0.74–0.76.
- **The baseline is not free 0.99.**
  - Overall, a random alarm would score 0.45–0.46 and the detector scores 0.99–1.00.
  - Under pfifo / codel / pie the ratio is the same: 0.41–0.43 against 0.98–1.00.
- **fq_codel** is where the baseline is weakest: 0.82–0.83 random against 0.98. There the headline precision says little.
- **Calm runs.** The detector precision rests on very few alarms (on-share ≈ 0), so it carries little weight.
- **v2-fixed-owd:** 0.98 overall, 0.95 under fq_codel, 0.77–0.91 calm, against the same baselines.

**c. fq_codel GT-H recall 0.20.** The low figure comes mostly from the counting rule; the detector is not missing these episodes.
- **Alarm on at harm onset.** In 0.98–0.99 of harmful fq_codel episodes the alarm is on at t_harm. 0.78–0.80 are held from an alarm that started in an earlier episode's collar.
  - Median gap from that earlier episode's end to this t0: 2.6–2.8 s.
  - Median time the alarm was held before t0: 4.3 s.
  - Median episode length: 0.38 s.
- **Fragmentation.** fq_codel cuts one queue period into many GT-Q episodes: 109–113 per flow-minute, against 55–63 for the other AQMs.
- **Merged-event recall.** Same flow, gap < G (M), and an alarm start counts if it lands in the merged collar:

  | AQM | per episode | G 0.5 s | G 1 s | G 2 s |
  |---|---|---|---|---|
  | fq_codel | 0.21 / 0.19 | 0.71 / 0.71 | 0.81 / 0.80 | 0.92 / 0.95 |
  | pfifo | 0.77 / 0.79 | 0.82 / 0.84 | 0.93 / 0.92 | 0.98 / 0.95 |
  | all | 0.57 / 0.58 | 0.77 / 0.80 | 0.90 / 0.89 | 0.96 / 0.94 |

  - The merged events are long (episodes per merged event at G 1 s: about 27–31 for fq_codel and about 21 overall). So this measures "an alarm start somewhere in the queue period". It is not an alternative headline; G is not chosen.
- **Real fq_codel misses** (off at t_harm): 55 / 30 episodes (0.02 / 0.01). About 0.55–0.63 of them get a late start inside the collar.
- **Caveat on held alarms.** The test above only shows that the alarm was open at harm onset. Whether the held alarm "belongs" to the same queue or to an earlier one is a judgement on the hold rule, and this measurement cannot settle it.

## What these runs cannot tell us

- How recall depends on U: every stimulus runs at U 0.7. Higher U was tested only in CALM, where only sensitivity is measured.
- Why ECG is unstable on L-LONG and T-TREE16: the truth onsets fail the same way, so the cause is in the engine or the event structure, and no analysis of it was asked for.
- Grouping under fq_codel / cake: the clients of one leaf are rarely constrained together, so pairs are seldom decided.
- Whether the old-campaign comparisons are like-for-like: different topologies, s, U and onset detector.
- Held-out N1–N5 (not run); generalisation beyond 2 reps; the 1 % of background in pinned fq_codel classes (FLAG).

## Deviations (this scoring) and decisions made on your behalf

1. The scenario catalog script reads only the old campaign folders. Its `calm_load` was called per v3 run (`catalog-v3.md`), not the whole script (T).
2. Step 5 / 6 / 7 read ECG output from the fixed dir `grouping-d150-v2-owd`. For the other two sources they ran on view folders (symlinks; that dir points at the source's output). No script was changed.
3. Part 3 uses `ppbp.run_row` as written: GT3 source A (FLAG: shares ACK timestamps with OWD). The source-B headline is quoted from `reports/v3-detector`.
4. Grouping set (T): every H-* block, A-MIXED, L-LONG, M6, M7, M8, plus C2 pfifo as M6's default point. Truth onsets do not exist on CALM (M6 calm): skipped.
5. Step 2's event classes are named from the old campaign names. On v3 they come out generic ("single group", "two groups…"); naming only.
6. "False memberships, strict per-event" = wrong by same-leaf minus those sharing a strictly congested egress (step 7 strict rule, half the members: FLAG as in step 7). Seconds to membership: from a flow's first event to its first close with L ≥ A (M).
7. Rep-disagreement flag rule as in earlier reports (largest difference of the other cells of the block). It flags small differences when the other cells are identical.
8. Campaign decisions taken during the build (u = stimulus intensity; gate checks 4a / 4b / 5 as revised; noecn; pub link 1000 Mb/s; raw tracepoints; 15 µs floor): listed in `reports/v3-suite/README.md` §5 and `docs/paper-notes-ground-truth.md` §9.
