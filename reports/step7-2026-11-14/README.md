# Step 7 (2026-11-14): overnight P3–P7 and ECG instability

Measurement only, grouping only. GT1, the detector and the ECG engine are not changed; gt1 is
the only truth (no GT-Q / GT-H).

Code:
- `step7.py`: Part A rows (`a-rows.jsonl`, 57 runs) and Part B rows (`b-rows.jsonl`, 251 runs
  with ECG output). It reuses the Step 6 helpers and the existing scripts' functions.
- `summarize7.py`: the tables in `step7-summary.md`.
- `ecg-rows-p3p7.jsonl`: ECG v1.2 (`baseline_scores.ecg_row`) on the 28 overnight P3–P7 runs.

Event intervals are ECG's (t0 − 1 s, t0 + 2 s).

New constants:
- strict per-event truth: an egress counts as congested in an event only if its GT1 episodes
  cover at least half of the interval (FLAG, brief A4);
- spike duration: time with delay >= 5 ms in [T, T + 0.5 s] after a keyframe (FLAG: GT1's
  target);
- Part B leaf-partition correctness per close (FLAG): ECG's per-close output has no internal
  nodes, so only the leaf partition is checked.

Folders:
- `.runs/2026-11-13_2238_ip4-sync-keyframes-oldGT` (mini, sync);
- `.runs/2026-11-14_0240_night-sync` and `.runs/2026-11-14_0240_night-stag`;
- `.runs/ip4-not-sync-keyframes-oldGT` (old, staggered, 1 rep except J1).

## Rep against rep

| result | values across reps | stable? |
|---|---|---|
| h3 pooled P collapses on K6 (any AQM, K6R) | pfifo 0.35–0.46 (4 reps), codel 0.37 / 0.40, pie 0.36 / 0.37, K6R 0.35 / 0.38; stag 0.97 / 0.88 | **stable** |
| h3 pooled P on C1 sync | pfifo 0.65–0.75, codel 0.88 / 0.67, pie 0.83 / 0.88; stag 0.98 / 0.90 | lower than stag in every rep; the codel / pie values are spread (**value not reliable**) |
| h3 on K1, J1, M6 | K1 0.84–0.93, J1 0.83 / 0.87, M6 indepfast 0.92 / 0.96 | stable, except **M6 indepslow 0.51 / 0.93**: not reliable, cause not checked |
| keyframe peaks, spike duration, drops | within ~2 ms / 25 ms per queue across reps | **stable** |
| A4 shared share, strict truth | K6 0.10–0.20 (all reps and AQMs), K1 0.31–0.58, C1 0.41–0.69 | K6 **stable**; K1 / C1 spread but always well below generous |
| A4 shared share, generous truth | h3 K6 0.72–0.82, K1 0.76–1.00, C1 0.75–1.00 | stable |
| ECG final values | see Part B | **unstable** in most multi-leaf scenarios, for reasons inside ECG (B3) |

No run looks broken.

## A1: load (K6R, root load 0.34 vs 0.67)

| | K6 sync pfifo (4 reps) | K6R (2 reps) |
|---|---|---|
| root rr->r0: load; keyframe peak p50 | 0.67–0.68; 27–29 ms | 0.34; 2.7 / 3.2 ms |
| X / Y r0->r1, r0->r2 (load 0.67): peak p50 | 6.5–9.5 ms | **23–35 ms** |
| share of ECG events with the root congested (generous ; strict) | 0.57–0.74 ; 0.06–0.09 | 0.11 / 0.14 ; 0.08 |
| X / Y congested in ECG events | 0.18–0.52 | **0.51–0.68** |
| h3 last P / pooled P | 0.25–0.67 / 0.35–0.46 | 0.33 / 0.40; 0.35 / 0.38 |
| h3 memberships wrong at declaration | 53–78 of 81–126 | 68 of 96, 91 of 152 |
| ECG final P / cov, tree | 1.00 / 0.42–0.78, 2/4 ok | 1.00 / 0.42, 0.78; 1/2 ok |
| B1 own, upstream only (--U) | 0.57–0.71 | 0.39 / 0.38 |

Halving the root load removes the root's keyframe queue. The queue then forms at the next
shared link that is still at ~0.67 (X / Y peaks ×3–4), and h3 collapses just as before. **The
effect is tied to loaded shared links**: it moves to whichever shared link carries the
synchronized keyframes at high load. The paper must state the load of the shared links, not
only of the root.

## A2: AQM (codel, pie vs pfifo; sync, 2 reps each)

Keyframe queue at the main shared egress (base router->switch, K1 / C1 r1->r2, K6 rr->r0):

| | peak p50 ms | spike p50 ms | keyframe windows with drops | stag peak |
|---|---|---|---|---|
| pfifo | base 40; K1 / C1 37–39; K6 27–29 | 220–300 | 0.1–3 % | 4–10 |
| codel | base 36–38; K1 / C1 36–38; K6 27–28 | 210–275 | **82–90 %** (1–3 drops each) | base 5 |
| pie | base 29–32; K1 34; C1 37; K6 26–27 | 200–250 | 5–36 % | 4 |

