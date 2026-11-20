#!/usr/bin/env python3
"""A.4 validation on never-used runs: frozen candidates only, rules as in ../a4-rules.md (all addenda).

    rows    build one row per run (frozen row builder + frozen candidates + frozen scorer) -> <out>/rows.jsonl
    report  tables, intervals, decision text -> <out>/report.md

    .venv/bin/python3 reports/npr-2026-11-17/a4/a4.py rows --set valset --rerun <re-run folder> [--jobs 2]
    .venv/bin/python3 reports/npr-2026-11-17/a4/a4.py report --set valset
    .venv/bin/python3 reports/npr-2026-11-17/a4/a4.py rows --set dev --only <run>[,<run>...]   # development runs (test)
    .venv/bin/python3 reports/npr-2026-11-17/a4/a4.py report --set dev                        # report code on dev rows

--set valset: the main and robustness tables of ../valset.json (frozen; sha256 checked). The 8 K3 I1 ip1.2 runs are
read under their ip1p2 run ids from the re-run folder (a4-rules.md addendum). --set dev: the 263 development runs
(reports/npr-step0b-2026-11-17/rows.jsonl), for testing only; never mixed with the validation output.

Code used, never modified: ../frozen-2026-11-18 (candidates, npr, npr_var, step12, npr0, npr0b, grouping_score). The
frozen tick-file patch writes under <out>/cache, never inside a run folder; this script writes only under <out>.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
NPRD = HERE.parent
FROZEN = NPRD / "frozen-2026-11-18"
ROOT = NPRD.parents[1]
sys.path[:0] = [str(FROZEN), str(ROOT / "scripts"), str(ROOT / "reports" / "sets-low-threshold-2026-11-16"), str(ROOT)]

VALSET = NPRD / "valset.json"
VALSET_SHA = {"valset.py": "180371ed60b0964a5c14c9e09c183c4e4519bfd8ff7832c4976b3db72011c335",
              "valset.md": "a58186a661dcf69fe0d71ec02671a72d55151cd49c6b81a5c10e6d9ab69a8a2f",
              "valset.json": "9a6e55a23ce5b96adc51bb32a150e9e1744df85c5ca2046b1c79e109a53ec070"}
DEV_SRC = ROOT / "reports" / "npr-step0b-2026-11-17" / "rows.jsonl"
CAMPAIGN_DIR = {"K1": ROOT / ".runs" / "2026-11-16_0105_v4-K1", "K2": ROOT / ".runs" / "2026-11-16_0105_v4-K2",
                "K3": ROOT / ".runs" / "2026-11-16_0105_v4-K3"}
OUT = {"valset": HERE / "valset", "dev": HERE / "dev"}

# (P) frozen candidates (FREEZE.md); k = 3 side by side for SETS
NPR_CANDS = ("NPR-B", "NPR-A", "NPR-A10")
SETS_REF = "SETS-v1.1"
ROWS_ORDER = ("NPR-B", "NPR-A", "NPR-A10", "SETS-v1.1", "SETS@E1-0.5", "SETS-v1.1 k3", "SETS@E1-0.5 k3")
ALPHA = 0.05            # (P) every NPR candidate; NPR-A's false-split condition is share <= ALPHA
PAIR_P_MIN = 0.90       # (P) user 2026-11-18
BOOT = 10_000           # (P) user 2026-11-19
BOOT_SEED = 20261119    # (P) user 2026-11-19
PERMS = 20              # (M) as STEP 2 / step12v: 20 random orders of each leaf's events (reported, not a condition)
LATE_MISS = 0.10        # (P) diag3: late responder = miss rate > 0.10 ...
LATE_LAG = 0.5          # (M) diag3: ... or at least half of its misses followed by its own onset within LATE_S
LATE_S = 1.0            # (M) diag3
PLATEAU_TOL = 0.01      # (P) user 2026-11-19
ACC_BINS = (1, 2, 3, 4, 5, 6, 7, 8)   # (M) accuracy by events seen: 1..8 and "more" (as grouping-step4)
FEW_RUNS = 5            # (P) user 2026-11-19: columns resting on 5 runs or fewer (top notice list, per-run values)
FLAGGED = {"v4-C1-sjoin-copa-pfifo-r2": "one unmatched drop record at the router (trace one drop row more than the "
           "kernel counter; GT-Q / GT-H on that hop by one packet); client-side inputs unaffected"}   # (P) user 2026-11-19
EXTRA_RERUN = ("v4-C1-sjoin-copa-pfifo-r2",)   # (P) user 2026-11-19: its re-run shown next to it, in no table total
COL_ORDER = ("main r1", "main r2", "main r3+", "robustness r1", "robustness r2", "robustness r3+")


# ---------------------------------------------------------------------------------------------------------- input

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def seed_col(rep: int) -> str:
    return "r1" if rep == 1 else "r2" if rep == 2 else "r3+"


def i1_id(name: str) -> str:
    return name.replace("ip1.2", "ip1p2")


def run_list(kind: str, rerun: Path | None, only: set | None) -> list[dict]:
    if kind == "valset":
        for f, h in VALSET_SHA.items():
            assert sha(NPRD / f) == h, f"{f} changed (frozen)"
        out = []
        for r in json.load(open(VALSET)):
            if r["table"] not in ("main", "robustness"):
                continue
            if "ip1.2" in r["run"]:
                assert rerun, "--rerun <folder> is needed for the 8 I1 ip1.2 runs (ip1p2 ids)"
                path = rerun / i1_id(r["run"])
            else:
                path = CAMPAIGN_DIR[r["campaign"]] / r["run"]
            out.append({"run": r["run"], "run_id": path.name, "path": str(path), "campaign": r["campaign"],
                        "table": r["table"], "rep": r["rep"], "block": r["block"], "type": r["type"],
                        "variant": r["variant"], "aqm": r["aqm"]})
            if r["run"] in EXTRA_RERUN:
                assert rerun, "--rerun <folder> is needed for the extra re-run rows"
                out.append({**out[-1], "run": r["run"] + "@rerun", "run_id": r["run"], "path": str(rerun / r["run"]),
                            "table": "extra"})
    else:
        val = {(r["campaign"], r["run"]) for r in json.load(open(VALSET))}
        out = []
        for x in DEV_SRC.read_text().splitlines():
            if not x.strip():
                continue
            r = json.loads(x)
            if "error" in r:
                continue
            short = r["campaign"].split("_v4-")[-1] if "_v4-" in r["campaign"] else r["campaign"]
            assert (short, r["run"]) not in val, f"validation run in the development set: {r['run']}"
            single = r["aqm"] not in ("fq_codel", "cake")
            out.append({"run": r["run"], "run_id": r["run"], "path": str(ROOT / ".runs" / r["campaign"] / r["run"]),
                        "campaign": short, "table": "main" if single else "robustness", "rep": r["rep"],
                        "block": r["block"], "type": r["type"], "variant": r.get("variant"), "aqm": r["aqm"]})
    if only:
        out = [r for r in out if r["run"] in only or r["run_id"] in only]
    return out


def folder_state(rd: Path) -> dict:
    """File list with size and mtime: checked before and after, to prove nothing was written in the run folder."""
    return {str(p.relative_to(rd)): (p.stat().st_size, p.stat().st_mtime_ns) for p in sorted(rd.rglob("*")) if p.is_file()}


# ---------------------------------------------------------------------------------------------------------- per run

def best_f1(groups, leaf):
    import grouping_score as gs
    return max((gs._f1(g, leaf)[2] for g in groups), default=0.0)


def leaf_curves(ts, events, series):
    """Per true leaf: after each close of one of its own events (the leaf hot, as Score.leaf_events), the best F1 of any
    group with the leaf: [(events seen, F1, close)]."""
    out = {}
    for n, v in ts.items():
        if v["level"] != "leaf":
            continue
        L, k, cur = frozenset(v["members"]), 0, []
        for i, e in enumerate(events):
            if n in e["hot"]:
                k += 1
                cur.append((k, best_f1(series[i], L), e["close"]))
        out[n] = cur
    return out


def late_joiner(name, ts, clients, events):
    """grouping_score's late-joiner test (as step12 / step12v): per true leaf with >= 3 members its largest client id
    is hidden (NA for NPR, absent for SETS) until a group with F1 >= F1_OK on the rest exists, then released."""
    import candidates as C
    import grouping_score as gs
    import npr_var
    import step12
    from grouping import sets as S
    from grouping.sets import SetsConfig
    kind, spec, _, _ = C.CANDIDATES[name.split(" k")[0]]
    k = 3 if name.endswith(" k3") else (spec if kind == "sets" else None)
    scfg = SetsConfig()
    out = []
    for n, info in ts.items():
        if info["level"] != "leaf" or len(info["members"]) < 3:
            continue
        L = frozenset(info["members"])
        hid = max(info["members"])
        rest = L - {hid}
        st = {"rel": None, "join": None}
        rd = npr_var.make(spec, clients) if kind == "npr" else None
        table = Counter()
        for i, e in enumerate(events):
            hide = st["rel"] is None
            ones = [c for c in e["ones"] if not (hide and c == hid)]
            if rd is not None:
                rd.add(step12.step_col(ones, e["na"], clients, hid if hide else None))
                groups = [frozenset(g) for g in rd.read((C.ALPHA,))["groups"][C.ALPHA]]
            else:
                if len(ones) >= scfg.min_set:
                    table[frozenset(ones)] += 1
                groups = [frozenset(g.members) for g in S.groups(table, k, scfg)] if table else []
            if st["rel"] is None:
                if any(gs._f1(g, rest)[2] >= gs.F1_OK for g in groups):
                    st["rel"] = (i, e["close"])
            elif any(hid in g and gs._f1(g, L)[2] >= gs.F1_OK for g in groups):
                st["join"] = (i, e["close"])
                break
        rec = {"leaf": n, "released": st["rel"] is not None, "joined": st["join"] is not None}
        if st["rel"] and st["join"]:
            rec.update(events=st["join"][0] - st["rel"][0], seconds=st["join"][1] - st["rel"][1])
        out.append(rec)
    return out


def member_stats(mem, sub, ev_all):
    """diag3: per member, miss rate on the leaf's events and the share of misses followed by its own onset."""
    st = {}
    for x in mem:
        zeros = [j for j, e in enumerate(sub) if x not in e["ones"] and x not in e["na"]]
        nn = sum(1 for e in sub if x not in e["na"])
        lag = sum(1 for j in zeros if any(x in f["ones"] and sub[j]["t0"] < f["t0"] <= sub[j]["close"] + LATE_S
                                          for f in ev_all))
        miss = len(zeros) / nn if nn else None
        st[x] = bool((miss is not None and miss > LATE_MISS) or (len(zeros) >= 2 and lag / len(zeros) >= LATE_LAG))
    return st


