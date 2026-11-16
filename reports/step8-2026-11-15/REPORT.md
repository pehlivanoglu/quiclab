# Step 8: observed sets, recurrence, and per-flow-queue negative control (2026-11-15)

Campaign `.runs/2026-11-14_1818_v3`. Measurement only on existing runs: the detector, ECG v1.2, h3 (replay4, m = 3), the step 2 within-event split (`partition_fixed`) and the step 6 readers are called unchanged. Reps side by side (rep 1 / rep 2).

**Files** (all in this folder):
- `step8.py` → `rows.jsonl`, then `report.py` → `tables.md` (parts A–D, full tables);
- `fq_control.py` → `fq-rows.jsonl`, then `fq-control.md` (part E).

**Cells.** C7, C8, C9, C10, C11, C13, M7 under pfifo / codel / pie: 26 runs. fq_codel and mixab only in E.

**Definitions** (M unless tagged):
- **Observed set:** the ECG event's members, with sub-ctrl removed. Two onset sources: v2-owd and truth.
- **Congested egresses:** shaped plan egresses whose queue-log episodes cover ≥ half of [t0 − 1, t0 + 2]. This is gt1's CoDel rule on the per-packet trace (T).
  - C13 pfifo r1 has an invalid GT-Q health file and uses GT1 instead (FLAG). Q1 showed the two are identical under pfifo.
- **Truth set:** the union of the clients behind the congested egresses.
- **True sets:** "clients behind e" for every shaped egress.
- **Recurrence** counts sets of ≥ 2 clients only.

## A. The observed set per event

| event type | v2-owd: equal | v2-owd: strict subset (missing p50) | v2-owd: superset | truth onsets: equal |
|---|---|---|---|---|
| leaf (361 / 355 events) | **0.76 / 0.83** | 0.24 / 0.15 (2 / 3) | 0.00 / 0.01 | 0.99 / 0.98 |
| mid, C9 (25 / 28) | 0.92 / 0.71 | 0.08 / 0.29 (4) | 0 | 1.00 / 1.00 |
| up (81 / 101) | 0.69 / 0.68 | 0.31 / 0.32 (5 / 4) | 0 | 0.97 / 1.00 |
| root, C9 (18 / 14) | 0.33 / 0.71 | 0.67 / 0.29 (8) | 0 | 1.00 / 1.00 |
| nested a+up (51 / 42) | 0.39 / 0.38 | 0.61 / 0.62 (4) | 0 | 0.68 / 0.66 |
| disjoint a+b, A+C, … (202 / 221) | 0.21 / 0.15 | 0.79 / 0.85 (4) | 0 | 0.30 / 0.24 |

- **Single egress.** With truth onsets the observed set is the true set in 97–100 % of events. With detector onsets it is 68–83 % at leaf and up level and 33–92 % at mid / root.
- **The error is almost always missing clients, never extra ones** (superset ≤ 0.04). For leaf events, |difference| = 0 in 0.76 / 0.83 and 1–3 in 0.15 / 0.13 (A2).
- **Combined events.** Most events are "strict subsets" only because the event shows the clients whose congestion *started*, while my truth set includes egresses that were already congested. A3, with truth onsets:
  - staggered a+b (C7): the event shows **b** 24 / 25 times and **a∪b** 16 / 13;
  - simultaneous A+C (C9): **A∪C** 12 / 12;
  - nested a+up (C7, C8): **a∪up = up** in every event;
  - C10 nested (both reps): in 23 of 33 events the observed set is the *other* leaf's 4 clients, i.e. up minus the leaf that was already congested; in 8 it is up and in 2 the own leaf.
- So an observed set is one true set, or the union of the true sets whose congestion began together. With v2-owd the same pattern holds, plus 1–3-client fragments.

## B. Within-event split by curve (`partition_fixed` on the observed clients)

