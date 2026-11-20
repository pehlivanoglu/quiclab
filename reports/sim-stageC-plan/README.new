# Stage C plan (plan only; 2026-11-19, rewritten for the user's standing instructions of that day)

**Stage C starts only after the emulation is completely finished (the 12 runs, then K5, until about Friday
afternoon). The user starts every batch.** Nothing here has run.

Measured inputs come from one run, the 300-client test (`../sim-scale300/README.md`). Every other number is
extrapolated by `simulation/simlab/stagec_numbers.py` (rules in its header); the full per-run table is in
`numbers.md`. The older `numbers.txt` belongs to the earlier grid (100 / 300 / 1000 x both queues, traces everywhere)
and is superseded.

**Answer first:**
- The decided grid is 42 runs, 9.8 M client-seconds.
- It fits the disk if run outputs are compressed after scoring: 56 GB compressed under quiclab/, ~76-88 GB at the
  peak with runs in flight. The tick cache sits outside quiclab/, one run at a time (<= 7.4 GB).
- Memory stays at or below 20 GB per step: largest GT-Q 19.7 GB at 300 x L100; at 1,000 clients the largest steps
  are SETS 13.7 GB and the detector 8.4 GB, both upper bounds.
- The grid takes about **26-28 h** of wall-clock time on this machine. **11 core-hours of it (~23 % of all CPU) are
  the quadratic input reading** in SETS and GT3 scoring, 9.5 h of those at 1,000 clients.

## 1. Grid (user decisions, 2026-11-19)

| block | clients | layouts | queues | seeds | point | GT-Q / router trace | runs |
|---|---|---|---|---|---|---|---|
| C1 | 100 | L10, L50, L100, uneven 2-200 | pfifo, CoDel | 2 | U 0.50 | yes, sampled: upstream + every 10th leaf, >= 3 leaves | 16 |
| C2 | 300 | same | pfifo, CoDel | 2 | U 0.50 | yes, sampled | 16 |
| C3 | 1,000 | same | pfifo | 2 | U 0.50 | **no** (detector against GT3 only; grouping truth from the topology) | 8 |
| C4 | 1,000 | L50 (**assumed**, W3) | pfifo | 2 | U 0.70 | no | 2 |

All runs 600 s, 500 / 1,000 kb/s clients mixed, events per spec section 6 (per-leaf surges, a share on two leaves at
once, a share on the upstream link). Run names `sim-C-<block>-<layout>-n<clients>-<queue>-r<seed>`.

Kept for every run, for later grouping scoring without re-running: the frozen onsets (episodes-v2-owd.json) and the
event lists (E0 and E1-0.5, as JSON). That is ~0.4 MB per 100 clients. Frozen SETS is scored as the reference row.
Which NPR variant is scored at scale is decided after the analysis session's validation.

## 2. Numbers (extrapolated unless marked measured)

### 2.1 Measured base (300 clients x 335 s, one run)

| step | wall | peak RSS |
|---|---|---|
| quicsim | 475 s | 0.52 GB |
| health (frozen, full trace) | 557 s | 8.96 GB |
| detector | 184 s | 1.41 GB |
| SETS step | 200 s (of which ~98 s quadratic input reading, measured 0.164 s per `det_eval.Run` x 606) | 2.29 GB |
| GT3 | 145 s (of which ~98 s the same input reading) | in truth step |
| GT-Q | 1,345 s | <= 11.0 GB |

Sizes per client-second: 52.1 kB raw, 9.1 kB zstd; tick cache 12.4 / 4.0 kB.

### 2.2 Per run, 600 s (from numbers.md; ranges over layouts)

| block | raw output GB | zstd GB | tick cache raw GB | sim min | heavy min (health + GT-Q + detector) | light min (SETS + GT3) | of which N^2 input min | largest step peak GB |
|---|---|---|---|---|---|---|---|---|
| C1, 100 | 2.1-3.1 | 0.4-0.5 | 0.7 | 4-5 | 10-21 | 2-3 | 1 | GT-Q 2.9-6.6 |
| C2, 300 | 5.3-9.4 | 1.0-1.6 | 2.2 | 14 | 21-62 | 10 | 5 | GT-Q 5.6-19.7 |
| C3, 1,000 | 12.5 | 2.7 | 7.4 | 47-63 | 18 (detector only) | 72 | 57 | SETS <= 13.7, detector <= 8.4 |
| C4, 1,000 U 0.70 | 12.5 | 2.7 | 7.4 | 66-88 (x1.4, FLAG) | 18 | 72 | 57 | as C3 |

