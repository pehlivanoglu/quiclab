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
scripts/grouping_adapter.py   quiclab run -> onset log (shadow / OWD oracle / burst truth) -> engine -> metrics, spread
scripts/grouping_baselines.py SBD baselines (DCW, rmcatSBD, dcSBD) scored as grouping methods next to ECG
scripts/grouping_campaign.py  campaigns K1-K6: plan, run one after another, report per campaign when it finishes
configs/topologies/detector-tree8.yaml + configs/scenarios/grp-burst-tree8.yaml   K6 three-level tree (9 clients)
configs/topologies/detector-rev.yaml + configs/scenarios/grp-burst-rev.yaml   ACKs and a cross-traffic route share the router egress r1 -> r0 (K3 revcross)
configs/topologies/detector-access.yaml + configs/scenarios/det-burst-access.yaml   one access router per client: private bottlenecks (K5, isolate)
tests/unit/test_grouping.py   52 tests (alignment, clustering, weights, cases, scenarios, determinism)
tests/unit/test_grouping_tools.py  hierarchical pair truth, baseline scoring
tests/unit/test_grouping_campaign.py  planner: every type validates, seeded, windows vs events, join/leave rules
```

Grouping-only tooling: these scripts read `<run>/detector`, `<run>/publishers`
and `<run>/baselines` and write only under `<run>/grouping*/`. The shadow
detector is frozen (det_eval `TUNED`); nothing here changes it.

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
# oracle onsets: perfect delay detector on the OWD log / the burst truth itself
.venv/bin/python scripts/grouping_adapter.py RUN --onsets owd --set theta_J=0.6 theta_cov=0.6
.venv/bin/python scripts/grouping_adapter.py RUN --onsets truth --set theta_J=0.6 theta_cov=0.6
# SBD baselines next to the three ECG variants, same truth
.venv/bin/python scripts/grouping_baselines.py RUN...
.venv/bin/python -m pytest -q tests/unit/test_grouping.py tests/unit/test_grouping_tools.py
```

Outputs of the synthetic run land in `.runs/<ts>_grouping-synth/`: `table.md`,
`results.json`, and per cell `<S>/<profile>/seed<k>-{metrics.json,L.png}`
(`-evidence.jsonl` for seed 0). The adapter writes `<run>/grouping/` (shadow)
or `<run>/grouping-owd/`, `<run>/grouping-truth/`: `onsets.jsonl` (the log
the engine consumed), `truth.json`, `spread.csv`, `evidence.jsonl`,
`metrics.json`, `pairs_t.json` (pairwise decision after every event close),
`L.png`. The baseline scorer writes `<run>/grouping/baselines.json`.

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

## Testbed step 1: oracle onsets, split topology, SBD baselines

Three Mechanism-A sources separate the grouping rules from the detector
(`--onsets`): **shadow** (frozen tuned detector, alarms backdated as above),
**owd** (a perfect delay detector: `det_eval.measured_bands` on the exact OWD
log, a standing queue ≥ 10 ms for ≥ 0.5 s is an episode; no delay, no misses,
the real cross-flow spread stays; windows without receive timestamps are
unobservable), **truth** (every hit client fires at the burst start; aligned
spread 0: the tree logic alone). The difference truth → owd is the cost of
real onset spread and partial events, owd → shadow the cost of the detector.

Truth has two pair relations now. `pairs`: both hit by a common burst (share
some link). `pairs_leaf`: same *tightest* group, the intersection of every hit
set containing the client, so on the split topology `leaf(a1) = {a1,a2,a3}`
and the a–b pairs are DIFFERENT although upstream bursts hit both. ECG SAME
(same confirmed leaf) is scored against `pairs_leaf` (headline) and `pairs`.

