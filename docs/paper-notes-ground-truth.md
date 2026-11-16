# Paper notes: ground truths (GT-Q, GT-L, GT-H)

Kept up to date while the GT-Q / GT-H work goes on (spec "Ground Truth and Scoring
Spec, final" v1.2, section 8). Code names: GT-L is still called GT3 in the code
(rename postponed by the user, 2026-11-14); GT1 / GT2 remain as they are.

## 8.1 Fixed roles for the three ground truths (seed note)

With three ground truths a reviewer can say "you picked the favourable one for each
metric". The defence is that the roles were fixed in advance, each with a stated
reason:

- Precision -> GT-Q. An alarm raised while any real congestion exists is not wrong.
- Recall (headline) -> GT-H. Where a miss matters is congestion that causes harm.
- Detection delay -> GT-Q onset. That is the physical start.
- Lead time -> GT-H. How long before harm.
- GT-L -> side column for every metric.

In addition, a full table showing every metric at all three levels goes in the
appendix, so it is visible that nothing was cherry-picked.

## 8.2 Log

### 2026-11-14: implementation (no real run yet)

**Freeze:** GT-Q parameters, the theta grid and the operating-theta rule are NOT
frozen yet: no run with the tracer exists. Record the commit hash here when they are,
and confirm it happened before the scorer was run on the detector.

**How sojourn is measured.** Kernel tracepoints via bpftrace, one tracer per router:
enqueue = `net:net_dev_queue` (just before the root qdisc's enqueue, every packet),
dequeue = `qdisc:qdisc_dequeue` (root qdisc), drop = `skb:kfree_skb` of a packet that
was enqueued and not dequeued. Qdisc chain on a traced egress:
`htb 5: (class 5:1, rate C, burst 15k) -> [netem 10: delay only] -> AQM leaf 20:`.
Without netem the root's enqueue-to-dequeue time is the time in the AQM leaf (HTB
keeps no queue of its own above a single class). With a delay-only netem the
sojourn is t_deq - t_enq - d(t_enq), d = the netem delay in force at enqueue (netem
fixes each packet's release time at its enqueue; a later `tc change` does not move
it); the remainder is time queued in the AQM or held by HTB. Egresses whose netem
has loss or jitter are not traced (netem loss would look like queue drops; jittered
release times are not known per packet). Egresses towards the publisher carry no
subscriber's forward traffic and are not traced. Clock: CLOCK_MONOTONIC ns, the clock of
router-metrics, events.csv and qvideo-server's mono_us.

**t_obs method.** Primary (b): router packet -> QUIC packet number by flow + order +
size (router skb->len = QUIC encoded size + 42 B, 0 <= t_enq - t_send <= 2 s, up to
256 sender packets skipped for loss before the router), then the first ACK whose
newly acked ranges contain that number. Used per flow when >= 95 % of the flow's
router packets match (threshold chosen by the agent, not tuned on data); otherwise
the config fallback (a) = t_deq + base OWD router -> client + base delay client ->
sender (scenario t=0 delays). Both are recorded where both exist (`t_obs_b_minus_a_ms`).
Drop-only episodes always use (a) from the first drop (a dropped packet is never acked).

**Deviations from the spec / judgment calls (agent, 2026-11-14):**

1. Busy-run end (3.4 step 1): the spec says "t_deq of the first non-busy packet after
   the run". Read literally, on a lightly loaded link the next packet arrives a whole
   frame interval later and the "run" spans the idle gap (a 15 fps, 2.5 Mb/s video on
   10 Mb/s would show 66 ms runs). Implemented: min(t_deq of the next packet, t_deq of
   the last busy packet + tau), i.e. when the queue drained. Found by the idle-link
   sanity test.
2. Enqueue tracepoint: `net:net_dev_queue` instead of `qdisc:qdisc_enqueue` (the latter
   fires only on NET_XMIT_SUCCESS and misses packets fq_codel accepts while dropping
   from the same flow).
3. t_stim: the latest scripted stimulus in [t0 - 3 W, t0 + W] ("within a few W").
   Stimuli = scenario link / aqm / flow / ppbp event times and burst starts.
4. tau(t) and capacity: C from events.csv applied link events (det_eval.capacity_series),
   MTU 1500 B. The health check's inter-dequeue ideal uses scheduled event times
   (same values, ms apart).
5. fq_codel sub-queue: pinned flow id from skb->priority (20:<minor>, minor - 1), else
   reciprocal_scale(skb->hash, 1024), as fq_codel_classify. f's sub-queue = the mode of
   its packets' index; other flows' packets in that index are included and listed as a
   collision in gtq-params.csv. cake: its set-associative hash is not reproduced; f's
   own packets only (flagged by the AQM name). dualpi2: treated as one shared queue.
6. GT-H horizon: a frame never received counts as a miss only if t_gen + B is before
   the end of the client's log (last received frame, at most duration - 1 s);
   otherwise it is censored. Sender head-dropped frames (drops.csv) miss at t_gen + B
   with t_gen = drop time - age.
7. AQM changes during a run (aqm events): the t=0 AQM decides the sojourn sequence;
   gtq-params.csv flags `aqm_changed`.
8. Scorer: the detectors emit alarm start times, not a score in [0, 1]; there is no
   theta sweep yet, one operating point per detector. Alarm starts closer than W are
   merged. Missed episodes are counted as censored; the Kaplan-Meier CDF is not drawn yet.
9. Gray zone: busy runs in [W/2, W) without an f drop and not inside an episode; and
   tau-episodes with no overlap with a 2 tau episode (drop intervals exist at both
   thresholds, so drop episodes are never gray).
10. Netem delay on a traced egress (access routers, router -> sub-ctrl) is subtracted
   per packet (see "How sojourn is measured"); the onset t0 is then the time the
   packet left netem, i.e. arrival + delay.

**Facts to disclose about GT-L (= GT3 in code):** it uses the same client packet
timing (ACK receive timestamps) the detector consumes; its constants were chosen
earlier (2026-11-07/08) and are unchanged; it is reported as a reference column only.

**Facts to disclose about GT-Q:** the W and tau derivation is our own design (no
sources added; record them only when given).

**Still to append after the first real runs:** W and tau per scenario and the gray
share per AQM; emulation fidelity (inter-dequeue / ideal distribution, from
gtq-health.csv); match rate and b - a per scenario; the nesting result GT-H in GT-L
in GT-Q with exception counts.

### Frame-side GT-H on the existing 192-run campaign (2026-11-08_det-*, I/P 4)

Deadline misses as a share of produced frames (send_us / recv_us; head-dropped frames
count; `late_us` not used). client send_us equals sender send_us for every received
frame (0 mismatches in 992 run x client logs); misses fall monotonically 300 -> 600 ->
1000 ms in every log.

| campaign | AQM | frames | head-dropped | miss 300 | miss 600 | miss 1000 | late_us > 0 |
|---|---|---|---|---|---|---|---|
| access | fq_codel | 109 718 | 780 | 4.66 % | 2.87 % | 1.40 % | 93 |
| access | pfifo | 109 718 | 597 | 4.54 % | 2.81 % | 1.32 % | 132 |
| access | pie | 109 716 | 571 | 4.51 % | 2.83 % | 1.27 % | 109 |
| access | red | 109 716 | 597 | 4.37 % | 2.76 % | 1.20 % | 101 |
| base | fq_codel | 1 458 598 | 25 891 | 8.68 % | 6.45 % | 4.23 % | 582 |
| base | pfifo | 1 458 530 | 49 587 | 15.12 % | 10.78 % | 7.14 % | 1 316 |
| base | pie | 1 458 545 | 43 695 | 14.78 % | 10.28 % | 6.35 % | 1 101 |
| base | red | 1 458 557 | 38 503 | 14.27 % | 9.55 % | 6.16 % | 1 058 |
| split | fq_codel | 274 380 | 2 691 | 6.01 % | 4.18 % | 2.30 % | 108 |
| split | pfifo | 274 384 | 11 026 | 14.13 % | 10.60 % | 6.78 % | 239 |
| split | pie | 274 382 | 11 119 | 15.08 % | 11.32 % | 7.05 % | 211 |
| split | red | 274 382 | 10 510 | 13.41 % | 9.72 % | 6.19 % | 258 |

The player's `late_us` counts far fewer late frames (its schedule is a 600 ms startup
buffer that slides later after every stall), which is why GT-H is computed from
send_us / recv_us as the spec requires.

