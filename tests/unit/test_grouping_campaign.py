"""Planner of the grouping campaigns (scripts/grouping_campaign.py): seeded,
schema-valid, windows consistent with the events and the K5 join/leave rules."""

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import det_matrix as dm  # noqa: E402
from quiclab.orchestrator.mininet_backend import initial_shaping_commands  # noqa: E402
from quiclab.runtime import edge_interfaces  # noqa: E402
import grouping_campaign as gc  # noqa: E402
from quiclab.config.scenario import load_scenario  # noqa: E402
from quiclab.config.schema import load_topology  # noqa: E402

ALL_CELLS = [(k, rtype, aqm) for k, c in gc.CAMPAIGNS.items() for rtype in c["types"] for aqm in c["aqms"][:1]]


@pytest.mark.parametrize("k,rtype,aqm", ALL_CELLS)
def test_every_type_plans_and_validates(tmp_path, k, rtype, aqm):
    scenario, topo, duration = gc.scenario_for(k, rtype, aqm, 1, tmp_path)
    load_scenario(scenario, load_topology(topo))
    data = yaml.safe_load(scenario.read_text())
    assert data["duration_s"] == duration and duration >= 60
    windows = __import__("json").loads((tmp_path / "_gen" / f"{gc.run_id(rtype, aqm, 1)}-windows.json").read_text())
    assert (not windows) if k == "G0" else windows        # negatives plan no window (revcross: windows, nobody expected)
    assert all(w["end"] > w["start"] and w["end"] <= duration and "hop" in w and "stimulus_type" in w for w in windows)


def test_plan_is_seeded():
    n = dm.topology_numbers("split")
    assert gc.plan_hier(n, 7) == gc.plan_hier(n, 7)
    assert gc.plan_hier(n, 7) != gc.plan_hier(n, 8)


def test_hier_offsets_and_pairs_of_windows():
    n = dm.topology_numbers("split")
    events, windows, _ = gc.plan_hier(n, 1)
    by_cell = {}
    for w in windows:
        by_cell.setdefault((w["cell"], w["start"] if "@" not in w["cell"] else None), []).append(w)
    offs = [w for w in windows if w["cell"] == "a+b@2"]
    a = sorted(w["start"] for w in offs if w["target"] == "a")
    b = sorted(w["start"] for w in offs if w["target"] == "b")
    assert len(a) == len(b) == 9 and all(abs((y - x) - 2.0) < 1e-6 for x, y in zip(a, b))
    sim = [w for w in windows if w["cell"] == "a+b"]
    assert len(sim) == 18 and len({w["start"] for w in sim}) == 9
    assert all(set(w["expected"]) == {"a1", "a2", "a3"} for w in windows if w["target"] == "a")
    assert all(set(w["expected"]) == {"a1", "a2", "a3", "b1", "b2", "b3"} for w in windows if w["target"] == "up")
    links = [(e["from"], e["to"]) for e in events if e["type"] == "link"]
    assert {("r1", "r2"), ("r2", "switch-a"), ("r2", "switch-b")} == set(links)


def test_mixed_respects_the_join_and_nobody_leaves():
    n = dm.topology_numbers("access")
    events, windows, duration = gc.plan_mixed(n, 3)
    assert all(e["from"] != "switch" for e in events if e["type"] == "link")
    assert {e["type"] for e in events} == {"link", "join"}
    for w in windows:
        if w["target"] == gc.JOIN_SUB:
            assert w["start"] > gc.JOIN_T + 10
    # u {1.1, 1.3, 2.0} x d {1, 2, 4} x 2 shared, u x d {2, 4} x 4 clients private
    assert sum(w["cell"] == "shared" for w in windows) == 18 and sum(w["cell"] == "private" for w in windows) == 24


