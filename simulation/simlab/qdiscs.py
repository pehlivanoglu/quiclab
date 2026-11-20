#!/usr/bin/env python3
"""<sim run>/qdiscs.txt in the testbed's format, from the simulation plan (derived file; nothing re-simulated).

    python3 simulation/simlab/qdiscs.py <sim run> [...]

The testbed writes `tc qdisc show` of every interface ("== <node> <iface>", then the chain); frozen readers
(grouping_score.egress_aqm) take the AQM leaf per interface from it. Here: one block per egress of the plan
(sim/plan.txt "egress" records; interface names from quiclab.runtime.edge_interfaces), with a
"qdisc <aqm> 20: ..." line where the egress has an AQM (pfifo / codel / pie / red); the default queue of a
direction without AQM gets no leaf line, as on the testbed (htb / netem only). FLAG: a description of what
the simulation configured, not a kernel dump.
"""

from __future__ import annotations

import sys
from pathlib import Path

QUICLAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(QUICLAB))

from quiclab.config.schema import load_topology  # noqa: E402
from quiclab.runtime import edge_interfaces  # noqa: E402


def write(run: Path) -> None:
    topo = load_topology(run / "topology.yaml")
    iface = {}
    for e in edge_interfaces(topo):
        iface[(e.a, e.b)] = e.a_iface
        iface[(e.b, e.a)] = e.b_iface
    out = []
    for line in (run / "sim" / "plan.txt").read_text().splitlines():
        if not line.startswith("egress "):
            continue
        kv = dict(w.split("=", 1) for w in line.split()[1:])
        node, peer, aqm = kv["node"], kv["peer"], kv["aqm"]
        out.append(f"== {node} {iface[(node, peer)]}")
        out.append("qdisc htb 5: root (simulation: ns-3 point-to-point device at the plan's rate)")
        if aqm != "fifo":
            out.append(f"qdisc {aqm} 20: parent 5:1 limit {kv['limit_p']}p (simulation: ns-3 queue disc)")
    (run / "qdiscs.txt").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        write(Path(p))
        print(f"{p}/qdiscs.txt")