`scripts/grouping_baselines.py` scores DCW, rmcatSBD and dcSBD (oracle OWD
input, `scripts/sbd_baselines.py`) on the same truth: *final* grouping = pair
grouped in ≥ half of the burst windows; `t_correct` = first time the running
grouping (ECG: tree at an event close; SBD: majority over the windows so far)
equals `pairs_leaf` on every pair and stays so for 5 s; window-level
precision/recall and the fraction of pairs grouped in calm windows (SBD's own
terms).

Runs with full OWD coverage (after the client PING fix) are only
`2026-11-03_2121_split-smoke/det-splitcap-pfifo-r1` (split: 3 + 3 clients,
bursts up / a / b / a+up, 30 bursts) and
`2026-11-03_1236_owd-ping-check/det-burstcap-pfifo-r1` (large, 8 clients).
The newscn-base and large campaigns lose OWD timestamps on the high-rate
clients mid-run (sub-g/h at ~63 s), so the owd source and the baselines are
not meaningful there until those campaigns are rerun.

| run | method | leaf P / R | t_correct (s) | cases / notes |
|---|---|---|---|---|
| split | ECG shadow | 1.0 / 1.0 | 245.6 | A 11, C 4, GLOBAL 9, SOLO 5 |
| split | ECG owd | 1.0 / 1.0 | 153.5 | A 13, C 6, GLOBAL 10 |
| split | ECG truth | 1.0 / 1.0 | 245.5 | A 10, C 4, GLOBAL 9 |
| split | DCW | 1.0 / 1.0 | 37.5 | windows P 0.80 R 0.62, 30 % of pairs grouped in calm windows |
| split | rmcatSBD / dcSBD | – / 0.0 | never | window recall 0.05 / 0.08: 1–4 s bursts are below their history |
| large | ECG shadow / owd / truth | 1.0 / 1.0 | 47.5 / 47.4 / 32.1 | one leaf of eight, ctrl out |
| large | DCW | 1.0 / 1.0 | 16.5 | 26 % of pairs grouped in calm windows |
| large | rmcatSBD / dcSBD | – / 0.0 | never | window recall 0.09 / 0.14 |

What the split run shows (all three sources agree, so it is the rules, not
the detector): the final tree is right — two leaves {a1,a2,a3}, {b1,b2,b3},
every upstream burst GLOBAL, a-only / b-only bursts case A. It is slow
because the scenario's first three bursts were all upstream: ECG correctly
built one six-flow leaf, and the first a-only bursts were case C
(sub-pattern) until `s_split_weight = 8` was reached (4 events). **During
those four events the silent b flows took the minority-rule `w⁻` and fell
below A**, and after the split they needed three b-only bursts to re-confirm
(first SAME for b pairs at 245 s; with the owd source 153 s). Rule
responsible: the Case C update applies the minority rule to the silent
members although the event is being recorded as a sub-pattern. A v1.2
candidate: when an event is recorded as a sub-pattern, do not charge the
silent members (or charge them only once the split is rejected). Not applied.
DCW is faster on this run because it groups instantaneously from the OWD
oracle, at the price of grouping 30 % of pairs in calm windows and of having
no hierarchy at all.

## Campaigns K1–K6 (`scripts/grouping_campaign.py`)

Shadow frozen, BBR only, rep = seed (same sequence on every AQM), calm u ≈ 0.65,
capacity drops unless noted, gaps U(10, 15) s. One command runs them back to
back and writes `<campaign>/<K>/report.md` the moment a campaign's last run
is done (adapter with the three onset sources, θ = 0.6, then the SBD scorer):

```bash
.venv/bin/python scripts/grouping_campaign.py --plan                  # YAMLs + budget, runs nothing
.venv/bin/python scripts/grouping_campaign.py --ks K1,K2,K3,K5,K6 --reps 3    # in tmux; ~10.4 h + setup
.venv/bin/python scripts/grouping_campaign.py --campaign .runs/<dir> --skip-existing   # resume
.venv/bin/python scripts/grouping_campaign.py --campaign .runs/<dir> --report-only --set theta_J=0.7 theta_cov=0.7
```

