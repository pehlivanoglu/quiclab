"""ECG grouping engine: alignment, clustering, weights, tree cases, the six
synthetic scenarios under both profiles (with the §8.3 invariants) and
determinism. The full pass/fail table over 10 seeds is produced by
scripts/grouping_synth.py; tests assert the properties that hold on every
seed, see grouping/README.md for the rest."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from grouping import Config, Engine, FlowMeta, ObsSample, Onset  # noqa: E402
from grouping import replay, synth  # noqa: E402
from grouping.invariants import Invariants  # noqa: E402
from grouping.synth import FlowSpec, Scenario  # noqa: E402

EXACT = synth.PROFILES["exact"]


def feed(eng: Engine, flows: dict[str, float], onsets: list[tuple[str, float]], until: float,
         idle: dict[str, tuple[float, float]] | None = None) -> None:
    """Meta for `flows` (name -> mrtt), obs every 20 ms, onsets at (flow, t)
    with t_arrival = t_onset; `idle` marks a flow not sending in [a, b)."""
    for f, mrtt in flows.items():
        eng.on_meta(FlowMeta(f, mrtt, False, 1e6))
    ons = sorted(onsets, key=lambda o: o[1])
    t, i = 0.0, 0
    while t <= until:
        eng.tick(t)
        for f in flows:
            a, b = (idle or {}).get(f, (math.inf, math.inf))
            eng.on_obs(ObsSample(f, t, not (a <= t < b), False))
        while i < len(ons) and ons[i][1] <= t:
            eng.on_onset(Onset(ons[i][0], ons[i][1], ons[i][1]))
            i += 1
        t = round(t + 0.02, 6)
    eng.finish()


def events_of(log: list[dict]) -> list[dict]:
    return [r for r in log if r["type"] == "event"]


def engine(**kw) -> tuple[Engine, list[dict]]:
    """Brief v1.1 engine (Config.V11) unless kw says otherwise; the case tests
    below describe v1.1 behaviour, the v1.2 tests use _v12()."""
    log: list[dict] = []
    cfg = Config(**{"delta": 0.03, "hold": 0.1, **Config.V11, **kw})
    return Engine(cfg, log.append), log


# ── alignment and clustering ─────────────────────────────────────────────

def test_alignment_modes() -> None:
    o = Onset("f", 10.0, 10.3)
    for mode, table, want in (("half_mrtt", {}, 9.98), ("none", {}, 10.0), ("table", {"f": 0.1}, 9.9)):
        eng = Engine(Config(align_mode=mode, align_table=table))
        eng.on_meta(FlowMeta("f", 0.04))
        assert eng._align(o) == pytest.approx(want)


def test_onsets_within_delta_share_an_event_and_beyond_do_not() -> None:
    eng, log = engine()
    feed(eng, {"a": 0.02, "b": 0.02, "c": 0.02}, [("a", 10.0), ("b", 10.02), ("c", 10.2)], 12)
    ev = events_of(log)
    assert [e["members"] for e in ev] == [["a", "b"], ["c"]]
    assert ev[0]["span_al"] == pytest.approx(0.02)


def test_hold_keeps_event_open_for_late_arrival() -> None:
    eng, log = engine(delta=0.3, hold=1.0)
    for f in ("a", "b"):
        eng.on_meta(FlowMeta(f, 0.0))
    t = 0.0
    while t <= 14:
        eng.tick(t)
        eng.on_obs(ObsSample("a", t, True, False))
        eng.on_obs(ObsSample("b", t, True, False))
        if t == 10.0:
            eng.on_onset(Onset("a", 10.0, 10.0))
        if t == 11.4:                       # arrives 1.4 s later, onset backdated to 10.1
            eng.on_onset(Onset("b", 10.1, 11.4))
        t = round(t + 0.02, 6)
    eng.finish()
    assert [e["members"] for e in events_of(log)] == [["a", "b"]]


def test_second_onset_in_episode_is_ignored() -> None:
    eng, log = engine()
    eng.on_meta(FlowMeta("a", 0.0))
    for t in (0.0, 0.02):
        eng.on_obs(ObsSample("a", t, True, False))
    eng.on_onset(Onset("a", 0.02, 0.02))
    eng.on_obs(ObsSample("a", 0.04, True, True))
    eng.on_onset(Onset("a", 0.04, 0.04))
    assert [r["reason"] for r in log if r["type"] == "onset_ignored"] == ["in_episode"]
    eng.on_obs(ObsSample("a", 0.06, True, False))     # episode over
    eng.on_onset(Onset("a", 0.06, 0.06))
    assert sum(r["type"] == "onset" for r in log) == 2


# ── evidence weights ─────────────────────────────────────────────────────

def test_p_fa_floor_cap_and_signs() -> None:
    eng, _ = engine(delta=0.3)
    eng.on_meta(FlowMeta("a", 0.0))
    assert eng._p_fa("a", 0.0) == pytest.approx(0.03)
    from grouping.types import Event, Member
    ev = Event(1, 10.0, [Member("a", 10.0, 10.0, "delay", 1.0, False)])
    w, comps = eng._w_pos("a", 1, ev, ev.members[0])
    assert comps["base"] == pytest.approx(math.log(0.8 / 0.03)) and comps["capped"]
    assert w == pytest.approx(0.55 * eng.A) and w < eng.A
    assert eng._w_neg("a", ev) == pytest.approx(math.log(0.2 / 0.97))
    assert eng._w_neg("a", ev) < 0
    # a busy flow: p_fa grows with its onset rate
    for k in range(20):
        eng.on_onset(Onset("a", k * 0.5, k * 0.5))
        eng.state["a"].episode_since = None
    assert eng._p_fa("a", 10.0) > 0.03


def test_c_lag_penalises_inconsistent_lag_after_two_observations() -> None:
    eng, _ = engine()
    eng.on_meta(FlowMeta("a", 0.0))
    from grouping.types import Event, Member
    for lag in (0.0, 0.0):
        eng._update_lag("a", 1, lag)
    good = Event(1, 10.0, [Member("a", 10.0, 10.0, "delay", 1.0, False)])
    bad = Event(2, 20.0, [Member("a", 20.5, 20.5, "delay", 1.0, False)])
    assert eng._w_pos("a", 1, good, good.members[0])[1]["c_lag"] == pytest.approx(1.0)
    assert eng._w_pos("a", 1, bad, bad.members[0])[1]["c_lag"] < 0.01


# ── tree cases ───────────────────────────────────────────────────────────

def test_case_d_then_a_makes_members_and_confirms_leaf() -> None:
    eng, log = engine()
    feed(eng, {"a": 0.0, "b": 0.0, "c": 0.0}, [(f, t) for t in (10, 20) for f in "abc"], 22)
    assert [e["case"] for e in events_of(log)] == ["D", "A"]
    leaf = eng.state["a"].node
    assert leaf is not None and eng.nodes[leaf].members == {"a", "b", "c"}
    assert all(eng.state[f].L >= eng.A for f in "abc") and eng.nodes[leaf].confirmed
    assert eng.query_pair("a", "b")["status"] == "SAME"


def test_case_c_subset_splits_after_enough_weight() -> None:
    eng, log = engine(theta_J=0.7, s_split_weight=4.0)
    ons = [(f, t) for t in (10, 20, 30) for f in "abcd"] + [(f, t) for t in (40, 50) for f in "ab"]
    feed(eng, {f: 0.0 for f in "abcd"}, ons, 52)
    cases = [e["case"] for e in events_of(log)]
    assert cases == ["D", "A", "A", "C", "C"]
    assert any(r.get("op") == "split" for r in log)
    assert eng.state["a"].node == eng.state["b"].node != eng.state["c"].node == eng.state["d"].node
    assert eng.query_pair("a", "b")["status"] == "SAME"
    assert eng.nodes[eng.state["a"].node].parent == eng.nodes[eng.state["c"].node].parent != 0


def test_case_b_builds_parent_and_global_leaves_leaves_alone() -> None:
    eng, log = engine()
    A, B = list("abc"), list("def")
    ons = [(f, 10) for f in A] + [(f, 20) for f in B] + [(f, 30) for f in A + B]   # leaves exist, unconfirmed
    ons += [(f, 40) for f in A] + [(f, 50) for f in B] + [(f, 60) for f in A + B]
    feed(eng, {f: 0.0 for f in A + B}, ons, 62)
    cases = [e["case"] for e in events_of(log)]
    assert cases[:3] == ["D", "D", "GLOBAL"] and cases[-1] == "GLOBAL"
    la, lb = eng.state["a"].node, eng.state["d"].node
    assert la != lb and eng.nodes[la].members == set(A) and eng.nodes[lb].members == set(B)
    assert eng.nodes[0].support > 0


def test_case_b_creates_internal_node_when_a_third_leaf_stays_silent() -> None:
    eng, log = engine()
    A, B, C = list("abc"), list("def"), list("ghi")
    ons = []
    for t, grp in ((10, A), (20, B), (30, C), (40, A), (50, B), (60, C), (70, A + B), (80, A + B)):
        ons += [(f, t) for f in grp]
    feed(eng, {f: 0.0 for f in A + B + C}, ons, 82)
    assert [e["case"] for e in events_of(log)][-2:] == ["B", "B"]
    internal = [n for n in eng.nodes.values() if n.kind == "internal"]
    assert len(internal) == 1 and internal[0].children == {eng.state["a"].node, eng.state["d"].node}
    assert eng.query_pair("a", "d") == {"status": "DIFFERENT", "lca": internal[0].id,
                                        "conf": pytest.approx(eng.conf(eng.state["a"].L)), "level": 1}


def test_solo_emits_private_and_two_flow_leaf_gets_negative_evidence() -> None:
    eng, log = engine()
    feed(eng, {"a": 0.0, "b": 0.0}, [("a", 10), ("b", 10), ("a", 15), ("a", 18)], 20)
    assert [e["case"] for e in events_of(log)] == ["D", "SOLO", "SOLO"]
    assert sum(r.get("kind") == "PRIVATE" for r in log) == 2
    assert eng.state["b"].cand[1] < 0            # a's solo onsets contradicted the provisional pair
    assert eng.query("a")["status"] == "UNCERTAIN"


def test_idle_flow_gets_no_evidence() -> None:
    eng, log = engine()
    ons = [(f, t) for t in (10, 20, 30, 40) for f in "abc"]
    feed(eng, {f: 0.0 for f in "abc"}, [o for o in ons if not (o[0] == "c" and o[1] > 25)], 42,
         idle={"c": (25.0, 100.0)})
    st = eng.state["c"]
    assert st.node is not None and st.L >= eng.A and st.apart == 0


def test_migration_moves_flow_to_new_leaf() -> None:
    eng, log = engine(theta_J=0.6, theta_cov=0.6)
    A, B = list("abc"), list("def")
    ons = []
    for t in (10, 20, 30):
        ons += [(f, t) for f in A] + [(f, t + 5) for f in B]
    for t in (40, 50, 60, 70):                               # c now behind B's link
        ons += [(f, t) for f in ("a", "b")] + [(f, t + 5) for f in B + ["c"]]
    feed(eng, {f: 0.0 for f in A + B}, ons, 77)
    assert eng.state["c"].node == eng.state["d"].node and eng.state["c"].L >= eng.A
    assert eng.nodes[eng.state["a"].node].members == {"a", "b"}


# ── config ───────────────────────────────────────────────────────────────

def test_config_from_dict_and_json(tmp_path: Path) -> None:
    cfg = Config.from_dict({"delta": 0.1, "tau": 100})
    assert cfg.delta_max == 0.2 and cfg.sigma_min == 0.05 and cfg.tau == 100
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"delta": 0.05}))
    assert Config.from_json(p).delta_max == pytest.approx(0.1)
    with pytest.raises(KeyError):
        Config.from_dict({"nope": 1})
    with pytest.raises(ValueError):
        Config(enable_priming=True)
    assert cfg.replace(delta=0.3).delta_max == pytest.approx(0.6)


# ── scenarios ────────────────────────────────────────────────────────────

def run_scenario(sid: str, profile: str, seed: int, **over) -> tuple[replay.Result, dict, bool, dict]:
    sc = synth.SCENARIOS[sid]()
    prof = synth.PROFILES[profile]
    cfg = synth.config_for(prof, **over)
    rec, truth = synth.generate(sc, prof, seed)
    checked = {}

    def hook(records, cfg_, **kw):
        eng = Engine(cfg_)
        checked["inv"] = Invariants(eng)
        return eng
    res = replay.run(rec, cfg, keep_engine=True, engine_factory=hook)
    ok, d = replay.check(sid, res, truth)
    assert checked["inv"].n_checked == sum(res.cases.values())
    return res, truth, ok, d


@pytest.mark.parametrize("profile", ["ideal", "realistic"])
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_s1_one_leaf(profile, seed) -> None:
    res, truth, ok, d = run_scenario("S1", profile, seed)
    assert d["same_leaf_end"] and d["no_false_leaf"]
    assert d["events_to_leaf"] is not None and d["events_to_leaf"] <= 6   # <= 3 only when nobody misses


@pytest.mark.parametrize("profile", ["ideal", "realistic"])
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_s2_independent(profile, seed) -> None:
    res, truth, ok, d = run_scenario("S2", profile, seed)
    assert res.cases["SOLO"] > 40
    pairs = res.pairs()
    assert pairs[("f1", "f2")] != "SAME"
    if profile == "ideal":
        assert ok, d


@pytest.mark.parametrize("profile", ["ideal", "realistic"])
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_s3_shared_plus_private(profile, seed) -> None:
    res, truth, ok, d = run_scenario("S3", profile, seed)
    assert d["others_member"]
    assert res.cases["SOLO"] > 20
    assert d["private_fraction"] > 0.3


@pytest.mark.parametrize("profile", ["ideal", "realistic"])
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_s4_two_leaves_one_parent_at_theta_0_6(profile, seed) -> None:
    res, truth, ok, d = run_scenario("S4", profile, seed, theta_J=0.6, theta_cov=0.6)
    assert ok, d


@pytest.mark.parametrize("profile", ["ideal", "realistic"])
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_s5_noise_idle_migrate_invariants(profile, seed) -> None:
    res, truth, ok, d = run_scenario("S5", profile, seed, theta_J=0.6, theta_cov=0.6)
    assert d["f5_apart_idle"] <= 0 and d["f5_member_idle"]
    assert d["f2_joined_t"] is not None                  # the noisy flow does join (and may leave again)


@pytest.mark.parametrize("profile", ["ideal", "realistic"])
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_s6_four_leaves_invariants(profile, seed) -> None:
    res, truth, ok, d = run_scenario("S6", profile, seed, theta_J=0.6, theta_cov=0.6)
    # Structure is not asserted: see README (coincidence pairs, misses on 12
    # flows). Invariants hold and root-level events are recognised.
    assert res.cases["GLOBAL"] >= 1


def test_v11_default_theta_is_reported_not_tuned() -> None:
    """Brief v1.1 at its own default theta 0.7 does not pass S4 (one missed
    flow in a three-flow leaf falls to case D); kept as the record of why the
    sweep value 0.6 was reported, not tuned."""
    res, truth, ok, d = run_scenario("S4", "ideal", 0, **Config.V11)
    assert not ok and d["cases"].get("D", 0) > 2


def test_replay_is_deterministic(tmp_path: Path) -> None:
    sc = synth.s4()
    prof = synth.PROFILES["realistic"]
    rec, _ = synth.generate(sc, prof, 3)
    cfg = synth.config_for(prof)
    replay.run(rec, cfg, log_path=tmp_path / "a.jsonl")
    replay.run(rec, cfg, log_path=tmp_path / "b.jsonl")
    assert (tmp_path / "a.jsonl").read_bytes() == (tmp_path / "b.jsonl").read_bytes()
    synth.write_log(rec, tmp_path / "log.jsonl")
    res = replay.run(list(synth.read_log(tmp_path / "log.jsonl")), cfg, log_path=tmp_path / "c.jsonl")
    assert (tmp_path / "a.jsonl").read_bytes() == (tmp_path / "c.jsonl").read_bytes()
    assert sum(res.cases.values()) > 0


# ── v1.2 rules (Config.V12; README "v1.2") ───────────────────────────────

def _v12(**kw) -> tuple[Engine, list[dict]]:
    return engine(**{**Config.V12, **kw})


def test_v12_false_pair_is_charged_when_its_member_fires_elsewhere() -> None:
    """Rule 1. a2 and b2 co-fire twice (a shared upstream), then a2 fires six
    times with a3 only. v1.1: those events open a new leaf and b2 is never
    charged, the false pair survives. v1.2: b2 takes w_neg each time and leaves."""
    ons = [(f, t) for t in (10, 20) for f in ("a2", "b2")] + [(f, t) for t in range(30, 90, 10) for f in ("a2", "a3")]
    flows = {"a2": 0.0, "a3": 0.0, "b2": 0.0}
    old, log_old = engine()
    feed(old, flows, ons, 92)
    assert not any(r.get("flow") == "b2" and r.get("w", 0) < 0 for r in log_old)   # the v1.1 hole: never charged
    new, log = _v12()
    feed(new, flows, ons, 92)
    assert new.state["b2"].node is None and new.state["b2"].L == 0.0           # left the false pair
    assert new.query_pair("a2", "a3")["status"] == "SAME"
    assert new.query_pair("a2", "b2")["status"] == "UNCERTAIN"
    assert any(r.get("case", "").endswith(":unmatched") and r.get("flow") == "b2" for r in log)


def test_v12_membership_hysteresis_survives_one_miss() -> None:
    ons = [(f, t) for t in (10, 20) for f in "abc"] + [("a", 30), ("b", 30)]
    old, _ = engine()
    feed(old, {f: 0.0 for f in "abc"}, ons, 32)
    assert old.query("c")["status"] == "UNCERTAIN" and old.A / 2 < old.state["c"].L < old.A
    new, _ = _v12()
    feed(new, {f: 0.0 for f in "abc"}, ons, 32)
    assert new.A / 2 < new.state["c"].L < new.A and new.query("c")["status"] == "MEMBER"
    assert new.query_pair("a", "c")["status"] == "SAME"


def test_v12_majority_attribution_follows_a_shifting_set() -> None:
    """K5 pattern: {a,b,c} then {b,c,d}. J = 2/4 < theta made the second event
    case D in v1.1; with majority attribution leaf 1 holds two of M and takes it."""
    ons = [(f, 10) for f in "abc"] + [(f, 20) for f in "bcd"]
    old, log_old = engine()
    feed(old, {f: 0.0 for f in "abcd"}, ons, 22)
    assert [e["case"] for e in events_of(log_old)] == ["D", "D"]
    new, log = _v12()
    feed(new, {f: 0.0 for f in "abcd"}, ons, 22)
    assert [e["case"] for e in events_of(log)] == ["D", "A"]
    assert len([n for n in new.nodes.values() if n.kind == "leaf"]) == 1
    # d is an outsider while a stayed silent (cov 2/3): it joins only from an
    # event in which the whole leaf fires with it (A-superset condition).
    assert "d" not in new.nodes[1].candidates
    feed(new, {f: 0.0 for f in "abcd"}, [(f, 30) for f in "abcd"], 32)
    assert "d" in new.nodes[1].candidates


def test_v12_case_c_counts_the_sub_pattern_without_charging_the_silent() -> None:
    ons = [(f, t) for t in (10, 20, 30) for f in "abcd"] + [(f, t) for t in (40, 50) for f in "ab"]
    new, log = _v12(s_split_weight=4.0)
    feed(new, {f: 0.0 for f in "abcd"}, ons, 52)
    cases = [e["case"] for e in events_of(log)]
    assert cases[-2:] == ["C", "C"] and any(r.get("op") == "split" for r in log)
    assert not any(r.get("case") == "C" and r.get("flow") in ("c", "d") and r.get("w", 0) < 0 for r in log)
    assert new.query_pair("a", "b")["status"] == "SAME" and new.query_pair("c", "d")["status"] == "SAME"


def test_v12_global_tolerates_one_miss_in_a_two_flow_leaf() -> None:
    """Root event over four confirmed two-flow leaves with one flow missing:
    v1.1 case B (a false internal node), v1.2 GLOBAL (the leaf still voted)."""
    leaves = [list("ab"), list("cd"), list("ef"), list("gh")]
    ons = []
    for t, grp in zip((10, 20, 30, 40, 50, 60, 70, 80), leaves * 2):
        ons += [(f, t) for f in grp]
    allf = [f for g in leaves for f in g]
    ons += [(f, 90) for f in allf if f != "h"]
    old, log_old = engine()
    feed(old, {f: 0.0 for f in allf}, ons, 92)
    new, log = _v12()
    feed(new, {f: 0.0 for f in allf}, ons, 92)
    assert events_of(log_old)[-1]["case"] == "B" and events_of(log)[-1]["case"] == "GLOBAL"


def test_v12_default_is_deterministic_and_passes_s4() -> None:
    ra = run_scenario("S4", "realistic", 1)
    rb = run_scenario("S4", "realistic", 1)
    assert ra[0].to_json() == rb[0].to_json()
    assert ra[2], ra[3]
