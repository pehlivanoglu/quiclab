# Smoke 1 (.runs/2026-11-14_1730_v3-smoke): FAIL on check 4 only

Tables: [health.md](health.md) (per traced egress; script [health_table.py](health_table.py)),
[smoke-report.md](smoke-report.md) (copy of the run's report).

## What passed

All 7 runs pass checks 1, 2, 3 and 6, and the S-BURST run passes check 5.
- Check 1: calm load 0.707-0.713 against 0.70, video share 0.307-0.310 against 0.30, on all 17
  bottleneck egresses.
- Check 2: no ECN mark, and no AQM leaf installed with `ecn`.
- Check 3: no oversize skb; offloads off.
- Check 6: no phase lock.
- Health of the shaped bottleneck egresses: every one passes service timing (backlogged gaps
  within +-10 %: 99.00-99.97 %; 20 ms windows within +-5 %: 100 %) and has lost events 0. CPU idle
  >= 0.80 everywhere.

## Why check 4 fails

**(1) Service timing (4b) fails only on links that are not bottlenecks.** These are
pub -> first router (1000 Mb/s: one packet = 10 us, finer than dequeue scheduling; 58-87 % of
gaps within +-10 %), the sub-ctrl egress (50 Mb/s, carrying 2.5 Mb/s; 76-93 %), the T-ACCESS
access egresses that are rarely backlogged (ra 48 %), and T-UNEVEN's unshaped r1 -> r2
(1000 Mb/s, 58 %). On those links "backlogged" means a short batch, and the ideal is microseconds.

**(2) Accounting (4a): tracepoint events are missed while another BPF program runs on the CPU.**
- `recursion_misses` (read at stop) is the same for every tracer of a run, and the unmatched
  packets are ~0.3 of it in every run:

  | run | misses | unmatched |
  |---|---|---|
  | base | 38 | 12 |
  | split4 | 223 | 64 |
  | tree16 | 667 | 190 |
  | uneven | 599 | 178 |
  | access | 158 | 66 |
  | rev | 90 | 35 |
  | sburst | 102 | 31 |

  Every tracer's programs fire for every packet in the kernel, so all of them count the same
  nested events. Only the events of their own netns are unmatched packets.
- The publisher egress shows only unmatched **enqueues** (orphans, spread over the run), never
  unmatched dequeues: 7-65 per run, 0.8-3.6 x 10^-4 of dequeues. Its enqueues run in process
  context (mvfst's sendmsg); its dequeues run in softirq (netem / htb timer) and can arrive while
  the enqueue program runs. Classic tracepoints share one per-CPU guard (`bpf_prog_active`), so
  the nested dequeue program is skipped.
- 60 s runs have small denominators. On the sub-ctrl and access egresses (~17 000 dequeues), a
  single unmatched packet is 5.9 x 10^-5, above 5e-5.

## Options (yours to decide; nothing changed)

1. Tracer on raw tracepoints (`rawtracepoint:net_dev_queue / qdisc_dequeue / kfree_skb`): their
   recursion guard is per program, so an enqueue program and a dequeue program no longer block
   each other. Checked: bpftrace 0.20 in the image loads the three raw tracepoints with BTF
   casts. It is a change to router_trace.bt only (the arguments become arg0..arg3), plus a
   re-run of the smoke to see how many misses remain.
2. One bpftrace for all traced nodes (netns filter per node) instead of one per node: the
   number of programs per packet goes from N to 1. More code (one tracer, several netns),
   independent of 1.
3. Scope of 4b: apply the service-timing rule to the shaped bottleneck egresses of the plan
   only, and report the other traced egresses as information.
4. Scope of the accounting rule on short runs: as written it fails a 2.5 Mb/s egress on a single
   missed event in a 60 s run.

## Other numbers you asked for (not gating)

- Emission, re-measured with pub -> first router at 1000 Mb/s: every client is in the fast mode
  (pacing 13-154 Mb/s). Keyframes 2.4-7.3 ms; the 5000 kb/s clients' keyframes 4.8-6.2 ms;
  P-frames 1.1-1.2 ms (0 ms where the frame leaves in one batch). ASV medians on the smoke:
  keyframe 4.82-5.96 ms, P 1.16 ms (against 5.85 / 1.16 in the code). ASV_KEY_MS / ASV_P_MS are
  unchanged.
- Keyframe queueing peak (p50, 200 ms after each keyframe) against 0.121 s U = 25.4 ms:
  - single bottlenecks: 19.6-23.4 ms;
  - hierarchies: the peak forms at the top level and gets smaller below it: split up 22.1 /
    leaves 11-12 ms; tree16 root 21.8 / X, Y 11-12 / leaves 6-8 ms. The upper queue spreads
    the keyframes before they reach the lower ones.

## Decisions of 2026-11-14 (implemented; smoke 2 pending)

1. **Tracer on raw tracepoints.** `quiclab/router_trace.bt` uses `rawtracepoint:net_dev_queue`,
   `qdisc_dequeue` and `kfree_skb` (arguments as TP_PROTO, checked in the container on a veth:
   packets = 1, skb lengths and both ifindex paths agree, pfifo drop reason 64 as in the old
   classic-tracepoint runs, 1992 traced drops = the qdisc's own count). The programs are of type
   17 (raw tracepoint). The single-bpftrace change was not made.
2. **4b** gates only the run's bottleneck targets: the plan's shaped bottlenecks, plus access
   egresses with private windows. It needs >= 1000 backlogged gaps, otherwise "not evaluated".
3. **4a** on targets: unmatched of each kind <= max(3, 5e-5 x dequeues), <= 2 per 200 ms, lost
   events 0. Other traced egresses (publisher, sub-ctrl, ...) are reported only. The health file
   keeps recursion_misses, both unmatched counts and `unmatched_allowed`.
4. ASV_KEY_MS / ASV_P_MS stay 5.85 / 1.16.
5. The smoke report gets a before / after table per topology ([baseline.json](baseline.json),
   from [baseline.py](baseline.py)).

Smoke 1 under these rules (classic tracepoints): check 4 passes on base, split4, rev and the
S-BURST run. It fails on tree16 (targets r0->r1, r0->r2, r2->switch-d, rr->r0: 4a; rr->r0 also
4b, 99.00 %), uneven (r2->switch-a, r2->switch-b: 4a) and access (router->switch: 4a, 19
unmatched dequeues).
