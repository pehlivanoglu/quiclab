"""SETS v1 (frozen 2026-11-15, grouping/FREEZE-sets-v1.md): engine behaviour, the synthetic scenarios, order
independence, and a replay of the frozen configuration on v3 runs against the Step 9 / Step 10 values
(skipped when the run folders are not present; scripts/sets_replay.py check replays all 34 runs)."""

from __future__ import annotations

import json
import random
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from grouping import Config, FlowMeta, ObsSample, Onset, SetsEngine, synth  # noqa: E402
from grouping import sets as S  # noqa: E402
from grouping.sets_engine import replay_records  # noqa: E402

EXACT_CFG = Config(delta=0.03, hold=0.1)


def feed(eng, flows, onsets, until):
    for f in flows:
        eng.on_meta(FlowMeta(f, 0.02, False, 1e6))
    pending = sorted(onsets, key=lambda x: x[1])
    t = 0.0
    while t <= until:
        for f in flows:
            eng.on_obs(ObsSample(f, t, True, False))
        while pending and pending[0][1] <= t:
            f, to = pending.pop(0)
            eng.on_onset(Onset(f, to + 0.01, to + 0.01))
        eng.tick(t)
        t = round(t + eng.cfg.obs_window, 6)
    eng.finish()


def leaves_of(truth):
    acc = {}
    for f, v in truth["flows"].items():
        acc.setdefault(v["access_end"], set()).add(f)
    return acc


def run_scenario(sc, profile, seed):
    recs, truth = synth.generate(synth.SCENARIOS[sc](), synth.PROFILES[profile], seed)
    return replay_records(recs, synth.config_for(synth.PROFILES[profile])), truth


# ── engine behaviour ────────────────────────────────────────────────────

def test_event_formation_is_ecg_and_only_sets_of_two_are_stored() -> None:
    eng = SetsEngine(EXACT_CFG, exclude={"ctrl"})
    # one event {a, b, ctrl}, one solo event {c}, one event {a, b} again
    feed(eng, ["a", "b", "c", "ctrl"], [("a", 1.0), ("b", 1.01), ("ctrl", 1.0), ("c", 3.0), ("a", 5.0), ("b", 5.02)], 7.0)
    assert [e["members"] for e in eng.events] == [["a", "b"], ["c"], ["a", "b"]]
    assert eng.table == Counter({frozenset({"a", "b"}): 2})
    g = eng.groups(2)
    assert [(x.members, x.support, x.jaccard) for x in g] == [(("a", "b"), 2, 1.0)]
    assert eng.groups(3) == []


def test_no_decay_nothing_is_forgotten() -> None:
    eng = SetsEngine(EXACT_CFG)
    feed(eng, ["a", "b"], [("a", 1.0), ("b", 1.0), ("a", 3.0), ("b", 3.0)], 4.0)
    before = Counter(eng.table)
    eng.tick(10_000.0)
    assert eng.table == before and len(eng.groups(2)) == 1


def test_fragment_missing_two_is_absorbed_and_counts_toward_its_set() -> None:
    # {a, b} is seen once: not a group at K_EST, assigned to {a, b, c, d} -> m > 0 -> q(4, m) = 2 -> absorbed
    t = Counter({frozenset("abcd"): 6, frozenset("ab"): 1})
    assert S.estimate_m(t)[0] > 0
    g = S.groups(t, 2)
    assert [x.members for x in g] == [("a", "b", "c", "d")]
    assert g[0].support == 7 and 0.9 < g[0].jaccard < 1.0


def test_extra_flow_rule_lets_a_superset_count_toward_a_fragment() -> None:
    # Frozen property (EXTRA = 1): an observation with one flow more counts toward the smaller set, so a
    # fragment seen once is reported with its parent's support (the "true set minus clients" spurious groups)
    t = Counter({frozenset("abcd"): 6, frozenset("abc"): 1})
    g = {x.members: x.support for x in S.groups(t, 2)}
    assert g == {("a", "b", "c"): 7, ("a", "b", "c", "d"): 6}


