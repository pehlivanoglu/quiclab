# SETS v1: frozen grouping configuration (2026-11-15)

**Frozen:** SETS with observed set O1 and the "old" matching rule of Step 9.

- **Code:** `grouping/sets.py` (matching), `grouping/sets_engine.py` (`SetsEngine`).
- **Tests:** `tests/unit/test_grouping_sets.py`.
- **Replay check:** `scripts/sets_replay.py check`, against `tests/data/sets_v1_expected.json`.
- **Git tag:** `grouping-sets-v1` (the commit that adds this note).
- **ECG v1.2 and h3** stay as comparison methods, frozen as they are, with no further development.

Evidence: `reports/step8-2026-11-15/`, `reports/step9-2026-11-15/`, `reports/step10-2026-11-15/`.

## 1. Definition

**Event formation.** Inherited unchanged from the ECG engine (`grouping.Engine`):
- onsets are aligned by half the flow's minimum RTT and clustered into events (constants in §2);
- an onset while the flow is already in an episode is ignored;
- an event closes `delta_max + hold` after its first aligned onset.

**Observed set (O1).** At each event close, the flows with an onset in the event, minus the control flow `sub-ctrl`.
- An onset implies the detector observed the flow; no further observability filter is applied (as in Steps 8–10).
- Sets of fewer than 2 flows are not stored.

**State.** A table of distinct observed sets and their counts. Nothing else: no per-flow evidence, no merging, no splitting, no decay.

**Matching (the old rule, Step 9, `quantile` path).** S' counts toward S when
- |S' − S| ≤ EXTRA, and
- |S − S'| ≤ q(|S|, m), where q is the Q quantile of Binomial(|S|, m).

**Miss rate m.** Estimated from the table:
1. start at m = 0;
2. assign every stored set to the smallest group (at k = K_EST) that contains it up to EXTRA extra flows;
3. m = missing (flow, observation) pairs / all (flow, observation) pairs of those assignments;
4. recompute the groups with the new m and repeat until the change is < M_TOL, or for at most M_ITERS rounds.

**Output.** Computed from the table at every read, so it is independent of the order of events:
- **Groups:** every stored set with support ≥ k that does not count toward a stored set with a higher count.
  - Support = the summed counts of the sets counted toward it.
  - Each group is reported with its support and its mean Jaccard (count-weighted |S ∩ S'| / |S ∪ S'| over the sets counted toward it).
- **Tree:** the inclusion order of the groups. A group's parent is the smallest group that strictly contains it.
- **Membership:** a client belongs to every group that contains it, smallest first.

**No single k is frozen.** Results are reported at k = 2 and k = 3 side by side.

**Ties** are broken by the order of the sets as bitmasks over the sorted flow names, exactly as in Step 9.

## 2. Constants

| constant | value | tag | where |
|---|---|---|---|
| Q (binomial quantile of misses) | 0.99 | T | `grouping/sets.py` |
| EXTRA (flows allowed outside the set) | 1 | FLAG | `grouping/sets.py` |
| M_TOL (m convergence) | 1e-4 | M | `grouping/sets.py` |
| M_ITERS (m rounds) | 30 | M | `grouping/sets.py` |
| K_EST (k used while estimating m) | 2 | M | `grouping/sets.py` |
| MIN_SET (smallest stored set) | 2 flows | M | `grouping/sets.py` |
| k for reporting | 2 and 3, side by side | not frozen | |
| delta (onset co-occurrence tolerance, aligned time; inherited) | 0.150 s | P (user decision 2026-11-11) | `grouping/config.py` |
| delta_max (max event span, = 2 delta; inherited) | 0.300 s | M | `grouping/config.py` |
| hold (wait after t0 + delta_max for late detectors; inherited) | 1.0 s | M | `grouping/config.py` |
| align_mode (inherited) | half_mrtt | M | `grouping/config.py` |
| obs_window (tick and observation window; inherited) | 0.020 s | M | `grouping/config.py` |
| in-episode rule (second onset in an episode ignored; inherited) | on | M | `grouping/engine.py` |
| excluded flows | `sub-ctrl` | M | caller (`exclude=`) |
| onset source | frozen Shadow v2 (ip4 values), OWD | frozen detector | `scripts/shadow_v2_frozen.py` |
| acceptance condition (set before the numbers were seen) | pair precision ≥ 0.93 in both reps | P | this note |
| "group found" threshold in the time-to-group scores | F1 ≥ 0.9 | FLAG | Step 9 / 10 scoring |

