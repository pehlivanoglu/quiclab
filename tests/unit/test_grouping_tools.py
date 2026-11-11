"""Pure parts of the grouping run tooling (scripts/grouping_adapter.py,
scripts/grouping_baselines.py): hierarchical pair truth and baseline scoring."""

import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import grouping_adapter as ga  # noqa: E402
import grouping_baselines as gb  # noqa: E402

A, B = {"a1", "a2", "a3"}, {"b1", "b2", "b3"}
SUBS = sorted(A | B | {"ctrl"})


def _b(hit, expected=None):
    return {"hit": sorted(hit)} if expected is None else {"hit": sorted(hit), "expected": sorted(expected)}


def test_leaf_groups_split_topology():
    leaf = ga.leaf_groups([_b(A | B), _b(A), _b(B), _b(A | B)], {}, SUBS)
    assert leaf["a1"] == frozenset(A) and leaf["b2"] == frozenset(B)
    assert leaf["ctrl"] == frozenset()


def test_leaf_groups_single_bottleneck_equals_link_relation():
    leaf = ga.leaf_groups([_b(A), _b(A)], {}, sorted(A | {"ctrl"}))
    assert all(leaf[s] == frozenset(A) for s in A) and leaf["ctrl"] == frozenset()


def test_leaf_groups_topology_fallback():
    same = {"a1": {"a2"}, "a2": {"a1"}, "ctrl": set()}
    leaf = ga.leaf_groups([], same, ["a1", "a2", "ctrl"])
    assert leaf["a1"] == leaf["a2"] == frozenset({"a1", "a2"}) and leaf["ctrl"] == frozenset()


def test_leaf_groups_partial_hits_and_private_windows_keep_the_link_group():
    # fq_codel-like partial hits (2 of 3) and a private access-link window on a1.
    bursts = [_b({"a1", "a2"}, A), _b({"a2", "a3"}, A), _b({"a1"}, {"a1"}), _b(B, B), _b(A | B, A | B)]
    leaf = ga.leaf_groups(bursts, {}, SUBS)
    assert leaf["a1"] == leaf["a2"] == leaf["a3"] == frozenset(A)
    assert leaf["b1"] == frozenset(B) and leaf["ctrl"] == frozenset()
    # never hit -> no group
    assert ga.leaf_groups([_b({"a2", "a3"}, A)], {}, SUBS)["a1"] == frozenset()


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


def _split_run():
    links = [("pub", "r1"), ("r1", "r2"), ("r2", "sa"), ("r2", "sb"), ("sa", "a1"), ("sa", "a2"), ("sb", "b1"),
             ("sb", "b2"), ("r1", "ctrl")]
    subs = ("a1", "a2", "b1", "b2", "ctrl")
    return SimpleNamespace(subs=list(subs), pub="pub",
                           topology={"publishers": {"pub": {}}, "subscribers": {s: {} for s in subs},
                                     "links": [{"from": a, "to": b} for a, b in links]})


def test_window_hop_is_the_deepest_egress_behind_which_exactly_the_expected_sit():
    run = _split_run()
    assert ga.window_hop(run, {"expected": ["a1", "a2"]}) == "r2->sa"
    assert ga.window_hop(run, {"expected": ["a1", "a2", "b1", "b2"]}) == "r1->r2"
    assert ga.window_hop(run, {"expected": ["a1"]}) == "sa->a1"
    assert ga.window_hop(run, {"expected": []}) is None
    assert ga.window_hop(run, {"expected": ["a1"], "hop": "x->y"}) == "x->y"


def test_window_hits_follow_the_router_episode_of_the_stimulated_egress():
    # Two links congested at once: GT1 sees both egresses; the window's own egress decides, not the clients.
    run = _split_run()
    hops = {"r2->sa": [(10.2, 11.5)], "r2->sb": [(10.3, 11.4)], "r1->r2": [(20.0, 21.0)]}
    windows = [{"start": 10, "end": 11, "kind": "cap", "target": "a", "expected": ["a1", "a2"]},
               {"start": 10, "end": 11, "kind": "cap", "target": "b", "expected": ["b1", "b2"]},
               {"start": 20, "end": 21, "kind": "rev", "target": "rev", "expected": []},
               {"start": 30, "end": 31, "kind": "cap", "target": "up", "expected": ["a1", "a2", "b1", "b2"]}]
    bursts = ga.measured_bursts(run, windows, hops)
    assert [b["hit"] for b in bursts] == [["a1", "a2"], ["b1", "b2"], [], []]
    assert [b["hop"] for b in bursts] == ["r2->sa", "r2->sb", None, "r1->r2"]
    # Secondary truth: per-client episodes decide (fq_codel: only the client that queued).
    flows = {"a1": [(10.4, 12.0)], "a2": [], "b1": [(10.1, 10.9)], "b2": []}
    assert [b["hit"] for b in ga.measured_bursts(run, windows, {}, flows)] == [["a1"], ["b1"], [], []]


