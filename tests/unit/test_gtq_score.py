"""Detector scoring against GT-Q / GT-H (new files only)."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests" / "unit"))
import gtq  # noqa: E402
import gtq_score  # noqa: E402
from test_gtq import make_run, stream  # noqa: E402


def test_merge_alarms_within_w():
    assert gtq_score.merge_alarms([1.0, 1.05, 1.2, 3.0], 0.1) == [1.0, 1.2, 3.0]


def test_score_run_tp_fp_gray_and_latency(tmp_path):
    rows = stream("pub", "sub-a", 1, 30, 0.004, lambda t: 0.04 if 10 <= t < 13 else 0.0005)
    run = make_run(tmp_path, "pfifo", rows)
    gtq.score(run)
    eps = [r for r in (run / "truth" / "gtq.csv").read_text().splitlines()[1:]]
    assert len(eps) == 1
    starts = {("shadow", "sub-a"): [10.3, 10.32, 20.0], ("gcc", "sub-a"): [], ("bbr", "sub-a"): [9.97]}
    ep_rows, tallies = gtq_score.score_run(run, starts)
    by = {(t["detector"], t["flow"]): t for t in tallies}
    s = by[("shadow", "sub-a")]
    assert s["alarms"] == 2 and s["alarms_matched"] == 1 and s["fp"] == 1   # 10.32 merged into 10.3
    hit = next(r for r in ep_rows if r["detector"] == "shadow" and r["flow"] == "sub-a")
    assert hit["hit"] == 1 and hit["L_0_ms"] == pytest.approx(300, abs=5)
    assert by[("bbr", "sub-a")]["alarms_matched"] == 1                     # inside the pre-collar (W)
    miss = next(r for r in ep_rows if r["detector"] == "gcc")
    assert miss["hit"] == 0 and miss["censor_ms"] > 0
    m = gtq_score._metrics([r for r in ep_rows if r["detector"] == "shadow"],
                           [t for t in tallies if t["detector"] == "shadow"])
    assert m["precision_gtq"] == pytest.approx(0.5) and m["recall_gtq"] == 1.0