ECG's evidence, tree, decay and matching constants (`A`, `B`, `tau`, `decay_period`, `theta_*`, …) are not used by SETS.

## 3. Why this configuration (decided 2026-11-15)

**Acceptance condition.** It was set before the numbers were seen: pair precision (same-leaf truth, from each client's smallest group, summed over every event close) ≥ 0.93 in both reps.
- O1 + old meets it at k = 2 (0.987 / 0.965) and k = 3 (0.972 / 0.949).
- O4 + old does not (0.961 / 0.896).

**Why O4 was rejected.** O4 gains 0.01–0.02 leaf F1 and costs false pairs, which are the more expensive error: clients of different leaves in one group cost more than a spurious fragment of a real leaf. O4 also needs a hand-picked 0.3 s window; O1 needs none.

**Why the new matching was rejected.** It lowers pair precision to 0.75–0.91.

**Pair precision / recall, same-leaf truth, 34 v3 runs, detector onsets** (rep 1 / rep 2):

| configuration | P | R | status |
|---|---|---|---|
| **O1 + old, k = 2** | **0.987 / 0.965** | **0.908 / 0.927** | **frozen** |
| **O1 + old, k = 3** | **0.972 / 0.949** | **0.953 / 0.956** | **frozen** |
| O4 + old, k = 2 | 0.961 / 0.896 | 0.860 / 0.883 | rejected: precision < 0.93 in rep 2 |
| O4 + old, k = 3 | 0.938 / 0.900 | 0.923 / 0.947 | rejected: precision < 0.93 in rep 2 |
| O4 + new, k = 2 | 0.831 / 0.754 | 0.949 / 0.990 | rejected: false pairs |
| O1 + new, k = 2 | 0.912 / 0.855 | 0.982 / 0.990 | rejected: false pairs |

Leaf F1 of the frozen configuration (best-matching group per leaf, mean over closes): k = 2 0.83 / 0.85, k = 3 0.76 / 0.78. For comparison, ECG 0.73 / 0.73 and h3 0.75 / 0.78 (Step 10 C1).

**Per block, pair precision / recall and the block's share of all false pairs** (rep 1 ; rep 2):

| block | O1 + old k = 2 (frozen) | O1 + old k = 3 (frozen) | O4 + old k = 2 (rejected) |
|---|---|---|---|
| C7 | 0.99 / 0.87, 0.18 ; 1.00 / 0.81, 0 | 0.94 / 0.91, 0.34 ; 1.00 / 0.89, 0 | 1.00 / 0.81, 0 ; 1.00 / 0.74, 0 |
| C8 | 1.00 / 0.97, 0 ; 0.96 / 0.86, 0.06 | 1.00 / 0.98, 0 ; 1.00 / 1.00, 0 | 0.91 / 0.51, 0.09 ; 1.00 / 0.98, 0 |
| C9 (robustness row) | 1.00 / 0.96, 0 ; 0.93 / 0.99, 0.28 | 0.94 / 0.97, 0.28 ; 0.86 / 1.00, 0.39 | 0.88 / 0.95, 0.53 ; 0.76 / 1.00, 0.43 |
| C10 | 1.00 / 0.80, 0.03 ; **0.85** / 0.76, 0.35 | 1.00 / 0.84, 0 ; **0.83** / 0.87, 0.32 | 1.00 / 0.81, 0 ; 0.88 / 0.83, 0.10 |
| C11 | 1.00 / 0.93, 0 ; 1.00 / 0.98, 0 | 1.00 / 0.99, 0 ; 1.00 / 0.98, 0 | 1.00 / 0.92, 0 ; **0.92** / 0.88, 0.38 |
| C12 | 1.00 / 0.75, 0 ; 1.00 / 0.84, 0 | 1.00 / 0.85, 0 ; 1.00 / 0.85, 0 | 1.00 / 0.55, 0 ; 1.00 / 0.85, 0 |
| C13 | 0.97 / 0.76, 0.02 ; 1.00 / 1.00, 0 | 0.92 / 0.81, 0.03 ; **0.69** / 1.00, 0.08 | 1.00 / 0.74, 0 ; 1.00 / 1.00, 0 |
| M7 | 1.00 / 0.80, 0 ; 1.00 / 0.89, 0 | 1.00 / 0.88, 0 ; 1.00 / 0.89, 0 | 0.97 / 0.77, 0.03 ; 1.00 / 0.89, 0 |
| M8 (see §5) | 0.80 / 0.98, 0.77 ; 0.74 / 1.00, 0.31 | 0.80 / 1.00, 0.34 ; 0.74 / 1.00, 0.21 | 0.75 / 1.00, 0.35 ; 0.74 / 0.99, 0.10 |

- **C9** is a robustness row (three-level tree), not a headline result.
- **C11 rep 2** under O4 (0.92) is not reliable, cause unknown. The variant is rejected; O1 has 1.00 there.
- **Also not reliable, cause unknown** (reps disagree): C10 rep 2 under O1 (0.85 / 0.83 against 1.00 in rep 1), and C13 rep 2 at k = 3 (0.69 against 0.92).
- **Rejected variants and why:**
  - O2 (in alarm during the event) pulls in clients alarmed for another reason: 9 % false inclusion at leaf level.
  - O3 (onset within one base RTT before the event) changes nothing.
  - O4 fails the acceptance condition.
  - The new matching (per-group m from participation, measured extra-flow allowance) and the 90 % containment matching lower pair precision to 0.75–0.91.

## 4. Known limits

- **Upstream groups.** Nested upstream groups (mid / up / root) are out of scope. They are reported as a side table only. Leaf groups are the result; upstream events do not damage them (Step 10 C3: leaf F1 right after an upstream event −0.06 … +0.09 against other closes).
- **Concurrent leaves.** Unions of repeatedly concurrent leaves (two leaves congested together again and again, e.g. A∪C in C9, a∪b in M7) are not separated from a real upstream set. This is a stated limitation (Step 9 D).
- **Fragments.** Under EXTRA = 1, an observation with one flow more counts toward a smaller set, so a fragment of a leaf seen once is reported with the leaf's support. These are the "true set minus clients" spurious groups (Step 9 B2; test `test_extra_flow_rule_lets_a_superset_count_toward_a_fragment`). The mean Jaccard is the second confidence value for them: groups below 0.85 are wrong in 90–100 % of cases (Step 9 A6).
- **Scale.** Validated only up to the group sizes in the v3 runs (2–16 clients per group). The scale model of Steps 9 / 10 is a model, not a scale test. It holds at 200–900 clients only under the measured bursty miss pattern and fails under independent misses, because SETS reports only observed sets.
- **No forgetting yet.** A client that leaves or changes branch keeps its old sets (synthetic S5 migration).
- **Synthetic scenarios** (tests):
  - S1, S2, S3: exact;
  - S4: every leaf F1 ≥ 0.8;
  - S6: ≥ 2 of 4 leaves exact and every leaf F1 ≥ 0.6. A leaf can be seen only inside its aggregation set.

## 5. Open decision (the user's): per-flow-queue cells

How fq_codel / cake cells are scored is open: same queue (every group there is false) or same link (clients constrained together at the egress). Both readings are kept in the reports.

**M8's false pairs** above are b–b pairs on the fq_codel branch, scored here as false because the b leaf is not an ordinary queue. **They depend on this decision.**

## 6. Reproduction

- **Engine.** `SetsEngine(cfg, exclude={"sub-ctrl"})` fed by `grouping.sets_engine.replay_log(<run>/grouping-d150-v2-owd/onsets.jsonl, Config.from_dict(metrics.json["config"]))`. It reproduces each run's ECG events (members identical) and the Step 9 / Step 10 values.
- **Replay check** (`scripts/sets_replay.py check`): 34 of 34 runs reproduce exactly:
  - the per-close leaf scores and pair counts at k = 2 and 3;
  - the end-of-run groups with support and mean Jaccard;
  - the pooled pair precision / recall 0.987 / 0.965 (k = 2) and 0.972 / 0.949 (k = 3).