def _result(events, snapshots, leaves):
    return SimpleNamespace(events=events, snapshots=snapshots, leaves=leaves, final=snapshots[-1])


def test_membership_events_counts_the_flows_own_events():
    events = [{"t0": 10, "members": ["a", "b"]}, {"t0": 20, "members": ["a", "c"]}, {"t0": 30, "members": ["a", "b"]}]
    snaps = [{"t": 11, "flows": {"a": {"member": False, "node": 1}, "b": {"member": False, "node": 1}, "c": {"member": False, "node": None}}},
             {"t": 21, "flows": {"a": {"member": True, "node": 1}, "b": {"member": False, "node": 1}, "c": {"member": False, "node": None}}},
             {"t": 31, "flows": {"a": {"member": True, "node": 1}, "b": {"member": True, "node": 1}, "c": {"member": False, "node": None}}}]
    assert ga.membership_events(_result(events, snaps, {})) == {"a": 2, "b": 2}


def test_private_window_outcomes_solo_silent_grouped():
    events = [{"t0": 10.5, "members": ["a"]}, {"t0": 30.2, "members": ["b", "c"]}, {"t0": 50.0, "members": ["c"]},
              {"t0": 51.0, "members": ["c", "d"]}]
    windows = [{"start": 10, "end": 12, "cell": "private", "expected": ["a"]},
               {"start": 20, "end": 22, "cell": "private", "expected": ["a"]},
               {"start": 30, "end": 32, "cell": "private", "expected": ["b"]},
               {"start": 50, "end": 52, "cell": "private", "expected": ["c"]},
               {"start": 60, "end": 62, "cell": "shared", "expected": ["a", "b"]}]
    assert ga.private_window_outcomes(_result(events, [{}], {}), windows) == {"n": 4, "solo": 1, "silent": 1, "grouped": 2}


def test_confirmed_leaves_report_members_of_confirmed_leaves_only():
    leaves = {1: {"kind": "leaf", "confirmed": True, "members": ["a", "b", "c"]},
              2: {"kind": "leaf", "confirmed": False, "members": ["d", "e"]},
              3: {"kind": "leaf", "confirmed": True, "members": ["f", "g"]}}
    final = {"t": 1, "flows": {f: {"member": f != "c", "node": 1 if f in "abc" else 2 if f in "de" else 3}
                               for f in "abcdefg"}}
    assert set(ga.confirmed_leaves(_result([], [final], leaves))) == {frozenset("ab"), frozenset("fg")}


def test_sessions_of_names_later_sessions_with_at():
    run = SimpleNamespace(topology={"subscribers": {"sub-a": {}, "sub-b": {}, "sub-a@2": {}, "sub-ctrl": {}}},
                          scenario={"events": [{"type": "leave", "subscriber": "sub-a", "at_s": 100},
                                               {"type": "join", "subscriber": "sub-a", "at_s": 130},
                                               {"type": "join", "subscriber": "sub-b", "at_s": 60},
                                               {"type": "link", "at_s": 5}]})
    assert ga.sessions_of(run) == {"sub-a": (0.0, 100), "sub-a@2": (130, None), "sub-b": (60, None), "sub-ctrl": (0.0, None)}


def test_session_run_aliases_sessions_into_the_topology(tmp_path):
    import yaml
    (tmp_path / "publishers" / "pub").mkdir(parents=True)
    for f in ("sub-a", "sub-a@2", "sub-b"):
        (tmp_path / "publishers" / "pub" / f"{f}-acks.csv").write_text("mono_us\n")
    (tmp_path / "topology.yaml").write_text(yaml.safe_dump({
        "publishers": {"pub": {}}, "subscribers": {"sub-a": {"rate_kbps": 1000}, "sub-b": {"rate_kbps": 2500}},
        "links": [{"from": "pub", "to": "router"}, {"from": "router", "to": "switch"},
                  {"from": "switch", "to": "sub-a"}, {"from": "switch", "to": "sub-b"}]}))
    (tmp_path / "scenario.yaml").write_text(yaml.safe_dump({"duration_s": 100, "routers": {"router": {"aqm": "pfifo"}},
                                                             "events": []}))
    (tmp_path / "events.csv").write_text("event,at_s,applied_s,applied_mono_ns,applied_unix_ns,target,detail,label,status\n"
                                         "epoch,0,0,1000000000,2000000000,,,,applied\n")
    run = ga.load_run(tmp_path)
    assert isinstance(run, ga.SessionRun) and run.subs == ["sub-a", "sub-b", "sub-a@2"]
    assert run.sid_of["sub-a@2"] == "sub-a" and run.topology["subscribers"]["sub-a@2"]["rate_kbps"] == 1000
    assert {"from": "switch", "to": "sub-a@2"} in run.topology["links"]
    assert run.sender_file("sub-a@2", "acks").name == "sub-a@2-acks.csv"
