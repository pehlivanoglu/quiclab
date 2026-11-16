# SETS v1: frozen grouping method (2026-11-15)

**Frozen:** the configuration O1 + old matching, called SETS.
- **Tag:** `grouping-sets-v1.1`.
  - It supersedes `grouping-sets-v1` (the first freeze commit, same rule), adding the configuration object, the crossing option, the read API, dump / restore, the single scorer and the benchmark.
  - The rule and every score are unchanged from `grouping-sets-v1`.
- **ECG v1.2 and h3** stay as comparison methods, frozen as they are, with no further development. Their code is untouched by this freeze.

| part | file |
|---|---|
| engine | `grouping/sets_engine.py` (`SetsEngine`) |
| rule and configuration | `grouping/sets.py` (`SetsConfig`, `FROZEN`) |
| tests | `tests/unit/test_grouping_sets.py` |
| replay regression | `scripts/sets_replay.py check`, against `tests/data/sets_v1_expected.json` |
| one scorer for SETS / ECG / h3 | `scripts/grouping_score.py` |
| cost benchmark | `scripts/sets_bench.py` |

Evidence: `reports/step8-2026-11-15/`, `reports/step9-2026-11-15/`, `reports/step10-2026-11-15/`, `reports/sets-v1-2026-11-15/`.

## 1. Definition

**Input.** The same interface as ECG: `FlowMeta`, `ObsSample`, `Onset`, `tick`. Event formation and the per-flow observability state are ECG's, inherited from `grouping.Engine` (subclassed, not copied):
- onset alignment by half the flow's minimum RTT;
- clustering within delta on aligned time, events at most delta_max long;
- the close at t0 + delta_max + hold;
- the in-episode rule: a second onset while the flow is in an episode is ignored.

ECG's evidence, cases, tree and decay are not used.

**Observed set of an event (O1).** The flows with an onset in the ECG event, minus the configured control flows (`sub-ctrl`).
- This is exactly the set Steps 8–10 used.
- ECG's observability check at the close (`Engine._observable`) is not applied to the members. It would drop 147 of 10397 v3 event members (1.4 %), and the frozen numbers were measured without it.

**State.** A table of distinct observed sets (≥ 2 flows) with their counts, nothing else. It is updated when an event closes, and reading never changes it.

**Matching and group extraction.** The rule as implemented in Step 9 (`grouping/sets.py`).
- S' counts toward S when |S' − S| ≤ extra and |S − S'| ≤ q(|S|, m), the 0.99 quantile of Binomial(|S|, m).
- m is estimated from the table, starting from exact matches.
- Support of S = the summed counts of the sets counted toward S.
- **Groups** are the stored sets with support ≥ k that do not count toward a stored set with a higher count. Fragments are absorbed by the set they come from.
- **Ties** are broken by the sets' order as bitmasks over the sorted flow names, so the output is a deterministic function of the table, never of insertion order.

**Output** (read at any time, for a given k):
- every group with its members, support, mean Jaccard (count-weighted |S ∩ S'| / |S ∪ S'| over the sets counted toward it) and its parent by inclusion (the smallest group that strictly contains it);
- the tree (the inclusion order);
- for each client, its smallest group.

**No single k is frozen.** Results are always reported at k = 2 and k = 3 side by side.

**Crossing filter.** An option, off by default; reported with and without. While two groups overlap without one containing the other, it drops the one that takes part in more crossings; on a tie, the lower support.

**State dump / restore.** `SetsEngine.dump()` / `restore()` / `save()` / `load()` cover the table, the configuration and the closed-event log. ECG's transient event-formation state (open events, episode flags) is not part of the SETS state, so dump between events.

## 2. Decisions (also in docs/paper-notes-ground-truth.md, 2026-11-15)

- **Scope.** The goal is each client's leaf group.
  - Nested upstream groups (mid / up / root) are out of scope: a limitation and future work, reported as a side table only.
  - Upstream events must not damage leaf groups. This is measured at the closes right after an upstream event, against all other closes.