def false_splits(name, ts, ev):
    """STEP 2 / diag3: each true leaf alone through the reader (its events, members only), original order and PERMS
    random orders; the first accepted split and its parts (original order)."""
    import candidates as C
    out = []
    for n, v in sorted(ts.items()):
        mem = sorted(v["members"])
        if v["level"] != "leaf":
            continue
        sub = [e for e in ev if set(e["ones"]) & set(mem)]
        if len(mem) < 2 or len(sub) < 2:
            continue
        sub = [{**e, "ones": [c for c in e["ones"] if c in mem], "na": {c: x for c, x in e["na"].items() if c in mem}}
               for e in sub]
        late = member_stats(mem, sub, ev)
        rec = {"leaf": n, "size": len(mem), "events": len(sub), "late": sorted(c for c, x in late.items() if x),
               "perm_split": []}
        for order in range(PERMS + 1):
            seq = list(sub)
            if order:
                random.Random(order - 1).shuffle(seq)
            ser = C.run(name, seq, mem)
            i = next((j for j, g in enumerate(ser) if len(g) > 1), None)
            if order == 0:
                rec["split"] = None
                if i is not None:
                    kids = [sorted(g) for g in ser[i] if len(g) < len(mem)]
                    rest = sorted(set(mem) - set().union(*map(set, kids))) if kids else []
                    rec["split"] = {"event": i + 1, "close": seq[i]["close"],
                                    "parts": sorted(kids + ([rest] if rest else []), key=len)}
            else:
                rec["perm_split"].append(i is not None)
        out.append(rec)
    return out


