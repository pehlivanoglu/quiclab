#!/usr/bin/env python3
"""What-if for CC-driven rate adaptation (K5-sender note, 1.8), on the open-loop v3 logs. It cannot show the closed
loop: the video in these runs never sent less because of the estimate. Nothing frozen changes; nothing is written
inside run folders.

    nice -n 19 .venv/bin/python3 reports/adapt-whatif-2026-11-17/aw.py rows [--jobs 2]
    .venv/bin/python3 reports/adapt-whatif-2026-11-17/aw.py report

Estimate (per client, sender cc.csv every 50 ms): BBR bw_est_bps (BBR's bandwidth estimate, wire bytes); Copa
cwnd_bytes x 8 / srtt. Nominal = the client's produced media rate (frames.csv + drops.csv bytes over the run).
Rule: a cut is in force while x * estimate < nominal, x in X (P).
Calm time: the calm runs (C1a / C1b) after the warm-up; for the stimulus runs (Copa M13 has no calm run), GT3
source B CLEAR cells outside every window span [start - 2 s, end + 10 s] (M).
Per GT3 onset t_on (source B, after the warm-up, stimulus runs): t_cut(x) = the first sample in
[t_on - 1 s, t_on + SEARCH_S] with x * estimate < nominal ("already" when the first sample is), next to the frozen
detector's first alarm start in [t_on - 1 s, t_on + 10 s] (the TP window) and the client's first GOP drop in
[t_on - 1 s, t_on + SEARCH_S].
"""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "reports" / "detector-r2-2026-11-16"))
sys.path.insert(0, str(ROOT / "reports" / "sender-policy-2026-11-17"))

KDIR = ROOT / ".runs" / "2026-11-14_1818_v3"
X = (0.7, 0.85, 1.0)        # (P) the note's values
SEARCH_S = 10.0             # (M) = det_eval.SEARCH_S
CALM_BLOCKS = ("C1a", "C1b")
PHASE_BINS = 10             # (M) 100 ms bins of a 1 s GOP
ROWS = HERE / "rows.jsonl"


def series(run, s):
    import pandas as pd
    c = pd.read_csv(run.sender_file(s, "cc"), usecols=["t_us", "cc", "srtt_us", "cwnd_bytes", "bw_est_bps"])
    t = np.array([run.t_unix_us(x) for x in c.t_us.values])
    cc = str(c.cc.iloc[-1])
    if cc == "copa":
        est = np.where(c.srtt_us > 0, c.cwnd_bytes * 8 / (c.srtt_us / 1e6), np.nan)
    else:
        est = np.where(c.bw_est_bps > 0, c.bw_est_bps.astype(float), np.nan)
    return cc, t, est


def nominal(run, s, duration):
    import pandas as pd
    b = pd.read_csv(run.sender_file(s, "frames"), usecols=["size"])["size"].sum()
    f = run.sender_file(s, "drops")
    if f.exists():
        b += pd.read_csv(f, usecols=["size"])["size"].sum()
    return b * 8 / duration


def keyframes(run, s):
    import pandas as pd
    fr = pd.read_csv(run.sender_file(s, "frames"), usecols=["keyframe", "send_us"])
    return np.sort(np.array([run.t_unix_us(x) for x in fr.send_us[fr.keyframe == 1].values]))


def entries(below: np.ndarray) -> int:
    """Number of transitions into the cut state."""
    if not len(below):
        return 0
    return int(below[0]) + int(np.sum(below[1:] & ~below[:-1]))


def worker(rd: Path) -> dict:
    try:
        return _worker(rd)
    except Exception as e:  # noqa: BLE001
        import traceback
        return {"run": rd.name, "error": repr(e), "tb": traceback.format_exc()[-2500:]}


