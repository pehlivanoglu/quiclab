#!/usr/bin/env python3
"""Suite v3, spec section 2.3: the checks before anything else.

    .venv/bin/python3 scripts/v3_checks.py ecn [--runs .runs]     # (c) ECN marks in every existing run folder
    .venv/bin/python3 scripts/v3_checks.py ect                    # (b) does mvfst set ECT? (source reading)
    .venv/bin/python3 scripts/v3_checks.py kernel-cmd             # (a) the command that prints the kernel's
                                                                  #     default limits (the user runs it)
    .venv/bin/python3 scripts/v3_checks.py kernel-parse <file>    # (a) parse that command's output

(c) reads `ecn_marks` (per-interval deltas) from every router-metrics egress CSV under --runs; the column
is filled for dualpi2 / red / pie / fq_codel / codel and is 0 by construction for pfifo and cake
(quiclab/router_metrics.py does not read cake's per-tin marks), so cake runs are listed separately.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MVFST = ROOT / "qvideo" / "build" / "_deps" / "mvfst-src"   # the mvfst checkout qvideo is built from


def ecn_scan(runs: Path) -> int:
    per_run: dict[Path, dict[str, int]] = defaultdict(dict)
    n_csv = 0
    for p in sorted(runs.rglob("router-metrics/*/*.csv")):
        if p.name.endswith(("-queue.csv", "-flows.csv")):
            continue
        n_csv += 1
        total = 0
        with p.open() as fh:
            rd = csv.DictReader(fh)
            if "ecn_marks" not in (rd.fieldnames or []):
                continue
            for r in rd:
                try:
                    total += int(r["ecn_marks"])
                except (TypeError, ValueError):
                    pass
        per_run[p.parents[2]][f"{p.parent.name}/{p.stem}"] = total
    runs_nonzero = {r: {k: v for k, v in e.items() if v} for r, e in per_run.items() if any(e.values())}
    aqm_of = {}
    for r in per_run:
        s = r / "scenario.yaml"
        m = re.search(r"aqm:\s*(\w+)", s.read_text()) if s.exists() else None
        aqm_of[r] = m.group(1) if m else "?"
    by_aqm = defaultdict(int)
    for r in per_run:
        by_aqm[aqm_of[r]] += 1
    print(f"# 2.3(c) ECN marks in existing run folders under {runs}\n")
    print(f"{len(per_run)} run folders, {n_csv} router-metrics egress CSVs. Runs per (first) AQM: "
          + ", ".join(f"{a} {n}" for a, n in sorted(by_aqm.items())) + ".")
    print("cake runs: marks not recorded by router_metrics (cake's per-tin counters are not read).\n")
    if not runs_nonzero:
        print("Non-zero ECN marks: none.")
    else:
        print(f"Non-zero ECN marks in {len(runs_nonzero)} run(s):\n")
        for r, e in sorted(runs_nonzero.items()):
            print(f"- {r.relative_to(runs)} ({aqm_of[r]}): " + ", ".join(f"{k} {v}" for k, v in sorted(e.items())))
    return 0


def ect_check() -> int:
    """mvfst marks ECT only when TransportSettings.enableEcnOnEgress is set; qvideo never sets it."""
    ts = next(MVFST.rglob("quic/state/TransportSettings.h"), None)
    lines = [l.strip() for l in ts.read_text().splitlines() if "Ecn" in l or "ecn" in l] if ts else []
    users = sorted({str(p.relative_to(ROOT)) for p in (ROOT / "qvideo" / "src").glob("*.cpp")
                    if re.search(r"[Ee]cn", p.read_text())})
    print("# 2.3(b) ECT on mvfst packets\n")
    print(f"{ts.relative_to(ROOT) if ts else 'TransportSettings.h not found'}:")
    for l in lines:
        print(f"    {l}")
    print(f"qvideo sources that mention ECN: {users or 'none'}")
    print("=> mvfst default enableEcnOnEgress=false and qvideo does not change it: video packets are Not-ECT, "
          "so an AQM's `ecn` flag never marks them (it drops instead).")
    return 0


KERNEL_CMD = r"""docker run --rm --privileged --network none -v /lib/modules:/lib/modules:ro quiclab:latest bash -c '
modprobe sch_htb; modprobe sch_codel; modprobe sch_pie; modprobe sch_fq_codel
ip link add v3a type veth peer name v3b && ip link set v3a up && ip link set v3b up
for q in codel pie fq_codel; do
  tc qdisc replace dev v3a root handle 5: htb default 1
  tc class add dev v3a parent 5: classid 5:1 htb rate 54mbit ceil 54mbit burst 15k quantum 1500
  tc qdisc add dev v3a parent 5:1 handle 20: $q
  echo "== $q"; tc qdisc show dev v3a; tc -j qdisc show dev v3a
  tc qdisc del dev v3a root
done
uname -r'"""


def kernel_parse(path: Path) -> int:
    text = path.read_text()
    print("# 2.3(a) kernel default limits (htb 54 Mb/s parent, no limit argument)\n")
    for block in re.split(r"^== ", text, flags=re.M)[1:]:
        name, _, rest = block.partition("\n")
        line = next((l for l in rest.splitlines() if l.startswith(f"qdisc {name} 20:")), "")
        print(f"- {name}: `{line.strip()}`")
    kernel = text.strip().splitlines()[-1] if text.strip() else "?"
    print(f"\nkernel: {kernel}")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("check", choices=["ecn", "ect", "kernel-cmd", "kernel-parse"])
    ap.add_argument("file", nargs="?")
    ap.add_argument("--runs", type=Path, default=ROOT / ".runs")
    a = ap.parse_args(argv)
    if a.check == "ecn":
        return ecn_scan(a.runs)
    if a.check == "ect":
        return ect_check()
    if a.check == "kernel-cmd":
        print(KERNEL_CMD)
        return 0
    return kernel_parse(Path(a.file))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
