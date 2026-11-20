#!/usr/bin/env python3
"""NPR STEP 1 and STEP 2 on the selected event formation (from reports/npr-step0b-2026-11-17/rows.jsonl).

    nice -n 19 .venv/bin/python3 reports/npr-2026-11-17/step12.py rows --cand E1-0.5 [--jobs 2]
    .venv/bin/python3 reports/npr-2026-11-17/step12.py report

Per run, at every close of the selected events (the same closes for every method):
  NPR V-bin / V-bb / V-na0 at alpha 0.05 (main), 0.01, 0.1;
  SETS (frozen grouping.sets.groups, k = 1, 2, 3) on the same events: the table {members: count} of the selected
  events with >= min_set members;
  frozen SETS on frozen events (E0 closes), as the reference.
Scored with the common scorer (grouping_score.Score) at each close: hot names = the event's strict_hot set.
STEP 2 (calibration): every run whose truth has one leaf, and every true leaf taken alone (its members, the events
where at least one member has 1): share split at any read, per alpha; plus 20 random event orders (seeds 0-19).
"""

from __future__ import annotations

import json
import math
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(HERE))

SRC = ROOT / "reports" / "npr-step0b-2026-11-17" / "rows.jsonl"
ALPHAS = (0.05, 0.01, 0.1)       # (P) main first
VARIANTS = ("bin", "na0")      # V-bb dropped (user, 2026-11-18)
PERMS = 20                       # (P) the note's
LONG_S = 5.0                     # (P) the note's "events longer than 5 s"


def matrix_col(e, clients):
    ones, na = set(e["ones"]), e["na"]
    return np.array([1.0 if c in ones else (np.nan if c in na else 0.0) for c in clients])


def run_npr(events, clients, variant, rho=None, alphas=ALPHAS):
    import npr
    rd = npr.Reader(clients, variant=variant)
    reads = []
    for e in events:
        rd.add(matrix_col(e, clients))
        t = time.perf_counter()
        r = rd.read(alphas)
        r["read_s"] = time.perf_counter() - t
        reads.append(r)
    if reads:   # winning EM start per null fit (index into npr.EM_STARTS), reported
        reads[-1]["em_starts"] = [int((np.array(rd.em_starts) == i).sum()) for i in range(len(npr.EM_STARTS))]
    return reads


def first_stim(rd: Path, names):
    w = json.loads((rd / "grouping" / "windows.json").read_text()) if (rd / "grouping" / "windows.json").exists() else []
    return {n: min((x["start"] for x in w if x.get("target") == n), default=None) for n in names}


def score_series(ts, clients, events, groups_at):
    """groups_at(i) -> list of frozensets at close i."""
    import grouping_score as gs
    sc = gs.Score(ts, clients)
    for i, e in enumerate(events):
        hn = set(e["hot"])
        hl = {gs.LEVEL(n) for n in hn}
        sc.close(e["close"], hl, hn, groups_at(i))
    return sc.summary()


def worker(args):
    row, cand, rho = args
    try:
        return _worker(row, cand, rho)
    except Exception as ex:  # noqa: BLE001
        import traceback
        return {"run": row["run"], "error": repr(ex), "tb": traceback.format_exc()[-2500:]}