- **No final precision.** "Final precision" is no longer a metric. Every score is averaged over all event closes of a run.
- **Per-flow-queue AQMs (fq_codel, cake): the "same link" truth.**
  - The clients constrained together at the same egress (their own sub-queues, during that egress's stimuli) form the group. Clients never constrained there are correct when left out.
  - Decided after the fq_codel grouping results had been seen. It replaces the earlier decision of the same day ("same queue", negative control).
  - The detector is still scored per client against its own sub-queue.
- **Scenario parameters for future campaigns:**
  - load U: default 0.50; 0.70 is the extreme point; 0.85 is removed;
  - stream share s: default 0.30; the upper value is 0.50;
  - the existing s = 0.65 runs are kept as a stress row;
  - all existing v3 event runs are at U = 0.70 and are labelled extreme-load runs from now on.

## 3. Constants (`SetsConfig.constants()`; one config object)

| constant | value | tag |
|---|---|---|
| q (binomial quantile of missed flows) | 0.99 | T |
| extra (flows allowed outside the set) | 1 | FLAG |
| m_tol (m convergence) | 1e-4 | M |
| m_iters (m rounds) | 30 | M |
| k_est (k while estimating m) | 2 | M |
| min_set (smallest stored set) | 2 flows | M |
| crossing (crossing filter) | off | M (option) |
| exclude (control flows) | `sub-ctrl` | M |
| event.delta (inherited) | 0.150 s | P (user decision 2026-11-11) |
| event.delta_max (inherited) | 0.300 s (= 2 delta) | M |
| event.hold (inherited) | 1.0 s | M |
| event.align_mode (inherited) | half_mrtt | M |
| event.obs_window (inherited) | 0.020 s | M |
| event.in_episode_rule (inherited) | second onset in an episode ignored | M (ECG engine, always on) |
| k for reporting | 2 and 3 side by side | not frozen |
| acceptance condition (fixed before the numbers were seen) | pair precision ≥ 0.93 in both reps | P |
| scoring: "group found" | best-match F1 ≥ 0.9 | FLAG |
| scoring: same-link window | stimulus window [start, end + 2 s] | M |
| scoring: upstream event | a non-leaf egress with GT1 episodes over ≥ half of [t0 − 1 s, t0 + 2 s] | M |

The onset source is the frozen Shadow v2 detector (ip4 values, OWD), unchanged.

## 4. Why this configuration (decided 2026-11-15)

**Acceptance condition.** It was fixed before the numbers were seen: pair precision ≥ 0.93 in both reps.
- O1 + old meets it at k = 2 (0.987 / 0.965) and k = 3 (0.972 / 0.949).
- **O4 + old does not** (0.961 / 0.896). It gains only 0.01–0.02 leaf F1, adds false pairs (the more expensive error) and needs a hand-picked 0.3 s window.
- **The new matching** lowers pair precision to 0.75–0.91.

Pair scores (same-leaf truth, from each client's smallest group, summed over every close, 34 v3 runs, Step 10), rep 1 / rep 2:

| configuration | pair P | pair R | status |
|---|---|---|---|
| **O1 + old, k = 2** | **0.987 / 0.965** | **0.908 / 0.927** | **frozen** |
| **O1 + old, k = 3** | **0.972 / 0.949** | **0.953 / 0.956** | **frozen** |
| O4 + old, k = 2 | 0.961 / 0.896 | 0.860 / 0.883 | rejected: P < 0.93 in rep 2 |
| O4 + old, k = 3 | 0.938 / 0.900 | 0.923 / 0.947 | rejected: P < 0.93 in rep 2 |
| O4 + new, k = 2 | 0.831 / 0.754 | 0.949 / 0.990 | rejected: false pairs |
| O1 + new, k = 2 | 0.912 / 0.855 | 0.982 / 0.990 | rejected: false pairs |

**Per block** (Step 10 scoring): pair P / R and the block's share of all false pairs, rep 1 ; rep 2:

| block | O1 + old k = 2 (frozen) | O1 + old k = 3 (frozen) | O4 + old k = 2 (rejected) |
|---|---|---|---|
| C7 | 0.99 / 0.87, 0.18 ; 1.00 / 0.81, 0 | 0.94 / 0.91, 0.34 ; 1.00 / 0.89, 0 | 1.00 / 0.81, 0 ; 1.00 / 0.74, 0 |
| C8 | 1.00 / 0.97, 0 ; 0.96 / 0.86, 0.06 | 1.00 / 0.98, 0 ; 1.00 / 1.00, 0 | 0.91 / 0.51, 0.09 ; 1.00 / 0.98, 0 |
| C9 (robustness row) | 1.00 / 0.96, 0 ; 0.93 / 0.99, 0.28 | 0.94 / 0.97, 0.28 ; 0.86 / 1.00, 0.39 | 0.88 / 0.95, 0.53 ; 0.76 / 1.00, 0.43 |
| C10 | 1.00 / 0.80, 0.03 ; 0.85 / 0.76, 0.35 | 1.00 / 0.84, 0 ; 0.83 / 0.87, 0.32 | 1.00 / 0.81, 0 ; 0.88 / 0.83, 0.10 |
| C11 | 1.00 / 0.93, 0 ; 1.00 / 0.98, 0 | 1.00 / 0.99, 0 ; 1.00 / 0.98, 0 | 1.00 / 0.92, 0 ; 0.92 / 0.88, 0.38 |
| C12 | 1.00 / 0.75, 0 ; 1.00 / 0.84, 0 | 1.00 / 0.85, 0 ; 1.00 / 0.85, 0 | 1.00 / 0.55, 0 ; 1.00 / 0.85, 0 |
| C13 | 0.97 / 0.76, 0.02 ; 1.00 / 1.00, 0 | 0.92 / 0.81, 0.03 ; 0.69 / 1.00, 0.08 | 1.00 / 0.74, 0 ; 1.00 / 1.00, 0 |
| M7 | 1.00 / 0.80, 0 ; 1.00 / 0.89, 0 | 1.00 / 0.88, 0 ; 1.00 / 0.89, 0 | 0.97 / 0.77, 0.03 ; 1.00 / 0.89, 0 |
| M8 (Step 10 truth: b not a group) | 0.80 / 0.98, 0.77 ; 0.74 / 1.00, 0.31 | 0.80 / 1.00, 0.34 ; 0.74 / 1.00, 0.21 | 0.75 / 1.00, 0.35 ; 0.74 / 0.99, 0.10 |

- **C9** is a robustness row (three-level tree), not a headline result.
- **C11 rep 2 (0.92, O4)** is not reliable, cause unknown.
- **Also not reliable, cause unknown** (reps disagree): C10 rep 2 under the frozen configuration (0.85 / 0.83 against 1.00), and C13 rep 2 at k = 3 (0.69 against 0.92).
- **Other rejected variants:**
  - O2 (in alarm during the event): 9 % false inclusion at leaf level;
  - O3 (onset within one base RTT before the event): no gain;
  - the 90 % containment matching: pair precision 0.75–0.91.

## 5. Re-scored v3 grouping blocks (scripts/grouping_score.py; all three methods)

**Setup.**
- 42 runs: C7, C8, C9, C10, C11, C12, C13, M7, M8 and the fq_codel cells of C7 / C9 / C10 / C12.
- Detector onsets. Scores averaged over every event close. Every value is rep 1 / rep 2.
- The fq_codel cells and the M8 fq_codel leaf (b) use the same-link truth.
- Full per-cell tables, with `*` marking "not reliable", are in `reports/sets-v1-2026-11-15/scores.md`.

**Single-queue AQM cells** (pfifo, codel, pie, mixab; 34 runs):

| method | leaf P | leaf R | leaf F1 | pair P | pair R | coverage | spurious / close | leaf F1 right after an upstream event | other closes |
|---|---|---|---|---|---|---|---|---|---|
| **SETS k2** | 0.84 / 0.85 | 0.82 / 0.85 | **0.83 / 0.84** | **0.99 / 0.97** | 0.91 / 0.92 | 0.86 / 0.88 | 0.79 / 0.71 | 0.90 / 0.88 | 0.83 / 0.86 |
| **SETS k3** | 0.77 / 0.77 | 0.76 / 0.80 | **0.76 / 0.78** | **0.98 / 0.95** | 0.95 / 0.95 | 0.81 / 0.84 | 0.50 / 0.48 | 0.84 / 0.78 | 0.76 / 0.79 |
| SETS k2 + crossing | 0.84 / 0.84 | 0.82 / 0.85 | 0.83 / 0.84 | 0.99 / 0.97 | 0.91 / 0.93 | 0.86 / 0.88 | 0.47 / 0.41 | 0.90 / 0.88 | 0.83 / 0.86 |
| SETS k3 + crossing | 0.77 / 0.77 | 0.76 / 0.79 | 0.76 / 0.78 | 0.97 / 0.95 | 0.95 / 0.95 | 0.81 / 0.83 | 0.27 / 0.27 | 0.84 / 0.78 | 0.76 / 0.78 |
| ECG | 0.74 / 0.69 | 0.71 / 0.79 | 0.72 / 0.72 | 0.92 / 0.68 | 0.97 / 0.98 | 0.75 / 0.76 | 0.07 / 0.01 | 0.74 / 0.72 | 0.71 / 0.73 |
| h3 | 0.77 / 0.81 | 0.75 / 0.78 | 0.74 / 0.78 | 0.81 / 0.84 | 0.61 / 0.75 | 0.81 / 0.86 | 0.78 / 0.52 | 0.79 / 0.78 | 0.72 / 0.79 |

**fq_codel cells, same-link truth** (8 runs):

| method | leaf F1 | pair P | pair R | spurious / close |
|---|---|---|---|---|
| SETS k2 | 0.70 / 0.69 | 0.26 / 0.34 | 0.42 / 0.38 | 2.19 / 3.05 |
| SETS k3 | 0.64 / 0.64 | 0.25 / 0.32 | 0.43 / 0.38 | 1.93 / 2.75 |
| ECG | 0.40 / 0.54 | 0.34 / 0.30 | 0.98 / 0.58 | 0.11 / 0.16 |
| h3 | 0.29 / 0.37 | 0.03 / 0.00 | 0.09 / 0.01 | 0.56 / 1.11 |

**Time to a leaf group with F1 ≥ 0.9, and late joiner** (all 42 runs):

| method | leaf events p50 | seconds p50 | leaves never found | late joiner joined | late: events / s p50 |
|---|---|---|---|---|---|
| SETS k2 | 3 / 3 | 102 / 84 | 3 of 44 / 4 of 43 | 33 of 36 / 34 of 38 | 9 / 8, 117 / 92 s |
| SETS k3 | 5 / 5 | 140 / 128 | 4 / 4 | 29 / 30 | 13 / 10, 152 / 130 s |
| ECG | 4 / 4 | 134 / 90 | 5 / 8 | 25 / 24 | 8 / 8, 84 / 94 s |
| h3 | 3 / 3 | 60 / 84 | 11 / 9 | 34 / 35 | 2 / 3, 53 / 47 s |

**Side table, mid / up / root F1** (all runs):

| method | mid | up | root |
|---|---|---|---|
| SETS k2 | 0.73 / 0.76 | 0.88 / 0.85 | 0.70 / 0.73 |
| SETS k3 | 0.67 / 0.71 | 0.84 / 0.79 | 0.60 / 0.68 |
| ECG | 0.51 / 0.54 | 0.58 / 0.69 | 0.51 / 0.60 |
| h3 | 0.60 / 0.64 | 0.61 / 0.60 | 0.53 / 0.58 |

**Reading:**
- **Single-queue cells.** SETS has the highest leaf F1 and pair precision. ECG has the fewest spurious groups. h3 finds leaves fastest when it finds them, but misses the most leaves (9–11 never found).
- **No method is damaged by upstream events.** Leaf F1 right after them is equal or higher.
- **fq_codel under the same-link truth.** SETS has the best leaf F1 there, but low pair precision (0.26–0.34): co-constrained sets of neighbouring sub-queues are merged.
- **"Not reliable" cells** (`*` in the full tables) for SETS k2 / k3 outside fq_codel: pair precision in C9 codel (1.00 / 0.89, 0.91 / 0.81) and C7 pfifo k = 3 (0.93 / 1.00).

**Regression.**
- `scripts/sets_replay.py check`: the engine reproduces the Step 9 / Step 10 values of the frozen configuration in **34 of 34 runs exactly**:
  - the per-close leaf P / R / F1 / exact;
  - the pair counts;
  - the spurious groups per close;
  - the end-of-run groups with support and mean Jaccard, at k = 2 and 3.
- **Per block and rep** the replay prints the same table as Step 10.
- **The single scorer** gives identical SETS numbers in 32 of 34 runs. The two differences are both M8 runs, and they are explained by the truth change of §2: the M8 fq_codel leaf b is now the same-link group {b3, b4}, where Step 10 had no group on b.
- The robustness column uses the GT1 egress rule; Step 10 used the queue-log rule, which Q1 showed to be identical on pfifo / codel.

## 6. Known limits

- **Upstream groups.** Nested upstream groups are out of scope (side table only).
- **Concurrent leaves.** Unions of repeatedly concurrent leaves (A∪C in C9, a∪b in M7) are not separated from a real upstream set.
- **Long continuous overload.** One continuous overload gives a single observation, and so no group at k = 2. Repetition is what makes a group (see the FlowBot note below).
- **Scale.** Validated only at the group sizes of the v3 runs (2–16 clients per group). The scale model of Steps 9 / 10 is not a scale test, and §7 measures cost, not accuracy.
- **No forgetting.** A client that leaves or changes branch keeps its old sets.
- **Fragments.** Under extra = 1, an observation with one flow more counts toward a smaller set, so a fragment seen once is reported with its parent's support (the "true set minus clients" spurious groups). Mean Jaccard flags them: groups below 0.85 are wrong in 90–100 % of cases.
- **Synthetic scenarios** (tests):
  - S1, S2, S3: exact;
  - S4: every leaf F1 ≥ 0.8;
  - S6: ≥ 2 of 4 leaves exact and every leaf F1 ≥ 0.6.

## 7. Cost benchmark (computational cost only, NOT accuracy)

`scripts/sets_bench.py`. Synthetic input:
- 100, 1000 and 10000 clients; leaves of 10–500;
- 0.1, 1 and 10 events per second over 600 s;
- the measured bursty miss pattern and 0.6 % false inclusion (M).

It measures time per event (the table update), time per read (groups at k = 2, at the end of the horizon) and memory, for exact matching and for the frozen matching. **It says nothing about how well groups are found at these sizes.**

| clients | group size | events / s | events | distinct sets | time per event (µs) | table (MB) | exact: read (s) / peak (MB) | frozen: read (s) / peak (MB) | frozen groups at k = 2 |
|---|---|---|---|---|---|---|---|---|---|
| 100 | 10 | 0.1 | 60 | 41 | 0.8 | 0.00 | 0.0000 / 0.00 | 0.014 / 0.05 | 21 |
| 100 | 10 | 1 | 600 | 312 | 0.6 | 0.01 | 0.0000 / 0.00 | 0.351 / 0.13 | 70 |
| 100 | 10 | 10 | 5998 | 2314 | 0.6 | 0.07 | 0.0001 / 0.00 | 28.283 / 1.80 | 503 |
| 100 | 50 | 0.1 | 60 | 20 | 1.0 | 0.00 | 0.0000 / 0.00 | 0.003 / 0.03 | 2 |
| 100 | 50 | 1 | 600 | 200 | 0.7 | 0.01 | 0.0000 / 0.00 | 0.144 / 0.11 | 5 |
| 100 | 50 | 10 | 6000 | 1609 | 0.7 | 0.07 | 0.0000 / 0.00 | 7.633 / 0.86 | 5 |
| 1000 | 10 | 0.1 | 60 | 60 | 0.6 | 0.00 | 0.0000 / 0.00 | 0.007 / 0.04 | 0 |
| 1000 | 10 | 1 | 600 | 600 | 0.4 | 0.02 | 0.0000 / 0.00 | 0.544 / 0.22 | 0 |
| 1000 | 10 | 10 | 6000 | 6000 | 0.5 | 0.28 | 0.0001 / 0.00 | 53.429 / 2.61 | 5 |
| 1000 | 50 | 0.1 | 60 | 60 | 0.7 | 0.00 | 0.0000 / 0.00 | 0.008 / 0.06 | 0 |
| 1000 | 50 | 1 | 600 | 600 | 0.5 | 0.02 | 0.0000 / 0.00 | 0.551 / 0.22 | 0 |
| 1000 | 50 | 10 | 6000 | 5987 | 0.5 | 0.28 | 0.0001 / 0.00 | > 300 s | - |
| 1000 | 100 | 0.1 | 60 | 60 | 0.7 | 0.00 | 0.0000 / 0.00 | 0.009 / 0.06 | 0 |
| 1000 | 100 | 1 | 600 | 600 | 0.6 | 0.02 | 0.0000 / 0.00 | 11.615 / 2.15 | 211 |
| 1000 | 100 | 10 | 6000 | 5982 | 0.7 | 0.28 | 0.0001 / 0.00 | > 300 s | - |
| 1000 | 500 | 0.1 | 60 | 53 | 1.6 | 0.00 | 0.0000 / 0.00 | 0.043 / 0.83 | 22 |
| 1000 | 500 | 1 | 600 | 486 | 1.8 | 0.02 | 0.0000 / 0.00 | 1.296 / 6.96 | 189 |
| 1000 | 500 | 10 | 6000 | 4251 | 2.1 | 0.14 | 0.0001 / 0.00 | 75.521 / 44.51 | 1215 |
| 10000 | 10 | 0.1 | 60 | 60 | 0.7 | 0.00 | 0.0000 / 0.00 | 0.011 / 0.24 | 0 |
| 10000 | 10 | 1 | 600 | 600 | 0.5 | 0.02 | 0.0000 / 0.00 | 1.129 / 1.30 | 0 |
| 10000 | 10 | 10 | 6000 | 6000 | 0.6 | 0.28 | 0.0001 / 0.00 | 109.508 / 9.53 | 0 |
| 10000 | 50 | 0.1 | 60 | 60 | 0.8 | 0.00 | 0.0000 / 0.00 | 0.014 / 0.29 | 0 |
| 10000 | 50 | 1 | 600 | 600 | 0.5 | 0.02 | 0.0000 / 0.00 | 1.144 / 1.32 | 0 |
| 10000 | 50 | 10 | 6000 | 6000 | 0.6 | 0.28 | 0.0001 / 0.00 | 109.826 / 9.53 | 0 |
| 10000 | 100 | 0.1 | 60 | 60 | 0.8 | 0.00 | 0.0000 / 0.00 | 0.018 / 0.63 | 0 |
| 10000 | 100 | 1 | 600 | 600 | 0.7 | 0.02 | 0.0000 / 0.00 | 1.160 / 1.32 | 0 |
| 10000 | 100 | 10 | 6000 | 6000 | 0.8 | 0.28 | 0.0001 / 0.00 | 109.515 / 9.53 | 0 |
| 10000 | 500 | 0.1 | 60 | 60 | 1.7 | 0.00 | 0.0000 / 0.00 | 0.039 / 0.63 | 0 |
| 10000 | 500 | 1 | 600 | 600 | 1.7 | 0.02 | 0.0000 / 0.00 | 1.423 / 1.32 | 0 |
| 10000 | 500 | 10 | 6000 | 6000 | 1.8 | 0.28 | 0.0001 / 0.00 | 122.903 / 9.57 | 0 |

**Reading** (pure Python, one core):
- **Time per event:** the table update at an event close takes 0.4–2 µs at every size.
- **Time per read:**
  - it grows with the square of the number of distinct stored sets, not with the number of clients;
  - about 600 distinct sets take 0.1–1.4 s per read;
  - about 6000 take 8–123 s;
  - two configurations (1000 clients, groups of 50 / 100, 10 events/s) exceed the 300 s cap.
- **Memory:** ≤ 0.3 MB of table, and a read peak of ≤ 45 MB.
- **Exact matching** (count only) reads in ≤ 0.1 ms.
- **Practical consequence.** At high event rates a read every event close is not affordable in this implementation. Reads have to be periodic, or the engine needs the C++ port noted below.
- **The "frozen groups at k = 2" column is not an accuracy result.** It is 0 wherever false inclusions make every observation distinct (1000+ clients). That matches the Step 9 / 10 model's finding that SETS reports only observed sets.

## 8. Testbed fix (before any new campaign)

**The problem.** Under fq_codel about 1 % of the unpinned background packets landed in a pinned client's sub-queue: fq_codel's own hash spreads them over all 1024 sub-queues.

**The fix** (`quiclab/orchestrator/shaping.py`, `flow_pin_commands`):
- a catch-all `flow hash ... divisor 768 baseclass 20:1` filter on the qdisc puts every unpinned packet on sub-queues 0–767, below the pinned ids (768 + i);
- it takes every protocol, so nothing is dropped as unclassified;
- each run now also writes `tc-filters.txt`.

**Verification** (to be run by the user; no run was started here):
- `scripts/tc_fq_pin_leak_probe.sh fixed`, and `old` for comparison (netns, docker): 2000 unpinned 5-tuples, pinned clients silent. PASS means no backlog on a client's class.
- One short run per topology: `scripts/fq_pin_short.py` writes 60 s scenarios (T-BASE, H-HIER, H-DEPTH, A-MIXED, mixab) and prints the `quiclab run` commands. Check each run with `scripts/fq_pin_check.py`.
- Existing v3 fq_codel runs stay flagged.
- **Probe result (2026-11-15, user run).** 6250 datagrams over 2000 unpinned 5-tuples, 70 class dumps.
  - `fixed`: unpinned backlog on classes ≤ 20:300 in 70 of 70 dumps, on a pinned client class in 0. PASS.
  - `old`: on a pinned client class in 40 of 70 dumps. LEAK.
  - The leak was real, and the catch-all closes it.
- **Short runs (2026-11-15, user run, `scripts/run_pinfix_short.sh`, `.runs/2026-11-15_2238_pinfix`).** All five topologies OK on `fq_pin_check.py`:
  - the catch-all filter is on every fq_codel egress (T-BASE 3 / 3, H-HIER 6 / 6, H-DEPTH 12 / 12, A-MIXED 11 / 11, mixab 1 / 1);
  - unpinned background is backlogged only on classes ≤ 20:300 (2 701–23 647 samples per run);
  - no backlog on any non-client class above 20:300.
  - The run data cannot show packets inside a client's own class; that part rests on the probe.
  - **The fix is verified.**
- **Not in the tagged commit.** The fix and its scripts are in the working tree, not in the `grouping-sets-v1.1` commit: `shaping.py`, `mininet_backend.py` and `test_shaping.py` also carry other uncommitted v3 testbed changes, so the fix is committed together with them.

## 9. Notes for later (not done now)

- **A C++ SETS engine**, to be implemented later.
- **FlowBot block.** It tests the weak point of the set method: congestion lasting 30 s without a break gives one observation, so no group at k = 2.
  - Report, per method, when it first groups within the first congestion, and what happens after 2, 3 and 4 repetitions.
  - The curve method (h3) may lead there. Decide only after seeing the result.
