# Scenario and Topology Suite v4: implementation spec (for the coding agent)

Status: 2026-11-15. Builds on `claude/scenario-suite-v3-spec.md` (v3). Everything v3 defines stays valid unless this document changes it: sizing rule, background generator, AQM settings, offloads, timing, seeds, naming, outputs, gate checks, health file. Read v3 first. This spec adds operating points, topologies, stimuli, scenario types and three campaigns.

Do this after the SETS engine, the common scorer and the fq_codel pinning fix are done (see the freeze note). It does not change the detector, SETS, ECG, h3 or any scoring script.

## 0. What changes, in one page

1. **Operating points.** Default is now s = 0.30, U = 0.50. U = 0.70 is the extreme point. U = 0.85 is removed. The upper stream share is s = 0.50; s = 0.65 is not run again (existing runs stay as a stress row).
2. **Five seeds** on the core grouping blocks at the default point; top-up to five on the key v3 blocks at the extreme point.
3. **Group size**: single leaves of 4 to about 40 clients, to see how misses behave as groups grow.
4. **Literature scenarios**: FlowBot, Hayes et al. (LCN 2014 and ToN 2020), MPTCP-SBD, Rubenstein et al., RFC 8867.
5. **New grouping situations**: shifting bottleneck, persistent overload, real churn, share of concurrent events, sparse mild events, other background modes in a hierarchy, negatives.
6. **Copa, I/P ratio, detector blocks, and all v3 microbenchmarks again at the default point.**

Total about 66 h emulated, in three campaigns of about 22 h each. Time is not a constraint; correctness and health are.

Rules, as in v3: new files only, `v4` prefix; existing topologies, scenarios, planners and run folders stay untouched and working; old ground truths produced as today, GT-Q / GT-H logging on; keyframes synchronized unless a scenario says otherwise; OWD from ACK receive timestamps; you implement and verify, **the user starts each campaign**; anything that cannot be done as written goes under "deviations", never changed silently.

## 1. Operating points and constraints

| Name | s | U | Use |
|---|---|---|---|
| DEF | 0.30 | 0.50 | default for every block unless stated |
| EXT | 0.30 | 0.70 | extreme load; all v3 event runs are at this point |
| HS50 | 0.50 | 0.50 | high stream share |
| HS70 | 0.50 | 0.70 | high stream share at extreme load |

Sizing per bottleneck egress as in v3: `C_e = D_e / (s * U)`, `BG_e = D_e * (1 - s) / s`.

Constraints as in v3 (every shaped link ≤ 100 Mb/s; every instrumented flow ≤ 15 % of each bottleneck it crosses, 25 % accepted at s ≥ 0.50 and in the literature blocks; total rate through all router egresses ≤ 300 Mb/s). If a topology violates a constraint at a point: (1) use the low rendition variant defined below; (2) if it still fails, skip that cell and list it. Do not change s or U to make it fit.

## 2. Topologies

Access delays: narrow set of v3 (5 / 7.5 / 12.5 / 20 ms one way, cycling) unless stated. `sub-ctrl` as in v3 in every topology.

### 2.1 Kept from v3
T-BASE, T-ACCESS, T-SPLIT4, T-TREE16, T-UNEVEN, T-REV. T-TREE16 and T-SPLIT4 are used only at EXT (they do not fit at DEF).

### 2.2 Low-rendition variants (for DEF)

**T-SPLIT4L**: T-SPLIT4 with clients 500, 1000, 1000, 2500 kb/s per leaf. `D_leaf = 5.15`, `D_up = 10.3`.

| point | leaf C / BG | up C / BG |
|---|---|---|
| DEF | 34.3 / 12.0 | 68.7 / 24.0 |
| EXT | 24.5 / 12.0 | 49.0 / 24.0 |
| HS50 | 20.6 / 5.15 | 41.2 / 10.3 |

**T-UNEVENL**: three leaves, `r1->r2` unshaped. A (2 clients): 1000, 2500. B (5): 500, 500, 1000, 1000, 2500. C (9): 500 ×4, 1000 ×3, 2500 ×2. `D = 3.605 / 5.665 / 10.3`; at DEF `C = 24.0 / 37.8 / 68.7`.

T-BASE and T-ACCESS at DEF use the standard client set (`C main = 75.5`, `BG = 26.4`).