def worker(item):
    try:
        return _worker(item)
    except Exception as ex:  # noqa: BLE001
        import traceback
        return {**item, "error": repr(ex), "tb": traceback.format_exc()[-2500:]}


def _worker(item):
    import candidates as C
    import npr0
    import npr0b
    import step12
    rd = Path(item["path"])
    before = folder_state(rd)
    npr0.CACHE = Path(item["cache"])
    row = npr0b._worker(rd)                         # frozen row builder (onsets T100, E0 / E1-0.5 events, truth)
    clients = row["clients"]
    ts = {n: {"members": frozenset(v["members"]), "level": v["level"]} for n, v in row["truth"].items()}
    ev = [e for e in row["cands"]["E1-0.5"] if e["ones"]]
    e0 = [e for e in row["cands"]["E0"] if e["ones"]]
    L = {n: set(v["members"]) for n, v in ts.items() if v["level"] == "leaf"}
    out = {k: v for k, v in item.items() if k != "cache"}
    out.update(n_clients=len(clients), n_leaves=len(L), n_events=len(ev), n_events_e0=len(e0),
               first_stim=step12.first_stim(rd, list(ts)),
               truth={n: {"members": sorted(v["members"]), "level": v["level"]} for n, v in ts.items()},
               check={"E1-0.5": hashlib.sha256(json.dumps(row["cands"]["E1-0.5"], sort_keys=True).encode()).hexdigest(),
                      "E0": hashlib.sha256(json.dumps(row["cands"]["E0"], sort_keys=True).encode()).hexdigest()})
    sep = None
    for i, e in enumerate(ev):
        H = set(e["hot"])
        on = [n for n in L if n in H or any(a in H for a, v in ts.items() if a != n and L[n] < set(v["members"]))]
        if 0 < len(on) < len(L):
            sep = i + 1
            break
    out["first_separating_event"] = sep
    out["cands"] = {}
    for name in ROWS_ORDER:
        base = name.split(" k")[0]
        k = 3 if name.endswith(" k3") else None
        events = e0 if C.CANDIDATES[base][2] == "E0" else ev
        ser = C.run(base, events, clients, k)
        rec = {"score": step12.score_series(ts, clients, events, lambda i, s=ser: s[i]),
               "first_split": next((j + 1 for j, g in enumerate(ser) if len(g) > 1), None),
               "events_basis": C.CANDIDATES[base][2],
               "curves": leaf_curves(ts, events, ser),
               "late": late_joiner(name, ts, clients, events)}
        if base in NPR_CANDS:
            rec["false_splits"] = false_splits(base, ts, ev)
        out["cands"][name] = rec
    after = folder_state(rd)
    out["run_folder_unchanged"] = before == after
    if before != after:
        raise RuntimeError(f"run folder changed: {rd}")
    return out