def test_hier_v2_has_seven_target_kinds_and_five_aqms():
    n = dm.topology_numbers("split")
    _, windows, _ = gc.plan_hier(n, 1)
    assert {w["cell"] for w in windows} == set(gc.HIER_TARGETS) and "a+b@1" not in gc.HIER_TARGETS
    assert gc.CAMPAIGNS["K1"]["aqms"] == ["pfifo", "red", "pie", "fq_codel", "mixab"]
    assert len(gc.cells_of("K1")) == 15 and len(gc.cells_of("K6")) == 10 and len(gc.cells_of("N1")) == 15


def test_windows_carry_stimulus_type_and_concurrent_flag():
    n = dm.topology_numbers("split")
    _, windows, _, _ = gc.plan_type("hier", n, 1)
    assert all(w["stimulus_type"] == "capdrop" for w in windows)
    assert all(w["concurrent"] for w in windows if w["cell"].startswith("a+"))
    assert not any(w["concurrent"] for w in windows if w["cell"] in ("a", "b", "up"))


def test_indep_timing_never_scripts_simultaneity():
    n = dm.topology_numbers("split")
    events, windows, duration = gc.plan_indep(n, 2)
    assert duration == gc.N_DURATION_S
    for tgt in ("up", "a", "b"):
        ws = sorted((w for w in windows if w["target"] == tgt), key=lambda w: w["start"])
        starts = [w["start"] for w in ws]
        gaps = [b["start"] - a["end"] for a, b in zip(ws, ws[1:])]
        assert len(ws) >= 10 and min(gaps) >= gc.INDEP_GAP_MIN_S - 1e-9
        assert starts[0] >= dm.WARMUP_S and ws[-1]["end"] <= duration - dm.TAIL_S
    # different seeds give different processes, the same seed the same
    assert gc.plan_indep(n, 2) == gc.plan_indep(n, 2) and gc.plan_indep(n, 2) != gc.plan_indep(n, 3)
    starts = sorted(w["start"] for w in windows)
    assert len(set(starts)) == len(starts)
    for w in windows:
        overlaps = [v for v in windows if v["target"] != w["target"]
                    and v["start"] - gc.CONCURRENT_S <= w["end"] and w["start"] - gc.CONCURRENT_S <= v["end"]]
        assert w["concurrent"] == bool(overlaps)


def test_cross_mixes_udp_bursts_and_tcp_bulk(tmp_path):
    scenario, _, _ = gc.scenario_for("N3", "cross", "pfifo", 1, tmp_path)
    data = yaml.safe_load(scenario.read_text())
    windows = __import__("json").loads((tmp_path / "_gen" / "grp-cross-pfifo-r1-windows.json").read_text())
    types = {w["stimulus_type"] for w in windows}
    assert types == {"udp", "tcp"} and {w["cell"] for w in windows} <= {f"{t}:{s}" for t in "ab" for s in types} | {f"up:{s}" for s in types}
    bursts = {e["route"]: e for e in data["events"] if e["type"] == "bursts"}
    assert set(bursts) <= {"shared", "cross-a", "cross-b"} and bursts
    n = dm.topology_numbers("split")
    for w in windows:
        if w["stimulus_type"] == "udp":
            h = n["hops"][w["target"]]
            b = next(b for b in bursts[h["route"]]["bursts"] if b["start_s"] == w["start"])
            assert b["rate_mbps"] == pytest.approx(w["u"] * h["base"] - h["demand"], abs=1e-3)
        else:
            e = next(e for e in data["events"] if e["type"] == "flow" and e["at_s"] == w["start"])
            assert e["kind"] == "tcp" and e["cc"] == "cubic" and e["parallel"] == w["tcp_flows"] in gc.TCP_FLOWS
            assert w["u"] is None and round(w["end"] - w["start"], 3) in gc.TCP_D
    assert all(e["type"] != "link" for e in data["events"])   # no capacity drops in N3


