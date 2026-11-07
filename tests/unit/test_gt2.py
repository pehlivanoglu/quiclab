import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import gt2  # noqa: E402

DT = 0.025
CAP = [(0.0, 10.0)]  # 10 Mb/s: 31250 B per 25 ms
FULL = 10e6 * DT / 8


def series(rho: list[float], util: list[float], drops: list[int] | None = None):
    n = len(rho) + 1  # sample 0 opens the first interval
    t = np.arange(n) * DT
    offered = np.array([0.0] + [r * FULL for r in rho])
    sent = np.array([0.0] + [u * FULL for u in util])
    d = np.array([0] + (drops or [0] * len(rho)), dtype=float)
    return t, offered, sent, d


def episodes(rho, util, drops=None, p=gt2.Params()):
    t, offered, sent, d = series(rho, util, drops)
    return gt2.gt2_episodes(gt2.intervals(t, offered, sent, d, CAP, p), p)


def test_four_of_six_active_is_an_episode_with_backdated_onset():
    rho = [0.5, 0.5, 1.2, 1.2, 0.9, 1.2, 1.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
    util = [0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
    eps = episodes(rho, util)
    assert len(eps) == 1
    e = eps[0]
    assert e["t_on"] == pytest.approx(3 * DT) and e["t_end"] == pytest.approx(7 * DT)  # intervals 2..6 end at t[3]..t[7]
    assert e["peak_rho"] == pytest.approx(1.2) and e["sample_dt"] == pytest.approx(DT)


def test_three_of_six_is_not_persistent():
    rho = [1.2, 1.2, 1.2, 0.5, 0.5, 0.5, 0.5, 0.5]
    util = [1.0, 1.0, 1.0, 0.5, 0.5, 0.5, 0.5, 0.5]
    assert episodes(rho, util) == []


def test_drops_count_when_rho_hovers_at_one_but_not_on_an_idle_link():
    rho = [0.99] * 8
    assert len(episodes(rho, [0.99] * 8, [1] * 8)) == 1  # AQM: rho ~1, drops, link busy
    assert episodes([0.3] * 8, [0.3] * 8, [1] * 8) == []  # random loss on an idle link


def test_util_threshold_allows_one_packet_but_has_a_floor():
    p = gt2.Params()
    t, offered, sent, d = series([1.1] * 6, [0.955] * 6)  # 1 - 1500*8/250000 = 0.952
    assert gt2.intervals(t, offered, sent, d, CAP, p)["active"].all()
    t, offered, sent, d = series([1.1] * 6, [0.93] * 6)
    assert not gt2.intervals(t, offered, sent, d, CAP, p)["active"].any()
    slow = [(0.0, 0.5)]  # 0.5 Mb/s: one packet = 0.96 of 25 ms, floor 0.90 applies
    t, offered, sent, d = series([1.1] * 6, [0.92] * 6)
    offered, sent = offered * 0.05, sent * 0.05
    assert gt2.intervals(t, offered, sent, d, slow, p)["active"].all()


def test_gap_shorter_than_p_off_merges_longer_splits():
    on, off = [1.2] * 6, [0.5] * 5
    rho = on + [0.5] * 4 + on + off
    util = [1.0] * 6 + [0.5] * 4 + [1.0] * 6 + off
    assert len(episodes(rho, util, p=gt2.Params(p_off=0.15))) == 1  # 100 ms gap < 150
    assert len(episodes(rho, util, p=gt2.Params(p_off=0.1))) == 2


def test_t_x_is_earliest_excess_before_onset():
    rho = [0.5, 1.3, 0.8, 0.8, 1.2, 1.2, 1.2, 1.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
    util = [0.5, 0.5, 0.9, 0.9, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
    e = episodes(rho, util)[0]
    assert e["t_on"] == pytest.approx(5 * DT) and e["t_x"] == pytest.approx(2 * DT)


def test_thinning_sums_counters_per_interval():
    t = np.arange(7) * DT
    x = np.arange(7, dtype=float)  # sample i carries interval (t[i-1], t[i]]
    tt, a, b, c, q = gt2.thin(t, x, x, x, x, 2)
    assert list(tt) == list(t[[0, 2, 4, 6]])
    assert list(a) == [0, 1 + 2, 3 + 4, 5 + 6]


def test_severity_bins_and_cause():
    assert [gt2.severity(r) for r in (1.05, 1.3, 1.6)] == ["mild", "moderate", "severe"]
    spans = [(10.0, 14.0, "capacity_drop"), (20.0, 22.0, "cross_udp")]
    assert gt2.cause_of(spans, 10.02, 0.15) == "capacity_drop"
    assert gt2.cause_of(spans, 12.0, 0.15) == "capacity_drop"  # a later fragment of a running event
    assert gt2.cause_of(spans, 16.0, 0.15) == "endogenous"


def test_hysteresis_rides_through_a_dip_and_labels_ambiguous_load():
    rho = [1.2, 1.2, 1.2, 0.97, 1.2, 1.2, 1.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
    util = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
    banded = gt2.Params()
    plain = gt2.Params(util_band=0.0, rho_band=0.0)
    t, offered, sent, d = series(rho, util)
    iv = gt2.intervals(t, offered, sent, d, CAP, banded)
    assert iv["active"][:7].all()  # rho 0.97 >= 1 - 0.05 keeps it active
    assert not gt2.intervals(t, offered, sent, d, CAP, plain)["active"][3]
    eps = gt2.gt2_episodes(iv, banded)
    assert len(eps) == 1
    lab = gt2.interval_labels(iv, eps)
    assert list(lab[:7]) == ["CONGESTED"] * 7 and set(lab[7:]) == {"CLEAR"}
    t, offered, sent, d = series([0.8] * 8, [0.93] * 8)  # busy-ish, no excess: util in the band
    iv = gt2.intervals(t, offered, sent, d, CAP, banded)
    assert set(gt2.interval_labels(iv, gt2.gt2_episodes(iv, banded))) == {"AMBIGUOUS"}
