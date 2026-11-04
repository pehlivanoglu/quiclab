# ECG — Event Co-occurrence Grouping (Phase 1 + testbed step 0)

Shared-bottleneck grouping from per-flow congestion onsets, implemented from
`grouping-implementation-v01.md` (brief v1.1). Engine, synthetic harness,
replay/metrics, invariants, and an adapter that feeds the shadow detector's
alarms from real quiclab runs into the engine.

```
grouping/
  config.py      Config: defaults of brief §7, from_dict / from_json, derived delta_max, sigma_min, L_cap
  types.py       Onset, ObsSample, FlowMeta, Node, FlowState, outputs
  engine.py      the ECG engine (§4-§6) + JsonlLogger
  synth.py       generator, detection-delay profiles, scenarios S1-S6
  replay.py      run(records) -> Result, metrics (§8.4), pass criteria (§8.2), L plot
  invariants.py  §8.3 invariants checked after every event
scripts/grouping_synth.py     scenarios x profiles x seeds (+ sweeps) -> table.md, metrics, L plots
scripts/grouping_adapter.py   quiclab run -> onset log (shadow alarms) -> engine -> metrics, spread
tests/unit/test_grouping.py   52 tests (alignment, clustering, weights, cases, scenarios, determinism)
```

## Running

```bash
# all six scenarios, both profiles, 10 seeds, default config
.venv/bin/python scripts/grouping_synth.py
# the theta sweep reported below
.venv/bin/python scripts/grouping_synth.py --sweep theta_J=0.7,0.6 --sweep theta_cov=0.7,0.6
# one cell, keep the onset logs
.venv/bin/python scripts/grouping_synth.py --scenarios S4 --profiles realistic --seeds 3 --write-log
# real runs: shadow alarms -> ECG, plus the per-burst onset-spread measurement
.venv/bin/python scripts/grouping_adapter.py .runs/<campaign>/det-burstcap-pfifo-r1 --set theta_J=0.6 theta_cov=0.6
.venv/bin/python scripts/grouping_adapter.py ".runs/<campaign>/det-*-r1" --spread-only
.venv/bin/python -m pytest -q tests/unit/test_grouping.py
```

Outputs of the synthetic run land in `.runs/<ts>_grouping-synth/`: `table.md`,
`results.json`, and per cell `<S>/<profile>/seed<k>-{metrics.json,L.png}`
(`-evidence.jsonl` for seed 0). The adapter writes `<run>/grouping/`:
`onsets.jsonl` (the log the engine consumed), `truth.json`, `spread.csv`,
`evidence.jsonl`, `metrics.json`, `L.png`.

## Reading the L plots

One line per flow: `L[f, node]`, the membership log-odds toward the flow's
current leaf, after each event close. Dashed line `A ≈ 4.55` (member), dotted
`B ≈ −2.99` (not a member); between them the flow is *uncertain*. A dot marks
an event where the flow changed node (joined, migrated, or left); the line is
broken there. `L` is capped at `L_cap = 2A ≈ 9.1`. Flat stretches are decay
only (`exp(−10/300)` per 10 s). A healthy leaf: all members rise to the cap
within 2–3 events and stay there; a private episode shows as a `−0.79` step
(SOLO); a path change shows as a staircase down by `w⁻ ≈ −1.5` per missed
event followed by a jump onto the new leaf.

## Pass/fail table (10 seeds, 300 s, both profiles)

From `scripts/grouping_synth.py --sweep theta_J=0.7,0.6 --sweep theta_cov=0.7,0.6`
(`.runs/2026-11-03_*_grouping-synth/table.md`). Defaults are the brief's;
`θ=0.6` is the sweep value the brief allows (range 0.6–0.8).

