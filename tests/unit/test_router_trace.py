"""GT-Q router tracer output: parsing, pairing traps, identity, sender matching, health."""

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from quiclab import router_trace as rt  # noqa: E402


def ipw(dotted: str) -> int:
    """IPv4 as the tracer prints it: the network-order word read little-endian."""
    a, b, c, d = (int(x) for x in dotted.split("."))
    return a | b << 8 | c << 16 | d << 24


def portw(port: int) -> int:
    return ((port & 0xFF) << 8) | (port >> 8)


A, B, X = "10.99.0.3", "10.99.0.4", "10.99.0.9"   # video A, video B, cross traffic


def rec(kind, t_enq, t, src, dst, length=1442, ifindex=3, reason=0, h=7, prio=0, eth=8, sport=4433, dport=5000):
    return (f"{kind},{t_enq},{t},{ifindex},{eth},{ipw('10.99.0.2') if src == 'pub' else ipw(src)},"
            f"{ipw(dst)},17,{portw(sport)},{portw(dport)},{length},{h},{prio},{reason}")


def raw_text(lines, counters, lost=0, start=1_000, end=99_000_000_000):
    out = [f"Attaching 4 probes...", f"# gtq-tracer start {start}", *lines]
    if lost:
        out.append(f"Lost {lost} events")
    out.append(f"# gtq-tracer end {end}")
    out += [f"@{k}[3]: {v}" for k, v in counters.items()]
    return "\n".join(out) + "\n"


TRAPS = [
    # 1. plain dequeue
    rec(1, 2_000_000_000, 2_001_000_000, "pub", A),
    # 2. batched dequeue: two skbs handed over at one instant (same t)
    rec(1, 2_000_500_000, 2_002_000_000, "pub", A),
    rec(1, 2_000_600_000, 2_002_000_000, "pub", B),
    # 3. requeue: first dequeue at 2.003 s, requeued and dequeued again at 2.0045 s
    rec(1, 2_000_700_000, 2_003_000_000, "pub", A),
    rec(2, 2_000_700_000, 2_004_500_000, "pub", A),
    # 4. dropped at enqueue (tail drop): the tracer saw net_dev_queue, then kfree_skb
    rec(4, 2_005_000_000, 2_005_000_100, X, B, reason=72),
    # 5. fq_codel overlimit: a packet of A arrives, fq_codel drops from the fattest flow (B's head)
    rec(4, 2_000_800_000, 2_006_000_000, "pub", B, reason=73),
    rec(1, 2_006_000_000, 2_007_000_000, "pub", A),
    # 6. skb address reuse: the same skb address enqueued twice in a row is two independent rows
    rec(1, 2_008_000_000, 2_008_100_000, "pub", A),
    rec(1, 2_008_200_000, 2_008_300_000, "pub", A),
    # 7. nohit: dequeued in the first second (enqueued before the tracer attached)
    rec(3, 0, 1_000_500, "pub", A),
    # 8. a non-IPv4 frame (ARP): kept for the counts, address fields empty
    rec(1, 2_009_000_000, 2_009_100_000, "pub", A, eth=0x0608, length=42),
]
COUNTS = {"n_enq": 10, "n_deq": 8, "n_drop": 2, "n_requeue": 1, "n_nohit": 1, "n_batched": 1, "n_truncated": 0}


def table(lines=TRAPS, counters=COUNTS, **kw):
    raw = rt.parse_raw(raw_text(lines, counters, **kw))
    return raw, rt.packets_table(raw, 3)


def test_parse_counters_markers_and_lost_events():
    raw, _ = table(lost=5)
    assert raw.counters["n_enq"] == {3: 10} and raw.counters["n_batched"] == {3: 1}
    assert raw.lost_events == 5 and raw.start_ns == 1_000 and raw.end_ns == 99_000_000_000
    assert len(raw.records) == len(TRAPS)


def test_requeue_keeps_the_last_dequeue_and_one_row():
    _, t = table()
    req = t[t["t_enq_ns"] == 2_000_700_000]
    assert len(req) == 1 and req["kind"].iloc[0] == "dequeue" and req["t_deq_ns"].iloc[0] == 2_004_500_000


