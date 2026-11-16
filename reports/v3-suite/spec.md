# Scenario and Topology Suite v3: implementation spec (for the coding agent)

Status: 2026-11-14. Background and reasons: `claude/scenario-review.md`. This spec replaces the scenario set of the current campaigns for all new runs. It does not change the detector, ECG, the template method, or any scoring script.

## 0. What you are building, in one page

Today every bottleneck carries only our video (load 0.65, video share ~1.00), every hierarchy level is a scaled copy of the others, congestion is made almost only by capacity drops, and AQM hard limits are set to the pfifo packet count with `ecn` on. v3 fixes these:

1. **Always-on background traffic at every bottleneck**, so that the share of our synchronized stream in the link's traffic (`s`) and the total load (`U`) are explicit parameters.
2. **Each bottleneck sized independently** from the video behind it, with its own background source and sink.
3. **Congestion by load increase** (background surge, TCP flows, viewers joining). Capacity drops stay only on access links and in one comparison microbenchmark.
4. **AQMs with kernel default limits and no ECN.**
5. **Narrow RTT spread** behind a shared bottleneck (20–50 ms) by default.
6. **At least 4 instrumented clients per leaf** in the hierarchy topologies.
7. **Two repetitions (seeds 1 and 2) of every run.** Core blocks first, microbenchmarks last. Target total about 20 h of emulated time.

Rules:
- New files only. Keep every existing topology, scenario, planner and run folder working and untouched. Name new things with a `v3` prefix or folder.
- Old ground truths (GT1 / GT2 / GT3) are produced as today. GT-Q / GT-H logging stays on (`QUICLAB_GTQ_LOGGING=1`) with its per-run health file.
- Keyframes synchronized (phase 0 for every client) unless a scenario says otherwise.
- OWD from ACK receive timestamps, as today.
- You implement and verify; **I start the campaign.** Deliver the command (section 9).
- If something here cannot be done as written, do the closest thing, and list it under "deviations" in your report. Do not silently change parameters.

## 1. Definitions and sizing rule

For a bottleneck egress `e`:

| Symbol | Meaning |
|---|---|
| `D_e` | Wire rate of the instrumented video behind `e` = sum of client rates × 1.03 |
| `s` | Share of the synchronized stream in the traffic on `e` (calm) |
| `U` | Calm load on `e` = total traffic / capacity |
| `C_e` | Capacity of `e` |
| `BG_e` | Always-on background rate on `e` |

Sizing, applied to **every** bottleneck egress separately:

```
C_e  = D_e / (s * U)
BG_e = D_e * (1 - s) / s          # independent of U
```

Constraints (check in the planner, fail loudly):
- every shaped link ≤ 100 Mb/s;
- every instrumented flow ≤ 15 % of the capacity of each bottleneck it crosses (exception: the s = 0.65 and legacy cells, where up to 25 % is accepted);
- total rate through all emulated router egresses ≤ 300 Mb/s.

Default operating point: **s = 0.30, U = 0.70**. Other levels are used only where the matrix says so.

Expected synchronized-keyframe queueing peak at an egress, for reference only (not a pass criterion): about `0.121 * s * U` seconds (25 ms at the default point, 80 ms in the legacy setup).

## 2. Common settings

### 2.1 Video and sender
Unchanged: qvideo-server over mvfst, bbr, pacing on, one connection per client, one stream per GOP, 30 fps, GOP 1000 ms, no B-frames, I/P size ratio 4, lognormal frame noise sigma 0.2, 600 ms client buffer, 1000 ms application queue. Video frame-size seed = repetition number. All clients phase 0.

### 2.2 Delays
- `pub -> first router`: 5 ms each way (as today).
- Client access delays (one way, each direction), default **narrow** set, cycling through a leaf's clients in order: 5, 7.5, 12.5, 20 ms. Base RTTs: 20, 25, 35, 50 ms.
- **wide** set (microbenchmark only): today's 5 / 15 / 30 / 45 ms.