def test_trace_scaling_hits_the_below_target_or_says_so():
    import numpy as np
    steps = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0] * 10)
    mult, below, adjusted = gc.scale_trace(steps, 2.0)
    # mean 5.5 -> x0.727 puts 1 and 2 (20 %) below 2.0: outside the target, so the
    # multiplier is re-set to the 10 % quantile and the result says so
    assert adjusted and mult == pytest.approx(2.0 / np.quantile(steps, 0.10)) and below == pytest.approx(0.1, abs=0.05)
    mult, below, adjusted = gc.scale_trace(np.array([1.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0] * 10), 2.0)
    assert not adjusted and mult == pytest.approx(gc.TRACE_MEAN_X * 2.0 / 2.8) and below == pytest.approx(0.1)


def test_trace_plan_replays_every_access_link_and_labels_private_windows(tmp_path):
    scenario, _, duration = gc.scenario_for("N4", "trace", "pfifo", 2, tmp_path)
    data = yaml.safe_load(scenario.read_text())
    plan = __import__("json").loads((tmp_path / "_gen" / "grp-trace-pfifo-r2-plan.json").read_text())
    windows = __import__("json").loads((tmp_path / "_gen" / "grp-trace-pfifo-r2-windows.json").read_text())
    n = dm.topology_numbers("access")
    assert set(plan["traces"]) == set(n["clients"]) and len({m["trace"] for m in plan["traces"].values()}) == 4
    for c, m in plan["traces"].items():
        trace_events = [e for e in data["events"] if e["type"] == "link" and e["to"] == c]
        assert trace_events and all(e["from"] == n["uplink"][c] and e["label"] == "trace" for e in trace_events)
        assert all(e["bandwidth_mbps"] >= gc.TRACE_MIN_MBPS for e in trace_events)
        assert gc.TRACE_BELOW[0] <= m["below_fraction"] <= gc.TRACE_BELOW[1] + 0.05 or m["adjusted"]
        priv = [w for w in windows if w["cell"] == "private" and w["target"] == c]
        assert len(priv) == m["n_private_windows"] and all(w["stimulus_type"] == "trace" and w["expected"] == [c]
                                                            for w in priv)
    shared = [w for w in windows if w["cell"] == "shared"]
    assert shared and all(set(w["expected"]) == set(n["clients"]) for w in shared)
    assert duration == gc.N_DURATION_S and all(e["at_s"] <= duration for e in data["events"])
    # the same seed assigns the same traces on another AQM
    gc.scenario_for("N4", "trace", "fq_codel", 2, tmp_path)
    plan2 = __import__("json").loads((tmp_path / "_gen" / "grp-trace-fq_codel-r2-plan.json").read_text())
    assert plan2["traces"] == plan["traces"]


def test_churn_sessions_alternate_and_windows_expect_whole_window_sessions(tmp_path):
    scenario, topo, duration = gc.scenario_for("N5", "churn", "pfifo", 1, tmp_path)
    sc = load_scenario(scenario, load_topology(topo))
    windows = __import__("json").loads((tmp_path / "_gen" / "grp-churn-pfifo-r1-windows.json").read_text())
    n = dm.topology_numbers("large")
    sessions = {c: sc.sessions(c) for c in n["clients"]}
    assert sum(len(ss) for ss in sessions.values()) > len(n["clients"])     # somebody re-joined
    for c, ss in sessions.items():
        assert ss[0][0] == 0.0
        for (j1, l1), (j2, _) in zip(ss, ss[1:]):
            assert l1 is not None and l1 - j1 >= gc.N5_ON[1] - 1e-6 and j2 - l1 >= gc.N5_OFF[1] - 1e-6
    ids = {sc.session_id(c, k) for c, ss in sessions.items() for k in range(1, len(ss) + 1)}
    for w in windows:
        assert set(w["expected"]) <= ids and w["n_on"] == len(w["expected"])
        for f in w["expected"]:
            c, k = sc.session_of(f, sessions)
            join, leave = sessions[c][k - 1]
            assert join <= w["start"] and (leave is None or leave >= w["end"])
        drop = next(e for e in sc.events if e.type == "link" and e.at_s == w["start"])
        assert drop.bandwidth_mbps == pytest.approx(w["demand_on_mbps"] / w["u"], abs=1e-3)
    assert duration == gc.N5_DURATION_S


