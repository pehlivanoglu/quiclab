"""Planner of the grouping campaigns (scripts/grouping_campaign.py): seeded,
schema-valid, windows consistent with the events and the K5 join/leave rules."""

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import det_matrix as dm  # noqa: E402
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
    assert windows and all(w["end"] > w["start"] for w in windows)
    assert all(w["end"] <= duration for w in windows)


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
    assert len(a) == len(b) == 6 and all(abs((y - x) - 2.0) < 1e-6 for x, y in zip(a, b))
    sim = [w for w in windows if w["cell"] == "a+b"]
    assert len(sim) == 12 and len({w["start"] for w in sim}) == 6
    assert all(set(w["expected"]) == {"a1", "a2", "a3"} for w in windows if w["target"] == "a")
    assert all(set(w["expected"]) == {"a1", "a2", "a3", "b1", "b2", "b3"} for w in windows if w["target"] == "up")
    links = [(e["from"], e["to"]) for e in events if e["type"] == "link"]
    assert {("r1", "r2"), ("r2", "switch-a"), ("r2", "switch-b")} == set(links)


def test_mixed_respects_join_and_leave():
    n = dm.topology_numbers("base")
    events, windows, duration = gc.plan_mixed(n, 3)
    assert {e["type"] for e in events} == {"link", "join", "leave"}
    for w in windows:
        if w["target"] == gc.JOIN_SUB:
            assert w["start"] > gc.JOIN_T + 10
        if w["target"] == gc.LEAVE_SUB:
            assert w["start"] < gc.LEAVE_T - 10
    assert duration > gc.LEAVE_T + 30
    assert sum(w["cell"] == "shared" for w in windows) == 6 and sum(w["cell"] == "private" for w in windows) == 16


def test_revcross_has_no_expected_clients_and_reverse_link_capped(tmp_path):
    scenario, topo, _ = gc.scenario_for("K3", "revcross", "pfifo", 1, tmp_path)
    data = yaml.safe_load(scenario.read_text())
    windows = __import__("json").loads((tmp_path / "_gen" / "grp-revcross-pfifo-r1-windows.json").read_text())
    assert all(w["expected"] == [] for w in windows)
    link = next(l for l in data["links"] if (l["from"], l["to"]) == ("router", "switch"))
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


def test_part_rate_matches_severity(tmp_path):
    scenario, _, _ = gc.scenario_for("K2", "part130", "pfifo", 1, tmp_path)
    data = yaml.safe_load(scenario.read_text())
    n = dm.topology_numbers("base")
    h = n["hops"]["main"]
    rate = data["events"][0]["bursts"][0]["rate_mbps"]
    assert rate == pytest.approx(1.3 * h["base"] - h["demand"], abs=1e-3)