def cmd_rows(kind, rerun, jobs, only):
    out = OUT[kind]
    out.mkdir(parents=True, exist_ok=True)
    rows = out / "rows.jsonl"
    items = run_list(kind, rerun, only)
    missing = [r["path"] for r in items if not (Path(r["path"]) / "v3-checks.json").exists()]
    if missing:
        print(f"{len(missing)} runs missing or unfinished (no v3-checks.json), e.g. {missing[:3]}: not started",
              flush=True)
        return 2
    done = set()
    if rows.exists():
        good = [x for x in rows.read_text().splitlines() if x.strip().endswith("}") and '"error"' not in x]
        done = {json.loads(x)["run"] for x in good}
        rows.write_text("".join(x + "\n" for x in good))
    items = [{**r, "cache": str(out / "cache")} for r in items if r["run"] not in done]
    print(f"{len(items)} runs ({len(done)} already done)", flush=True)
    enc = lambda o: (sorted(o) if isinstance(o, (set, frozenset)) else  # noqa: E731
                     o.tolist() if hasattr(o, "tolist") else None if isinstance(o, float) and not math.isfinite(o) else str(o))
    with rows.open("a") as fh, Pool(jobs) as pool:
        for i, r in enumerate(pool.imap_unordered(worker, items), 1):
            fh.write(json.dumps(r, default=enc) + "\n")
            fh.flush()
            print(f"  {i}/{len(items)} {r['run']}{' ERROR ' + r['error'] if 'error' in r else ''}", flush=True)
    return 0


# ---------------------------------------------------------------------------------------------------------- report

def f_(x, d=3):
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{d}f}"


def q(a, p):
    return float(np.percentile(a, p)) if len(a) else None


def run_stats(r, name):
    """(pair vector, leaf F1 of the run or None): the step12_report.pooled ingredients for one run."""
    s = r["cands"][name]["score"]
    leaf = s["levels"].get("leaf")
    return np.array(s["pairs"], dtype=float), (leaf[2] if leaf else None)


def point(R, name):
    P = sum((run_stats(r, name)[0] for r in R), np.zeros(5))
    F = [run_stats(r, name)[1] for r in R]
    F = [x for x in F if x is not None]
    return (P[0] / (P[0] + P[1]) if P[0] + P[1] else None), (P[0] / (P[0] + P[2]) if P[0] + P[2] else None), \
        (float(np.mean(F)) if F else None)


