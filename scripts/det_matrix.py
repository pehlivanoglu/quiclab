#!/usr/bin/env python3
"""Run the detector matrix: every AQM x det-* scenario x repetition, then score.

    python3 scripts/det_matrix.py [--reps N] [--aqms a,b] [--scenarios a,b] [--topology base|large|split]
                                  [--name NAME] [--campaign DIR] [--skip-existing]

Scenarios: capacity, cbr, ppbp (det-<name>.yaml) and the event benchmark
generated from det-burst.yaml (seed = rep, see BURST_SCENARIOS): burstcap,
burstudp, bursttiny, ramp, isolate, tcpcubic, tcpbbr, burstcaplowrtt,
burstcaphighrtt, burstlong, burstcapshallow, burstcapdeep, onoff, revdelay,
the no-congestion false-alarm runs calm030, calm065, calm090,
calmcbr090, delaystep, randloss, and for --topology split (upstream + two
downstream bottlenecks, detector-split.yaml) splitcap, splitudp. Other event
scenarios on split load the upstream bottleneck.

Every run matrix gets its own folder .runs/<YYYY-MM-DD_HHMM>_<name>/ (--name,
default det-[<topology>-]<scenarios>) with a matrix.yaml manifest: name, start
and finish time, command, git commit, topology, scenarios, AQMs, reps and the
outcome of every run. Pass --campaign <folder> with --skip-existing to resume. Run ids inside are det-<scenario>-<aqm>-r<rep>;
scenario copies with the AQM swapped go to <campaign>/_gen/. Each finished run
is scored (scripts/det_eval.py score) and the per-AQM x scenario tables are
written to <campaign>/det-report.{md,csv} (burst runs: det-burst-report.{md,csv});
the same against the measured truth (runs with the OWD oracle) go to
det-report-measured.* and det-burst-report-measured.*.
"""

from __future__ import annotations

import argparse
import datetime
import random
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / ".runs"
# --topology NAME -> (topology, event-benchmark base scenario, bottleneck hops
# {target: (from, to, cross-traffic route)}, default target). capacity / cbr /
# ppbp exist for "base" only.
TOPOLOGIES = {
    "base": ("detector.yaml", "det-burst.yaml", {"main": ("router", "switch", "shared")}, "main"),
    "large": ("detector-large.yaml", "det-burst-large.yaml", {"main": ("router", "switch", "shared")}, "main"),
    # Upstream r1 -> r2 (both groups), downstream r2 -> switch-a / switch-b (one group each).
    "split": ("detector-split.yaml", "det-burst-split.yaml",
              {"up": ("r1", "r2", "shared"), "a": ("r2", "switch-a", "cross-a"), "b": ("r2", "switch-b", "cross-b")},
              "up"),
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
    # Long congestion (the method-limit test; SBD baselines need 10-17 s of history).
    "burstlong": {"kind": "cap", "u": (1.1, 1.3, 2.0), "d": (10, 30, 60), "repeats": 1},
    # burstcap with the bottleneck queue scaled: shallow (~0.25 BDP, loss before delay) / deep (~4 BDP).
    "burstcapshallow": {"kind": "cap", "u": (1.1, 1.3, 2.0), "d": (1, 2, 4), "repeats": 2, "queue_scale": 0.25},
    "burstcapdeep": {"kind": "cap", "u": (1.1, 1.3, 2.0), "d": (1, 2, 4), "repeats": 2, "queue_scale": 4.0},
    # On/off UDP cross traffic: 2 s on, 4 s off, light / medium / heavy levels in seeded order.
    "onoff": {"kind": "udp", "u": (1.1, 1.3, 2.0), "d": (2,), "repeats": 6, "gap_s": 4.0},
    # burstcap with each client's reverse (ACK) path delay raised by its own amount
    # (cycled over the shared clients): asymmetric RTTs, forward truth unchanged.
    "revdelay": {"kind": "cap", "u": (1.1, 1.3, 2.0), "d": (1, 2, 4), "repeats": 2, "rev_extra_ms": (0, 20, 40, 80)},
    # No congestion at all: every alarm is a false alarm (scored per minute of clear time).
    # Calm load set by the bottleneck capacity (u = video / capacity).
    "calm030": {"kind": "calm", "base_u": 0.3, "duration_s": 120},
    "calm065": {"kind": "calm", "duration_s": 120},
    "calm090": {"kind": "calm", "base_u": 0.9, "duration_s": 120},
    # Same u 0.9, reached by constant UDP cross traffic instead of a smaller link.
    "calmcbr090": {"kind": "calm", "cbr_u": 0.9, "duration_s": 120},
    # Propagation delay steps on pub -> router (every client), forward or reverse, held d s:
    # RTT rises, nothing queues.
    "delaystep": {"kind": "delay", "u": (("forward", 20), ("forward", 50), ("reverse", 20), ("reverse", 50)),
                  "d": (5,), "repeats": 3},
    # Random loss on pub -> router (every client), held d s, no queue.
    "randloss": {"kind": "loss", "u": (0.5, 1.0, 2.0), "d": (10,), "repeats": 3},
    # --topology split: capacity drops / UDP bursts on one bottleneck at a time, and on the
    # upstream and group a's downstream link at once ("a+up": two congested hops in series).
    "splitcap": {"kind": "cap", "u": (1.3, 2.0), "d": (1, 2, 4), "repeats": 1, "targets": ("up", "a", "b", "a+up")},
    "splitudp": {"kind": "udp", "u": (1.3, 2.0), "d": (1, 2, 4), "repeats": 1, "targets": ("up", "a", "b")},
}
AQM_INDEPENDENT = {"isolate"}
FEED_DELAY_MS = 5  # delay both ways of the publisher's first link in det-burst*.yaml (delaystep, randloss)


