#!/usr/bin/env python3
"""Suite v4 run checks on top of the v3 gate checks (scripts/v3_gate.py). Reads only what
a run wrote; changes nothing.

    .venv/bin/python3 scripts/v4_checks.py <run> [<run> ...]      # one line per run, writes <run>/v4-checks.json

 path   (T-HAYES, spec 2.5) every group crosses exactly its four links: per shaped
        bottleneck egress, the clients whose loopback is the destination of a publisher
        packet in the GT-Q trace = the plan's clients of that egress.
 pause  (pause stimulus) the paused client gets no frame produced in [start, resume),
        resume = the first keyframe due at or after the end, and frames again after it
        (publishers/<pub>/<client>-frames.csv, send_us on the stream clock).
 salvo  (shorttcp) every short TCP flow connected; per stimulus the bytes sent and the
        share of flows that finished (<run>/traffic/<id>-flows.csv). Gating: connections only.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _json(p: Path) -> dict | list:
    return json.loads(p.read_text()) if p.exists() else {}


def stream_start_us(rd: Path) -> int | None:
    for row in csv.DictReader((rd / "events.csv").open()):
        if row["event"] == "epoch":
            for part in row["detail"].split():
                if part.startswith("stream_start_unix_us="):
                    return int(part.split("=", 1)[1])
    return None


def check_path(rd: Path, plan: dict) -> dict | None:
    if plan.get("topology") != "hayes":
        return None
    from quiclab.config.schema import load_topology
    from quiclab.runtime import node_loopback_ips
    topo = load_topology(rd / "topology.yaml")
    ips = node_loopback_ips(topo)
    pub = next(iter(topo.publishers))
    who = {ips[s]: s for s in topo.subscribers if s != "sub-ctrl"}
    ifaces = {r["hop"]: (r["router"], r["iface"]) for r in csv.DictReader((rd / "router-trace" / "interfaces.csv").open())}
    out, ok = {}, True
    for name, e in plan["egress"].items():
        if not e.get("shaped", True):
            continue
        if e["hop"] not in ifaces:
            out[name] = {"ok": False, "why": "egress not traced"}
            ok = False
            continue
        router, iface = ifaces[e["hop"]]
        x = pd.read_csv(rd / "router-trace" / f"{iface}-packets.csv", usecols=["saddr", "daddr"],
                        dtype=str, keep_default_na=False)
        seen = sorted({who[dst] for dst in x.loc[x.saddr == ips[pub], "daddr"].unique() if dst in who})
        good = seen == sorted(e["clients"])
        out[name] = {"hop": e["hop"], "seen": seen, "planned": sorted(e["clients"]), "ok": good}
        ok &= good
    return {"ok": ok, "egress": out}


def check_pause(rd: Path, plan: dict, wins: list[dict]) -> dict | None:
    pauses = [w for w in wins if w.get("stimulus_type") == "pause"]
    if not pauses:
        return None
    t0 = stream_start_us(rd)
    topo = yaml.safe_load((rd / "topology.yaml").read_text())
    pub = next(iter(topo["publishers"]))
    fps = topo["publishers"][pub].get("fps", 30)
    gop_ms = topo["publishers"][pub].get("gop_ms", 1000)
    out, ok = [], True
    for w in pauses:
        sid = w["target"]
        f = pd.read_csv(rd / "publishers" / pub / f"{sid}-frames.csv")
        t = (f.send_us - t0) / 1e6
        key_t = t[f.keyframe == 1]
        resume = float(key_t[key_t >= w["end"] - 1e-3].min()) if (key_t >= w["end"] - 1e-3).any() else None
        inside = int(((t >= w["start"]) & (t < (resume if resume is not None else w["end"]))).sum())
        after = int((t >= (resume or w["end"])).sum())
        good = inside == 0 and resume is not None and after > 0 and resume - w["end"] <= gop_ms / 1000 + 1 / fps
        out.append({"client": sid, "start": w["start"], "end": w["end"], "resume": resume,
                    "frames_inside": inside, "frames_after": after, "ok": bool(good)})
        ok &= good
    return {"ok": bool(ok), "pauses": out}


def check_salvo(rd: Path, wins: list[dict]) -> dict | None:
    files = sorted((rd / "traffic").glob("salvo*-flows.csv"))
    if not files:
        return None
    out, ok = [], True
    for p in files:
        f = pd.read_csv(p)
        good = bool((f.error == 0).all() and (f.connect_us > 0).all())
        out.append({"id": p.name[:-len("-flows.csv")], "flows": len(f), "connected": int((f.connect_us > 0).sum()),
                    "finished": int((f.done_us > 0).sum()), "planned_bytes": int(f.bytes.sum()),
                    "sent_bytes": int(f.sent_bytes.sum()), "ok": good})
        ok &= good
    return {"ok": ok, "salvos": out}


def run_checks(rd: Path) -> dict:
    rd = Path(rd)
    plan = _json(rd / "v3-plan.json")
    wins = _json(rd / "grouping" / "windows.json") or []
    out = {"run": rd.name}
    for name, fn in (("path", lambda: check_path(rd, plan)), ("pause", lambda: check_pause(rd, plan, wins)),
                     ("salvo", lambda: check_salvo(rd, wins))):
        try:
            out[name] = fn()
        except Exception as e:  # noqa: BLE001
            out[name] = {"ok": False, "error": repr(e)}
    (rd / "v4-checks.json").write_text(json.dumps(out, indent=1, default=str))
    return out


def _mark(c) -> str:
    return "-" if not isinstance(c, dict) else ("ok" if c.get("ok") else "FAIL")


def line(res: dict) -> str:
    return "v4 checks: " + "; ".join(f"{k} {_mark(res.get(k))}" for k in ("path", "pause", "salvo"))


def report(run_dirs: list[Path]) -> tuple[bool, str]:
    """(all v4 checks that apply hold, markdown section)."""
    L = ["", "## Suite v4 checks (path: T-HAYES routing; pause: no frame in the window; salvo: flows connected)", "",
         "| run | path | pause | salvo | details |", "|---|---|---|---|---|"]
    ok = True
    for rd in map(Path, run_dirs):
        if not (rd / "events.csv").exists():
            continue
        r = run_checks(rd)
        for k in ("path", "pause", "salvo"):
            if isinstance(r.get(k), dict) and not r[k].get("ok"):
                ok = False
        det = []
        if r.get("path"):
            det += [f"{n}: {v.get('seen')}" for n, v in (r["path"].get("egress") or {}).items() if not v.get("ok")]
        if r.get("pause"):
            det += [f"{p['client']} {p['start']}-{p['end']} resume {p['resume']} inside {p['frames_inside']}"
                    for p in r["pause"].get("pauses", [])]
        if r.get("salvo"):
            det += [f"{s['id']}: {s['connected']}/{s['flows']} connected, {s['finished']} finished, "
                    f"{s['sent_bytes']}/{s['planned_bytes']} B" for s in r["salvo"].get("salvos", [])]
        L.append(f"| {rd.name} | {_mark(r.get('path'))} | {_mark(r.get('pause'))} | {_mark(r.get('salvo'))} | "
                 f"{'; '.join(det) or '-'} |")
    return ok, "\n".join(L) + "\n"


def main(argv: list[str]) -> int:
    for a in argv:
        print(Path(a).name, line(run_checks(Path(a))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
