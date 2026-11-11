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

**Rule set: v1.2 is the default since 2026-11-10** (`Config` defaults =
`Config.V12`; `Config.V11` / `--v11` reproduce the brief v1.1 tables). The
rules are frozen at this state; the next campaign is scored without touching
them (see "Frozen definitions" below).

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

## Campaigns K1–K6 as run on 2026-11-06 (`scripts/grouping_campaign.py`; v2 changes below)

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

## Campaign results (v1.1, `.runs/old/ip8/2026-11-06_1526_grp`, 85 runs) and the v1.2 rules

Scored with θ = 0.6 and the corrected leaf truth (`leaf_groups`: intersection of
the *expected* sets of the shared windows a client was hit in; private windows
and partial fq_codel hits no longer shrink a client's group to itself). Reports:
`<campaign>/<K>/report.md` (v1.1) and `report-v12.md` (v1.2 re-score of the
same runs). Headline rows (median leaf P / R, t_correct s, shadow onsets):

| K | cell | v1.1 | what it showed |
|---|---|---|---|
| K1 | pfifo / pie / red (8 runs) | 1.0 / 1.0, 130–143 s | two leaves + GLOBAL on `up` and `a+up`; `a+b` simultaneous → GLOBAL (harmless: root support only); `a+b@0.5…2` separated (δ_max / hold) |
| K1 | fq_codel, mixa, mixab | 1.0 / 1.0 on few pairs, coverage 0.14–0.29 | 1 Mb/s clients never congest; **r2: confirmed cross-branch pair {a2,b2}** (L 8.7 / 9.1) |
| K2 | pfifo, all u | 1.0 / 1.0, 39–66 s | FIFO hits every client even at u 1.05 (oracle hit share 1.0) |
| K2 | fq_codel u ≤ 1.15 | no leaf | onsets spread 0.5–8 s, 1–3 of 4 clients queue: no shared *event* exists (OWD source agrees) |
| K3 | revasym, revjit10 | 1.0 / 1.0 | reverse asymmetry / 10 ms jitter: spread ×2 / ×5, grouping intact |
| K3 | revcross (pfifo) | false 4-client leaf in 3/3 (shadow); none with OWD onsets | detector confound (RTT), not grouping |
| K5 | pfifo / pie / red | 1.0 / 1.0, cov 0.1–0.3 | 203 of 204 private windows → SOLO; only 6 shared windows per run (too few; plan now has 12) |
| K6 | pfifo | shadow 1.0 / 0.75 (r1: 0.33), truth 1.0 / 1.0, 170–350 s | two-flow leaves break on one miss; A+C simultaneous → case B internal node over A and C |

Three rule defects, confirmed by tracing the evidence logs (not detector effects:
the OWD and truth sources show them too):

1. **A wrong leaf is never charged.** `{a2,b2}` formed on two co-fires. Every
   later `a` event `{a2,a3}` had J = 1/3 against it → case D → a new leaf, and
   b2 received no negative evidence at all (`_case_d` touched no other leaf).
   Negative evidence was tied to *matching*, not to *membership*.
2. **Small leaves and shifting sets break the J / cov thresholds.** K5: `{a,b,c}`
   then `{b,c,d}` → J = 2/4 < 0.6 → case D, so sub-b never reached A before it
   left at 240 s (not decay: τ = 300 s is correct). K6 pfifo at 472 s: a 4-flow
   event with two 2-flow leaves present fell to D because one leaf was not
   "covered"; K6 fq_codel: small leaves dissolved between events and were
   re-opened from zero.
3. **No membership hysteresis.** A member at L ≈ A dropped to "uncertain" on a
   single missed event; in two-flow leaves that cascaded into the false leaves of
   K6 r1 (`{c1,d1,d2}`, `{a2,c2}`).

**v1.2** (`Config.V12`, flags default off so v1.1 stays reproducible; campaign
`--v12`, synth `--set …`):

| # | rule | code |
|---|---|---|
| 1 | *a member fired without you*: every touched leaf the case did not update applies the minority rule itself (silent observable flows get `w⁻`, or the lone fired member gets 0.5 `w⁻`) | `charge_unmatched`, `Engine._charge_unmatched` |
| 2 | visibility: pairwise SAME needs both flows reported members **and** a confirmed leaf; provisional leaves are evidence buffers (the S6 `no_false_leaf` criterion counts confirmed leaves only) | `report_confirmed_only`, `replay.Result.pairs` |
| 3 | membership hysteresis: enter at `L ≥ A`, stay until `L ≤ A/2`, "not a member" at `L ≤ B` | `member_hysteresis`, `FlowState.member` |
| 4 | case C counts the sub-pattern and credits the fired flows; silent members are not charged | `c_silent_penalty = False` |
| 5 | reporting: coverage column; P/R over confirmed memberships | campaign report |
| 6 | dissolve only when a leaf is down to one flow or its support has decayed to ≈ 0 | `dissolve_support = 0.05` |
| 7 | majority attribution: an event goes to the leaf holding most of its flows (≥ 2); two or more such leaves with disjoint hypotheses → case B / GLOBAL, where every leaf with a fired flow votes; fired flows all inside the leaf and ≤ half of it → case C; no leaf with two of M → case D. `theta_J` / `theta_cov` are unused in v1.2 | `majority_match`, `Engine._match_majority` |

Two deviations from the review, both found by the first v1.2 re-score:
(a) rule 7 first required the covered leaves to be confirmed; that made every
cold-start aggregation event case A with the other leaf's flows as candidates
(overlapping hypotheses, S4 merged in 6/10 seeds), so coverage needs k ≥ 2 only
and confirmation is the tie-break. (b) "most of M" alone let a leaf swallow
outsiders: K6 pfifo-r1 went `{a1,a2,b1}` (X, one miss) → `{a1,a2,c1,c2}` (A+C,
k = 2 → case A, c's become candidates) → `{c1,c2,d2}` (Y) … into one 7-flow leaf
in which every later event was case C. Outsiders now join only when the whole
leaf fired with them (v1.1's A-superset condition); two members firing with
strangers says nothing about the leaf's extent.

**Synthetic table, v1.1 (θ 0.6) → v1.2** (10 seeds, `.runs/old/ip8/2026-11-10_grouping-synth-v12/`):

| scenario | ideal | realistic | note |
|---|---|---|---|
| S1 | 6 → 6 | 6 → 6 | median events-to-leaf 2 in both; the "≤ 3 events for all three flows" criterion fails on seeds with an early miss |
| S2 | 10 → 10 | 8 → 8 | the two failing seeds are coincidence pairs that reach A once; they no longer confirm but the criterion is "never reaches A" |
| S3 | 9 → 9 | 9 → 9 | private fraction within ±0.03 |
| S4 | 7 → **9** | 9 → **10** | aggregation events GLOBAL after both leaves confirm |
| S5 | 0 → 0 | 0 → 0 | the noisy flow now joins (median 4–6 events) and stays; the f3 migration still fails: after 150 s the engine ends with one 5-flow leaf (f1 and the B flows) — the A leaf loses f2 to noise and f1 follows f3 into B. Open. |
| S6 | 0 (4) → **7** | 0 → **2** | ideal: G1/G2 are case B, root GLOBAL, 4 leaves + 2 internals. Realistic failures are **merged leaves** such as {f7, f10, f11, f12}: an A4 event fires 3 of its 4 flows, which the majority rule reads as "one miss" (case A, f7 charged `w⁻`) rather than a sub-pattern, and the G2 / R events refill f7 (+2 `w⁺` per cycle vs −1.5). A wrong fourth flow in a three-flow group is indistinguishable from a detector miss at the event level; only the long-run ratio could tell, and v1.2 has no rule for it. |

**Campaign re-score, v1.1 → v1.2** (`report.md` vs `report-v12.md`, same runs; median leaf P / R and t_correct, shadow onsets; cov = share of pairs decided):

| K | cell | v1.1 | v1.2 | cov v1.2 |
|---|---|---|---|---|
| K1 (21 runs) | pfifo / pie / red / mixb | 1.0 / 1.0, 130–160 s | same (mixb 160 → 147 s) | 0.71 |
| K1 | mixa / mixab (fq_codel downstream) | 1.0 / 1.0 on the pairs that decide | same; {a2,a3}, {b2,b3} (+ {a1,a2,a3} on the pfifo branch of mixab) | 0.29 / 0.48 |
| K1 | fq_codel | r2: confirmed cross pairs {a1,b1}, {a2,b2} | r2 unchanged, r1 now {a2,b2,b3} | 0.29 |
| K2 | fq_codel | leaf only at u ≥ 1.15 | same (u 1.15: 99 → 77 s) | 0.0–0.1 |
| K3 | revasym / revjit10 / revcrossmix | 1.0 / 1.0 | same (revjit10 fq_codel 59 → 48 s) | 0.3–0.6 |
| K3 | revcross pfifo | false leaf (shadow), none (owd) | same: a detector confound, not a rule | – |
| K5 | pfifo / pie / red | 1.0 / 1.0 | same; pfifo now reaches a sustained correct state (305 s; never in v1.1) | 0.60 |
| K6 | pfifo | r1 0.33 / 0.33, r2 1.0 / 0.75, r3 1.0 / 1.0 | **3 / 3 runs: four correct two-flow leaves**, 1.0 / 1.0, 187 s (owd) / 331 s (shadow) | 0.78 |
| K6 | fq_codel | cross-group pairs, cov 0.03–0.08 | still cross-group leaves (`{a1,a2,c2,d1,d2}`), cov 0.03–0.28 | – |

K6 pfifo is the test the rules were written for and it now passes on every
run and every onset source. K1 fq_codel's cross pairs survive rule 1 for a
reason worth stating: with the a+b cells (4 of the 8 stimulus cells fire both
branches at once) and a1 / b1 never queuing under fq_codel, a2 and b2 co-fire in
~36 of 42 windows and fire apart in 6. Negative evidence (6 × w⁻ ≈ −9) cannot
beat that much co-occurrence (36 × 2.5), and should not: at the event level these
two flows *are* a group ("same external cause, different queue"). Only the full
leaves, present under FIFO-like queues, turn those events into GLOBAL. K6 fq_codel stays wrong for the fq_codel reason
(the 1 Mb/s flow of each pair rarely queues, so most leaf events are one flow
and the few two-flow events are cross-group coincidences); with so few decided
pairs the P/R numbers there are noise either way. Nothing else moved: v1.2
changes no result where v1.1 was right. K1 is re-scored once its two missing
runs finish (`--ks K1 --report-only --v12 --tag v12`).



## Frozen definitions (2026-11-10)

**Rules**: `Config` defaults (v1.2: rules 1–7 above with the two deviations).
Nothing in `engine.py` changes for the unseen campaign; its result is reported
as it comes.

**Truth** (`grouping_adapter.truth_of`, `leaf_groups`; hit rule changed
2026-11-10 before any held-out scoring, see campaign v2 below):
- a *stimulus window* is a planned congestion interval on one router egress
  (`hop`), with the clients behind that egress as `expected`;
- the expected clients are *hit* in a window when the egress shows a GT1
  standing-queue episode (`gt1.run_truth`, router counters only) inside
  [start, end + 2 s]. This is independent of every client-side signal. Under
  fq_codel the router cannot say which flows queued, so every expected client
  counts; the same windows scored with GT3 per-client OWD episodes are the
  secondary truth (`pairwise_gt3`, "GT3" column), with the note that GT3 reads
  the signal the OWD-mode detector reads. Until 2026-11-10 the hit rule was the
  OWD oracle itself (`det_eval.measured_bands`), i.e. the detector's own input;
- `pairs[f,g]` (share a link) = both hit in at least one common window;
- `leaf[f]` (tightest shared group) = intersection of the `expected` sets of
  the *shared* windows (≥ 2 expected clients) in which f was hit; empty when f
  was never hit in a shared window; private (single-client) windows do not
  count;
- `pairs_leaf[f,g]` = `leaf[f]` non-empty and equal to `leaf[g]`.
- Without plan windows (det_matrix runs): `bursts.csv` hit sets, else topology.

**Scoring**: pairwise SAME = both flows reported members (hysteresis) of the
same *confirmed* leaf; P / R over decided pairs, coverage reported next to
them; `t_correct` = first time the decision equals `pairs_leaf` on every pair
and stays so for 5 s. Synthetic pass criteria as in `replay.check`, with S2
aligned to the visibility rule (never *reported* SAME; the peak accumulation
`drift` is reported too) and S6's `no_false_leaf` counting confirmed leaves.

All of the above was fixed while looking at the same 87 runs it was scored on;
the K1–K6 tables are therefore the development set, not evidence. Campaign v2
below is the test.

## Campaign v2 (specified 2026-11-10, before any run): development set re-run + held-out N1–N5

Specification, open-point decisions, implementation notes and the frozen pass
criteria: [`campaign-v2-spec.md`](campaign-v2-spec.md). Nothing in `engine.py`
or in the truth changes after this point in response to N1–N5 results; a
failure is reported with the L plot and the rule believed responsible.

```bash
.venv/bin/python scripts/trace_prepare.py --download /path/raw     # once: Mahimahi + Norway traces -> configs/traces
.venv/bin/python scripts/grouping_campaign.py --plan               # 145 runs, 20.7 h of emulation
.venv/bin/python scripts/grouping_campaign.py --campaign .runs/<dir> --ks N2 --only pfifo-r1   # smoke: 17 clients
.venv/bin/python scripts/grouping_campaign.py --campaign .runs/<dir> --ks N4 --only pfifo-r1   # smoke: tc keeps up?
.venv/bin/python scripts/grouping_campaign.py --campaign .runs/<dir> --skip-existing           # the rest (tmux)
.venv/bin/python scripts/grouping_campaign.py --campaign .runs/<dir> --report-only --compare .runs/old/ip8/2026-11-06_1526_grp
.venv/bin/python scripts/grouping_campaign.py --campaign .runs/<dir> --report-only --score-held-out   # after the freeze only
```

Order of events (review, 2026-11-10): the engine is not frozen yet (episode
end as an event, in-episode metrics still open), so the runs happen now, the
development set is scored as it comes, and **N1–N5 are not scored until the
rules are frozen and tagged**: until then they get `infra.md` only (finished,
clients / sessions, event errors, link event lag, windows GT1 confirmed,
clients never hit, control client). Onset sources on every run: shadow (RTT,
comparison), **shadow-owd (primary; the criteria are evaluated on it)**, owd,
truth. N5 has no SBD baseline columns (the baselines need one common span of
long-lived flows).

Second review the same day, applied before the runs: the detector's OWD input
and the truth must not be the same signal, so (1) the grouping truth moved to
GT1 router episodes with GT3 as the secondary column (above), (2) the
publisher's `acks.csv` gained `owd_us`, the largest newly acked packet's own
one-way delay at that ACK, which `owd_mode` now prefers over the 5 ms send-bin
minimum (older runs fall back to the bins, with a few ms of lookahead), (3)
Copa is dropped, (4) `cake` is available as an AQM (`cake unlimited
besteffort` under the HTB shaper; ignores `queue_limit_packets`) for the
microbenchmarks (pfifo, red, pie, cake; fq_codel stays in the core set only).
The merged core / microbenchmark / negative campaign of that review is in
place (spec notes, "Merged campaign"): one planner (`grouping_campaign.py`,
det_matrix's event benchmark shared through `det_matrix.scenario_data`),
both scorers on every run, three layers (`GROUPS`: core K/C1/N, negatives G0,
micro M1–M6), the end-to-end table (`scripts/e2e_score.py`) and det_eval's
detector table in every campaign report. 577 runs, 61.5 h of emulation.

```bash
.venv/bin/python scripts/grouping_campaign.py --plan                                   # budget, every YAML validated
.venv/bin/python scripts/grouping_campaign.py --campaign .runs/<dir> --ks N2 --only pfifo-r1
.venv/bin/python scripts/grouping_campaign.py --campaign .runs/<dir> --ks N4 --only pfifo-r1
.venv/bin/python scripts/grouping_campaign.py --campaign .runs/<dir> --skip-existing    # all 18 campaigns (tmux)
```

| campaign | topology | stimulus | AQMs × reps | criterion (shadow-owd source; RTT shadow as comparison) |
|---|---|---|---|---|
| K1 hier | split | 7 target kinds (a+b@1 dropped) × 6 cells | pfifo, red, pie, fq_codel, mixab × 3 | report; flag cells worse than 2026-11-06 |
| K2 part | detector | unchanged | pfifo, fq_codel × 3 | report |
| K3 rev | detector / rev | unchanged | pfifo, fq_codel × 3 | report |
| K5 mixed | access | 12 shared + 16 private; sub-d joins at 60 s; nobody leaves | 4 × 3 | report |
| K6 depth | tree8, leaves 2.5 / 5 Mb/s (11.9 / 23.8 / 47.5 Mb/s) | unchanged kinds | pfifo, fq_codel × 5 | report |
| N1 indep | split | independent processes on up, a, b (exp gaps, mean 30 s, min 5 s), 600 s | pfifo, pie, fq_codel × 5 | pfifo/pie: 0 confirmed cross-branch pairs, both leaves correct, P, R ≥ 0.95; fq_codel: count reported |
| N2 uneven | uneven (2 + 5 + 9 clients; `uneven6` = 2 + 5 + 6) | independent processes on A, B, C, 600 s | pfifo, pie, fq_codel × 5 | pfifo/pie: three groups correct, P, R ≥ 0.95, cov ≥ 0.7, sub-ctrl ungrouped; events-to-membership reported |
| N3 cross | split | UDP constant rate (u × capacity) or 2 / 4 Cubic flows for 4 / 8 s, independent timing, 600 s | pfifo, fq_codel × 5 | pfifo: tree = the two branches; case matrix per stimulus type |
| N4 trace | access | shared drops U(10, 15) s + every access link replays a scaled cellular trace (200 ms steps), 600 s | pfifo, fq_codel × 5 | shared P, R ≥ 0.9; ≥ 90 % of private windows solo; sub-ctrl ungrouped |
| N5 churn | large (8 clients) | on exp(90, min 20) / off exp(30, min 5) per client, sessions `<sub>@n`; drops sized to the on-demand, 900 s | pfifo, fq_codel × 5 | sub-ctrl ungrouped; no session a confirmed member while off; share of ≥ 3-event sessions that became members reported |
| all fq_codel cells | | | | no threshold; leaf and link truths side by side |

New per-run outputs: `windows.json` with `stimulus_type` and `concurrent`,
`plan.json` (seed, variant, git describe, N4 trace scaling), and in
`metrics.json` the per-flow L series, `membership_events`, `tree_correct`,
`ctrl_grouped`, link P / R, `private_windows`, sessions and `off_membership`.
The report opens with the PASS / FAIL lines of the criteria above. Sessions
(N5) are the one testbed change: a subscriber may join and leave repeatedly,
each later session runs as client `<sub>@<n>` with its own files, and the
adapter treats every session as a flow (`SessionRun`).

## Two questions from the review, answered on the data

**S2 realistic, seeds 2 and 3.** Each has exactly one coincidence pair of
events (D then A, 2 s apart in seed 2, 12 s in seed 3): two capped weights
(0.55 A each) sum to 4.93 > A, so the *internal* `drift` criterion fails. The
pair was **never reported SAME** (0 of 60 / 52 event closes): in seed 2 only f1
moved into the leaf, in seed 3 neither did, and the lone onsets that followed
charged the pair (rule 1 / SOLO) down to −1.8 and dissolved it by 245 s. The
criterion was written before the visibility rule and now follows it. The
residual limit stands: two coincidences inside one decay window do make a
*provisional* pair, by construction of the cap (two clean co-fires must reach A
for speed). Only visibility and erosion keep it off the output.

**Speed (S1 6/10, "1–2 events" target).** Not the multipliers: in the S1
evidence logs `c_mag` = 1.0 always, `c_lag` ≥ 0.93 (median 1.0), base
`log(p_det/p_fa)` = 2.9–3.3 and 52 % of events are capped at 0.55 A = 2.50. Two
clean events give 5.0 ≥ A, and 6 of 10 seeds reach the leaf in exactly 2
events. The other four take 4 (3 seeds) or 6 (1 seed): a flow that misses one
of the first two events (p_miss 0.1, three flows → ≈ 46 % of seeds) takes
`w⁻` = −1.5 for the miss and needs two more clean events (2.5 − 1.5 + 2.5 = 3.5
< A). "All three flows after ≤ 3 events" is therefore a criterion on the
detector's miss rate, not on the rules; median events-to-leaf is 2 as targeted.

**Synthetic table with the frozen defaults** (10 seeds, `.runs/old/ip8/2026-11-10_grouping-synth-default/table.md`):

| scenario | ideal | realistic |
|---|---|---|
| S1 one leaf | 6/10 (median 2 events) | 6/10 |
| S2 independent | 10/10 | 10/10 (drift peak 2.5; never reported SAME) |
| S3 shared + private | 9/10 | 9/10 |
| S4 two leaves, one parent | 9/10 | 10/10 |
| S5 noise / idle / migrate | 0/10 (migration) | 0/10 |
| S6 four leaves, two parents | 7/10 | 2/10 (merged four-flow leaves) |



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