| scenario | ideal, θ=0.7 | realistic, θ=0.7 | ideal, θ=0.6 | realistic, θ=0.6 | why it fails (rule responsible) |
|---|---|---|---|---|---|
| S1 one_leaf | 7/10 | 8/10 | 6/10 | 6/10 | median events-to-leaf = 2. "All three flows after ≤ 3 events" needs every flow to fire in two of the first three events; with `p_miss = 0.1` and the per-event cap that holds in ≈ 0.92 of seeds. Failing seeds reach the leaf after 4–6 events; no false leaf in any seed. |
| S2 independent | 10/10 | 8/10 | 10/10 | 8/10 | failing seeds: two coincidences of the two Poisson streams inside the same decay period (`δ = 0.3` gives ≈ 1.8 coincidences per 300 s run); both capped weights sum to ≥ A. The SOLO rule (below) undoes it within a few onsets, so the pair is never *confirmed-and-stable*, but the criterion is "never reaches A". |
| S3 shared_plus_private | 8/10 | 9/10 | 9/10 | 9/10 | `private_fraction` within ±0.03 of truth when noise onsets count as private (they are solo onsets). Failing seeds: flow 1 drifts below A late in the run when its private stimuli outnumber shared ones in a stretch (solo penalty `0.5·w⁻` per private episode vs `+w⁺` per shared one). |
| S4 two_leaves_one_parent | 2/10 | 1/10 | 7/10 | 9/10 | at θ=0.7 one missed flow in a 3-flow leaf gives `cov = 2/3 < 0.7`; the aggregation event is not case B, falls to D and creates a 5-flow junk leaf that then competes with the true leaves. At θ=0.6 the remaining failures are a GLOBAL event classified B because one leaf had two misses (≈ 1 % per leaf-event). |
| S5 noise_idle_migrate | 0/10 | 0/10 | 0/10 | 0/10 | (a) the noisy flow (0.2 /s) joins (median 4–7 events) and then **leaves again**: the spec's SOLO penalty (`0.5·w⁻` per solo onset, ≈ 6 per 30 s) outweighs `+w⁺` per shared event (1 per 30 s). So leaf A ends as {f1, f3} and the "leaf A = {f1,f2,f3}" criterion fails in every seed. (b) idle flow: no `apart` while idle in 10/10 seeds, member throughout in 9–10/10. (c) migration by the 3rd B event: 1–5/10; it happens, but later, because leaf A still contains f2 noise and f5 idle leaves B with two observable flows (pair rules below). |
| S6 four_leaves_two_parents | 0/10 | 0/10 | 4/10 | 0/10 | with 12 flows a root-level event has a miss in ≈ 72 % of cases; any leaf still provisional as a **pair** (third flow missed its first event) then has `cov = 0.5` and the event is case B over the other leaves, creating an extra internal node. Coincidence pairs across groups (two noise onsets within δ) confirm as false leaves in 2–5/10 realistic seeds. G1/G2 events are case B in nearly all seeds and the two correct internal nodes exist whenever no spurious one is created. |

Invariants (§8.3) hold in every run of every cell (checked after every event;
`invariants_checked` in each metrics file). Replay is byte-identical (test).

**Recommendation for v1.2:** `theta_J = theta_cov = 0.6` (tolerates one miss
in three), a solo penalty scaled by the flow's own background rate (so a noisy
flow is not expelled by its noise), and a minimum of two co-occurrences before
a *pair* may take part in case B / GLOBAL decisions. None of these were
applied to the defaults.

## Testbed step 0 (existing runs, shadow as Mechanism A)

`scripts/grouping_adapter.py` on the newscn-base and large campaigns (BBR,
single shared bottleneck + control client; see `metrics.json` under each run):

- **Onset spread per burst** (hit clients, same burst): alarm times spread
  p50 ≈ 220–290 ms, p90 ≈ 500–1100 ms. Backdating each alarm to the start of
  the sustained queue-delay rise (`queue_delay_ms` rolling median ≥ 10 ms)
  brings it to **p50 ≈ 70–95 ms, p90 ≈ 120–510 ms** (large burstcap pfifo
  95/510, fq_codel 68/119, base bursttiny 68/119). The median backdate is
  ≈ 290 ms, consistent with the ≈ 350 ms detector floor measured earlier.
  `δ = 0.3`, `δ_max = 0.6`, `hold = 1.0` therefore stay. Ramp scenarios are
  not synchronous events (clients cross the threshold at different steps,
  spread 1.5–7 s) and are not what this layer is for.
- **Grouping** (42 r1 runs, θ = 0.6): on every burst run the shared clients
  form one leaf and `sub-ctrl` stays out (pairwise precision = recall = 1.0 in
  every burst run; coverage median 0.58, the rest uncertain because
  `sub-ctrl` never earns a node). TCP runs group the four shared clients too
  (truth falls back to topology there: no hit labels). Ramps under red/pfifo
  on the large topology fragment into pairs (clients cross the threshold
  seconds apart, so there is no co-occurring event to learn from). Under fq_codel
  the leaf holds only the over-share clients (sub-a at 1 Mb/s never congests),
  which is the intended semantics. `isolate` runs produce only SOLO/PRIVATE
  events and no leaf. These topologies cannot test the hierarchy: that needs
  the split topology campaign (TODO).

## Ambiguities in the brief and how they were resolved

1. **Provisional leaf members vs invariant 6.** Case D says the new leaf has
   `members = M` while flows "stay in their current leaf"; invariant 6 counts
   each flow once. Resolution: a case D leaf holds `M` as *candidates*;
   matching (`J`, `cov`, `n_obs`) uses `members ∪ candidates`; a flow becomes
   a member only through the §6.4 transition.