def test_batched_dequeue_rows_are_all_kept_with_their_own_flow():
    _, t = table()
    batch = t[t["t_deq_ns"] == 2_002_000_000]
    assert sorted(batch["daddr"]) == [A, B]


def test_drops_are_attributed_to_the_dropped_packet_and_carry_the_reason():
    _, t = table()
    drops = t[t["kind"] == "drop"]
    assert len(drops) == 2
    fat = drops[drops["reason"] == 73].iloc[0]
    assert fat["daddr"] == B and fat["t_enq_ns"] == 2_000_800_000 and fat["t_deq_ns"] == -1
    tail = drops[drops["reason"] == 72].iloc[0]
    assert tail["saddr"] == X and tail["t_drop_ns"] == 2_005_000_100


def test_address_reuse_gives_independent_rows_and_decoded_fields():
    _, t = table()
    reuse = t[t["t_enq_ns"].isin([2_008_000_000, 2_008_200_000])]
    assert len(reuse) == 2
    assert set(reuse["sport"]) == {4433} and set(reuse["dport"]) == {5000} and set(reuse["saddr"]) == {"10.99.0.2"}
    arp = t[t["len"] == 42].iloc[0]
    assert arp["saddr"] == "" and arp["proto"] == -1


def test_rows_sorted_by_event_time_and_nohit_has_no_enqueue():
    _, t = table()
    when = t["t_deq_ns"].where(t["t_deq_ns"] >= 0, t["t_drop_ns"])
    assert when.is_monotonic_increasing
    assert t[t["kind"] == "nohit"]["t_enq_ns"].tolist() == [-1]


def _counts_row(raw, t, **extra):
    tracer = rt.Tracer(router="router", ifaces={3: "router-eth1"}, hops={}, raw=Path("x"), log=Path("y"),
                       started_ns=1, stopped_clean=True)
    row = rt._count_row(tracer, 3, "router-eth1", raw, t)
    row.update(extra)
    return row


def test_identity_holds_for_the_trap_stream():
    raw, t = table()
    row = _counts_row(raw, t)
    assert row["rows_dequeue"] == 10 - 2 - 0 and row["rows_drop"] == 2
    ok, why = rt.identity(row)
    assert ok, why
    assert row["nohit_late"] == 0 and row["oversize"] == 0


def test_identity_fails_on_residual_or_missing_rows():
    raw, t = table(counters={**COUNTS, "n_enq": 11})
    assert not rt.identity(_counts_row(raw, t))[0]
    raw, t = table(lines=TRAPS[:-1])  # one row lost in the ring buffer
    assert not rt.identity(_counts_row(raw, t))[0]


def test_late_nohit_and_oversize_are_counted():
    lines = TRAPS + [rec(3, 0, 5_000_000_000, "pub", A), rec(1, 6_000_000_000, 6_000_100_000, "pub", A, length=3000)]
    raw, t = table(lines=lines)
    row = _counts_row(raw, t)
    assert row["nohit_late"] == 1 and row["oversize"] == 1


def test_match_flow_skips_packets_lost_before_the_router():
    send = [1000 + 10 * k for k in range(10)]
    size = [1400, 1400, 900, 1400, 1400, 1200, 1400, 1400, 1400, 700]
    keep = [0, 1, 2, 4, 5, 6, 8, 9]                    # 3 and 7 lost before the router
    t_enq = [send[k] + 5000 for k in keep]
    length = [size[k] + rt.QUIC_OVERHEAD_BYTES for k in keep]
    idx, rate = rt.match_flow(t_enq, length, send, size)
    assert rate == 1.0
    # size-identical neighbours of a lost packet may shift by one; distinct sizes resynchronise
    assert idx[2] == 2 and idx[4] == 5 and idx[7] == 9


def test_match_flow_unmatched_router_packet_lowers_the_rate():
    idx, rate = rt.match_flow([6000, 6010], [1442, 999], [1000, 1010], [1400, 1400])
    assert idx == [0, -1] and rate == 0.5


