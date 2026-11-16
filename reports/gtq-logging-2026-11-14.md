# GT-Q / GT-H: final report (2026-11-14)

Nothing is committed. No testbed run, smoke run or privileged container was started:
a tracer probe in a privileged container was attempted and denied by the permission
system, so it was not retried.

## 1. What is done, and what is untested

**Never run (they need a real run):**
- **The router tracer.** `quiclab/router_trace.bt` was not loaded once. bpftrace needs
  root even to compile, so syntax, verifier acceptance, tracepoint field names on
  kernel 7.0, and whether "Attaching" goes to the log or the output file are all
  unverified.
- **The sender logging.** `qvideo-server --pkt_log` builds and the flag is present
  (`--helpfull`), but it has never written a file.
- **The orchestrator start/stop path.** Starting bpftrace with mnexec in the router
  netns, mounting tracefs in the container, and the SIGINT stop have never run.

**Built and tested offline:**

| part | where | tested how |
|---|---|---|
| flag `gtq_logging` (default on) + env override | `quiclab/config/schema.py`, `quiclab/router_trace.py`, `quiclab/cli.py` | unit |
| bpftrace in the image | `docker/Dockerfile` (image rebuilt; the old one is tagged `quiclab:pre-gtq`) | build only |
| choice of traced egresses | `mininet_backend.gtq_trace_interfaces` | all 192 old runs (decision 1 lists what is traced) |
| tracer start/stop, never breaks a run | `mininet_backend._start_gtq_tracers / _stop_gtq_tracers / _gtq_health` | code review only (the failure paths are try/except) |
| raw → `router-trace/<iface>-packets.csv`, the traps | `router_trace.parse_raw / packets_table / finalize` | synthetic stream containing every trap |
| per-run health check | `router_trace.health` → `<run>/gtq-health.csv` + a log line | synthetic run dirs |
| sender packet log | `qvideo/src/Server.cpp` `PacketLog` | compiled only |
| router↔QUIC match, first ACK, t_obs (b) and (a) | `router_trace.match_flow / first_ack_us`, `gtq.Obs` | unit |
| GT-Q labeler, GT-H | `scripts/gtq.py` | unit + frame side on 192 real runs |
| detector vs GT-Q/GT-H (new files only) | `scripts/gtq_score.py` | unit |
| automatic post-run hook | `scripts/det_matrix.py` (separate try block after GT1/2/3) | import only |
| campaign health summary | `gtq.py summary` → `<campaign>/gtq-health-summary.{csv,md}` | unit (via score) |
| CoDel and BDP queue limits, available but off | `codel` already exists; new `queue_limit_bdp` on `RouterQueue` | unit (146 packets = 1 BDP on base) |
| probe for you | `scripts/gtq_tracer_probe.sh {pfifo,fq_codel,codel,pie,red}` | `bash -n` only |

How the four traps from my audit are handled:
- **Dropped packets:** enqueue time comes from `net:net_dev_queue`, not
  `qdisc:qdisc_enqueue`. The latter fires only on success, so it would miss a
  packet fq_codel accepts while dropping from the same flow.
- **Batched dequeue:** the tracer walks `skb->next` for `packets` entries (at most 16;
  anything beyond counts as truncated).
- **Requeue:** the later dequeue is kept as a separate record, and offline the last
  dequeue time wins.
- **fq_codel drop attribution and skb address reuse:** a drop row is the freed skb
  itself, so fq_codel's drop from the fattest flow is attributed to that flow. Address
  reuse is safe because every enqueue overwrites the entry for that address.

## 2. Turning the flag off, and where the health file is

- **Whole campaign:** `QUICLAB_GTQ_LOGGING=0 python3 scripts/det_matrix.py ...` (also
  works with `grouping_campaign.py` and `python -m quiclab run`; the variable is
  passed into the container).
- **One topology:** put `gtq_logging: false` at the top level of the YAML.
- **Health file:** `<run>/gtq-health.csv` (key, value), plus `<run>/logs/gtq-health.log`
  and a `*** gtq health: ...` line in the run's stdout.
- **Campaign summary:** `<campaign>/gtq-health-summary.md` lists the invalid runs and
  the worst CPU idle.
- **Full description:** `docs/gtq-logging.md`.

A run where the tracer fails to start, dies, loses events or fails the count identity
continues normally. GT1/GT2/GT3 are produced as usual and the run is marked
`gt_q_invalid = 1`. Such a run gets only `truth/gtq-status.csv`, no GT-Q.

## 3. Unit tests

Full suite: **844 passed, 36 skipped, 2 xfailed** (the xfails were there before). 51 of
these tests are new:

- `tests/unit/test_gtq.py` (24): spec section 5 rows on synthetic logs, plus netem delay subtraction —
  - idle link at 15/30/60 fps → 0 episodes
  - pfifo with a saturating bulk flow → 1 long episode
  - queue held at ~5 ms with drops → 1 episode
  - drop-only episodes and their W merge
  - merge gaps of 0.5 W and 1.5 W
  - gray zone: short busy run and below-2τ
  - presence check
  - onset at the start of the busy period
  - capacity drop
  - fq sub-queue index
  - fq_codel sparse video next to a busy sub-queue → 0 episodes
  - fq_codel video over its share → 1 episode
  - fq hash collision → included and flagged
  - shared queue gives both videos an episode, with W = 50 ms and τ = 1.2 ms
  - reverse path only → tagged reverse, never harmful
  - GT-H harm instant, deadline-miss censoring
  - invalid run → status file only
- `tests/unit/test_router_trace.py` (25): parsing, every trap, identity pass and fail,
  late nohit and oversize, matching with loss before the router, first ACK, flag/env,
  inter-dequeue ratio, health valid / lost events / tracer failed / off, egress
  selection, BDP limit.
- `tests/unit/test_gtq_score.py` (2): TP/FP/ignored, W merge, latency, censoring,
  precision/recall.

Tests that failed along the way, all fixed:

- **One labeler bug.** The spec's rule ends a busy run at "t_deq of the first non-busy
  packet". Read literally, the run stretches across the idle gap until the next
  frame arrives. Changed to the time the queue drained. This is deviation 1 in the
  paper notes.
- **One bug in my identity check:** nohit rows are a separate kind and must not be
  added to the dequeue count.
- **Three test-construction errors:**
  - wrong loopback IPs in the fixture;
  - physically impossible sojourns in the collision test (the colliding flow waited
    20 ms in a sub-queue where the video waited 0.5 ms);
  - a lost frame placed inside the episode collar of the GT-H test.
- **One loosened tolerance:** the capacity-drop onset came 100.1 ms after the stimulus
  with W = 100 ms. The spec says "about W", so the test now allows < 1.5 W.

## 4. GT1/GT2/GT3 are unchanged

I recomputed GT1/GT2/GT3 for all 192 runs of `.runs/old/ip4/2026-11-08_det-*` before
any code change and again after all changes, into a symlink farm in the scratchpad, so
the originals were not touched.

**All 1168 truth files are byte-identical before vs after, and identical to the files
on disk.** None of the GT1/GT2/GT3 code, file names or tables were changed.

## 5. Decisions I made for you, and open questions

Decisions:

1. **Which egresses are traced:** router egresses on a subscriber's forward path with
   HTB and a netem that only delays (no loss, no jitter). The labeler subtracts the
   netem delay in force at each packet's enqueue.
   - My first version allowed no netem at all. Checking the access campaign showed
     that this skipped its real bottlenecks (`ra…rd → sub-*` have netem delay), so I
     changed the rule.
   - On the 2026-11-08 topologies this traces: base `router-eth1` and `router-eth3`
     (→ sub-ctrl); access additionally `ra-eth1 … rd-eth1`; split `r1-eth1`,
     `r1-eth2`, `r2-eth1`, `r2-eth2`.
   - Egresses towards the publisher carry no subscriber's forward traffic and are not
     traced, so **reverse-path GT-Q episodes cannot occur in today's topologies**. The
     labeler supports them (unit test).
2. **Sender-match trust threshold:** 95 % of a flow's router packets. Below that, the
   flow uses the config fallback (a), marked `config (match rate low)`.
3. **t_stim:** the latest scripted stimulus in [t0 − 3W, t0 + W].
4. **AQMs the labeler can't model exactly:** for cake, only the flow's own packets are
   used; dualpi2 is treated as one shared queue; if AQM events change the AQM during a
   run, the t=0 AQM is used and the run is flagged.
5. **Never-received frames:** counted as misses only if t_gen + B falls before the end
   of the client log; otherwise censored.
6. **Scorer:** the detectors emit alarm start times, not a score, so there is no θ
   sweep. There is one operating point per detector, alarms are merged within W, and
   missed episodes are reported as censored counts (no Kaplan-Meier plot yet). The
   output is only the new file `<campaign>/gtq-detector-table.{csv,md}`.
7. **Host CPU sampling** (1 Hz from /proc/stat) also runs with the flag off, so on/off
   runs can be compared.
8. **`grouping_campaign.py` is not hooked**, because it has your uncommitted changes.
   Its runs still get the tracer and the health file. GT-Q/GT-H for them:
   `python3 scripts/gtq.py score <runs>`, then `gtq_score.py <campaign>`.

Projected disk use: about **50 MB per run** (base ~40, access ~100 because each video
packet is traced at two routers, split ~150), so about **10 GB for 200 runs**. Today a run is about 83 MB on average. This is an estimate from
the packet counts in the existing runs, not a measurement. 259 GB are free.

GT-H frame side on the existing campaign (no router trace needed): across the 992
run×client logs, the client and sender `send_us` match for every received frame, and
misses decrease as the budget grows. Deadline-miss rates at 600 ms:

| | fq_codel | pfifo | PIE | RED |
|---|---|---|---|---|
| base | 6.5 % | 10.8 % | 10.3 % | 9.6 % |
| split | 4.2 % | 10.6 % | 11.3 % | 9.7 % |
| access | about 2.8 % (all four AQMs) | | | |

The full table is in the paper notes. The player's `late_us` counts far fewer late
frames, which confirms that `late_us` must not be used for GT-H.

Open questions:

1. **First real run:** please run the probe first. If it fails, set
   `QUICLAB_GTQ_LOGGING=0` before the night campaign.

       docker run --rm --privileged -v "$PWD:$PWD" -w "$PWD" quiclab:latest bash scripts/gtq_tracer_probe.sh fq_codel

   Then run one short real run and check `gtq-health.csv`. Expected first-time
   failures if any: bpftrace syntax, tracefs mount, the "Attaching" detection. Any of
   these makes the run `gt_q_invalid` but does not change the run itself.
2. **Load check:** the on/off comparison from your earlier message (CPU idle,
   inter-dequeue time, throughput, OWD, detector scores, old GT episode counts) was not
   done, because no runs were allowed. The default is ON as you asked; the health file
   collects what that comparison needs.
3. **Parameter freeze:** GT-Q parameters, the θ grid and the operating-θ rule are not
   frozen. Freeze them after the first campaign with the tracer, and record the hash in
   `docs/paper-notes-ground-truth.md`.
4. **Reverse-path queues:** to test them, a topology would need a reverse egress with
   HTB and no netem. Do you want one?
5. **Netem jitter or loss on a bottleneck:** egresses with netem loss or jitter are
   never traced (none of the 2026-11-08 bottlenecks have them; `randloss` puts its
   loss on pub→router). If a future scenario puts jitter on a bottleneck, it gets no
   GT-Q for that egress.

Paper notes: `docs/paper-notes-ground-truth.md` contains the 8.1 seed, the measurement
method, the t_obs method, deviations 1-10, the disclosure facts and the GT-H table.

## Addendum: first probe run (user, 2026-11-14)

`gtq_tracer_probe.sh fq_codel` failed: `tracepoint not found: net:net_dev_queue`. The
kernel has the tracepoint. bpftrace ran under `ip netns exec`, which remounts `/sys` in
a new mount namespace, so tracefs was not visible there.

Fix:
- bpftrace now runs in the container's own namespaces, both in the probe and in the
  orchestrator (`subprocess.Popen` instead of `node.popen`). The script already
  filters by the router's netns inode.
- Switched to `BPFTRACE_MAX_MAP_KEYS` (the old variable name is deprecated).
- An interface that traced zero packets now marks the run `gt_q_invalid`: in the failed
  probe the empty trace had passed the count identity.

The probe needs to be run again.

## Addendum 2: first real run (`.runs/2026-11-14_0228_try-sync/G0/grp-calm065-pfifo-r1`)

What worked:
- tracer started and stopped cleanly; 0 lost events; sender logs written;
- CPU idle min 0.96; 21 MB of new logs for a 120 s run;
- router-eth3 (sub-ctrl, 20 ms netem) identity holds.

The run was marked `gt_q_invalid`:
- router-eth1 had 1 dequeue row more than the kernel counter.
- Cause: 2 of 146 334 dequeue events had no enqueue record and picked up a stale entry
  from the previous packet at the same skb address. The converter treated them as
  requeues. One was folded into an old packet (fake 2.8 s sojourn); the other became an
  extra dequeue row.

Fixes:
- A later dequeue counts as a requeue only within 100 ms of the same packet's first
  dequeue on the same interface. Otherwise it becomes a nohit row (enqueue time unknown).
- The identity check compares the kernel counters with the raw rows, before folding.
- Late nohit rows up to 0.01 % of dequeues are reported, not fatal.

Sender match rate:
- It was 0.936 for sub-a because of 871 pure ACK packets of 90 B. mvfst reports only
  ack-eliciting packets to the sender log, so these can never match.
- The match rate is now computed over router packets ≥ 200 B: 0.9988-0.9998 for every
  flow.

GT-Q / GT-H on this run (computed in memory, no files written):
- **router→switch:** 120 GT-Q episodes per flow. That is one per second, from the
  synchronized keyframes: all four clients' keyframes hit the queue at the same time and
  build a 130-160 ms, 40-58 ms deep standing queue, with pfifo drops. W = 100 ms (largest
  base RTT), so these qualify as episodes. GT1 (fixed INTERVAL 150 ms) finds 30.
- **GT-H:** 0 at every budget (no deadline misses).
- **t_obs:** taken from ACKs for all 480 episodes; ACK minus config (b − a) is p50 12 ms,
  p90 20 ms; d_obs p50 65 ms.
- **sub-ctrl:** 0 episodes (the netem delay is subtracted correctly).
- **Gray:** 76 short busy runs, 4 below 2τ.