def test_uneven_keeps_per_egress_queue_limits_and_red_thresholds(tmp_path):
    for aqm in ("pfifo", "red"):
        scenario, topo, _ = gc.scenario_for("N2", "uneven", aqm, 1, tmp_path)
        load_scenario(scenario, load_topology(topo))
        data = yaml.safe_load(scenario.read_text())
        r2 = data["routers"]["r2"]
        assert r2["aqm"] == aqm and r2["queue_limit_packets"] == 143
        assert r2["egress"]["switch-a"]["queue_limit_packets"] == 98 and r2["egress"]["switch-c"]["queue_limit_packets"] == 297
        if aqm == "red":
            assert r2["egress"]["switch-c"]["red_max_bytes"] > r2["egress"]["switch-a"]["red_max_bytes"]
    scenario, topo, _ = gc.scenario_for("N2", "uneven6", "pfifo", 1, tmp_path)
    assert topo.name == "detector-uneven6.yaml" and load_topology(topo).subscribers.keys() >= {"c6"} \
        and "c7" not in load_topology(topo).subscribers


def test_revcross_has_no_expected_clients_and_reverse_link_capped(tmp_path):
    scenario, topo, _ = gc.scenario_for("K3", "revcross", "pfifo", 1, tmp_path)
    data = yaml.safe_load(scenario.read_text())
    windows = __import__("json").loads((tmp_path / "_gen" / "grp-revcross-pfifo-r1-windows.json").read_text())
    assert all(w["expected"] == [] for w in windows)
    link = next(l for l in data["links"] if (l["from"], l["to"]) == ("r0", "r1"))
    assert link["reverse"]["bandwidth_mbps"] == gc.REV_LINK_MBPS
    assert any(e["type"] == "bursts" and e["route"] == "rshared" for e in data["events"])


def test_revasym_and_jitter_links(tmp_path):
    s1, _, _ = gc.scenario_for("K3", "revasym", "pfifo", 1, tmp_path)
    s2, _, _ = gc.scenario_for("K3", "revjit10", "pfifo", 1, tmp_path)
    d1, d2 = yaml.safe_load(s1.read_text()), yaml.safe_load(s2.read_text())
    rev1 = {l["to"]: l["reverse"]["delay_ms"] for l in d1["links"] if l["from"] == "switch" and l["to"].startswith("sub-")}
    assert sorted(rev1.values()) == sorted(gc.REV_ASYM_MS)
    assert all(l["reverse"].get("jitter_ms") == 10.0 for l in d2["links"] if l["from"] == "switch" and l["to"].startswith("sub-"))


def test_mixed_aqm_per_router(tmp_path):
    scenario, _, _ = gc.scenario_for("K1", "hier", "mixa", 1, tmp_path)
    data = yaml.safe_load(scenario.read_text())
    assert data["routers"]["r1"]["aqm"] == "pfifo" and data["routers"]["r2"]["aqm"] == "fq_codel"


def test_mixab_differs_between_branches_only(tmp_path):
    scenario, topo_file, _ = gc.scenario_for("K1", "hier", "mixab", 1, tmp_path)
    topo = load_topology(topo_file)
    # Every tc command, by the egress it lands on: the real t=0 setup, not the YAML.
    cmds = initial_shaping_commands(topo, load_scenario(scenario, topo))
    ifaces = {}
    for edge in edge_interfaces(topo):
        ifaces[(edge.a, edge.a_iface)], ifaces[(edge.b, edge.b_iface)] = edge.b, edge.a

    def aqm_on(router, peer):
        leaves = [c for nid, c in cmds if nid == router and " handle 20:" in c and ifaces[(router, c.split()[4])] == peer]
        assert len(leaves) == 1
        return leaves[0]
    assert "pfifo" in aqm_on("r2", "switch-a") and "fq_codel" in aqm_on("r2", "switch-b")
    assert "pfifo" in aqm_on("r2", "r1") and "pfifo" in aqm_on("r1", "r2")
    assert "limit 80" in aqm_on("r2", "switch-a") and "limit 80" in aqm_on("r2", "switch-b")