- Neither AQM removes the keyframe queue. CoDel drops a packet or more in most keyframe
  windows, but the spike is shorter than its 100 ms interval, so the peak is unchanged. PIE
  lowers the peak by up to ~25 % on the base topology.
- Grouping is just as affected:
  - K6 h3 pooled P codel 0.37 / 0.40, pie 0.36 / 0.37;
  - ECG on K6 is worse under codel / pie: final P 0.33–0.50 in 3 of 4 runs, sibling merges
    in 3 of 4;
  - K1 and base are unaffected, C1 between.
- **The problem is general, not specific to tail-drop queues.**

## A3: microbenchmarks, negatives, J1 (sync vs stag)

| | sync r1 / r2 | stag |
|---|---|---|
| M6 indepfast: h3 pooled P; ECG final P / cov | 0.92 / 0.96; 1.00 / 0.71 both | 0.96; 1.00 / 0.71 |
| M6 indepslow: h3 pooled P | **0.51 / 0.93** (not reliable) | 0.98 |
| J1 hierjit20: h3 pooled P; ECG P / cov | 0.87 / 0.83; 1.00 / 0.71 both | 0.93 / 0.84; 1.00 / 0.48, 0.71 |
| G0 randloss, calmuneven: topology truth, h3 SAME pairs right-wrong | randloss 6-0 / 2-0; calmuneven 25-0 / 46-1 | 6-0; 47-0 |
| G0: ECG SAME pairs | 0 everywhere | randloss 3-0 |

- B1 with a leaf queue congested stays 0.96–1.00 everywhere.
- Upstream-only votes are 0.46–0.89 (M6, J1).
- Independent timing and jitter scenarios change little. The negatives are as before: h3
  groups clients behind a congested shared egress (one wrong pair in 4 sync runs), and ECG
  states none.

## A4: strict per-event truth

h3 wrong pair-closes that share a congested egress in that event, generous → strict:

| | sync | stag |
|---|---|---|
| K6 (pfifo, codel, pie, K6R) | 0.57–0.82 → **0.10–0.20** | 0.88 / 0.56 → 0.88 / 0.48 |
| K1 (pfifo, codel, pie) | 0.76–1.00 → 0.31–0.58 | 0.50 / 1.00 → 0.50 / 1.00 |
| C1 (pfifo, codel, pie) | 0.75–1.00 → 0.41–0.69 | 0.50 / 0.62 → 0.50 / 0.62 |
| J1 hierjit20, M6 | 0.57–1.00 → 0.00–0.90 | 0.23–1.00 → 0.03–0.50 |

ECG wrong pair-closes, generous → strict: 0.08–0.88 → 0.00–0.39.

Under the strict truth the upstream / root counts as congested in only 3–33 % of ECG events
(generous 11–83 %).

**Reading: the shared share drops a lot, most of all on K6.** Most of h3's K6 errors are not
explained by a queue that is congested for most of the event. The root's keyframe spikes are
brief (~220 ms in a 3 s interval) and h3 merges on them: a real part of h3's errors remains.
On K1 / C1 about half survives the strict truth.

## B1: ECG final values across reps (multi-leaf configurations; all 26 with >= 2 reps in the summary)

| configuration | reps | coverage range | P range | tree correct | sibling merge at end |
|---|---|---|---|---|---|
| C1 sync pfifo | 4 | 0.05–0.71 | 0.40–1.00 | 0/4 | 1/4 |
| C1 sync codel / pie | 2 / 2 | 0.14–0.48 / 0.14–0.71 | 0.40–1.00 | 0/2, 0/2 | 1/2, 1/2 |
| C1 stag pfifo | 2 | 0.48 | 1.00 | 0/2 | 0/2 |
| K6 sync pfifo | 4 | 0.42–0.78 | 1.00 | 2/4 | 0/4 |
| K6 sync codel / pie | 2 / 2 | 0.17–0.42 / 0.58–0.78 | 0.33–1.00 / 0.43–0.50 | 0/2, 0/2 | 1/2, 2/2 |
| K6 stag pfifo | 2 | 0.78 | 0.50–1.00 | 1/2 | 1/2 |
| K6R | 2 | 0.42–0.78 | 1.00 | 1/2 | 0/2 |
| K1 sync pfifo / pie | 2 / 2 | 0.71 | 1.00 | 2/2, 2/2 | 0 |
| K1 sync codel | 2 | 0.48–0.71 | 1.00 | 1/2 | 0 |
| K1 stag pfifo | 2 | 0.71 | 1.00 | 2/2 | 0 |
| J1 (5 stag types, sync jit20) | 2 each | 0.48–0.71 | 1.00 | 11/12 | 0 |
| M6 indepfast / indepslow sync | 2 / 2 | 0.71 | 1.00 | 2/2, 2/2 | 0 |
| single-leaf (M1 × 3 AQMs) and G0 negatives | 2 each | no spread | – | all | 0 |