### 2.3 Grid totals

#### Disk for the grid, by component (GB)

| component | raw | zstd -3 |
|---|---|---|
| router-trace | 75.8 | 10.3 |
| publishers | 174.8 | 38.3 |
| rest | 36.0 | 7.3 |
| onsets+events | 0.0 | 0.0 |
| tick cache (outside quiclab/; one run at a time, so never all at once) | 122.0 | 39.8 |
| **outputs (all but cache)** | **286.6** | **56.0** |

Largest single run in flight: 1000 clients L10: raw output 12.5 GB + its tick cache 7.4 GB raw (outside quiclab/).

#### Time for the grid (hours)

| part | hours | how it runs |
|---|---|---|
| simulation | 13.5 - 16.1 core-h | in parallel |
| heavy scoring (health, GT-Q, detector) | 18.8 | one at a time |
| light scoring (SETS, GT3) | 15.1 core-h | beside the heavy queue |
| of which the N^2 input reading (det_eval.Run per flow) | 11.0 core-h | inside SETS and GT3 |

N^2 input reading by size: 100: 0.2 h, 300: 1.4 h, 1000: 9.5 h.
Light scoring at 1000 clients: 12.0 core-h, heavy at 1000: 3.1 h.

### 2.4 Disk: peak and end (extrapolated; check again at the start)

| | GB |
|---|---|
| free now (2026-11-19 14:00, measured) | 225 |
| expected free when stage C starts (user: after the 12 runs and K5) | ~140 |
| outputs kept under quiclab/, compressed after each run's scoring (W1) | 56 |
| raw output of runs in flight (scored before compression): 1 / 2 runs at 1,000 clients | 12.5 / 25 |
| tick cache outside quiclab/, one run at a time (largest) | 7.4 |
| **peak use**: 1 / 2 runs at 1,000 in flight | **76 / 88** |
| **free at the peak** (from ~140) | **64 / 52** (52 is just above the 50 GB warning) |
| **free at the end** | **~84** |

Without compression (if W1 is "no"): 287 GB of raw outputs. That does not fit, and the plan would stop.

### 2.5 Wall-clock time (extrapolated)

Heavy scoring (health, GT-Q, detector) runs one step at a time. The tick cache exists for one run at a time, so the
detector and SETS of one run finish before the next run's detector starts. Simulations and GT3 run beside, within
45 GB.

| block | critical chain | hours |
|---|---|---|
| C1 + C2 | heavy queue (health + GT-Q + detector); SETS beside it | ~15.7 |
| C3 + C4 | detector + SETS per run (cache one at a time), 10 runs | ~9.5 |
| lead time (the first simulations before scoring can start) | | ~1 |
| **total** | | **~26-28** |

CPU besides the chain: simulations 13.5-16 core-h, GT3 and the rest of light scoring in parallel. The quadratic
input reading is 11 core-h (0.2 at 100, 1.4 at 300, 9.5 at 1,000), about 23 % of all CPU in the grid. At 1,000
clients it is 57 of the 72 light-scoring minutes per run.

## 3. Health check without the router trace (C3, C4, and the 10,000-client attempt): proposal, waiting (W4)

### 3.1 What the frozen check verifies from the trace, and what replaces it