def test_tree_is_inclusion_order() -> None:
    gs = [S.Group(("a", "b"), 3, 1.0), S.Group(("c", "d"), 3, 1.0), S.Group(("a", "b", "c", "d"), 3, 1.0)]
    tr = S.tree(gs)
    assert tr[("a", "b")] == ("a", "b", "c", "d") and tr[("c", "d")] == ("a", "b", "c", "d") and tr[("a", "b", "c", "d")] is None


def test_memberships_list_nested_groups_smallest_first() -> None:
    eng = SetsEngine(EXACT_CFG)
    eng.table.update({frozenset("ab"): 3, frozenset("cd"): 3, frozenset("abcd"): 3})
    assert [g.members for g in eng.memberships("a", 2)] == [("a", "b"), ("a", "b", "c", "d")]


def test_matching_rule_extra_and_quantile() -> None:
    cfg = S.FROZEN
    assert S.qmiss(4, 0.0, cfg) == 0                       # m = 0: no missing flow allowed
    assert S.qmiss(4, 0.0714, cfg) == 2                    # Binomial(4, 0.0714): 0.99 quantile is 2
    assert S.qmiss(16, 0.15, cfg) == 6
    # {a,b,c,d,e} (one extra flow) counts toward {a,b,c,d}; {a,b,c,d,e,f} (two extra) does not
    t = Counter({frozenset("abcd"): 5, frozenset("abcde"): 1, frozenset("abcdef"): 1})
    g = {x.members: x.support for x in S.groups(t, 2)}
    assert g[("a", "b", "c", "d")] == 6


def test_extraction_at_k2_and_k3_and_mean_jaccard() -> None:
    t = Counter({frozenset("ab"): 2, frozenset("cde"): 3, frozenset("cd"): 1})
    k2 = {x.members: (x.support, round(x.jaccard, 4)) for x in S.groups(t, 2)}
    k3 = {x.members for x in S.groups(t, 3)}
    assert ("a", "b") in k2 and k2[("a", "b")] == (2, 1.0)
    assert ("a", "b") not in k3 and ("c", "d", "e") in k3
    # mean Jaccard of {c,d,e}: 3 x 1.0 plus, when {c,d} counts toward it, 1 x 2/3
    sup, jac = k2[("c", "d", "e")]
    assert (sup, jac) in ((3, 1.0), (4, round((3 + 2 / 3) / 4, 4)))


def test_smallest_group_and_parent() -> None:
    t = Counter({frozenset("ab"): 3, frozenset("cd"): 3, frozenset("abcd"): 3})
    gs = S.groups(t, 2)
    assert S.smallest_group(gs, "a").members == ("a", "b")
    assert S.smallest_group(gs, "z") is None
    par = {g.members: g.parent for g in gs}
    assert par[("a", "b")] == ("a", "b", "c", "d") and par[("a", "b", "c", "d")] is None


def test_crossing_filter_off_by_default_and_on_drops_the_crossing_set() -> None:
    # {a,b,c,d} and {e,f,g,h} recur; {c,d,e,f} crosses both (two flows off each, so it matches neither)
    # and is dropped by the filter: it takes part in more crossings
    t = Counter({frozenset("abcd"): 4, frozenset("efgh"): 4, frozenset("cdef"): 3})
    off = {g.members for g in S.groups(t, 2)}
    on = {g.members for g in S.groups(t, 2, crossing=True)}
    cross = ("c", "d", "e", "f")
    assert cross in off and cross not in on and {("a", "b", "c", "d"), ("e", "f", "g", "h")} <= on
    assert S.FROZEN.crossing is False


