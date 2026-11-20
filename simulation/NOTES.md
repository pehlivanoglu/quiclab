# Simulation notes (spec: ../docs/simulation-spec.md)

Kept by the simulation session; the paper notes are merged from here on request.
Stage A: [../reports/sim-stageA-2026-11-17/README.md](../reports/sim-stageA-2026-11-17/README.md) (accepted
2026-11-17: mainline ns-3.48, same design).

## Design

One simulation run = one testbed run's plan. `simlab/plan.py` reads the testbed run's `topology.yaml` +
`scenario.yaml` through quiclab's own models and helpers (link conditions, router queues and limits,
interface names, loopback addresses, the egresses the testbed samples and traces, the qtraffic sources
and schedules), writes `sim/plan.txt`, and copies the plan artifacts. `ns3/quicsim` builds the network
and writes the testbed's run-folder records, so the frozen detector, truths, SETS and scorers read the
folder unchanged.

| piece | source |
|---|---|
| frame sizes, live schedule, GOP-aware send queue, playback | `qvideo/src/Common.h`, `SendQueue.h`, `Playback.h`, included unchanged (symlink `ns3/quicsim/qvideo`) |
| background / stimuli departures | `qvideo/src/Departures.h` (poisson), `Ppbp.h` (PPBP bursts), the pace credit loop of `Traffic.cpp`, same seeds |
| pump: hand frames to the transport while unsent < 1 cwnd, every 5 ms and after each frame | `Server.cpp` `pump()` |
| per-ACK record (`-acks.csv`), `-sent.csv`, `-owd.csv`, `-cc.csv`, `-frames.csv`, `-drops.csv`, `-pkts.csv`, `-pktacks.csv`; `clients/-frames.csv`, `-playback.csv` | `Server.cpp` / `Client.cpp` formats |
| router-metrics (25 ms deltas, 5 ms queue), router-trace packets, interfaces, tracer counts | `router_metrics.py`, `router_trace.py` formats |
| `events.csv` | the testbed run's rows, applied times = plan times |
| `gtq-health.csv` | `quiclab.router_trace.health`, unchanged |

Files: `ns3/quicsim/{quicsim.cc,plan.h,common.h,flow.h,video.h,traffic.h,router.h}`, `simlab/{plan.py,run.py}`,
`build_ns3.sh`; ns-3 source in `third_party/ns-3.48` (official tarball, `third_party/ns-3.48-download/PROVENANCE.md`),
FlowBot generator copy in `third_party/flowbot-sim` (PROVENANCE.md). No ns-3 file is edited.

## Constants

| constant | value | tag | where |
|---|---|---|---|
| TCP segment | 1208 B (IP packet 1260 B = testbed QUIC packet 1232 + 28) | M | plan.py SEGMENT |
| delayed ACK | every 2 segments, at most 25 ms | M | spec 4 |
| initial cwnd | 10 segments | M | |
| minimum RTO | 200 ms (Linux; ns-3 default 1 s) | M | |
| TCP send / receive buffer | 16 MiB (the queue lives in the application; pump caps unsent at 1 cwnd) | FLAG | spec 4 says "about one cwnd" |
| pacing | on (BBR sets the rate) | M | |
| unshaped direction | 10 Gb/s | FLAG | veth |
| queue of a direction with netem and no AQM | fifo 50 000 p | M | shaping.py `_NETEM_LIMIT_PKTS` |
| queue of a rate-only direction, no AQM | fifo 1000 p | FLAG | htb default leaf (txqueuelen) |
| AQM limit when the plan gives none | 1000 p | FLAG | Linux default |
| device queue | 1 packet | FLAG | the queue stays in the queue disc |
| epoch | simulator t = 2 s; initial clients connect at 1 s | FLAG | |

## Queue limits and conversions (FLAG: every conversion)

