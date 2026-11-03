#!/usr/bin/env python3
"""Run the detector matrix: every AQM x det-* scenario x repetition, then score.

    python3 scripts/det_matrix.py [--reps N] [--aqms a,b] [--scenarios a,b] [--topology base|large]
                                  [--name NAME] [--campaign DIR] [--skip-existing]

Scenarios: capacity, cbr, ppbp (det-<name>.yaml) and the event benchmark
generated from det-burst.yaml (seed = rep): burstcap, burstudp, bursttiny,
ramp, isolate, tcpcubic, tcpbbr, burstcaplowrtt, burstcaphighrtt (see
BURST_SCENARIOS).

Every run matrix gets its own folder .runs/<YYYY-MM-DD_HHMM>_<name>/ (--name,
default det-[<topology>-]<scenarios>) with a matrix.yaml manifest: name, start
and finish time, command, git commit, topology, scenarios, AQMs, reps and the
outcome of every run. Pass --campaign <folder> with --skip-existing to resume. Run ids inside are det-<scenario>-<aqm>-r<rep>;
scenario copies with the AQM swapped go to <campaign>/_gen/. Each finished run
is scored (scripts/det_eval.py score) and the per-AQM x scenario tables are
written to <campaign>/det-report.{md,csv} (burst runs: det-burst-report.{md,csv}).
"""

from __future__ import annotations

import argparse
import datetime
import random
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / ".runs"
# --topology NAME -> (topology, event-benchmark base scenario). capacity / cbr /
# ppbp exist for "base" only.
TOPOLOGIES = {
    "base": ("detector.yaml", "det-burst.yaml"),
    "large": ("detector-large.yaml", "det-burst-large.yaml"),
}
WIRE_OVERHEAD = 1.03    # measured wire rate / rendition rate (QUIC + headers)
AQMS = {
    "pfifo": {},
    "red": {},  # thresholds ~15 / 45 ms at the bottleneck capacity, set in scenario_for
    "pie": {},
    "fq_codel": {},
}
SCENARIOS = ["capacity", "cbr", "ppbp"]

# Event benchmark (configs/scenarios/det-burst.yaml base: 17.5 Mb/s bottleneck,
# u ~0.65 calm). Every scenario is a seeded random sequence of events with
# random calm gaps; each event's start and end are exact ground truth
# (det_eval.burst_truth reads the "burst u=..." / "burst-end" labels or the
# bursts / flow events back). Same seed (= rep) on every AQM.
WARMUP_S, GAP_S, TAIL_S = 15.0, (10.0, 15.0), 10.0
RAMP_STEP_S = 2.0

BURST_SCENARIOS = {
    # Bottleneck capacity drops: severity grid u x duration.
    "burstcap": {"kind": "cap", "u": (1.1, 1.3, 2.0), "d": (1, 2, 4), "repeats": 2},
    # Fixed UDP bursts on top of the video (fq_codel isolates them).
    "burstudp": {"kind": "udp", "u": (1.1, 1.3, 2.0), "d": (1, 2, 4), "repeats": 2},
    # Short transients a 1 BDP queue partly absorbs: how often do they alarm?
    "bursttiny": {"kind": "cap", "u": (1.3, 2.0), "d": (0.2, 0.5), "repeats": 5},
    # Slow capacity ramps through u = 0.9, 0.95, ..., peak, ..., 0.9 (2 s steps):
    # borderline load; truth = the time above u = 1.
    "ramp": {"kind": "ramp", "u": (1.05, 1.1, 1.2), "d": (0,), "repeats": 4},
    # One client's own access link drops (netem FIFO, no router AQM): only that
    # client may alarm. AQM-independent, so it runs once (first AQM).
    "isolate": {"kind": "access", "u": (1.3, 2.0), "d": (1, 2, 4), "repeats": 1, "per_client": True},
    # Competing elastic TCP (iperf3 bulk, one connection) for d seconds.
    "tcpcubic": {"kind": "tcp", "cc": "cubic", "u": (0,), "d": (2, 4, 8), "repeats": 5},
    "tcpbbr": {"kind": "tcp", "cc": "bbr", "u": (0,), "d": (2, 4, 8), "repeats": 5},
    # burstcap with every link delay scaled (base RTT x0.25 / x2).
    "burstcaplowrtt": {"kind": "cap", "u": (1.1, 1.3, 2.0), "d": (1, 2, 4), "repeats": 2, "rtt_scale": 0.25},
    "burstcaphighrtt": {"kind": "cap", "u": (1.1, 1.3, 2.0), "d": (1, 2, 4), "repeats": 2, "rtt_scale": 2.0},
}
AQM_INDEPENDENT = {"isolate"}


def _ramp_steps(peak: float) -> list[float]:
    up = [0.9, 0.95] + [u for u in (1.05, 1.1, 1.2) if u <= peak]
    return up + up[-2::-1]


