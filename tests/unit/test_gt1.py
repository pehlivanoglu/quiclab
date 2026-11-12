import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import gt1  # noqa: E402

DT = 0.025
CAP = [(0.0, 10.0)]  # 10 Mb/s: 25 ms carries 31.25 kB, 5 ms of queue = 6.25 kB
P = gt1.Params(interval_s=0.1, merge_gap_s=0.1).resolve(0.0)


def series(backlog_ms: list[float], util: list[float] | None = None, cap=CAP):
    t = np.arange(len(backlog_ms)) * DT
    cap_bps = np.array([gt1.det_eval.value_at(cap, x) for x in t]) * 1e6
    backlog = np.array(backlog_ms) / 1000 * cap_bps / 8
    tx = None if util is None else np.array(util) * cap_bps * DT / 8
    return t, backlog, tx


def test_standing_queue_is_one_episode_with_backdated_start():
    t, backlog, tx = series([0, 0, 20, 20, 20, 20, 20, 20, 0, 0], [0.5, 0.5, 1, 1, 1, 1, 1, 1, 0.3, 0.3])
    drops = np.array([0, 0, 0, 3, 0, 2, 0, 0, 9, 0])
    eps = gt1.gt1_episodes(t, backlog, tx, CAP, P, drops)
    assert len(eps) == 1
    ep = eps[0]
    assert ep["start_s"] == t[2] and ep["start_lo_s"] == t[1] and ep["end_s"] == t[7]
    assert ep["q_min_ms"] == 20 and ep["q_max_ms"] == 20 and ep["fragments"] == 1 and ep["drops"] == 5


def test_shorter_than_interval_is_not_an_episode():
    t, backlog, tx = series([0, 20, 20, 20, 0, 0], [1] * 6)  # 3 samples: 50 ms < 100 ms
    assert gt1.gt1_episodes(t, backlog, tx, CAP, P) == []


def test_below_target_or_below_mtu_is_not_above():
    t, backlog, tx = series([4.9] * 8, [1] * 8)
    assert gt1.gt1_episodes(t, backlog, tx, CAP, P) == []
    t, backlog, tx = series([5.0] * 8, [1] * 8, cap=[(0.0, 2.0)])  # 5 ms at 2 Mb/s = 1250 B < MTU
    assert gt1.gt1_episodes(t, backlog, tx, CAP and [(0.0, 2.0)], P) == []


def test_deep_backlog_cannot_drain_between_samples_so_util_dips_do_not_split():
    # 170 ms backlog, utilisation quantised down to 0.90 in some intervals: still one episode.
    util = [1, 0.9, 1.05, 0.93, 1, 0.9, 1, 1]
    t, backlog, tx = series([170] * 8, util)
    eps = gt1.gt1_episodes(t, backlog, tx, CAP, gt1.Params(interval_s=0.1, util_th=0.98, merge_gap_s=0.0).resolve(0.0))
    assert len(eps) == 1 and eps[0]["fragments"] == 1


def test_shallow_backlog_needs_a_busy_link_to_be_continuous():
    # 10 ms of backlog can empty inside 25 ms; an idle interval breaks the run.
    t, backlog, tx = series([10] * 12, [1, 1, 1, 1, 1, 1, 0.6, 1, 1, 1, 1, 1])
    p = gt1.Params(interval_s=0.1, merge_gap_s=0.0).resolve(0.0)
    eps = gt1.gt1_episodes(t, backlog, tx, CAP, p)
    assert [(e["start_s"], e["end_s"]) for e in eps] == [(t[0], t[5]), (t[6], t[11])]
    # Without transmitted bytes (5 ms queue CSV) only the drain bound applies.
    assert len(gt1.gt1_episodes(t, backlog, None, CAP, p)) == 0
    t5 = np.arange(12) * 0.005
    assert len(gt1.gt1_episodes(t5, backlog, None, CAP, gt1.Params(interval_s=0.05, merge_gap_s=0.0).resolve(0.0))) == 1


def test_auto_threshold_allows_one_packet_of_quantisation():
    # 25 ms at 10 Mb/s = 20.8 packets: one packet short (0.952) is busy, two (0.90) is not.
    t, backlog, tx = series([10] * 8, [1, 0.952, 1, 1, 1, 1, 1, 1])
    assert len(gt1.gt1_episodes(t, backlog, tx, CAP, P)) == 1
    t, backlog, tx = series([10] * 8, [1, 0.90, 1, 1, 1, 1, 1, 1])
    assert len(gt1.gt1_episodes(t, backlog, tx, CAP, P)) == 1  # second run alone is 150 ms
    assert gt1.gt1_episodes(t, backlog, tx, CAP, P)[0]["start_s"] == t[1]


def test_close_episodes_merge_and_count_fragments():
    q = [20] * 6 + [0] * 2 + [20] * 6
    t, backlog, tx = series(q, [1] * len(q))
    eps = gt1.gt1_episodes(t, backlog, tx, CAP, gt1.Params(interval_s=0.1, merge_gap_s=0.1).resolve(0.0))
    assert len(eps) == 1 and eps[0]["fragments"] == 2 and eps[0]["end_s"] == t[13]
    eps = gt1.gt1_episodes(t, backlog, tx, CAP, gt1.Params(interval_s=0.1, merge_gap_s=0.05).resolve(0.0))
    assert len(eps) == 2


