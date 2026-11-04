"""Pure parts of the grouping run tooling (scripts/grouping_adapter.py,
scripts/grouping_baselines.py): hierarchical pair truth and baseline scoring."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import grouping_adapter as ga  # noqa: E402
import grouping_baselines as gb  # noqa: E402

A, B = {"a1", "a2", "a3"}, {"b1", "b2", "b3"}
SUBS = sorted(A | B | {"ctrl"})


def test_leaf_groups_split_topology():
    leaf = ga.leaf_groups([A | B, A, B, A | B], {}, SUBS)
    assert leaf["a1"] == frozenset(A) and leaf["b2"] == frozenset(B)
    assert leaf["ctrl"] == frozenset()


def test_leaf_groups_single_bottleneck_equals_link_relation():
    leaf = ga.leaf_groups([A, A], {}, sorted(A | {"ctrl"}))
    assert all(leaf[s] == frozenset(A) for s in A) and leaf["ctrl"] == frozenset()


def test_leaf_groups_topology_fallback():
    same = {"a1": {"a2"}, "a2": {"a1"}, "ctrl": set()}
    leaf = ga.leaf_groups([], same, ["a1", "a2", "ctrl"])
    assert leaf["a1"] == leaf["a2"] == frozenset({"a1", "a2"}) and leaf["ctrl"] == frozenset()


def test_first_sustained_ignores_single_lucky_window():
    states = [(0.0, True), (1.0, False), (2.0, True), (3.0, True), (8.0, True), (9.0, True)]
    assert gb.first_sustained(states, sustain_s=5.0) == 2.0
    assert gb.first_sustained([(0.0, True), (1.0, False)], sustain_s=5.0) is None
    assert gb.first_sustained([(0.0, False), (1.0, True)], sustain_s=5.0) == 1.0   # last sample holds


def _truth():
    subs = sorted(A | B)
    pairs = {f"{f}|{g}": True for i, f in enumerate(subs) for g in subs[i + 1:]}
    pairs_leaf = {p: (set(p.split("|")) <= A or set(p.split("|")) <= B) for p in pairs}
    return {"bursts": [{"start": 10.0, "end": 12.0, "hit": sorted(A | B)},
                       {"start": 30.0, "end": 32.0, "hit": sorted(A)},
                       {"start": 50.0, "end": 52.0, "hit": sorted(B)}],
            "pairs": pairs, "pairs_leaf": pairs_leaf}


def test_score_sbd_majority_over_burst_windows():
    truth = _truth()
    pairs = sorted(truth["pairs_leaf"])
    # Perfect per-window grouping: one label per active group, singletons elsewhere.
    windows = []
    for t in [x / 2 for x in range(20, 120)]:
        hits = gb.active_hits(truth, t)
        labels = {s: i for i, s in enumerate(sorted(A | B), start=10)}
        for h in hits:
            for s in h:
                labels[s] = 1
        windows.append((t, labels))
    m = gb.score_sbd(windows, truth, pairs)
    assert m["windows"]["precision"] == 1.0 and m["windows"]["recall"] == 1.0
    assert m["windows"]["calm_grouped_fraction"] == 0.0
    # a-b pairs are grouped only in the upstream burst's windows (1 of 3 bursts): DIFFERENT.
    assert m["final"]["vs_leaf"]["precision"] == 1.0 and m["final"]["vs_leaf"]["recall"] == 1.0
    assert m["final"]["vs_link"]["recall"] < 1.0
    # Running majority: b pairs reach half only during the b burst, a-b pairs fall below it.
    assert 50.0 <= m["t_correct"] <= 54.0