def _worker(row, cand, rho):
    from collections import Counter

    from grouping import sets as S
    from grouping.sets import SetsConfig
    import grouping_score as gs
    scfg = SetsConfig()
    clients = row["clients"]
    ts = {n: {"members": frozenset(v["members"]), "level": v["level"]} for n, v in row["truth"].items()}
    ev = [e for e in row["cands"][cand] if e["ones"]]
    e0 = [e for e in row["cands"]["E0"] if e["ones"]]
    out = {k: row[k] for k in ("run", "campaign", "block", "type", "aqm", "rep", "topology")}
    out["n_clients"] = len(clients)
    out["leaf_sizes"] = sorted(len(v["members"]) for v in ts.values() if v["level"] == "leaf")
    out["first_stim"] = first_stim(ROOT / ".runs" / row["campaign"] / row["run"], list(ts))
    calm = row["type"] == "calm" or not any(v["level"] == "leaf" for v in ts.values())
    res = {}

    def sets_on(events):
        table = Counter()
        snaps = []
        for e in events:
            m = frozenset(e["ones"])
            if len(m) >= scfg.min_set:
                table[m] += 1
            snaps.append({k: [frozenset(g.members) for g in S.groups(table, k, scfg)] if table else [] for k in (1, 2, 3)})
        return snaps

    if not calm:
        for name, events in (("SETS@" + cand, ev), ("SETS@E0", e0)):
            snaps = sets_on(events)
            for k in (1, 2, 3):
                res[f"{name} k{k}"] = score_series(ts, clients, events, lambda i, k=k: snaps[i][k])
    reads_main = {}
    for v in VARIANTS:
        reads = run_npr(ev, clients, v, rho)
        reads_main[v] = reads
        for a in ALPHAS:
            if not calm:
                res[f"NPR-{v} a{a}"] = score_series(ts, clients, ev,
                                                     lambda i, a=a: [frozenset(g) for g in reads[i]["groups"][a]])
    out["methods"] = res
    out["read_s"] = {v: [r["read_s"] for r in reads_main[v]] for v in VARIANTS}
    out["em_starts"] = {v: reads_main[v][-1].get("em_starts") if reads_main[v] else None for v in VARIANTS}
    out["final"] = {v: {str(a): [sorted(g) for g in reads_main[v][-1]["groups"][a]] for a in ALPHAS}
                    for v in VARIANTS if reads_main[v]}
    # long events: duration > LONG_S and the true leaves each contains (a leaf counts when a member is in the event)
    leaf_sets = [set(v["members"]) for v in ts.values() if v["level"] == "leaf"]
    out["durations"] = [e["close"] - e["t0"] for e in ev]
    out["long_leaves"] = [sum(bool(set(e["ones"]) & L) for L in leaf_sets) for e in ev if e["close"] - e["t0"] > LONG_S]
    out["n_events"] = len(ev)
    out["late"] = [] if calm else late_joiner(ts, clients, ev, e0)
    out["n_events_e0"] = len(e0)
    # STEP 2: calibration on single-leaf groups
    cal = []
    leaves = [(n, sorted(v["members"])) for n, v in ts.items() if v["level"] == "leaf"]
    single = len(leaves) == 1
    for n, mem in leaves:
        sub = [e for e in ev if set(e["ones"]) & set(mem)]
        if len(mem) < 2 or len(sub) < 2:
            continue
        sub = [{**e, "ones": [c for c in e["ones"] if c in mem], "na": {c: x for c, x in e["na"].items() if c in mem}}
               for e in sub]
        for order in range(PERMS + 1):
            seq = list(sub)
            if order:
                random.Random(order - 1).shuffle(seq)
            rec = {"leaf": n, "size": len(mem), "events": len(seq), "whole_run": single, "perm": order}
            for v in ("bin",):
                reads = run_npr(seq, mem, v, rho)
                for a in ALPHAS:
                    rec[f"split_{a}"] = any(len(r["groups"][a]) > 1 for r in reads)
            cal.append(rec)
    out["calibration"] = cal
    return out


def rows_path(cand: str) -> Path:
    return HERE / f"rows-v2-{cand}.jsonl"     # corrected test (2026-11-18); the first run is rows-<cand>.jsonl


