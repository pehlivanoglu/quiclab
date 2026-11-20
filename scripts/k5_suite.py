#!/usr/bin/env python3
"""K5-sender campaign: sender policy and CC-driven adaptation (user's K5-sender note, Part 3, 2026-11-17).

    .venv/bin/python3 scripts/k5_suite.py --plan-only --set K5 --campaign <scratch dir>
    .venv/bin/python3 scripts/k5_suite.py --run --set K5                       # the user starts it, after K3
    .venv/bin/python3 scripts/k5_suite.py --run --set K5 --campaign .runs/<ts>_v4-K5   # resume

Runs on suite v4's planner and runner unchanged (scripts/v4_suite.py is not edited; K1-K3 plans stay byte-identical).
The sender settings are publisher fields of the topology (quiclab.config.schema.PublisherConfig): send_buffer_ms,
and for adaptation adapt_x = 0.85 (P), adapt_floor = 0.3 (P) (user decision 2026-11-17, evidence
reports/adapt-whatif-2026-11-17). Fixed: DEF point (s 0.30, U 0.50), seeds 1 and 2, synchronised keyframes,
BBR and Copa in every block, AQMs pfifo / codel / pie / red (no fq_codel, no cake). One send_buffer_ms per run.

Blocks (0 = unlimited):
  S1  S-BURST   off  600, 3000, 0   all four AQMs, BBR and Copa                         48
  S2  S-BURST   off  1000           pie, red; Copa only (missing reference cells)          4
  A1  S-BURST   on   1000, 3000     all four                                              32
  P1  S-PERSIST off and on, 1000 and 3000, pfifo / codel (BBR off 1000 = K2 N2, left out)  28
  G1  H-HIERL   on   1000           all four                                              16
  G2  H-HIERL   off  1000           BBR red; Copa pie, red (missing reference cells)        6
  G3  H-HIERL   off  3000           pfifo, codel                                           8
Reference cells not re-run: S-BURST off 1000 BBR pfifo / codel / pie / red = K1 A2 (seeds 1-5); Copa pfifo / codel =
K3 C1 (not run yet: exists once K3 has run); S-PERSIST off 1000 BBR pfifo / codel = K2 N2 (seeds 1-2); H-HIERL off
1000 BBR pfifo / codel / pie = K1 A4 (seeds 1-5), Copa pfifo / codel = K3 C1.
Gate first (automatic stop on failure): one CALM per topology (T-BASE, T-SPLIT4L) with each congestion controller,
and one S-BURST run with adaptation on (send_buffer_ms 1000), pfifo, one seed.
Order: all seed 1 in block order S1, S2, A1, P1, G1, G2, G3, then all seed 2 (v4_suite.plan_all).
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import v4_suite as v4   # noqa: E402

K5_KEYS = ("send_buffer_ms", "adapt_x", "adapt_floor")
ADAPT_X, ADAPT_FLOOR = 0.85, 0.3        # (P) user decision 2026-11-17
AQ4 = ("pfifo", "codel", "pie", "red")
PC = ("pfifo", "codel")
SEEDS = (1, 2)
CCS = ("bbr", "copa")

_topo_of_v4 = v4.topo_of


def topo_of_k5(c, seed):
    """v4's topology, with the K5 sender settings moved from the cell's opts into the publisher."""
    k5 = {k: c.opts[k] for k in K5_KEYS if k in c.opts}
    if not k5:
        return _topo_of_v4(c, seed)
    t = _topo_of_v4(dataclasses.replace(c, opts={k: v for k, v in c.opts.items() if k not in K5_KEYS}), seed)
    for pub in t.topo["publishers"].values():
        pub.update(k5)
    return t


def policy(cc: str, buf: int, on: bool) -> tuple[str, dict]:
    o = {} if cc == "bbr" else {"cc": "copa"}
    o["send_buffer_ms"] = buf
    if on:
        o.update(adapt_x=ADAPT_X, adapt_floor=ADAPT_FLOOR)
    return f"{cc}-b{buf}-{'on' if on else 'off'}", o


def cell(block, rtype, kind, aqms, cc, buf, on):
    v, o = policy(cc, buf, on)
    return v4.Cell(block, rtype, v, kind, aqms, seeds=SEEDS, opts=o)


def k5() -> list:
    out = []
    out += [cell("S1", "sburst", "base", AQ4, cc, buf, False) for cc in CCS for buf in (600, 3000, 0)]
    out += [cell("S2", "sburst", "base", ("pie", "red"), "copa", 1000, False)]
    out += [cell("A1", "sburst", "base", AQ4, cc, buf, True) for cc in CCS for buf in (1000, 3000)]
    out += [cell("P1", "spersist", "base", PC, cc, buf, on) for cc in CCS for on in (False, True) for buf in (1000, 3000)
            if not (cc == "bbr" and not on and buf == 1000)]
    out += [cell("G1", "hhier", "split4l", AQ4, cc, 1000, True) for cc in CCS]
    out += [cell("G2", "hhier", "split4l", ("red",), "bbr", 1000, False),
            cell("G2", "hhier", "split4l", ("pie", "red"), "copa", 1000, False)]
    out += [cell("G3", "hhier", "split4l", PC, cc, 3000, False) for cc in CCS]
    return out


def k5_gate(cells) -> list:
    out = []
    for kind in ("base", "split4l"):
        for cc in CCS:
            out.append(v4.Cell("GATE", "calm", f"{kind}-{cc}", kind, ("pfifo",), seeds=(1,),
                               opts={} if cc == "bbr" else {"cc": "copa"}))
    v, o = policy("bbr", 1000, True)
    out.append(v4.Cell("GATE", "sburst", f"adapt-{v}", "base", ("pfifo",), seeds=(1,), opts=o))
    return out


def main(argv: list[str]) -> int:
    v4.topo_of = topo_of_k5
    v4.CAMPAIGNS["K5"] = k5
    v4.SPEC_HOURS["K5"] = 21
    gate_v4 = v4.gate_cells
    v4.gate_cells = lambda cells: k5_gate(cells) if cells and cells[0].block == "S1" else gate_v4(cells)
    return v4.main(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