class Boot:
    """Paired percentile bootstrap over runs within one seed column (a4-rules.md addendum): one generator, columns drawn
    in COL_ORDER; per replicate the same drawn runs for every candidate; a breakdown column uses the drawn runs that
    belong to it."""

    def __init__(self, cols: dict):
        rng = np.random.default_rng(BOOT_SEED)
        self.cols, self.idx = cols, {}
        for c in COL_ORDER:
            n = len(cols.get(c, []))
            self.idx[c] = rng.integers(0, n, size=(BOOT, n)) if n else None

    def stats(self, col, name, subset=None, ref=SETS_REF):
        R = self.cols[col]
        if self.idx[col] is None:
            return None
        pv = np.array([run_stats(r, name)[0] for r in R])
        fv = np.array([np.nan if run_stats(r, name)[1] is None else run_stats(r, name)[1] for r in R])
        fr = np.array([np.nan if run_stats(r, ref)[1] is None else run_stats(r, ref)[1] for r in R])
        keep = np.ones(len(R), bool) if subset is None else np.array([subset(r) for r in R])
        P, D, skipped = [], [], 0
        for row in self.idx[col]:
            row = row[keep[row]]
            if not len(row):
                skipped += 1
                continue
            s = pv[row].sum(axis=0)
            if s[0] + s[1]:
                P.append(s[0] / (s[0] + s[1]))
            ok = ~np.isnan(fv[row]) & ~np.isnan(fr[row])
            if ok.any():
                D.append(float(np.mean(fv[row][ok]) - np.mean(fr[row][ok])))
        ci = lambda a: (q(a, 2.5), q(a, 97.5)) if a else (None, None)   # noqa: E731
        return {"pP_ci": ci(P), "dF_ci": ci(D), "skipped": skipped}


def times(R, name):
    """step12_report.times: events and seconds from the leaf's first own stimulus to the first correct group."""
    ev, sec, never = [], [], 0
    for r in R:
        s = r["cands"][name]["score"]
        for n, (e, t) in s.get("t_ok", {}).items():
            ev.append(e)
            fs = r["first_stim"].get(n)
            if fs is not None:
                sec.append(t - fs)
        never += s.get("n_leaves", 0) - len(s.get("t_ok", {}))
    return {"ev": (q(ev, 50), q(ev, 90)), "s": (q(sec, 50), q(sec, 90)), "never": never}


def root_delay(R, name):
    """diag3: runs with two leaves: the candidate's first close with two or more groups minus the first separating
    event (E1-0.5 events; for SETS-v1.1 counted in its own E0 events, so not comparable)."""
    lag = [r["cands"][name]["first_split"] - r["first_separating_event"] for r in R
           if r["n_leaves"] == 2 and r["cands"][name]["first_split"] and r["first_separating_event"]]
    never = sum(1 for r in R if r["n_leaves"] == 2 and not r["cands"][name]["first_split"])
    return (q(lag, 50), q(lag, 90)), never, len(lag)


def late(R, name):
    xs = [x for r in R for x in r["cands"][name]["late"]]
    j = [x["seconds"] for x in xs if x.get("joined") and "seconds" in x]
    return sum(x["joined"] for x in xs), sum(x["released"] for x in xs), len(xs), (q(j, 50), q(j, 90))


def fsplit(R, name):
    """False-split share (original order) of true leaves alone; with / without a late responder in the leaf; split-off
    part holding a late responder; 20-order mean (reported only)."""
    C = [c for r in R for c in r["cands"][name].get("false_splits", [])]
    if not C:
        return None
    S_ = [c for c in C if c["split"]]
    wl = [c for c in C if c["late"]]
    wo = [c for c in C if not c["late"]]
    off_late = sum(1 for c in S_ if set(c["split"]["parts"][0]) & set(c["late"]))
    perm = [np.mean(c["perm_split"]) for c in C if c["perm_split"]]
    return {"share": len(S_) / len(C), "n": len(C), "k": len(S_),
            "with_late": (sum(1 for c in wl if c["split"]), len(wl)), "without_late": (sum(1 for c in wo if c["split"]), len(wo)),
            "off_late": off_late, "single_member": sum(1 for c in S_ if len(c["split"]["parts"][0]) == 1),
            "perm_mean": float(np.mean(perm)) if perm else None}


def plateau(R, name):
    """Per leaf: first own-event index from which the best F1 stays within PLATEAU_TOL of its final value; seconds =
    that close minus the leaf's first own stimulus. Accuracy by events seen: mean best F1 at the k-th own event."""
    pe, ps, acc = [], [], defaultdict(list)
    for r in R:
        for n, cur in r["cands"][name]["curves"].items():
            if not cur:
                continue
            fin = cur[-1][1]
            j = len(cur) - 1
            while j > 0 and abs(cur[j - 1][1] - fin) <= PLATEAU_TOL:
                j -= 1
            pe.append(cur[j][0])
            fs = r["first_stim"].get(n)
            if fs is not None:
                ps.append(cur[j][2] - fs)
            for k, f, _ in cur:
                acc[k if k in ACC_BINS else "more"].append(f)
    return {"ev": (q(pe, 50), q(pe, 90)), "s": (q(ps, 50), q(ps, 90)), "leaves": len(pe),
            "acc": {k: (float(np.mean(v)), len(v)) for k, v in acc.items()}}