| # | item the frozen check verifies | from | in the simulation today | without the trace: from aggregate counters or sender-side records? |
|---|---|---|---|---|
| 1 | tracer started / stopped clean, lost events, kernel counters = rows written (`rows_match`), no-hit / truncated / requeue / oversize, unmatched enqueue / dequeue (`accounting`) | the eBPF tracer's counters (tracer-counts.csv) and its rows | true by construction: quicsim's own recorder writes every row; these counters guard the kernel tracer | **not needed**: no tracer, nothing to lose. One item stays: the output files are complete (`files_open_at_exit` 0, done line present) |
| 2 | packet identity per egress: enqueued = dequeued + dropped | tracer counters | yes (quicsim counts) | **yes, from aggregate counters.** The ns-3 queue disc's own totals (enqueued / dequeued / dropped packets per egress), written as one row per egress at the end. They exist today only as tracer-counts.csv, which is written only with the trace on: a small change to write them always |
| 3 | service timing while backlogged: inter-dequeue gap against 8 len / C (p50 / p99 ratio, share within tolerance, jitter, 20 ms windows within 5 %) | every dequeue time | yes | **partly, from router-metrics** (25 ms intervals): transmitted bytes per interval while the queue is non-empty, against capacity x interval. Shows that the egress serves at its configured rate; does not show per-packet gaps or jitter |
| 4 | sender match rate: share of each subscriber's sent packets found on the egress, in order (`match.<sub>`, `match_rate_min`) | trace rows joined with the sender's -pkts | yes (1.0 at 300) | **partly, from sender and receiver records**: per subscriber, packets sent and packets acknowledged with timing (sender -owd.csv columns packets_sent / packets_timed per bin), frames sent against frames received (sender -frames / client -frames; the client keeps no per-packet record). Checks that each flow's unacknowledged packets match its retransmissions / losses, and that the sum over flows on an egress is consistent with that egress's drop counter (router-metrics drops; QUIC retransmits, so this is a consistency check with a tolerance, not an identity). Does not show that a given packet crossed a given egress (routing is fixed in a tree, so that is by construction) |
| 5 | CPU idle of the host during the run | host-cpu.csv | empty in the simulation (no host contention) | not applicable |
| 6 | bytes written | file sizes | yes | yes (without the trace part) |

Items the user listed, outside the frozen check, all available without the trace:
- measured load and share against target: the frozen `v3_gate.check_load_share` reads router-metrics and sender
  -sent, not the trace;