def test_capacity_change_inside_an_interval_uses_the_integral():
    caps = [(0.0, 10.0), (0.0625, 5.0)]  # drop halfway through the interval ending at t=0.075
    assert gt1.capacity_integral(caps, 0.05, 0.075) == pytest.approx(0.0125 * 10e6 + 0.0125 * 5e6)
    assert gt1.capacity_max(caps, 0.05, 0.075) == 10e6
    t = np.arange(8) * DT
    backlog = np.full(8, 0.030 * 5e6 / 8)  # 30 ms at 5 Mb/s, 15 ms at 10 Mb/s: above target throughout
    tx = np.array([gt1.capacity_integral(caps, max(0, x - DT), x) / 8 for x in t])  # saturated throughout
    eps = gt1.gt1_episodes(t, backlog, tx, caps, P)
    assert len(eps) == 1 and eps[0]["start_s"] == 0.0 and eps[0]["end_s"] == t[-1]
    assert eps[0]["q_min_ms"] == 15.0 and eps[0]["q_max_ms"] == 30.0


def test_params_resolve_interval_from_rtt():
    assert gt1.Params().resolve(0.2).interval_s == 0.15  # fixed 150 ms by default
    assert gt1.Params().resolve(0.2).merge_gap_s == 0.15
    auto = gt1.Params(interval_s="auto")
    assert auto.resolve(0.05).interval_s == 0.1
    assert auto.resolve(0.2).interval_s == 0.2
    assert gt1.Params(interval_s=0.35, merge_gap_s=0.5).resolve(0.2) == gt1.Params(5.0, 0.35, "auto", 0.5)


def test_plot_windows_merge_simultaneous_events_and_cover_long_ones():
    import truth_plot as gt1_plot
    from types import SimpleNamespace
    bursts = [{"start": 20.0, "end": 24.0, "kind": "capacity", "u_agg": 2.0, "hop": ("r1", "r2")},
              {"start": 20.01, "end": 24.0, "kind": "capacity", "u_agg": 2.0, "hop": ("r2", "switch-a")},
              {"start": 40.0, "end": 41.0, "kind": "udp", "u_agg": 1.3, "hop": ("r1", "r2")}]
    wins = gt1_plot.windows(SimpleNamespace(duration=100.0), bursts)
    assert len(wins) == 2
    assert wins[0][0] == 20.0 - gt1_plot.LEAD_S and wins[0][1] == pytest.approx(20.01 - gt1_plot.LEAD_S + gt1_plot.WINDOW_S)
    assert "r1->r2" in wins[0][2] and "r2->switch-a" in wins[0][2]
    assert wins[1] == (40.0 - gt1_plot.LEAD_S, 40.0 - gt1_plot.LEAD_S + gt1_plot.WINDOW_S, wins[1][2])
    calm = gt1_plot.windows(SimpleNamespace(duration=120.0), ())
    w0 = gt1_plot.d.WARMUP_S
    assert [w[0] for w in calm] == [w0 + k * gt1_plot.CALM_STEP_S for k in range(4)]


def test_hysteresis_keeps_a_queue_dipping_into_the_band_and_labels_windows():
    q = [0, 20, 20, 20, 3, 20, 20, 20, 1, 0]  # one sample at 3 ms: below TARGET, above TARGET - 2.5
    t, backlog, tx = series(q, [1] * len(q))
    banded = gt1.Params(interval_s=0.1, merge_gap_s=0.0).resolve(0.0)
    plain = gt1.Params(interval_s=0.1, merge_gap_s=0.0, q_band_ms=0.0, util_band=0.0).resolve(0.0)
    eps, lab = gt1.gt1_core(t, backlog, tx, CAP, banded)
    assert [(e["start_s"], e["end_s"]) for e in eps] == [(t[1], t[7])]
    assert list(lab) == ["CLEAR"] + ["CONGESTED"] * 7 + ["CLEAR", "CLEAR"]
    assert gt1.gt1_episodes(t, backlog, tx, CAP, plain) == []  # each side alone is 50 ms < 100 ms
    _, lab = gt1.gt1_core(*series([0, 3, 4, 20, 0], [1] * 5), CAP, banded)
    assert list(lab) == ["CLEAR", "AMBIGUOUS", "AMBIGUOUS", "AMBIGUOUS", "CLEAR"]  # 20 ms alone fails persistence


def test_per_flow_queue_delay_is_taken_at_the_fair_share():
    # A flow queue of 4 ms at the full 10 Mb/s (below target, drains within a 25 ms sample) is 32 ms
    # at an eighth share (8 backlogged flows): above target and it cannot empty between samples.
    t, backlog, _ = series([4.0] * 10)
    assert gt1.gt1_episodes(t, backlog, None, CAP, P) == []
    eps = gt1.gt1_episodes(t, backlog, None, CAP, P, share=np.full(10, 8.0))
    assert len(eps) == 1 and eps[0]["q_min_ms"] == pytest.approx(32.0) and eps[0]["cap_mbps"] == pytest.approx(10.0)