## 9 Scenario design (suite v3)

Kept with the code of the suite (scripts/v3_suite.py, spec copy reports/v3-suite/spec.md,
hand-over reports/v3-suite/README.md). Status 2026-11-14: implemented, nothing run yet.

**Why.** Before v3 every bottleneck carried only our video (load ~0.65, video share ~1),
every hierarchy level was a scaled copy of the others, congestion came almost only from
capacity drops, and AQM limits were the pfifo packet count with `ecn` on. v3 makes the
share of the synchronized stream in a link (s) and the link's calm load (U) explicit.

**Sizing rule.** For each bottleneck egress e separately, with D_e = sum of the client
rates behind e x 1.03 (wire): C_e = D_e / (s U), BG_e = D_e (1 - s) / s (independent of U).
Default s = 0.30, U = 0.70. Levels: T-BASE s in {0.10, 0.30, 0.65} x U in {0.50, 0.70,
0.85} (s 0.10 / U 0.50 left out: 103 Mb/s), plus the legacy cell (17.5 Mb/s, no
background, pfifo 100 packets). Hierarchies at the default point; T-SPLIT4 also at s 0.65.
Constraints checked by the planner: shaped links <= 100 Mb/s, an instrumented flow <= 15 %
of every bottleneck it crosses (25 % for the s 0.65 and legacy cells), <= 300 Mb/s through
all router egresses; the flow-share rule does not apply to a client's private access link.
Three cells the spec lists break a constraint and are kept (decision 2026-11-14): legacy
(29 %), s 0.65 / U 0.85 (25.1 %), M11 1000/2500/5000/12000 (27 %). Reference keyframe queueing peak ~0.121 s U seconds
(25 ms at the default point; not a criterion).

