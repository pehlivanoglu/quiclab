**Agree:** GT3 precision (14 / 14 stimulus pairs) and recall (14 / 14; ack-matched 13 / 14), detection delay p50 (12 / 14), onset spread p50 / p90 in about two thirds of the pairs (spec-ACK 9 / 14 and 10 / 14). **Do not agree:** keyframe queue peak, F1 calm mean and sigma (0 / 22 each, simulation 4-9 x smaller), BBR's reaction time D1-bw (0-2 / 14). One model difference explains every failing row: ns-3's TCP does not mark a frame-by-frame video flow as application-limited, so BBR's bandwidth estimate follows the video rate (1.5-1.7 x) instead of staying near the path (testbed 5-6 x), keyframes are paced out over ~70 ms instead of 3-30 ms, and no keyframe queue forms. Matching the ACK policy to mvfst changes almost nothing. Stopped here, as the spec says.

# Simulation stage B: calibration against the testbed (2026-11-18)

Spec: [../../docs/simulation-spec.md](../../docs/simulation-spec.md) section 5. Stage A:
[../sim-stageA-2026-11-17/README.md](../sim-stageA-2026-11-17/README.md). PPBP port check:
[../sim-ppbp-2026-11-18/README.md](../sim-ppbp-2026-11-18/README.md) (identical burst lists, rate 0.0 %, Hurst within 0.01).
Per-cell tables, reps side by side: [tables.md](tables.md). Raw rows: `rows-spec.jsonl`, `rows-matched.jsonl`.

## 1. Validity

