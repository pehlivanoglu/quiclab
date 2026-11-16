# Step 9: SETS, set-based grouping, replayed on v3 and scored next to ECG and h3 (2026-11-15)

Measurement only. The detector, ECG v1.2, h3 and the Step 8 rows (observed sets, congested egresses, split classes, ECG / h3 groups per close) are used unchanged.

**Files** (all in this folder):
- `sets.py` (the procedure)
- `step9.py` (replay, scoring, model)
- `extra_rows.py` (Step 8 rows for C12 and M8)
- `report9.py` → `tables.md` (all tables)

**Runs.**
- Main: C7, C8, C9, C10, C11, C12, C13, M7, M8 under pfifo / codel / pie, plus mixab: 34 runs.
- fq_codel (E): C7, C9, C10, C12: 8 runs.

Two onset sources: v2-owd and truth. Every value is rep 1 / rep 2.

**True sets.** Clients behind each shaped egress with an ordinary queue. For M8 this is `up` and `a`; the fq_codel `b` leaf is not a group (decision 2026-11-15).

**Constants:**
- Q = 0.99 (T);
- ≤ 1 extra client (FLAG);
- m estimate: K_EST = 2, tolerance 1e-4, ≤ 30 iterations (M);
- F1 ≥ 0.9 counts as "found" (FLAG);
- same-link sets in E: seen in ≥ 2 events (M);
- late joiner: the last client of each leaf by name (M);
- model replicas r ∈ {1, 5, 25, 100}.

## A. The procedure

- **State.** A table of distinct observed sets (≥ 2 clients) and their counts. Nothing else.
- **Output.** Support, groups, tree, crossing-filter variant, memberships and mean Jaccard are computed from the table at every read.
- **Order.** End groups are identical for reversed and three random orders in all 34 runs × 2 sources × 18 variants.
  - The first version failed this in 2 runs (C10 codel). Ties in the m estimate and in the crossing filter followed table insertion order. Both are now broken by the set's bitmask, and the property holds.
- **m estimated from the table:** 0.000–0.125 per run with v2-owd (1–4 iterations) and 0.000 with truth onsets.
  - This is far below the measured miss rate of 0.16 (C1).
  - The reason: a fragment that recurs becomes its own group at K_EST = 2 and absorbs its own misses. The estimate measures misses not explained by a recurring fragment, not the per-client miss rate.
- **Fixed-m reference:** 0.161 (v2-owd), 0.013 (truth), pooled over single-egress events.

## B. Scoring next to ECG and h3 (v2-owd onsets; truth onsets in `tables.md`)

**B1. Best-matching group per true set, F1** (mean over every close, then over runs):

| level | SETS quantile k2 | k3 | k4 | k3 + crossing | exact k3 | fixed-m k3 | ECG | h3 |
|---|---|---|---|---|---|---|---|---|
| leaf | **0.83 / 0.85** | 0.76 / 0.78 | 0.68 / 0.72 | 0.76 / 0.78 | 0.67 / 0.74 | 0.77 / 0.78 | 0.73 / 0.73 | 0.75 / 0.78 |
| mid (C9) | **0.80 / 0.81** | 0.71 / 0.75 | 0.62 / 0.59 | 0.71 / 0.73 | 0.69 / 0.63 | 0.83 / 0.80 | 0.59 / 0.62 | 0.66 / 0.68 |
| up | **0.88 / 0.87** | 0.83 / 0.81 | 0.72 / 0.73 | 0.83 / 0.79 | 0.73 / 0.76 | 0.87 / 0.90 | 0.57 / 0.73 | 0.64 / 0.64 |
| root (C9) | **0.77 / 0.71** | 0.62 / 0.66 | 0.55 / 0.52 | 0.62 / 0.65 | 0.52 / 0.55 | 0.72 / 0.67 | 0.52 / 0.67 | 0.56 / 0.59 |

- **Exactly-equal share** (reference), SETS quantile k2: leaf 0.75 / 0.82, up 0.76 / 0.78, root 0.48 / 0.38. ECG reaches up 0.00 / 0.28 and h3 0.01 / 0.05.
- **ECG and h3 hold upper levels with high precision but low recall.** For example, ECG up: P 0.88 / 0.95, R 0.42 / 0.62. Their groups are leaf-sized parts of the upper set.
- **Weak blocks:**
  - C13: 12–14 events per run, so k3 / k4 groups arrive late (k4 leaf 0.22 / 0.32);
  - C12: 4 clients, 22 events (0.55–0.70);
  - C9 leaf at k ≥ 3: 0.54–0.72.

**B2. Spurious groups** (per close, mean; at the end, summed over runs):