def test_scoring_survives_a_missing_replay_binary(tmp_path, monkeypatch):
    def process(_run, _cfg, a):
        if a.onsets == "v2":
            raise SystemExit("replay binary missing")
        return {"onsets": 1}
    monkeypatch.setattr(gc.ga, "process", process)
    monkeypatch.setattr(gc.gb, "process", lambda *_: {"methods": {}})
    out = gc.score_run(tmp_path, None)
    assert out["ecg"]["v2"] == {"error": "replay binary missing"}
    assert out["ecg"]["owd"] == out["ecg"]["truth"] == out["ecg"]["v2-owd"] == {"onsets": 1}
    assert gc.ONSET_SOURCES == ("v2-owd", "v2", "v2-owd-nohold", "v2-nohold", "owd", "truth") and gc.PRIMARY == "v2-owd"
    assert "baselines" in out and "baselines" not in gc.score_run(tmp_path, None, with_baselines=False)
    assert gc.CAMPAIGNS["N5"]["baselines"] is False


def test_link_lag_reads_applied_link_events_per_label():
    rows = [{"event": "epoch", "at_s": "0", "applied_s": "0.0001", "status": "applied", "label": ""},
            {"event": "link", "at_s": "15", "applied_s": "15.002", "status": "applied", "label": "trace"},
            {"event": "link", "at_s": "15.2", "applied_s": "15.45", "status": "applied", "label": "trace"},
            {"event": "link", "at_s": "20", "applied_s": "20.001", "status": "applied", "label": "burst u=1.3 d=2"},
            {"event": "link", "at_s": "21", "applied_s": "", "status": "failed", "label": "trace"}]
    all_ = gc.link_lag(rows)
    assert all_["n"] == 3 and all_["max"] == pytest.approx(0.25) and all_["p50"] == pytest.approx(0.002)
    assert gc.link_lag(rows, "trace")["n"] == 2 and gc.link_lag(rows, "nope") is None
    assert f"> {gc.TRACE_LAG_MAX_S}" in gc.infra_line({"run": "r", "finished": True, "errors": 0, "sender_files_missing": [],
                                             "lag_trace": gc.link_lag(rows, "trace"), "lag_all": all_,
                                             "sessions_planned": 0, "sessions_found": 0, "clients_never_hit": [],
                                             "clients": 5, "windows_hit": 1, "windows": 1, "shared_hit2": 1,
                                             "shared_windows": 1, "private_hit": 0, "private_windows": 0,
                                             "link_events": 4, "ctrl_congested_bins": 0})


def test_only_filter_limits_the_cells(tmp_path):
    secs = gc.run_campaign("N2", tmp_path / "N2", None, False, dry=True, only="pfifo-r1")
    assert secs == gc.N_DURATION_S and sorted(p.name for p in (tmp_path / "N2" / "_gen").glob("*.yaml")) == \
        ["grp-uneven-pfifo-r1.yaml"]


def test_part_types_keep_their_severity():
    assert gc.CAMPAIGNS["K2"]["types"] == ["part105", "part110", "part115", "part130"]


@pytest.mark.parametrize("rtype,u", [("part115", 1.15), ("part130", 1.3)])
def test_part_rate_matches_severity(tmp_path, rtype, u):
    scenario, _, _ = gc.scenario_for("K2", rtype, "pfifo", 1, tmp_path)
    data = yaml.safe_load(scenario.read_text())
    n = dm.topology_numbers("base")
    h = n["hops"]["main"]
    drop, restore = data["events"][:2]
    assert (drop["from"], drop["to"]) == ("router", "switch")
    assert drop["bandwidth_mbps"] == pytest.approx(h["demand"] / u, abs=1e-3)
    assert restore["bandwidth_mbps"] == h["base"]