| item | value |
|---|---|
| cells | 11 (CALM 4 and 8 clients x pfifo / codel; S-BURST T-BASE x pfifo / codel / pie; H-HIERL T-SPLIT4L x pfifo / codel; G-SIZE T-LEAFn 16 and 24 x pfifo), testbed counterparts K1 A1 / A2 / A4 / G1 r1, r2 |
| runs planned / completed / failed | 2 ACK configurations x 22 = 44 / 44 / 0 (first attempt: 2 crashed, A4 hhier r2, a write after the run's end; fixed, see 7) |
| code version | every one of the 44 runs: quicsim binary `cb92cacb8758f83b` (built 2026-11-18 13:25); 29 runs also carry the source hash `5ad3b13385402e0c`, 15 ack-matched runs finished before source hashes were recorded (binary hash back-filled: same file, same mtime) |
| re-run check (user request) | the 22 spec-ACK runs re-run on the fixed build against the first batch: every simulation output file **byte-identical** in all 22 runs (not even end-of-run lines differ); only `sim/plan.txt` differs, by keys the new build writes (`ack_profile=spec`, the same 2 / 25 ms delayed-ACK values per client) ([rerun-diff.md](rerun-diff.md)) |
| events delivered against plan | exact by construction (the simulator applies the plan's events at their times; `events.csv` written from the plan) |
| measured load and share against target | **not computed for the simulation** (the v3 / v4 load-share check was not run on the simulation folders; the background departure processes are the testbed's own, PPBP verified) |
| GT-Q health | ok on all 44 (identity, rows = counters, sender match 1.000) |
| wall clock | spec-ACK 22 runs 29 min simulation + 41 min frozen scoring; ack-matched 8 min + 18 min (the spec-ACK sum includes guard pauses; longest single run 70 s), 1 core |
| disk | 8.9 GB (spec) + 8.6 GB (matched); first batch 8.9 GB kept for the re-run check; tick cache 4.0 GB |

## 2. Agreement table (spec section 5 limits, P)

Counts are pairs (cell x rep) inside the limit; CALM cells have no stimulus, so 14 pairs carry the stimulus rows.
Values: median over the pairs.

| measure | limit | spec-ACK: ok / fail | ack-matched: ok / fail | testbed median | sim median (spec / matched) |
|---|---|---|---|---|---|
| keyframe queue peak in calm time (p50 of per-GOP maxima) | 20 % | 0 / 22 | 0 / 22 | 5.1 ms | 0.58 / 0.44 ms |
| detector F1 calm mean | 30 % | 0 / 22 | 0 / 22 | 2.16 ms | 0.58 / 0.49 ms |
| detector F1 calm sigma | 30 % | 0 / 22 | 0 / 22 | 1.49 ms | 0.29 / 0.26 ms |
| detection delay p50 (v2-owd on GT3-A) | 30 % | 12 / 2 | 12 / 2 | 161 ms | 129 / 134 ms |
| GT3 precision | >= 0.98 | 14 / 0 | 14 / 0 | 1.00 | 1.00 / 1.00 |
| GT3 recall | +- 0.05 | 14 / 0 | 13 / 1 | 1.00 | 1.00 / 1.00 |
| onset spread p50 (per leaf and stimulus) | 30 % | 9 / 5 | 7 / 7 | 49.5 ms | 33 / 33 ms |
| onset spread p90 | 30 % | 10 / 4 | 9 / 5 | 147 ms | 132 / 149 ms |
| D1-bw reaction (delay p50) | 30 % | 0 / 14 | 2 / 12 | 506 ms | 0 / 0 ms |

Onset spread (the row that decides event formation, user 2026-11-18): onsets live on the detector's 33 ms tick, so
the spread takes values 0, 33, 66, ... ms; most "fails" at p50 are one tick (33 against 50 ms, the testbed median of 33
and 66). At p90 the simulation is within one or two ticks in most cells and wider on G-SIZE r2 (244 / 363 against 175 /
247 ms). Per cell and rep: [tables.md](tables.md). The 30 % limit is tighter than the measure's resolution for p50
(FLAG for the user: a tick-resolution limit, e.g. +- 1 tick, would read differently).

Not limited (spec section 5 "also report"): delay p90, false alarms per minute, GOP drops per client-minute, video
rate under overload, grouping scores: [tables.md](tables.md). Frozen SETS leaf F1 (k = 2) median 0.947 testbed, 0.95
simulation. GT3 from frames (source B, testbed side, user request 4): recall median 0.998 against 1.00 from per-packet
OWD (source A), precision 1.00 on both: the source difference is small on these cells.

## 3. Why the failing rows fail: BBR in application-limited flows (user request 3)

Measured, per client (pooled medians, spec-ACK; ack-matched in [tables.md](tables.md)):

| quantity | testbed (mvfst) | simulation (ns-3) |
|---|---|---|
| share of ACK rows marked app-limited | 0.85 | 0.025 |
| BBR bandwidth estimate / client video rate (A1 calm-base r1: sub-a, b, d) | 5.2, 6.1, 4.8 | 1.7, 1.5, 1.7 |
| share of time in ProbeBW / STARTUP | 0.93 / 0.06 | 0.99 / 0.001 |
| pacing gain in effect at keyframe writes (p50) | 1.20 | 1.24 |
| keyframe pacing spread (v3_emission, median per egress) | 3-4 ms calm, 24-31 ms with surges | 66-73 ms in every cell |
| keyframe queue peak in calm time (v3_gate, p50) | 13-15 ms (T-BASE, up), 5 ms (leaves), 18-19 ms (T-LEAFn) | 0.3 ms (2.6 ms T-LEAFn) |

The pacing gain is the same; the bandwidth it multiplies is not. A keyframe (12 % of a GOP: ~38 KB at 2.5 Mb/s) paced at
1.24 x 3.9 Mb/s leaves in ~63 ms in the simulation; on the testbed the estimate is 15 Mb/s and the keyframe leaves in a few
ms, so all clients' keyframes meet at the shared egress and build the 0.121 s U queue the spec predicts. That queue is
what F1 measures in calm time, and BBR's own estimate is what D1-bw reads: in the simulation it rises and falls with the
video rate, so D1-bw fires all the time (10 false alarms / min, precision 0.33-0.38, its first alarm before every onset:
delay p50 0).

Mechanism, from the source (no change to the ns-3 model, user request):

| | mvfst 4b691f3 (testbed) | ns-3.48 TcpBbr |
|---|---|---|
| parameters | STARTUP gain 2.885 (`Bbr.h:20`), ProbeBW cycle 1.25 / 0.75 / 1 x 6 (`Bbr.h:31`), bandwidth filter 10 rounds (`Bbr.h:41` numOfCycles + 2), min-RTT window 10 s (`Bbr.h:46` kDefaultRttSamplerExpiration), ProbeRTT 200 ms (`Bbr.h:35`) | HighGain 2.89, `PACING_GAIN_CYCLE` same (`tcp-bbr.cc:22`), BwWindowLength 10, RttWindowLength 10 s, ProbeRttDuration 200 ms; pacing 1 % below the estimate (`tcp-bbr.h:391` m_pacingMargin 0.01) |
| STARTUP exit test | bandwidth must grow 1.25 x per round; 3 rounds without = exit; skipped for app-limited samples (`Bbr.cpp:284-286`, `694-713`) | the same rule and skip (`tcp-bbr.cc:305-322`) |
| when is a flow app-limited? | whenever the write loop finds less than one packet to send while the window allows more (`QuicTransportBaseLite.cpp:1910-1913` -> `Bbr.cpp:648-655` setAppLimited) | only inside `Send()`, **after** the new data is added (`tcp-socket-base.cc:920-937`; rule `tcp-rate-ops.cc:142-148`: less than one segment unsent). Linux checks before adding the data. Every frame write adds at least one segment, so the check never fires for this application |
| effect on the bandwidth estimate | app-limited samples cannot lower the max filter (`BbrBandwidthSampler.cpp:166-173`): the estimate keeps the path's rate from the last unlimited burst | every sample counts: the estimate is the delivery rate of the video itself |

So the difference is where ns-3 marks application-limited data, not BBR's parameters. FLAG: this is the largest model
difference found; it affects every measure that depends on how fast a keyframe leaves (keyframe queue, F1, D1-bw), and
it would affect stage C the same way. The decision on a fix (an application-side app-limited mark, or placing the check
as Linux does) is the user's; nothing was changed.

## 4. ACK policy (user request 2)

The testbed's receiver (mvfst 4b691f3, `qvideo/build/_deps/mvfst-src`): ACK after 10 ack-eliciting packets
(`QuicConstants.h:625,627` rxPacketsBeforeAck{Before,After}Init = 10; `QuicStateFunctions.cpp:128-152`), else on the
ACK timer max(timer tick, min(maxAckDelay 25 ms, 0.25 x srtt)), rounded up to ms (`QuicTransportBaseLite.cpp:3766-3777`;
`QuicConstants.h:631,633`; `AckStates.h:81`); tick = folly HHWheelTimer default 10 ms (`HHWheelTimer.h:99`; the client
uses a default EventBase, `Client.cpp:265`); no ACK_FREQUENCY (`Client.cpp:69-85`). The spec's "every 2 segments, at
most 25 ms" was therefore not close to mvfst.

"ack-matched": ns-3 delayed-ACK count 10 and a fixed per-client timeout from the same formula at the client's base RTT
(10-13 ms here). FLAG: ns-3 has one fixed timeout per socket; mvfst's grows with srtt under queueing (up to 25 ms).
Effect on the section 5 measures: none on the agreement counts beyond one or two pairs either way (table in 2); ACK
rows per client fall towards the testbed's.

## 5. Stage C sizing from the 100-client test run (user requests 2 of 2026-11-18)

Test run: v4 suite's own planner (G1-type T-LEAFn, 100 clients at 500 kb/s, default point s 0.30 U 0.50, S-BURST,
335 s, pfifo, seed 1), [simulation/simlab/gen_plan.py](../../simulation/simlab/gen_plan.py). 33 500 client-seconds.

| quantity | 100 clients x 335 s |
|---|---|
| simulation wall clock, 1 core | 164 s (0.49 x real time) |
| frozen scoring (GT1, GT3, GT-Q, detector) | 295 s |
| peak memory | 1.28 GB |
| output | 1.86 GB raw (55.5 kB / client-s); zstd -3 0.33 GB (9.8 kB / client-s); zstd -19 0.20 GB |

Per file type ([sizes-n100.md](sizes-n100.md)), kB per client-second raw / zstd -3: router-trace packets 30.1 / 3.9
(54 % of all bytes), sender -owd.csv 8.6 / 1.2, -acks.csv 3.7 / 1.3, -cc.csv 2.4 / 0.6, truth gt3-labels 2.1 / 0.2
(derived), -sent 1.8 / 0.6, client -frames 1.8 / 0.6, -pkts 1.7 / 0.5, sender -frames 1.5 / 0.3, -pktacks 0.8 / 0.3,
-playback 0.6 / 0.2, everything else < 0.2.

Proposal for stage C (to agree before the plan is final):

| keep | how | why |
|---|---|---|
| -acks, -sent (detector input), -owd (GT3 A), -cc (D1 baselines), sender / client -frames, -drops, -playback, router-metrics, traffic/* | all clients, zstd -3 after the run | frozen readers need them |
| router-trace packets, -pkts, -pktacks (GT-Q) | **sampled bottlenecks only**: the upstream egress plus every 10th leaf (at least 2 leaves), and those leaves' clients' -pkts / -pktacks | 54 % of the bytes; spec: per-packet queue records on a sample only |
| truth/*-labels | not kept (regenerated by the frozen scripts when needed) | derived |

Estimate with that rule: ~5.0 kB / client-second after zstd -3 (4.9 for the kept per-client files, ~0.1-0.4 for the
sampled traces). A 1000-client 900 s run: ~4.5 GB compressed (~20 GB raw while being written). The full section 6 grid
(100 / 300 / 1000 clients x 4 layouts x pfifo / codel x 2 seeds at 900 s, plus the U 0.70 row) is ~20 M client-seconds:
**~100 GB compressed**. Proposed budget: **<= 5 GB per run, <= 60 GB for stage C**, which means 600 s runs (~65 GB)
or dropping one layout at 1000 clients, the user's choice.

Open points this sizing exposes (FLAG, not decided):
- Memory: the simulator keeps every transmission of every flow in memory (for the exact per-packet records): 1.28 GB at
  33 500 client-seconds, so a 1000 x 900 s run would need ~30 GB, above the 16 GB rule. Needed before stage C: release
  acknowledged transmissions (a code change; the records do not change).
- Compression and the frozen readers: they read plain CSV (`det_eval.rows` uses `open`, pandas has no zstd module in
  the environment), so scoring a compressed run means decompressing it to a temporary folder first (~20 GB at 1000
  clients, transient).
- Wall clock: if it scales with client-seconds, a 1000 x 900 s run takes ~75 min to simulate and ~2.3 h to score on
  one core; the full grid ~25 h simulation + ~45 h scoring on one core (~12 h + ~23 h on 2 cores). Packet-rate effects
  above 100 clients are not measured yet: one 300-client test run would pin this down.
- Addressing: quiclab's `node_loopback_ips` allows 254 nodes, so 300 and 1000 clients need our own addressing for the
  plan builder (stage A already flagged it).

## 6. Deviations and decisions taken on the user's behalf

- GT3 from per-packet OWD (source A) on both sides (spec 4, accepted by the user); source B shown for the testbed.
- Frozen SETS on frozen-detector onsets, through R1's level T100 path (`reports/sets-low-threshold-2026-11-16/r1.py`
  `run_level`) and `grouping_score`; the simulation has no live grouping output, so both sides use the testbed
  counterpart's ECG configuration.
- `qdiscs.txt` in the simulation folders is written from the simulation plan (the frozen SETS scorer reads each
  egress's AQM from it), not a kernel dump (FLAG).
- The keyframe table reuses the analysis session's code: testbed values from each run's own `v3-checks.json` /
  `v3-emission.json`, simulation values from the same functions (`v3_gate.keyframe_peaks`, `v3_emission.run_emission`).
- Calm time for the F1 and queue rows: outside every stimulus window widened by [-1 s, +3 s], after the 5 s warm-up.
- The "0.121 s U minus spread" prediction is in [tables.md](tables.md) per egress (ref 18.1 ms; with the testbed's
  calm spread of 3-4 ms the prediction is 14 ms and the testbed measures 13-15 ms on shared egresses).

## 7. Faults found and fixed during stage B (simulation code only)

- Router trace times on egresses with netem delay (first smoke: sender match 0.82-0.96): fixed (NOTES.md FLAG 5).
- Two runs crashed (segmentation fault): data arriving after the run's end was written to closed files; the sink and
  sender now ignore it. The re-run check shows no other output changed.
- Comparison script: three faults (D1 spans read as starts, `qdiscs.txt` missing, a plan-builder branch for plans
  that never ran on the testbed); none touched a simulation output.
- A cache write into a K1 testbed folder on 2026-11-17 (removed the same minute, reported then); the frozen detector's
  cache now goes to `reports/sim-cache` only.

## 8. Constants

Unchanged from [simulation/NOTES.md](../../simulation/NOTES.md); new in stage B: the ack-matched profile (count 10,
timeout max(10, min(25, ceil(0.25 x base RTT))) ms; M, from mvfst's source), the onset-spread search window
[start - 1 s, start + 10 s] (det_eval's detection window, reused).

## 9. What these runs cannot tell

- Whether the measures that agree would still agree once the application-limited difference is removed: the keyframe
  queue feeds F1, and F1 feeds the detector; the detector rows agree now partly because surges dominate them.
- Anything about fq_codel / cake, jitter, loss, TCP background (not modelled), or about QUIC-specific behaviour.
- Harm at the player (TCP head-of-line blocking; spec 1).
- Stage C cost above 100 clients (one test run only).
