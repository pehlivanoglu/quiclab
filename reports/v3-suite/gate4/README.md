# Gate check 4: diagnosis on the existing GT-Q runs (2026-11-14)

No new runs. Data: every run with a GT-Q trace (35 runs, 166 traced egresses, night campaign
2026-11-14 sync + stag). Scripts and raw outputs here:
[accounting.py](accounting.py) -> [accounting.md](accounting.md),
[service.py](service.py) -> [service.md](service.md), [service.json](service.json).

**Outcome: stop (spec 1c).** (a) shows unmatched packets away from the trace edges, so the
new accounting rule fails on every run; I did not change the gate. (b) shows no heavy tail and
the 20 ms rule holds; the old p99 was an artifact of the statistic's definition.

## (a) Packet accounting

Two kinds of unmatched packets:
- **dequeues with no enqueue record** (`nohit` rows; all of them are "requeues" more than
  100 ms after the address's previous dequeue, which router_trace reclassifies; the kernel
  side's own `n_nohit` is 0 everywhere): **4974**, of which **4 in the first / last 1 s** of
  the trace and **4970 elsewhere**. Position in the trace by deciles of trace time:
  521, 486, 513, 510, 530, 450, 459, 528, 480, 497. Flat: they are spread uniformly in time.
- **enqueues never dequeued or dropped** (residual = n_enq - n_deq - n_drop): **4897** in total
  (0 to 130 per egress, non-zero on 157 of 166 egresses). Their enqueue records are not written
  to the CSV (only dequeue / drop rows are), so their times are not recoverable from the files.
  Packets still queued at stop explain at most a few of them. The last queue sample (5 ms CSV,
  taken 0.6 to 2 s before the tracer stops, after the scenario's end) shows 0 packets on 143
  egresses, 1 to 3 on 10 (residuals 19 to 102), 20 on one (C1 burstlongsplit pfifo r2 r2-eth1,
  residual 16), and no sample on 12. That bound is weak, because the stop came later.

Both counts are ~1 per 2 x 10^5 dequeues. Across egresses (residual + nohit) correlates with
the number of dequeues (r = 0.86), not with the drop share (r = -0.22). The two kinds come in
similar numbers.

Inferred mechanism (not verified): the tracer misses single tracepoint events at random, both
enqueues (the packet then shows up as an unmatched dequeue) and dequeues / drops (the packet
stays an unmatched enqueue). A kernel BPF program that would run while another one is already
running on the same CPU is skipped and counted only in that program's `recursion_misses`
counter. bpftrace's "lost events" counts only perf ring-buffer losses, which are 0 here. That
fits a uniform, rate-proportional pattern. Check: read `recursion_misses` (`bpftool prog show`)
at the tracer's stop. bpftool is not in the image, so adding that is your call.

## (b) Service timing

Backlogged gap: packet i+1 was enqueued before packet i was dequeued.
router_trace.interdequeue_ratio today divides the gap by the serialization time of packet
**i+1**. HTB releases i+1 once it has paid the tokens of packet **i**, so the ideal gap is
8 len[i] / C. With len[i+1], a small packet (ACK, frame tail) after a full one gives
1242 / 42 ~ 30. That is the observed maximum (30.4), and it is where the p99 of 6.85 comes from.

| run | egress | C Mb/s | backlogged gaps | gap / ideal(len[i]) p50 / p99 / p99.9 / max | within +-10 % | same with len[i+1]: p99, within +-10 % | 20 ms windows within +-5 % (p1 / p50 / p99) |
|---|---|---|---|---|---|---|---|
| G0 randloss pfifo r1 | router->switch | 17.5 | 236 495 | 1.000 / 1.003 / 1.009 / 1.32 | 100.0 % | 6.85, 85.0 % | 100.0 % of 2947 (0.971 / 0.990 / 1.021) |
| K6R depthroot2 pfifo r1 | rr->r0 | 15.5-95 | 2 521 282 | 1.000 / 1.031 / 1.107 / 14.1 | 99.77 % | 4.08, 93.2 % | 99.84 % of 1261 (0.980 / 0.998 / 1.025) |
| K1 hier pie r1 | r1->r2 | 8.8-27 | 1 670 185 | 1.000 / 1.006 / 1.018 / 3.09 | 99.97 % | 6.85, 86.3 % | 99.88 % of 14 995 (0.978 / 0.994 / 1.024) |

Absolute busy gaps at 17.5 Mb/s: p50 0.582 ms, p99.9 0.587 ms, max 0.769 ms (one full packet
takes 0.568 ms). Shape: unimodal and narrow. Gaps below 0.2 packet times are < 0.01 %
(no htb burst mode; 0.5-0.95 at most 0.4 %). Gaps above 1.5 packet times are at most 0.02 %
(no heavy tail). The
20 ms-window rule (+-5 % for >= 99 % of backlogged windows) would pass on all three runs.

## What I changed and did not change

- Gate check 4 in scripts/v3_gate.py: **unchanged** (stop rule 1c).
- router_trace.interdequeue_ratio: **unchanged** (it still uses len[i+1]; the health file's p99
  keeps the artifact). Switching it to len[i] is a one-line fix; I left it for you to decide.
- If you want (b) as written: check 4 = lost 0, CPU idle >= 35 %, the 20 ms window rule, the
  per-packet p99 (len[i]) as information, and an accounting rule (a) that the data cannot meet
  without first finding and fixing the missed tracepoint events.

## Follow-up, same day: decisions implemented

**gtq.py and unmatched packets (confirmed, no change needed).** In `gtq.run_truth` the sojourn
sequence is `deq = table[table["kind"] == "dequeue"]` and then `t_enq_ns >= 0`. A dequeue with no
enqueue record has kind `nohit`, so it is never in the sequence. It is not busy and not non-busy,
and it cannot start, end or split a busy run (busy_runs works on that sequence only). Enqueues
that are never matched are not rows of `<iface>-packets.csv`. From now on they go to their own file
`<iface>-unmatched-enq.csv` (kinds `orphan` and `open_at_exit`). gtq.py reads only `-packets.csv`,
so the labeler never sees them.

**Accounting (4a).** The tracer now writes the time of every unmatched enqueue:
- kind 5 `orphan`: the enqueue record is overwritten by a later enqueue of the same skb address;
- `open_at_exit`: the record is still open at stop (bpftrace's own map dump).

Health, per traced egress:
- `unmatched_deq`, `unmatched_enq` (= n_enq - n_deq - n_drop);
- both ratios to dequeues;
- the most of each kind in any sliding 200 ms window;
- `rows_match` and `accounting_ok`.

Rule (router_trace.accounting): both ratios <= 5e-5, <= 2 of either kind per 200 ms, lost
events 0. `gt_q_invalid` now follows this rule; strict `identity_ok` stays as information.

**The rule against the existing runs** (dequeue side complete; the enqueue-side window cannot be
checked on old data, which has no enqueue times):

| | value |
|---|---|
| unmatched dequeues / dequeues per egress | median 2.1e-5, max 2.1e-4; 21 of 166 egresses > 5e-5 |
| unmatched enqueues / dequeues per egress | median 2.6e-5, max 1.1e-4; 22 of 166 > 5e-5 |
| most unmatched dequeues in 200 ms | 0: 7, 1: 103, 2: 43, 3: 11, 4: 1, 5: 1 egresses |
| egresses failing the rule | 40 of 166; runs with a failing egress: 11 of 35 |
| by campaign | split C1 0/28, K1 0/20, M6 0/16, J1 0/8; base M1 0/8; uneven G0 9/14; tree8 K6 18/56, K6R 13/16 |

My earlier "1 per 2 x 10^5" was the total over all egresses. Per egress the median is ~2 x 10^-5,
so 5e-5 is ~2x the median, not 10x. Failures cluster where many tracers run at once (tree8 has
4 routers, so 4 bpftrace processes whose programs all fire on every packet in the kernel) and
where traffic is high (uneven: 17 clients). That fits the recursion-miss explanation. In v3,
T-TREE16 (4 routers + the publisher tracer, with background traffic) is the likely place to fail.
One bpftrace for all routers would cut the programs per packet from N to 1. That is a change to
the tracer, not made; your call.

**recursion_misses.** bpftool is not needed: the kernel prints `recursion_misses` per BPF program
in `/proc/<pid>/fdinfo/<fd>`. router_trace reads it from the bpftrace process just before
stopping it and writes `<router>.recursion_misses` (sum) and `.recursion_misses_per_prog` to
the health file. A short live test in the container (veth, ping flood) read 3 tracepoint
programs with 0 misses. Whether the counts match the unmatched packets will show in the
smoke. Expect the misses to be larger: every program also fires for other namespaces' packets.

**Service timing (4b).** `router_trace.service_stats` replaces `interdequeue_ratio`: ideal =
the previous packet's serialization time, backlogged gaps only, plus the 20 ms windows.
Health per egress: `interdeq_ratio_p50/p99` (corrected), `interdeq_within10`, `interdeq_gaps`,
`win20_n`, `win20_within5`. The gate requires >= 99 % for both.