def topology_numbers(topology: str) -> dict:
    """Burst sizing from the topology's own files: per-client wire demand of the
    clients behind the shared bottleneck, its calm capacity, access capacity."""
    topo_file, base_file = TOPOLOGIES[topology]
    topo = yaml.safe_load((ROOT / "configs" / "topologies" / topo_file).read_text())
    base = yaml.safe_load((ROOT / "configs" / "scenarios" / base_file).read_text())
    shared = {link["to"] for link in topo["links"] if link["from"] == "switch"}
    clients = {sid: sub["rate_kbps"] / 1000 * WIRE_OVERHEAD
               for sid, sub in topo["subscribers"].items() if sid in shared}
    cap = next(link["forward"]["bandwidth_mbps"] for link in base["links"]
               if (link["from"], link["to"]) == ("router", "switch"))
    return {"clients": clients, "demand": sum(clients.values()), "base": cap,
            "access": base["link_defaults"]["forward"]["bandwidth_mbps"]}


def burst_events(name: str, seed: int, topology: str = "base") -> tuple[list[dict], float]:
    """Scenario events for one event-benchmark run and its duration."""
    spec = BURST_SCENARIOS[name]
    n = topology_numbers(topology)
    DEMAND_MBPS, BASE_MBPS, ACCESS_MBPS, CLIENT_MBPS = n["demand"], n["base"], n["access"], n["clients"]
    rng = random.Random(seed)
    if spec.get("per_client"):
        # Each (u, d) cell 4 times, clients assigned round-robin in a shuffled order:
        # 24 events whatever the client count (every client 6x on base, 3x on large).
        grid = [(u, d) for u in spec["u"] for d in spec["d"]] * 4
        rng.shuffle(grid)
        clients = sorted(CLIENT_MBPS)
        rng.shuffle(clients)
        cells = [(u, d, clients[i % len(clients)]) for i, (u, d) in enumerate(grid)]
    else:
        cells = [(u, d, None) for u in spec["u"] for d in spec["d"]] * spec["repeats"]
        rng.shuffle(cells)
    t, events, udp = WARMUP_S, [], []
    cap = {"from": "router", "to": "switch"}
    for i, (u, d, client) in enumerate(cells):
        at = round(t, 3)
        if spec["kind"] == "cap":
            events += [{"at_s": at, "type": "link", **cap, "bandwidth_mbps": round(DEMAND_MBPS / u, 3),
                        "label": f"burst u={u} d={d}"},
                       {"at_s": round(at + d, 3), "type": "link", **cap, "bandwidth_mbps": BASE_MBPS,
                        "label": "burst-end"}]
        elif spec["kind"] == "access":
            link = {"from": "switch", "to": client}
            events += [{"at_s": at, "type": "link", **link, "bandwidth_mbps": round(CLIENT_MBPS[client] / u, 3),
                        "label": f"burst u={u} d={d} {client}"},
                       {"at_s": round(at + d, 3), "type": "link", **link, "bandwidth_mbps": ACCESS_MBPS,
                        "label": "burst-end"}]
        elif spec["kind"] == "udp":
            udp.append({"start_s": at, "duration_s": d, "rate_mbps": round(u * BASE_MBPS - DEMAND_MBPS, 3)})
        elif spec["kind"] == "tcp":
            events.append({"at_s": at, "type": "flow", "kind": "tcp", "id": f"tcp-{i}", "route": "shared",
                           "duration_s": d, "cc": spec["cc"]})
        else:  # ramp
            steps = _ramp_steps(u)
            above = sum(x > 1 for x in steps) * RAMP_STEP_S
            first = True
            for k, x in enumerate(steps):
                label = "ramp"
                if x > 1 and first:
                    label, first = f"burst u={u} d={above:g}", False
                elif x < 1 and not first and steps[k - 1] > 1:
                    label = "burst-end"
                events.append({"at_s": round(at + k * RAMP_STEP_S, 3), "type": "link", **cap,
                               "bandwidth_mbps": round(DEMAND_MBPS / x, 3), "label": label})
            events.append({"at_s": round(at + len(steps) * RAMP_STEP_S, 3), "type": "link", **cap,
                           "bandwidth_mbps": BASE_MBPS, "label": "ramp"})
            d = len(steps) * RAMP_STEP_S
        t += d + rng.uniform(*GAP_S)
    if udp:
        events.append({"at_s": 0, "type": "bursts", "id": "udp-bursts", "route": "shared", "bursts": udp})
    return events, round(t - GAP_S[0] + TAIL_S)


def scenario_for(name: str, aqm: str, rep: int = 1, campaign: Path = RUNS, topology: str = "base") -> Path:
    if name in BURST_SCENARIOS:
        base_file = TOPOLOGIES[topology][1]
    elif topology == "base":
        base_file = f"det-{name}.yaml"
    else:
        raise SystemExit(f"scenario {name} exists for --topology base only")
    data = yaml.safe_load((ROOT / "configs" / "scenarios" / base_file).read_text())
    if name in BURST_SCENARIOS:
        # Same seed for every AQM: each repetition plays one burst sequence on all of them.
        data["events"], data["duration_s"] = burst_events(name, seed=rep, topology=topology)
        scale = BURST_SCENARIOS[name].get("rtt_scale", 1.0)
        for link in data["links"]:
            for side in ("forward", "reverse"):
                if "delay_ms" in (link.get(side) or {}):
                    link[side]["delay_ms"] = round(link[side]["delay_ms"] * scale, 3)
    for router in data["routers"].values():
        limit = router.get("queue_limit_packets")
        router.clear()
        router.update({"aqm": aqm, "queue_limit_packets": limit, **AQMS[aqm]})
        if aqm == "red":
            bytes_per_ms = topology_numbers(topology)["base"] * 1e6 / 8 / 1000
            router.update({"red_min_bytes": int(15 * bytes_per_ms), "red_max_bytes": int(45 * bytes_per_ms)})
    out = campaign / "_gen" / f"det-{name}-{aqm}-r{rep}.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(data, sort_keys=False))
    return out