- events delivered against plan: events.csv against traffic/*-bursts.csv and the plan;
- drops: router-metrics per egress (and per flow where the queue has flows);
- late arrivals: `late_arrivals` in the quicsim done line and meta.json (E-horizon; expected 0).

### 3.2 Proposal: a lighter check ("sim-health-lite"; not written, waiting for the user)

Per run, from aggregate counters and sender / receiver records only:
1. completeness: done line present, `late_arrivals` 0, `files_open_at_exit` 0;
2. per egress: enqueued = dequeued + dropped (quicsim writes the queue-disc totals with or without the trace; small
   quicsim change, byte regression with the trace on);
3. per egress: transmitted bytes in backlogged 25 ms intervals within a tolerance of capacity x interval;
4. per subscriber: packets sent against packets acknowledged, frames sent against frames received; the losses summed over an egress's flows within a tolerance of its drop counter;
5. load and share against target (frozen check, unchanged), events against plan, drops listed.

It would **not** cover:
- per-packet service gaps and jitter (item 3 only at 25 ms resolution);
- per-packet identity on a given egress (item 4 only as totals per flow);
- anything GT-Q needs. The run has no GT-Q, so GT-Q validity does not arise.

Cost: linear in clients, no full-trace read. Memory: per-client totals only, well under 1 GB at 10,000 clients
(estimate).

Tolerances in items 3 and 4 are not set here. They would be (P), declared before the first run, and checked on the
B2 runs and the 300-client run, where the frozen check passes.

### 3.3 Validation against the frozen check (once written; the 300-client run has the trace, so both checks run on it)

- On the 300-client run and the 44 B2 runs, compare item by item:
  - item 2: the queue-disc totals equal tracer-counts.csv (n_enq, n_deq, n_drop) exactly;
  - item 3: the 25 ms backlogged-rate check passes on every egress where the frozen per-packet service check passes;
  - item 4: per-flow losses from the sender records against the per-flow drop rows in the trace (exact where QUIC
    did not retransmit, within the declared tolerance otherwise).
- Negative tests on scratch copies outside quiclab/: a truncated sender file, a missing egress counter row, and a
  capacity mismatch in the plan. The light check must flag each one.
- Accepted only if it passes on every run where the frozen check passes and flags every negative test. Writing it
  starts only after the user agrees.

## 4. Faster scoring path: description only, for the user's decision (W5)

**What:** a scoring entry point in `simulation/simlab/`, next to the frozen scorer (no frozen file changed). It
removes the quadratic input reading in two ways, in one process per run:
1. it builds `det_eval.Run` once per run and reuses it (today it is built twice per flow per `gt3.run_truth` call,
   each build re-parsing topology.yaml and scenario.yaml);
2. it computes GT3 once per run (`gt3.run_truth`) and hands the same result to the SETS onset building
   (`grouping_adapter.truth_of`) and to the GT3 scoring step. Today it is computed in both.

The plan / topology / scenario files are then read once per run.

**Acceptance:** byte-identical outputs on the 44 stage B2 runs and the 300-client run, against the frozen path:
- gt3.csv and gt3-labels.csv;
- episodes-v2-owd.json;
- the SETS rows (sets.json / rows) and the E0 / E1-0.5 event lists.

Any difference means stop and report. The risk is that a caller mutates the shared `det_eval.Run` object; the
regression would show it.

**Effort:** about half a day of code and tests. The validation on B2 runs is light (small runs, allowed during the
campaign under the guard). Re-scoring the 300-client run is heavy and waits until no campaign runs.

**Expected saving:**

| | today | with the faster path |
|---|---|---|
| grid, light-scoring CPU | 15.1 core-h | ~4 core-h (-11) |
| grid wall-clock (C3 + C4 chain: detector + SETS 57 -> ~28 min per run) | ~26-28 h | ~21-23 h |
| 10,000 clients, per 100 simulated seconds: SETS step / GT3 step | 15.7 h / 15.3 h | ~0.5 h / ~0.2 h |

**Is the 10,000-client attempt feasible without it?** Yes, but slowly: ~30 core-hours of input parsing per 100
simulated seconds, split over the two steps (~15 h wall if they run in parallel), on top of ~1.3-3 h of simulation.
Memory is not the limit there (SETS <= 23 GB per 100 s simulated, an upper bound). The run length is not planned
here (user).

## 5. The 10,000-client column (no router trace, no GT-Q; per 100 simulated seconds; run length not planned)

| quantity | per 100 s simulated |
|---|---|
| raw output / zstd | 20.9 / 4.5 GB |
| tick cache raw / zstd | 12.4 / 4.0 GB |
| simulation | 1.3-3.0 h, peak 5.8 GB |
| detector | 31 min, <= 14 GB |
| SETS step | 15.7 h (N^2 input 15.2 h, pair loop 0.2 h), <= 23 GB |
| GT3 step | 15.3 h (N^2 input 15.2 h) |
| health | the light check only (W4) |
| GT-Q | not run (user) |

D2 (35,535 background-flow ceiling): untouched until that attempt is planned.

## 6. Proposed temporary tick-cache folder (W2, waiting for the user)

**`/home/ubuntu/simcache-stageC/`** (new folder, outside quiclab/, on the same disk as everything else; this machine
has one data disk).

Layout `<folder>/<run name>/shadow-v2/ticks-frozen-owd/*.csv`, written by the frozen tick builder through
`simlab/frozen.py`; its CACHE becomes a parameter, while `reports/sim-cache/` stays the default for everything else.

Deletion rule, as the user set it:
- only in that folder, only tick files this session produced;
- only after the run's scoring finished and its outputs exist and are complete (scored.json without "FAILED",
  episodes and event lists written, sets rows written);
- a failed step keeps the cache and is reported.

The cache can be rebuilt from the run's raw records by the same frozen builder. So the raw records of a run are
compressed only after its cache is deleted, and re-scoring later means decompressing to a temporary folder first.

## 7. Batch: commands (planned; the driver `simulation/simlab/stagec.py` is not written yet)

Start, in tmux, only after the emulation has finished and the disk check passes:
```bash
tmux new -s stagec
cd ~/Research/Repos/multirelay/quiclab && .venv/bin/python3 reports/batch_guard.py auto --session sim --what "stage C" --cores 8 --expect <end> -- nice -n 19 .venv/bin/python3 simulation/simlab/stagec.py run --blocks C1,C2,C3,C4 --sim-parallel 4 --tick-cache /home/ubuntu/simcache-stageC 2>&1 | tee -a simulation/runs/joblogs/stagec.log
```

Watch:
```bash
cd ~/Research/Repos/multirelay/quiclab && .venv/bin/python3 simulation/simlab/stagec.py status    # runs done / running / failed, memory, disk, next step
tail -f simulation/runs/joblogs/stagec.log
```

Stop cleanly: `Ctrl-C` in the tmux window. The guard passes SIGTERM; the driver stops the running steps and keeps
every finished run. Resume with the same start command: it skips runs whose scored outputs are complete, and
restarts a run whose simulation did not finish (its folder kept and reported, never deleted).

What the driver checks:
- Before each run: free disk, against the run's expected size; it stops cleanly if the end would fall below 50 GB.
- Before each step: the expected peak memory against 45 GB minus what is running. It does not start a step that
  does not fit.
- Every minute: swap use. If the machine swaps, it stops and reports.

Before handing over these commands I will state:
- free disk then;
- the batch's expected use (measured from the smoke runs);
- the expected free disk at the end.

If that is below 50 GB, there is no command.

## 8. Steps

| step | what | when | gate |
|---|---|---|---|
| S1 | Router-trace sampling (upstream + every 10th leaf, >= 3) and -pkts / -pktacks for the sampled clients only; a "no trace" switch for C3 / C4; queue-disc totals written with or without the trace | code now (allowed) | byte regression on 2 B2 runs (trace on, all egresses) |
| S2 | `stagec.py`: plan-only, run, status; scoring queue (health out of run.py into the serial queue; memory check per step; one tick cache at a time with the deletion rule; onsets and events kept; compression after scoring per W1) | code now | dry run on the 300-client run (scoring only, when no campaign runs) |
| S3 | `stagec.py --plan-only`: run list, capacities, expected events per leaf, the uneven layout's leaf list, expected disk / memory / time per run | code now | user reads the list |
| S4 | Smoke run per layout (short, 300 clients) and one 1,000-client smoke | user starts, after the emulation | within 20 % of the numbers here, else they are redone |
| S5 | Gate: one calm run per layout, load and share against target (frozen v3 check) | user starts | ok on every egress |
| S6 | Grid C1-C4 | user starts | disk / memory / swap rules |
| S7 | Scoring rows: detector (and D1-bw never reported from the simulation, D2, D3), frozen SETS reference, NPR variant per the analysis session; report per spec section 9 with the B2 use limits | after S6 | - |

## 9. Waiting for the user

- **W1. Compressing each stage C run under quiclab/ after its scoring.** The 56 GB figure assumes it. The standing
  rule forbids compressing anything under quiclab/ "to make room", so I ask instead of assuming. Without
  compression it is 287 GB and does not fit.
- **W2.** The temporary tick-cache folder `/home/ubuntu/simcache-stageC/`.
- **W3.** The layout of the U 0.70 row (L50 assumed).
- **W4.** The light health check (section 3): write it?
- **W5.** The faster scoring path (section 4): write it?
- **W6.** The uneven layout's leaf list (drawn by `--plan-only`; the sampled share above uses L50 as a proxy).

## 10. Risks

- **R1.** Frozen SETS forms groups late at large leaves (method; `../sim-scale300/sets-npr.md`). Reported as it is.
  Expect late groups at L100 and in the uneven layout's largest leaves.
- **R2.** SETS's m ~ 0.5 tolerance after the bootstrap, untested with several leaves.
- **R3.** Detector and SETS memory at 1,000 clients are linear upper bounds (8.4 / 13.7 GB), unmeasured above 300.
  The smoke run measures them.
- **R4.** The U 0.70 simulation time factor (x1.4) and the "upstream" trace share (layout without upstream
  background) are assumptions.
- **R5.** Everything rests on one 300-client run until the smoke runs.
