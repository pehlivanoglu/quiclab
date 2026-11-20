# SETS and NPR at the 300-client leaf (analysis only, 2026-11-19)

Input: the 300-client run (sim-Cs-G1-sburst-n300-pfifo-r1), its frozen v2-owd onsets at T100 read from the tick
cache; no new simulation. Code: `simulation/simlab/sets300_diag.py`; numbers: `sets-diag.json`. The NPR candidates
were imported read-only from `reports/npr-2026-11-17/frozen-2026-11-18/candidates.py`; nothing in that folder was
written (PYTHONDONTWRITEBYTECODE). One run, one seed, one generated cell.

**This run has one leaf.** It tests whether the leaf is found and kept whole. It says nothing about separating
leaves from each other.

## Answer

1. **Why the frozen SETS leaf group appears only at the 21st close (138 s)**, with no group before. The leaf is the
   same thing as "the 19th event" in the README (the scorer counts events touching the leaf). Two causes, both from
   the method:
   - **E0 events split every stimulus.** E0 groups onsets within 150 ms of the first one. The onset spread at this
     leaf is 280 ms p50, so 18 stimuli become 40 closes: one large set (252-299 members) and 1-4 fragments of
     1-48 members. 99.8 % of the members missing from an observed set (5,996 of 6,011, summed over closes) did have an onset in that stimulus, in another
     E0 event of it; only 0-9 per stimulus had no onset at all.
   - **SETS v1 needs a near-exact repeat to start.** m (the missing rate) is estimated from groups found at
     k_est = 2, and starts at 0. At m = 0 an observation counts toward a stored set S only if it contains all of S
     and at most 1 more flow. The first time this happened was close 21 (stimulus 7, 138 s): the first observation
     of all 300 members, which contains the 299-member set of stimulus 2. Before that, 18 stored sets
     (291, 252, 299, 293, 297, 260, 297, ... members) all differ by more than one flow in both directions.
   - At close 21, m jumps from 0 to 0.55. The q bound for a 300 set becomes 186 missing members, everything stored
     counts toward the leaf, and from then on the group is the exact leaf (20 / 20 closes).
2. **Method behaviour at this size, not something specific to the simulation.**
   - Fragmentation follows from the onset spread. The testbed's spread is wider than the simulation's at small leaves
     and similar at 16-24. At leaf 40 the testbed's p50 is already 165 ms, above the 150 ms E0 window.
   - The bootstrap needs one observation to contain another up to one flow. Its chance falls with leaf size
     whatever produces the misses.
   - If anything the simulation helps SETS here: 300 identical 500 kb/s clients with four access delays fire more
     synchronously than a heterogeneous testbed leaf would.
3. On E1-0.5 events (no fragmentation: 22 closes for 18 stimuli) the same SETS rule still waits for the second
   complete observation: first group at close 8 (stimulus 4, 90 s). The bootstrap delay remains; only the
   fragmentation part goes.
4. **NPR-A finds the leaf at the first stimulus and keeps it whole. NPR-B finds it as fast, but splits it** (a second
   and third group inside the leaf) in 10 of the 22 closes (closes 3-13).

## 1a. Frozen SETS on its own events (E0), per close

Columns:
- missing = leaf members not in the observed set, as (no onset in this stimulus / onset in another event of it);
- distinct = distinct sets stored;
- m, q = the estimate and the q bound for a 300 set;
- toward = the number of earlier stored sets this observation counts toward;
- k = 2 = groups / leaf F1.

| close | stimulus | t0 s | size | missing (none / other event) | distinct | m | q(300) | toward | k = 2 |
|---|---|---|---|---|---|---|---|---|---|
| 1-2 | before 1st | 11.6 | 4, 5 | 296, 295 | 1-2 | 0 | 0 | 0 | 0 / 0 |
| 3 | 0 | 15.0 | 291 | 9 (9 / 0) | 3 | 0 | 0 | 0 | 0 / 0 |
| 4-6 | 1 | 39.6-40.0 | 252, 36, 11 | 48 / 264 / 289 (1 / rest) | 4-6 | 0 | 0 | 0 | 0 / 0 |
| 7-8 | 2 | 60.3-60.5 | 299, 1 | 1 / 299 (0 / all) | 7 | 0 | 0 | 0 | 0 / 0 |
| 9-13 | 3 | 73.0-73.9 | 2, 293, 3, 1, 1 | (0 / all) | 8-10 | 0 | 0 | 0 | 0 / 0 |
| 14-15 | 4 | 89.9-90.1 | 297, 3 | (0 / all) | 11-12 | 0 | 0 | 0 | 0 / 0 |
| 16-18 | 5 | 110.8-111.1 | 260, 34, 5 | (1 / rest) | 13-15 | 0 | 0 | 0 | 0 / 0 |
| 19-20 | 6 | 124.5-124.8 | 297, 3 | (0 / all) | 16-17 | 0 | 0 | 0 | 0 / 0 |
| **21** | **7** | **138.0** | **300** | 0 | 18 | **0.554** | **186** | 1 (the 299 set of close 7) | **3 / 1.00** |
| 22-24 | 8 | 158.6-159.0 | 154, 125, 21 | (0 / all) | 19-21 | 0.55-0.57 | 185-191 | 4, 2, 0 | 4 / 1.00 |
| 25-40 | 9-17 | 175-318 | complete (300) at 9, 11, 14, 16, 17; split at 10, 12, 13, 15 | | 21-29 | 0.47-0.55 | 161-184 | 0-8 | 1 / 1.00 (exact) |