The testbed plans already carry packet limits computed by the suite with the user's formula
`max(20, C x 50 ms / 1500 B)` (e.g. 75.53 Mb/s -> 315 p); the simulation uses the plan's value, so the
two agree by construction. RED: bytes as `shaping.py` (`min` / `max` bytes, limit = packet limit x 1500 B
or 4 x max), avpkt 1200, max_p 0.02. Spec 4's time-based RED (15 / 45 / 150 ms) would be converted with
the egress capacity (bytes = C x t / 8); no stage-B cell uses RED, so none is converted yet.

## FLAG list (differences that could move a result)

1. TCP instead of QUIC: head-of-line blocking at the receiver (frame completion), delayed ACKs instead
   of QUIC ACK frequency, cumulative + SACK instead of per-packet ACKs.
2. Arrival times from the simulator clock (ideal receive timestamps).
3. `-acks.csv`: a row only for ACKs that move the cumulative ACK (duplicate / SACK-only ACKs have no row);
   `rtt_us` = ACK time - send time of the acked transmission (includes the delayed-ACK hold; mvfst
   subtracts ack delay); `send_bps` uses delivered bytes / send interval (mvfst: bytes sent / send interval);
   `newly_lost` = ns-3 rate-sample lost bytes / segment.
4. Per-packet size columns: IPv4 length - 28 (equal wire size to the testbed's QUIC packets).
5. Router trace: video packets written with proto 17 (frozen GT-Q selects by UDP). Times: `t_enq` = arrival
   at the egress (= queue entry here), `t_deq` / `t_drop` = simulator time + egress netem delay (testbed chain
   htb -> netem -> AQM: the packet leaves after delay + queue; the labeler's `t_deq - (t_enq + delay)` is the
   true sojourn and the sender-log match sees the true arrival). First version subtracted the delay from
   `t_enq` instead: correct sojourn but match 0.82-0.96 on pub-eth0; with this mapping 1.000 (smoke A2 r1).
   Tracer counts: `n_enq` = enqueue attempts (tail drops included), packets still queued at the end excluded.
6. Delay on the wire after the queue (testbed: netem before the AQM); equal end to end for FIFO service.
7. ns-3 TcpBbr (BBRv1 port of Linux) vs mvfst BBRv1: same parameters; **application-limited marking differs** (largest
   model difference, stage B report section 3): ns-3 checks only in Send() after adding data, so a frame-by-frame video
   flow is never app-limited; BBR's bandwidth estimate follows the video rate (1.5-1.7 x, testbed 5-6 x), keyframes
   leave in ~70 ms instead of 3-30 ms, no keyframe queue forms. Not changed (user: size of effect first).
11. ACK policy: spec-ACK (2 segments / 25 ms) and ack-matched (mvfst: 10 packets / max(10, min(25, 0.25 srtt)) ms; ns-3
   fixed timeout from base RTT) both run in stage B; little effect.
12. `qdiscs.txt` written from the plan (simlab/qdiscs.py) for the frozen SETS scorer; not a kernel dump.
8. HTB burst (15 KB) not modelled: the shaped device serialises at exactly C.
9. Switch modelled as an IP node (testbed: L2 switch).
10. PIE / CoDel: ns-3 models vs Linux qdiscs (to be tabled with every attribute in the stage B report).

## Decisions and deviations after stage B (user, 2026-11-18)

- ACK profile: **ack-matched is primary** (mvfst: 10 packets / max(10, min(25, 0.25 base RTT)) ms); the 2-segment
  profile stays a second row in stage B only.
- **Deviation (criterion widened after the results were seen):** onset spread p50 / p90 and detection delay p50 agree
  when within 30 % OR within one detector tick (33 ms), whichever is wider, because both are quantised to the tick.
  No other criterion changes.
- **Application-limited patch (FLAG, to be stated in the paper):** one ns-3 file changed,
  `patches/ns3-tcp-app-limited-before-add.patch`: the app-limited check moved before the new data is added, as Linux
  (`tcp.c` v7.0:1204, check :1113-1127). Remaining differences: ns-3 lacks Linux's qdisc / NIC-queue condition; mvfst
  marks whenever its write loop runs dry, not only at writes. Details: patches/README.md.
- Stage C budget: <= 5 GB per run, <= 60 GB total, zstd, per-packet queue records on the upstream link plus every
  10th leaf (never fewer than 3 leaves per run), 600 s runs, all layouts.

## After stage B2 (user acceptance 2026-11-18)

- Stage B2 (patch 1, both ACK profiles): reports/sim-stageB2-applimited/README.md. Accepted: F1 mean fixed; spread
  p50 agrees (12 / 14 before the patch already, under the tick rule; chat summary corrected in the report).
- **Use restrictions (binding for stage C reports):** the simulation may be used for grouping at scale (SETS leaf F1,
  pair precision; pair recall optimistic by ~0.08), detection precision / recall / delay p50, onset spread p50. It must
  not be used for false-alarm rates, the keyframe queue size, or **D1-bw (never reported from the simulation: its
  delay is 2.5 x late, which favours our method)**.
- Deviation (definition fault, fixed before any table): calm "keyframe-aligned" window 3 ticks, not the 2 declared
  first (33.0 ms tick grid drifts against the 33.3 ms frame grid).
- **Patch 2 (FLAG: models mvfst, no longer plain Linux behaviour), off by default:**
  `patches/ns3-tcp-app-limited-mvfst-drain.patch`, GlobalValue `QuiclabAppLimitedAtDrain` (set by run.py
  `--applimited mvfst` through NS_GLOBAL_VALUE). One pre-declared attempt (user): one-run check, then stage B once,
  ack-matched only; it becomes primary only if keyframe peak p50 AND D1-bw delay p50 agree in a clear majority of cells
  and no agreeing row gets worse; otherwise dropped. No third variant, no parameter change. Result:
  reports/sim-stageB3-mvfst-drain/README.md. **Dropped 2026-11-19: no effect** (one-run check byte-identical to B2
  with the value verified on; stage B3 not run). Patch reversed in the tree, file kept in patches/dropped/ (not
  applied; build_ns3.sh refuses a tree that still has it).

## Item 5: scale (accepted plan, user 2026-11-18; code in place 2026-11-19)

Gate: byte-for-byte regression on two B2 matched runs (A4 hhier-def, G1 sburst-n24) before anything else; any
differing byte means stop and report. **Correction 2026-11-19: both runs were pfifo; PIE changed and went unseen (see "Randomness").** ns3/quicsim-b2/ keeps the B2 source of quicsim (reference, not built).

- **E-pool (engineering constant, not a model parameter): 256 MiB** shared output buffer for all Csv files
  (common.h OutputPool / CsvBuf); above it every buffered file is flushed. Was 1 MB per file (~12 files per client).
- **E-horizon (engineering constant, not a model parameter): 10 s** in-memory horizon for per-transmission records
  (flow.h kRecordHorizonNs): records older than every segment's last transmission and 10 s are released; OWD bins are
  streamed to owd.csv once 10 s old. A packet arriving for a released record or an already written bin is counted,
  never dropped silently: `late_arrivals` in the quicsim done line and in sim/meta.json, every run. **Expected 0;
  non-zero is a finding, reported, never tuned away.**
- Routing: nix-vector (on-demand per source/destination) instead of global routing (all-pairs tables, N^2);
  build_ns3.sh enables the module and reconfigures once. Tree topologies have one path, so routes are unchanged.
- Addresses beyond 254 nodes / routes and more than 256 background flows per event: simlab/scale_ext.py (patches
  quiclab.runtime / scenario models at import; up to 254 entries returns exactly the original addresses; nothing
  in quiclab/ edited). run.py imports it first; stage-B scoring runs the frozen scripts through it.
- Link subnets: 10.0.0.0 - 10.98.255.0 (quicsim.cc throws past that: 25,344 links).
- Background source ports: each event gets a block of max(300, its flows) from 30000 (plan.py); with <= 300 flows per
  event identical to B2. Ceiling: 35,535 background flows per run (plan.py raises). One UDP socket per flow is
  kept (each flow its own 5-tuple); a failed bind falls back to an ephemeral port, a second failure stops the run.
- **Rejected and reverted (accepted by the user 2026-11-19): "one UDP socket per background event".** It merged all
  flows of an event into one 5-tuple on the wire: a model change (any flow-hashing queue, fq_codel / cake, would see
  one flow instead of hundreds) that a byte regression on pfifo runs cannot detect. The port-label overlap it was
  meant to fix is solved in plan.py (port blocks above).

## Grouping at the 300-client leaf (accepted by the user 2026-11-19; reports/sim-scale300/sets-npr.md)

**Superseded 2026-11-19 evening by the fast-links re-run (reports/sim-scale300-rerun/README.md).** The first run's
surges were weakened at the source.
- With full-strength stimuli the SETS group appears at the 2nd stimulus, not the 7th (leaf F1 0.885, not 0.50).
- Onset spread p50 is 66 ms, not 280 ms.
- NPR-B no longer splits the leaf.
- Superseded: "late group because of the method" (mostly the weakened surges); NPR-B's splits in the first run (also
  the weakened surges); every onset-spread figure of the first run.