def test_first_ack_per_packet_number(tmp_path):
    p = tmp_path / "acks.csv"
    p.write_text("ack_mono_us,ranges\n100,0-2\n150,1-1;4-5\n200,3-3\n")
    assert rt.first_ack_us(p, 6).tolist() == [100, 100, 100, 200, 150, 150, -1]


def test_flag_env_overrides_topology(monkeypatch):
    class T:
        gtq_logging = True
    monkeypatch.delenv(rt.GTQ_ENV, raising=False)
    assert rt.enabled(T())
    monkeypatch.setenv(rt.GTQ_ENV, "0")
    assert not rt.enabled(T())
    T.gtq_logging = False
    monkeypatch.setenv(rt.GTQ_ENV, "1")
    assert rt.enabled(T())
    monkeypatch.setenv(rt.GTQ_ENV, "")
    assert not rt.enabled(T())


def test_tracer_argv_mask():
    argv = rt.tracer_argv(Path("/r/x.raw"), 4026531840, [3, 5])
    assert argv[-2:] == ["4026531840", str((1 << 3) | (1 << 5))] and argv[0] == "bpftrace"


def test_service_stats_ideal_link_is_one():
    import pandas as pd
    n, ser = 100, 1_200_000          # 1500 B at 10 Mb/s = 1.2 ms
    deq = [10**9 + k * ser for k in range(n)]
    t = pd.DataFrame({"kind": ["dequeue"] * n, "t_enq_ns": [10**9] * n, "t_deq_ns": deq, "len": [1500] * n})
    sv = rt.service_stats(t, 0, [(0.0, 10.0)])
    assert sv["gap_p50"] == pytest.approx(1.0) and sv["gap_p99"] == pytest.approx(1.0)
    assert sv["gap_within10"] == 1.0 and sv["win20_n"] == 5 and sv["win20_within5"] == 1.0


def test_service_stats_tolerance_floor_15us():
    """Rate-independent jitter on a 100 Mb/s link (packet time 120 us): gaps of 134 / 106 us
    (+-14 us) are outside +-10 % (12 us) but inside the 15 us floor."""
    import numpy as np
    import pandas as pd
    n, ser = 2000, 120_000          # 1500 B at 100 Mb/s
    jit = np.where(np.arange(n) % 2 == 0, 14_000, -14_000)
    deq = 10**9 + np.cumsum(np.full(n, ser) + jit)
    t = pd.DataFrame({"kind": ["dequeue"] * n, "t_enq_ns": [10**9] * n, "t_deq_ns": deq, "len": [1500] * n})
    sv = rt.service_stats(t, 0, [(0.0, 100.0)])
    assert sv["gap_within10"] < 0.01 and sv["gap_within_tol"] == 1.0
    assert sv["jitter_us_p1"] == pytest.approx(-14) and sv["jitter_us_p99"] == pytest.approx(14)


def test_service_stats_ideal_is_the_previous_packet():
    """HTB releases packet i+1 after paying packet i: a 42 B packet after a 1500 B one
    leaves 1.2 ms later at 10 Mb/s, which is ideal (the old statistic said ~36)."""
    import pandas as pd
    lens = [1500, 42] * 50
    deq, t = [], 10**9
    for ln in lens:
        deq.append(t)
        t += round(8 * ln / 10e6 * 1e9)
    tab = pd.DataFrame({"kind": ["dequeue"] * len(lens), "t_enq_ns": [10**9] * len(lens), "t_deq_ns": deq,
                        "len": lens})
    sv = rt.service_stats(tab, 0, [(0.0, 10.0)])
    assert sv["gap_p99"] == pytest.approx(1.0, abs=1e-3) and sv["gap_within10"] == 1.0


def _health_run(tmp_path, lines, counters, lost=0, stopped=True):
    run = tmp_path / "run"
    (run / rt.TRACE_DIR).mkdir(parents=True)
    (run / "logs").mkdir()
    raw = run / rt.TRACE_DIR / "router.raw"
    raw.write_text(raw_text(lines, counters, lost=lost))
    tracer = rt.Tracer(router="router", ifaces={3: "router-eth1"}, hops={"router-eth1": ("router", "switch")},
                       raw=raw, log=run / "logs" / "router-tracer.log", started_ns=1, stopped_clean=stopped)
    counts = rt.finalize(run, [tracer])
    (run / rt.CPU_FILE).write_text("mono_ns,idle\n1,0.80\n2,0.60\n")
    return run, tracer, counts


