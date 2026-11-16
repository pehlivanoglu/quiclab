# Step 6 (2026-11-14): grouping on synchronized keyframes

Analysis only. GT1, the detector and the ECG engine are not changed; truth is gt1 only (the
new GT-Q / GT-H truths are not used).

Code: `step6.py` (rows) and `summarize.py` (tables). Both call the existing
`grouping_step2/3/4/5`, `grouping_adapter`, `keyframe_spread` and `det_eval` functions
without changing them. `ecg-rows-night.jsonl` is ECG v1.2 (`baseline_scores.ecg_row`) on the 7
overnight P1 / P2 runs only; P3–P7 are not scored. Tables: `step6-summary.md`. Rows:
`step6-rows.jsonl`.

Runs (pfifo):
- sync: `.runs/2026-11-13_2238_ip4-sync-keyframes-oldGT` (calm065, burstcap, K1, C1, K6;
  r1 r2) and `.runs/2026-11-14_0240_night-sync` (K6, C1 r3 r4);
- stag: `.runs/ip4-not-sync-keyframes-oldGT` r1 and `.runs/2026-11-14_0240_night-stag` (K1,
  K6, C1 r2).

The two older folders were renamed by the user; they are the former `_grp-sync` and
`2026-11-10_1946_v2`.

Constants:
- per-event truth = a GT1 episode of the egress overlaps the ECG event interval (t0 − 1 s,
  t0 + 2 s) (FLAG);
- shared membership = a congested egress shared with at least half of the other members
  (FLAG);
- KEY_FRAC 4/33 (P);
- PEAK_S 0.5 s (FLAG);
- calm time = outside stimulus windows ± 1 s (FLAG).

## Overnight usability

All 35 runs finished in pass 1 (02:40 → 11:33); none was retried. Every run has:
- 0 event errors and no missing sender files;
- OWD files to the end of the run;
- keyframe spread scheduled p50 ≤ 1.3 ms, max ≤ 2 ms on sync runs; staggered 750 / 800 ms.

Windows not hit: K1 pie r2 98 / 99, M6 indepfast r1 127 / 130, r2 120 / 122 (the same order as
earlier campaigns). K6R planned root load 0.325; the realised load is not measured yet (P3 not
scored). Full table: `night-usability.md`.

## Rep against rep

| result | reps | stable? | cause of the spread |
|---|---|---|---|
| h3 collapses on K6 sync (pooled P) | 0.44 / 0.35 / 0.38 / 0.46 vs stag 0.97 / 0.88 | **stable** (direction and size) | – |
| h3 final P on K6 sync | 0.67 / 0.36 / 0.25 / 0.50 | value unstable, always far below stag 1.00 | a snapshot of a state that keeps changing (many groups, splits); direction stable, value **not reliable** |
| h3 worse on C1 sync (pooled P) | 0.65 / 0.75 / 0.69 / 0.70 vs stag 0.98 / 0.90 | **stable** | – |
| h3 on K1 | 0.93 / 0.93 vs stag 0.94 / 0.99 | stable, small difference | – |
| item 1, h3 wrong pairs shared in that event | K1 0.76 / 0.81, C1 0.80 / 0.85 / 0.79 / 1.00, K6 0.74 / 0.76 / 0.82 / 0.76 | **stable** | – |
| item 1, ECG wrong pairs shared | K1 0.10 / 0.69, C1 – / 0.70 / 0.48 / –, K6 0.71 / 0.81 / – / 0.79 | **unstable** | ECG's wrong SAME pairs are few and transient (0–313 pair-closes); the share depends on which events happen to close while the transient merge lasts: **not reliable** |
| ECG final coverage, C1 | 0.05 / 0.48 / 0.71 / 0.48 (stag 0.48 / 0.48) | unstable | **cause found:** ECG membership L sits near A = 4.55 and is eroded by late SOLO / GLOBAL events. C1 r1: the a-leaf node is unconfirmed, a1–a3 at L 3.3 / 2.5 / 1.1, b3 2.2. Coverage over closes swings 0.05–0.71 in sync **and** stag (stag C1 0.29–0.71). A method property, not phase-specific: the final value is not a headline |
| ECG final coverage / tree, K6 | 0.42 no / 0.78 ok / 0.78 ok / 0.58 no (stag 0.78 / 0.78) | unstable | **cause found:** r1 d1, d2 at L 1.5 (not members); r1 an internal node joins a and c (they share only the root); r4 a2 at L 1.5. Threshold erosion as in C1 plus cross-branch internal nodes |
| ECG final precision | 1.00 except C1 sync r3 0.40 and K6 **stag** r2 0.50 | unstable | **cause found:** sibling leaves merged into one ECG leaf (C1 r3: a + b, last third mostly case C; K6 stag r2: c + d under r2). Happens in both phases; its frequency is **not reliable** |
| item 2 GLOBAL share | K1 0.20 / 0.24 vs 0.21 / 0.15; C1 0.17 / 0.05 / 0.00 / 0.18 vs 0.14 / 0.05; K6 0.07–0.10 vs 0.06 / 0.08 | stable in that there is no sync increase | – |
| item 3 recall drop after subtraction | K1 0.48 / 0.45, C1 0.76 / 0.67 / 0.83 / 0.87, K6 0.64 / 0.72 / 0.68 / 0.61 | **stable** | – |
| item 4 peaks | within 1–2 ms across r1–r4 per queue | **stable** | – |