- Standing: the 0.5 s event window holds at 300 clients (0.02 % outside); one leaf only.
- New: SETS on E1-0.5 splits the leaf permanently after a single 299-member event (one late member; q = 0 at near-zero
  miss rate, nothing is forgotten). Stage C reports grouping per stimulus level (u 1.05 / 1.15 / 1.3).
- The text below is kept as written (SUPERSEDED).

- **Frozen SETS forms the leaf group late, from the method, not the simulation:** first group at close 21 (stimulus 7,
  138 s), none before. Two causes:
  - (1) E0 events (150 ms) split each stimulus at a 280 ms onset spread (18 stimuli -> 40 closes);
  - (2) the miss-rate estimate starts at 0, so a group needs an observation that contains a stored set up to one
    flow (first complete 300 observation).

  SETS stays frozen and is reported as it is. On E1-0.5 events the same rule still waits for the second complete
  observation (stimulus 4).
- **NPR-A and NPR-B (frozen, E1-0.5) find the leaf at the first stimulus** (close 2, 15 s). NPR-B splits it (two
  extra groups inside the leaf) during closes 3-13; NPR-A never splits it. One leaf only: this tests finding and
  keeping a leaf, not separating leaves.
- FLAG: after SETS bootstraps, m stays near 0.5 (q ~ 170 of 300); untested with several leaves.