def _ramp_steps(peak: float) -> list[float]:
    up = [0.9, 0.95] + [u for u in (1.05, 1.1, 1.2) if u <= peak]
    return up + up[-2::-1]


def topology_numbers(topology: str) -> dict:
    """Burst sizing from the topology's own files: per bottleneck target its link,
    cross-traffic route, clients behind it (wire demand) and calm capacity; the
    publisher's first link (feed), each client's access link and access capacity."""
    topo_file, base_file, targets, default = TOPOLOGIES[topology]
    topo = yaml.safe_load((ROOT / "configs" / "topologies" / topo_file).read_text())
    base = yaml.safe_load((ROOT / "configs" / "scenarios" / base_file).read_text())
    pub = next(iter(topo["publishers"]))
    adj = defaultdict(set)
    for link in topo["links"]:
        adj[link["from"]].add(link["to"])
        adj[link["to"]].add(link["from"])
    parent, todo = {pub: None}, [pub]  # BFS tree from the publisher (det_eval.path_hops does the same)
    for node in todo:
        for nb in sorted(adj[node]):
            if nb not in parent:
                parent[nb] = node
                todo.append(nb)

    def hops(node: str) -> set[tuple[str, str]]:
        out = set()
        while node != pub:
            out.add((parent[node], node))
            node = parent[node]
        return out

    rates = {sid: sub["rate_kbps"] / 1000 * WIRE_OVERHEAD for sid, sub in topo["subscribers"].items()}
    caps = {(link["from"], link["to"]): link["forward"].get("bandwidth_mbps") for link in base["links"]}
    hop_info = {}
    for name, (a, b, route) in targets.items():
        clients = {sid: r for sid, r in rates.items() if (a, b) in hops(sid)}
        hop_info[name] = {"link": {"from": a, "to": b}, "route": route, "clients": clients,
                          "demand": sum(clients.values()), "base": caps[(a, b)]}
    shared = {sid: r for h in hop_info.values() for sid, r in h["clients"].items()}
    return {"hops": hop_info, "default": default, "clients": shared,
            "feed": {"from": pub, "to": next(link["to"] for link in topo["links"] if link["from"] == pub)},
            "uplink": {sid: parent[sid] for sid in rates},
            "access": base["link_defaults"]["forward"]["bandwidth_mbps"]}


