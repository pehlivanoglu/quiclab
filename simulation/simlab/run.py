#!/usr/bin/env python3
"""One simulation run: plan from a testbed run, ns-3 quicsim, post-processing.

    python3 simulation/simlab/run.py <testbed run dir> <sim run dir> --seed N

Launch batches of these through reports/batch_guard.py (auto --session sim --cores 1); this
script itself runs one simulation on one core. Post-processing writes what the testbed
writes at teardown: gtq-health.csv (quiclab.router_trace.health, unchanged), plus
sim/meta.json (wall time, peak memory, output size) for the stage reports.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import resource
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scale_ext  # noqa: E402,F401  (first: lifts the 254-address / 256-flow limits; runs <= 254 unchanged)
import plan as P  # noqa: E402

from quiclab import router_trace  # noqa: E402
from quiclab.config.scenario import load_scenario  # noqa: E402
from quiclab.config.schema import load_topology  # noqa: E402
from quiclab.runtime import node_loopback_ips  # noqa: E402

BINARY = HERE.parent / "third_party" / "ns-3.48" / "build" / "scratch" / "quicsim" / "ns3.48-quicsim-optimized"
LIB_DIR = HERE.parent / "third_party" / "ns-3.48" / "build" / "lib"
MIN_FREE_GB = 30


def gtq_health(run_dir: Path) -> str:
    topo = load_topology(run_dir / "topology.yaml")
    scen = load_scenario(run_dir / "scenario.yaml", topo)
    on = router_trace.enabled(topo)
    counts_csv = run_dir / router_trace.TRACE_DIR / "tracer-counts.csv"
    counts, tracers = [], {}
    if on and counts_csv.exists():
        for r in csv.DictReader(counts_csv.open()):
            row = {k: (int(v) if v.lstrip("-").isdigit() else v) for k, v in r.items()}
            counts.append(row)
            t = tracers.setdefault(row["router"], router_trace.Tracer(
                router=row["router"], ifaces={}, hops={}, raw=run_dir / "none", log=run_dir / "none",
                started_ns=row["tracer_start_ns"], stopped_clean=True))
            t.ifaces[row["ifindex"]] = row["iface"]
        for r in csv.DictReader((run_dir / router_trace.TRACE_DIR / "interfaces.csv").open()):
            a, b = r["hop"].split("->")
            tracers[r["router"]].hops[r["iface"]] = (a, b)
    ips = node_loopback_ips(topo)
    flows = {sid: (sub.connects_to, ips[sub.connects_to], ips[sid]) for sid, sub in topo.subscribers.items()}
    _, line = router_trace.health(run_dir, on=on, scenario=scen, epoch_mono_ns=P.MONO0_NS + round(P.EPOCH_S * 1e9),
                                  tracers=list(tracers.values()), counts=counts, flows=flows)
    return line


SOURCES = HERE.parent / "ns3" / "quicsim"


def build_id() -> dict:
    """Which simulator produced a run: sha256 of the quicsim binary and of our simulator sources
    (ns3/quicsim/*.{cc,h}, the qvideo headers it includes, simlab/plan.py, patches/*.patch)."""
    import hashlib
    src = hashlib.sha256()
    files = sorted(SOURCES.glob("*.cc")) + sorted(SOURCES.glob("*.h")) + sorted((SOURCES / "qvideo").glob("*.h")) \
        + [HERE / "plan.py"] + sorted((HERE.parent / "patches").glob("*.patch"))
    for f in files:
        src.update(f.name.encode() + b"\0" + f.read_bytes())
    return {"binary_sha256": hashlib.sha256(BINARY.read_bytes()).hexdigest()[:16],
            "lib_internet_sha256": hashlib.sha256((LIB_DIR / "libns3.48-internet-optimized.so").read_bytes()).hexdigest()[:16],
            "sources_sha256": src.hexdigest()[:16]}


def dir_bytes(p: Path) -> int:
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("testbed_run", type=Path)
    ap.add_argument("sim_run", type=Path)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--ack", default="spec", help="delayed-ACK profile (plan.py)")
    ap.add_argument("--trace", default="full", help="plan.py --trace: full / sample / none")
    ap.add_argument("--ports", default="global", help="plan.py --ports: global / route / reuse")
    ap.add_argument("--fast-links", action="store_true", help="plan.py --fast-links (stage C, 300-client test)")
    ap.add_argument("--no-health", action="store_true", help="skip the frozen GT-Q health check here (stage C: scoring queue)")
    a = ap.parse_args(argv)
    free_gb = shutil.disk_usage("/").free / 1e9
    if free_gb < MIN_FREE_GB:
        sys.exit(f"free disk {free_gb:.0f} GB < {MIN_FREE_GB} GB: not starting")
    if a.sim_run.exists() and any(a.sim_run.iterdir()):
        sys.exit(f"{a.sim_run} exists and is not empty")
    P.main([str(a.testbed_run), str(a.sim_run), "--seed", str(a.seed), "--ack", a.ack]
           + (["--trace", a.trace] if a.trace != "full" else []) + (["--ports", a.ports] if a.ports != "global" else [])
           + (["--fast-links"] if a.fast_links else []))
    (a.sim_run / "logs").mkdir(exist_ok=True)
    env = {"LD_LIBRARY_PATH": str(LIB_DIR)}
    if os.environ.get("QUICSIM_GLOBAL_ROUTING"):   # test only (fixed-stream check, NOTES.md)
        env["QUICSIM_GLOBAL_ROUTING"] = "1"
    if os.environ.get("QUICSIM_EXTRA_RVS"):        # test only (fixed-stream check, NOTES.md)
        env["QUICSIM_EXTRA_RVS"] = os.environ["QUICSIM_EXTRA_RVS"]
    t0 = time.time()
    with (a.sim_run / "logs" / "quicsim.log").open("w") as log:
        proc = subprocess.run([str(BINARY), f"--plan={a.sim_run / 'sim' / 'plan.txt'}", f"--out={a.sim_run}"],
                              stdout=log, stderr=subprocess.STDOUT, env=env)
    wall = time.time() - t0
    rss_mb = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024
    if proc.returncode != 0:
        sys.exit(f"quicsim failed ({proc.returncode}); see {a.sim_run / 'logs' / 'quicsim.log'}")
    health = "not run here (--no-health)" if a.no_health else gtq_health(a.sim_run)
    done = [ln for ln in (a.sim_run / "logs" / "quicsim.log").read_text().splitlines() if ln.startswith("quicsim done:")]
    tail = dict(kv.strip().rsplit(" ", 1) for kv in done[-1].split(",")[1:]) if done else {}
    late = int(tail["late_arrivals"]) if "late_arrivals" in tail else None   # records past the 10 s horizon (E-horizon); expected 0, non-zero is a finding
    import qdiscs
    qdiscs.write(a.sim_run)   # derived: each egress's AQM in the testbed's qdiscs.txt format (frozen SETS scorer)
    meta = {"testbed_run": str(a.testbed_run.resolve()), "seed": a.seed, "ack": a.ack, "wall_s": round(wall, 1),
            "peak_rss_mb": round(rss_mb, 1), "late_arrivals": late, "bytes": dir_bytes(a.sim_run), "gtq_health": health,
            "build": build_id()}
    (a.sim_run / "sim" / "meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(json.dumps(meta))


if __name__ == "__main__":
    main(sys.argv[1:])