def _git_commit() -> str:
    out = subprocess.run(["git", "-C", str(ROOT), "describe", "--always", "--dirty"],
                         capture_output=True, text=True)
    return out.stdout.strip() or "unknown"


def write_manifest(campaign: Path, info: dict) -> None:
    """<campaign>/matrix.yaml: what this run matrix is, when it ran, how it went."""
    (campaign / "matrix.yaml").write_text(yaml.safe_dump(info, sort_keys=False))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--aqms", default=",".join(AQMS))
    ap.add_argument("--scenarios", default=",".join(SCENARIOS))
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--name", default=None,
                    help="matrix name; folder .runs/<YYYY-MM-DD_HHMM>_<name> (default: det-[<topology>-]<scenarios>)")
    ap.add_argument("--campaign", default=None, help="existing folder under .runs/ to resume (with --skip-existing)")
    ap.add_argument("--topology", default="base", choices=sorted(TOPOLOGIES))
    args = ap.parse_args()
    topology_file = ROOT / "configs" / "topologies" / TOPOLOGIES[args.topology][0]
    started = datetime.datetime.now()
    name = args.name or ("det-" + ("" if args.topology == "base" else f"{args.topology}-")
                         + "-".join(args.scenarios.split(",")))
    if any(c in name for c in "/\\ ") or not name:
        raise SystemExit(f"--name must be a non-empty folder name without spaces or slashes: {name!r}")
    campaign = RUNS / (args.campaign or f"{started:%Y-%m-%d_%H%M}_{name}")
    resumed = (campaign / "matrix.yaml").exists()
    campaign.mkdir(parents=True, exist_ok=True)
    print(f"campaign: {campaign}", flush=True)
    manifest = yaml.safe_load((campaign / "matrix.yaml").read_text()) if resumed else {
        "name": name,
        "started": started.isoformat(timespec="seconds"),
        "finished": None,
        "command": " ".join([Path(sys.argv[0]).name, *sys.argv[1:]]),
        "git": _git_commit(),
        "topology": args.topology,
        "topology_file": str(topology_file.relative_to(ROOT)),
        "scenarios": args.scenarios.split(","),
        "aqms": args.aqms.split(","),
        "reps": args.reps,
        "runs": {},
    }
    if resumed:
        manifest.setdefault("resumed", []).append(started.isoformat(timespec="seconds"))
        manifest["finished"] = None
    write_manifest(campaign, manifest)
    done = []
    for rep in range(1, args.reps + 1):
        for i, aqm in enumerate(args.aqms.split(",")):
            for scn in args.scenarios.split(","):
                if scn in AQM_INDEPENDENT and i > 0:
                    continue
                run_id = f"det-{scn}-{aqm}-r{rep}"
                run_dir = campaign / run_id
                if not (args.skip_existing and (run_dir / "detector" / "detections.csv").exists()):
                    scenario = scenario_for(scn, aqm, rep, campaign, args.topology)
                    print(f"== {run_id}", flush=True)
                    status = subprocess.run([sys.executable, "-m", "quiclab", "--runs-dir", str(campaign),
                                             "run", "-c", str(topology_file),
                                             "-s", str(scenario), "--run-id", run_id], cwd=ROOT)
                    if status.returncode != 0:
                        print(f"!! {run_id} failed ({status.returncode}); skipped", flush=True)
                        manifest["runs"][run_id] = f"failed ({status.returncode})"
                        write_manifest(campaign, manifest)
                        continue
                    det_eval.score(run_dir)
                    manifest["runs"][run_id] = f"done {datetime.datetime.now():%Y-%m-%dT%H:%M:%S}"
                    write_manifest(campaign, manifest)
                done.append(run_dir)
                bursts = [r for r in done if det_eval.scenario_name(r) in BURST_SCENARIOS]
                others = [r for r in done if r not in bursts]
                if others:
                    text, table = det_eval.report(others)
                    (campaign / "det-report.md").write_text(text)
                    det_eval.write_csv(campaign / "det-report.csv", table)
                if bursts:
                    text, table = det_eval.burst_report(bursts)
                    (campaign / "det-burst-report.md").write_text(text)
                    det_eval.write_csv(campaign / "det-burst-report.csv", table)
    manifest["finished"] = datetime.datetime.now().isoformat(timespec="seconds")
    write_manifest(campaign, manifest)


if __name__ == "__main__":
    main()