### 2.3 T-PARk: parallel leaves, no shared bottleneck (FlowBot-style)
`pub -> r1 -> r2 -> {switch-1 .. switch-k} -> clients`. `r1->r2` unshaped (1000 Mb/s, no AQM, no background). Each leaf egress `r2->switch-j` is a bottleneck with its own background pair. Four clients per leaf, low set (500, 1000, 1000, 2500). k ∈ {2, 4, 6}. At DEF each leaf has `C = 34.3`, `BG = 12.0`.
Variant **T-PAR4x8**: k = 4 with eight clients per leaf (the low set twice), `D = 10.3`, `C = 68.7` at DEF.

### 2.4 T-LEAFn: one leaf of n identical clients (group size)
T-BASE shape, n clients at 500 kb/s each, point EXT (s 0.30, U 0.70; the extreme point is used so that capacities stay comparable with v3). `C = n * 2.452 Mb/s`.

| n | 4 | 8 | 16 | 24 | 32 | 40 |
|---|---|---|---|---|---|---|
| C (Mb/s) | 9.8 | 19.6 | 39.2 | 58.9 | 78.5 | 98.1 |

Find the largest n in {24, 32, 40} that passes the health check (CPU idle, inter-dequeue error, tracer) in a 90 s smoke run; call it n_max and report it. Use n ∈ {4, 8, 16, 24, n_max} (drop duplicates).

**T-LEAF16W**: n = 16 with one-way access delays spaced evenly from 5 to 95 ms (base RTT 20 to 200 ms). pfifo limit follows the largest base RTT.

**T-SPLITn**: two leaves of n clients at 500 kb/s under a shaped `up`, n ∈ {8, 12}, point EXT.

### 2.5 T-HAYES: every pair shares a bottleneck in turn (Hayes et al., LCN 2014, Fig. 4)
Four client groups g1..g4, two clients each. g1, g2: 1000 kb/s per client; g3, g4: 500 kb/s per client (their sources 1 and 2 send at twice the rate of 3 and 4).
Path: `pub -> R0 -> stage 1 -> R1 -> stage 2 -> R2 -> stage 3 -> R3 -> stage 4 -> R4 -> clients`. Each stage is a set of parallel links between two routers; routing by destination subnet decides which link a group uses:

| stage | parallel links (groups carried) |
|---|---|
| 1 | L12 (g1, g2), L34 (g3, g4) |
| 2 | L13 (g1, g3), L24 (g2, g4) |
| 3 | L14 (g1, g4), L23 (g2, g3) |
| 4 | L1234 (all) |

Every one of the seven links is a candidate bottleneck with its own background pair, sized at s = 0.20, U = 0.50 (80 % background; theirs is above 90 %, which does not fit our limits; FLAG): L12 41.2, L34 20.6, L13 / L24 / L14 / L23 30.9 each, L1234 61.8 Mb/s. Verify with a traceroute-style check that every group crosses exactly its four links.

### 2.6 T-TEACUP: two access links and a shared link (Hayes et al., ToN 2020, Fig. 1)
T-SPLIT4L shape with uniform access delays giving a 100 ms base RTT for every client. Leaf capacity from s = 0.30 at a calm load of 0.80 (their background fills the bottleneck to about 80 %; this block is a replication and is the only place a calm load above 0.70 is used; FLAG): `C_leaf = 21.5`. `C_up = 2.5 * C_leaf = 53.6` (their 25 : 10 ratio). pfifo limits of 0.5, 1 and 2 BDP at 100 ms. Variant **rev**: the ACK path of `up` limited to 10 Mb/s and loaded to 90 % with UDP, as in T-REV.

## 3. Background modes

BG-CBR (default), BG-BURSTY, BG-MIX as in v3. One addition:

**BG-ONOFF** (Rubenstein et al.; Hayes ToN testbed): same mean `BG_e`; n = max(4, round(BG_e / 2.5 Mb/s)) UDP sources, each on for an exponential time (mean 1 s) at twice its mean rate and off for an exponential time (mean 1 s), independent RNG streams, Poisson packet gaps while on.

## 4. Stimuli

surge, ramp, tcp, join, capdrop, revburst, loss as in v3. Additions:

| Stimulus | How it is made |
|---|---|
| **persist** | A surge held for d ∈ {30, 60, 120 s}. Same generator as surge. |
| **shorttcp** | A salvo of short TCP flows on the target's background path: n = 10 cubic flows, sizes Pareto with mean 500 kB (shape 1.5), starts spread uniformly over 2 s, salvos repeated so that the mean offered extra load over `d` is `(u - U) * C_e`. Check RFC 8867 section 5.7; if it gives concrete values, use them and say so. FLAG. |
| **pause** | One client stops receiving video for d ∈ {5, 20 s} (the sender stops sending to it) and then resumes. No load change. |
| **cold** | The surge is already on at t = 0; clients start within the first 3 s; the run lasts 45 s (FlowBot's runs: 30 s with flows starting in the first 3 s). No warm-up. |

## 5. New scenario types

Grids as in v3: `u3 = {1.05, 1.15, 1.3}`, `d3 = {2, 5, 10 s}`. Gaps uniform 10-15 s, warm-up 15 s, tail 10 s unless stated. Durations are approximate.

| Type | Topology | Events | ~s |
|---|---|---|---|
| **H-HIERL** | T-SPLIT4L | the H-HIER plan of v3 (51 events) | 950 |
| **H-INDEPL** | T-SPLIT4L | the H-INDEP plan of v3 | 600 |
| **H-UNEVENL** | T-UNEVENL | the H-UNEVEN plan of v3 | 600 |
| **L-LONG2** | T-SPLIT4L | surge on up, a, b: u ∈ {1.15, 1.3} × d ∈ {10, 30}, each twice (24 events) | 830 |
| **G-SIZE** | T-LEAFn, T-LEAF16W | S-BURST plan (18 events) | 350 |
| **G-SIZE2** | T-SPLITn | surge on up, a, b: `u3 × d3` each (27 events) | 520 |
| **P-PAR** | T-PARk | independent timing per leaf as in H-INDEP (mean gap 15 s, min 5 s), u and d from `u3`, `d3` | 600 |
| **FB-LOAD** | T-PAR4 | persist 30 s on **all leaves at once**, 30 s calm between episodes; congestion level per episode from {1.0, 1.1, 1.2, 1.5, 2.0, 2.5}, each twice, shuffled (12 episodes). BG-BURSTY. | 750 |
| **FB-CROSS** | T-PAR4 at s ∈ {0.8, 0.6, 0.4, 0.2} (cross-traffic ratio 0.2 / 0.4 / 0.6 / 0.8), U 0.50 | persist 30 s on all leaves, level 1.1, 8 episodes, 30 s calm between. BG-BURSTY. | 520 |
| **FB-LAG** | T-PAR4 with per-leaf access delays: two clients at 10 ms, two drawn from U(50, 210) ms one way (seeded) | as FB-CROSS at DEF, level 1.2 | 520 |
| **FB-SCALE** | T-PAR2, T-PAR6, T-PAR4x8 | as FB-CROSS at DEF, level 1.2 | 520 |
| **FB-COLD** | T-PAR4 | cold, level 1.2, one episode | 45 |
| **HY-COMBO** | T-HAYES | each of the seven links targeted with surge: u ∈ {1.15, 1.3} × d ∈ {5, 10} (28 events), shuffled. Variant **cap**: the same plan with capdrop (their method). | 520 |
| **HY-TB** | T-TEACUP | surge on a, b, up: u ∈ {1.15, 1.3} × d ∈ {5, 10}, each twice (24 events). BG-ONOFF. | 600 |
| **SB-NSB** | SB: T-LEAFn-like with the eight clients of T-PAR2 behind one link at DEF. NSB: T-PAR2. | identical plan and seed in both: 18 surges (`u3 × d3` twice); in NSB every surge hits both leaves at once. BG-MIX. | 350 |
| **H-SHIFT** | T-SPLIT4L | phases of 60 s; in a phase only one target is hit, with surges u ∈ {1.15, 1.3}, d = 5 s, every 10-15 s. Phase order: a, up, b, a+b, up, a, b, up, a+b, up. Variant **sustained**: one persist of 40 s per phase instead of repeated surges. | 650 |
| **S-PERSIST** | T-BASE | persist d ∈ {30, 60, 120} × u ∈ {1.1, 1.3}, 30 s calm between | 600 |
| **H-CHURN** | T-SPLIT4L | H-INDEPL timing, 900 s. Per leaf: one client present throughout, one joins at 120 s, one leaves at 450 s, one leaves at 300 s and rejoins at 600 s. Variant **move** (if feasible): a client leaves leaf a at 450 s and continues with the same client identity behind leaf b; if the testbed cannot keep the identity, skip and report. | 900 |
| **H-CONC** | T-PAR2 | 40 surges per run, u ∈ {1.15, 1.3}, d ∈ {5, 10}; a fraction f ∈ {0, 0.25, 0.5, 1.0} of them hit both leaves at the same instant, the rest hit one leaf | 600 |
| **H-SPARSE** | T-SPLIT4L | surge on up, a, b: u ∈ {1.05, 1.15} × d ∈ {5, 10} (12 events), gaps uniform 45-75 s | 900 |
| **H-JOIN** | T-SPLIT4L | join on a, on b and on up, u ∈ {1.05, 1.15}, each twice (12 events; 40 s each) | 700 |
| **NEG-CALM** | T-SPLIT4L, T-PAR4 | none | 600 |
| **NEG-PRIV** | T-ACCESS | private capdrops only (as A-MIXED without the shared surges), 24 events | 410 |
| **NEG-LOSSH** | T-SPLIT4L | loss stimuli on single clients, as N-LOSS | 300 |
| **S-SHORT** | T-BASE | shorttcp on main, `u3`, d = 10 s, each three times | 350 |
| **S-PAUSE** | T-BASE | S-BURST plan with 6 pause stimuli added (each client paused at least once, never during a surge and once during a surge) | 400 |
| **S-DENSE** | T-BASE | surge `u3 × d = 2`, 60 events, gaps uniform 2-4 s | 300 |
| **S-MILD** | T-BASE | on/off overload as in the old K2: on U(1, 4) s with 15 % U(10, 20) s, off U(5, 20) s, one level per run from u ∈ {1.05, 1.10, 1.15} | 330 |
| **R-REVASYM** | T-REV | R-REV plan with the forward and reverse path delays made asymmetric as in the old `revasym` | 320 |
| **D-CLEAN** | T-BASE | no background for the first 60 s, then background on; from 90 s the S-BURST plan | 420 |

Truth for the new types: stimulus windows, targets and expected clients are written as today. For FB-* and NSB the expected set of an episode is per leaf (clients behind each congested leaf); the leaves are congested at the same time but are different groups. For HY-COMBO the expected set is the clients of the groups on the targeted link; there is no leaf in this topology, so the headline for that block is the per-link true set. For pause, record the window per client.

## 6. Campaign matrix

Run names `v4-<block>-<type>-<variant>-<aqm>-r<rep>`. Seeds 1..n per row; the same seed across AQMs as in v3. Blocks are listed in priority order inside each campaign; queue order inside a campaign: all rep 1 in block order, then all rep 2, and so on. Hours are emulated, for all seeds.

### Campaign K1 (about 24 h): default point and group size

| Block | Type | Topology, point | AQMs | Seeds | Runs | Hours |
|---|---|---|---|---|---|---|
| A1 | CALM | T-BASE, T-SPLIT4L, T-UNEVENL, T-ACCESS, T-PAR4; DEF | pfifo, codel | 3 | 30 | 1.0 |
| A2 | S-BURST | T-BASE DEF | pfifo, codel, pie, fq_codel, red, cake | 5 | 30 | 2.9 |
| A3 | S-RAMP, S-TCP, S-JOIN | T-BASE DEF | pfifo, codel | 3 | 18 | 1.4 |
| A4 | H-HIERL | T-SPLIT4L DEF | pfifo, codel, pie, fq_codel | 5 | 20 | 5.3 |
| A5 | H-INDEPL | T-SPLIT4L DEF | pfifo, codel, fq_codel | 5 | 15 | 2.5 |
| A6 | H-UNEVENL | T-UNEVENL DEF | pfifo, codel | 5 | 10 | 1.7 |
| A7 | A-MIXED | T-ACCESS DEF | pfifo, codel, fq_codel | 5 | 15 | 1.7 |
| A8 | L-LONG2 | T-SPLIT4L DEF | pfifo, codel | 5 | 10 | 2.3 |
| A9 | N-LOSS, R-REV | DEF | pfifo | 3 | 6 | 0.5 |
| G1 | G-SIZE | T-LEAFn, n ∈ {4, 8, 16, 24, n_max} | pfifo, codel | 3 | 30 | 2.9 |
| G2 | G-SIZE2 | T-SPLIT8, T-SPLIT12 | pfifo | 3 | 6 | 0.9 |
| G3 | G-SIZE | T-LEAF16W | pfifo, codel | 3 | 6 | 0.6 |

### Campaign K2 (about 22 h): extreme point, high share, new situations, detector

| Block | Type | Topology, point | AQMs | Seeds | Runs | Hours |
|---|---|---|---|---|---|---|
| X1 | H-HIER (v3 C7), seeds 3-5 | T-SPLIT4 EXT | pfifo, codel, pie | +3 | 9 | 2.4 |
| X2 | H-INDEP (C10), H-UNEVEN (C11), A-MIXED (C12), seeds 3-5 | EXT | pfifo, codel | +3 | 18 | 2.7 |
| X3 | H-DEPTH (C9), seeds 3-5; S-BURST pie (C2), seeds 3-5 | EXT | pfifo; pie | +3 | 6 | 1.1 |
| X4 | H-HIERL (bridge to the low rendition set) | T-SPLIT4L EXT | pfifo | 2 | 2 | 0.5 |
| X5 | S-BURST | T-BASE HS50 and HS70 | pfifo, codel | 3 | 12 | 1.2 |
| X6 | H-HIERL | T-SPLIT4L HS50 | pfifo, codel | 3 | 6 | 1.6 |
| N1 | H-SHIFT, and variant sustained | T-SPLIT4L DEF | pfifo, codel; sustained pfifo only | 3; 2 | 8 | 1.5 |
| N2 | S-PERSIST | T-BASE DEF | pfifo, codel | 2 | 4 | 0.7 |
| N3 | H-CHURN (and move if feasible) | T-SPLIT4L DEF | pfifo, codel | 3 | 6 (+2) | 1.5 (+0.5) |
| N4 | H-CONC, f ∈ {0, 0.25, 0.5, 1.0} | T-PAR2 DEF | pfifo | 3 | 12 | 2.0 |
| N5 | H-SPARSE | T-SPLIT4L DEF | pfifo, codel | 3 | 6 | 1.5 |
| N6 | H-HIERL with BG-BURSTY and BG-MIX | T-SPLIT4L DEF | pfifo | 2 | 4 | 1.1 |
| N7 | H-JOIN | T-SPLIT4L DEF | pfifo, codel | 2 | 4 | 0.8 |
| N8 | NEG-CALM, NEG-PRIV, NEG-LOSSH | DEF | pfifo, codel (NEG-LOSSH pfifo) | 2 | 14 | 2.0 |
| T1 | D-CLEAN | T-BASE at DEF, EXT, HS50 | pfifo | 2 | 6 | 0.7 |
| T2 | forward access jitter 2, 5, 10 ms (order kept), S-BURST | T-BASE DEF | pfifo, codel | 2 | 12 | 1.2 |
| T3 | S-DENSE, S-MILD (three levels), R-REVASYM | DEF | pfifo (S-MILD also codel) | 2 | 16 | 1.4 |

### Campaign K3 (about 21 h): literature, Copa, I/P ratio, microbenchmarks

| Block | Type | Topology, point | AQMs | Seeds | Runs | Hours |
|---|---|---|---|---|---|---|
| L1 | FB-LOAD | T-PAR4 DEF | pie, codel, pfifo | 2 | 6 | 1.3 |
| L2 | FB-CROSS, four ratios | T-PAR4 | pie, codel | 2 | 16 | 2.3 |
| L3 | FB-LAG | T-PAR4 | pie, codel | 2 | 4 | 0.6 |
| L4 | FB-SCALE | T-PAR2, T-PAR6, T-PAR4x8 | pie | 2 | 6 | 0.9 |
| L5 | FB-COLD | T-PAR4 | pie, codel | 10 | 20 | 0.3 |
| L6 | P-PAR | T-PAR4 DEF | pfifo, codel | 3 | 6 | 1.0 |
| L7 | HY-COMBO, and variant cap | T-HAYES | pfifo | 3 | 6 | 0.9 |
| L8 | HY-TB at 0.5 / 1 / 2 BDP; variant rev at 1 BDP | T-TEACUP | pfifo | 2 | 8 | 1.3 |
| L9 | SB-NSB | SB and NSB | pfifo | 3 | 6 | 0.6 |
| L10 | H-HIERL with BG-ONOFF | T-SPLIT4L DEF | pfifo | 2 | 2 | 0.5 |
| L11 | S-SHORT; S-PAUSE | T-BASE DEF | pfifo, codel; pfifo | 2 | 6 | 0.6 |
| C1 | Copa: CALM at DEF and EXT; S-BURST; S-TCP; S-JOIN; H-HIERL; H-INDEPL; A-MIXED | DEF | CALM, S-TCP, S-JOIN, H-INDEPL, A-MIXED pfifo; S-BURST pfifo, codel, fq_codel; H-HIERL pfifo, codel | 2 | 24 | 2.7 |
| I1 | I/P size ratio 1.2 and 6: CALM, S-BURST, H-HIERL; S-BURST also on codel | DEF | pfifo (+ codel) | 2 | 16 | 2.0 |
| M | All v3 microbenchmarks M1-M12 and M14 again at DEF (same definitions, "relative to A2" instead of C2; M11 keeps its own s and U) | DEF | as in v3 | 2 | 58 | 6.1 |

Copa: if it is not available in the sender, skip C1 and report. If v3's M13 Copa runs were never read separately, score them first and put the table in the K3 report.

### Budget
K1 ≈ 23.7 h, K2 ≈ 23.9 h, K3 ≈ 21.1 h emulated; about 69 h in all. Compute the real totals in the planner. There is no cut rule: if a campaign is longer than planned, say so and keep every block. Never drop a seed instead of a block.

Not in v4: the held-out set. Prepare, but do not run, a command that regenerates N1-N5 at DEF on the v4 topologies.

## 7. Before each campaign

1. `--plan-only` for the campaign: run list, per-run duration, per-block and total hours, per-egress `C_e` / `BG_e`, constraint results, cells skipped by section 1.
2. Smoke test, which you may run: one 60 s CALM per new topology and one 90 s run per new stimulus (persist, shorttcp, pause, cold) and per new background mode. Apply v3 gate checks 1-4 and 6. For T-HAYES also the path check of 2.5; for T-LEAFn the n_max search of 2.4.
3. A gate block at the start of each campaign, automatic stop on failure, as in v3: one CALM per topology used in that campaign and one event run per new stimulus, pfifo, one seed.
4. Hand over the start and resume commands. The user starts the campaign.

## 8. After each campaign

With the SETS engine, the common scorer and the existing detector scripts, unchanged. No tuning, no new analysis beyond this list. Seeds side by side, never pooled silently; a "seed against seed" block on top; results that disagree across seeds without a known cause are marked "not reliable".

1. Validity: gate result, runs completed / failed / invalid, measured load and share against target, offered load during stimuli, health worst cases, deviations, cells skipped.
2. Detector (frozen v2-owd; and next to it any new detector variant that exists by then, both scored on the same runs): the tables of the v3 detector report per block, AQM and point; the learned calm baseline and sigma per point; the two recall definitions (onset in window; alarm on at harm onset) with the random baselines.
3. Grouping, SETS at k = 2 and 3, ECG and h3 side by side with the common scorer: leaf precision / recall / F1 averaged over event closes, spurious groups, pair precision / recall, the closes right after an upstream event, time to a leaf group in events and seconds, late joiner. Per-flow-queue cells against the "same link" truth.
4. Per block, the specific question:
   - G1-G3: miss rate, false-inclusion rate and dispersion of misses per event against group size; how often one onset wave is split into two ECG events against group size and RTT spread; leaf F1 against group size.
   - FB-*, S-PERSIST, FB-COLD: for each method, whether and when the leaves are grouped **inside the first episode** (seconds from the start of the overload), and after 2, 3, 4 episodes. This is the comparison with detectors that decide within one period of sustained congestion; report it plainly even if SETS has nothing to say inside one episode.
   - HY-COMBO: per-link true set F1; how many of the seven sets each method holds.
   - SB-NSB: in SB one group of eight; in NSB two groups of four; report what each method outputs and the pair precision in NSB.
   - H-SHIFT: per phase, the group each client is reported in, and how long after a phase change the output follows.
   - H-CHURN: groups of a client after it left; time for a joining or returning client to be grouped; what the missing forgetting costs.
   - H-CONC: leaf F1 and the number of union groups against f.
   - NEG-*: groups declared; every one counts as false, except pairs that share a congested queue by the topology truth.
   - D-CLEAN, T2: detector recall and delay before and after the load starts; delay against jitter level (p50 and p90).
   - C1: everything in items 2 and 3 for Copa next to the same cells with BBR.
   - I1: keyframe queue peak, detector and grouping against the I/P ratio.
5. Catalog for v4 (measured load and share per egress, calm and in stimulus windows) and the keyframe table per point.

## 9. Flag rather than decide

- Any cell that violates a constraint of section 1.
- n_max below 24.
- T-HAYES routing that cannot be realised with parallel links; H-CHURN move without a stable client identity; Copa missing.
- RFC 8867 values for short TCP flows that differ from section 4.
- fq_codel or cake cells where no instrumented flow is ever constrained.
- Any place where a new hand-picked constant would be needed.

Keep the paper notes: add the v4 operating points, every new topology and stimulus with its source paper, and every deviation. Do not add citations yourself.