| method | per close | at end | end types (r1 + r2) | life p50 (max) closes |
|---|---|---|---|---|
| SETS quantile k2 | 0.84 / 0.77 | 21 / 25 | true set minus clients 35, union of two true sets 8, plus clients 2, other 1 | 12 (89) |
| SETS quantile k3 | 0.55 / 0.54 | 15 / 17 | minus clients 22, union 7, plus clients 2, other 1 | 17 (86) |
| SETS quantile k3 + crossing | 0.32 / 0.32 | 11 / 9 | minus clients 17, union 3 | 14 (86) |
| SETS exact k3 | 0.21 / 0.21 | 10 / 7 | minus clients 11, union 6 | 22 (82) |
| ECG | 0.10 / 0.03 | 0 / 1 | minus clients 1 | 60 (83) |
| h3 | 0.81 / 0.53 | 19 / 9 | minus clients 27, other 1 | 2 (85) |

- **"Minus clients" groups are mostly the M8 fq_codel leaf {b3, b4}** (2–3 per run, lifetime 46–78 closes), plus 2–3-client fragments of a leaf.
- **The unions** are C9 A∪C and M7 a∪b. They are real recurring observations of concurrent stimuli (Step 8). The crossing filter removes the C9 ones but not M7.
- **With truth onsets**, SETS quantile k3 has 0.19 / 0.16 spurious groups per close, all unions or M8 b-sets.

**A6. Second confidence (mean Jaccard).** End-of-run SETS groups, quantile k3, v2-owd; share whose best F1 is below 0.9:

| mean Jaccard | share wrong | groups |
|---|---|---|
| < 0.7 | 1.00 | 10 |
| 0.7–0.85 | 0.92 | 12 |
| 0.85–0.95 | 0.17 | 23 |
| ≥ 0.95 | 0.08 | 89 |

Low Jaccard reliably marks wrong groups.

**B3. Pairs from each client's smallest group, same-leaf truth.**

| method | P | R | coverage |
|---|---|---|---|
| SETS quantile k3 | 0.97 / 0.95 | 0.95 / 0.96 | 0.81 / 0.84 |
| ECG | 0.92 / 0.68 | 0.97 / 0.98 | 0.75 / 0.76 |
| h3 | 0.81 / 0.83 | 0.61 / 0.74 | 0.81 / 0.86 |

Shared-queue precision is 0.99–1.00 for all three.

**B4. Time to F1 ≥ 0.9** (median; events of that egress / seconds):

| method | leaf | up | mid | root |
|---|---|---|---|---|
| SETS quantile k2 | 3 / 3 events, 103 / 82 s | 2 events, 104 / 165 s | 2–3 events, 170 / 276 s | 2 events, 321 / 313 s |
| SETS quantile k3 | 4–5 events, 122–140 s | – | – | 3 events, 355–396 s |
| ECG | – | never for 9 / 5 of its true sets | – | – |
| h3 | fastest, 2–3 events, 58–82 s | 4–6 events, 247–434 s; never for 2 / 4 | – | – |

Every true set reaches F1 ≥ 0.9 with SETS quantile k2 in both reps.

**B5. Late joiner** (SETS quantile k2, 34 cases per rep): joined 33 / 34 and 34 / 34, after 9 / 8 events (3 of its own leaf), 117 / 92 s. At k3, 29 / 30 join within the run.

**B6. Order.** End groups are identical for every rule, k and crossing variant.

**B7. Cost.**
- 3–16 distinct sets per run (max 20), 27–148 bytes.
- 15–274 set comparisons per read for all three rules.
- The whole 18-variant replay with scoring takes ≤ 0.2 s per run.

## C. Large groups: a model, not a run

**C1. Measured misses are not independent** (v2-owd, single-egress events):
- **Rates.** Leaf miss rate 0.12–0.17 (mixab 0.38), up 0.13–0.25, mid 0.04–0.14, root 0.25. Leaf false inclusion 0.001–0.002 (pie 0.107).
- **Dispersion index:** 2.7–3.6 at leaf, 4.9–6.0 at up / mid, 12.4–13.0 at root; 1.0 would be binomial.
- **Many events are complete.** 50–81 % of events miss nobody (leaf 0.75), while the rest miss many.
- **The binomial underestimates the spread.** Events missing ≥ half of the clients:

  | level | measured | binomial |
  |---|---|---|
  | leaf | 0.12–0.19 | 0.08–0.14 |
  | up | 0.13–0.25 | 0.01–0.11 |
  | root | 0.25 | 0.027 (9× lower) |

**C2 / C3. Model replay.** Truth-onset sequences of C7, C9 and C11 pfifo, both reps. Every client becomes r replicas; misses and false inclusions are drawn with the pooled C1 rates (leaf m 0.146, f 0.0059). End-of-run F1 at leaf (up / mid in brackets) and spurious groups, rule k3:

