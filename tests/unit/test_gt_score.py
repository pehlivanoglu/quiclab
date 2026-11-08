import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import gt_bands  # noqa: E402
import gt_score  # noqa: E402


def test_alarm_classes_follow_the_three_labels():
    run = SimpleNamespace(duration=40.0, subs=["s"])
    spans = [{"t_start": 0.0, "t_end": 20.0, "label": gt_bands.CLEAR},
             {"t_start": 20.0, "t_end": 25.0, "label": gt_bands.AMBIGUOUS},
             {"t_start": 25.0, "t_end": 30.0, "label": gt_bands.CONGESTED},
             {"t_start": 30.0, "t_end": 40.0, "label": gt_bands.CLEAR}]
    code = gt_score.client_view_codes(run, spans)
    view = {"s": ([(25.0, 30.0)], code)}
    # 10 s: CLEAR -> FP; 22 s: AMBIGUOUS -> ignored; 24.5 s: early tolerance -> TP; 27 s: duplicate; 35 s: FP
    starts = {(d, "s"): [10.0, 22.0, 24.5, 27.0, 35.0] for d in gt_score.SCORED}
    t = gt_score.score(run, view, starts)["shadow"]
    assert (t["episodes"], t["detected"], t["tp"], t["fp"]) == (1, 1, 1, 2)
    assert t["latency"] == [0.0]
    assert abs(t["clear_s"] - (15.0 + 10.0)) < 0.02 and abs(t["amb_s"] - 5.0) < 0.02  # warm-up (5 s) excluded
    s = gt_score.summarize([t])
    assert s["precision"] == 1 / 3 and s["recall"] == 1.0


def test_hysteresis_state_machine():
    enter = np.array([0, 1, 0, 0, 0, 1], dtype=bool)
    stay = np.array([0, 1, 1, 0, 1, 1], dtype=bool)
    assert list(gt_bands.hysteresis(enter, stay)) == [False, True, True, False, False, True]


def test_recall_by_duration_bin_and_hop_level_recall():
    run = SimpleNamespace(duration=60.0, subs=["x", "y"], pub="pub")
    code = gt_score.client_view_codes(run, [{"t_start": 0.0, "t_end": 60.0, "label": gt_bands.CLEAR}])
    # x: a 0.3 s and a 3 s episode; y: a 1.5 s episode. Alarms only on the long ones.
    view = {"x": ([(10.0, 10.3), (20.0, 23.0)], code), "y": ([(30.0, 31.5)], code)}
    starts = {("shadow", "x"): [20.1], ("shadow", "y"): [30.2]}
    s = gt_score.summarize([gt_score.score(run, view, starts, ("shadow",))["shadow"]])
    assert s["bin_episodes"] == [1, 0, 1, 1] and s["recall"] == 2 / 3
    assert s["bin_recall"][0] == 0.0 and s["bin_recall"][2] == 1.0 and s["bin_recall"][3] == 1.0
    # hop level: one hop episode exposed to x and y counts once, detected if either alarms.
    import det_eval
    run.topology = {"links": [{"from": "pub", "to": "r"}, {"from": "r", "to": "x"}, {"from": "r", "to": "y"}]}
    hop = gt_score.hop_score(run, [("pub->r", 20.0, 23.0), ("pub->r", 40.0, 41.0)], starts, ("shadow",))["shadow"]
    assert hop == {"hop_episodes": 2, "hop_detected": 1}