### 2.3 Queue limits and AQMs
`ms_to_pkts(C, t) = ceil(C[bit/s] * t / 12000)`.

| AQM | Configuration in v3 |
|---|---|
| pfifo | `limit = ms_to_pkts(C_e, 50 ms)`. This is "1 BDP" (50 ms = the largest default base RTT). Variants in microbenchmark M1: 100 ms ("2 BDP") and 300 ms ("bloated"). Minimum 20 packets. |
| codel | kernel defaults: no `limit` argument, **no `ecn`** |
| pie | kernel defaults, no `limit`, no `ecn` |
| fq_codel | kernel defaults, no `limit`, no `ecn`; per-client flow pinning and per-flow counters as today; background flows must never land in a pinned class (verify and log) |
| red | thresholds from **that egress's own capacity**: min 15 ms, max 45 ms, `limit` = 150 ms worth; no `ecn` |
| cake | as today (`cake unlimited besteffort` under htb), per-client pinning |

Verify before anything else and report: (a) the actual default limits `tc qdisc show` prints on this kernel for codel, pie, fq_codel; (b) whether mvfst sets ECT on its packets; (c) the ECN mark counts in the existing run folders (router metrics). If (c) is non-zero anywhere, list those runs.

### 2.4 Offloads and host settings
- Disable TSO, GSO and GRO on every veth in v3 runs (`ethtool -K ... tso off gso off gro off`), so every qdisc sees MTU-sized packets. Record it in the run folder.
- Report the CPU frequency governor and whether you could set it to `performance`. If you cannot, say so; do not skip the run.
- One run at a time. No parallel runs.

### 2.5 Background traffic generator
Background must be **statistically independent of the video's frame and GOP clock**.

| Mode | Definition |
|---|---|
| **BG-CBR** (default) | `n = max(4, round(BG_e / 2.5 Mb/s))` UDP flows with distinct 5-tuples, equal mean rate `BG_e / n`, each with **Poisson** packet departures (exponential gaps, own RNG stream), payload 1200 B. |
| **BG-BURSTY** | The existing PPBP generator (Hurst 0.8), same mean rate `BG_e`. |
| **BG-MIX** | Same mean `BG_e`, made of: 50 % rate-limited TCP flows (half CUBIC, half BBR, each paced by the application to its share), 30 % on-off TCP flows (2 s of data at 2× the mean, 2 s idle, random phase), 20 % BG-CBR. No greedy flow. |

If you only have a constant-interval UDP sender, add jittered send times to get Poisson gaps; do not use fixed-interval CBR. State what you used.

Every bottleneck egress `e` has its own source `tx-<e>` attached to the router that owns `e`, and its own sink `rx-<e>` attached to the node right after `e`. Source and sink links are 1000 Mb/s, no delay, no AQM. Background for `e` crosses `e` and nothing below it.

### 2.6 Timing, seeds, naming
- Warm-up 15 s, gaps between stimuli uniform 10–15 s, tail 10 s (as today), unless stated.
- Repetition r uses plan seed r and video seed r. The same seed is used across AQMs (paired comparison), as today.
- Run name: `v3-<block>-<type>-<variant>-<aqm>-r<rep>`. `plan.json` additionally records `s`, `U`, `bg_mode`, `rtt_set`, per-egress `C_e` and `BG_e`.

## 3. Topologies

All have `sub-ctrl` (2500 kb/s) on its own 50 Mb/s egress at the first router, as today.

### 3.1 T-BASE (from `base`)
`pub -> router -> switch -> clients`; one bottleneck `main = router->switch`.

Clients (standard set): sub-a 1000, sub-b 2500, sub-c 2500, sub-d 5000 kb/s. `D = 11.33`.
Clients (low set, used only for s = 0.10): sub-a 500, sub-b 1000, sub-c 1000, sub-d 2500 kb/s. `D = 5.15`.

