import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from baselines.sbd.detector import CobottleneckDetector  # noqa: E402
from baselines.sbd.sbd import SBDAlgorithm  # noqa: E402


def test_dcw_separates_two_correlated_groups() -> None:
    rng = np.random.default_rng(1)
    t = np.round(np.arange(0, 3.0, 0.01), 3)
    shared = [np.cumsum(rng.normal(0, 1e-3, len(t))) for _ in range(2)]
    rows = []
    for flow in range(6):
        owd = 0.02 + shared[flow // 3] + rng.normal(0, 1e-5, len(t))
        rows.append(pd.DataFrame({"run": "r", "flow": flow, "time": t, "owd": owd, "drop": 0, "label": 0}))
    df = pd.concat(rows, ignore_index=True)
    det = CobottleneckDetector(df, 1.5, t_unit=0.01, model_th=0.8)
    selected = det._get_selected_dfs(0, t.max(), 150)
    (labels, *_rest) = det.classify(0, t.max(), selected, method="dcw", seq_len=150)
    assert labels[0] == labels[1] == labels[2] and labels[3] == labels[4] == labels[5]
    assert labels[0] != labels[3]


def test_rmcat_non_bottlenecked_label_does_not_collide_with_a_group() -> None:
    # flows 0, 1 not bottlenecked (skew above c_s, no loss); flows 2, 3 bottlenecked, identical stats.
    # "run" (a string column, as in real SBD input) keeps iterrows rows as Python ints for its df.query
    df = pd.DataFrame({"run": "r", "time": 0.35, "flow": [0, 1, 2, 3], "skew_est": [0.5, 0.5, -0.5, -0.5],
                       "var_est": 0.01, "freq_est": 0.0, "pkt_loss": 0.0})
    labels = SBDAlgorithm().rmcat_clustering(df).set_index("flow").group
    assert labels[2] == labels[3]
    assert len({labels[0], labels[1], labels[2]}) == 3
