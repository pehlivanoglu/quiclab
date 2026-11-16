"""Suite v4 (scripts/v4_suite.py) and the shared-code additions it needs: sizing of the new
topologies against the spec tables, the campaign matrix, the new stimuli and scenario
types, subscriber paths, BG-ONOFF periods, salvo / pause events. Nothing is emulated."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import v4_suite as v4  # noqa: E402
from quiclab.config.scenario import BgEvent, PauseEvent, SalvoEvent, Scenario, load_scenario  # noqa: E402
from quiclab.config.schema import TopologyConfig, load_topology  # noqa: E402
from quiclab.orchestrator import mininet_backend as mb  # noqa: E402

QTRAFFIC = ROOT / "qvideo" / "build" / "qtraffic"


def topo(kind, point="DEF", **opts):
    s, U = v4.POINTS[point]
    return v4.build4(kind, opts.pop("variant", ""), s, U, 1, opts)


def caps(t):
    return {n: (round(e.cap, 1), round(e.bg, 2)) for n, e in t.egress.items() if e.shaped}


# ---------------------------------------------------------------- sizing (spec 2)

@pytest.mark.parametrize("point,leaf,up", [("DEF", (34.3, 12.02), (68.7, 24.03)), ("EXT", (24.5, 12.02), (49.0, 24.03)),
                                           ("HS50", (20.6, 5.15), (41.2, 10.3))])
def test_split4l_table(point, leaf, up):
    c = caps(topo("split4l", point))
    assert c["a"] == c["b"] == leaf and c["up"] == up


def test_unevenl_and_par():
    c = caps(topo("unevenl"))
    assert [c[x][0] for x in "ABC"] == [24.0, 37.8, 68.7]
    t = topo("unevenl")
    assert not t.egress["up"].shaped and len(t.rates) == 16
    for k in (2, 4, 6):
        t = topo("par", k=k)
        assert sorted(caps(t)) == list("abcdef"[:k]) and set(caps(t).values()) == {(34.3, 12.02)}
        assert not t.egress["up"].shaped
    t = topo("par", k=4, per=8)
    assert caps(t)["a"][0] == 68.7 and len(t.rates) == 32


@pytest.mark.parametrize("n,cap", [(4, 9.8), (8, 19.6), (16, 39.2), (24, 58.9), (32, 78.5), (40, 98.1)])
def test_leafn_table(n, cap):
    assert caps(topo("base", "EXT", **v4.leaf_opts(n)))["main"][0] == cap


def test_leaf16w_and_splitn():
    t = topo("base", "EXT", **v4.leaf_opts(16), delays=v4.LEAF16W_MS)
    d = sorted(t.delays.values())
    assert d[0] == 5.0 and d[-1] == 95.0 and len(set(d)) == 16
    for n in (8, 12):
        t = topo("splitn", "EXT", n=n)
        assert len(t.rates) == 2 * n and t.egress["up"].shaped and set(t.rates.values()) == {500}


def test_hayes_links_and_paths():
    t = topo("hayes")
    c = caps(t)
    assert c == {"L12": (41.2, 16.48), "L34": (20.6, 8.24), "L13": (30.9, 12.36), "L24": (30.9, 12.36),
                 "L14": (30.9, 12.36), "L23": (30.9, 12.36), "L1234": (61.8, 24.72)}
    cfg = TopologyConfig.model_validate(t.topo)
    hop_name = {e.hop: n for n, e in t.egress.items() if e.shaped}
    for sid in t.rates:
        crossed = [hop_name[h] for h in mb._path_hops(cfg, "pub", sid) if h in hop_name]
        assert crossed == v4.hayes_links(sid[:2])
        assert sorted(n for n, e in t.egress.items() if e.shaped and sid in e.clients) == sorted(crossed)
    # every pair of groups shares exactly one stage link, all four share L1234
    sets = [frozenset(g[:2] for g in e.clients) for n, e in t.egress.items() if e.shaped and n != "L1234"]
    assert len(set(sets)) == 6 and all(len(x) == 2 for x in sets)


def test_teacup_point_and_rev():
    t = topo("teacup")
    assert caps(t)["a"][0] == 21.5 and caps(t)["up"][0] == 53.6
    assert t.egress["up"].U == pytest.approx((10.3 + 24.033) / 53.65, abs=1e-3) and t.egress["a"].U == 0.8
    assert set(t.delays.values()) == {45.0}
    t = topo("teacup", variant="rev")
    up = next(c for c in t.links if (c["from"], c["to"]) == ("r1", "r2"))
    assert up["reverse"]["bandwidth_mbps"] == 10.0 and t.rev == ("r2", "r1")


def test_constraints_hold_on_every_new_topology():
    for kind, point, o in (("split4l", "DEF", {}), ("split4l", "HS50", {}), ("unevenl", "DEF", {}), ("par", "DEF", {"k": 6}),
                           ("par", "DEF", {"k": 4, "per": 8}), ("base", "EXT", v4.leaf_opts(40)), ("hayes", "DEF", {}),
                           ("splitn", "EXT", {"n": 12})):
        assert v4.constraint_check4(topo(kind, point, **o), literature=kind == "hayes") == []
    assert v4.constraint_check4(topo("teacup"), literature=True) == []


# ---------------------------------------------------------------- campaign matrix (spec 6)

SPEC_RUNS = {"K1": {"A1": 30, "A2": 30, "A3": 18, "A4": 20, "A5": 15, "A6": 10, "A7": 15, "A8": 10, "A9": 6,
                    "G1": 30, "G2": 6, "G3": 6},
             "K2": {"X1": 9, "X2": 18, "X3": 6, "X4": 2, "X5": 12, "X6": 6, "N1": 8, "N2": 4, "N3": 6, "N4": 12,
                    "N5": 6, "N6": 4, "N7": 4, "N8": 14, "T1": 6, "T2": 12, "T3": 16},
             "K3": {"L1": 6, "L2": 16, "L3": 4, "L4": 6, "L5": 20, "L6": 6, "L7": 6, "L8": 8, "L9": 6, "L10": 2, "L11": 10,
                    "C1": 22, "I1": 16, "M": 58}}


@pytest.mark.parametrize("name", ["K1", "K2", "K3"])
def test_run_counts(name):
    cells = v4.CAMPAIGNS[name](40) if name == "K1" else v4.CAMPAIGNS[name]()
    n = Counter()
    for c in cells:
        n[c.block] += len(c.aqms) * len(c.seeds)
    assert dict(n) == SPEC_RUNS[name]   # C1: spec says 24, its own list gives 22 (README deviation)


def test_top_up_seeds_are_v3_reps():
    cells = {c.block: c for c in v4.k2()}
    assert cells["X1"].seeds == (3, 4, 5) and cells["X1"].point == "EXT" and cells["X1"].kind == "split4"


def test_plan_validates_and_orders_by_seed(tmp_path):
    cells = [c for c in v4.k3() if c.block in ("L7", "L8", "L9", "L11")] + [c for c in v4.k2() if c.block in ("N3", "N4")]
    plans = v4.plan_all(tmp_path, cells, "test")
    for p in plans:
        v4.validate(p)
    seeds = [p.rep for p in plans]
    assert seeds == sorted(seeds)
    assert v4.check_violations(plans) == []


# ---------------------------------------------------------------- stimuli and types

def windows(rtype, t, seed=1, variant=""):
    ev, w, d = v4.plan_type4(rtype, t, seed, variant)
    return ev, w, d


def test_persist_and_fb_episodes():
    t = topo("par", k=4)
    ev, w, d = windows("fbload", t)
    starts = sorted({x["start"] for x in w})
    assert len(starts) == 12 and all(len([x for x in w if x["start"] == s]) == 4 for s in starts)
    assert {x["d"] for x in w} == {30.0} and Counter(x["u"] for x in w) == Counter({u: 8 for u in v4.FB_LEVELS})
    assert all(b - a == pytest.approx(60.0) for a, b in zip(starts, starts[1:]))
    assert {x["stimulus_type"] for x in w} == {"surge"} and {x["kind"] for x in w} == {"persist"}


def test_cold_start():
    t = topo("par", k=4)
    ev, w, d = windows("fbcold", t)
    joins = [e for e in ev if e["type"] == "join"]
    assert d == 45.0 and {x["start"] for x in w} == {0.0} and len(joins) == 16
    assert all(0 < e["at_s"] <= 3.0 for e in joins)


def test_shorttcp_bytes_match_load():
    t = topo("base")
    ev, w, d = windows("sshort", t)
    sal = [e for e in ev if e["type"] == "salvo"]
    assert len(sal) == 9
    for e, x in zip(sal, [x for x in w if x["kind"] == "shorttcp"]):
        target = (x["u"] - 0.5) * t.egress["main"].cap * 1e6 / 8 * 10 / v4.v3.TCP_WIRE
        got = sum(f["bytes"] for f in e["flows"])
        assert got >= target and len(e["flows"]) % v4.SALVO_N == 0
        assert max(f["start_s"] for f in e["flows"]) <= 10.0 + 1e-9
        SalvoEvent.model_validate(e)


def test_shorttcp_rfc():
    t = topo("base")
    ev, w, d = windows("sshortrfc", t)
    sal = [e for e in ev if e["type"] == "salvo"]
    assert d == 300.0 and w == [] and len(sal) == 1
    f = sal[0]["flows"]
    assert all(30e3 <= x["bytes"] <= 50e3 for x in f) and sum(x["start_s"] == 0.0 for x in f) == 2
    assert 200 <= len(f) <= 400   # ~ 10 flows x 300 s / 10 s
    SalvoEvent.model_validate(sal[0])


def test_pause_plan():
    t = topo("base")
    ev, w, d = windows("spause", t)
    p = [x for x in w if x["kind"] == "pause"]
    s = [x for x in w if x["kind"] == "surge"]
    assert len(p) == 6 and len(s) == 18 and {x["target"] for x in p} == set(t.rates)
    assert all(x["start"] == int(x["start"]) for x in p)
    overlap = [x for x in p if any(y["start"] < x["end"] and x["start"] < y["end"] for y in s)]
    assert len(overlap) == 1
    assert sorted({x["d"] for x in p}) != []


def test_sb_nsb_same_timing():
    _, wsb, dsb = windows("sbnsb", topo("base", rates={**v4._low("a"), **v4._low("b")}))
    _, wn, dn = windows("sbnsb", topo("par", k=2))
    assert dsb == dn and len(wn) == 2 * len(wsb) == 36
    assert sorted(x["start"] for x in wsb) == sorted({x["start"] for x in wn})


def test_churn_membership_and_truth():
    t = topo("split4l")
    ev, w, d = windows("hchurn", t)
    mem = [(e["at_s"], e["type"], e["subscriber"]) for e in ev if e["type"] in ("join", "leave")]
    assert (120.0, "join", "a2") in mem and (300.0, "leave", "a4") in mem and (600.0, "join", "a4") in mem
    for x in w:
        if x["start"] < 120:
            assert "a2" not in x["expected"] and "b2" not in x["expected"]
        if 300 < x["start"] < 600:
            assert "a4" not in x["expected"]


def test_conc_fraction():
    t = topo("par", k=2)
    for f, both in ((0.0, 0), (0.25, 10), (0.5, 20), (1.0, 40)):
        _, w, _ = windows("hconc", t, variant=f"f{round(f * 100):03d}")
        events = Counter(x["start"] for x in w)
        assert len(events) == 40 and sum(1 for v in events.values() if v == 2) == both


def test_shift_phases():
    t = topo("split4l")
    _, w, d = windows("hshift", t)
    for x in w:
        i = int(x["cell"].split(":")[0][5:]) - 1
        p0 = v4.WARMUP_S + i * v4.SHIFT_PHASE_S
        assert p0 <= x["start"] and x["end"] <= p0 + v4.SHIFT_PHASE_S
        assert x["target"] in v4.SHIFT_ORDER[i].split("+")
    _, w, _ = windows("hshift", t, variant="sustained")
    assert {x["d"] for x in w} == {40.0} and len(w) == 12


def test_onoff_background():
    t = topo("split4l")
    ev = v4.background4(t, "onoff", 1, 600.0)
    per = Counter(e["route"] for e in ev)
    assert per == {"bg-up": 10, "bg-a": 5, "bg-b": 5}
    for e in ev:
        BgEvent.model_validate(e)
    up = [e for e in ev if e["route"] == "bg-up"]
    mean = sum(e["rate_mbps"] * sum(dd for _, dd in e["periods"]) for e in up) / 600 * v4.v3.UDP_WIRE
    assert mean == pytest.approx(t.egress["up"].bg, rel=1e-3)


# ---------------------------------------------------------------- shared code

def test_subscriber_path_validation():
    t = topo("hayes").topo
    TopologyConfig.model_validate(t)
    bad = json.loads(json.dumps(t))
    bad["subscribers"]["g1a"]["path"] = ["pub", "r0", "r1"]
    with pytest.raises(ValueError):
        TopologyConfig.model_validate(bad)


def test_bg_periods_schedule():
    e = BgEvent.model_validate({"at_s": 0, "type": "bg", "id": "x", "route": "r", "duration_s": 10, "rate_mbps": 2,
                                "periods": [[0, 1.5], [4, 2]]})
    assert e.schedule() == [(0.0, 1.5, 2.0), (4.0, 2.0, 2.0)]
    with pytest.raises(ValueError):
        BgEvent.model_validate({"at_s": 0, "type": "bg", "id": "x", "route": "r", "duration_s": 3, "rate_mbps": 2,
                                "periods": [[2, 2]]})


def test_salvo_and_pause_events(tmp_path):
    t = topo("base")
    cfg = TopologyConfig.model_validate(t.topo)
    scen = {"duration_s": 60, "links": t.links, "events": [
        {"at_s": 10, "type": "salvo", "id": "s1", "route": "bg-main", "duration_s": 12, "cc": "cubic",
         "flows": [{"start_s": 0, "bytes": 1000}, {"start_s": 1.5, "bytes": 2000}]},
        {"at_s": 20, "type": "pause", "subscriber": "sub-a", "duration_s": 5}]}
    s = Scenario.model_validate(scen).check_against(cfg)
    assert [e.type for e in s.ppbp()] == ["salvo"] and s.traffic_ids() == ["s1"]
    argv = mb.qtraffic_send_argv(cfg, s, s.events[0], 10**15, tmp_path / "x")
    assert "--process=salvo" in argv and "--proto=tcp" in argv and "--flows=0:1000,1.5:2000" in argv
    assert "--proto=tcp" in mb.qtraffic_recv_argv(cfg, s, s.events[0], tmp_path / "x")
    assert mb.pause_argv(cfg, s, "pub") == ["--pause=sub-a@20+5"]
    bad = dict(scen, events=[{"at_s": 58, "type": "pause", "subscriber": "sub-a", "duration_s": 5}])
    with pytest.raises(ValueError):
        Scenario.model_validate(bad).check_against(cfg)
    PauseEvent.model_validate(scen["events"][1])


def _has_salvo() -> bool:
    if not QTRAFFIC.exists():
        return False
    out = subprocess.run([str(QTRAFFIC), "--helpfull"], capture_output=True, text=True)
    return "salvo" in out.stdout + out.stderr


@pytest.mark.skipif(not _has_salvo(), reason="qtraffic without --process=salvo; rebuild qvideo")
def test_qtraffic_salvo_loopback(tmp_path):
    port = 5600 + int(time.time()) % 300
    recv = subprocess.Popen([str(QTRAFFIC), "--mode=recv", "--proto=tcp", "--bind=127.0.0.1", f"--port={port}",
                             f"--out={tmp_path / 'r'}"])
    try:
        time.sleep(0.3)
        subprocess.run([str(QTRAFFIC), "--mode=send", "--proto=tcp", "--process=salvo", "--bind=127.0.0.1",
                        "--dest=127.0.0.1", f"--port={port}", "--duration_s=1.5",
                        "--flows=0:300000,0.2:700000,0.4:5000", f"--out={tmp_path / 's'}"], check=True, timeout=10)
        time.sleep(0.3)
    finally:
        recv.terminate()
        recv.wait(timeout=5)
    rows = (tmp_path / "s-flows.csv").read_text().splitlines()[1:]
    assert len(rows) == 3 and all(r.split(",")[5] == r.split(",")[2] for r in rows)
    got = sum(int(r.split(",")[2]) for r in (tmp_path / "r-recv.csv").read_text().splitlines()[1:])
    assert got == 1005000