| event type | split exactly into the true sets: v2-owd | truth onsets | false split (≥ 2 classes): v2-owd | truth onsets |
|---|---|---|---|---|
| leaf | 0.71 / 0.78 | 0.83 / 0.86 | **0.09 / 0.06** | 0.10 / 0.06 |
| mid | 0.80 / 0.46 | 0.92 / 0.67 | 0.04 / 0.23 | 0.04 / 0.25 |
| up | 0.37 / 0.47 | 0.51 / 0.62 | 0.28 / 0.17 | 0.32 / 0.24 |
| root | 0.27 / 0.42 | 0.58 / 0.58 | 0.20 / 0.17 | 0.17 / 0.17 |
| disjoint, C9 A+C (simultaneous) | 0.62 / 0.58 | **0.83 / 0.58** | – | – |

- **Disjoint on different leaves.** Split exactly into the two true sets in C9 (A | C): 0.58–0.83. C7 / C8 / C10 / C11 have few events with both leaves observed. The C7 outcomes (r1 + r2) were: b 35, a 22, a | b 21.
- **Single egress.** False splits occur in 6–10 % of leaf events and 17–32 % of up / root events. The pieces are mostly 2–7-client fragments.
- **Nested a+up.** The most common outcome is **a | b**: 27 of 81 v2-owd events and 36 of 75 truth-onset events. Curves separate the leaf with the extra queue from its sibling.
  - One class equal to the whole observed set (the up set) comes out in 0.43 / 0.35 of events with v2-owd and 0.30 / 0.34 with truth onsets.
  - "Exactly the true sets" is impossible here, since the true sets {a, up} are nested and a split gives disjoint classes.

## C. Recurrence (counts of distinct sets; full top-ten lists in `tables.md` C1)

**C1 / C2, all 26 runs** (true sets reaching k, of 46 true sets; spurious sets reaching k):

| version | onsets | true ≥ 2 | true ≥ 4 | spurious ≥ 2 | spurious ≥ 3 | spurious ≥ 4 |
|---|---|---|---|---|---|---|
| raw | v2-owd | 46 / 46 | 42 / 46 | 19 / 13 | 7 / 4 | 5 / 3 |
| raw | truth | 46 / 46 | 46 / 46 | 5 / 3 | 3 / 3 | 3 / 3 |
| split | v2-owd | 46 / 45 | 39 / 38 | 52 / 39 | 25 / 20 | 16 / 13 |
| pooled | v2-owd | 46 / 46 | 42 / 46 | 58 / 44 | 29 / 24 | 19 / 15 |

- **True sets.** Every true set occurs in every run. With truth onsets every true set ranks at or near the top; in C9, all seven appear 6 times each.
- **Spurious sets that recur at k ≥ 3 with truth onsets** are 3 per rep. They are exactly the unions of scheduled *simultaneous* combined stimuli:
  - A∪C in C9 pfifo and codel, 6 times each, as often as any true set;
  - a∪b in M7, 6 times;
  - in C7 / C8 / C10, a∪b equals the true **up** set, so a simultaneous a+b event cannot be told from an up event by the set alone.
- **With v2-owd onsets** there are, in addition, 1–3-client fragments: 19 / 13 at k = 2, falling to 5 / 3 at k = 4.
- **The split version adds spurious sets** (52 / 39 at k = 2). The raw sets are cleaner.
- **No k separates true from spurious in every run.** With raw v2-owd sets, k = 4 keeps 42 / 46 of the true sets and 5 / 3 spurious ones. Under truth onsets the spurious sets left at every k are the simultaneous unions, which no count can remove.

**C3. Time until a true set is seen twice** (raw, v2-owd; truth onsets in brackets; median events / seconds):
- leaf: 9 / 8 events, ~100 s (5–6, 60–75 s);
- up: 10 / 12 events, 133 / 180 s (6 / 10);
- mid: 12 / 28 events, 170 / 442 s (10 / 12);
- root: 32 / 39 events, 487 / 629 s (23 / 29).

Four times: leaf ~20 events. Root under v2-owd is never reached in 2 of 4 runs.

**C4. Tolerance** (differ by ≤ 1 client, FLAG), raw, v2-owd: true sets reaching 4 go from 42 → 46 in rep 1 (46 → 46 in rep 2), and spurious sets from 5 → 8 / 3 → 4. It helps the true sets a little and blurs little. With truth onsets it changes nothing.