## Recorder fault: CoDel drops counted twice (found 2026-11-19 by health-lite; fixed, user decision U1)

- **Fault:** ns-3 fires a queue disc's "Dequeue" trace for every packet taken out of its internal queue, including
  one that CoDel then drops ("DropAfterDequeue"; ns-3 queue-disc.cc PacketDequeued / DropAfterDequeue). quicsim's
  egress monitor (ns3/quicsim/router.h) counted such a packet as dequeued AND dropped:
  - router-metrics transmitted_bytes too high;
  - router-trace: a "dequeue" row and a "drop" row for the same packet;
  - tracer-counts enq < deq + drop.
- **Scope:** recording only; the simulated network is unchanged.
  - Affected queues: CoDel only among those modelled. PIE, RED, pfifo and fifo drop before enqueue only.
    fq_codel / cobalt / fq_pie also drop after dequeue, but they are not modelled.
  - Affected runs: every run with CoDel and drops-after-dequeue. In B2 that is identity_ok = 0 on A2-sburst-codel and
    A4-hhier-codel (both reps, both ACK profiles); calm CoDel runs have no such drops.
  - No other double-record path: a requeued packet fires "Dequeue" once (QueueDisc::Dequeue with m_requeued).
- **Fix:** the dequeue record is held until the next callback or sample, and cancelled when the same item is
  dropped right after. The row text is formatted at the dequeue, so its tags and size are as they were then. The
  packet is then a drop only, as the testbed's tracer records it.