R is 1.00 everywhere.

## B2: inside a run

Share of closes with the correct leaf partition; memberships lost / regained per run:

| | correct share | lost / regained |
|---|---|---|
| K1, J1, M6 | 0.29–0.89 | 0–17 |
| C1 (sync and stag) | 0.00–0.17 | 5–26 |
| K6 sync | 0.00–0.49 | 11–32 |
| K6 stag | 0.00 / 0.17 | 10–13 |

In the second half of a run, coverage swings from 0.00–0.29 to 0.71 inside C1 runs and 0.08 to
0.78 inside K6 runs.

## B3: mechanism

107 memberships were declared at some close and are below A (4.55) at the end. Their negative
L steps, by the case of the closing event:

| case | steps | summed dL | of which with the flow in that event (steps, summed dL) |
|---|---|---|---|
| SOLO | 1575 | −887 | 355, −273 |
| A | 741 | −528 | 40, −29 |
| GLOBAL | 506 | −184 | 457, −160 |
| D | 159 | −106 | 62, −53 |
| B | 131 | −87 | 3, −5 |
| C | 261 | −84 | 1, −1 |

- **Most of the loss happens at closes of events the flow is not in.** That is ECG's
  exponential decay of L (τ 300 s, applied every 10 s, `decay_period`). Between two events of
  its own leaf, a member loses L; it is credited to whichever event closes next, mostly other
  clients' SOLO and A events.
- The flow's own negative evidence is the smaller part: GLOBAL events it takes part in
  (−160), its own SOLO onsets (−273), and D.
- In C1 a leaf gets few attributable events (long bursts, many C and GLOBAL), so decay pulls
  its members below A. Examples: C1 sync r1 a1 L 9.1 → 0.9 over 12 closes of mostly other
  clients' SOLO events; K6 r1 d1 / d2 9.1 → 1.5.
- **Sibling merges** (8 cases; C1 sync r3 and K6 stag r2 among them):
  - All were created by one event, case A for 7 of 8, whose members came from two leaves (upstream / root
    congestion, or two leaves in one ECG event). C1 r3 is case C (only the a clients
    fired) on a node that already held both.
  - Later events were mostly SOLO, A on the merged leaf, and C. C is ECG's sub-pattern case;
    it adds to the split weight, but in these runs the split did not happen before the end
    (C1 r3: 16 C events after the merge). Why the split weight was not reached was not
    traced through the engine log.

## B4: the earlier "93 runs, P / R 1.00, tree 83 / 93"

- Of those 93 runs (one rep per configuration), **80 are single-leaf**: one group, where ECG
  is stable in every rep here (M1, G0: no spread). **Only 13 are multi-leaf**, with 10 / 13
  trees correct.
- Here, multi-leaf configurations with >= 2 reps had trees correct in 26 / 46 runs (K1 / J1 /
  M6 mostly right, C1 never, K6 about half).
- So for the multi-leaf part, a single rep is close to a coin flip on K6, a reliable "no" on
  C1, and a reliable "yes" on K1 / J1 / M6.
- The 83 / 93 headline is carried by the single-leaf runs. The 10 / 13 multi-leaf part could
  well be luck: with a per-run probability of ~0.5 (K6), 1 of 1 correct happens half of the
  time.

**Reps needed:**
- To bound a configuration's per-run tree-correct probability from below with 95 % confidence
  when all reps succeed: 5 / 5 gives >= 0.55, 10 / 10 >= 0.74, 20 / 20 >= 0.86.
- To estimate a probability near 0.5 to ± 0.15: about 40 reps.
- Final coverage and precision values vary inside a run as much as across reps, so a single
  final value should not be quoted at all. Report its range over closes or reps.

**Reading:** final values vary this much in most multi-leaf scenarios (C1, K6 under every AQM
and phase), so **ECG is not a safe fallback as it stands, and no single-rep result may be
quoted**. Exception: single-leaf scenarios, where ECG is stable.

## What these runs cannot tell us

- One load step (0.67 → 0.34 at the root only). The scaling at intermediate loads, or with
  every shared link at lower load, is untested.
- AQMs: codel and pie at defaults, 2 reps. No ECN, no RED in this set.
- 2 reps for most configurations (4 for K6 / C1 sync pfifo). B4's probabilities are rough; the
  reps-needed numbers are generic binomial bounds, not estimates for each configuration.
- The strict truth is one choice (half of the interval). A per-sample truth (queue congested
  at the moment of the client's own onset) is not computed.
- ECG's engine log was not traced, so the reason the sibling merges did not split is not
  pinned down.
- M6 indepslow r1 vs r2 (h3 0.51 vs 0.93) is unexplained.