def test_config_lists_every_constant_with_a_tag() -> None:
    names = {n for n, _, _ in S.FROZEN.constants()}
    assert {"q", "extra", "m_tol", "m_iters", "k_est", "min_set", "crossing", "exclude", "event.delta",
            "event.delta_max", "event.hold", "event.align_mode", "event.obs_window", "event.in_episode_rule"} <= names
    vals = {n: (v, tag) for n, v, tag in S.FROZEN.constants()}
    assert vals["event.delta"][0] == 0.150 and vals["event.delta_max"][0] == 0.300 and vals["event.hold"][0] == 1.0
    assert all(tag for _, _, tag in S.FROZEN.constants())
    assert S.SetsConfig.from_dict(S.FROZEN.to_dict()) == S.FROZEN


def test_reading_does_not_change_state_and_dump_restore_roundtrip(tmp_path) -> None:
    eng, _ = run_scenario("S4", "realistic", 0)
    before = Counter(eng.table)
    g1 = eng.groups(2)
    eng.groups(3), eng.tree(2), eng.smallest_group("f1", 2), eng.snapshot()
    assert eng.table == before and eng.groups(2) == g1
    p = tmp_path / "state.json"
    eng.save(p)
    back = SetsEngine.load(p)
    assert back.table == eng.table and back.scfg == eng.scfg
    for k in (2, 3):
        assert back.groups(k) == eng.groups(k)


@pytest.mark.parametrize("seed", range(20))
def test_order_independence_random_sequences(seed) -> None:
    rng = random.Random(seed)
    flows = [f"f{i}" for i in range(rng.randint(4, 30))]
    groups = [rng.sample(flows, rng.randint(2, min(10, len(flows)))) for _ in range(rng.randint(1, 6))]
    obs = []
    for _ in range(rng.randint(5, 80)):
        g = rng.choice(groups)
        o = [f for f in g if rng.random() > 0.15] + ([rng.choice(flows)] if rng.random() < 0.05 else [])
        if len(set(o)) >= 2:
            obs.append(frozenset(o))
    ref = {(k, c): S.groups(Counter(obs), k, crossing=c) for k in (2, 3) for c in (False, True)}
    for i in range(5):
        o = list(obs) if i == 0 else obs[::-1] if i == 1 else rng.sample(obs, len(obs))
        t = Counter()
        for x in o:
            t[x] += 1
        for (k, c), r in ref.items():
            assert S.groups(t, k, crossing=c) == r


# ── synthetic scenarios (properties that hold on every seed tested) ─────

@pytest.mark.parametrize("profile", ["exact", "realistic"])
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_s1_one_leaf(profile, seed) -> None:
    eng, truth = run_scenario("S1", profile, seed)
    for k in (2, 3):
        assert {frozenset(g.members) for g in eng.groups(k)} == {frozenset({"f1", "f2", "f3"})}


@pytest.mark.parametrize("profile", ["exact", "realistic"])
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_s2_independent_links_form_no_group(profile, seed) -> None:
    eng, _ = run_scenario("S2", profile, seed)
    assert eng.groups(2) == []


@pytest.mark.parametrize("profile", ["exact", "realistic"])
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_s3_shared_leaf_despite_private_resource(profile, seed) -> None:
    eng, truth = run_scenario("S3", profile, seed)
    gs = {frozenset(g.members) for g in eng.groups(2)}
    assert frozenset(leaves_of(truth)["A"]) in gs


@pytest.mark.parametrize("profile", ["exact", "realistic"])
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_s4_both_leaves_under_one_aggregation(profile, seed) -> None:
    # every leaf has a group with F1 >= 0.8 (realistic seed 1: leaf A is held as {f2, f3})
    eng, truth = run_scenario("S4", profile, seed)
    for k in (2, 3):
        gs = [set(g.members) for g in eng.groups(k)]
        for v in leaves_of(truth).values():
            assert max(2 * len(g & v) / (len(g) + len(v)) for g in gs) >= 0.8