Closes 1-20: no group at k = 2 or 3. Closes 21-40: the exact leaf (plus 2-3 extra groups at closes 21-24, gone from
close 25). CPU of the engine replay with a group read at every close: 1.8 s.

FLAG (not testable on one leaf): after the bootstrap m stays near 0.5. An observation may then miss more than half
of a 300 set and still count toward it. Harmless with one leaf. With several leaves of very different sizes, a large
tolerance on the large sets could matter. That is a question for the multi-leaf stage C layouts.

## 1b. Frozen candidates on E1-0.5 events (22 closes)

E1-0.5 events: 18 stimuli give 16 complete or near-complete observations (291-300 members). Three stimuli are split
once (291 + 9, 294 + 6, 298 + 1); in each the small part has the large part's members as "in alarm" (NA).
False split: at a close, the leaf's members fall in two or more different smallest groups.

| candidate | first close with leaf F1 >= 0.9 (= exact) | mean leaf F1 over closes | pair P / R | false-split closes | CPU (all 22 closes) |
|---|---|---|---|---|---|
| SETS@E1-0.5, k = 2 (reference) | close 8, stimulus 4, 89.8 s | 0.68 | 1.00 / 1.00 | 0 | 0.01 s |
| SETS@E1-0.5, k = 3 | close 8, stimulus 4, 89.8 s | 0.68 | 1.00 / 1.00 | 0 | 0.00 s |
| NPR-A (m_max 0.20, f_max 0.05) | **close 2, stimulus 0, 15.0 s** | **0.96** | 1.00 / 1.00 | **0** | 0.02 s |
| NPR-B (frozen, past-fitted null) | **close 2, stimulus 0, 15.0 s** | 0.96 | 1.00 / 0.97 | **10** (closes 3-13) | 0.16 s |

Notes:
- Mean leaf F1 includes close 1, a 9-member event 3.5 s before the first stimulus. Both NPR readers put out one
  9-member group there (F1 0.06 against the leaf); SETS puts out none. From close 2 on, both NPR readers show the
  exact leaf at every close.
- NPR-B's false splits: 3 groups at closes 3-4 and 6-13; the leaf group itself stays present (exact) at every close.
  The two extra groups lie inside the leaf, so pair recall drops (smallest group). From close 14 on there is one
  group. Group sizes were not recorded.
- NPR-B with the frozen code took 0.16 s CPU for 22 events at 300 clients. No need to wait for the incremental
  version at this size.
- Pair precision / recall here count only pairs where both clients have a group (the common scorer's convention;
  ungrouped pairs are counted apart).

## 4. Where the SETS scoring time goes (cProfile; description only, nothing changed)

The 200 s "score_sets" step at 300 clients, profiled (478 s under the profiler):

| part | share of profiled time | grows with N as |
|---|---|---|
| building onsets: `grouping_adapter.build` | 95 % (453 of 478 s) | |
| ... of which GT3 truth recomputed inside it (`gt3.run_truth` -> `coverage` / `source_a`) | 77 % (370 s) | **N^2**: `det_eval.Run(rd)` is built 606 times (twice per flow), and each build re-parses the run's YAML, whose size grows with N |
| ... of which the frozen detector's CUSUM over 301 flows | 13 % (61 s) | N |
| SETS replay + group reads + scorer (`r1.run_level` minus build) | 5 % (25 s) | |
| the scorer's pair loop alone (measured separately: 40 closes, one group = the leaf) | 2.5 s CPU | **N^2** per close |
| SETS method itself (1a replay with a group read at each close) | 1.8 s CPU | in stored sets, not in N |

- So at 300 clients the time is neither the method nor the pair loop: it is reading inputs. Repeated YAML parsing in
  `det_eval.Run` costs 0.16 s per build at 300 clients (measured). By extrapolation that is ~0.55 s x ~2,000 builds
  ≈ 18 min per scoring call at 1,000 clients and ~30 h at 10,000. GT3 scoring has the same pattern.
- The pair loop: 61 ms per close at 300, ~0.7 s at 1,000, ~70 s at 10,000 (N^2).
- **Pair counts from group sizes, with no reported number changed:**
  - **Requires:** true leaves are disjoint (each client is in at most one leaf: `same` is then "both in the same
    leaf"), and the smallest-group choice per client stays exactly as now (same tie-break).
  - **Counts:** n(g, L) = the number of clients whose smallest group is g and whose leaf is L, and N_grouped = the
    clients with a group.
  - **Formulas:**
    - pairs[0] = sum over g and L of C(n(g, L), 2);
    - pairs[1] = sum over g of C(n(g), 2) minus pairs[0];
    - pairs[2] = sum over L of C(n_grouped(L), 2) minus pairs[0];
    - pairs[3] = C(N_grouped, 2) minus pairs[0] minus pairs[1] minus pairs[2];
    - pairs[4] = C(N, 2) minus C(N_grouped, 2).
  - These are integer identities: the same five counts, in O(N + groups x leaves) instead of O(N^2) per close.
  - **To check before any use:** that the scorer's truth leaves are disjoint for every layout. The uneven layout and
    the hierarchical truth sets are where this could fail; there the formulas would need the leaf-of-client map
    instead.