**C5. Nested?** Raw recurring sets are laminar in 11 / 13 runs per rep at k ≥ 3. The only crossings, 4 per rep in both sources, are A∪C crossing X and Y in the two C9 runs, i.e. the simultaneous-union sets. The split and pooled versions cross more (k = 2: 46 / 20 pairs).

**C6. Order.** End counts are identical in 26 / 26 runs for reversed and three random orders, by construction. Time to a second sighting changes with order, most at root: 12–38 events with v2-owd, 6–26 with truth onsets.

## D. Share of closes at which a group equals each true set exactly (mean over the run)

| level | ECG v2-owd | h3 v2-owd | recurring raw k = 2 | k = 3 | k = 4 | ECG truth onsets | recurring raw k = 2, truth onsets |
|---|---|---|---|---|---|---|---|
| leaf | 0.62 / 0.51 | 0.52 / 0.55 | **0.80 / 0.84** | 0.68 / 0.69 | 0.61 / 0.61 | 0.76 / 0.61 | 0.88 / 0.88 |
| mid (C9) | 0.15 / 0.19 | 0.17 / 0.07 | 0.78 / 0.60 | 0.69 / 0.49 | 0.55 / 0.31 | 0.00 / 0.04 | 0.80 / 0.77 |
| up | **0.00** / 0.32 | 0.01 / 0.06 | 0.76 / 0.77 | 0.68 / 0.66 | 0.53 / 0.57 | 0.00 / 0.28 | 0.82 / 0.79 |
| root (C9) | 0.00 / 0.09 | 0.01 / 0.02 | 0.42 / 0.29 | 0.17 / 0.20 | 0.00 / 0.14 | 0.00 / 0.21 | 0.54 / 0.42 |

- **ECG and h3 almost never hold a group equal to an up / mid / root set.** ECG's 0.28–0.32 up share in rep 2 comes from the C10 / C13 runs where its one node took both leaves (Q3). That node is a wrong leaf node that happens to equal the up set.
- **Recurring sets hold the nested sets.** At k = 2 they cover 0.76–0.84 per level (root 0.29–0.42).
- **This score counts presence only.** It does not penalise the spurious recurring sets of C2, so it has to be read next to them.

## E. Per-flow-queue egresses as a negative control (`fq-control.md`; decision 2026-11-15)

**E5. Which egresses are per-flow.**
- C7, C9, C10 and C12 fq_codel: every router egress is fq_codel (qdiscs.txt). No ordinary queue is shared, so no group is correct.
- M8 mixab: `up` r1→r2 is pfifo, `a` is pfifo, and `b` is fq_codel. The true sets are **up** (all 8) and **a**; the b clients form no group of their own.
- cake has no grouping cell: C2 only, single leaf.

**E1. False groupings** (v2-owd onsets; mean per close / at the end):

| cell | ECG false groups (pairs) per close | ECG at end | h3 false groups (pairs) per close | h3 at end |
|---|---|---|---|---|
| C7 | 1.42 (1.42) / 1.43 (1.55) | 1 / 2 | 1.97 (2.42) / 2.45 (4.72) | 4 / 3 |
| C9 | 1.36 (4.70) / 1.99 (4.89) | 2 / 2 | 3.50 (12.2) / 3.47 (15.7) | 5 / 3 |
| C10 | 0.86 (5.73) / 1.79 (5.30) | 1 / 2 | 0.89 (1.04) / 3.59 (4.28) | 2 / 5 |
| C12 | 0.25 (1.16) / 0.80 (3.07) | 1 / 1 | 0.00 / 0.30 | 0 / 1 |
| M8 (b–b false; a–b mixed) | 0.43 / 0.62 groups; mixed pairs 0.09 / 0.14 | 1 / 1 | 1.41 / 1.00 groups; mixed pairs 8.9 / 1.9 | 2 / 1 |

- **Truth onsets** give the same picture: ECG 0.48–1.87 and h3 0–1.67 false groups per close, and 0–2 at the end.
- **No method passes the negative control.** Every fq_codel run ends with at least one false group, except h3 in C12 rep 1.

**E2. Lifetime.**
- False groups live a median of 20–106 closes, i.e. 184–731 s with v2-owd onsets. The longest last 764–870 s, i.e. most of the run.
- They are created during up / root events and during leaf events, in roughly equal numbers (per cell in `fq-control.md`).

