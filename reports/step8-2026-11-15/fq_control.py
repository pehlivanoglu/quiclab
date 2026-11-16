#!/usr/bin/env python3
"""Step 8 part E (decision 2026-11-15): per-flow-queue egresses as a grouping negative control.
Measurement only; ECG v1.2, h3 (replay4, m = 3) and the step 6 readers are called unchanged.

    .venv/bin/python3 reports/step8-2026-11-15/fq_control.py rows .runs/2026-11-14_1818_v3   # -> fq-rows.jsonl
    .venv/bin/python3 reports/step8-2026-11-15/fq_control.py report .runs/2026-11-14_1818_v3 > reports/step8-2026-11-15/fq-control.md

Truth (decision): no two instrumented clients behind a per-flow-queue egress share a queue there. A pair of
clients shares a queue only through an ordinary (single-queue) egress on both paths: in v3 that is only
mixab (M8: r1 -> r2 'up' pfifo, r2 -> switch-a pfifo, r2 -> switch-b fq_codel). True sets = clients behind
each ordinary shaped egress; a pair is a false grouping when the two clients share no ordinary shaped egress
(all pairs in the all-fq_codel cells; b-b pairs in M8 unless the group is the up set; a-b pairs in M8
reported separately as mixed). Groups: ECG nodes with L >= A after each event (step 6 ecg_closes), h3
groups after each event (replay4 trajectory).
Pinning check (every fq_codel run of the campaign): truth/gtq-params.csv fq_index per client and egress
(mode of the client's packets, gtq.fq_index) and fq_collision (other 5-tuples in that sub-queue).
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import step8  # noqa: E402

s6, s4, s2, d, diag = step8.s6, step8.s4, step8.s2, step8.d, step8.diag
CELLS = ("v3-C7-hhier-s030-fq_codel-", "v3-C9-hdepth-tree16-fq_codel-", "v3-C10-hindep-s030-fq_codel-",
         "v3-C12-amixed-access-fq_codel-", "v3-M8-hhier-mixab-")
CTRL = "sub-ctrl"


def egress_aqm(rd: Path, plan) -> dict:
    """plan egress name -> AQM of its qdisc (qdiscs.txt, matched by the router's device facing the next node)."""
    qd, dev = {}, None
    for line in (rd / "qdiscs.txt").read_text().splitlines():
        if line.startswith("=="):
            dev = line.split()[2]
        elif line.startswith("qdisc ") and line.split()[1] in ("fq_codel", "pfifo", "codel", "pie", "cake"):
            qd[dev] = line.split()[1]
    run = d.Run(rd)
    out = {}
    for n, e in plan["egress"].items():
        a, b = e["hop"].split("->")
        iface = None
        try:
            from quiclab.runtime import edge_interfaces
            iface = edge_interfaces(run.topology)[(a, b)] if (a, b) in edge_interfaces(run.topology) else None
        except Exception:   # noqa: BLE001
            iface = None
        if iface is None:   # traced egresses: router-trace/interfaces.csv
            meta = rd / "router-trace" / "interfaces.csv"
            for r in d.rows(meta) if meta.exists() else []:
                if r["hop"] == e["hop"]:
                    iface = r["iface"]
        out[n] = qd.get(iface, plan["aqm"] if plan["aqm"] != "mixab" else None) if e.get("shaped", True) else "unshaped"
    return out


def one(rd: Path):
    try:
        plan = json.loads((rd / "v3-plan.json").read_text())
        aqm = egress_aqm(rd, plan)
        ordinary = {n: sorted(set(e["clients"]) - {CTRL}) for n, e in plan["egress"].items()
                    if e.get("shaped", True) and aqm[n] not in ("fq_codel", "cake", "unshaped", None)}
        out = {"run": rd.name, "cell": rd.name.rsplit("-r", 1)[0][3:], "rep": plan["rep"], "egress_aqm": aqm,
               "egress_hop": {n: e["hop"] for n, e in plan["egress"].items()}, "ordinary": ordinary,
               "clients": sorted({c for e in plan["egress"].values() for c in e["clients"]} - {CTRL}),
               "levels": {n: step8.level_of(n) for n in plan["egress"]},
               "behind": {n: sorted(set(e["clients"]) - {CTRL}) for n, e in plan["egress"].items()}}
        st = diag.stimuli(rd)
        for src in step8.SRC:
            v = step8.view(rd, src)
            run, truth, subs, windows, events = s4.load_events(v, ecg_intervals=True)
            leaf = {s: frozenset(x) for s, x in truth["leaf"].items() if x}
            m, evs, closes = s6.ecg_closes(v, run, leaf)
            ev = [{"t0": e["t0"], "obs": sorted(set(e["members"]) - {CTRL}),
                   "stim": sorted({s_["target"] for s_ in diag.stim_at(st, e["t0"])}),
                   "groups": {str(k): sorted(set(g) - {CTRL}) for k, g in closes[x].items()}} for x, e in enumerate(evs)]
            h3 = []
            if events:
                h = s4.replay4(events, subs, truth["pairs_leaf"], leaf, 3, True)
                bb = round(h["b"], 2)
                for e_, t in zip(events, h["traj"]):
                    t0 = e_[0]["lo"] - s2.NEG_SPAN[0]
                    h3.append({"t0": t0, "stim": sorted({s_["target"] for s_ in diag.stim_at(st, t0)}),
                               "groups": {k: sorted(set(i for i, x in r_.items() if x >= bb) - {CTRL}) for k, r_ in t.items()}})
            out[src] = {"ecg": ev, "h3": h3}
        return out
    except Exception as e:   # noqa: BLE001
        import traceback
        return {"run": rd.name, "error": repr(e), "tb": traceback.format_exc()[-1500:]}


# ── report ───────────────────────────────────────────────────────────────

f = lambda x, k=2: "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{k}f}"   # noqa: E731


def pair_kind(r, a, b, group):
    """'ok' (share an ordinary egress), 'false', 'mixed' (M8: one client on each branch)."""
    if any(a in v and b in v for v in r["ordinary"].values()):
        if r["cell"].startswith("M8") and sorted(group) != sorted(r["ordinary"].get("up", [])) and \
                not (a in r["behind"]["a"] and b in r["behind"]["a"]):
            # shares only the up pfifo but the group is not the up set
            return "mixed" if (a in r["behind"]["a"]) != (b in r["behind"]["a"]) else "false"
        return "ok"
    return "false"


def close_stats(r, groups):
    fg = fp = mx = ok = 0
    for g in groups.values():
        if len(g) < 2:
            continue
        kinds = Counter(pair_kind(r, a, b, g) for a, b in combinations(sorted(g), 2))
        fp += kinds["false"]
        mx += kinds["mixed"]
        ok += kinds["ok"]
        fg += bool(kinds["false"] or kinds["mixed"])
    return fg, fp, mx, ok


def lifetimes(r, closes):
    """false groups by id: first / last close with a false or mixed pair, creating close's stimulus."""
    life = {}
    for x, c in enumerate(closes):
        for k, g in c["groups"].items():
            if len(g) < 2:
                continue
            bad = any(pair_kind(r, a, b, g) != "ok" for a, b in combinations(sorted(g), 2))
            if bad:
                L = life.setdefault(k, {"first": x, "t_first": c["t0"], "stim": c["stim"], "size": len(g)})
                L["last"], L["t_last"] = x, c["t0"]
    return life


def stim_level(r, stim):
    if not stim:
        return "none"
    lv = sorted({r["levels"].get(s_, "leaf") for s_ in stim})
    return "+".join(lv) + (" (" + "+".join(stim) + ")")


def report(kdir: Path):
    R = sorted((json.loads(x) for x in open(HERE / "fq-rows.jsonl") if x.strip()), key=lambda r: r["run"])
    err = [r for r in R if "error" in r]
    R = [r for r in R if "error" not in r]
    print("# Step 8 part E: per-flow-queue egresses as a negative control\n")
    if err:
        print("Errors: " + "; ".join(f"{e['run']}: {e['error']}" for e in err) + "\n")
    print("## E5. Which egresses are per-flow, per cell (qdiscs.txt)\n")
    print("| cell | egress (hop): AQM | ordinary (single-queue) shaped egresses | true sets |")
    print("|---|---|---|---|")
    seen = set()
    for r in R:
        if r["cell"] in seen:
            continue
        seen.add(r["cell"])
        eg = ", ".join(f"{n} ({r['egress_hop'][n]}): {a}" for n, a in r["egress_aqm"].items())
        print(f"| {r['cell']} | {eg} | {', '.join(r['ordinary']) or 'none'} | "
              f"{', '.join(f'{n} {{{len(v)}}}' for n, v in r['ordinary'].items() if len(v) >= 2) or 'none (no group is correct)'} |")
    print()
    for src in step8.SRC:
        print(f"## E1. False groupings per close (mean over the run) and at the end, onset source {src}; rep 1 / rep 2\n")
        print("| cell | method | closes | false groups / close | false pairs / close | mixed pairs / close (M8) | correct pairs / close | "
              "false groups at end | false pairs at end | mixed at end |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        cells = defaultdict(dict)
        for r in R:
            cells[r["cell"]][r["rep"]] = r
        for c, reps in cells.items():
            for meth in ("ecg", "h3"):
                vals = []
                for rep in (1, 2):
                    if rep not in reps:
                        vals.append(None)
                        continue
                    cl = reps[rep][src][meth]
                    st = [close_stats(reps[rep], x["groups"]) for x in cl]
                    end = st[-1] if st else (0, 0, 0, 0)
                    vals.append((len(cl), *[float(np.mean([s_[i] for s_ in st])) if st else math.nan for i in range(4)], *end[:3]))
                g = lambda i, k=2: " / ".join("-" if v is None else (str(v[i]) if i in (0, 5, 6, 7) else f(v[i], k)) for v in vals)  # noqa: E731
                print(f"| {c} | {meth} | {g(0)} | {g(1)} | {g(2)} | {g(3)} | {g(4)} | {g(5)} | {g(6)} | {g(7)} |")
        print()
        print(f"## E2. Lifetime of false groups ({src}): closes and seconds from the first to the last close in which the group "
              "holds a false or mixed pair; the stimulus active when it first did\n")
        print("| cell | method | rep | false groups | life p50 closes (max) | life p50 s (max) | created during (count) |")
        print("|---|---|---|---|---|---|---|")
        for c, reps in cells.items():
            for meth in ("ecg", "h3"):
                for rep in (1, 2):
                    if rep not in reps:
                        continue
                    r = reps[rep]
                    L = lifetimes(r, r[src][meth])
                    if not L:
                        print(f"| {c} | {meth} | {rep} | 0 | - | - | - |")
                        continue
                    lc = [x["last"] - x["first"] + 1 for x in L.values()]
                    ls = [x["t_last"] - x["t_first"] for x in L.values()]
                    cr = Counter(stim_level(r, x["stim"]) for x in L.values())
                    print(f"| {c} | {meth} | {rep} | {len(L)} | {f(float(np.median(lc)), 0)} ({max(lc)}) | "
                          f"{f(float(np.median(ls)), 0)} ({f(max(ls), 0)}) | {'; '.join(f'{k} {v}' for k, v in cr.most_common(4))} |")
        print()
        print(f"## E3. Recurring observed sets ({src}): every set of >= 2 clients that is not a true set is a false set\n")
        print("| cell | rep | events | false sets >= 2 / >= 3 / >= 4 | true sets >= 2 | most frequent sets (count) |")
        print("|---|---|---|---|---|---|")
        for c, reps in cells.items():
            for rep in (1, 2):
                if rep not in reps:
                    continue
                r = reps[rep]
                cnt = Counter(frozenset(e["obs"]) for e in r[src]["ecg"] if len(e["obs"]) >= 2)
                trues = {frozenset(v) for v in r["ordinary"].values() if len(v) >= 2}
                fk = [sum(1 for S, k_ in cnt.items() if S not in trues and k_ >= k) for k in (2, 3, 4)]
                tk = sum(cnt[S] >= 2 for S in trues)
                top = ", ".join(("**" if S in trues else "") + "{" + ",".join(sorted(S)) + "}" + ("**" if S in trues else "") + f" {k_}"
                                for S, k_ in cnt.most_common(6))
                print(f"| {c} | {rep} | {len(r[src]['ecg'])} | {' / '.join(map(str, fk))} | {tk} of {len(trues)} | {top} |")
        print()

    # E-a pinning check over every fq_codel / mixab run of the campaign
    print("## Ea. Sub-queue pinning check (every fq_codel and mixab run; truth/gtq-params.csv)\n")
    rows, bad, coll, nruns = [], 0, Counter(), 0
    for rd in sorted(p for p in kdir.iterdir() if p.is_dir() and ("fq_codel" in p.name or "mixab" in p.name)):
        pp = rd / "truth" / "gtq-params.csv"
        if not pp.exists():
            rows.append((rd.name, "no gtq-params (GT-Q invalid)"))
            continue
        nruns += 1
        ips = None
        try:
            import gtq
            ips = gtq.loopbacks(d.Run(rd))
        except Exception:   # noqa: BLE001
            ips = {}
        client_ip = {v: k for k, v in ips.items()}
        by = defaultdict(dict)
        for r_ in d.rows(pp):
            if r_["aqm"] != "fq_codel" or r_["direction"] != "forward" or r_["flow"] == CTRL:
                continue
            by[r_["resource"]][r_["flow"]] = (int(r_["fq_index"]), r_["fq_collision"])
        for res, fl in by.items():
            idx = Counter(v[0] for v in fl.values())
            dup = [i for i, n in idx.items() if n > 1]
            bad += bool(dup)
            for fl_, (i, col) in fl.items():
                for t in filter(None, col.split(";")):
                    dst = t.split(">")[1].split(":")[0] if ">" in t else ""
                    owner = client_ip.get(dst)
                    coll["same client (other 5-tuple to it)" if owner == fl_ else
                         "another instrumented client" if owner and owner != CTRL and owner in fl else "other traffic"] += 1
            rows.append((rd.name, f"{res}: {len(fl)} clients, indices {min(idx)}-{max(idx)}, shared indices {dup or 'none'}"))
    print(f"Runs checked: {nruns}; egresses where two instrumented clients share a sub-queue index: {bad}. "
          f"Other 5-tuples found in a client's sub-queue: {dict(coll)}.\n")
    for name, txt in rows[:400]:
        print(f"- {name}: {txt}")
    print()


if __name__ == "__main__":
    kdir = Path(sys.argv[2])
    if sys.argv[1] == "rows":
        runs = [p for p in sorted(kdir.iterdir()) if p.is_dir() and p.name.startswith(CELLS)]
        with Pool(8) as pool, open(HERE / "fq-rows.jsonl", "w") as fh:
            for r in pool.imap_unordered(one, runs):
                fh.write(json.dumps(r) + "\n")
    else:
        report(kdir)