**Background.** Always on, at every shaped bottleneck, from its own source (attached to
the router that owns the egress) to its own sink (the node right after it), 1000 Mb/s
links, crossing that egress and nothing below it. Default BG-CBR: n = max(4, round(BG_e /
2.5 Mb/s)) UDP flows, each its own socket (distinct source port, so distinct 5-tuple) and
its own Poisson departure process (exponential gaps, own RNG stream) of 1200 B payloads,
equal mean rate: statistically independent of the video's frame and GOP clock (qtraffic
`--process=poisson`, qvideo/src/Departures.h; unit tests check per-flow rates, CV 1 and
KS against the exponential law, cross-flow independence and no 1 Hz / 30 Hz line).
BG-BURSTY: the existing PPBP generator (Hurst 0.8, burst 2 Mb/s, mean burst 0.5 s) at
the same mean. BG-MIX: 50 % rate-limited TCP (half CUBIC, half BBR, application-paced),
30 % on-off TCP (2 s at 2x the mean, 2 s idle, random phase), 20 % BG-CBR; no greedy flow.
Rates are sized as router (tc) rates; UDP payload = rate x 1200 / 1242 (IP + UDP +
Ethernet header as counted by tc), TCP goodput = rate x 1448 / 1514.

**Stimuli.** Congestion by load increase: surge (extra Poisson flows of 2.5 Mb/s on the
target's own background path, total (u - U) C_e, step on / off), ramp (same, linear over
5 s in 0.5 s steps, held 5 s), tcp (2 or 4 greedy iperf3 flows, CUBIC or BBR), join (an
aggregate synchronized-video source: the 5000 kb/s rendition's frame-size pattern, same
seed, phase 0, scaled per GOP, 15 s up / 15 s hold / 10 s down; each frame spread over the
measured emission time of a real 5000 kb/s client in calm: keyframe 5.85 ms, P-frame
1.16 ms, medians over 8 client-runs; the emission time follows the connection's BBR pacing
state, ~5 ms or ~35-50 ms per keyframe, to be re-measured on the v3 smoke runs). Capacity drops only on access links (A-MIXED) and in
microbenchmark M2. Grids u {1.05, 1.15, 1.3} x d {2, 5, 10} s; warm-up 15 s, gaps
U(10, 15) s, tail 10 s. Under fq_codel and cake a surge constrains only flows above their
fair share; that is expected and not corrected.