# The traps plus enough plain dequeues that one unmatched dequeue is below UNMATCHED_MAX_SHARE.
PAD = [rec(1, 3_000_000_000 + k * 100_000, 3_000_050_000 + k * 100_000, "pub", A) for k in range(30_000)]
PAD_COUNTS = {**COUNTS, "n_enq": COUNTS["n_enq"] + len(PAD), "n_deq": COUNTS["n_deq"] + len(PAD)}


def test_health_valid_run(tmp_path):
    run, tracer, counts = _health_run(tmp_path, TRAPS + PAD, PAD_COUNTS)
    values, line = rt.health(run, on=True, tracers=[tracer], counts=counts)
    assert values["router-eth1.unmatched_deq"] == 1 and values["router-eth1.unmatched_enq"] == 0
    assert values["router-eth1.unmatched_deq_ratio"] == f"{1 / PAD_COUNTS['n_deq']:.3e}"
    assert values["router-eth1.rows_match"] == 1 and values["router-eth1.accounting_ok"] == 1
    assert values["gt_q_invalid"] == 0, values["invalid_reasons"]
    assert values["cpu_idle_min"] == 0.6 and values["cpu_idle_mean"] == 0.7
    assert not (run / rt.TRACE_DIR / "router.raw").exists()
    assert (run / rt.TRACE_DIR / "router-eth1-packets.csv").exists()
    assert values["bytes_router_trace"] > 0 and "ok" in line
    assert rt.read_health(run)["gt_q_invalid"] == "0"


def test_accounting_rule_ratio_and_200ms_window(tmp_path):
    # 1 unmatched dequeue in 8 dequeues: within the minimum allowance of 3
    run, tracer, counts = _health_run(tmp_path, TRAPS, COUNTS)
    values, _ = rt.health(run, on=True, tracers=[tracer], counts=counts)
    assert values["gt_q_invalid"] == 0 and values["router-eth1.unmatched_allowed"] == 3
    # 4 unmatched dequeues, 1 s apart, in a short trace: above max(3, 5e-5 x dequeues)
    spread = [rec(3, 0, 20_000_000_000 + k * 1_000_000_000, "pub", A) for k in range(3)]
    run1 = tmp_path / "c"
    run1.mkdir()
    run1, tracer1, counts1 = _health_run(run1, TRAPS + spread, {**COUNTS, "n_nohit": 4})
    v1, _ = rt.health(run1, on=True, tracers=[tracer1], counts=counts1)
    assert v1["router-eth1.unmatched_deq"] == 4 and "allowed 3" in v1["invalid_reasons"]
    # three unmatched dequeues within 200 ms break the window rule even at a tiny ratio
    burst = [rec(3, 0, 50_000_000_000 + k * 50_000_000, "pub", A) for k in range(3)]
    many = PAD * 4
    pad4 = [rec(1, 4 * 10**9 + k * 10_000, 4 * 10**9 + k * 10_000 + 5_000, "pub", A) for k in range(len(many))]
    n = {**COUNTS, "n_enq": COUNTS["n_enq"] + len(pad4), "n_deq": COUNTS["n_deq"] + len(pad4), "n_nohit": 4}
    run2 = tmp_path / "w"
    run2.mkdir()
    run2, tracer2, counts2 = _health_run(run2, TRAPS + pad4 + burst, n)
    v2, _ = rt.health(run2, on=True, tracers=[tracer2], counts=counts2)
    assert v2["router-eth1.unmatched_deq"] == 4 and v2["router-eth1.unmatched_deq_max_200ms"] == 3
    assert "200 ms window" in v2["invalid_reasons"]


