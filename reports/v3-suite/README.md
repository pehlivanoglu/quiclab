# Scenario and Topology Suite v3: hand-over (2026-11-14)

Spec: [spec.md](spec.md). Code: `scripts/v3_suite.py` (planner, runner), `scripts/v3_gate.py`
(checks), `scripts/v3_checks.py` (section 2.3), `scripts/v3_asv_spread.py` (S-JOIN emission
times), `qvideo/src/Departures.h` + `qvideo/src/Traffic.cpp` (qtraffic). Tests:
`tests/unit/test_qtraffic_v3.py` (8), `tests/unit/test_v3_suite.py` (17); full suite 871 passed.

**Nothing has been emulated yet.** The smoke test (spec 8.8) and the kernel check 2.3(a) are
yours to run (your rule: I give commands, you run them); the commands are below.

## 1. Commands

Run each one inside tmux.

```bash
# 2.3(a) kernel default limits (seconds, no emulation). Save the output, then I parse it:
.venv/bin/python3 scripts/v3_checks.py kernel-cmd | bash > reports/v3-suite/kernel-defaults.txt 2>&1
.venv/bin/python3 scripts/v3_checks.py kernel-parse reports/v3-suite/kernel-defaults.txt

# Smoke test: 6 x 60 s CALM (one per topology) + 1 x 90 s S-BURST, pfifo; ~15-20 min wall
bash scripts/run_v3_smoke.sh
#   watch:  tail -f .runs/*_v3-smoke/run.log
#   result: .runs/<ts>_v3-smoke/smoke-report.md
#   if T-TREE16 fails health: TREE16_S=0.35 bash scripts/run_v3_smoke.sh

# Campaign: gate, then core (rep 1, rep 2), then micro (rep 1, rep 2); ~19.5 h emulated
bash scripts/run_v3_campaign.sh
#   watch:   tail -f .runs/*_v3/run.log ; grep -E "^(==|!!|gate)" .runs/*_v3/run.log
#   gate:    .runs/<ts>_v3/gate-report.md   (starts with "# Gate: PASS" or "# Gate: FAIL";
#            on FAIL the campaign stops with exit 3 before any core run)
#   resume:  bash scripts/run_v3_campaign.sh .runs/<ts>_v3
#            (finished runs are kept; a half-written run is removed and redone; a passed gate
#            is not rerun)
#   per run: <run>/v3-checks.json; at the end: <campaign>/run-checks.{md,jsonl}

# Plan only (writes the YAMLs, prints the budget and the per-egress table, runs nothing)
.venv/bin/python3 scripts/v3_suite.py --plan-only --campaign /tmp/v3-plan > /tmp/v3-plan.md

# Held-out N1-N5 on v3: prepared, NOT to be run in this campaign (60 runs, 10.8 h)
.venv/bin/python3 scripts/v3_suite.py --held-out --plan-only      # check only
# .venv/bin/python3 scripts/v3_suite.py --held-out --run          # later, after the freeze
```

## 2. Budget

| part | runs | emulated h |
|---|---|---|
| gate G1-G3 | 9 | 0.42 |
| core C1a-C15 | 132 | 12.82 |
| micro M1-M14 | 62 | 6.27 |
| **total** | **203** | **19.50** |

Under the 20.5 h budget: nothing dropped. Spec estimate was 19.8 h; per-block hours are within
±0.05 h of the spec's table (durations come from the generated plans). Expect ~21-23 h wall.

## 3. Smoke-test results

**Smoke 2 (.runs/2026-11-14_1801_v3-smoke), re-evaluated under the final rules: PASS on all 7 runs**
([smoke2/README.md](smoke2/README.md)). Smoke 1 diagnosis: [smoke1/README.md](smoke1/README.md).

Not run yet (see section 1). The report will hold, per topology: measured calm load and video
share vs target, keyframe peak (p50 / p90 / max vs 0.121 s U), health (lost events, identity,
inter-dequeue p99, CPU idle), ECN marks, oversize skbs, offloads, phase-lock ratios.

