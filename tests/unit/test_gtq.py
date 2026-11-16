"""GT-Q labeler and GT-H on synthetic packet logs (spec v1.2 section 5 sanity rows)."""

import csv
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
import gtq  # noqa: E402
from quiclab import router_trace as rt  # noqa: E402

MTU = 1500
C = 10e6                       # bottleneck 10 Mb/s -> tau = 1.2 ms
TAU = 8 * MTU / C
W = 0.1                        # synthetic W for the core tests


def fifo(arrivals, capacity=C, limit=1000):
    """Single-server FIFO: arrivals [(t, bytes, flow)] -> (t_enq, t_deq, flow) of dequeued
    packets and [(t, flow)] drops (tail drop at `limit` queued packets)."""
    out, drops, busy_until, queue = [], [], 0.0, []
    for t, size, f in sorted(arrivals):
        queue = [d for d in queue if d > t]          # departures still pending at t
        if len(queue) >= limit:
            drops.append((t, f))
            continue
        start = max(t, busy_until)
        busy_until = start + 8 * size / capacity
        queue.append(start)
        out.append((t, start, f))
    return out, drops


def video(fps, rate_bps, t0, t1, flow="v", line=100e6):
    """Frames as back-to-back bursts of MTU packets at `line` rate."""
    arr, per_frame = [], rate_bps / fps / 8
    t = t0
    while t < t1:
        n = max(1, int(per_frame // MTU))
        arr += [(t + k * 8 * MTU / line, MTU, flow) for k in range(n)]
        t += 1 / fps
    return arr


def cbr(rate_bps, t0, t1, flow="bulk"):
    gap = 8 * MTU / rate_bps
    return [(t, MTU, flow) for t in np.arange(t0, t1, gap)]


def label(arrivals, limit=1000, flow="v", w=W, tau=TAU):
    deq, drops = fifo(arrivals, limit=limit)
    t_enq = np.array([d[0] for d in deq])
    t_deq = np.array([d[1] for d in deq])
    f_drops = np.array([t for t, f in drops if f == flow])
    f_enq = np.array([d[0] for d in deq if d[2] == flow] + list(f_drops))
    return gtq.queue_episodes(t_enq, t_deq, np.full(len(t_deq), tau), f_drops, f_enq, w)


# ── spec section 5, row by row ─────────────────────────────────────────────

@pytest.mark.parametrize("fps", [15, 30, 60])
def test_idle_link_frame_bursts_drain_within_w(fps):
    w = max(0.05, 1 / fps)
    eps, gray = label(video(fps, 2.5e6, 0, 10), w=w)
    assert eps == []
    assert gray == []


def test_pfifo_saturating_bulk_flow_is_one_long_episode_for_the_video():
    arr = video(30, 2.5e6, 0, 20) + cbr(12e6, 5, 15)
    eps, _ = label(arr, limit=100)
    assert len(eps) == 1
    e = eps[0]
    assert abs(e["t0"] - 5) < W and 15 <= e["t1"] < 15 + 0.5
    assert e["kind"] in ("standing", "both")


def test_queue_held_near_5ms_with_drops_is_an_episode():
    # CoDel-like: every packet waits ~5 ms (> tau) for 5 s; the video loses a packet every 0.3 s
    t = np.arange(10, 15, 0.001)
    t_enq, t_deq = t, t + 0.005
    f_drops = np.arange(10.1, 15, 0.3)
    eps, _ = gtq.queue_episodes(t_enq, t_deq, np.full(len(t), TAU), f_drops, t_enq, W)
    assert len(eps) == 1
    assert eps[0]["kind"] == "both" and eps[0]["f_drops"] == len(f_drops)
    assert abs(eps[0]["t0"] - 10) < 1e-9


def test_drop_only_episodes_and_their_merge_gap():
    t = np.arange(0, 10, 0.01)  # idle queue: no sojourn above tau
    for drops, n in (([2.0], 1), ([2.0, 2.15], 1), ([2.0, 2.25], 2)):
        eps, _ = gtq.queue_episodes(t, t, np.full(len(t), TAU), np.array(drops), t, W)
        assert len(eps) == n, drops
        assert all(e["kind"] == "drop" for e in eps)
        assert abs(eps[0]["t0"] - 2.0) < 1e-9 and abs(eps[-1]["t1"] - (drops[-1] + W)) < 1e-9


def _standing(spans, dt=0.001, soj=0.01):
    t = np.arange(0, 10, dt)
    s = np.zeros(len(t))
    for a, b in spans:
        s[(t >= a) & (t < b)] = soj
    return t, t + s


@pytest.mark.parametrize("gap,n", [(0.5 * W, 1), (1.5 * W, 2)])
def test_standing_intervals_merge_across_gaps_shorter_than_w(gap, n):
    t_enq, t_deq = _standing([(1, 1 + 2 * W), (1 + 2 * W + gap, 1 + 4 * W + gap)])
    eps, _ = gtq.queue_episodes(t_enq, t_deq, np.full(len(t_enq), TAU), np.array([]), t_enq, W)
    assert len(eps) == n


def test_gray_short_busy_run_and_below_two_tau():
    # 0.7 W busy run: gray, no episode
    t_enq, t_deq = _standing([(1, 1 + 0.7 * W)])
    eps, gray = gtq.queue_episodes(t_enq, t_deq, np.full(len(t_enq), TAU), np.array([]), t_enq, W)
    assert eps == [] and [g["why"] for g in gray] == ["short busy run"]
    # a busy run longer than W whose sojourn is between tau and 2 tau: gray, not positive
    t_enq, t_deq = _standing([(1, 1 + 3 * W)], soj=1.5 * TAU)
    eps, gray = gtq.queue_episodes(t_enq, t_deq, np.full(len(t_enq), TAU), np.array([]), t_enq, W)
    assert eps == [] and [g["why"] for g in gray] == ["below 2 tau"]
    # under W / 2: neither
    t_enq, t_deq = _standing([(1, 1 + 0.3 * W)])
    assert gtq.queue_episodes(t_enq, t_deq, np.full(len(t_enq), TAU), np.array([]), t_enq, W) == ([], [])


def test_shared_queue_episode_needs_the_flow_present():
    t_enq, t_deq = _standing([(1, 2)])
    f_enq = np.array([5.0])   # f only sends later
    eps, _ = gtq.queue_episodes(t_enq, t_deq, np.full(len(t_enq), TAU), np.array([]), f_enq, W)
    assert eps == []


def test_onset_is_start_of_the_busy_period_not_when_w_is_reached():
    t_enq, t_deq = _standing([(3, 4)])
    eps, _ = gtq.queue_episodes(t_enq, t_deq, np.full(len(t_enq), TAU), np.array([]), t_enq, W)
    assert abs(eps[0]["t0"] - 3) < 1e-9 and abs(eps[0]["t1"] - 4) < 0.002


def test_capacity_drop_onset_within_w_of_the_stimulus():
    # 10 -> 2 Mb/s at t = 5 s for 3 s under a 2.5 Mb/s video
    arr = video(30, 2.5e6, 0, 12)
    out, busy_until = [], 0.0
    for t, size, f in sorted(arr):
        cap = 2e6 if 5 <= t < 8 else C
        start = max(t, busy_until)
        busy_until = start + 8 * size / cap
        out.append((t, start))
    t_enq, t_deq = np.array(out).T
    tau = np.where((t_deq >= 5) & (t_deq < 8), 8 * MTU / 2e6, TAU)
    eps, _ = gtq.queue_episodes(t_enq, t_deq, tau, np.array([]), t_enq, W)
    # spec: "within about W" -- here the queue stops draining between frames 3 frames later
    assert len(eps) == 1 and 0 <= eps[0]["t0"] - 5 < 1.5 * W


def test_fq_index_pinned_priority_and_hash():
    prio = np.array([(0x20 << 16) | 0x301, 0, (0x10 << 16) | 5])
    hashes = np.array([0, 0x80000000, 0x40000000], dtype=np.uint64)
    assert gtq.fq_index(prio, hashes).tolist() == [0x300, 512, 256]


# ── whole-run wiring on a synthetic run directory ──────────────────────────

TOPOLOGY = """publishers:
  pub: { cc_algo: bbr }
subscribers:
  sub-a: { connects_to: pub, rate_kbps: 2500 }
  sub-b: { connects_to: pub, rate_kbps: 1000 }
routers:
  router: {}
switches:
  switch: {}
links:
  - { from: pub, to: router }
  - { from: router, to: switch }
  - { from: switch, to: sub-a }
  - { from: switch, to: sub-b }
"""

EPOCH_NS = 1_000_000_000_000
EPOCH_UNIX_NS = 1_700_000_000_000_000_000


def make_run(tmp_path: Path, aqm: str, rows: list[dict], frames: dict | None = None, hop="router->switch",
             bottleneck_delay_ms: float | None = None):
    run = tmp_path / "run"
    (run / "router-trace").mkdir(parents=True)
    (run / "topology.yaml").write_text(TOPOLOGY)
    (run / "scenario.yaml").write_text(f"""duration_s: 30
links:
- {{from: pub, to: router, forward: {{bandwidth_mbps: 100, delay_ms: 5.0}}, reverse: {{delay_ms: 5.0}}}}
- {{from: router, to: switch, forward: {{bandwidth_mbps: 10{f", delay_ms: {bottleneck_delay_ms}" if bottleneck_delay_ms else ""}}}}}
- {{from: switch, to: sub-a, forward: {{delay_ms: 20.0}}, reverse: {{delay_ms: 20.0}}}}
- {{from: switch, to: sub-b, forward: {{delay_ms: 20.0}}, reverse: {{delay_ms: 20.0}}}}
routers:
  router: {{aqm: {aqm}}}
""")
    (run / "events.csv").write_text(
        "event,at_s,applied_s,applied_mono_ns,applied_unix_ns,target,detail,label,status,error\n"
        f"epoch,0,0,{EPOCH_NS},{EPOCH_UNIX_NS},,,,applied,\n")
    a, b = hop.split("->")
    (run / "router-trace" / "interfaces.csv").write_text(
        f"router,iface,ifindex,netns,hop\n{a},{a}-eth1,3,1,{hop}\n")
    with (run / "router-trace" / f"{a}-eth1-packets.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rt.PACKET_FIELDS))
        w.writeheader()
        w.writerows(rows)
    (run / "gtq-health.csv").write_text("key,value\ngtq_logging,1\ngt_q_invalid,0\ninvalid_reasons,\n")
    for sid, (sent, recv) in (frames or {}).items():
        pub = run / "publishers" / "pub"
        pub.mkdir(parents=True, exist_ok=True)
        (run / "clients").mkdir(exist_ok=True)
        with (pub / f"{sid}-frames.csv").open("w") as f:
            f.write("index,keyframe,size,send_us,write_us,stream\n")
            f.writelines(f"{i},0,1000,{us},{us},1\n" for i, us in sent)
        (pub / f"{sid}-drops.csv").write_text("t_us,index,gop,keyframe,size,age_us\n")
        with (run / "clients" / f"{sid}-frames.csv").open("w") as f:
            f.write("index,keyframe,size,send_us,recv_us,owd_us,late_us\n")
            f.writelines(f"{i},0,1000,{s},{r},{r - s},0\n" for i, s, r in recv)
    return run


IPS = {"router": "10.99.0.1", "pub": "10.99.0.2", "sub-a": "10.99.0.3", "sub-b": "10.99.0.4"}


def test_loopbacks_match_the_fixture(tmp_path):
    import det_eval
    run = make_run(tmp_path, "pfifo", [])
    assert {k: v for k, v in gtq.loopbacks(det_eval.Run(run)).items() if k in IPS} == IPS


def pkt(t_enq, t_deq, src, dst, prio=0, h=0, kind="dequeue", t_drop=-1, length=1442):
    ns = lambda t: int(EPOCH_NS + t * 1e9) if t is not None else -1  # noqa: E731
    return {"kind": kind, "t_enq_ns": ns(t_enq), "t_deq_ns": ns(t_deq) if kind != "drop" else -1,
            "t_drop_ns": ns(t_drop) if kind == "drop" else -1, "reason": 2 if kind == "drop" else 0,
            "saddr": IPS[src] if src in IPS else src, "daddr": IPS[dst] if dst in IPS else dst, "proto": 17,
            "sport": 4433, "dport": 5000, "len": length, "hash": h, "prio": prio}


def stream(src, dst, t0, t1, dt, soj, **kw):
    return [pkt(t, t + soj(t), src, dst, **kw) for t in np.arange(t0, t1, dt)]


def score(tmp_path, aqm, rows, frames=None, hop="router->switch", bottleneck_delay_ms=None):
    import det_eval
    run = make_run(tmp_path, aqm, rows, frames, hop, bottleneck_delay_ms)
    return gtq.run_truth(det_eval.Run(run)), run


def test_fq_codel_sparse_video_next_to_a_busy_bulk_subqueue_has_no_episode(tmp_path):
    video_prio = (0x20 << 16) | 0x301
    rows = stream("pub", "sub-a", 1, 20, 0.004, lambda t: 0.0005, prio=video_prio)
    rows += stream("10.255.0.9", "10.255.0.8", 1, 20, 0.0012, lambda t: 0.02, h=0x10000000)
    (eps, gray, params, _), _ = score(tmp_path, "fq_codel", sorted(rows, key=lambda r: r["t_deq_ns"]))
    assert [e for e in eps if e["flow"] == "sub-a"] == []
    p = next(x for x in params if x["flow"] == "sub-a")
    assert p["fq_index"] == 0x300 and p["fq_collision"] == ""


def test_fq_codel_video_over_its_share_has_an_episode(tmp_path):
    video_prio = (0x20 << 16) | 0x301
    rows = stream("pub", "sub-a", 1, 20, 0.004, lambda t: 0.03 if 5 <= t < 10 else 0.0005, prio=video_prio)
    rows += stream("10.255.0.9", "10.255.0.8", 1, 20, 0.0012, lambda t: 0.02, h=0x10000000)
    (eps, _, _, _), _ = score(tmp_path, "fq_codel", sorted(rows, key=lambda r: r["t_deq_ns"]))
    mine = [e for e in eps if e["flow"] == "sub-a"]
    assert len(mine) == 1 and abs(mine[0]["t0"] - 5) < 0.01


def test_fq_codel_hash_collision_is_included_and_flagged(tmp_path):
    video_prio = (0x20 << 16) | 0x301
    # an unpinned flow whose hash lands in bucket 0x300 (reciprocal_scale(h, 1024) = 0x300)
    # shares the video's sub-queue from 5 to 10 s: both wait 20 ms there
    rows = stream("pub", "sub-a", 1, 20, 0.004, lambda t: 0.02 if 5 <= t < 10 else 0.0005, prio=video_prio)
    h = (0x300 << 22) + 5
    rows += stream("10.255.0.9", "10.255.0.8", 5, 10, 0.0012, lambda t: 0.02, h=h)
    (eps, _, params, _), _ = score(tmp_path, "fq_codel", sorted(rows, key=lambda r: r["t_deq_ns"]))
    p = next(x for x in params if x["flow"] == "sub-a")
    assert "10.255.0.9" in p["fq_collision"]
    assert any(e["flow"] == "sub-a" for e in eps)


def test_shared_queue_bulk_flow_gives_both_videos_one_episode(tmp_path):
    rows = stream("pub", "sub-a", 1, 20, 0.004, lambda t: 0.04 if 5 <= t < 12 else 0.0005)
    rows += stream("pub", "sub-b", 1, 20, 0.01, lambda t: 0.04 if 5 <= t < 12 else 0.0005)
    (eps, _, params, _), _ = score(tmp_path, "pfifo", sorted(rows, key=lambda r: r["t_deq_ns"]))
    assert sorted(e["flow"] for e in eps) == ["sub-a", "sub-b"]
    p = next(x for x in params if x["flow"] == "sub-a")
    # W = max(largest base RTT through router->switch = 2 x (5 + 20) ms, 33.3 ms) = 50 ms
    assert p["W_ms"] == pytest.approx(50.0) and p["tau_ms_t0"] == pytest.approx(1.2)


def test_reverse_path_only_is_tagged_and_never_harmful(tmp_path):
    # the traced egress carries only sub-a's ACKs (client -> publisher)
    rows = stream("sub-a", "pub", 1, 20, 0.004, lambda t: 0.04 if 5 <= t < 12 else 0.0005)
    (eps, _, _, _), _ = score(tmp_path, "pfifo", rows, hop="router->pub")
    assert len(eps) == 1 and eps[0]["direction"] == "reverse"
    assert eps[0]["harmful_600"] == 0 and eps[0]["t_obs_method"] == "reverse"


def test_gth_marks_a_late_frame_inside_the_collar_and_gives_the_harm_instant(tmp_path):
    rows = stream("pub", "sub-a", 1, 20, 0.004, lambda t: 0.04 if 5 <= t < 8 else 0.0005)
    us = lambda t: int((EPOCH_UNIX_NS + t * 1e9) // 1000)  # noqa: E731
    gen = [round(1 + i / 30, 6) for i in range(500)]
    sent = [(i, us(t)) for i, t in enumerate(gen)]
    # frames generated at 6 s arrive 0.8 s late (miss 600, not 1000); one frame never arrives (miss all)
    recv = []
    for i, t in enumerate(gen):
        if i == 450:   # generated at 16 s, outside the episode
            continue
        delay = 0.8 if 6.0 <= t < 6.1 else 0.03
        recv.append((i, us(t), us(t + delay)))
    (eps, _, _, misses), _ = score(tmp_path, "pfifo", rows, frames={"sub-a": (sent, recv)})
    e = next(x for x in eps if x["flow"] == "sub-a")
    assert e["harmful_600"] == 1 and e["harmful_300"] == 1 and e["harmful_1000"] == 0
    first_late = min(t for t in gen if 6.0 <= t < 6.1)
    assert e["t_harm_600"] == pytest.approx(first_late + 0.6, abs=1e-5)
    out = {m["budget_ms"]: m for m in misses if m["flow"] == "sub-a"}
    assert out[1000]["misses"] == 1 and out[1000]["misses_outside"] == 1
    assert out[600]["misses_in_episode"] == 3 and out[600]["misses_outside"] == 1


def test_deadline_misses_censor_unreceived_frames_after_the_horizon():
    import pandas as pd
    frames = pd.DataFrame({"t_gen": [1.0, 2.0, 9.8], "t_recv": [1.1, np.nan, np.nan], "dropped": [False, True, False]})
    assert gtq.deadline_misses(frames, 0.6, horizon=10.0).tolist() == pytest.approx([2.6])
    assert gtq.deadline_misses(frames, 0.05, horizon=11.0).tolist() == pytest.approx([1.05, 2.05, 9.85])


def test_invalid_run_gets_status_only(tmp_path):
    run = make_run(tmp_path, "pfifo", stream("pub", "sub-a", 1, 5, 0.004, lambda t: 0.0005))
    (run / "gtq-health.csv").write_text("key,value\ngtq_logging,1\ngt_q_invalid,1\ninvalid_reasons,lost tracer events\n")
    (run / "truth").mkdir()
    (run / "truth" / "gtq.csv").write_text("stale\n")
    line = gtq.score(run)
    assert "not produced" in line and not (run / "truth" / "gtq.csv").exists()
    assert "lost tracer events" in (run / "truth" / "gtq-status.csv").read_text()


def test_score_writes_every_output(tmp_path):
    run = make_run(tmp_path, "pfifo", stream("pub", "sub-a", 1, 20, 0.004, lambda t: 0.04 if 5 <= t < 8 else 0.0005))
    gtq.score(run)
    for name in ("gtq.csv", "gtq-gray.csv", "gtq-params.csv", "gth.csv", "gth-outside.csv", "gtq-status.csv"):
        assert (run / "truth" / name).exists(), name
    head = (run / "truth" / "gtq.csv").read_text().splitlines()[0].split(",")
    assert head == list(gtq.EPISODE_FIELDS)


def test_netem_delay_on_the_egress_is_not_sojourn(tmp_path):
    # 20 ms netem on router -> switch: every packet spends >= 20 ms between enqueue and dequeue
    rows = stream("pub", "sub-a", 1, 20, 0.004, lambda t: 0.020 + (0.04 if 5 <= t < 8 else 0.0005))
    (eps, _, params, _), _ = score(tmp_path, "pfifo", rows, bottleneck_delay_ms=20.0)
    mine = [e for e in eps if e["flow"] == "sub-a"]
    assert len(mine) == 1 and abs(mine[0]["t0"] - 5.02) < 0.01 and mine[0]["max_sojourn_ms"] < 41
    assert next(p for p in params if p["flow"] == "sub-a")["netem_delay_ms_t0"] == 20.0