def _worker(rd: Path) -> dict:
    import det_eval as d
    import gt3
    import gt_bands
    import gt_score as g
    import r2
    import shadow_v2_frozen as fz
    import shadow_v2_step3 as s3
    import shadow_v2_step5 as s5
    import sp
    r2._setup()
    run = d.Run(rd)
    plan = json.loads((rd / "v3-plan.json").read_text())
    calm_run = plan["block"] in CALM_BLOCKS
    wins = json.loads((rd / "grouping" / "windows.json").read_text()) if (rd / "grouping" / "windows.json").exists() else []
    subs = [s for s in run.subs if s != "sub-ctrl"]
    eb, lb = gt3.run_truth(run, gt3.Params(), source="B")
    view = gt3.view_of(run, eb, lb, need_path=True)
    alarms = {}
    if not calm_run:
        for s, df in r2.flows(run).items():
            r = s3.run_cusum(df, r2.FROZEN_LABEL, fz.FROZEN["OWD"]["g_ref"]["v2"], False)
            alarms[s] = [a for a, _, _ in s5.on_spans(r, s3.THETA_ON)]
    clients = {}
    onsets = []
    for s in subs:
        cc, t, est = series(run, s)
        nom = nominal(run, s, run.duration)
        eps, code = view.get(s, ([], np.array([])))
        # calm mask per sample
        ok = (t >= d.WARMUP_S) & np.isfinite(est)
        if calm_run:
            calm = ok.copy()
        else:
            cell = np.clip((t / g.GRID_S).astype(int), 0, max(len(code) - 1, 0))
            clear = (code[cell] == g.RANK[gt_bands.CLEAR]) if len(code) else np.zeros(len(t), bool)
            outside = np.ones(len(t), bool)
            for w in wins:
                outside &= ~((t >= w["start"] - 2.0) & (t <= w["end"] + 10.0))
            calm = ok & clear & outside
        ratio = est / nom
        info = {"cc": cc, "nominal_bps": nom, "calm_s": float(calm.sum() * 0.05)}
        if calm.sum() >= 20:
            rc = ratio[calm]
            info["ratio_p"] = [float(np.percentile(rc, p)) for p in (5, 50, 95)]
            kf = keyframes(run, s)
            if len(kf) > 1:
                k = np.searchsorted(kf, t[calm], side="right") - 1
                ph = np.where(k >= 0, t[calm] - kf[np.clip(k, 0, None)], np.nan)
                b = np.clip((ph / (1.0 / PHASE_BINS)).astype(int), 0, PHASE_BINS - 1)
                info["phase_median"] = [float(np.median(rc[(b == i) & (ph >= 0)])) if np.any((b == i) & (ph >= 0))
                                        else None for i in range(PHASE_BINS)]
            # false cuts: entries into the cut state within contiguous calm stretches
            for x in X:
                below = (x * est < nom)
                n = 0
                idx = np.flatnonzero(calm)
                if len(idx):
                    breaks = np.flatnonzero(np.diff(idx) > 1)
                    for seg in np.split(idx, breaks + 1):
                        n += entries(below[seg])
                info[f"cuts_{x}"] = n
                info[f"cut_share_{x}"] = float(below[calm].mean())
        clients[s] = info
        if calm_run:
            continue
        drops = [e["t"] for e in sp.gop_drops(run, s)]
        for a, _b in eps:
            if a < d.WARMUP_S:
                continue
            row = {"flow": s, "t_on": a, "nominal_bps": nom, "cc": cc}
            al = next((x for x in alarms.get(s, []) if a - 1.0 <= x <= a + SEARCH_S), None)
            row["t_alarm"] = al
            row["t_drop"] = next((x for x in drops if a - 1.0 <= x <= a + SEARCH_S), None)
            k0, k1 = np.searchsorted(t, a - 1.0), np.searchsorted(t, a + SEARCH_S, side="right")
            for x in X:
                seg = np.flatnonzero(np.nan_to_num(x * est[k0:k1], nan=np.inf) < nom)
                row[f"cut_{x}"] = None if not len(seg) else float(t[k0 + seg[0]])
                row[f"already_{x}"] = bool(len(seg) and seg[0] == 0)
            onsets.append(row)
    parts = rd.name.split("-")
    return {"run": rd.name, "block": parts[1], "type": parts[2], "variant": parts[3], "aqm": parts[4],
            "rep": int(parts[5][1:]), "calm": calm_run, "clients": clients, "onsets": onsets}


def runs() -> list[Path]:
    return sorted(p for p in KDIR.iterdir() if p.is_dir() and p.name.startswith("v3-") and (p / "events.csv").exists())


def cmd_rows(jobs: int, only: str | None) -> None:
    done = set()
    if ROWS.exists():
        good = [x for x in ROWS.read_text().splitlines() if x.strip().endswith("}")]
        done = {json.loads(x)["run"] for x in good}
        ROWS.write_text("".join(x + "\n" for x in good))
    rs = [r for r in runs() if (not only or only in r.name) and r.name not in done]
    print(f"{len(rs)} runs ({len(done)} already done)", flush=True)
    with ROWS.open("a") as fh, Pool(jobs) as pool:
        for i, row in enumerate(pool.imap_unordered(worker, rs), 1):
            fh.write(json.dumps(row, default=lambda o: None if (isinstance(o, float) and not math.isfinite(o))
                                else (o.tolist() if hasattr(o, "tolist") else str(o))) + "\n")
            fh.flush()
            print(f"  {i}/{len(rs)} {row['run']}{' ERROR ' + row['error'] if 'error' in row else ''}", flush=True)


def main(argv: list[str]) -> int:
    if argv[0] == "rows":
        cmd_rows(int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 2,
                 argv[argv.index("--only") + 1] if "--only" in argv else None)
    elif argv[0] == "one":
        row = worker(KDIR / argv[1])
        print(row["tb"] if "error" in row else json.dumps({"clients": row["clients"], "onsets": row["onsets"][:5]},
                                                          default=str, indent=1)[:4000])
    elif argv[0] == "report":
        import aw_report
        aw_report.report(ROWS)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