No run looks broken. All are complete. The unstable values have mechanisms visible in
the ECG state, not in transport or run artefacts.

## Item 1: errors shared in that event

h3, wrong pair-closes / shared in that event / not; memberships wrong at declaration /
shared / not:

| scenario | sync reps | stag reps |
|---|---|---|
| K1 | 63 / 48 / 15, 48 / 39 / 9; mem 12 / 12 / 0, 10 / 4 / 6 | 52 / 26 / 26, 3 / 3 / 0; mem 11 / 10 / 1, 1 / 1 / 0 |
| C1 | 124 / 99 / 25, 117 / 99 / 18, 100 / 79 / 21, 94 / 94 / 0; mem 14 / 14 / 0, 13 / 13 / 0, 13 / 13 / 0, 17 / 17 / 0 | 6 / 3 / 3, 24 / 15 / 9; mem 1 / 1 / 0, 4 / 4 / 0 |
| K6 | 672 / 496 / 176, 849 / 644 / 205, 792 / 652 / 140, 621 / 471 / 150; mem 72 / 53 / 19, 71 / 49 / 22, 53 / 47 / 6, 78 / 60 / 18 | 16 / 14 / 2, 77 / 43 / 34; mem 7 / 7 / 0, 23 / 14 / 9 |

- h3 makes 5–10× more same-leaf errors with synchronized keyframes.
- 74–100 % of its wrong pair-closes are clients that shared a congested egress in that
  very event, and 66–100 % of its wrong memberships (K6 22–34 % not shared).
- By the reading rule the h3 errors are mostly a truth artefact: the clients do share a
  congested queue in that event. On K6 the rest (19–26 % of pair-closes) are not.
- ECG has few wrong pair-closes (0–313, mostly transient); its shared share is not
  reliable (see above).

## Item 2: ECG cases

- ECG events do **not** turn GLOBAL. The GLOBAL share is the same in sync and stag (K1
  0.20–0.24 vs 0.15–0.21, C1 0.00–0.18 vs 0.05–0.14, K6 0.07–0.10 vs 0.06–0.08), and the
  event counts are the same order.
- What changes is that the upstream / root egress is congested in many more ECG events:
  - K1 r1->r2: 0.46 / 0.60 vs 0.20 / 0.25;
  - C1: 0.53–0.70 vs 0.29 / 0.33;
  - K6 root: 0.57–0.74 vs 0.09 / 0.11.
- The coverage drops are not GLOBAL events. They come from member evidence L hovering
  around A and being eroded late in the run, and from cross-branch internal nodes (K6 r1).
  The same swing happens in stag.
- So the reading "ECG loses evidence because the root is always in the picture" is
  **not** supported. The root is in the picture far more often, but ECG's event cases
  barely change.

## Item 3: subtracting the common component (sync)