**E3. Recurring false sets.**
- **Every fq_codel cell has false sets that recur 4 or more times.** With v2-owd: C7 6 / 7, C9 1 / 4, C10 5 / 3, C12 0 / 0. With truth onsets: C7 3 / 3, C9 3 / 3, C10 4 / 3, C12 1 / 1.
  - The most frequent are the same two clients per leaf, e.g. {a3, a4} and {b3, b4} in C7, 12 times each with v2-owd and 21 with truth onsets. These are the clients that exceed their fair share and are constrained together.
- **M8:** the true sets **a** (18–21) and **up** (9–15) recur, but so does the false set {b3, b4} (12–21).
- So recurrence alone would also turn per-flow co-constraint into groups.

**Ea. Testbed check.**
- On all 20 fq_codel and mixab runs with GT-Q, no two instrumented clients share a sub-queue index on any egress. The indices are 768 + i, from skb->priority 20:0x301 + i, set by a clsact flower filter on destination address; `flows 1024`.
- The only other 5-tuples in a client's sub-queue are its own other connections (529 cases) and other traffic (34 cases: the 1 % background leak into pinned classes, FLAG, to be fixed before the next campaign).
- Unpinned traffic keeps fq_codel's hash.

**Eb. Arithmetic** (1024 queues, uniform hash). Two given flows share a queue with probability 1/1024 = 0.001. At least two of n flows share one with probability:

| n | P(at least two share) |
|---|---|
| 10 | 0.043 |
| 30 | 0.35 |
| 100 | 0.993 |
| 1000 | 1.000 |

A given flow shares with probability 0.009 / 0.028 / 0.092 / 0.62 for the same n. These figures are written into `docs/paper-notes-ground-truth.md` §9 together with the decision.

## How it reads against the stated criteria

- **A: holds with truth onsets, partly with detector onsets.**
  - The observed set equals the true set in 97–100 % of single-egress events with truth onsets, and 68–83 % at leaf / up level with v2-owd (33–92 % at mid / root).
  - The detector's errors are missing clients, not extra ones.
- **B: partly.**
  - Simultaneous disjoint events split at the true boundary in 0.58–0.83 of cases (C9).
  - Leaf events are falsely split 6–10 % of the time, up / root events 17–32 %.
  - Nested events are split into the two leaves rather than kept as the up set.
- **C: true sets dominate; one class of spurious set does not go away.**
  - All true sets recur, and fragments mostly drop out by k = 4.
  - But the union of a *repeated simultaneous* combined stimulus recurs exactly as often as a true set (A∪C, a∪b). In two-level trees that union coincides with the up set.
  - Raw recurring sets are laminar except for those unions.
  - C6: the end result is order-free; the time to reach k is not.
- **E: the idea fails the negative control.** Under fq_codel the same clients are constrained together repeatedly, and their sets recur like true sets. Neither ECG, h3 nor recurrence leaves these cells without a group.

## What these runs cannot tell us

- **Spurious unions.** Whether they recur in practice. The v3 schedule repeats the same combined stimuli; real combined events would rarely repeat with the same pair of egresses. These runs cannot separate the two.
- **More seeds and orders.** Only 2 seeds; the C6 orders are offline permutations of the same events, not new runs.
- **Thin levels.** Root and mid levels exist only in C9: 4 runs, 12–18 root events.
- **No grouping procedure built on recurrence was run.** D scores the recurring sets as a family; nothing turns them into groups, as asked.
- **Untested AQMs and topologies.** cake hashing, collisions with many flows, and topologies with mixed AQMs beyond M8.
- **Truth definition.** The truth sets assume that the plan egresses are the only bottlenecks (shaped egresses only).

Constants: STRICT ½ coverage and gt1 TARGET / band / INTERVAL (T); sets of ≥ 2 clients only (M); tolerance one client (FLAG); random orders seeded crc32(run | source | i) (M); stimulus at t0 = [start − 0.5 s, end + 1 s] (M); for M8, "false" = b–b pairs in a group that is not the up set, and "mixed" = a–b pairs in such a group (M).