| s | U | client set | C main (Mb/s) | BG (Mb/s) |
|---|---|---|---|---|
| 0.30 | 0.70 | standard | 54.0 | 26.4 |
| 0.30 | 0.50 | standard | 75.5 | 26.4 |
| 0.30 | 0.85 | standard | 44.4 | 26.4 |
| 0.65 | 0.50 | standard | 34.9 | 6.1 |
| 0.65 | 0.70 | standard | 24.9 | 6.1 |
| 0.65 | 0.85 | standard | 20.5 | 6.1 |
| 0.10 | 0.70 | low | 73.6 | 46.4 |
| 0.10 | 0.85 | low | 60.6 | 46.4 |
| legacy | 0.65 | standard | 17.5 | none (today's `base`, pfifo 100 packets, with v3 offload settings) |

(s = 0.10, U = 0.50 needs 103 Mb/s and is left out.)

### 3.2 T-ACCESS (from `access`)
T-BASE at s = 0.30, U = 0.70, plus one access router per client (`ra..rd`). Access egress `r? -> client`: 25 Mb/s, same AQM as the scenario; for pfifo the limit is `ms_to_pkts(25 Mb/s, 50 ms)`. No access background. Access delays as in 2.2.

### 3.3 T-SPLIT4 (from `split`)
`pub -> r1 -> r2 -> {switch-a, switch-b} -> clients`. Bottlenecks: `up = r1->r2`, `a = r2->switch-a`, `b = r2->switch-b`.

Clients: a1 1000, a2 1000, a3 2500, a4 5000; b1..b4 the same. `D_a = D_b = 9.785`, `D_up = 19.57`.

| s | egress | C (Mb/s) | BG (Mb/s) | BG path |
|---|---|---|---|---|
| 0.30 | up | 93.2 | 45.7 | tx-up at r1 -> r2 -> rx-up |
| 0.30 | a, b | 46.6 each | 22.8 each | tx-a at r2 -> switch-a -> rx-a (same for b) |
| 0.65 | up | 43.0 | 10.5 | same |
| 0.65 | a, b | 21.5 each | 5.3 each | same |

(U = 0.70.) Variant **noroot** (microbenchmark M7): `up` unshaped (1000 Mb/s, no AQM, no BG-up).
Variant **mixab** (M8): r1 pfifo; `a` pfifo; `b` fq_codel.

### 3.4 T-TREE16 (from `tree8`)
`pub -> rr -> r0 -> {r1, r2}`, `r1 -> {switch-a, switch-b}`, `r2 -> {switch-c, switch-d}`. Bottlenecks: `root = rr->r0`, `X = r0->r1`, `Y = r0->r2`, leaves `A, B, C, D`.

Four clients per leaf: 500, 1000, 1000, 2500 kb/s (16 clients + sub-ctrl). `D_leaf = 5.15`, `D_mid = 10.3`, `D_root = 20.6`.

At s = 0.30, U = 0.70: leaf C = 24.5, BG = 12.0; mid C = 49.0, BG = 24.0; root C = 98.1, BG = 48.1. One `tx-`/`rx-` pair per egress (seven pairs).

The root is close to the 100 Mb/s limit. If the smoke test fails the health check on this topology, rerun the smoke test with s = 0.35 for T-TREE16 only (root 84.1 Mb/s) and report which was used.

### 3.5 T-UNEVEN (from `uneven`)
`pub -> r1 -> r2 -> {switch-a, switch-b, switch-c}`. `r1->r2` unshaped (1000 Mb/s, no AQM, no background). Bottlenecks: leaves A, B, C.

| Leaf | Clients (kb/s) | D | C at s 0.30 | BG |
|---|---|---|---|---|
| A (2) | 2500, 5000 | 7.725 | 36.8 | 18.0 |
| B (5) | 500, 1000, 1000, 2500, 5000 | 10.3 | 49.0 | 24.0 |
| C (9) | 500, 500, 1000, 1000, 1000, 2500, 2500, 2500, 5000 | 16.995 | 80.9 | 39.7 |

### 3.6 T-REV (from `rev`)
T-BASE at s = 0.30, U = 0.70 with `r0` in front of `r1`, and the reverse-path target `r1->r0` at 10 Mb/s as today.

## 4. Stimuli

`u` = overload factor = total offered load / capacity on the target egress during the stimulus. `d` = duration.

| Stimulus | How it is made |
|---|---|
| **surge** (default) | Extra BG-CBR flows on the target's own background path, total rate `(u - U) * C_e`, as flows of 2.5 Mb/s each (last one fractional), switched on for `d`. Step on, step off. |
| **ramp** | Same extra rate, rising linearly over 5 s (0.5 s steps), held 5 s, switched off. |
| **tcp** | `n` greedy TCP flows (iperf3) on the target's background path for `d`; `n ∈ {2, 4}`, cc ∈ {cubic, bbr}. |
| **join** | An aggregate synchronized-video source (ASV) on the target's background path: UDP, phase 0, emitting the frame-size pattern of the 5000 kb/s rendition (same video seed) scaled to the wanted rate. Rate ramps linearly from 0 to `(u - U) * C_e` in 15 s (scale updated every GOP), holds 15 s, ramps down in 10 s. Each frame is emitted over the same time a real 5000 kb/s client takes to emit that frame in calm; measure this from existing sender logs (first to last packet send time of keyframes and of P-frames) and use the medians. Report the two numbers. |
| **capdrop** | Capacity of the target egress set to `U * C_e / u` for `d` (pfifo limit unchanged in packets). Used on access links (`C` set to client demand / u) and in microbenchmark M2. |
| **revburst** | UDP on the ACK path only, as today's `revcross`. |
| **loss** | Random loss 0.5 / 1 / 2 % for 10 s on **one client's access link at a time**, independent across clients. |

Truth windows, expected clients and `events.csv` are written exactly as today (stimulus windows with their targets). For hierarchy targets, the expected clients are those behind the target egress.

Under fq_codel and cake a surge constrains only the flows above their fair share. That is expected; do not "fix" it. The per-flow truths handle it.

## 5. Scenario types

Grids: `u3 = {1.05, 1.15, 1.3}`, `d3 = {2, 5, 10 s}`. Durations are emulated seconds including warm-up, gaps and tail; yours may differ by a few seconds per seed.

| Type | Topology | Events | ~Duration |
|---|---|---|---|
| **CALM** | any | none | 120 |
| **S-BURST** | T-BASE | surge on main, `u3 × d3`, each cell twice (18 events) | 350 |
| **S-RAMP** | T-BASE | ramp on main, `u3`, each three times (9 events) | 230 |
| **S-TCP** | T-BASE | tcp on main, cc × n × d ∈ {5, 10}, each twice (16 events) | 345 |
| **S-JOIN** | T-BASE | join on main, u ∈ {1.05, 1.15}, each twice (4 events) | 235 |
| **H-HIER** | T-SPLIT4 | surge. Single targets up, a, b: `u3 × d3` each (27). Combined cells a+b simultaneous, a+b with b delayed 0.5 s, a+b with b delayed 2 s, a+up simultaneous: u ∈ {1.15, 1.3} × `d3` each (24). 51 events, shuffled. | 950 |
| **H-DEPTH** | T-TREE16 | surge. Cells A, B, C, D, X, Y, root, A+C: u ∈ {1.15, 1.3} × `d3` each (48 events), shuffled | 900 |
| **H-INDEP** | T-SPLIT4 | surge with independent timing on up, a, b: exponential gaps mean 15 s (min 5 s) per target, u and d drawn uniformly from `u3` and `d3`; overlaps allowed | 600 |
| **H-UNEVEN** | T-UNEVEN | same independent timing on A, B, C | 600 |
| **A-MIXED** | T-ACCESS | shared: surge on main `u3 × d3` (9). Private: capdrop on each client's access link, u = 1.3, `d3` (12). Shuffled. sub-d joins at 60 s. | 410 |
| **L-LONG** | T-SPLIT4 | surge on up, a, b: u ∈ {1.15, 1.3} × d ∈ {10, 30} (12 events) | 415 |
| **R-REV** | T-REV | 9 surges on main (`u3`, d ∈ {2, 5, 10} diagonal ×... use each u with each d once) and 9 revbursts (d ∈ {2, 5}), shuffled | 320 |
| **N-LOSS** | T-BASE | loss stimuli: 3 loss levels × 3 times, a different client each time | 220 |
| **S-STRESS** | T-BASE | surge u = 2.0 × d ∈ {2, 5} twice; surge u ∈ {1.3, 2.0} × d ∈ {0.2, 0.5} three times (16 events) | 280 |
| **S-SPARSE** | T-BASE | surge, 9 events (each u with each d once), gaps uniform 45–75 s | 620 |

## 6. Campaign matrix

Two repetitions of every row. Hours are emulated time for both repetitions.

### 6.1 Gate block (runs first, automatic)

| ID | Runs | Purpose |
|---|---|---|
| G1 | CALM on T-BASE at s 0.30 / U 0.70 and at legacy, pfifo, 1 rep each | load, share, keyframe peak, health |
| G2 | CALM on T-SPLIT4, T-TREE16, T-UNEVEN, T-ACCESS, T-REV at default point, pfifo, 1 rep each | same, per topology |
| G3 | S-BURST on T-BASE default point, pfifo and fq_codel, 1 rep each | stimulus sizing, truth windows, health under surge |

Gate checks on these runs (all must hold, else **stop the campaign** and write `gate-report.md`):
1. Measured calm load on every bottleneck egress within ±0.03 of `U`; measured video share within ±0.03 of `s` (after the 0.96 header correction you already document).
2. ECN marks = 0 on every egress.
3. No skb larger than the MTU at any bottleneck.
4. Health file: tracer lost events = 0; enqueue = dequeue + drops; inter-dequeue time while busy within 10 % of ideal for ≥ 99 % of packets; host CPU idle never below 35 % in any second.
5. During each surge in G3, measured offered load on the target within ±0.05 of `u`.
6. Background is not phase-locked: the spectrum (or autocorrelation) of the background's 5 ms byte counts has no peak at 1 Hz or 30 Hz above its neighbours.

Also report, without gating: the measured keyframe queueing peak per egress (p50 / p90 / max of the queue delay in the 200 ms after each keyframe) next to `0.121 * s * U`, and in the hierarchy topologies at which level the peak forms.

About 0.3 h.

### 6.2 Core blocks (run in this order: all rep 1, then all rep 2)

| Block | Type | Topology and point | AQMs | Runs | Hours |
|---|---|---|---|---|---|
| C1a | CALM | T-BASE, the nine rows of table 3.1 | pfifo, codel | 36 | 1.20 |
| C1b | CALM | T-SPLIT4, T-TREE16, T-UNEVEN, default point | pfifo | 6 | 0.20 |
| C2 | S-BURST | T-BASE default | pfifo, codel, pie, fq_codel, red, cake | 12 | 1.17 |
| C3a | S-BURST | T-BASE s 0.10 (U 0.70) and s 0.65 (U 0.70) | pfifo, codel | 8 | 0.78 |
| C3b | S-BURST | T-BASE legacy; stimulus = today's `burstudp` rule with the v3 `u3 × d3` grid | pfifo | 2 | 0.19 |
| C4 | S-RAMP | T-BASE default | pfifo, codel, pie, fq_codel | 8 | 0.51 |
| C5 | S-TCP | T-BASE default | pfifo, codel, pie, fq_codel | 8 | 0.77 |
| C6 | S-JOIN | T-BASE default | pfifo, codel, fq_codel | 6 | 0.39 |
| C7 | H-HIER | T-SPLIT4 s 0.30 | pfifo, codel, pie, fq_codel | 8 | 2.11 |
| C8 | H-HIER | T-SPLIT4 s 0.65 | pfifo | 2 | 0.53 |
| C9 | H-DEPTH | T-TREE16 | pfifo, codel, fq_codel | 6 | 1.50 |
| C10 | H-INDEP | T-SPLIT4 s 0.30 | pfifo, codel, fq_codel | 6 | 1.00 |
| C11 | H-UNEVEN | T-UNEVEN | pfifo, codel | 4 | 0.67 |
| C12 | A-MIXED | T-ACCESS | pfifo, codel, pie, fq_codel | 8 | 0.91 |
| C13 | L-LONG | T-SPLIT4 s 0.30 | pfifo, codel | 4 | 0.46 |
| C14 | R-REV | T-REV | pfifo, fq_codel | 4 | 0.36 |
| C15 | N-LOSS | T-BASE default | pfifo, codel | 4 | 0.24 |
| | | | **Core total** | **132** | **13.0** |

### 6.3 Microbenchmarks (run after the whole core; all rep 1, then all rep 2)

Each changes one thing relative to C2 (S-BURST, T-BASE, default point, BG-CBR) unless stated. Listed in priority order: if the planned total exceeds the budget, drop from the **bottom**.

| Block | What changes | AQMs | Runs | Hours |
|---|---|---|---|---|
| M1 | pfifo depth 100 ms and 300 ms | pfifo | 4 | 0.39 |
| M2 | stimulus = capdrop instead of surge (same `u3 × d3`) | pfifo, codel | 4 | 0.39 |
| M3 | background mode BG-BURSTY, BG-MIX | pfifo, codel | 8 | 0.78 |
| M4 | RTT: all delays ×0.5; all delays ×4; wide set. pfifo limit follows the largest base RTT of the variant | pfifo | 6 | 0.58 |
| M5 | 15 fps, 60 fps | pfifo, codel | 8 | 0.78 |
| M6 | keyframe phases staggered (0 / 250 / 500 / 750 ms): S-BURST and CALM | pfifo | 4 | 0.26 |
| M7 | H-HIER on T-SPLIT4 **noroot**: cells a, b (`u3 × d3`), a+b simultaneous, a+b delayed 0.5 s and 2 s (u ∈ {1.15, 1.3} × `d3`) | pfifo | 2 | 0.38 |
| M8 | H-HIER on T-SPLIT4 **mixab** | mixab | 2 | 0.53 |
| M9 | S-STRESS | pfifo, codel | 4 | 0.31 |
| M10 | I/P size ratio 2 and 8 (add the publisher option if missing) | pfifo | 4 | 0.39 |
| M11 | bitrates at s 0.65 / U 0.70: 4 × 1000 (C 9.1), 4 × 8000 (C 72.4), 1000 / 2500 / 5000 / 12000 (C 46.4) | pfifo | 6 | 0.58 |
| M12 | forward access jitter 10 ms (order kept); reverse jitter 10 ms | pfifo | 4 | 0.39 |
| M13 | sender congestion control Copa (if available in qvideo-server; otherwise skip and report) | pfifo, codel | 4 | 0.39 |
| M14 | S-SPARSE | pfifo | 2 | 0.34 |
| | | **Micro total** | **62** | **6.5** |

### 6.4 Budget
Gate 0.3 + core 13.0 + micro 6.5 ≈ **19.8 h emulated**, 194 runs plus the gate; expect about 21–23 h wall clock. Compute the real total in the planner from the generated plans. If it exceeds 20.5 h emulated, drop microbenchmark blocks from the bottom until it fits and say which. Never drop a repetition instead of a block, and never drop a core block.

Not in this campaign: the held-out set N1–N5. Prepare a separate command that regenerates N1–N5 on the v3 topologies and parameters (N1 on T-SPLIT4, N2 on T-UNEVEN, N3 with tcp + surge on T-SPLIT4, N4 traces on T-ACCESS access links, N5 churn on a v3 `large` with rates 500 / 1000 / 1000 / 2500 / 2500 / 2500 / 5000 / 5000 and C from the sizing rule). Do not run it and do not open its results.

## 7. Outputs per run and after the campaign

Per run, as today, plus: resolved per-egress `C_e`, `BG_e`, `s`, `U`; background generator log (per-flow rates, start and stop times of every surge flow); ASV log for S-JOIN; offload settings; `gtq-health.csv`.

After the campaign, with the **existing scripts unchanged**:
1. Regenerate the scenario catalog for v3 (same sections; section 5 now shows measured load and share per egress, calm and inside stimulus windows).
2. Detector scores (v2-owd) against GT1 / GT2 / GT3, and against GT-Q / GT-H where valid, per block, AQM, s and U.
3. ECG v1.2 and h3 results for the H-* and A-MIXED blocks.
4. Keyframe table: measured queueing peak after keyframes per egress vs `0.121 * s * U`, per s level; for hierarchies, per level.
5. Rep 1 vs rep 2 for every headline number. **Flag every cell where the two repetitions disagree by more than the spread seen in the other cells of that block**; do not average such cells silently.
6. Health summary: invalid runs, worst CPU idle, worst inter-dequeue error.

No tuning, no new analysis, no changes to the detector or grouping from what you see.

## 8. Implementation order and what to verify without me

1. Checks of 2.3 (kernel defaults, ECT, ECN marks in old runs). Report.
2. Background generator (BG-CBR first, then surge / ramp, then BG-BURSTY wiring, then BG-MIX), with unit tests for rates and Poisson gaps.
3. Sizing rule and constraints in the planner; topologies 3.1–3.6; AQM configuration 2.3; offloads 2.4.
4. Scenario types of section 5 and their planners; truth windows.
5. ASV and S-JOIN. If this is not ready, leave C6 out, say so, and do not block the rest.
6. Campaign runner: gate block with automatic stop, core order, microbenchmark order, per-run health, resume after interruption without overwriting.
7. `--plan-only` output: run list, per-run duration, per-block and total hours, per-egress `C_e` / `BG_e` for every topology and point, constraint check results.
8. **Smoke test (you may run this):** one 60 s CALM run per topology and one 90 s S-BURST with a single event, pfifo. Apply gate checks 1–4 and 6 to them. Fix what fails.

Then stop and report (section 9). Do not start the campaign.

## 9. Final report and hand-over

One file, most important first:
1. The command to start the campaign, the command to resume it, and where the gate report will appear.
2. Planned total hours and run count; anything dropped to fit.
3. Smoke-test results per topology: measured load and share vs target, keyframe peak, health.
4. Results of the 2.3 checks, including any old runs with non-zero ECN marks.
5. Deviations from this spec and every decision you made on my behalf.
6. What is untested.

Keep `docs/paper-notes-ground-truth.md` style notes for this work too: add a "scenario design" section with the sizing rule, the levels of s and U, the background definition, the AQM settings, and every deviation. Do not add citations yourself.

## 10. Flag rather than decide

- Any topology and point that violates a constraint of section 1.
- T-TREE16 failing health at s = 0.30.
- fq_codel or cake runs where no instrumented flow is ever constrained by a surge (expected in some cells; report how many).
- Background flows colliding with pinned fq_codel classes.
- Measured share or load off target by more than the gate tolerance in any core run (mark the run, keep going).
- Copa or the I/P ratio option not available.
- Anything that would need a new hand-picked constant not listed here.
