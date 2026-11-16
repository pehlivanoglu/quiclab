# GT-Q logging, GT-Q and GT-H (2026-11-14)

Status: code complete, unit-tested on synthetic data. **The router tracer and the
qvideo-server packet log have never run in a real testbed run** (no root / no
privileged container was available while this was written). The first real runs
are the test; their `gtq-health.csv` says whether the logging worked.

GT1, GT2 and GT3 are unchanged (code, names, outputs, tables). GT-Q and GT-H are
new, separate outputs next to them.

## The flag

One switch for both halves of the logging (router tracer + sender packet log):

| where | how |
|---|---|
| topology YAML | `gtq_logging: false` (top level; default `true`) |
| whole campaign, no YAML edit | `QUICLAB_GTQ_LOGGING=0 python3 scripts/det_matrix.py ...` (also `grouping_campaign.py`, `python -m quiclab run`); `1` forces it on. The variable is forwarded into the container. |

Off means: no bpftrace, no `--pkt_log`, no `router-trace/`. The per-run health file
and the 1 Hz host-CPU sample (`host-cpu.csv`) are written either way.

Rollback of the image: the image before bpftrace was added is tagged
`quiclab:pre-gtq` (`docker tag quiclab:pre-gtq quiclab:latest`). With the old image,
bpftrace is missing, the tracer fails to start, and the run goes on with
`gt_q_invalid = 1`.

## What runs during a run

* **Router tracer** (`quiclab/router_trace.bt`, lifecycle in `quiclab/router_trace.py`,
  started by `mininet_backend._start_gtq_tracers` before the publishers, in the container's own namespaces (not the router's: `ip netns exec` remounts /sys and hides tracefs; the script filters by netns inode), stopped after
  every traffic source plus a 0.5 s drain). One bpftrace per router, inside the
  router's netns, filtered in the kernel to the netns inode and an ifindex bitmask.
  Traced egresses (`gtq_trace_interfaces`): router egresses on at least one
  subscriber's forward path, rate-shaped (HTB), whose netem (if any) only delays: no
  loss (it would look like queue drops) and no jitter, at t=0 or in any event. The
  labeler subtracts the netem delay in force at each packet's enqueue. On the
  2026-11-08 campaigns: base `router-eth1` (-> switch) and `router-eth3` (-> sub-ctrl,
  20 ms netem); access additionally `ra-eth1` ... `rd-eth1` (the access bottlenecks);
  split `r1-eth1`, `r1-eth2` (-> sub-ctrl), `r2-eth1`, `r2-eth2`. Egresses towards the
  publisher carry no subscriber's forward traffic and are not traced, so
  **reverse-path GT-Q episodes cannot occur in today's topologies**.
  * enqueue time: `net:net_dev_queue` (every packet, just before the root qdisc).
    `qdisc:qdisc_enqueue` is not used: it fires only on NET_XMIT_SUCCESS, so it misses a
    packet fq_codel accepts while dropping from the same flow (NET_XMIT_CN).
  * dequeue: `qdisc:qdisc_dequeue`; a batched dequeue (packets > 1) is walked along
    `skb->next` (at most 16, counted as truncated beyond); a requeued skb's later
    dequeue is a `requeue` record, folded into the first one offline (the last
    dequeue time wins).
  * drop: `skb:kfree_skb` of an skb that was enqueued and not yet dequeued, with the
    drop reason: the dropped skb itself, so fq_codel's drop from the fattest flow is
    attributed to that flow. A packet dropped at enqueue (tail drop) has its
    `net_dev_queue` record and then its drop.
  * skb address reuse: every `net_dev_queue` overwrites the address's entry.
  * maps: 262 144 keys (`BPFTRACE_MAX_MAP_KEYS`), 512 ring pages per CPU, `-B full`.
    A full map shows as `nohit` dequeues after the first second -> invalid.
* **Sender log** (`qvideo-server --pkt_log`, class `PacketLog`): one row per AppData
  packet written (send time, packet number, encoded size) and per ACK (receive time,
  newly acked ranges). Rows go into 1 MiB / 256 KiB stream buffers, written out on the
  stats timer; nothing in the send, CC or detector path changes.
* **Host CPU** (`router_trace.CpuSampler`): /proc/stat idle share once per second.

Every step is wrapped: a tracer that does not attach within 15 s, dies, ignores
SIGINT for 20 s, or whose output cannot be converted leaves the run untouched and
marks it `gt_q_invalid`.

## After every run (automatic, inside the container)

`router_trace.finalize` converts the raw bpftrace output into
`router-trace/<iface>-packets.csv` (the raw file is deleted only after a successful
conversion) and `router-trace/tracer-counts.csv`; `router_trace.health` writes
**`<run>/gtq-health.csv`** (key, value) and prints one line (`*** gtq health: ...`, also
in `logs/gtq-health.log`):

| key | meaning |
|---|---|
| `tracer_started`, `tracer_stopped_clean`, `lost_events` | lifecycle; lost = bpftrace "Lost N events" |
| `<iface>.enq/deq/drop/identity_ok` | kernel counters; identity = enq == deq + drop and rows written == counters |
| `<iface>.requeue/batched/nohit_late/oversize` | traps seen; oversize = skb > 1514 B |
| `<iface>.interdeq_ratio_p50/p99` | inter-dequeue time / ideal serialization (8 len / C) while the queue was busy |
| `cpu_idle_min/mean` | host CPU idle over the run |
| `<iface>.match.<sub>`, `match_rate_min` | share of the flow's router packets matched to a QUIC packet number |
| `bytes_router_trace/sender_log/written` | disk used by the new logging |
| `gt_q_invalid`, `invalid_reasons` | 1 when events were lost, the identity fails, the tracer failed, or the map overflowed |

## Offline (post-run pipeline)

`scripts/det_matrix.py` runs, after GT1 / GT2 / GT3 and in its own try block:
`gtq.score(run)` for runs with `router-trace/`, `gtq.summary(campaign)` after every run,
and `gtq_score.report([campaign])` at the end of the campaign.
`scripts/grouping_campaign.py` was not touched (uncommitted user changes); run by hand:

    python3 scripts/gtq.py score .runs/<campaign>/*/       # GT-Q / GT-H per run
    python3 scripts/gtq.py summary .runs/<campaign>        # <campaign>/gtq-health-summary.{csv,md}
    python3 scripts/gtq_score.py .runs/<campaign>          # <campaign>/gtq-detector-table.{csv,md}

Per run (`truth/`): `gtq.csv` (episodes, with t_obs and GT-H columns per budget),
`gtq-gray.csv`, `gtq-params.csv` (W, tau, fq sub-queue, collision, match rate per
resource x flow), `gth.csv` (harmful episodes per budget), `gth-outside.csv` (deadline
misses outside every episode), `gtq-status.csv`; `gtq-score-episodes.csv` from the scorer.
A `gt_q_invalid` run gets `gtq-status.csv` only.

Algorithm and every deviation from the spec: `scripts/gtq.py` docstring and
`docs/paper-notes-ground-truth.md`.

## Probe (needs a privileged container)

    docker run --rm --privileged -v "$PWD:$PWD" -w "$PWD" quiclab:latest \
        bash scripts/gtq_tracer_probe.sh pfifo     # also fq_codel | codel | pie | red

Two netns, a 10 Mbit/s HTB + AQM, two iperf3 UDP flows overloading it; prints the
counters, the identity, drop reasons, sojourns, and `PROBE PASS` / `FAIL`. Not run yet.