| group size | independent misses, exact | independent misses, quantile | measured joint pattern, exact | joint, quantile |
|---|---|---|---|---|
| r 1 (4–16) | 0.73–1.00 | 0.98–1.00; 0–6.5 spurious | 0.92–1.00 | 0.96–1.00; 0–2.5 spurious |
| r 5 (20–80) | 0.00–0.33 | 0.82–0.98; 2.5–9.5 spurious | 0.83–1.00 | 0.96–1.00; 0–2.5 spurious |
| r 25 (50–400) | 0.00 | **0.00** | 0.50–1.00 | 0.87–1.00; 2.5–26.5 spurious |
| r 100 (200–1600) | 0.00 | **0.00** | 0.00–0.92 | 0.17–1.00 (C11 0.17); 0–24.5 spurious |

**Answer.**
- **With independent misses, exact matching stops at group sizes of about 20.**
- **The quantile rule as specified stops at about 100–400.** No two observations are equal, so the m estimate, which starts from exact matches, never leaves 0 (m_end = 0.000). Matching never becomes tolerant.
- **False inclusions add to this at large N.** At f = 0.006 an observation of a 400-client group in an 800-client tree has ~2.4 extra clients, beyond the fixed allowance of 1.
- **Under the measured joint pattern** (most events complete), exact repeats exist even at 1600 clients, so both rules keep F1 0.67–1.00 at r = 100 for C7 and C9. But spurious groups rise to ~25 with the quantile rule, and C11 r = 100 fails (0.00–0.17).
- **So the method has not been shown to scale.** Whether it survives 100–400-client groups depends on which miss pattern holds at scale, and the model cannot tell us that. The two specified parts that break are the bootstrap of m from exact matches and the fixed one-extra-client allowance.
- **Cost.** ≤ 74 distinct sets and < 0.01 s per read at 1600 clients.

## D. Unions: can curves tell an upstream queue from concurrent leaves?

Groups at the end of the run that are the disjoint union of two other groups. For each, the within-event split over the events whose observed set matches the union (v2-owd; truth onsets similar):

| case | blocks | events | split exactly into the two parts | one class | other |
|---|---|---|---|---|---|
| true upstream, parts are true sets | C7, C8 | 122, 41 | 0.45, 0.39 | 0.30, 0.29 | 0.25, 0.32 |
| | C10 | 60 | 0.20 | 0.48 | 0.32 |
| | C9 (root = X∪Y, X = A∪B, Y = C∪D) | 70 | **0.00** | 0.69 | 0.31 |
| | C13 | 16 | 0.00 | 0.62 | 0.38 |
| concurrent leaves, not a queue | C9 A∪C | 23 | **0.70** | 0.26 | 0.04 |
| | C11 | 18–20 | 0.80–0.83 | 0–0.05 | 0.15–0.17 |
| | M7 a∪b | 12 | 0.42 | 0.00 | 0.58 |

- **Curves point the right way.** Concurrent leaves split at the true boundary more often (0.42–0.83) than real upstream sets (0.00–0.45).
- **But the two cases overlap.** C7 upstream splits 0.45 of the time; M7 concurrent leaves 0.42.
- **Only C9 shows a clean gap** (0.00 against 0.70).
- **So unions of repeatedly concurrent leaves stay a stated limitation.**
- **Crossing filter:** it removes the C9 A∪C unions (2 / 2 per rep), which cross X and Y. It removes none in M7 or C11, which have no crossing set.

## E. Per-flow-queue cells (C7, C9, C10, C12 fq_codel)

SETS (quantile k3) reports 1.0–7.3 groups per close (v2-owd) and 0.7–4.5 (truth onsets). Examples at the end, with support:
- C7 r1: {a3, a4} 25, {b3, b4} 24, {a3, a4, b3, b4} 50;
- C10 r1: {b3, b4} 15, {a3, a4, b2, b3, b4} 38;
- C9 r1: {a4, b4} 10, {a2, a3, c2, c3} 12;
- C12 r1: {sub-b, sub-c, sub-d} 6.

The two readings:
- **Same queue:** every one of these groups is false.
- **Same link** (per-event co-constrained sets seen ≥ 2 times): best F1 0.60–0.81 (v2-owd) and 0.56–0.93 (truth onsets), with 0.0–3.5 extra groups per close. The high-support groups are exactly the co-constrained sets (F1 1.0).

The choice between the two readings is yours and is not made here.

## What these runs and the model cannot tell us

- **Scale.** Behaviour at 100+ clients per group is a model with pooled rates and resampled per-event miss fractions. It is not measured, and its two miss patterns give opposite answers.
- **Choice of k.** k is not chosen. k2 scores best on F1 and k3 has fewer spurious groups. The F1 ≥ 0.9 threshold is a FLAG.
- **m estimate.** It measures unexplained misses, not the per-client rate. A different bootstrap would be a design change, not tuning, and was not tried.
- **Seeds and orders.** 2 seeds; the order results are offline permutations of the same events.
- **Thin cells.** Root / mid exist only in C9 (4 runs). C13 has 12–14 events per run and C12 has 4 clients.
- **fq_codel.** The same-queue / same-link decision is open.