@pytest.mark.parametrize("profile", ["exact", "realistic"])
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_s6_three_level_tree_leaves(profile, seed) -> None:
    # at least two of the four leaves exactly and every leaf with F1 >= 0.6 (exact seed 0: leaf A2 is only
    # seen inside its aggregation set {f1..f6})
    eng, truth = run_scenario("S6", profile, seed)
    gs = [set(g.members) for g in eng.groups(2)]
    lv = list(leaves_of(truth).values())
    assert sum(v in gs for v in lv) >= 2
    assert all(max(2 * len(g & v) / (len(g) + len(v)) for g in gs) >= 0.6 for v in lv)


@pytest.mark.parametrize("sc", ["S1", "S3", "S4", "S5", "S6"])
def test_output_invariants(sc) -> None:
    eng, _ = run_scenario(sc, "realistic", 0)
    for k in (2, 3):
        gs = eng.groups(k)
        for g in gs:
            assert frozenset(g.members) in eng.table          # a group is an observed set
            assert g.support >= k and 0 < g.jaccard <= 1
        tr = S.tree(gs)
        for child, parent in tr.items():
            assert parent is None or set(child) < set(parent)


# ── order independence ──────────────────────────────────────────────────

@pytest.mark.parametrize("sc", ["S4", "S6"])
def test_order_independence(sc) -> None:
    eng, _ = run_scenario(sc, "realistic", 1)
    obs = [frozenset(e["members"]) for e in eng.events if e["stored"]]
    orders = {"recorded": obs, "reversed": obs[::-1]}
    for i in range(3):
        o = list(obs)
        random.Random(i).shuffle(o)
        orders[f"random {i}"] = o
    ref = {k: S.groups(Counter(obs), k) for k in (2, 3)}
    for name, o in orders.items():
        t = Counter()
        for s in o:
            t[s] += 1
        for k in (2, 3):
            assert S.groups(t, k) == ref[k], name
            assert S.tree(S.groups(t, k)) == S.tree(ref[k]), name


# ── replay of the frozen configuration on v3 runs ───────────────────────

FIXTURE = ROOT / "tests" / "data" / "sets_v1_expected.json"
KDIR = ROOT / ".runs" / "2026-11-14_1818_v3"
REPLAY_RUNS = ["v3-C7-hhier-s030-pfifo-r1", "v3-C9-hdepth-tree16-pfifo-r2", "v3-C11-huneven-uneven-codel-r2",
               "v3-M8-hhier-mixab-mixab-r1"]


@pytest.mark.skipif(not KDIR.exists(), reason="v3 run folders not present")
@pytest.mark.parametrize("run", REPLAY_RUNS)
def test_order_independence_recorded_v3_sequences(run) -> None:
    from grouping.sets_engine import replay_log
    gdir = KDIR / run / "grouping-d150-v2-owd"
    eng = replay_log(gdir / "onsets.jsonl", Config.from_dict(json.loads((gdir / "metrics.json").read_text())["config"]),
                     exclude={"sub-ctrl"})
    obs = [frozenset(e["members"]) for e in eng.events if e["stored"]]
    rng = random.Random(7)
    for o in (obs[::-1], rng.sample(obs, len(obs)), rng.sample(obs, len(obs)), rng.sample(obs, len(obs))):
        t = Counter()
        for x in o:
            t[x] += 1
        for k in (2, 3):
            for c in (False, True):
                assert S.groups(t, k, crossing=c) == eng.groups(k, crossing=c)


@pytest.mark.skipif(not KDIR.exists(), reason="v3 run folders not present")
@pytest.mark.parametrize("run", REPLAY_RUNS)
def test_replay_reproduces_step9_step10(run) -> None:
    import sets_replay
    exp = json.loads(FIXTURE.read_text())[run]
    got = sets_replay.replay_run((run, exp, str(KDIR)))
    assert sets_replay.compare(exp, got) == []
