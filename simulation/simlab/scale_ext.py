"""Limits of the testbed's configuration layer lifted for simulation runs (item 5; 10,000 clients later).

1. Address labels beyond 254 nodes / 254 traffic routes.

quiclab.runtime.node_loopback_ips (10.99.0.1-254) and traffic_route_ips (10.100.0.i / 10.101.0.i) refuse more
than 254 entries. The simulation only uses these addresses as labels (plan.txt, router-trace rows, GT-Q flow
match); they are never assigned to an ns-3 interface (links use 10.0.0.0 - 10.98.255.0, quicsim.cc). The frozen
tools (scripts/gtq.py, v3_stimuli, v4_checks) import the two functions from quiclab.runtime at call time, so
patching the module attributes covers them without changing any frozen file.

    import scale_ext      # before plan / scoring code runs; idempotent
    python3 simulation/simlab/scale_ext.py <script.py> [args]   # run a frozen script with the patches applied

Rule: entries 1-254 get exactly the original addresses, so every run with at most 254 nodes / routes is
unchanged; entry k > 254 continues in the same /16: 10.99.(j // 254).(j % 254 + 1) with j = k - 1, up to
254 * 256 = 65,024 entries (10.100 / 10.101 alike for routes).

2. Background flows per traffic event: quiclab.config.scenario caps flow_weights at 256 entries (the testbed's
qtraffic sender); the simulation's sources have no such cap (quicsim traffic.h), and the v4 planner gives one
flow per 2.5 Mb/s of background, so 300 clients already need 330. The cap is removed from the two event models
(BurstsEvent, BgEvent) at import time and the scenario models are rebuilt; validation is otherwise unchanged,
and a list of at most 256 validates exactly as before. Nothing in quiclab/ is edited.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

QUICLAB = Path(__file__).resolve().parents[2]
if str(QUICLAB) not in sys.path:
    sys.path.insert(0, str(QUICLAB))

from quiclab import runtime  # noqa: E402

MAX_ENTRIES = 254 * 256


def _addr(prefix16: str, k: int) -> str:
    j = k - 1
    if j >= MAX_ENTRIES:
        raise runtime.OrchestratorError(f"more than {MAX_ENTRIES} addresses in {prefix16}.0.0/16")
    return f"{prefix16}.{j // 254}.{j % 254 + 1}"


_orig_nodes = getattr(runtime.node_loopback_ips, "__wrapped_original__", runtime.node_loopback_ips)
_orig_routes = getattr(runtime.traffic_route_ips, "__wrapped_original__", runtime.traffic_route_ips)


def node_loopback_ips(topology):
    ordered = [nid for nid in runtime.all_node_ids(topology) if nid not in topology.switches]
    if len(ordered) <= 254:
        return _orig_nodes(topology)
    return {nid: _addr("10.99", i) for i, nid in enumerate(ordered, start=1)}


def traffic_route_ips(topology):
    if topology.traffic is None or len(topology.traffic.routes) <= 254:
        return _orig_routes(topology)
    return {name: (_addr("10.100", i), _addr("10.101", i)) for i, name in enumerate(topology.traffic.routes, start=1)}


def _lift_flow_weight_cap() -> None:
    import annotated_types
    from pydantic import BaseModel

    from quiclab.config import scenario as sc
    changed = False
    for model in (sc.BurstsEvent, sc.BgEvent):
        fi = model.model_fields["flow_weights"]
        keep = [m for m in fi.metadata if not isinstance(m, annotated_types.MaxLen)]
        if len(keep) != len(fi.metadata):
            fi.metadata[:] = keep
            changed = True
    if changed:
        models = [v for v in vars(sc).values() if isinstance(v, type) and issubclass(v, BaseModel) and v is not BaseModel]
        for m in (sc.BurstsEvent, sc.BgEvent):
            m.model_rebuild(force=True)
        for m in models:   # parents embed the event schemas: rebuild them all
            m.model_rebuild(force=True)


_lift_flow_weight_cap()

node_loopback_ips.__wrapped_original__ = _orig_nodes
traffic_route_ips.__wrapped_original__ = _orig_routes
runtime.node_loopback_ips = node_loopback_ips
runtime.traffic_route_ips = traffic_route_ips

if __name__ == "__main__":
    script = sys.argv[1]
    sys.argv = sys.argv[1:]
    sys.path.insert(0, str(Path(script).resolve().parent))
    runpy.run_path(script, run_name="__main__")
