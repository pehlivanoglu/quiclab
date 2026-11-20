#!/usr/bin/env python3
"""One-run check of the application-limited patch: testbed next to simulation runs (before / after the patch).

    python3 simulation/simlab/applimited_check.py <testbed run> <sim run> [<sim run> ...] > out.md

Per run and video client: BBR bandwidth estimate (acks.csv bbr_bw_bps, median) over the client's video rate; share of
ACK rows marked app-limited; share of time per BBR mode (acks.csv phase, held to the next row); keyframe pacing
spread (v3_emission key_ms_p50: the testbed's own v3-emission.json, the same function on simulation runs); keyframe
queue peak in calm time per egress (v3_gate.keyframe_peaks; testbed: its v3-checks.json). Read-only on the testbed run.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

QUICLAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(QUICLAB))
sys.path.insert(0, str(QUICLAB / "scripts"))


def per_run(rd: Path, testbed: bool) -> tuple[list[dict], dict]:
    import v3_emission
    import v3_gate
    topo = yaml.safe_load((rd / "topology.yaml").read_text())
    em = json.loads((rd / "v3-emission.json").read_text()) if testbed else v3_emission.run_emission(rd)
    rows = []
    for s, sub in topo["subscribers"].items():
        if s == "sub-ctrl":
            continue
        a = pd.read_csv(rd / "publishers" / "pub" / f"{s}-acks.csv", usecols=["mono_us", "bbr_bw_bps", "app_limited", "phase"])
        dt = np.diff(a.mono_us.values, append=a.mono_us.values[-1]).astype(float)
        share = pd.Series(dt).groupby(a.phase.values).sum()
        share = share / share.sum()
        bw = a.bbr_bw_bps[a.bbr_bw_bps > 0]
        rows.append({"client": s, "rate_mbps": sub["rate_kbps"] / 1000,
                     "bw_over_rate": round(float(bw.median()) / (sub["rate_kbps"] * 1000), 2) if len(bw) else None,
                     "app_limited": round(float(a.app_limited.mean()), 3),
                     "probe_bw": round(float(share.get("probe_bw", 0)), 3), "startup": round(float(share.get("startup", 0)), 3),
                     "key_spread_ms": (em.get(s) or {}).get("key_ms_p50")})
    if testbed:
        kp = json.loads((rd / "v3-checks.json").read_text()).get("keyframe_peaks") or {}
    else:
        plan = json.loads((rd / "v3-plan.json").read_text())
        wins = json.loads((rd / "grouping" / "windows.json").read_text()) if (rd / "grouping" / "windows.json").exists() else []
        kp = v3_gate.keyframe_peaks(rd, plan, wins)
    return rows, {n: (v["p50"], v["p90"]) for n, v in kp.items()}


def main(tb: Path, sims: list[Path]) -> None:
    print(f"testbed `{tb.name}`; simulation runs: " + ", ".join(f"`{s.parent.name}/{s.name}`" for s in sims) + "\n")
    runs = [("testbed", tb, True)] + [(f"sim {s.parent.name}", s, False) for s in sims]
    res = {name: per_run(rd, t) for name, rd, t in runs}
    print("| client | rate Mb/s | " + " | ".join(f"{n}: bw/rate, app-lim, ProbeBW / STARTUP, key spread ms" for n, _, _ in runs) + " |")
    print("|---|---|" + "---|" * len(runs))
    for i, r0 in enumerate(res["testbed"][0]):
        cells = []
        for n, _, _ in runs:
            r = res[n][0][i]
            ks = f"{r['key_spread_ms']:.1f}" if r["key_spread_ms"] is not None else "-"
            cells.append(f"{r['bw_over_rate']} x, {r['app_limited']}, {r['probe_bw']} / {r['startup']}, {ks}")
        print(f"| {r0['client']} | {r0['rate_mbps']:g} | " + " | ".join(cells) + " |")
    print("\nKeyframe queue peak in calm time, p50 / p90 ms per egress (v3_gate.keyframe_peaks):\n")
    for n, _, _ in runs:
        print(f"- {n}: " + ", ".join(f"{e} {a} / {b}" for e, (a, b) in res[n][1].items()))


if __name__ == "__main__":
    main(Path(sys.argv[1]), [Path(p) for p in sys.argv[2:]])
