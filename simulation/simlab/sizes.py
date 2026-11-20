#!/usr/bin/env python3
"""Output size of one simulation run per file type: raw and compressed, per client-second.

    python3 simulation/simlab/sizes.py <sim run> [out.md]

File types: the path with the client / interface / event id replaced by a placeholder (e.g.
publishers/pub/<c>-acks.csv, router-trace/<if>-packets.csv). Compressed sizes from the zstd and gzip
command-line tools, streamed (nothing written). Per client-second = bytes / (video clients x duration).
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import yaml


def ftype(rel: str, subs: list[str]) -> str:
    for s in sorted(subs, key=len, reverse=True):
        rel = rel.replace(f"/{s}-", "/<c>-").replace(f"/{s}.", "/<c>.")
    rel = re.sub(r"router-trace/[^/]+-(packets|unmatched-enq)\.csv", r"router-trace/<if>-\1.csv", rel)
    rel = re.sub(r"router-metrics/([^/]+)/[^/]+?(-queue|-flows)?\.csv", r"router-metrics/<r>/<if>\2.csv", rel)
    rel = re.sub(r"traffic/[^/]+-(sent5|sent|recv|bursts|flows)\.csv", r"traffic/<id>-\1.csv", rel)
    return rel


def csize(path: Path, cmd: list[str]) -> int:
    with path.open("rb") as f:
        p = subprocess.run(cmd, stdin=f, capture_output=True)
    return len(p.stdout)


def main(run: Path, out: Path | None) -> None:
    topo = yaml.safe_load((run / "topology.yaml").read_text())
    scen = yaml.safe_load((run / "scenario.yaml").read_text())
    subs = list(topo["subscribers"])
    clients = len([s for s in subs if s != "sub-ctrl"])
    cs = clients * float(scen["duration_s"])
    agg = defaultdict(lambda: [0, 0, 0, 0, 0])
    for f in sorted(run.rglob("*")):
        if not f.is_file():
            continue
        t = ftype(str(f.relative_to(run)), subs)
        a = agg[t]
        a[0] += 1
        a[1] += f.stat().st_size
        a[2] += csize(f, ["gzip", "-6", "-c"])
        a[3] += csize(f, ["zstd", "-3", "-c", "-q"])
        a[4] += csize(f, ["zstd", "-19", "-c", "-q"])
    rows = sorted(agg.items(), key=lambda kv: -kv[1][1])
    tot = [sum(v[i] for _, v in rows) for i in range(5)]
    lines = [f"run `{run.name}`: {clients} video clients x {float(scen['duration_s']):g} s = {cs:g} client-seconds\n",
             "| file type | files | raw MB | gzip -6 MB | zstd -3 MB | zstd -19 MB | raw kB / client-s | zstd -3 kB / client-s |",
             "|---|---|---|---|---|---|---|---|"]
    for t, (n, raw, gz, z3, z19) in rows + [("**total**", tot)]:
        lines.append(f"| {t} | {n} | {raw / 1e6:.1f} | {gz / 1e6:.1f} | {z3 / 1e6:.1f} | {z19 / 1e6:.1f} | "
                     f"{raw / cs / 1e3:.2f} | {z3 / cs / 1e3:.2f} |")
    text = "\n".join(lines) + "\n"
    print(text)
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]) if len(sys.argv) > 2 else None)