def test_dm_types_get_windows_from_their_events():
    n = dm.topology_numbers("base")
    for name, stype, expect_windows in (("burstcap", "capdrop", True), ("burstudp", "udp", True),
                                        ("tcpcubic", "tcp", True), ("ramp", "capdrop", True),
                                        ("calm065", None, False), ("randloss", None, False), ("calmcbr090", None, False)):
        events, windows, duration = gc.plan_dm(name, n, 1, "base")
        assert bool(windows) == expect_windows, name
        for w in windows:
            assert w["stimulus_type"] == stype and set(w["expected"]) == set(n["clients"]) and w["target"] == "main"
            assert w["end"] <= duration
    _, wp, dur = gc.plan_dm("ppbp", n, 1, "base")
    assert len(wp) == 1 and wp[0]["from_truth"] and wp[0]["stimulus_type"] == "ppbp" and wp[0]["end"] <= dur
    ev, win, _ = gc.plan_dm("burstlongsplit", dm.topology_numbers("split"), 1, "split")
    assert {w["target"] for w in win} == {"up", "a", "b"} and all(w["end"] - w["start"] >= 10 for w in win)
    assert all(w["cell"] == w["target"] for w in win)


def test_micro_variants_change_one_factor(tmp_path):
    q = {}
    for t in ("burstcap", "burstcapq05", "burstcapq20"):
        scenario, _, _ = gc.scenario_for("M1" if t == "burstcap" else "M2", t, "pfifo", 1, tmp_path)
        q[t] = yaml.safe_load(scenario.read_text())["routers"]["router"]["queue_limit_packets"]
    assert q["burstcapq05"] == 50 and q["burstcap"] == 100 and q["burstcapq20"] == 200
    s15, topo15, _ = gc.scenario_for("M4", "fps15", "pfifo", 1, tmp_path)
    assert load_topology(topo15).publishers["pub"].fps == 15
    sb, topob, _ = gc.scenario_for("M5", "bw8", "pfifo", 1, tmp_path)
    data = yaml.safe_load(sb.read_text())
    assert all(sub.rate_kbps == 8000 for sid, sub in load_topology(topob).subscribers.items() if sid != "sub-ctrl")
    drop = next(e for e in data["events"] if e["type"] == "link" and e.get("label", "").startswith("burst u=1.3 d=1"))
    assert drop["bandwidth_mbps"] == pytest.approx(32.96 / 1.3, abs=0.01)
    sj, _, _ = gc.scenario_for("M3", "revjit20", "pfifo", 1, tmp_path)
    assert all(l["reverse"].get("jitter_ms") == 20.0 for l in yaml.safe_load(sj.read_text())["links"]
               if l["from"] == "switch" and l["to"].startswith("sub-"))
    _, wf, _ = gc.plan_gaps(dm.topology_numbers("base"), 1, gc.GAPS["gapfast"])
    gaps = [b["start"] - a["end"] for a, b in zip(wf, wf[1:])]
    assert 2.0 - 1e-6 <= min(gaps) and max(gaps) <= 5.0 + 1e-6 and len(wf) == 18
    _, wi, _ = gc.plan_indep(dm.topology_numbers("split"), 1, gc.INDEP_MEANS["indepfast"])
    assert len(wi) > len(gc.plan_indep(dm.topology_numbers("split"), 1)[1])
    assert gc.CAMPAIGNS["G0"]["types"][-3:] == ["calmsplit", "calmtree8", "calmuneven"]
    assert gc.topology_of("G0", "calmtree8") == "tree8" and gc.CAMPAIGNS["M1"]["aqms"] == ["pfifo", "red", "pie", "cake", "codel"]