2. **`A/2` cap and "two co-occurrences".** Two capped events sum to exactly
   `A`; the 10 s decay (×0.967) breaks the equality, so two events never
   sufficed. `w_cap_frac = 0.55` (config) keeps "no single event creates a
   membership" and makes two events enough.
3. **Unbounded L vs migration.** With `L` unbounded a flow that moved links
   could never be overtaken by a new candidate (`cand > L`). `L` and `cand`
   are clipped at `L_cap = 2A` (config).
4. **Observability for a flow that fired.** If the producer folds
   `in_episode` into `observable`, a flow that fired at `t0` is observable in
   only half of `[t0−δ, t0+δ]`. Producers emit "sending" only; the engine
   applies the `in_episode` test at `t0−δ` (§4.3).
5. **Second onset while in episode.** The onset arrives after its episode
   has started (detector latency), so "ignore while `in_episode`" would drop
   every onset. The engine ignores an onset only while a previously accepted
   onset's episode is still open.
6. **GLOBAL.** Also GLOBAL when an event covers *all* existing leaves (not
   only all confirmed ones): at cold start such an event says nothing about
   structure, and creating an internal node over every leaf is the root
   again. GLOBAL events add root support only — no within-leaf updates: an
   event that hits every leaf carries no information about leaf membership
   (the brief applies the within-leaf updates; that made migration
   undetectable because every G event refreshed the old membership).
7. **Case order.** Case B is evaluated before case A: an aggregation event
   with one missed flow otherwise matches the fully fired leaf as case A
   (`J = 3/5`) and turns the other leaf's flows into its candidates.
8. **Overlapping leaves in case B.** Leaves that share flows (members or
   unassigned candidates) are competing hypotheses, not a hierarchy. Among
   covered leaves the better supported one wins (confirmed first, then
   support); the loser gets nothing. A member of A that is a candidate of B
   is a possible migration, not an overlap.
9. **Coverage of tiny leaves.** A leaf with fewer than two observable flows
   is never "covered" and cannot vote on GLOBAL (one flow firing is not group
   evidence); the same minimum applies to case A-superset.
10. **SOLO and pairs.** A SOLO event applies the minority rule to the leaves
    the flow belongs to or is a candidate of: with ≥ 2 other observable flows
    the soloist gets `0.5·w⁻` (as in the brief); with exactly one other
    observable flow that silent flow gets `w⁻`. Without the second clause a
    provisional pair from a coincidence could never receive negative evidence
    (the brief's SOLO rule needs two other members).
11. **Candidate negative evidence** is applied in cases A, A-superset and B
    only when the group as a whole fired (`k ≥ m/2`); not in case C.
12. **Transitions into internal nodes.** The brief says to create a
    single-flow leaf under the internal node, which the dissolution rule
    (`< 2 members`) would remove at once. Candidates on internal nodes are
    kept (they appear in `query().ancestors` and in the metrics) but
    transitions only target leaves.
13. **Split support.** After a case C split, `n_a` (the recurring subset)
    takes the sub-pattern weight as support, `n_b` inherits the parent's.
14. **Decay of `together` / `apart`.** Both decay with `solo`, otherwise
    `private_fraction` drifts to 0 on a steady private share.
15. **Dissolution.** Members of a dissolved leaf get `L = 0` (and are exempt
    from invariant 3 for that event); candidates lose their entry. Internal
    nodes whose children were reparented by a case B event are spliced.
16. **Invariant 4** is checked as "no two leaves merge" (no leaf afterwards
    holds ≥ 2 members from each of two earlier leaves): a flow may still
    migrate, join its own leaf, or drop to uncertain during a B event.
17. **S3 truth.** Noise onsets are solo onsets; `private_fraction` is
    compared with the share of flow-1 episodes *not* caused by the shared
    link (the P-only share is reported alongside).
18. **S5 / S6 stimulus gaps** are not given in the brief: S4/S5 cycle A/B/G
    with U(8, 12) s, S6 cycles seven resources with U(5, 8) s.
19. **Realistic `d_f`** is drawn U(0.1, 0.5) s and scaled by
    `0.5 + 0.5·(1 − rendition/max)` (higher rendition, earlier detection).
20. The synthetic table includes an `exact` profile (no jitter) used by the
    unit tests only.

## Known limits (brief §11, plus what the runs showed)

- Timing co-occurrence cannot separate one shared queue from two queues
  driven by the same external process.
- Under FQ-CoDel the hit set depends on severity; groups are
  severity-dependent (seen on the large fq_codel runs: 6–7 of 8 clients).
- Reverse-path congestion is grouped like forward congestion.
- Coincidence pairs (two noise onsets within δ) are the main source of
  junk structure at δ = 0.3 s; the SOLO pair rule removes them over time but
  they can briefly confirm. Single-bottleneck testbed runs cannot exercise
  the hierarchy at all.
