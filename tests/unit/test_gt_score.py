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
