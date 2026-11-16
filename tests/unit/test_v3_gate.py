"""Suite v3 gate checks 2 and 4 and the rep 1 vs rep 2 table on synthetic run files."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import v3_gate  # noqa: E402


def health(**over) -> dict:
    h = {"lost_events": "0", "cpu_idle_min": "0.6"}
    for i in ("r-eth1", "pub-eth0"):
        h.update({f"{i}.rows_match": "1", f"{i}.deq": "100000", f"{i}.unmatched_deq": "3",
                  f"{i}.unmatched_deq_max_200ms": "1", f"{i}.unmatched_enq": "2", f"{i}.unmatched_enq_max_200ms": "1",
                  f"{i}.interdeq_within10": "0.98", f"{i}.interdeq_within_tol": "0.998", f"{i}.interdeq_ratio_p99": "1.03", f"{i}.interdeq_gaps": "50000",
                  f"{i}.win20_n": "500", f"{i}.win20_within5": "0.999"})
    h.update(over)
    return h


def run_dir(tmp_path):
    (tmp_path / "router-trace").mkdir(exist_ok=True)
    (tmp_path / "router-trace" / "interfaces.csv").write_text(
        "router,iface,ifindex,netns,hop\nr,r-eth1,3,1,r->switch\npub,pub-eth0,2,2,pub->r\n")
    return tmp_path


PLAN = {"egress": {"main": {"hop": "r->switch", "shaped": True}}}


def test_check4_gates_targets_only(tmp_path):
    rd = run_dir(tmp_path)
    res = v3_gate.check_health(rd, health(), PLAN, [])
    assert res["ok"] and res["egress"]["r-eth1"]["role"] == "target" and res["egress"]["pub-eth0"]["role"] == "info"
    # the publisher egress may break every rule without failing the gate
    bad_pub = {"pub-eth0.unmatched_enq": "60", "pub-eth0.interdeq_within_tol": "0.6", "pub-eth0.unmatched_enq_max_200ms": "5"}
    res = v3_gate.check_health(rd, health(**bad_pub), PLAN, [])
    assert res["ok"] and res["egress"]["pub-eth0"]["accounting_ok"] is False
    for bad in ({"lost_events": "1"}, {"cpu_idle_min": "0.3"}, {"r-eth1.rows_match": "0"},
                {"r-eth1.unmatched_deq": "6"}, {"r-eth1.unmatched_enq_max_200ms": "3"},
                {"r-eth1.interdeq_within_tol": "0.985"}, {"r-eth1.win20_within5": "0.97"}):
        assert not v3_gate.check_health(rd, health(**bad), PLAN, [])["ok"], bad


def test_check4_allowance_and_not_evaluated(tmp_path):
    rd = run_dir(tmp_path)
    small = {"r-eth1.deq": "17000", "r-eth1.unmatched_deq": "3", "r-eth1.interdeq_gaps": "800",
             "r-eth1.interdeq_within_tol": "0.5"}
    res = v3_gate.check_health(rd, health(**small), PLAN, [])
    e = res["egress"]["r-eth1"]
    assert res["ok"] and e["allowed"] == 3 and e["service"] == "not evaluated"
    assert not v3_gate.check_health(rd, health(**{**small, "r-eth1.unmatched_deq": "4"}), PLAN, [])["ok"]
    assert v3_gate.check_health(rd, health(**{"r-eth1.deq": "200000", "r-eth1.unmatched_deq": "10"}), PLAN, [])["ok"]


def test_access_egress_is_a_target_with_private_windows(tmp_path):
    rd = run_dir(tmp_path)
    wins = [{"kind": "access", "hop": "pub->r"}]
    res = v3_gate.check_health(rd, health(**{"pub-eth0.unmatched_enq": "60"}), PLAN, wins)
    assert res["egress"]["pub-eth0"]["role"] == "target" and not res["ok"]


def test_check2_reads_installed_qdiscs(tmp_path):
    (tmp_path / "router-metrics" / "r").mkdir(parents=True)
    (tmp_path / "router-metrics" / "r" / "r-eth1.csv").write_text("timestamp_mono_ns,ecn_marks\n1,0\n2,0\n")
    q = ("== r r-eth1\nqdisc htb 5: root refcnt 2 r2q 10 default 0x1\n"
         "qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms "
         "memory_limit 32Mb drop_batch 64\n== r r-eth2\nqdisc cake 20: parent 5:1 bandwidth unlimited besteffort\n")
    (tmp_path / "qdiscs.txt").write_text(q)
    res = v3_gate.check_ecn(tmp_path)
    assert res["ok"] and res["aqm_lines"] == 2 and res["cake_no_ecn_switch"] == ["r/r-eth2"]
    (tmp_path / "qdiscs.txt").write_text(q.replace("memory_limit 32Mb drop_batch", "memory_limit 32Mb ecn drop_batch"))
    assert not v3_gate.check_ecn(tmp_path)["ok"]


def test_rep_compare_flags_the_outlier_cell(tmp_path):
    rows = []
    for k, (a, b) in enumerate([(25.0, 25.5), (24.0, 24.4), (26.0, 26.2), (25.0, 40.0)]):
        for rep, v in ((1, a), (2, b)):
            name = f"v3-C2-sburst-x{k}-pfifo-r{rep}"
            rows.append({"run": name, "keyframe_peaks": {"main": {"p50": v}}})
            (tmp_path / name).mkdir()
            (tmp_path / name / "v3-emission.json").write_text(json.dumps(
                {"sub-d": {"rate_kbps": 5000, "pacing_mbps_p50": 15.0 if rep == 1 else 150.0,
                           "key_ms_p50": 36.6 if rep == 1 else 4.7, "p_ms_p50": 8.1}}))
    text = v3_gate.rep_compare(tmp_path, rows)
    flagged = [l for l in text.splitlines() if "**disagree**" in l]
    assert len(flagged) == 1 and "x3" in flagged[0]
    assert "| sub-d | 5000 | 15.0 / 150.0 | 36.6 / 4.7 | 8.1 / 8.1 |" in text


def test_check5_is_on_the_stimulus_not_the_total(tmp_path):
    import csv as _csv
    import v3_stimuli
    rows = [{"start": 20, "end": 25, "kind": "surge", "stimulus_type": "surge", "target": "main", "hop": "r->switch",
             "cell": "u=1.3 d=5", "u_nominal": 1.3, "d": 5, "planned_nonvideo": 1.09, "nonvideo_load": 1.085,
             "video_load": 0.09, "total_load": 1.175, "video_calm": 0.21, "video_rel_calm": 0.43,
             "capacity_ratio": 1.0, "source": "trace"}]
    with (tmp_path / "v3-stimuli.csv").open("w", newline="") as fh:
        w = _csv.DictWriter(fh, fieldnames=v3_stimuli.FIELDS)
        w.writeheader()
        w.writerows(rows)
    res = v3_gate.check_surge(tmp_path, {}, [])
    assert res["ok"] and res["windows"][0]["total"] == 1.175    # total 1.175 vs u 1.3: not gated
    rows[0]["nonvideo_load"] = 1.03
    with (tmp_path / "v3-stimuli.csv").open("w", newline="") as fh:
        w = _csv.DictWriter(fh, fieldnames=v3_stimuli.FIELDS)
        w.writeheader()
        w.writerows(rows)
    assert not v3_gate.check_surge(tmp_path, {}, [])["ok"]


def test_reaction_table_reps_side_by_side(tmp_path):
    import csv as _csv
    import v3_stimuli
    for block, variant, rel in (("C2", "s030u070", (0.5, 0.45)), ("C5", "s030u070", (0.8, 0.82)), ("M3", "bgmix", (0.7, 0.6))):
        for rep in (1, 2):
            rd = tmp_path / f"v3-{block}-x-{variant}-pfifo-r{rep}"
            rd.mkdir()
            (rd / "events.csv").write_text("event\n")
            st = "tcp" if block == "C5" else "surge"
            with (rd / "v3-stimuli.csv").open("w", newline="") as fh:
                w = _csv.DictWriter(fh, fieldnames=v3_stimuli.FIELDS)
                w.writeheader()
                w.writerow({k: "" for k in v3_stimuli.FIELDS} | {"stimulus_type": st, "cell": "cubic n=2 d=5",
                            "u_nominal": "" if st == "tcp" else 1.3, "video_rel_calm": rel[rep - 1]})
    text = v3_stimuli.reaction_table(tmp_path)
    assert "| C2 | BG-CBR surge | s030u070 | pfifo | u 1.3 | 0.50 (1) | 0.45 (1) |" in text
    assert "| C5 | TCP surge | s030u070 | pfifo | cubic n=2 d=5 | 0.80 (1) | 0.82 (1) |" in text
    assert "| M3 | BG-BURSTY / BG-MIX surge | bgmix | pfifo | u 1.3 | 0.70 (1) | 0.60 (1) |" in text