| | precision / recall of the congested set vs the leaf truth, before → after | exact match before → after | B1 own, upstream only (--U), before → after |
|---|---|---|---|
| K1 r1, r2 | 0.78 / 1.00 → 0.81 / 0.48; 0.77 / 1.00 → 0.71 / 0.45 | 0.64 → 0.20; 0.62 → 0.17 | 0.50 → no votes; 0.62 → no votes |
| C1 r1–r4 | P 0.49–0.63 → 0.62–0.72; R 0.99–1.00 → 0.67–0.87 | 0.27–0.45 → 0.27–0.32 | 0.13–0.36 → no votes |
| K6 r1–r4 | P 0.39–0.48 → 0.42–0.49; R 0.97–1.00 → 0.61–0.72 | 0.06–0.10 → 0.05–0.15 | 0.57–0.71 → 0.52–0.74 |

B1 with a leaf queue congested stays 0.97–1.00 before and after.

After the subtraction the congested set does **not** match the leaf truth. What remains:

1. **The median removes leaf congestion too.** Where most participants are behind a
   congested leaf, the median is that congestion (K1: leaf truth p50 6 of 7 participants;
   both leaves have GT1 episodes in ~80 % of the 3 s ECG intervals). That is why recall
   halves in K1.
2. **On K6, non-leaf clients still look congested** after the subtraction (precision
   0.42–0.49). The root spike is not the same curve for every client, so the median does
   not cancel it.

Not measured: why the root spike differs per client. Candidates are per-client pacing (see
item 4) and FIFO position.

## Item 4: keyframe queue size

Load = transmitted / capacity in calm time, 0.67–0.68 on every queue; model load × 4/33 s =
81–83 ms. Peaks per rep (p50; p90 in the summary):

| queue | sync | stag | sync / model |
|---|---|---|---|
| base router->switch (25 ms samples) | 53.2, 51.6 | 14.2 | 0.64–0.66 |
| K1 upstream r1->r2 | 36.8, 36.9 | 4.1, 3.9 | 0.45 |
| K1 leaves | 6.8–7.0 | 7.5–8.0 | 0.08 |
| K6 root rr->r0 | 28.2, 27.4, 28.1, 28.7 | 9.8, 9.0 | 0.33–0.35 |
| K6 r0->r1 / r0->r2 / leaves | 6.5–9.5 | 4.3–17.6 | 0.08–0.12 |

**Hand-over.** The application writes each frame whole as soon as it is due (no spreading
by the app). QUIC paces each connection (`pacingEnabled`, BBR pacing rate). Measured
transmit time of one keyframe, from the first packet after the write until its bytes have
left:

| | keyframe transmit time p50 | pacing rate p50 |
|---|---|---|
| K1 | 28–48 ms | 2.6–12.4 Mb/s, ~2.4× the client's rate |
| K6 | 37–56 ms | |
| base calm065 | 3–10 ms | 32–73 Mb/s |

Why BBR's estimate is so much higher on the base topology was not checked.

**Peaks follow load × 0.12 s minus the pacing spread:**
- K1 upstream: 82 − ~45 ≈ 37 ms, measured 37 ms;
- K6 root: 82 − ~50 ≈ 32 ms, measured 28 ms;
- base: 81 − ~6 ≈ 75 ms, measured 53 ms. The 25 ms sampling of the base CSV misses the
  top of a ~20–50 ms spike, so this is a lower bound.

Queues below a congested upstream see almost nothing (leaves 7–9 ms): the upstream queue
already serialises the keyframes, and each leaf receives its share at no more than the
upstream rate.

All loads here are ~0.67, so the scaling with load is not tested by these runs. The
overnight K6R (root load 0.33) is the test; not scored yet. The number of clients does not
enter: same load and peak with 4 (base), 6 (K1) and 8 (K6) clients, apart from the pacing
difference.

## What these runs cannot tell us

- One AQM (pfifo). The overnight codel / pie runs are not scored yet.
- 2 reps (4 for K6 / C1 sync), 2 staggered reps. Several ECG headline values swing between
  reps for method reasons. Their frequencies (sibling-leaf merges, coverage at the end of
  the run) need many more reps.
- One load level (~0.67): item 4's load scaling is untested until K6R is scored.
- The per-event truth uses GT1 episodes overlapping a 3 s interval. A 5 ms / 150 ms
  standing queue anywhere in the interval counts, so "shared in that event" is generous;
  no stricter variant was computed.
- Item 3 is one subtraction (the median over all participants). It says what that
  subtraction removes, not whether another decomposition would work.
- Base topology has 25 ms router samples: its keyframe peaks are lower bounds.
