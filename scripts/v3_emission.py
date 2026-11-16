#!/usr/bin/env python3
"""Per run, per client: median BBR pacing rate and median keyframe / P-frame emission time
(calm GOPs only). The keyframe pulse a run produces depends on these (2026-11-14: a 5000 kb/s
keyframe leaves in ~5 ms on a fast-pacing connection and in 35-50 ms on a slow one), so
every v3 run records them and the rep 1 vs rep 2 report shows them next to cells whose
repetitions disagree.

    .venv/bin/python3 scripts/v3_emission.py <run> [...]     # writes <run>/v3-emission.json, prints a table

Sender logs: <client>-frames.csv (write times, sizes), <client>-pkts.csv (per-packet send
times, GT-Q logging), <client>-cc.csv (pacing_bps).
- keyframe: from the first packet sent at / after its write to the packet that brings the
  payload since then to the keyframe size minus one packet (payload = packet size - the
  run's median per-packet overhead; the keyframe's tail can ride in the next frame's first
  packet, sent only when that frame is written, so the end is exact to one packet);
- P-frame: first to last packet in [its write, the next frame's write); frames whose packets
  reach within SPILL_MS of the next write are skipped (they may continue into it) and counted.
Calm: outside every stimulus window (grouping/windows.json) +- 1 s, after warm-up + 5 s.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval  # noqa: E402

SPILL_MS = 1.0     # (M) as scripts/v3_asv_spread.py
CALM_MARGIN_S = 1.0


def _busy(rd: Path) -> list[tuple[float, float]]:
    p = rd / "grouping" / "windows.json"
    wins = json.loads(p.read_text()) if p.exists() else []
    return [(w["start"] - CALM_MARGIN_S, w["end"] + CALM_MARGIN_S) for w in wins]


def client(run: det_eval.Run, sid: str, busy: list[tuple[float, float]]) -> dict | None:
    fp, pp = run.sender_file(sid, "frames"), run.sender_file(sid, "pkts")
    if not (fp.exists() and pp.exists()):
        return None
    fr = pd.read_csv(fp)
    pk = pd.read_csv(pp, usecols=["send_mono_us", "size"]).sort_values("send_mono_us", kind="stable")
    ts = np.array([run.t_mono_us(x) for x in pk.send_mono_us])
    sz = pk["size"].to_numpy(dtype=float)
    w = np.array([run.t_unix_us(x) for x in fr.write_us])
    size = fr["size"].to_numpy(dtype=float)
    key = fr.keyframe.to_numpy() == 1
    calm = lambda t: (t > det_eval.WARMUP_S + 5) & (t < run.duration - 2) & ~np.any(  # noqa: E731
        [(t >= a) & (t <= b) for a, b in busy] or [np.zeros_like(t, dtype=bool)], axis=0)
    cum = np.r_[0, np.cumsum(sz)]
    keys = np.flatnonzero(key)
    oh = []
    for g in range(len(keys) - 1):
        a, b = np.searchsorted(ts, [w[keys[g]], w[keys[g + 1]]], side="left")
        if b > a:
            oh.append((cum[b] - cum[a] - size[keys[g]:keys[g + 1]].sum()) / (b - a))
    overhead = float(np.median(oh)) if oh else 0.0
    pay = np.r_[0, np.cumsum(sz - overhead)]
    full = float(np.median(sz)) - overhead
    key_ms, p_ms, spilled = [], [], 0
    for g in range(len(keys) - 1):
        i, j = keys[g], keys[g + 1]
        a, b = np.searchsorted(ts, [w[i], w[j]], side="left")
        if b <= a or not calm(np.array([w[i]]))[0]:
            continue
        k = min(max(int(np.searchsorted(pay, pay[a] + size[i] - full - 1e-6, side="left")), a), b - 1)
        key_ms.append((ts[k] - ts[a]) * 1000)
    for i in np.flatnonzero(~key[:-1]):
        if not calm(np.array([w[i]]))[0]:
            continue
        a, b = np.searchsorted(ts, [w[i], w[i + 1]], side="left")
        if b <= a:
            continue
        if (w[i + 1] - ts[b - 1]) * 1000 < SPILL_MS:
            spilled += 1
            continue
        p_ms.append((ts[b - 1] - ts[a]) * 1000)
    pacing = None
    cc = run.sender_file(sid, "cc")
    if cc.exists():
        x = pd.read_csv(cc, usecols=["t_us", "pacing_bps"])
        tt = np.array([run.t_unix_us(v) for v in x.t_us])
        m = calm(tt) & (x.pacing_bps.to_numpy() > 0)
        pacing = round(float(np.median(x.pacing_bps.to_numpy()[m])) / 1e6, 2) if m.any() else None
    med = lambda v: round(float(np.median(v)), 2) if v else None   # noqa: E731
    return {"rate_kbps": run.topology["subscribers"][sid].get("rate_kbps"), "pacing_mbps_p50": pacing,
            "key_ms_p50": med(key_ms), "key_n": len(key_ms), "p_ms_p50": med(p_ms), "p_n": len(p_ms),
            "p_spilled": spilled}


def run_emission(rd: Path) -> dict:
    run = det_eval.Run(rd)
    busy = _busy(rd)
    out = {}
    for sid in run.subs:
        try:
            c = client(run, sid, busy)
        except Exception as e:  # noqa: BLE001
            c = {"error": repr(e)}
        if c is not None:
            out[sid] = c
    return out


def write(rd: Path) -> dict:
    res = run_emission(rd)
    (rd / "v3-emission.json").write_text(json.dumps(res, indent=1))
    return res


def load(rd: Path) -> dict:
    p = rd / "v3-emission.json"
    return json.loads(p.read_text()) if p.exists() else write(rd)


def line(res: dict) -> str:
    return "emission " + "; ".join(f"{s} {v.get('pacing_mbps_p50')} Mb/s key {v.get('key_ms_p50')} P {v.get('p_ms_p50')}"
                                   for s, v in sorted(res.items()) if "error" not in v)


def side_by_side(a: dict, b: dict) -> list[str]:
    """Markdown rows: client | rate | pacing r1 / r2 | keyframe ms r1 / r2 | P ms r1 / r2."""
    rows = []
    for s in sorted(set(a) | set(b)):
        x, y = a.get(s, {}), b.get(s, {})
        rows.append(f"| {s} | {x.get('rate_kbps') or y.get('rate_kbps')} | {x.get('pacing_mbps_p50')} / "
                    f"{y.get('pacing_mbps_p50')} | {x.get('key_ms_p50')} / {y.get('key_ms_p50')} | "
                    f"{x.get('p_ms_p50')} / {y.get('p_ms_p50')} |")
    return rows


def main(argv: list[str]) -> None:
    for rd in map(Path, argv):
        print(f"{rd.name}: {line(write(rd))}")


if __name__ == "__main__":
    main(sys.argv[1:])