| K | topology | types | AQMs | runs (3 reps) | what it decides |
|---|---|---|---|---|---|
| K1 hier | split (3+3) | cells u {1.3, 2} × d {1, 2, 4} × {up, a, b, a+b, a+b@0.5, a+b@1, a+b@2, a+up} | 4 uniform + mixa (r1 pfifo / r2 fq_codel) + mixb (r1 fq_codel / r2 pfifo) + mixab (r1 pfifo; r2: branch a pfifo, branch b fq_codel) | 21 × 12.7 min | hierarchy (A / B / GLOBAL), false GLOBAL on simultaneous independent events, δ_max / hold on offsets, serial bottleneck |
| K2 part | detector | Poisson on/off capacity drops, u ∈ {1.05, 1.1, 1.15, 1.3} per run, on U(1, 4) s (15 % U(10, 20)), off U(5, 20) | pfifo (shared queue), fq_codel (per-flow queues: only clients above their fair share are hit) | 24 × 5 min | share of a leaf that alarms at light load → θ; long episodes |
| K3 rev | detector / detector-rev | revasym (reverse delays 5/40/80/120), revjit10, revcross (ACK-path bursts only, router egress r1 → r0 at 10 Mb/s), revcrossmix | pfifo, fq_codel (ACKs isolated: control) | 24 × 3–6 min | alignment error, false onsets from jitter, correlated false onsets from reverse congestion |
| K5 mixed | detector-access | shared cap bursts + per-client access router drops shuffled; sub-d joins at 60 s, sub-b leaves at 240 s | 4 | 12 × 6 min | private events leave the leaf alone, Case D→A for the joiner, the leaver's decay |
| K6 depth | tree8 (4 × 2) | {A, B, C, D, X, Y, root, A+C} | pfifo, fq_codel | 6 × 12.7 min | two-flow leaves, two-level LCA, A+C simultaneous |

"Mixed AQM" on the split topology: mixa / mixb differ upstream vs downstream
(r1 vs r2), mixab differs between the branches through r2's per-egress `egress`
override. det_eval's own model reads one AQM per run (the first router's), so
its detector tables are approximate on all three; the grouping truth below does
not use that model.

Truth for these runs is not det_eval's model: each run carries its stimulus
windows (`<run>/grouping/windows.json`, from the plan) and a client counts as
hit in a window when the OWD oracle shows a standing queue inside
[start, end + 2 s] **and** the plan expected that client (`expected` = the
clients behind the stimulated link; empty for reverse-path stimuli). The
second condition is needed for a+b / A+C: two links congested at the same
instant are indistinguishable on the oracle alone. `truth_of` picks this
source whenever `windows.json` exists, else `bursts.csv`, else topology.
Rechecked on the split-smoke run with plan-style windows: same final tree,
same P/R, same t_correct as with `bursts.csv`. The report adds a case matrix
(ECG event case × stimulus cell), which is the K1/K6 headline: `a+b` cells
must not be GLOBAL, `up`/`root` must.

det_eval.score still runs after every run (best effort, for the detector's
own tables). The replay's shared-group context is the client's leaf queue
(det_eval.leaf_queues), on every topology; on one-bottleneck topologies that
equals the old "first router egress". Without the replay binary the campaign
continues on the owd and truth sources: score the runs later, then --report-only.

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
  This is the chosen truth definition (2026-11-05): `pairs_leaf` asks whether
  clients congest together behind one stimulated link, not whether they share a
  queue. One window where b3 is hit without b2 makes that pair DIFFERENT, so a
  leaf of clients on one fq_codel egress can score as a false positive.
- Reverse-path congestion is grouped like forward congestion.
- Coincidence pairs (two noise onsets within δ) are the main source of
  junk structure at δ = 0.3 s; the SOLO pair rule removes them over time but
  they can briefly confirm. Single-bottleneck testbed runs cannot exercise
  the hierarchy at all.