def burst_events(name: str, seed: int, topology: str = "base") -> tuple[list[dict], float]:
    """Scenario events for one event-benchmark run and its duration."""
    spec = BURST_SCENARIOS[name]
    n = topology_numbers(topology)
    hops, feed = n["hops"], n["feed"]
    base = {t: base_mbps(name, topology, t) for t in hops}
    default = hops[n["default"]]
    rng = random.Random(seed)
    if spec["kind"] == "calm":
        events = []
        if "cbr_u" in spec:
            events.append({"at_s": 0, "type": "flow", "kind": "udp", "id": "cbr", "route": default["route"],
                           "duration_s": spec["duration_s"],
                           "rate_mbps": round(spec["cbr_u"] * base[n["default"]] - default["demand"], 3)})
        return events, spec["duration_s"]
    if spec.get("per_client"):
        # Each (u, d) cell 4 times, clients assigned round-robin in a shuffled order:
        # 24 events whatever the client count (every client 6x on base, 3x on large).
        grid = [(u, d) for u in spec["u"] for d in spec["d"]] * 4
        rng.shuffle(grid)
        clients = sorted(n["clients"])
        rng.shuffle(clients)
        cells = [(u, d, clients[i % len(clients)]) for i, (u, d) in enumerate(grid)]
    else:
        targets = spec.get("targets", (n["default"],))
        cells = [(u, d, tgt) for u in spec["u"] for d in spec["d"] for tgt in targets] * spec["repeats"]
        rng.shuffle(cells)
    t, events, udp = WARMUP_S, [], defaultdict(list)
    for i, (u, d, target) in enumerate(cells):
        at = round(t, 3)
        if spec["kind"] == "cap":
            for tgt in target.split("+"):
                h = hops[tgt]
                events += [{"at_s": at, "type": "link", **h["link"], "bandwidth_mbps": round(h["demand"] / u, 3),
                            "label": f"burst u={u} d={d}" + (f" {tgt}" if len(hops) > 1 else "")},
                           {"at_s": round(at + d, 3), "type": "link", **h["link"], "bandwidth_mbps": base[tgt],
                            "label": "burst-end"}]
        elif spec["kind"] == "access":
            link, rate = {"from": n["uplink"][target], "to": target}, n["clients"][target]
            events += [{"at_s": at, "type": "link", **link, "bandwidth_mbps": round(rate / u, 3),
                        "label": f"burst u={u} d={d} {target}"},
                       {"at_s": round(at + d, 3), "type": "link", **link, "bandwidth_mbps": n["access"],
                        "label": "burst-end"}]
        elif spec["kind"] == "delay":
            direction, extra = u
            events += [{"at_s": at, "type": "link", **feed, "direction": direction,
                        "delay_ms": FEED_DELAY_MS + extra, "label": f"delay {direction} +{extra}ms"},
                       {"at_s": round(at + d, 3), "type": "link", **feed, "direction": direction,
                        "delay_ms": FEED_DELAY_MS, "label": "delay-end"}]
        elif spec["kind"] == "loss":
            events += [{"at_s": at, "type": "link", **feed, "loss_pct": u, "label": f"loss {u}%"},
                       {"at_s": round(at + d, 3), "type": "link", **feed, "loss_pct": 0, "label": "loss-end"}]
        elif spec["kind"] == "udp":
            h = hops[target]
            udp[h["route"]].append({"start_s": at, "duration_s": d, "rate_mbps": round(u * base[target] - h["demand"], 3)})
        elif spec["kind"] == "tcp":
            events.append({"at_s": at, "type": "flow", "kind": "tcp", "id": f"tcp-{i}", "route": default["route"],
                           "duration_s": d, "cc": spec["cc"]})
        else:  # ramp
            cap, base_d = default["link"], base[n["default"]]
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
                               "bandwidth_mbps": round(default["demand"] / x, 3), "label": label})
            events.append({"at_s": round(at + len(steps) * RAMP_STEP_S, 3), "type": "link", **cap,
                           "bandwidth_mbps": base_d, "label": "ramp"})
            d = len(steps) * RAMP_STEP_S
        t += d + (spec["gap_s"] if "gap_s" in spec else rng.uniform(*GAP_S))
    for route, bursts in udp.items():
        events.append({"at_s": 0, "type": "bursts", "id": "udp-bursts" if route == "shared" else f"udp-{route}",
                       "route": route, "bursts": bursts})
    return events, round(t - spec.get("gap_s", GAP_S[0]) + TAIL_S)