def test_unmatched_enqueues_kept_out_of_packets_csv(tmp_path):
    """Orphan enqueue records (kind 5) and enqueues still open at exit go to
    <iface>-unmatched-enq.csv only: the GT-Q labeler reads <iface>-packets.csv."""
    orphan = "5,2500000000,2600000000,3,0,0,0,0,0,0,0,0,0,0"
    counters = {**PAD_COUNTS, "n_enq": PAD_COUNTS["n_enq"] + 2}
    run, tracer, counts = _health_run(tmp_path, TRAPS + PAD + [orphan], counters)
    raw_extra = "@enq[0xffff888100000001]: 98000000000\n@eif[0xffff888100000001]: 3\n" \
                "@enq[0xffff888100000002]: 97000000000\n@eif[0xffff888100000002]: 4\n"
    raw = rt.parse_raw(raw_text(TRAPS + PAD + [orphan], counters) + raw_extra)
    assert raw.open_enq["0xffff888100000001"] == 98_000_000_000 and raw.open_if["0xffff888100000002"] == 4
    un = rt.unmatched_enqueues(raw, 3)
    assert list(un["kind"]) == ["orphan", "open_at_exit"] and list(un["t_enq_ns"]) == [2_500_000_000, 98_000_000_000]
    table_ = rt.packets_table(raw, 3)
    assert (table_["kind"].isin(["dequeue", "drop", "nohit"])).all() and 2_500_000_000 not in set(table_["t_enq_ns"])
    assert counts[0]["unmatched_enq"] == 2 and counts[0]["unmatched_enq_rows"] == 1   # exit dump not in this raw
    assert (run / rt.TRACE_DIR / "router-eth1-unmatched-enq.csv").exists()


def test_health_marks_lost_events_and_unclean_stop_invalid(tmp_path):
    run, tracer, counts = _health_run(tmp_path, TRAPS, COUNTS, lost=3)
    values, line = rt.health(run, on=True, tracers=[tracer], counts=counts)
    assert values["gt_q_invalid"] == 1 and "lost" in values["invalid_reasons"] and "INVALID" in line


def test_health_tracer_failed_to_start_is_invalid_but_written(tmp_path):
    run = tmp_path / "run"
    run.mkdir()
    tracer = rt.Tracer(router="router", ifaces={3: "router-eth1"}, hops={}, raw=run / "nope.raw", log=run / "nope.log")
    tracer.errors.append("tracer exited at start (status 1)")
    counts = rt.finalize(run, [tracer])
    values, _ = rt.health(run, on=True, tracers=[tracer], counts=counts)
    assert values["gt_q_invalid"] == 1 and "exited at start" in values["invalid_reasons"]


def test_health_logging_off(tmp_path):
    values, line = rt.health(tmp_path, on=False)
    assert values["gt_q_invalid"] == 0 and values["gtq_logging"] == 0 and "off" in line


def test_traced_interfaces_on_the_detector_topologies():
    from quiclab.config.scenario import load_scenario
    from quiclab.config.schema import load_topology
    from quiclab.orchestrator.mininet_backend import gtq_trace_interfaces
    base = ROOT / ".runs/old/ip4/2026-11-08_det-base/det-burstcap-pfifo-r1"
    if not base.exists():
        pytest.skip("campaign data not present")
    t = load_topology(base / "topology.yaml")
    s = load_scenario(base / "scenario.yaml", t)
    # router -> switch and router -> sub-ctrl (delay-only netem, subtracted offline);
    # router -> pub carries no subscriber's forward traffic; pub -> router is the publisher's egress
    assert gtq_trace_interfaces(t, s) == {"pub": [("pub-eth0", ("pub", "router"))],
                                          "router": [("router-eth1", ("router", "switch")),
                                                     ("router-eth3", ("router", "sub-ctrl"))]}
    # netem loss on an egress excludes it (the loss would look like queue drops)
    s.links[1].forward.loss_pct = 1.0
    assert ("router-eth1", ("router", "switch")) not in gtq_trace_interfaces(t, s)["router"]


def test_bpftrace_script_present_and_uses_the_planned_tracepoints():
    text = rt.SCRIPT.read_text()
    body = text.split("*/", 1)[1]
    # raw tracepoints: each program has its own recursion guard (classic ones share one per CPU)
    for probe in ("rawtracepoint:net_dev_queue", "rawtracepoint:qdisc_dequeue", "rawtracepoint:kfree_skb"):
        assert probe in body
    assert "tracepoint:net:" not in body and "args->" not in body
    assert "qdisc_enqueue" not in body   # only mentioned in the header comment


