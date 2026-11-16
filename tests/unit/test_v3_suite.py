"""Suite v3 planner (scripts/v3_suite.py): sizing, topologies, AQM settings, stimuli and the
campaign matrix, against the numbers of the spec. Nothing runs."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import v3_suite as v3  # noqa: E402
from quiclab.config.scenario import BgEvent, BurstsEvent, load_scenario  # noqa: E402
from quiclab.config.schema import load_topology  # noqa: E402
from quiclab.orchestrator import mininet_backend as mb  # noqa: E402


@pytest.mark.parametrize("variant,cap,bg", [
    ("s030u070", 54.0, 26.4), ("s030u050", 75.5, 26.4), ("s030u085", 44.4, 26.4), ("s065u050", 34.9, 6.1),
    ("s065u070", 24.9, 6.1), ("s065u085", 20.5, 6.1), ("s010u070", 73.6, 46.4), ("s010u085", 60.6, 46.4)])
def test_base_table(variant, cap, bg):
    row = v3.base_row(variant)
    t = v3.build("base", variant, s=row["s"], U=row["U"], **row.get("build_opts", {}))
    e = t.egress["main"]
    assert round(e.cap, 1) == cap and round(e.bg, 1) == bg


def test_hierarchy_tables():
    sp = v3.build("split4", s=0.30)
    assert [round(sp.egress[x].cap, 1) for x in ("up", "a", "b")] == [93.2, 46.6, 46.6]
    assert [round(sp.egress[x].bg, 1) for x in ("up", "a", "b")] == [45.7, 22.8, 22.8]
    sp65 = v3.build("split4", s=0.65)
    assert [round(sp65.egress[x].cap, 1) for x in ("up", "a")] == [43.0, 21.5]
    tr = v3.build("tree16", s=0.30)
    assert [round(tr.egress[x].cap, 1) for x in ("root", "X", "A")] == [98.1, 49.0, 24.5]
    assert [round(tr.egress[x].bg, 1) for x in ("root", "X", "A")] == [48.1, 24.0, 12.0]
    assert len(tr.topo["traffic"]["routes"]) == 7 and len(tr.rates) == 16
    assert round(v3.build("tree16", s=0.35).egress["root"].cap, 1) == 84.1
    un = v3.build("uneven", s=0.30)
    assert [round(un.egress[x].cap, 1) for x in ("A", "B", "C")] == [36.8, 49.0, 80.9]
    assert not un.egress["up"].shaped and "bg-up" not in un.topo["traffic"]["routes"]
    assert not v3.build("split4", "noroot", s=0.30).egress["up"].shaped


def test_routes_cross_only_their_egress():
    for kind in ("base", "split4", "tree16", "uneven", "access", "rev"):
        t = v3.build(kind, s=0.30)
        for e in t.bottlenecks():
            path = t.topo["traffic"]["routes"][e.route]["path"]
            assert path == [f"tx-{e.name}", e.hop[0], e.hop[1], f"rx-{e.name}"]
            assert path[1] in t.routers


def test_delays_narrow_cycle_and_scale():
    t = v3.build("split4", s=0.30)
    assert [t.delays[c] for c in ("a1", "a2", "a3", "a4", "b1")] == [5.0, 7.5, 12.5, 20.0, 5.0]
    assert v3.build("access", s=0.30).delays == {"sub-a": 5.0, "sub-b": 7.5, "sub-c": 12.5, "sub-d": 20.0}
    t4 = v3.build("base", s=0.30, delay_scale=4.0)
    assert t4.delays["sub-d"] == 80.0


def test_aqm_settings():
    t = v3.build("base", s=0.30)
    r = v3.aqm_routers(t, "pfifo")["router"]["egress"]
    assert r["switch"] == {"aqm": "pfifo", "queue_limit_packets": 225}
    assert r["tx-main"] == {}
    for aqm in ("codel", "pie", "fq_codel"):
        assert v3.aqm_routers(t, aqm)["router"]["egress"]["switch"] == {"aqm": aqm, "ecn": False}
    red = v3.aqm_routers(t, "red")["router"]["egress"]["switch"]
    assert red["ecn"] is False and red["queue_limit_packets"] == v3.ms_to_pkts(53.95, 150)
    assert red["red_min_bytes"] == round(53.95e6 * 0.015 / 8)
    assert v3.aqm_routers(v3.build("base", "legacy", s=None, U=0.65), "pfifo")["router"]["egress"]["switch"][
        "queue_limit_packets"] == 100
    mix = v3.aqm_routers(v3.build("split4", s=0.30), "mixab")
    assert mix["r2"]["egress"]["switch-b"]["aqm"] == "fq_codel" and mix["r2"]["egress"]["switch-a"]["aqm"] == "pfifo"
    assert v3.ms_to_pkts(1.0, 1.0) == 1 and v3.queue("pfifo", 2.0, 50)["queue_limit_packets"] == 20


def test_background_counts_and_surge_flows():
    t = v3.build("base", s=0.30)
    (bg,) = v3.background(t, "cbr", 1, 100)
    assert len(bg["flow_weights"]) == round(26.437 / 2.5) and bg["type"] == "bg"
    assert v3.surge_weights(7.2) == [2.5, 2.5, 2.2]
    mix = v3.background(t, "mix", 1, 100)
    tcp = [e for e in mix if e.get("process") == "tcp"]
    assert {e["cc"] for e in tcp} == {"cubic", "bbr"} and any("on_s" in e for e in tcp)
    assert v3.background(v3.build("base", "legacy", s=None, U=0.65), "cbr", 1, 100) == []


def test_schedule_ramp_and_onoff():
    b = BurstsEvent.model_validate({"at_s": 0, "type": "bursts", "id": "x", "route": "r", "process": "poisson",
                                    "ramp_up_s": 5, "bursts": [{"start_s": 1, "duration_s": 10, "rate_mbps": 10}]})
    sched = b.schedule()
    assert len(sched) == 10 and abs(sum(r for _, _, r in sched) - 10) < 1e-9
    assert all(abs(a + d - 11) < 1e-6 for a, d, _ in sched) and sched[-1][0] == pytest.approx(5.5)
    g = BgEvent.model_validate({"at_s": 0, "type": "bg", "id": "y", "route": "r", "duration_s": 10, "rate_mbps": 2,
                                "process": "tcp", "on_s": 2, "off_s": 2, "phase_s": 1})
    s = g.schedule()
    assert s[0] == (0.0, 1.0, 4.0) and s[1] == (3.0, 2.0, 4.0)
    with pytest.raises(ValueError):
        BurstsEvent.model_validate({"at_s": 0, "type": "bursts", "id": "x", "route": "r", "flow_weights": [1],
                                    "bursts": [{"start_s": 0, "duration_s": 1, "rate_mbps": 1}]})


def test_matrix_counts():
    def runs(cells):
        return sum(len(c.aqms) * len(c.reps) for c in cells)
    assert runs(v3.CORE) == 132 and runs(v3.MICRO) == 62 and runs(v3.GATE) == 9


def test_every_plan_validates_and_only_listed_violations(tmp_path):
    gen = tmp_path / "_gen"
    plans = v3.plan_all(gen, v3.GATE + v3.CORE + v3.MICRO)
    assert len(plans) == 203
    for p in plans:
        topo = load_topology(p.topology)
        sc = load_scenario(p.scenario, topo)
        cmds = [c for _, c in mb.initial_shaping_commands(topo, sc)]
        assert not any(c.endswith(" ecn") or " ecn " in c for c in cmds if "cake" not in c), p.name
    assert v3.check_violations(plans) == []
    flagged = {p.cell.variant for p in plans if p.violations}
    assert flagged == set(v3.SPEC_LISTED_VIOLATIONS)
    hours = sum(p.duration for p in plans) / 3600
    assert hours <= v3.BUDGET_H
    # rep-major inside each part: no rep-2 run before the last rep-1 run of the core
    core = [p for p in plans if p.cell.block.startswith("C")]
    assert max(i for i, p in enumerate(core) if p.rep == 1) < min(i for i, p in enumerate(core) if p.rep == 2)


def test_windows_and_stimuli(tmp_path):
    t = v3.build("split4", s=0.30)
    ev, win, dur = v3.plan_type("hhier", t, 1)
    surges = [e for e in ev if e["type"] == "bursts"]
    assert len(surges) == 27 + 2 * 24   # 27 single cells, 24 combined cells of two parts each
    assert len(win) == len(surges) and all(w["hop"] for w in win)
    e = t.egress["a"]
    w = next(w for w in win if w["target"] == "a" and w["u"] == 1.3)
    assert w["extra_mbps"] == pytest.approx((1.3 - 0.7) * e.cap, abs=1e-3)
    assert sorted(w["expected"]) == ["a1", "a2", "a3", "a4"]
    ev, win, dur = v3.plan_type("sjoin", v3.build("base", s=0.30), 1)
    assert all(float(x["at_s"]).is_integer() for x in ev if x["type"] == "bursts")
    ev, win, dur = v3.plan_type("amixed", v3.build("access", s=0.30), 1)
    private = [w for w in win if w["kind"] == "access"]
    assert len(private) == 12 and all(w["start"] > v3.JOIN_T + 10 for w in private if w["target"] == v3.JOIN_SUB)
    ev, win, dur = v3.plan_type("nloss", v3.build("base", s=0.30), 1)
    assert len(win) == 9 and all(a["target"] != b["target"] for a, b in zip(win, win[1:]))


def test_v3_feed_is_1000_and_traced(tmp_path):
    (p,) = v3.plan_all(tmp_path, [v3.Cell("G2", "calm", "split4", "split4", ("pfifo",), reps=(1,))])
    topo = load_topology(p.topology)
    sc = load_scenario(p.scenario, topo)
    fwd, rev = sc.initial_link("pub", "r1")
    assert fwd.bandwidth_mbps == 1000 and fwd.delay_ms == 5 and rev.delay_ms == 5
    traced = mb.gtq_trace_interfaces(topo, sc)
    assert [h for _, h in traced["pub"]] == [("pub", "r1")]
    assert {h for _, h in traced["r1"]} == {("r1", "r2"), ("r1", "sub-ctrl")}
    assert {h for _, h in traced["r2"]} == {("r2", "switch-a"), ("r2", "switch-b")}


def test_aqm_leaves_say_noecn(tmp_path):
    cells = [v3.Cell("C2", "sburst", "s030u070", "base", ("codel", "pie", "fq_codel", "red", "cake"), reps=(1,))]
    for p in v3.plan_all(tmp_path, cells):
        topo = load_topology(p.topology)
        leaves = [c for _, c in mb.initial_shaping_commands(topo, load_scenario(p.scenario, topo)) if "handle 20:" in c]
        assert leaves
        for c in leaves:
            if p.aqm in ("codel", "pie", "fq_codel"):
                assert c.endswith(f"{p.aqm} noecn"), c
            else:
                assert "ecn" not in c.split(), c