**Gate check 4 (third rules, 2026-11-14; [smoke1/README.md](smoke1/README.md)):** gated on the
run's bottleneck targets only (shaped bottlenecks of the plan, plus access egresses with private
windows):
- 4a: unmatched dequeues and enqueues each <= max(3, 5e-5 x dequeues), <= 2 per 200 ms, rows =
  kernel counters;
- 4b: with >= 1000 backlogged gaps, >= 99 % of gaps within max(10 %, 15 us) of the previous
  packet's serialization time and 20 ms windows >= 99 % within +-5 % (else "not evaluated");
- for the run: lost events 0 and CPU idle >= 35 %.

The publisher, sub-ctrl and other traced egresses are reported only. The tracer uses raw
tracepoints since 2026-11-14 (per-program recursion guard).

The smoke report also lists the `tc qdisc show` line of every AQM leaf (check 2 now also
fails if any shows `ecn`), and per run and client the pacing rate and the keyframe / P-frame
emission times.

## 4. Section 2.3 checks

- (a) Kernel default limits (your run): codel 1000p, pie 1000p, fq_codel 10240p (flows 1024).
  fq_codel's default is ECN **on**, so v3 now writes `noecn` explicitly for fq_codel, codel and pie
  (red: off unless asked). cake has no ECN switch in tc (its help lists none), so it marks
  ECT packets; all v3 traffic is Not-ECT (QUIC, qtraffic UDP, kernel TCP with tcp_ecn = 2).
- (b) mvfst ECT: `TransportSettings.enableEcnOnEgress{false}` (and `readEcnOnIngress{false}`,
  `useL4sEcn{false}`); qvideo never sets them. Video packets are Not-ECT. [check-b-ect.md](check-b-ect.md)
- (c) ECN marks in existing run folders: **none non-zero** in 267 run folders / 1056 egress CSVs
  (cake 33, codel 33, fq_codel 25, pfifo 92, pie 48, red 36 runs). cake's per-tin marks are not
  read by router_metrics, so for cake the column is 0 by construction. [check-c-ecn.md](check-c-ecn.md)

## 5. Deviations and decisions made on your behalf

Constants are tagged in the code: (S) spec, (M) measured, (T) my choice, (FLAG) yours to decide.

**Changes to shared code** (backward compatible; existing scenarios give the same tc commands
and qtraffic behaviour):
1. `RouterQueue.ecn` (optional; unset = `ecn` on, as before). v3 sets `false`.
2. New scenario event `bg` (always-on background; not a stimulus, so no truth script treats it
   as a burst). `bursts` gained optional `process` (pace | poisson | asv), `flow_weights`,
   `seed`, `ramp_up_s` / `ramp_down_s` / `ramp_step_s`, `asv`.
3. qtraffic: `--process=poisson|asv`, `--proto=tcp`, `--mode=plan`; header +4 bytes (flow index)
   so loss is counted per flow (reordering across flows under fq_codel is no longer loss).
   Rebuilt with `cmake --build qvideo/build --target qtraffic` (host build, bind-mounted: no
   docker image rebuild needed, unlike I said before).
4. The backend writes `<run>/offloads.csv` (ethtool -k per interface) for every run, and
   loads `tcp_bbr` for `bg` TCP flows.

**Spec interpretations:**
5. Rates: C_e, BG_e and surges are router (tc) rates. UDP payload = rate x 1200 / 1242
   (IP + UDP + Ethernet as tc counts; (M), to be confirmed by gate check 1); TCP goodput =
   rate x 1448 / 1514.
6. Each shaped bottleneck gets its tx/rx pair even without background (legacy cell), as the
   path for its stimuli. Unshaped links (T-UNEVEN r1->r2, M7 noroot `up`) have none.
7. BG-CBR: one qtraffic process per egress with n sockets (distinct source ports) and n RNG
   streams; non-homogeneous Poisson by thinning. Ramp = staircase of 10 overlapping 0.5 s steps.
8. S-JOIN emission times: keyframe 5.85 ms, P-frame 1.16 ms (pooled medians). Only runs from
   2026-11-14 have per-packet sender logs; the 5000 kb/s clients there are in calmuneven (sync,
   pfifo, 2 reps x 4 clients). One cell disagrees: r1:a1 (keyframe 28.0 ms, P 7.5 ms vs 4.7-7.0 /
   0-1.2 ms elsewhere), **not reliable**, cause unknown. [asv-spread.json](asv-spread.json).
   ASV starts on a GOP boundary and reads its scale at each GOP start.
