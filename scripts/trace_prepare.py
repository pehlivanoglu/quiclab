#!/usr/bin/env python3
"""Cellular capacity traces for the grouping campaign N4 (trace-driven access
links): download the public Mahimahi and Norway HSDPA traces and aggregate
each to 200 ms capacity steps.

    python3 scripts/trace_prepare.py --download <raw dir>          # fetch the raw files (network)
    python3 scripts/trace_prepare.py --raw <raw dir> [--out configs/traces]

Output: configs/traces/<name>.csv with `t_s,mbps` (one row per 200 ms step,
capacity of that step) and configs/traces/index.json (name, source, duration,
mean). The raw files stay out of the repository.

Sources
  Mahimahi (Netravali et al., USENIX ATC 2015; traces from Winstein et al.,
  NSDI 2013): github.com/ravinet/mahimahi, traces/*.down. One line per
  1500-byte packet delivery opportunity, in ms.
  Norway HSDPA (Riiser, Vigmostad, Griwodz, Halvorsen, MMSys 2013 dataset):
  datasets.simula.no/hsdpa, mirrored at
  skulddata.cs.umass.edu/traces/mmsys/2013/pathbandwidth. One line per
  report (~1 s): unix_s, ms, lat, lon, bytes, interval_ms (lat/lon may read
  NOFIX).
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "configs" / "traces"
STEP_S = 0.2
PACKET_BYTES = 1500

MAHIMAHI_URL = "https://raw.githubusercontent.com/ravinet/mahimahi/master/traces/{}"
MAHIMAHI = ["ATT-LTE-driving.down", "ATT-LTE-driving-2016.down", "TMobile-LTE-driving.down",
            "TMobile-LTE-short.down", "TMobile-UMTS-driving.down", "Verizon-EVDO-driving.down",
            "Verizon-LTE-driving.down", "Verizon-LTE-short.down"]
NORWAY_URL = "https://skulddata.cs.umass.edu/traces/mmsys/2013/pathbandwidth/{}/{}"
NORWAY = {
    "bus.ljansbakken-oslo": ["report.2010-09-28_1407CEST.log", "report.2010-09-29_0852CEST.log"],
    "metro.kalbakken-jernbanetorget": ["report.2010-09-13_1003CEST.log", "report.2010-09-13_1046CEST.log"],
    "tram.ljabru-jernbanetorget": ["report.2010-11-23_1541CET.log", "report.2010-12-09_1244CET.log"],
    "ferry.nesoddtangen-oslo": ["report.2010-09-20_1542CEST.log", "report.2010-09-21_1001CEST.log"],
    "car.snaroya-smestad": ["report.2011-02-14_2032CET.log", "report.2011-02-14_2051CET.log"],
    "train.oslo-vestby": ["report.2011-02-11_1618CET.log", "report.2011-02-14_0644CET.log"],
}


def norway_name(route: str, log: str) -> str:
    return f"norway-{route}-{log[len('report.'):-len('.log')]}"


def sources() -> list[tuple[str, str, str]]:
    """(name, raw file name, url)."""
    out = [(f[:-len(".down")], f, MAHIMAHI_URL.format(f)) for f in MAHIMAHI]
    for route, logs in NORWAY.items():
        out += [(norway_name(route, log), f"norway-{route}-{log}", NORWAY_URL.format(route, log)) for log in logs]
    return out


def download(raw: Path) -> None:
    raw.mkdir(parents=True, exist_ok=True)
    for _, fname, url in sources():
        dst = raw / fname
        if dst.exists():
            continue
        req = urllib.request.Request(url, headers={"User-Agent": "trace_prepare"})
        with urllib.request.urlopen(req, timeout=60) as r:
            dst.write_bytes(r.read())
        print(f"fetched {fname}")


def mahimahi_steps(path: Path) -> np.ndarray:
    """Capacity per STEP_S from packet delivery times (ms)."""
    ts = np.loadtxt(path, dtype=np.int64)
    counts = np.bincount(ts // int(STEP_S * 1000))
    return counts * PACKET_BYTES * 8 / STEP_S / 1e6


def norway_steps(path: Path) -> np.ndarray:
    """Capacity per STEP_S: each report's bytes / interval, held over its interval."""
    rates, out = [], []
    for line in path.read_text().splitlines():
        f = line.split()
        if len(f) < 6:
            continue
        nbytes, interval_ms = float(f[4]), float(f[5])
        if interval_ms <= 0:
            continue
        rates.append((nbytes * 8 / (interval_ms / 1000) / 1e6, interval_ms / 1000))
    t = 0.0
    for mbps, dur in rates:
        n = int(round((t + dur) / STEP_S)) - int(round(t / STEP_S))
        out += [mbps] * max(n, 0)
        t += dur
    return np.array(out)


def prepare(raw: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    index = {}
    for name, fname, url in sources():
        src = raw / fname
        if not src.exists():
            print(f"missing {src}", file=sys.stderr)
            continue
        steps = norway_steps(src) if name.startswith("norway-") else mahimahi_steps(src)
        with (out / f"{name}.csv").open("w") as fh:
            fh.write("t_s,mbps\n")
            for i, v in enumerate(steps):
                fh.write(f"{i * STEP_S:.1f},{v:.3f}\n")
        index[name] = {"source": url, "duration_s": round(len(steps) * STEP_S, 1), "step_s": STEP_S,
                       "mean_mbps": round(float(steps.mean()), 3), "zero_fraction": round(float((steps == 0).mean()), 4)}
    (out / "index.json").write_text(json.dumps(index, indent=1))
    return index


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--download", type=Path, metavar="RAW_DIR", help="fetch the raw traces into this directory")
    ap.add_argument("--raw", type=Path, help="raw trace directory to aggregate")
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args(argv)
    if a.download:
        download(a.download)
    raw = a.raw or a.download
    if raw:
        index = prepare(raw, a.out)
        for name, m in index.items():
            print(f"{name:55s} {m['duration_s']:7.1f} s  mean {m['mean_mbps']:6.2f} Mb/s  zero {m['zero_fraction']:.1%}")


if __name__ == "__main__":
    main(sys.argv[1:])
