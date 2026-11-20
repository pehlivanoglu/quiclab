#!/usr/bin/env python3
"""PPBP port check: the simulation's PPBP sources against the testbed generator on one run.

    python3 simulation/simlab/ppbp_check.py <testbed run> <sim run> <out.md>

Per PPBP source (scenario events of type ppbp), from traffic/<id>-bursts.csv and -sent.csv:
- burst list: identical? (both come from qvideo/src/Ppbp.h with the same parameters and seed)
- burst length distribution: count, mean, p50 / p90 / p99, max, two-sample KS statistic
- realized mean rate (sent bytes over the source's duration) against the configured mean_mbps
- Hurst estimate of the realized 100 ms sent-bytes series, aggregated-variance method
  (block sizes 1..64 x 100 ms, slope of log var vs log m = 2H - 2), against the configured hurst
Read-only on both runs.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


def hurst_aggvar(x: np.ndarray, ms=(1, 2, 4, 8, 16, 32, 64)) -> float:
    v = []
    for m in ms:
        n = len(x) // m
        if n < 8:
            break
        v.append((m, x[: n * m].reshape(n, m).mean(axis=1).var()))
    m, var = np.log([a for a, _ in v]), np.log([b for _, b in v])
    slope = np.polyfit(m, var, 1)[0]
    return 1 + slope / 2


def ks(a: np.ndarray, b: np.ndarray) -> float:
    grid = np.sort(np.concatenate([a, b]))
    fa = np.searchsorted(np.sort(a), grid, side="right") / len(a)
    fb = np.searchsorted(np.sort(b), grid, side="right") / len(b)
    return float(np.abs(fa - fb).max())


def source_stats(run: Path, e: dict) -> dict:
    b = pd.read_csv(run / "traffic" / f"{e['id']}-bursts.csv")
    s = pd.read_csv(run / "traffic" / f"{e['id']}-sent.csv")
    x = s["sent_bytes"].to_numpy(dtype=float)
    return {"bursts": b, "rate": x.sum() * 8 / e["duration_s"] / 1e6, "hurst": hurst_aggvar(x), "bins": len(x)}


def main(tb: Path, sim: Path, out: Path) -> None:
    scen = yaml.safe_load((tb / "scenario.yaml").read_text())
    rows = []
    for e in (e for e in scen["events"] if e["type"] == "ppbp"):
        t, s = source_stats(tb, e), source_stats(sim, e)
        same = t["bursts"].shape == s["bursts"].shape and np.allclose(
            t["bursts"][["start_s", "duration_s", "rate_mbps"]], s["bursts"][["start_s", "duration_s", "rate_mbps"]],
            atol=1e-4)
        q = lambda d: np.percentile(d["bursts"]["duration_s"], [50, 90, 99])  # noqa: E731
        rows.append({
            "source": e["id"], "mean_mbps cfg": e["mean_mbps"], "hurst cfg": e["hurst"],
            "bursts tb / sim": f"{len(t['bursts'])} / {len(s['bursts'])}", "burst list identical": "yes" if same else "NO",
            "burst s p50/p90/p99 tb": "/".join(f"{v:.2f}" for v in q(t)),
            "burst s p50/p90/p99 sim": "/".join(f"{v:.2f}" for v in q(s)),
            "KS burst length": round(ks(t["bursts"]["duration_s"].to_numpy(), s["bursts"]["duration_s"].to_numpy()), 4),
            "rate Mb/s tb / sim": f"{t['rate']:.3f} / {s['rate']:.3f}",
            "rate diff %": round(100 * (s["rate"] - t["rate"]) / t["rate"], 2),
            "Hurst tb / sim": f"{t['hurst']:.3f} / {s['hurst']:.3f}",
            "100 ms bins tb / sim": f"{t['bins']} / {s['bins']}",
        })
    df = pd.DataFrame(rows)
    out.parent.mkdir(parents=True, exist_ok=True)
    md = ["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
    md += ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    out.write_text(f"testbed: `{tb}`\n\nsimulation: `{sim}`\n\n" + "\n".join(md) + "\n")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