def late_joiner(ts, clients, ev, e0):
    """grouping_score's late-joiner test (as R1): per true leaf with >= 3 members, its largest client id is hidden
    (no onset: NA for NPR, absent for SETS) until a group with F1 >= F1_OK on the rest exists; then released.
    Joined = a group containing it with F1 >= F1_OK on the whole leaf; events and seconds from the release."""
    from collections import Counter

    import grouping_score as gs
    import npr
    from grouping import sets as S
    from grouping.sets import SetsConfig
    scfg = SetsConfig()
    out = []
    for n, info in ts.items():
        if info["level"] != "leaf" or len(info["members"]) < 3:
            continue
        L = frozenset(info["members"])
        hid = max(info["members"])
        rest = L - {hid}
        for meth, events in (("NPR-bin a0.05", ev), ("SETS k2", ev), ("SETS@E0 k2", e0)):
            st = {"rel": None, "join": None}
            rd = npr.Reader(clients) if meth.startswith("NPR") else None
            table = Counter()
            for i, e in enumerate(events):
                hide = st["rel"] is None
                ones = [c for c in e["ones"] if not (hide and c == hid)]
                if rd is not None:
                    col = step_col(ones, e["na"], clients, hid if hide else None)
                    rd.add(col)
                    groups = [frozenset(g) for g in rd.read((0.05,))["groups"][0.05]]
                else:
                    if len(ones) >= scfg.min_set:
                        table[frozenset(ones)] += 1
                    groups = [frozenset(g.members) for g in S.groups(table, 2, scfg)] if table else []
                if st["rel"] is None:
                    if any(gs._f1(g, rest)[2] >= gs.F1_OK for g in groups):
                        st["rel"] = (i, e["close"])
                elif st["join"] is None and any(hid in g and gs._f1(g, L)[2] >= gs.F1_OK for g in groups):
                    st["join"] = (i, e["close"])
                    break
            rec = {"leaf": n, "method": meth, "released": st["rel"] is not None, "joined": st["join"] is not None}
            if st["rel"] and st["join"]:
                rec.update(events=st["join"][0] - st["rel"][0], seconds=st["join"][1] - st["rel"][1])
            out.append(rec)
    return out


def step_col(ones, na, clients, hidden):
    s = set(ones)
    return np.array([np.nan if c == hidden else 1.0 if c in s else (np.nan if c in na else 0.0) for c in clients])


def cmd_rows(cand: str, jobs: int, only: str | None, rho: float) -> None:
    ROWS = rows_path(cand)
    rows = [json.loads(x) for x in SRC.read_text().splitlines() if x.strip()]
    rows = [r for r in rows if "error" not in r and (not only or only in r["run"])]
    done = set()
    if ROWS.exists():
        good = [x for x in ROWS.read_text().splitlines() if x.strip().endswith("}")]
        done = {json.loads(x)["run"] for x in good}
        ROWS.write_text("".join(x + "\n" for x in good))
    rows = [r for r in rows if r["run"] not in done]
    print(f"{len(rows)} runs ({len(done)} already done), candidate {cand}, rho {rho}", flush=True)
    with ROWS.open("a") as fh, Pool(jobs) as pool:
        for i, out in enumerate(pool.imap_unordered(worker, [(r, cand, rho) for r in rows]), 1):
            fh.write(json.dumps(out, default=lambda o: None if (isinstance(o, float) and not math.isfinite(o))
                                else (sorted(o) if isinstance(o, (set, frozenset)) else
                                      (o.tolist() if hasattr(o, "tolist") else str(o)))) + "\n")
            fh.flush()
            print(f"  {i}/{len(rows)} {out['run']}{' ERROR ' + out['error'] if 'error' in out else ''}", flush=True)


def main(argv: list[str]) -> int:
    if argv[0] == "rows":
        cand = argv[argv.index("--cand") + 1]
        rho = float(argv[argv.index("--rho") + 1]) if "--rho" in argv else 0.0
        cmd_rows(cand, int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 2,
                 argv[argv.index("--only") + 1] if "--only" in argv else None, rho)
    elif argv[0] == "report":
        import step12_report
        step12_report.report(rows_path(argv[argv.index("--cand") + 1]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