def cell_of(r):
    return r["run"].rsplit("-r", 1)[0]


def cmd_report(kind):
    out = OUT[kind]
    R = [json.loads(x) for x in (out / "rows.jsonl").read_text().splitlines() if x.strip()]
    err = [r for r in R if "error" in r]
    R = [r for r in R if "error" not in r]
    extra = [r for r in R if r["table"] == "extra"]
    R = [r for r in R if r["table"] != "extra"]
    cols = defaultdict(list)
    for r in R:
        cols[f"{r['table']} {seed_col(r['rep'])}"].append(r)
    for c in cols:
        cols[c].sort(key=lambda r: r["run"])        # fixed run order: the draws index into this list
    boot = Boot(cols)
    L = [f"# A.4 validation{' (DEVELOPMENT RUNS: test of the code, not the validation)' if kind == 'dev' else ''} (a4.py)\n"]
    if err:
        L.append(f"**Errors: {len(err)} runs** ({', '.join(e['run'] for e in err[:10])}); not in the tables.\n")

    # columns that rest on few runs (notice only)
    breakdown = []   # (column label, table, seed, runs, selector)
    for t in ("main", "robustness"):
        for sc in ("r1", "r2", "r3+"):
            col = f"{t} {sc}"
            Rc = cols.get(col, [])
            for camp in sorted({r["campaign"] for r in Rc}):
                breakdown.append((f"campaign {camp}", t, sc, sum(r["campaign"] == camp for r in Rc),
                                  lambda r, camp=camp: r["campaign"] == camp))
            for cl in sorted({cell_of(r) for r in Rc}):
                breakdown.append((f"cell {cl}", t, sc, sum(cell_of(r) == cl for r in Rc), lambda r, cl=cl: cell_of(r) == cl))
            for lab, sel in (("FB-* cells", lambda r: str(r["type"]).startswith("fb")),
                             ("other cells", lambda r: not str(r["type"]).startswith("fb"))):
                breakdown.append((lab, t, sc, sum(sel(r) for r in Rc), sel))
    if True:
        few = sorted([b for b in breakdown if 0 < b[3] <= FEW_RUNS], key=lambda b: (b[3], b[1], b[2], b[0]))
        L.append(f"## Columns resting on {FEW_RUNS} runs or fewer (notice only: no value is marked unreliable or left "
                 "out; per-run values are shown for them below)\n")
        L.append("| runs | column | table | seed |\n|---|---|---|---|")
        L += [f"| {b[3]} | {b[0]} | {b[1]} | {b[2]} |" for b in few]
        L.append("")

    # main tables
    for t in ("main", "robustness"):
        L.append(f"## {t} table\n")
        L.append("| candidate | column | runs | pair P [95 %] | pair R | leaf F1 | leaf F1 - SETS-v1.1 [95 %] | "
                 "false-split share (k / leaves; 20-order mean) | root split delay p50 / p90 (n; never) | first correct "
                 "group events p50 / p90; s p50 / p90 (never) | late joiner joined / released (s p50 / p90) | plateau "
                 "events p50 / p90; s p50 / p90 |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for name in ROWS_ORDER:
            for sc in ("r1", "r2", "r3+"):
                col = f"{t} {sc}"
                Rc = cols.get(col, [])
                if not Rc:
                    continue
                pP, pR, F = point(Rc, name)
                _, _, Fs = point(Rc, SETS_REF)
                b = boot.stats(col, name)
                fs = fsplit(Rc, name)
                (d50, d90), dn, dk = root_delay(Rc, name)
                tm = times(Rc, name)
                lj = late(Rc, name)
                pl = plateau(Rc, name)
                L.append(f"| {name} | {sc} | {len(Rc)} | {f_(pP)} [{f_(b['pP_ci'][0])}, {f_(b['pP_ci'][1])}] | {f_(pR)} | "
                         f"{f_(F)} | {f_(None if F is None or Fs is None else F - Fs)} [{f_(b['dF_ci'][0])}, "
                         f"{f_(b['dF_ci'][1])}] | "
                         + (f"{f_(fs['share'])} ({fs['k']} / {fs['n']}; {f_(fs['perm_mean'])})" if fs else "-")
                         + f" | {f_(d50, 0)} / {f_(d90, 0)} ({dk}; {dn}) | {f_(tm['ev'][0], 0)} / {f_(tm['ev'][1], 0)}; "
                         f"{f_(tm['s'][0], 1)} / {f_(tm['s'][1], 1)} ({tm['never']}) | {lj[0]} / {lj[1]} "
                         f"({f_(lj[3][0], 1)} / {f_(lj[3][1], 1)}) | {f_(pl['ev'][0], 0)} / {f_(pl['ev'][1], 0)}; "
                         f"{f_(pl['s'][0], 1)} / {f_(pl['s'][1], 1)} |")
        L.append("")

    # flagged runs and their re-runs (extra rows, in no total)
    fl = [r for r in R if r["run"] in FLAGGED]
    if fl or extra:
        L.append("## Flagged runs (kept in their table) and extra re-run rows (in no total)\n")
        L.append("| run | table | row | pair P (NPR-B) | leaf F1 per candidate (NPR-B / NPR-A / NPR-A10 / SETS-v1.1) | note |")
        L.append("|---|---|---|---|---|---|")
        for r in fl + extra:
            base = r["run"].split("@")[0]
            row = "re-run (extra)" if r["table"] == "extra" else "original (in the table)"
            L.append(f"| {base} | {r['table'] if r['table'] != 'extra' else 'extra'} | {row} | "
                     f"{f_(point([r], 'NPR-B')[0])} | " + " / ".join(f_(point([r], n)[2]) for n in
                                                        ("NPR-B", "NPR-A", "NPR-A10", SETS_REF))
                     + f" | {FLAGGED.get(base, '') if r['table'] != 'extra' else 'shown next to the original; replaces nothing'} |")
        L.append("")

    # decision (main r1 / r2 totals only)
    L.append("## Decision (main table, r1 and r2 totals; a4-rules.md)\n")
    cond = {}
    for name in NPR_CANDS:
        for sc in ("r1", "r2", "r3+"):
            Rc = cols.get(f"main {sc}", [])
            if not Rc:
                continue
            pP, _, F = point(Rc, name)
            _, _, Fs = point(Rc, SETS_REF)
            fs = fsplit(Rc, name)
            cond[(name, sc)] = {"P": pP is not None and pP >= PAIR_P_MIN, "F": F is not None and Fs is not None and F >= Fs,
                                "S": fs is not None and fs["share"] <= ALPHA, "vals": (pP, F, Fs, fs["share"] if fs else None)}
    L.append("| candidate | seed | pair P >= 0.90 | leaf F1 >= SETS-v1.1 | false-split share <= alpha (NPR-A only) |")
    L.append("|---|---|---|---|---|")
    for (name, sc), c in cond.items():
        pP, F, Fs, s = c["vals"]
        L.append(f"| {name} | {sc} | {'yes' if c['P'] else 'no'} ({f_(pP)}) | {'yes' if c['F'] else 'no'} "
                 f"({f_(F)} vs {f_(Fs)}) | {'yes' if c['S'] else 'no'} ({f_(s)}) |")
    L.append("")
    text = None
    for name, extra in (("NPR-B", ()), ("NPR-A", ("S",))):
        keys = ("P", "F") + extra
        if not all((name, s) in cond for s in ("r1", "r2")):
            text = f"{name}: r1 or r2 missing; no decision."
            break
        r3 = cond.get((name, "r3+"))
        if r3 is not None:
            contra = [k for k in keys if (cond[(name, "r1")][k] and cond[(name, "r2")][k] and not r3[k]) or
                      (not cond[(name, "r1")][k] and not cond[(name, "r2")][k] and r3[k])]
            if contra:
                text = (f"**Not reliable**: the r3+ column contradicts r1 / r2 for {name} on {', '.join(contra)}. "
                        "Work stops (a4-rules.md).")
                break
        if all(cond[(name, s)]["P"] for s in ("r1", "r2")) and not all(cond[(name, s)]["F"] for s in ("r1", "r2")):
            diffs = []
            for s in ("r1", "r2"):
                pP, F, Fs, _ = cond[(name, s)]["vals"]
                b = boot.stats(f"main {s}", name)
                diffs.append(f"{s}: {f_(F)} vs SETS-v1.1 {f_(Fs)}, difference {f_(F - Fs)} [95 % {f_(b['dF_ci'][0])}, "
                             f"{f_(b['dF_ci'][1])}]")
            text = (f"**{name}: leaf F1 condition not met** ({'; '.join(diffs)}). Pair precision met. Per-cell breakdown "
                    "below. Stop: the user decides.")
            break
        if all(cond[(name, s)][k] for s in ("r1", "r2") for k in keys):
            text = f"**{name} passes** on the main table r1 and r2 totals."
            break
    if text is None:
        text = "Neither NPR-B nor NPR-A passes: SETS stays, NPR is future work (a4-rules.md)."
    L.append(text + " The other NPR rows are in the tables above.\n")

    # breakdown columns
    L.append("## Breakdown columns (point value, runs, interval on the restricted resampled-run lists)\n")
    L.append("| table | seed | column | runs | candidate | pair P [95 %] | leaf F1 | leaf F1 - SETS-v1.1 [95 %] | skipped "
             "replicates | per-run (pair P / leaf F1) |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for lab, t, sc, n, sel in breakdown:
        col = f"{t} {sc}"
        Rc = [r for r in cols.get(col, []) if sel(r)]
        if not Rc:
            continue
        for name in ("NPR-B", "NPR-A", "NPR-A10", SETS_REF):
            pP, _, F = point(Rc, name)
            _, _, Fs = point(Rc, SETS_REF)
            b = boot.stats(col, name, subset=sel)
            per = ""
            if n <= FEW_RUNS:
                per = "; ".join(f"{r['run_id']}: {f_(point([r], name)[0])} / {f_(point([r], name)[2])}" for r in Rc)
            L.append(f"| {t} | {sc} | {lab} | {n} | {name} | {f_(pP)} [{f_(b['pP_ci'][0])}, {f_(b['pP_ci'][1])}] | "
                     f"{f_(F)} | {f_(None if F is None or Fs is None else F - Fs)} [{f_(b['dF_ci'][0])}, "
                     f"{f_(b['dF_ci'][1])}] | {b['skipped']} | {per} |")
    L.append("\nIntervals computed from a handful of runs are rough and can be too narrow; the per-run values are shown "
             "for that reason.\n")

    # false splits by late responders, accuracy by events seen
    L.append("## False splits (leaf alone, original order): late-responder breakdown\n")
    L.append("| candidate | column | false splits / leaves | in leaves with a late responder | in leaves without | "
             "split-off part holds a late responder | single-member split-off |\n|---|---|---|---|---|---|---|")
    for name in NPR_CANDS:
        for col in COL_ORDER:
            fs = fsplit(cols.get(col, []), name) if cols.get(col) else None
            if fs:
                L.append(f"| {name} | {col} | {fs['k']} / {fs['n']} | {fs['with_late'][0]} / {fs['with_late'][1]} | "
                         f"{fs['without_late'][0]} / {fs['without_late'][1]} | {fs['off_late']} / {fs['k']} | "
                         f"{fs['single_member']} / {fs['k']} |")
    vals = [fsplit(cols.get(f"main {s}", []), "NPR-B") for s in ("r1", "r2")]
    if all(vals):
        L.append(f"\nNPR-B false-split share across seeds (range): {f_(min(v['share'] for v in vals))} - "
                 f"{f_(max(v['share'] for v in vals))}.\n")
    L.append("## Accuracy by events seen (main table; mean best leaf F1 at the leaf's k-th own event; leaves)\n")
    L.append("| candidate | seed | " + " | ".join(str(k) for k in ACC_BINS) + " | more |\n|" + "---|" * (len(ACC_BINS) + 3))
    for name in ROWS_ORDER:
        for sc in ("r1", "r2"):
            Rc = cols.get(f"main {sc}", [])
            if not Rc:
                continue
            a = plateau(Rc, name)["acc"]
            L.append(f"| {name} | {sc} | " + " | ".join(f"{f_(a[k][0])} ({a[k][1]})" if k in a else "-"
                                                    for k in (*ACC_BINS, "more")) + " |")
    L.append("")
    (out / "report.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


def main(argv):
    kind = argv[argv.index("--set") + 1] if "--set" in argv else None
    if kind not in OUT or not argv or argv[0] not in ("rows", "report"):
        print(__doc__)
        return 2
    if argv[0] == "rows":
        rerun = Path(argv[argv.index("--rerun") + 1]).resolve() if "--rerun" in argv else None
        only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
        jobs = int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 2
        return cmd_rows(kind, rerun, jobs, only)
    return cmd_report(kind)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
