# Per-client queue counters for multi-queue AQMs (design, 2026-11-11)

Status: design agreed with the user on 2026-11-11, verified with
`scripts/tc_perflow_probe.sh`, implemented the same day (unit tests; an end-to-end
probe of the orchestrator's pin commands plus router_metrics in the quiclab
image). No campaign run uses it yet.

## Why

GT1, the grouping truth, reads one backlog per router egress. On fq_codel and
cake that backlog is the sum of per-flow queues. A client whose own queue never
builds is still counted as hit when the aggregate queue stands. Its silence is
then scored as a missed alarm, although its path was not congested.

The 2026-11-11 episode study shows this: on fq_codel and cake, "same group"
pairs have uncorrelated delay curves (r ≈ 0.1), and the clients' queues drain
about 1 s before the router aggregate does. A per-client router counter turns GT1
into "this client's own queue stood", which is the truth these AQMs need.

## Environment

| | |
|---|---|
| kernel | 7.0.0-42-generic (host; the container uses the host kernel) |
| tc in the quiclab image | iproute2 6.17.0 (the one the testbed runs) |
| tc on the host | iproute2 6.1.0 (not used by the testbed) |

## Mechanism

Every egress already has the shape `HTB 5: → class 5:1 → [netem 10:] → AQM 20:`.
Each subscriber gets a fixed flow id on every fq_codel or cake router egress:
`shaping.client_flow_ids`, sorted subscribers from 0x301 upward, at most 0x400
(the fq_codel default of 1024 flows; 256 subscribers). The ids are always
rendered as hex; they are never typed by hand. Packets to a client carry its
loopback address as destination (routes pin `src` to the loopback), so one
address match per client is enough; re-joined sessions `<sid>_<n>` share it.

**fq_codel: no filter on the qdisc.** A clsact egress filter on the same
interface sets `skb->priority = 20:<id>`. fq_codel's classifier first checks
whether the major of `skb->priority` equals its handle and the minor is ≤ its
flow count, and if so uses the minor as the flow. Unmarked packets (cross
traffic, ARP, ICMP) keep fq_codel's normal hash.

```bash
tc qdisc add dev X clsact
tc filter add dev X egress protocol ip prio 1 u32 match ip dst <client IP>/32 action skbedit priority 20:<id>
```

**cake: u32 filters on the qdisc.** cake reads `skb->priority` only to choose a
tin. With `besteffort` it ignores the mark: the probe shows the flows hashed.
Filters with a classid do override cake's flow; packets no filter matches fall
back to cake's hash.

```bash
tc filter add dev X parent 20: protocol ip prio 1 u32 match ip dst <client IP>/32 flowid 20:<id>
```

**Reading.** `tc -s -j class show dev X parent 20:` lists each active flow as
class `20:<n>`, with backlog bytes and packets, qlen and drops. router-metrics
(`--flows 301=sub-a,...`, passed by the orchestrator to every client-facing
sampler; the map is also in `router-metrics/flow-ids.json`) dumps the classes
at its 25 ms interval whenever the leaf is fq_codel or cake and writes
`<iface>-flows.csv`: `timestamp_mono_ns, class, flow, qlen_packets,
backlog_bytes, drops`, one row per pinned class the dump lists (also when
empty: proves the pin) and per other class with a backlog (flow empty; counts
the backlogged flows). Timestamps equal the egress CSV's rows.

**Per-client GT1** (`gt1.run_flow_truth`): the GT1 rule on the client's own
backlog, with the delay at its fair share: `q = backlog × n / capacity`, n = the
number of backlogged classes at the sample (`gt1_core(share=...)`). The grouping
truth (`grouping_adapter.measured_bursts`, `hop_flow_episodes`) counts an
expected client as hit on such an egress only when its own episode overlaps the
window; other egresses and older runs keep the aggregate GT1.

## Pitfalls (both found in the probe)