**Publisher link.** pub -> first router is 1000 Mb/s (5 ms each way) in every v3 topology,
and GT-Q traces the publisher's egress, so a queue of the synchronized keyframes at the
sender's own link would be visible. In the earlier runs (100 Mb/s) keyframes left at each
connection's BBR pacing rate (2-14 Mb/s; 5000 kb/s keyframes 44-51 ms), not at the link rate;
only sub-ctrl paced near 100 Mb/s.

**Delays.** Narrow set by default: one-way access delays 5 / 7.5 / 12.5 / 20 ms cycling
through a leaf's clients (base RTTs 20 / 25 / 35 / 50 ms with the 5 ms feed); wide set
5 / 15 / 30 / 45 ms and x0.5 / x4 only in microbenchmark M4.

**AQMs.** pfifo limit = 50 ms of the egress's capacity (min 20 packets; M1: 100 and
300 ms; M4: the variant's largest base RTT); codel, pie, fq_codel with the kernel's
default limits and no `ecn`; red thresholds from the egress's own capacity (15 / 45 ms,
limit 150 ms, no `ecn`); cake as before (`cake unlimited besteffort`). Every router
egress gets its own setting; source / sink egresses and unshaped links have no AQM.
Checks before the suite: no existing run folder has a non-zero ECN mark (267 runs);
mvfst leaves ECT off (enableEcnOnEgress false), so the video was never markable.

**Host.** TSO / GSO / GRO and UDP GSO off on every veth, recorded per run in
offloads.csv. CPU governor set to performance (by hand). One run at a time.

**Deviations from the spec (all in reports/v3-suite/README.md).** Background flows are
one qtraffic process per egress with one socket per flow; a ramp is a staircase of
overlapping steps; BG-MIX TCP is qtraffic's own TCP mode (application-paced writes), not
iperf3; the inter-dequeue check uses the stored p99 (one-sided); the phase-lock check
needs a number for "a peak above its neighbours" (10 x the median within 0.5 Hz, flagged);
the held-out regeneration uses seeds 101-105.

**GT-Q tracer and its health gate (v3 smoke tests, 2026-11-14).**
- The enqueue time has always come from `net_dev_queue`, which fires for every packet just
  before the root qdisc's enqueue. `qdisc_enqueue` is not used: it fires only when the enqueue
  returns NET_XMIT_SUCCESS, so it misses a packet that fq_codel accepts while dropping from the
  fattest flow (NET_XMIT_CN).
- The first smoke used classic tracepoints. Those share one per-CPU recursion guard, so an
  event arriving while any BPF program ran on the CPU was skipped. The cost was ~2 x 10^-5
  unmatched packets per egress, worse with more tracers. The second smoke used raw tracepoints
  (one guard per program): 0 unmatched packets and 0 recursion misses on every egress.
- Probe points unchanged: on router->switch, the empty-queue sojourn floor is 0.4 us in both
  smokes. Calm load, video share and keyframe peaks moved by at most 0.002 / 0.002 / 1.1 ms.
- Gate on bottleneck targets:
  - unmatched packets <= max(3, 5e-5 x dequeues) per kind, <= 2 per 200 ms;
  - backlogged inter-dequeue gaps within max(10 % of the previous packet's serialization
    time, 15 us) for >= 99 %;
  - bytes per backlogged 20 ms window within +-5 % of C x 20 ms for >= 99 %.
- Why the 15 us floor: dequeue timing has a rate-independent jitter of about +-4.5 us (p1 / p99,
  the same on 24.5, 49 and 98 Mb/s links; reports/v3-suite/smoke2/gap-jitter.md).
  - 15 us is about three times that jitter.
  - It is far below one packet time on the fastest link (101-122 us).
  - It is below every window we measure with.
  - Without the floor, the 98.1 Mb/s root fails at 98.96 % because +-10 % is only +-10 us
    there. With it, the root reaches 99.79 %, and its 20 ms windows are all within +-5 %.