def test_bdp_queue_limit_option_off_by_default_and_derived_when_set():
    from quiclab.config.scenario import load_scenario
    from quiclab.config.schema import load_topology
    from quiclab.orchestrator.mininet_backend import bdp_queue_limit, initial_shaping_commands
    base = ROOT / ".runs/old/ip4/2026-11-08_det-base/det-burstcap-pfifo-r1"
    if not base.exists():
        pytest.skip("campaign data not present")
    t = load_topology(base / "topology.yaml")
    s = load_scenario(base / "scenario.yaml", t)
    assert s.router_queue("router").queue_limit_bdp is None
    assert any("pfifo limit 100" in cmd for _, cmd in initial_shaping_commands(t, s))
    forward, _ = s.initial_link("router", "switch")
    # 17.5 Mb/s x 100 ms (sub-d: 2 x (5 + 45) ms) / 12000 bit = 145.8 -> 146 packets per BDP
    assert bdp_queue_limit(t, s, ("router", "switch"), forward, 1.0) == 146
    assert bdp_queue_limit(t, s, ("router", "switch"), forward, 1.5) == 219


def test_health_attached_tracer_that_saw_nothing_is_invalid(tmp_path):
    run, tracer, counts = _health_run(tmp_path, [], {c: 0 for c in COUNTS})
    values, _ = rt.health(run, on=True, tracers=[tracer], counts=counts)
    assert values["gt_q_invalid"] == 1 and "no packet traced" in values["invalid_reasons"]


def test_stale_requeue_is_a_different_packet_not_folded():
    # seen in the first real run: a "requeue" 2.8 s after the address's first dequeue
    lines = TRAPS + [rec(2, 2_000_000_000, 4_800_000_000, "pub", A)]
    raw, t = table(lines=lines, counters={**COUNTS, "n_requeue": 2})
    first = t[t["t_enq_ns"] == 2_000_000_000]
    assert len(first) == 1 and first["t_deq_ns"].iloc[0] == 2_001_000_000   # not moved to 4.8 s
    stale = t[t["t_deq_ns"] == 4_800_000_000]
    assert stale["kind"].tolist() == ["nohit"] and stale["t_enq_ns"].tolist() == [-1]
    row = _counts_row(raw, t)
    assert rt.identity(row)[0] and row["requeue_stale"] == 1 and row["nohit_late"] == 1


def test_a_few_late_nohits_are_reported_not_fatal(tmp_path):
    lines = TRAPS + [rec(2, 2_000_000_000, 4_800_000_000, "pub", A)]
    run, tracer, counts = _health_run(tmp_path, lines, {**COUNTS, "n_requeue": 2})
    values, _ = rt.health(run, on=True, tracers=[tracer], counts=counts)
    # 1 late nohit of 8 dequeues is above 1e-4: invalid here; in a real run 2 of 146 332 is not
    assert values["router-eth1.requeue_stale"] == 1 and values["gt_q_invalid"] == 1
    assert 2 <= rt.NOHIT_MAX_SHARE * 146_332


def test_sender_match_ignores_pure_ack_sized_router_packets(tmp_path):
    import pandas as pd
    pub = tmp_path / "publishers" / "pub"
    pub.mkdir(parents=True)
    (pub / "sub-a-pkts.csv").write_text("send_mono_us,pn,size\n1000,1,1400\n1010,2,1400\n")
    t = pd.DataFrame({"kind": ["dequeue"] * 4, "t_enq_ns": [6_000_000, 6_005_000, 6_010_000, 6_020_000],
                      "saddr": ["10.99.0.2"] * 4, "daddr": ["10.99.0.3"] * 4, "proto": [17] * 4,
                      "len": [1442, 90, 1442, 90]})
    assert rt.sender_match_rate(tmp_path, "pub", "sub-a", t, "10.99.0.2", "10.99.0.3") == 1.0