1. **Class minors are hex.** `flowid 20:1001` means 0x1001 = 4097, which is
   larger than fq_codel's 1024 flows. fq_codel then drops the packet without an
   error message: `Sent 0 pkt (dropped N)`.
2. **A filter on fq_codel drops every packet it does not classify,** ARP
   included, because `fq_codel_classify` returns 0 when filters exist and none
   match. A catch-all filter would avoid the drop but would merge all other
   flows into one bucket, which changes the AQM. The `flow` classifier, which
   could rebuild a per-flow hash, is rejected by this kernel with EINVAL in
   every form tried (also under HTB). Hence the priority mark, which needs no
   filter on fq_codel at all.
3. **The mark must be set on the egress interface itself.** Forwarding rewrites
   `skb->priority` from the TOS byte, so a mark set at ingress is lost. clsact
   egress runs right before the root qdisc.
4. **HTB also reads `skb->priority`**, but only when its major is HTB's own
   handle (5:). The AQM handle must stay different from the HTB handle; it is
   20: today.

## Limits

- Continuity at 25 ms: without per-flow transmitted bytes, a flow's run is
  continuous between samples only when its queue cannot drain in one interval
  at its fair share (the drain bound). Short per-flow queues (fair-share delay
  < 25 ms) therefore split or fall below the GT1 interval. The first fq_codel /
  cake runs should show whether a faster per-flow sampler is needed.
- The fair share counts backlogged classes only; a flow that is active but
  momentarily empty is not in n, so the delay estimate is a lower bound.

- An unmarked flow (cross traffic) can hash into a pinned client bucket.
  Probability about (pinned clients) / 1024 per flow; it cannot be prevented,
  only reported.
- Per-flow classes exist only for fq_codel and cake. pfifo, RED and PIE are
  single queues, so the aggregate GT1 already is the per-client truth there.

## Per-run self-check (into `infra.md`)

- Every pinned client shows up as a class `20:<id>` on every fq_codel or cake
  egress of its path at least once while it sends.
- The AQM's `Sent` counter grows (no silent drop from a misclassification).

## qevents (tc(8) "QEVENTS"; looked at 2026-11-11)

A qdisc can run a filter block when an event happens inside it. In tc(8),
tc-red(8), tc-fq_codel(8), tc-cake(8) and tc-pie(8), only RED defines qevents:
`early_drop` and `mark` (ECN). The probe's `red` mode attaches block 10 with one
counting filter per client and gets per-client early-drop counts that sum to
RED's `early` counter (1197 + 216 + the unpinned flow = 2212).

So for RED a qevent gives a per-client "received a congestion signal" truth: who
was dropped or marked, and when. It is not queue occupancy, and it does not
exist on fq_codel or cake, where the per-client truth is needed. Possible later
use: a per-client drop/mark column for RED next to GT1, if early drops
(rather than the standing queue) turn out to be the better truth there.

## Code

| step | where |
|---|---|
| ids, pin commands (flower: idempotent `replace`, fixed pref / handle) | `quiclab/orchestrator/shaping.py` (`client_flow_ids`, `flow_pin_commands`) |
| pins at setup and after a live AQM change | `quiclab/orchestrator/mininet_backend.py` (`initial_shaping_commands`, `apply_live_router_aqm`) |
| `--flows`, `<iface>-flows.csv` | `quiclab/router_metrics.py` (`parse_flows`, `flow_rows`, `run`) |
| per-client GT1 | `scripts/gt1.py` (`gt1_core(share=)`, `load_flow_samples`, `run_flow_truth`) |
| grouping truth | `scripts/grouping_adapter.py` (`gt1_hop_flow_episodes`, `measured_bursts(hop_flow_episodes=)`) |
| self-check column in `infra.md` | `scripts/grouping_campaign.py` (`pin_check`) |

Left: re-run the fq_codel and cake cells of `.runs/2026-11-10_1946_v2` (the
user runs them).