**Stimulus intensity u and the video's reaction (campaign gate, 2026-11-14).**
- u is defined as the stimulus intensity with the video at its calm rate. A surge cell u offers
  background + surge = U(1 - s) + (u - U) of C on its target. That is what the gate checks
  (within +-0.05; measured at the target's ingress from the GT-Q trace: -0.009 to +0.014 in the
  gate runs).
- The video is not part of u. Its reaction is an outcome, written per window (v3-stimuli.csv:
  nominal u, measured non-video, video and total load, video relative to its calm rate). Later
  tables show the measured values next to the nominal u; run names keep the nominal u.
- With non-responsive background (constant-rate Poisson UDP) the video's own sending falls under
  overload. In the gate runs (T-BASE, default point) the video fell to 0.43-0.66 of its calm
  rate at u = 1.3, roughly half. The realised total load was therefore 1.18-1.24 instead of 1.3.
  At u = 1.05 the video stayed at 0.81-1.13 of calm.
- Non-responsive background makes overload harsher for the video than responsive background
  would. The video is the only sender that backs off, so it gives up all the capacity the surge
  takes.
- Comparison blocks: C5 (TCP surges: the stimulus itself responds) and M3 (BG-BURSTY, BG-MIX:
  responsive TCP in the background). The post-campaign table `video-reaction.md`
  (scripts/v3_stimuli.py) shows the video's load relative to calm during stimuli, by nominal u
  (C5 by TCP cell), for C2 vs C5 vs M3, per AQM, reps side by side.

**Per-flow-queue AQMs (fq_codel, cake): grouping truth (decision 2026-11-15, REPLACED the same day by the "same link" decision below; kept for the record).** Taken after
the fq_codel grouping results had been seen (Part 4 of reports/v3-score/REPORT.md and
reports/v3-grouping-diag/REPORT.md Q4).
- The method detects a *shared queue*. Under fq_codel and cake each instrumented client is
  pinned to its own sub-queue, so the two parts are scored differently:
  - Detector: scored per client against that client's own sub-queue (GT-Q per flow). This was
    already the case; nothing changes.
  - Grouping: no two instrumented clients behind a per-flow-queue egress share a queue there,
    so the correct output among them is *no group*. These cells are a negative control, not a
    grouping test. Every pair a method declares as sharing is a false grouping.
  - Topology exception: a client behind a per-flow-queue egress still shares an ordinary queue
    upstream when one exists. In v3 every egress of a run has the same AQM except mixab
    (M8: r1 -> r2 'up' pfifo, r2 -> switch-a pfifo, r2 -> switch-b fq_codel). There the true
    sets are 'up' (all 8 clients) and 'a'; the b clients form no group of their own.
- Limitation, in one sentence: with per-flow queueing, flows share the link but not the queue.
  The reading "clients competing for the same link capacity form a group" is not a goal of the
  method. The numbers produced under that per-flow co-constraint truth stay as a side table
  (reports/v3-grouping-diag/REPORT.md Q4) and are not extended.
- Testbed check (reports/step8-2026-11-15/fq-control.md Ea).
  - Configuration: fq_codel runs with the kernel defaults, `flows 1024`, target 5 ms,
    interval 100 ms, limit 10240 packets.
  - Pinning: each instrumented client is pinned by destination address. A clsact egress
    flower filter sets skb->priority = 20:<0x301 + i>, and fq_codel takes the minor number
    minus one as the flow index (768 + i).
  - Unpinned traffic (background, sub-ctrl) keeps fq_codel's hash, reciprocal_scale(skb->hash,
    1024), so it can land on a pinned index.
  - Check on all 20 fq_codel / mixab runs with a valid GT-Q (M8 r1: no GT-Q):
    - no egress has two instrumented clients on one sub-queue index;
    - the only other 5-tuples in a client's sub-queue are the client's own other connections
      (529 tuple-egress cases) and other traffic (34 cases: the known ~1 % background leak
      into pinned classes, FLAG, to be fixed before the next campaign).
  - cake runs (C2 only) have no grouping output; their pinning (a flower classid on the qdisc)
    was checked by configuration only.