- B2 re-run with the fix: simulation/runs/stageB2-codelfix, reports/sim-stageB2-codelfix (see the B2 report's
  correction).

## Background source ports in stage C (user decision U2, 2026-11-19)

- plan.py --ports:
  - **global** (default; stages A / B; byte-identical to before): one range, blocks of max(300, flows);
  - **route** (stage C, 100 / 300 clients): per route (source node), blocks of exactly the source's flows, never
    reused;
  - **reuse** (stage C, 1000 clients): per route, a block is given to a later source once the earlier one has ended
    (+1 s); such sources open their sockets at their own start and close them at their end (plan "lazy=1").
- **Restriction: reuse only for runs without GT-Q (trace "none") and with pfifo / fifo queues only.** plan.py
  refuses it otherwise, so it never applies to a per-flow queue (fq_codel, cake, ...) or a run with GT-Q.
- Check: route and reuse on the same pfifo run give identical outputs except what carries a port label: plan.txt
  sport / lazy, the src_port column of traffic/*-flows.csv, and the run's byte count in meta.json.
- Stage C plan check (42 runs): highest port in use on one route 14,041 (300 clients, route) and 2,369 (1000
  clients, reuse), of 35,536.

## Randomness (inventory 2026-11-19; user decision: fixed streams)

| source | where | seeded by | status |
|---|---|---|---|
| background / stimulus departures (Poisson) | qvideo Departures.h (std::mt19937_64 per flow) | the plan's event seed (splitmix) | own generator, fixed |
| PPBP bursts | qvideo Ppbp.h (mt19937_64) | the plan's event seed | own generator, fixed |
| frame sizes (size_sigma) | qvideo Common.h frameSize | hash of (video seed, rate, index) | deterministic, fixed |
| client phase / join / leave times | plan.py (from the scenario) | the plan | fixed |
| ns-3 run seed | quicsim.cc RngSeedManager | plan seed, run 1 | fixed |
| **PIE** drop decision | ns-3 PieQueueDisc m_uv | **stream kStreamQueue + egress index (since 2026-11-19)** | **fixed** |
| **RED** early drop | ns-3 RedQueueDisc m_uv | same (RED not used in any run so far) | **fixed** |
| **BBR** ProbeBW cycle index, sender | ns-3 TcpBbr m_uv (EnterProbeBW) | **stream kStreamBbr + flow index** | **fixed (user 2026-11-19 evening)**; changed the S-BURST / H-HIERL / G-SIZE runs, adopted as the new B2 reference (stageB2-streams) |
| BBR, receiver (listening socket; accepted sockets share it) | ns-3 TcpBbr m_uv | **stream kStreamBbrRx + flow index** | fixed |
| ARP request jitter, IPv6 / ICMPv6, global routing (tests) | ns-3 internet stack | **InternetStackHelper::AssignStreams from kStreamStack** | fixed (never drawn here; fixed anyway) |
| congestion-control objects the socket factory creates and quicsim replaces at once | ns-3 TcpL4Protocol | automatic | never used: replaced before the connection starts |
| CoDel, pfifo, fifo | | | no randomness |

- Item 5 correction: removing global routing shifted the automatic stream numbering and changed PIE's drop sequence.
  The item-5 byte regression covered only two pfifo runs. The B2 PIE rows from before 2026-11-19 cannot be
  reproduced with the current build; the reference PIE runs are simulation/runs/stageB2-piestreams.
- **No random variable that is used in the simulation is on automatic numbering** (from 2026-11-19 evening).
- **Regression gate from now on:** at least one run per queue type used (pfifo, CoDel, PIE; RED if used), plus the
  scenario types where BBR enters ProbeBW (S-BURST, H-HIERL, G-SIZE); not two pfifo runs. Each gate run also:
  - with QUICSIM_EXTRA_RVS=7 (unrelated random variables created first);
  - with QUICSIM_GLOBAL_ROUTING=1 (other routing objects).

  Both must be byte-identical to the plain run. Test outputs go to a temporary folder outside quiclab/ and are
  removed there once the gate has passed.
- **B2 reference runs from 2026-11-19 evening: simulation/runs/stageB2-streams** (all 44; every random stream fixed;
  binary 0bf1962382fb9e3d plus the later stream fixes of the receiver BBR and the internet stack, shown
  byte-identical on 7 gate runs). Superseded:
  - simulation/runs/stageB2-codelfix (post-U1) and stageB2-piestreams (PIE-only fix);
  - stageB2-applimited (original B2).

  The user deletes them.
- v1 (stage B before the application-limited patch): runs and caches deleted 2026-11-19. reports/
  sim-stageB-2026-11-18/README.md restored from the session record; its generated tables are gone (RESTORED.md
  there).

## Traffic sources limited by the testbed's 1 Gb/s source links (found 2026-11-19 by health-lite; OPEN, user decision)

- Every background / stimulus route starts at a source host tx-<egress> on a 1000 Mb/s link (v3 SRC_SINK_MBPS, the
  testbed's NIC). At scale one route's offered rate exceeds it, and the excess is dropped in the source host's own
  queue (unmonitored) before it reaches the planned bottleneck.
- **300-client test:** an S-BURST surge at u = 1.3 offers 796 Mb/s on top of 348 Mb/s background (u = 1.15 just above
  1 Gb/s too). Light check item 4: unacked video + lost background exceeds the router drops by 676k packets
  (1.68M lost against 1.00M dropped at the router). The surges arrived weaker than planned; calm load / share
  (background only, 348 Mb/s) was unaffected.
- **Stage C as planned:** the largest single source per route is 1.19 Gb/s at 300 clients (L100) and 3.98 Gb/s at
  1000 clients (upstream). The upstream's own background at 1000 clients is above 1 Gb/s, so the calm gate (S5) would
  fail.
- **Decision (user, 2026-11-19 evening):** plan.py --fast-links. Every link direction that is not a designed
  bottleneck (a shaped egress of v3-plan.json) runs at 100 Gb/s: sources, sinks, the publisher's link, client
  access links, inter-router links and reverse directions. With it, quicsim writes router-metrics/queue-totals-all.csv
  (every queue disc), so health-lite item 7 can check that no queue but a designed bottleneck drops. Item 8 checks
  that the load offered to the bottleneck in each stimulus window matches U_e x C_e + extra.
  - Used for stage C and the 300-client test only; B2 and every testbed-counterpart plan are unchanged.
  - Audit per layout and client count: reports/sim-stageC-plan/link-audit.md.
- **Results of the first 300-client run that rest on weakened surges** (u = 1.3 at 0.86-0.89 of the planned load;
  u = 1.15 slightly):
  - the onset spread per leaf and the share of onsets outside 0.5 s (reports/sim-scale300/README.md section 4);
  - the SETS-at-300 analysis and the NPR diagnostic (reports/sim-scale300/sets-npr.md);
  - the GT-Q / GT3 episode counts.

  Timings, memory and sizes are affected only slightly (the source host dropped 676k packets that never reached the
  router). The re-run with fast links replaces them (reports/sim-scale300-rerun).

## Offline scoring against an online system (check 2026-11-19, user request)

What the offline detector / grouping pipeline uses that an online system at that instant would not have:

- **Clean** (no look-ahead):
  - detector input: per-ACK OWD at the ACK's arrival time; the testbed's OWD comes from mvfst ACK receive
    timestamps (qvideo/src/Client.cpp:75-82), the simulation gives the same exactly;
  - tick features binned by ACK arrival, running-minimum base, EWMA normalisation;
  - the F3 "congested" mask gets no_truth in the frozen path (frozen.py:59-62);
  - the onset = the CUSUM's last zero before the alarm, known at alarm time;
  - SETS's own E0 events (alarms in arrival order, close 1.3 s after the first aligned onset);
  - NPR-B's past-fitted null;
  - ground truth: whole-run, but used for scoring only.
- **To fix (user decision 2026-11-19, OPEN; to be done once the emulation runs that lock heavy work have finished,
  and before stage C):** the grouping's onset alignment uses each flow's **whole-run** minimum RTT
  (scripts/grouping_adapter.py:265, FlowMeta.mrtt). An online system knows only the minimum up to the alarm.
  - Fix: the running minimum at each onset's alarm time.
  - The code is in scripts/ (frozen, shared with the testbed scoring), so testbed and simulation change together.
  - Gate: the grouping outputs of the B2 runs, the 300-client run and their testbed counterparts, before and
    after; every changed value reported.
- **Accepted as is (user 2026-11-19):** E1-0.5 events are formed offline in aligned onset time and treated as closed
  at first onset + 0.5 s. A member's alarm can arrive later than that, by the detector lag. Group membership is
  what an online system gets by reading the event that much later. Time-to-group figures from E1-0.5 events are
  optimistic by the detector lag; say so wherever such a time is reported.

## Not modelled (plan.py raises)

jitter, loss, asymmetric delays, delay changes, fq_codel / cake / dualpi2, AQM changes, ECN, TCP
background, salvos, asv, pauses, forced paths (T-HAYES), more than one publisher. (Addressing beyond 254 nodes:
item 5, scale_ext.py.)

## Status

- 2026-11-18: stage B done, report reports/sim-stageB-2026-11-18/README.md (stopped there, as the spec says).
  44 runs (2 ACK profiles x 22), one binary cb92cacb8758f83b; spec-ACK re-run byte-identical to the first batch.
- Before stage C (open, user): app-limited fix decision; memory (release acked transmissions); addressing > 254 nodes;
  compressed outputs + sampled GT-Q traces (budget proposal in the report, section 5).
- 2026-11-18: stage B2 done (44 runs, binary cb92cacb8758f83b, lib internet 21eecfc6eeaf93bd); patch 2 added (off by
  default; the library hash changes with it, so later runs carry a new build id).
- 2026-11-19: mvfst check done, no effect, patch 2 dropped. Item 5 code moved in (ns3/quicsim); byte regression
  passed (A4 519 + G1-n24 368 files identical, late_arrivals 0); accepted by the user. 300-client test: user starts
  simulation/runs/joblogs/scale300.sh.
- 2026-11-19: 300-client test done and accepted (reports/sim-scale300/README.md; late arrivals 0). SETS / NPR at the
  300 leaf analysed (reports/sim-scale300/sets-npr.md, simlab/sets300_diag.py). Stage C numbers and plan, plan only:
  reports/sim-stageC-plan/README.md (simlab/stagec_numbers.py). User rules from 2026-11-19: no simulation or heavy
  scoring while a campaign runs; otherwise all simulation work < 45 GB, heavy scoring one step at a time. 10,000-client
  attempt: no GT-Q, no router trace (user).
- 2026-11-19 afternoon: D1-D3 code written (reports/sim-stageC-plan/d1-d3.md). Fast scoring path identical on 44 B2
  runs (300-client part pending). Trace modes full / sample / none: byte regression passed; sample / none identical
  to full outside the trace. FAULT FOUND (FLAG, not fixed, user decision U1): the egress monitor counts CoDel's
  drops-after-dequeue as dequeued too (ns-3 fires "Dequeue" before "DropAfterDequeue"): transmitted_bytes and trace
  "dequeue" rows too high under CoDel; identity_ok = 0 on 8 B2 CoDel runs (A2-sburst, A4-hhier). Stage C plan check:
  32 / 42 runs exceed the background port ceiling (D2, user decision U2).
- Batches are run by the user (detached command via batch_guard auto); tests by this session.
