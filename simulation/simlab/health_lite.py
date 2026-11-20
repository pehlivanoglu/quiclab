#!/usr/bin/env python3
"""Light health check of a simulation run WITHOUT the per-packet router trace (user 2026-11-19, W4).

    python3 simulation/simlab/health_lite.py <run dir> [--json out.json]

Writes <run>/health-lite.csv (key,value; as gtq-health.csv) and prints one summary line. Reads only aggregate counters
and sender / receiver records; never the router trace.

Items (each ok / not ok, with its values):
  1 completeness     quicsim done line present; late_arrivals 0 and files_open_at_exit 0 (when the build reports
                     them); sim/meta.json present
  2 accounting       every monitored egress: n_enq = n_deq + n_drop, from the queue-disc totals
                     (router-metrics/<node>/<iface>-totals.csv, written when the plan asks for totals); a monitored
                     egress without its totals row fails ("missing counter row")
  3 service rate     every metrics egress: in 25 ms intervals where the queue was non-empty at every 5 ms sample
                     (busy), transmitted bits / interval against the scenario's capacity in force (the frozen
                     router_trace.capacity_timeline); intervals across a capacity change are skipped
  4 sender records   per client: rows of -sent.csv = sum of packets_sent in -owd.csv, and -sent.csv ends with a
                     complete line; per run: video packets not acknowledged (packets_sent - packets_timed) plus
                     background packets lost (traffic/*-recv.csv) against the drops summed over the egress totals
  5 load / share     the frozen v3_gate.check_load_share (router-metrics + sender -sent), unchanged
  6 events vs plan   every planned background / stimulus source wrote its bursts file with the planned number of
                     bursts (plan.txt "schedule")
  7 drops elsewhere  (user 2026-11-19) no queue other than a designed bottleneck egress (v3-plan shaped egress) drops
                     a packet: router-metrics/queue-totals-all.csv (every queue disc of the run, written when the plan
                     asks for it); a run with drops elsewhere is invalid
  8 stimulus load    (user 2026-11-19) in every stimulus window (grouping/windows.json), the load offered to its
                     bottleneck egress (router-metrics offered bytes, [start + 0.5 s, end]) against the plan:
                     U_e x C_e + the window's extra (+ the extras of windows on the same egress covering the whole
                     interval; a window partly overlapped on its egress is skipped and counted)

NOT covered (state this in every report that uses this check): per-packet service intervals and jitter (item 3 is
at 25 ms resolution), and per-packet egress identity (which packet left which egress; item 4 is per-flow totals and
one run-wide balance). There is no GT-Q in runs checked this way.

Tolerances (P, declared before stage C; checked on the B2 runs and the 300-client run where the frozen check passes):
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
QUICLAB = HERE.parents[1]
sys.path.insert(0, str(HERE))
import scale_ext  # noqa: E402,F401
import stageb_compare  # noqa: E402,F401  (sys.path for scripts/)

RATE_MEDIAN_TOL = 0.05      # (P) median of busy-interval rate / capacity within 1 +- 5 %
RATE_SHARE_TOL = 0.10       # (P) ... and at least RATE_SHARE_MIN of busy intervals within 1 +- 10 %
RATE_SHARE_MIN = 0.90       # (P)
RATE_MIN_BUSY = 20          # (P) fewer busy intervals: item 3 reports "not enough busy time" (not a failure)
LOSS_BALANCE_TOL = 0.05     # (P) |unacked video + lost background - egress drops| <= 5 % of drops (+ LOSS_ABS)
LOSS_ABS = 200              # (P) packets: in flight at the end, acknowledged without an RTT sample
STIM_TOL = 0.10             # (P) offered load in a stimulus window within 1 +- 10 % of the plan
STIM_SKIP_S = 0.5           # (P) the window's first 0.5 s is not measured (sources start, queues fill)
__doc__ += (f"  item 3: median within 1 +- {RATE_MEDIAN_TOL:g}, >= {RATE_SHARE_MIN:g} of busy intervals within "
            f"1 +- {RATE_SHARE_TOL:g}, at least {RATE_MIN_BUSY} busy intervals\n"
            f"  item 4: balance within {LOSS_BALANCE_TOL:g} of drops + {LOSS_ABS} packets\n")


def rows(p: Path) -> list[dict]:
    with p.open() as f:
        return list(csv.DictReader(f))


def plan_records(rd: Path, kind: str) -> list[dict]:
    out = []
    for line in (rd / "sim" / "plan.txt").read_text().splitlines():
        if line.startswith(kind + " "):
            out.append(dict(x.split("=", 1) for x in line.split()[1:] if "=" in x))
    return out


def item_completeness(rd: Path) -> dict:
    log = rd / "logs" / "quicsim.log"
    done = [ln for ln in log.read_text().splitlines() if ln.startswith("quicsim done:")] if log.exists() else []
    v = {"done_line": bool(done), "meta": (rd / "sim" / "meta.json").exists()}
    if done:
        tail = dict(kv.strip().rsplit(" ", 1) for kv in done[-1].split(",")[1:] if " " in kv.strip())
        v["late_arrivals"] = int(tail["late_arrivals"]) if "late_arrivals" in tail else "n/a (build before item 5)"
        v["files_open_at_exit"] = int(tail["files_open_at_exit"]) if "files_open_at_exit" in tail else "n/a"
    ok = v["done_line"] and v["meta"] and v.get("late_arrivals") in (0, "n/a (build before item 5)") \
        and v.get("files_open_at_exit") in (0, "n/a")
    return {"ok": bool(ok), **v}


def totals(rd: Path) -> tuple[dict, list[str]]:
    got, missing = {}, []
    for m in plan_records(rd, "monitor"):
        if m.get("totals") != "1":
            continue
        p = rd / "router-metrics" / m["node"] / f"{m['iface']}-totals.csv"
        r = rows(p) if p.exists() else []
        if not r:
            missing.append(m["iface"])
        else:
            got[m["iface"]] = {k: (int(x) if x.lstrip("-").isdigit() else x) for k, x in r[0].items()}
    return got, missing


def item_accounting(rd: Path) -> dict:
    got, missing = totals(rd)
    if not got and not missing:
        return {"ok": None, "why": "plan asks for no totals (run before the totals file / trace 'full')"}
    bad = [i for i, r in got.items() if r["n_enq"] != r["n_deq"] + r["n_drop"]]
    return {"ok": not bad and not missing, "egresses": len(got), "missing_counter_rows": missing,
            "identity_failures": bad, "n_drop_total": sum(r["n_drop"] for r in got.values())}


def item_service(rd: Path) -> dict:
    from quiclab import router_trace
    from quiclab.config.scenario import load_scenario
    from quiclab.config.schema import load_topology
    scen = load_scenario(rd / "scenario.yaml", load_topology(rd / "topology.yaml"))
    ep = rows(rd / "events.csv")[0]
    epoch_ns = int(ep["applied_mono_ns"]) - round(float(ep["applied_s"]) * 1e9)
    out, ok = {}, True
    for m in plan_records(rd, "monitor"):
        if m.get("metrics") != "1":
            continue
        base = rd / "router-metrics" / m["node"] / m["iface"]
        main, queue = rows(base.with_name(base.name + ".csv")), rows(base.with_name(base.name + "-queue.csv"))
        caps = router_trace.capacity_timeline(scen, (m["node"], m["peer"]))
        qt = np.array([int(r["timestamp_mono_ns"]) for r in queue], dtype=np.int64)
        qp = np.array([int(r["queue_packets"]) for r in queue])
        ratios = []
        for r in main:
            iv = int(r["interval_ns"])
            if iv <= 0:
                continue
            t1 = int(r["timestamp_mono_ns"])
            t0 = t1 - iv
            sel = (qt > t0) & (qt <= t1)
            if not sel.any() or (qp[sel] == 0).any():
                continue
            s0, s1 = (t0 - epoch_ns) / 1e9, (t1 - epoch_ns) / 1e9
            c_at = [c for t, c in caps if t <= s0]
            if any(s0 < t <= s1 for t, _ in caps) or not c_at or not np.isfinite(c_at[-1]):
                continue
            ratios.append(int(r["transmitted_bytes"]) * 8 / (iv / 1e9) / (c_at[-1] * 1e6))
        x = np.array(ratios)
        if len(x) < RATE_MIN_BUSY:
            out[m["iface"]] = {"busy": len(x), "ok": None, "why": "not enough busy time"}
            continue
        med = float(np.median(x))
        share = float(np.mean(np.abs(x - 1) <= RATE_SHARE_TOL))
        good = abs(med - 1) <= RATE_MEDIAN_TOL and share >= RATE_SHARE_MIN
        out[m["iface"]] = {"busy": len(x), "median": round(med, 4), "within_tol": round(share, 4), "ok": good}
        ok &= good
    return {"ok": ok, "egress": out}


def item_sender(rd: Path) -> dict:
    pub = next((rd / "publishers").iterdir())
    bad, unacked = [], 0
    for owd in sorted(pub.glob("*-owd.csv")):
        sid = owd.name[: -len("-owd.csv")]
        r = rows(owd)
        sent = sum(int(x["packets_sent"] or 0) for x in r)
        timed = sum(int(x["packets_timed"] or 0) for x in r)
        unacked += sent - timed
        sp = pub / f"{sid}-sent.csv"
        raw = sp.read_bytes() if sp.exists() else b""
        n = raw.count(b"\n") - 1 if raw else -1
        if not raw.endswith(b"\n") or n != sent:
            bad.append({"client": sid, "sent_rows": n, "owd_packets_sent": sent, "complete_last_line": raw.endswith(b"\n")})
    bg_lost = sum(int(x["lost"]) for p in (rd / "traffic").glob("*-recv.csv") for x in rows(p))
    got, missing = totals(rd)
    if got:
        drops = sum(r["n_drop"] for r in got.values())
        src = "queue-disc totals"
    else:
        tc = rd / "router-trace" / "tracer-counts.csv"
        drops = sum(int(x["n_drop"]) for x in rows(tc)) if tc.exists() else None
        src = "tracer-counts.csv (validation only: run has no totals file)"
    balance = None if drops is None else unacked + bg_lost - drops
    bal_ok = balance is not None and abs(balance) <= LOSS_BALANCE_TOL * drops + LOSS_ABS
    return {"ok": not bad and bal_ok, "client_record_failures": bad[:10], "n_client_failures": len(bad),
            "video_unacked": unacked, "bg_lost": bg_lost, "drops": drops, "drops_from": src, "balance": balance}


def item_load_share(rd: Path) -> dict:
    import v3_gate
    plan = json.loads((rd / "v3-plan.json").read_text())
    res = v3_gate.check_load_share(rd, plan)
    return {"ok": bool(res.get("ok")), **{k: v for k, v in res.items() if k != "ok"}}


def item_events(rd: Path) -> dict:
    bad = []
    for g in plan_records(rd, "bg"):
        planned = len([x for x in g.get("schedule", "").split(",") if x])
        p = rd / "traffic" / f"{g['id']}-bursts.csv"
        got = len(rows(p)) if p.exists() else -1
        if got != planned:
            bad.append({"id": g["id"], "planned": planned, "written": got})
    return {"ok": not bad, "sources": len(plan_records(rd, "bg")), "mismatches": bad}


def item_drops_elsewhere(rd: Path) -> dict:
    p = rd / "router-metrics" / "queue-totals-all.csv"
    if not p.exists():
        return {"ok": None, "why": "no queue-totals-all.csv (plan did not ask for it: runs before 2026-11-19 / B2)"}
    plan = json.loads((rd / "v3-plan.json").read_text())
    bott = {e["hop"] for e in plan["egress"].values() if e.get("shaped")}
    bad = [{"hop": r["hop"], "dropped": int(r["n_dropped"])} for r in rows(p)
           if int(r["n_dropped"]) > 0 and r["hop"] not in bott]
    return {"ok": not bad, "queues": len(rows(p)), "drops_outside_bottlenecks": bad[:10], "n_bad": len(bad)}


def item_stimulus_load(rd: Path) -> dict:
    wp = rd / "grouping" / "windows.json"
    if not wp.exists():
        return {"ok": None, "why": "no stimulus windows"}
    wins = [w for w in json.loads(wp.read_text()) if w.get("hop") and w.get("extra_mbps") is not None]
    plan = json.loads((rd / "v3-plan.json").read_text())
    eg = {e["hop"]: e for e in plan["egress"].values()}
    mon = {f"{m['node']}->{m['peer']}": m for m in plan_records(rd, "monitor") if m.get("metrics") == "1"}
    ep = rows(rd / "events.csv")[0]
    epoch_ns = int(ep["applied_mono_ns"]) - round(float(ep["applied_s"]) * 1e9)
    cache, res, skipped, missing = {}, [], 0, set()
    for w in wins:
        h = w["hop"]
        if h not in mon or h not in eg:
            missing.add(h)
            continue
        a, b = w["start"] + STIM_SKIP_S, w["end"]
        same = [x for x in wins if x["hop"] == h and x is not w and x["start"] < b and x["end"] > a]
        if any(not (x["start"] <= a and x["end"] >= b) for x in same):
            skipped += 1
            continue
        e = eg[h]
        planned = (e.get("U") or plan["U"]) * e["C_e_mbps"] + w["extra_mbps"] + sum(x["extra_mbps"] for x in same)
        if h not in cache:
            m = mon[h]
            r = rows(rd / "router-metrics" / m["node"] / f"{m['iface']}.csv")
            cache[h] = (np.array([(int(x["timestamp_mono_ns"]) - epoch_ns) / 1e9 for x in r]),
                        np.array([int(x["offered_bytes"]) for x in r], dtype=float),
                        np.array([int(x["interval_ns"]) for x in r], dtype=float))
        t, by, iv = cache[h]
        sel = (t - iv / 1e9 >= a) & (t <= b) & (iv > 0)
        if sel.sum() < 2:
            continue
        got = by[sel].sum() * 8 / (iv[sel].sum() / 1e9) / 1e6
        res.append({"start": w["start"], "hop": h, "u": w.get("u"), "planned_mbps": round(planned, 1),
                    "offered_mbps": round(got, 1), "ratio": round(got / planned, 4)})
    bad = [x for x in res if abs(x["ratio"] - 1) > STIM_TOL]
    ratios = np.array([x["ratio"] for x in res])
    return {"ok": (not bad and not missing) if res else None, "windows": len(res), "skipped_overlap": skipped,
            "no_metrics_for": sorted(missing), "ratio_min": round(float(ratios.min()), 4) if len(ratios) else None,
            "ratio_max": round(float(ratios.max()), 4) if len(ratios) else None, "out_of_tolerance": bad[:10],
            "n_out": len(bad)}


ITEMS = {"1_completeness": item_completeness, "2_accounting": item_accounting, "3_service_rate": item_service,
         "4_sender_records": item_sender, "5_load_share": item_load_share, "6_events_vs_plan": item_events,
         "7_drops_elsewhere": item_drops_elsewhere, "8_stimulus_load": item_stimulus_load}


def check(rd: Path) -> dict:
    res = {}
    for name, fn in ITEMS.items():
        try:
            res[name] = fn(rd)
        except Exception as e:  # noqa: BLE001
            res[name] = {"ok": False, "why": f"check failed: {e!r}"}
    res["ok"] = all(v["ok"] is not False for k, v in res.items() if k != "ok")
    return res


def main(argv: list[str]) -> int:
    rd = Path(argv[0])
    res = check(rd)
    flat = [{"key": k, "value": json.dumps(v, default=str)} for k, v in res.items()]
    with (rd / "health-lite.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, ["key", "value"])
        w.writeheader()
        w.writerows(flat)
    if "--json" in argv:
        Path(argv[argv.index("--json") + 1]).write_text(json.dumps(res, indent=1, default=str) + "\n")
    state = "ok" if res["ok"] else "INVALID"
    fails = [k for k, v in res.items() if k != "ok" and v["ok"] is False]
    print(f"health-lite: {state}" + (f"; failing: {', '.join(fails)}" if fails else "")
          + "; not covered: per-packet service intervals / jitter, per-packet egress identity")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