- Collisions in a real deployment, fq_codel default 1024 queues, flows hashed independently
  and uniformly:

  | concurrent flows | P(at least two flows share a queue) | P(a given flow shares) | expected colliding pairs |
  |---|---|---|---|
  | 2 | 0.001 (1/1024) | 0.001 | 0.001 |
  | 10 | 0.043 | 0.009 | 0.04 |
  | 30 | 0.35 | 0.028 | 0.42 |
  | 100 | 0.993 | 0.092 | 4.8 |
  | 1000 | 1.000 | 0.62 | 488 |

  The formulas:
  - P(at least two share) = 1 − ∏_{i<n}(1 − i/1024);
  - P(a given flow shares) = 1 − (1 − 1/1024)^(n−1);
  - expected colliding pairs = C(n, 2)/1024.

  So "no shared queue" holds for links with few flows and only approximately for links with
  very many. cake's 8-way set-associative hash avoids most of these collisions until its
  1024 queues fill up; this was not measured.


**Grouping freeze and scoring decisions (2026-11-15).** SETS v1 is frozen (grouping/FREEZE-sets-v1.md);
ECG v1.2 and h3 stay as comparison methods, frozen, with no further development.
- Scope. The goal is each client's *leaf* group. Nested upstream groups (mid / up / root) are out of scope:
  a limitation and future work, reported as a side table only. Upstream events must not damage leaf groups;
  this is measured at the event closes right after an upstream event, against all other closes.
- "Final precision" (the last snapshot of a run) is no longer a metric. Every grouping score is averaged over
  all event closes of the run.
- Per-flow-queue AQMs (fq_codel, cake): grouping is scored against the "same link" truth. The clients that are
  constrained together at the same egress (their own sub-queues, during that egress's stimuli) form the group;
  clients that are never constrained there are correct when left out. Decided after the fq_codel grouping
  results had been seen (Part 4 of reports/v3-score/REPORT.md, reports/v3-grouping-diag/ Q4, Step 8-10 E).
  It replaces the earlier decision of the same day ("same queue": per-flow-queue cells as a negative control,
  every group false). The detector is still scored per client against that client's own sub-queue.
- Scenario parameters for future campaigns: default load U = 0.50; U = 0.70 is the extreme point; U = 0.85 is
  removed. Default stream share s = 0.30; the upper value is s = 0.50. The existing s = 0.65 runs are kept as a
  stress row. All existing v3 event runs are at U = 0.70 and are labelled extreme-load runs from now on.
- Testbed fix before any new campaign: under fq_codel about 1 % of the unpinned background landed in a pinned
  client's sub-queue (fq_codel's own hash over all 1024 sub-queues). Fixed in quiclab/orchestrator/shaping.py:
  a catch-all flow-hash filter on the qdisc puts every unpinned packet on sub-queues 0-767, below the pinned
  ids (768 + i). Verification: scripts/tc_fq_pin_leak_probe.sh (netns) and one short run per topology checked
  with scripts/fq_pin_check.py. Existing v3 fq_codel runs stay flagged. Probe result (2026-11-15): with the
  fix, 0 of 70 class dumps show unpinned traffic in a pinned client class (PASS); without it, 40 of 70 (LEAK).
  Short runs per topology (T-BASE, H-HIER, H-DEPTH, A-MIXED, mixab; .runs/2026-11-15_2238_pinfix):
  all OK, the catch-all on every fq_codel egress, unpinned backlog only on classes <= 20:300. Fix verified.
- Open notes (not done now): (1) a C++ SETS engine, to be implemented later. (2) The FlowBot block tests the
  known weak point of the set method: congestion that lasts 30 s without a break gives one observation, so no
  group at k = 2. Report, per method, when it first groups within the first congestion and what happens after
  2, 3 and 4 repetitions; the curve method (h3) may lead there; decide only after seeing the result.