def base_mbps(name: str, topology: str, target: str) -> float:
    """Calm capacity of one bottleneck: the base file's, or its video demand / base_u."""
    h, spec = topology_numbers(topology)["hops"][target], BURST_SCENARIOS.get(name, {})
    return round(h["demand"] / spec["base_u"], 3) if "base_u" in spec else h["base"]


def scenario_for(name: str, aqm: str, rep: int = 1, campaign: Path = RUNS, topology: str = "base") -> Path:
    if name in BURST_SCENARIOS:
        base_file = TOPOLOGIES[topology][1]
    elif topology == "base":
        base_file = f"det-{name}.yaml"
    else:
        raise SystemExit(f"scenario {name} exists for --topology base only")
    data = yaml.safe_load((ROOT / "configs" / "scenarios" / base_file).read_text())
    n = topology_numbers(topology)
    if name in BURST_SCENARIOS:
        spec = BURST_SCENARIOS[name]
        unknown = set(t for tgt in spec.get("targets", ()) for t in tgt.split("+")) - set(n["hops"])
        if unknown:
            raise SystemExit(f"scenario {name} targets {sorted(unknown)}: not bottlenecks of --topology {topology}")
        # Same seed for every AQM: each repetition plays one burst sequence on all of them.
        data["events"], data["duration_s"] = burst_events(name, seed=rep, topology=topology)
        scale = spec.get("rtt_scale", 1.0)
        shared = sorted(n["clients"])
        caps = {(h["link"]["from"], h["link"]["to"]): base_mbps(name, topology, t) for t, h in n["hops"].items()}
        for link in data["links"]:
            ends = (link["from"], link["to"])
            for side in ("forward", "reverse"):
                if "delay_ms" in (link.get(side) or {}):
                    link[side]["delay_ms"] = round(link[side]["delay_ms"] * scale, 3)
            if ends in caps:
                link["forward"]["bandwidth_mbps"] = caps[ends]
            if (extras := spec.get("rev_extra_ms")) and link["to"] in shared and link["from"] == n["uplink"][link["to"]]:
                extra = extras[shared.index(link["to"]) % len(extras)]
                link["reverse"]["delay_ms"] = round(link["reverse"]["delay_ms"] + extra, 3)
            if spec["kind"] == "loss" and ends == (n["feed"]["from"], n["feed"]["to"]):
                link["forward"]["loss_pct"] = 0  # netem loss must exist at t=0 to be editable live
    for router in data["routers"].values():
        limit = router.get("queue_limit_packets")
        if limit and name in BURST_SCENARIOS and "queue_scale" in BURST_SCENARIOS[name]:
            limit = max(4, round(limit * BURST_SCENARIOS[name]["queue_scale"]))
        router.clear()
        router.update({"aqm": aqm, "queue_limit_packets": limit, **AQMS[aqm]})
        if aqm == "red":
            # Thresholds ~15 / 45 ms at the smallest bottleneck's capacity.
            bytes_per_ms = min(h["base"] for h in n["hops"].values()) * 1e6 / 8 / 1000
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
                # Burst runs have bursts.csv; the rest (capacity/cbr/ppbp, calm, delaystep, randloss)
                # are onset / false-alarm scored only.
                for tag, suffix in (("detector", ""), ("detector/measured", "-measured")):
                    have = [r for r in done if (r / tag / "truth.csv").exists()]
                    bursts = [r for r in have if (r / tag / "bursts.csv").exists()]
                    others = [r for r in have if r not in bursts]
                    if others:
                        text, table = det_eval.report(others, tag=tag)
                        (campaign / f"det-report{suffix}.md").write_text(text)
                        det_eval.write_csv(campaign / f"det-report{suffix}.csv", table)
                    if bursts:
                        text, table = det_eval.burst_report(bursts, tag=tag)
                        (campaign / f"det-burst-report{suffix}.md").write_text(text)
                        det_eval.write_csv(campaign / f"det-burst-report{suffix}.csv", table)
    manifest["finished"] = datetime.datetime.now().isoformat(timespec="seconds")
    write_manifest(campaign, manifest)


if __name__ == "__main__":
    main()
