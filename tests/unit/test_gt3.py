import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import gt3  # noqa: E402

DT = 0.005


def flow(owd_ms, sent=None, timed=None):
    n = len(owd_ms)
    t = 20.0 + np.arange(n) * DT
    sent = np.ones(n) if sent is None else np.asarray(sent, dtype=float)
    timed = sent.copy() if timed is None else np.asarray(timed, dtype=float)
    return t, np.asarray(owd_ms, dtype=float), sent, timed


def run(owd, sent=None, timed=None, p=gt3.Params()):
    t, o, s, tm = flow(owd, sent, timed)
    return t, gt3.flow_core(t, o, s, tm, [], p, DT)


def test_standing_queue_is_one_delay_episode_backdated_to_its_start():
    owd = [20.0] * 400 + [50.0] * 200 + [20.0] * 400  # 30 ms queue for 1 s
    t, (eps, lab, _) = run(owd)
    assert len(eps) == 1
    e = eps[0]
    assert e["trigger"] == "delay"
    assert e["t_on"] == pytest.approx(t[400], abs=DT)  # backdated over the 150 ms minimum
    assert e["peak_q"] == pytest.approx(30.0)
    assert set(lab[:390]) == {"CLEAR"}


def test_short_spike_is_not_an_episode_and_band_is_ambiguous():
    owd = [20.0] * 400 + [80.0] * 20 + [20.0] * 400  # 100 ms spike: the 150 ms minimum never reaches 10 ms
    _, (eps, lab, _) = run(owd)
    assert eps == []
    owd = [20.0] * 400 + [27.0] * 200 + [20.0] * 400  # 7 ms standing: between stay (5) and enter (10)
    _, (eps, lab, _) = run(owd)
    assert eps == [] and "AMBIGUOUS" in set(lab)


def test_loss_channel_enters_at_ten_percent_and_onset_is_the_first_lost_bin():
    n = 1000
    sent = np.full(n, 2.0)  # 400 packets per second
    timed = sent.copy()
    timed[500:600] = 1.0  # 50 % loss for 0.5 s
    _, (eps, _, _) = run([20.0] * n, sent, timed)
    assert len(eps) == 1 and eps[0]["trigger"] == "loss"
    assert eps[0]["t_on"] == pytest.approx(20.0 + 500 * DT)


def test_empty_bins_are_no_data_and_keep_the_state():
    owd = [20.0] * 400 + [50.0] * 100 + [np.nan] * 20 + [50.0] * 100 + [20.0] * 400
    timed = [0.0 if np.isnan(x) else 1.0 for x in owd]
    _, (eps, lab, _) = run(owd, None, timed)
    assert len(eps) == 1
    _, (_, lab, _) = run([20.0] * 200 + [np.nan] * 10 + [20.0] * 200, None, [1.0] * 200 + [0.0] * 10 + [1.0] * 200)
    assert list(lab[200:210]) == ["NO_DATA"] * 10


def test_baseline_follows_a_path_delay_decrease_within_its_window():
    t = np.arange(0, 40, DT)
    owd = np.where(t < 20, 40.0, 20.0)  # path delay drops by 20 ms, no queue anywhere
    base = gt3.baseline(t, owd, [], 10.0)
    assert base[t.searchsorted(19.0)] == 40.0 and base[t.searchsorted(21.0)] == 20.0
    base = gt3.baseline(t, np.where(t < 20, 20.0, 40.0), [20.0], 10.0)  # increase, reset at the change
    assert base[t.searchsorted(21.0)] == 40.0


def test_queue_between_band_and_episode_windows_is_ambiguous_not_clear():
    owd = [20.0] * 400 + [50.0] * 60 + [20.0] * 400  # 30 ms standing queue for 300 ms: < 500 ms, > 150 ms
    _, (eps, lab, _) = run(owd)
    assert eps == []
    assert set(lab[430:460]) == {"AMBIGUOUS"} and set(lab[:390]) == {"CLEAR"}