9. BG-BURSTY: PPBP with today's det-ppbp burst parameters (2 Mb/s, 0.5 s, H 0.8) (T).
10. BG-MIX: one TCP flow per 2.5 Mb/s of each share, even count for TCP (T); TCP is qtraffic's
    own application-paced TCP mode, not iperf3.
11. R-REV revbursts: u cycles through u3 (rate u x 10 Mb/s), d alternates 2 / 5 s (T).
12. M12 jitter: normal distribution, order kept (T, as J1).
13. Smoke S-BURST: one surge at 45 s, u 1.15, d 5 s (T).
14. Gate check 4: unchanged, see section 3 and gate4/. Gate check 6: "peak above its
    neighbours" = power in the 3 bins at 1 / 30 Hz > 10 x the median within 0.5 Hz (T; accepted).
15. fq_codel class collisions of background flows: checked from the GT-Q trace's skb hash
    (bucket = hash x 1024 >> 32 + 1 vs the pinned ids); reported as "unverifiable" when the trace
    holds no hash. Logged, never gating.
16. Held-out N1-N5: seeds 101-105, 5 reps, AQMs as campaign v2 (T). N3 = surge or 2 / 4 CUBIC
    flows, 50/50; N4 = the grouping campaign's trace law on the access egresses plus shared
    surges; N5 = its churn law on v3 `large` (rates 500 / 1000 / 1000 / 2500 x 3 / 5000 x 2).
17. CPU governor: you set it to `performance`; the suite records it in the manifest.
18. pub -> first router is 1000 Mb/s in every v3 topology (delay unchanged), and the publisher's
    egress is traced by GT-Q from now on, for every topology. Details:
    [publisher/README.md](publisher/README.md).
19. Per run and client: median BBR pacing and keyframe / P-frame emission (scripts/v3_emission.py,
    `<run>/v3-emission.json`); `<campaign>/rep-compare.md` lists rep 1 vs rep 2 per cell (calm load,
    keyframe peak per egress), flags a cell when its |r1 - r2| exceeds the largest of the block's
    other cells, and puts both reps' per-client pacing / emission next to every flagged cell.
    P-frames of 1000 kb/s clients often show 0 ms: their packets leave in one batched send.
20. The ASV emission times (item 8) depend on the connection's BBR pacing state. A 5000 kb/s
    keyframe takes ~5 ms on a fast-pacing connection and ~35-50 ms on a slow one (also the
    cause of the r1:a1 outlier, not the publisher link). The smoke re-measures them; I change
    ASV_KEY_MS / ASV_P_MS only after you see those numbers.

**Constraint flags** (spec 10; kept by your decision of 2026-11-14; the planner fails on any
other violation; the 15 % rule does not apply to private access links):

| cell | violation |
|---|---|
| legacy (C1a, C3b, G1) | sub-d 5.15 Mb/s = 29 % of 17.5 Mb/s (> 25 %) |
| T-BASE s 0.65 / U 0.85 (C1a) | 25.1 % (> 25 %) |
| M11 1000 / 2500 / 5000 / 12000 | 27 % of 46.4 Mb/s (> 25 %) |

## 6. Untested

- No run of the new code in Mininet: qtraffic's new modes are tested in plan mode and on
  loopback only (rates, gaps, ports, TCP on-off); timing accuracy inside namespaces at the
  T-TREE16 root (~5000 packets/s from one process) and the CPU cost of 7 tx/rx pairs with
  1000 Mb/s HTB are unknown until the smoke.
- Gate checks 1, 5, 6 have never seen real v3 data (exercised on an old run copy only).
- Kernel defaults 2.3(a).
- Copa (M13) exists in mvfst's controller list (`CcAlgo`) but has never been run here.
- The held-out plan is validated (schema) only.
- After the campaign (spec 7), the catalog / scoring scripts run unchanged; `det_eval` does not
  count `bg` events as cross traffic in its own demand model (the truths use router counters).
