#!/usr/bin/env python3
"""One scorer for the three grouping methods (SETS v1, ECG v1.2, h3), used from 2026-11-15 on.

    .venv/bin/python3 scripts/grouping_score.py rows .runs/<campaign> [out.jsonl]     # score every grouping run
    .venv/bin/python3 scripts/grouping_score.py report out.jsonl > tables.md

Methods (detector onsets, the run's grouping-d150-v2-owd ECG output):
  SETS   grouping.SetsEngine replayed from the run's onset log; k = 2 and 3; crossing filter off and on
  ECG    the run's ECG v1.2 output: after each event, the flows whose L >= A on a node form that node's group
  h3     scripts/grouping_step4.replay4 (m = 3, half test) on the ECG event intervals; groups = E >= b
Truth (per run; true sets of >= 2 clients):
  ordinary (single-queue) shaped egress   the clients behind it
  per-flow-queue egress (fq_codel, cake)  "same link": the clients behind it whose own sub-queue has a per-client
                                          GT1 episode (gt1.run_flow_truth via grouping_adapter) overlapping a
                                          stimulus window on that egress, [start, end + 2 s] (M); clients never
                                          constrained are correct when left out
  level   leaf / mid / up / root by plan egress name; leaf sets are the headline, the others a side table
  pairs   same-leaf: the two clients are in one leaf true set
  upstream event: an ECG event in whose [t0 - 1 s, t0 + 2 s] a non-leaf shaped egress has GT1 episodes covering
                  >= half (step 7 STRICT rule); "events of a leaf": events where its egress does
Scores, per run and method, averaged over every event close (never the final snapshot):
  leaf P / R / F1 of the best-matching group per true leaf (no group: R 0); exact share as reference;
  spurious groups per close (groups that are no true set's best match); pair P / R / coverage from each client's
  smallest group; leaf F1 at closes right after an upstream event vs the other closes; events of the leaf and
  seconds until a group with F1 >= 0.9 (FLAG); late joiner (one client of each leaf of >= 3, the last by name
  (M), hidden until the rest has a group with F1 >= 0.9, then released; SETS and ECG replayed with the client's
  onsets withheld, h3 with replay4(hide=...)); mid / up / root best-match F1.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

CTRL = "sub-ctrl"
F1_OK = 0.9              # (FLAG)
STIM_TAIL_S = 2.0        # (M)
NEG_SPAN = (-1.0, 2.0)   # (M) event interval for congestion bookkeeping (step 7)
STRICT = 0.5             # (M) step 7 strict coverage
GROUP_BLOCKS = ("C7", "C8", "C9", "C10", "C11", "C12", "C13", "M7", "M8")
LEVEL = lambda name: {"root": "root", "X": "mid", "Y": "mid", "up": "up"}.get(name, "leaf")   # noqa: E731


def _f1(g, t):
    i = len(g & t)
    if not i:
        return 0.0, 0.0, 0.0
    p, r = i / len(g), i / len(t)
    return p, r, 2 * p * r / (p + r)


def egress_aqm(rd: Path, plan: dict) -> dict:
    qd, dev = {}, None
    for line in (rd / "qdiscs.txt").read_text().splitlines():
        if line.startswith("=="):
            dev = line.split()[2]
        elif line.startswith("qdisc ") and line.split()[1] in ("fq_codel", "pfifo", "codel", "pie", "cake", "red"):
            qd[dev] = line.split()[1]
    iface = {}
    meta = rd / "router-trace" / "interfaces.csv"
    if meta.exists():
        for r in csv.DictReader(meta.open()):
            iface[r["hop"]] = r["iface"]
    return {n: (qd.get(iface.get(e["hop"]), plan["aqm"]) if e.get("shaped", True) else "unshaped") for n, e in plan["egress"].items()}


def truth_sets(rd: Path, run, plan: dict) -> dict:
    """name -> {"members", "level", "kind"} (ordinary / same-link)."""
    import grouping_adapter as ga
    aqm = egress_aqm(rd, plan)
    out = {}
    flow_eps = None
    stim = list(csv.DictReader((rd / "v3-stimuli.csv").open())) if (rd / "v3-stimuli.csv").exists() else []
    for n, e in plan["egress"].items():
        if not e.get("shaped", True):
            continue
        clients = sorted(set(e["clients"]) - {CTRL})
        if aqm[n] in ("fq_codel", "cake"):
            if flow_eps is None:
                flow_eps = ga.gt1_hop_flow_episodes(run)
            wins = [(float(s["start"]), float(s["end"]) + STIM_TAIL_S) for s in stim if s["hop"] == e["hop"]]
            eps = flow_eps.get(e["hop"], {})
            mem = sorted(c for c in clients if any(a <= hi and b >= lo for a, b in eps.get(c, []) for lo, hi in wins))
            kind = "same-link"
        else:
            mem, kind = clients, "ordinary"
        if len(mem) >= 2:
            out[n] = {"members": mem, "level": LEVEL(n), "kind": kind, "hop": e["hop"]}
    return out


def strict_hot(eps, lo, hi):
    return {h for h, v in eps.items() if sum(max(0.0, min(b, hi) - max(a, lo)) for a, b in v) >= STRICT * (hi - lo)}


class Score:
    """Accumulates one method's per-close scores over a run."""

    def __init__(self, ts: dict, clients: list[str]):
        self.ts = {n: frozenset(v["members"]) for n, v in ts.items()}
        self.lv = {n: v["level"] for n, v in ts.items()}
        self.leaves = {n: s for n, s in self.ts.items() if self.lv[n] == "leaf"}
        self.clients = clients
        self.rank = {c: i for i, c in enumerate(clients)}
        self.lev = defaultdict(lambda: np.zeros(4))
        self.lev_n = Counter()
        self.spur, self.rob = [], {"up": [], "other": []}
        self.pairs = np.zeros(5)
        self.t_ok, self.leaf_events = {}, Counter()

    def close(self, t: float, hot_levels: set, hot_names: set, groups: list[frozenset]):
        for n in self.leaves:
            if n in hot_names:
                self.leaf_events[n] += 1
        bests, leaf_f = set(), []
        for n, t_ in self.ts.items():
            best = max(((_f1(g, t_), g) for g in groups), key=lambda z: z[0][2], default=((0.0, 0.0, 0.0), None))
            (p, r, f), g = best
            self.lev[self.lv[n]] += (p if g is not None else 0.0, r, f, float(g == t_))
            self.lev_n[self.lv[n]] += 1
            if g is not None:
                bests.add(g)
            if self.lv[n] == "leaf":
                leaf_f.append(f)
                if f >= F1_OK and n not in self.t_ok:
                    self.t_ok[n] = (self.leaf_events[n], t)
        self.spur.append(sum(g not in bests for g in groups))
        if leaf_f:
            self.rob["up" if hot_levels - {"leaf"} else "other"].append(float(np.mean(leaf_f)))
        key = lambda g: tuple(sorted((self.rank.get(c, -1) for c in g), reverse=True))   # noqa: E731
        small = {}
        for c in self.clients:
            cg = [g for g in groups if c in g]
            if cg:
                small[c] = min(cg, key=lambda g: (len(g), key(g)))
        for i, a in enumerate(self.clients):
            for b in self.clients[i + 1:]:
                same = any(a in s and b in s for s in self.leaves.values())
                if a not in small or b not in small:
                    self.pairs[4] += 1
                elif small[a] == small[b]:
                    self.pairs[0 if same else 1] += 1
                else:
                    self.pairs[2 if same else 3] += 1

    def summary(self) -> dict:
        return {"levels": {lv: list(self.lev[lv] / self.lev_n[lv]) for lv in self.lev}, "n_true": dict(Counter(self.lv.values())),
                "spur": float(np.mean(self.spur)) if self.spur else math.nan, "pairs": list(self.pairs),
                "robust": {k: (float(np.mean(v)) if v else math.nan) for k, v in self.rob.items()},
                "robust_n": {k: len(v) for k, v in self.rob.items()}, "t_ok": self.t_ok, "n_leaves": len(self.leaves)}


def ecg_groups_from_engine(eng) -> list[frozenset]:
    g = defaultdict(set)
    for f, st in eng.state.items():
        if f != CTRL and st.node is not None and st.L >= eng.A:
            g[st.node].add(f)
    return [frozenset(v) for v in g.values() if len(v) >= 2]


def run_row(rd: Path) -> dict:
    try:
        import det_eval as d
        import grouping_adapter as ga
        import grouping_step4 as s4
        from grouping import Config, Engine
        from grouping.sets_engine import replay_records
        from grouping.synth import read_log
        plan = json.loads((rd / "v3-plan.json").read_text())
        run = d.Run(rd)
        gdir = rd / "grouping-d150-v2-owd"
        m = json.loads((gdir / "metrics.json").read_text())
        cfg = Config.from_dict(m["config"])
        ts = truth_sets(rd, run, plan)
        clients = sorted({c for e in plan["egress"].values() for c in e["clients"]} - {CTRL})
        level_of = {n: LEVEL(n) for n in plan["egress"]}
        hop_name = {e["hop"]: n for n, e in plan["egress"].items()}
        geps = {hop_name[h]: v for h, v in ga.gt1_hop_episodes(run).items() if h in hop_name}

        def hot(t0):
            names = strict_hot(geps, t0 + NEG_SPAN[0], t0 + NEG_SPAN[1])
            return {level_of[n] for n in names}, names

        records = list(read_log(gdir / "onsets.jsonl"))
        out = {"run": rd.name, "cell": rd.name.rsplit("-r", 1)[0][3:], "block": plan["block"], "aqm": plan["aqm"],
               "rep": plan["rep"], "truth": ts, "methods": {}}
        # SETS
        sc = {(k, c): Score(ts, clients) for k in (2, 3) for c in (False, True)}

        def on_close(eng, e):
            hl, hn = hot(e.t0)
            for (k, c), s in sc.items():
                s.close(eng.now, hl, hn, [frozenset(g.members) for g in eng.groups(k, crossing=c)])
        replay_records(records, cfg, exclude={CTRL}, on_close=on_close)
        for (k, c), s in sc.items():
            out["methods"][f"SETS k{k}" + (" +cross" if c else "")] = s.summary()
        # ECG (the run's own output, every event close)
        A = cfg.A
        s = Score(ts, clients)
        for x, e in enumerate(m["events"]):
            g = defaultdict(set)
            for f, ser in m["series"].items():
                if f == CTRL:
                    continue
                hit = ser[x] if x < len(ser) and abs(ser[x][0] - e["t"]) < 1e-6 else next((y for y in ser if abs(y[0] - e["t"]) < 1e-6), None)
                if hit and hit[1] is not None and hit[2] >= A:
                    g[hit[1]].add(f)
            hl, hn = hot(e["t0"])
            s.close(e["t"], hl, hn, [frozenset(v) for v in g.values() if len(v) >= 2])
        out["methods"]["ECG"] = s.summary()
        # h3
        _, truth, subs, windows, events = s4.load_events(rd, ecg_intervals=True)
        leaf = {x: frozenset(v) for x, v in truth["leaf"].items() if v}
        same = truth["pairs_leaf"]
        s = Score(ts, clients)
        if events:
            h = s4.replay4(events, subs, same, leaf, 3, True)
            bb = round(h["b"], 2)
            for ev, t in zip(events, h["traj"]):
                t0 = ev[0]["lo"] - NEG_SPAN[0]
                gs = [frozenset(i for i, x in r_.items() if x >= bb and i != CTRL) for r_ in t.values()]
                hl, hn = hot(t0)
                s.close(ev[0]["hi"], hl, hn, [g for g in gs if len(g) >= 2])
        out["methods"]["h3"] = s.summary()
        # late joiner
        late = []
        for n, info in ts.items():
            if info["level"] != "leaf" or len(info["members"]) < 3:
                continue
            L = frozenset(info["members"])
            hid = max(info["members"])
            rest = L - {hid}
            for meth in ("SETS k2", "SETS k3", "ECG"):
                st = {"rel": None, "join": None, "x": 0}

                def check(groups, t):
                    st["x"] += 1
                    if st["join"] is not None:
                        return
                    if st["rel"] is None:
                        if any(_f1(g, rest)[2] >= F1_OK for g in groups):
                            st["rel"] = (st["x"], t)
                    elif any(hid in g and _f1(g, L)[2] >= F1_OK for g in groups):
                        st["join"] = (st["x"], t)
                hide = lambda eng, o: o.flow == hid and st["rel"] is None   # noqa: E731
                if meth.startswith("SETS"):
                    k = int(meth[-1])
                    replay_records(records, cfg, exclude={CTRL}, hide=hide,
                                   on_close=lambda eng, e: check([frozenset(g.members) for g in eng.groups(k)], eng.now))
                else:
                    eng = Engine(cfg)
                    eng.on_event_closed.append(lambda en, e, case: check(ecg_groups_from_engine(en), en.now))
                    nt = 0.0
                    for kind, t, obj in records:
                        while nt <= t:
                            eng.tick(nt)
                            nt = round(nt + cfg.obs_window, 6)
                        if kind == "meta":
                            eng.on_meta(obj)
                        elif kind == "obs":
                            eng.on_obs(obj)
                        elif not hide(eng, obj):
                            eng.on_onset(obj)
                    eng.finish()
                rec = {"leaf": n, "method": meth, "released": st["rel"] is not None, "joined": st["join"] is not None}
                if st["rel"] and st["join"]:
                    rec.update(events=st["join"][0] - st["rel"][0], seconds=st["join"][1] - st["rel"][1])
                late.append(rec)
            if events:
                j = s4.replay4(events, subs, same, leaf, 3, True, hide=(hid, sorted(rest)))
                rec = {"leaf": n, "method": "h3", "released": j is not None, "joined": bool(j and j.get("joined"))}
                if j and j.get("joined"):
                    rec.update(events=j["joined"]["events"], seconds=j["joined"]["s"])
                late.append(rec)
        out["late"] = late
        return out
    except Exception as e:   # noqa: BLE001
        import traceback
        return {"run": rd.name, "error": repr(e), "tb": traceback.format_exc()[-2000:]}


def runs_of(kdir: Path) -> list[Path]:
    out = []
    for p in sorted(kdir.iterdir()):
        if p.is_dir() and p.name.startswith("v3-") and p.name.split("-")[1] in GROUP_BLOCKS \
                and (p / "grouping-d150-v2-owd" / "metrics.json").exists():
            out.append(p)
    return out


# ── report ───────────────────────────────────────────────────────────────

METHODS = ["SETS k2", "SETS k3", "SETS k2 +cross", "SETS k3 +cross", "ECG", "h3"]
f_ = lambda x, k=2: "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{k}f}"   # noqa: E731


def flags(vals: dict) -> set:
    """Cells whose rep difference exceeds the largest of the other cells of the block (>= 2 others): not reliable."""
    by = defaultdict(dict)
    for c, (a, b) in vals.items():
        if a is not None and b is not None and not (math.isnan(a) or math.isnan(b)):
            by[c.split("-")[0]][c] = abs(a - b)
    out = set()
    for dd in by.values():
        for c, v in dd.items():
            o = [x for k, x in dd.items() if k != c]
            if len(o) >= 2 and v > max(o) + 1e-12:
                out.add(c)
    return out


def report(path: Path) -> None:
    R = [json.loads(x) for x in open(path) if x.strip()]
    err = [r for r in R if "error" in r]
    R = [r for r in R if "error" not in r]
    print("# Grouping scores (scripts/grouping_score.py): SETS v1, ECG v1.2, h3\n")
    if err:
        print("Errors: " + "; ".join(f"{e['run']}: {e['error']}" for e in err) + "\n")
    print("Detector onsets. Every value rep 1 / rep 2; `*` = rep difference larger than every other cell of the block "
          "(>= 2 others): not reliable. fq_codel cells and the M8 fq_codel leaf are scored with the same-link truth.\n")
    cells = defaultdict(dict)
    for r in R:
        cells[r["cell"]][r["rep"]] = r
    order = sorted(cells, key=lambda c: (GROUP_BLOCKS.index(c.split("-")[0]), c))

    def val(c, rep, meth, fn):
        r = cells[c].get(rep)
        return fn(r["methods"][meth]) if r else None

    leafF = lambda s: s["levels"]["leaf"][2] if "leaf" in s["levels"] else None   # noqa: E731
    pairP = lambda s: s["pairs"][0] / (s["pairs"][0] + s["pairs"][1]) if s["pairs"][0] + s["pairs"][1] else None   # noqa: E731
    pairR = lambda s: s["pairs"][0] / (s["pairs"][0] + s["pairs"][2]) if s["pairs"][0] + s["pairs"][2] else None   # noqa: E731
    for title, fn in (("Leaf F1 (best-matching group per true leaf, mean over closes)", leafF),
                      ("Pair precision (same-leaf truth; each client's smallest group; summed over closes)", pairP),
                      ("Pair recall", pairR), ("Spurious groups per close", lambda s: s["spur"])):
        print(f"## {title}\n")
        print("| cell | " + " | ".join(METHODS) + " |")
        print("|---|" + "---|" * len(METHODS))
        fl = {m_: flags({c: (val(c, 1, m_, fn), val(c, 2, m_, fn)) for c in order}) for m_ in METHODS}
        for c in order:
            print(f"| {c} | " + " | ".join(" / ".join(f_(val(c, rep, m_, fn)) for rep in (1, 2)) + ("*" if c in fl[m_] else "")
                                         for m_ in METHODS) + " |")
        print()
    for title, sel in (("single-queue AQM cells (pfifo, codel, pie, mixab; M8's fq_codel leaf with the same-link truth)",
                        lambda r: r["aqm"] != "fq_codel"),
                       ("fq_codel cells (same-link truth)", lambda r: r["aqm"] == "fq_codel")):
        pooled(R, sel, title)
    _time_tables(R)


def pooled(R, sel, title):
    print(f"## Pooled per rep: {title}\n")
    print("| method | leaf P | leaf R | leaf F1 | pair P | pair R | coverage | spurious / close | leaf F1 after upstream event | other closes |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for m_ in METHODS:
        v = defaultdict(list)
        for rep in (1, 2):
            ss = [r["methods"][m_] for r in R if r["rep"] == rep and sel(r)]
            for i, k in enumerate(("P", "R", "F")):
                xs = [s["levels"]["leaf"][i] for s in ss if "leaf" in s["levels"]]
                v[k].append(float(np.mean(xs)) if xs else None)
            p = np.sum([s["pairs"] for s in ss], axis=0)
            v["pP"].append(p[0] / (p[0] + p[1]) if p[0] + p[1] else None)
            v["pR"].append(p[0] / (p[0] + p[2]) if p[0] + p[2] else None)
            v["cov"].append(p[:4].sum() / p.sum() if p.sum() else None)
            v["sp"].append(float(np.mean([s["spur"] for s in ss])))
            up = [s["robust"]["up"] for s in ss if s["robust_n"]["up"]]
            ot = [s["robust"]["other"] for s in ss if s["robust_n"]["up"]]
            v["up"].append(float(np.nanmean(up)) if up else None)
            v["ot"].append(float(np.nanmean(ot)) if ot else None)
        print(f"| {m_} | " + " | ".join(" / ".join(f_(x) for x in v[k]) for k in ("P", "R", "F", "pP", "pR", "cov", "sp", "up", "ot")) + " |")
    print()


def _time_tables(R):
    cells = defaultdict(dict)
    for r in R:
        cells[r["cell"]][r["rep"]] = r
    order = sorted(cells, key=lambda c: (GROUP_BLOCKS.index(c.split("-")[0]), c))
    print("## Time to a leaf group with F1 >= 0.9 (FLAG): events of that leaf / seconds, median over leaves (never); late joiner\n")
    print("| method | leaf events p50 | seconds p50 | never / leaves | late joiner joined / cases | late: events p50 | late: seconds p50 |")
    print("|---|---|---|---|---|---|---|")
    for m_ in METHODS:
        v = defaultdict(list)
        for rep in (1, 2):
            ev, sec, nev, nl = [], [], 0, 0
            lj = []
            for r in R:
                if r["rep"] != rep:
                    continue
                s = r["methods"][m_]
                for n, info in r["truth"].items():
                    if info["level"] != "leaf":
                        continue
                    nl += 1
                    if n in s["t_ok"]:
                        ev.append(s["t_ok"][n][0])
                        sec.append(s["t_ok"][n][1])
                    else:
                        nev += 1
                lj += [x for x in r["late"] if x["method"] == m_]
            j = [x for x in lj if x["joined"]]
            v["ev"].append(f_(float(np.median(ev)), 0) if ev else "-")
            v["sec"].append(f_(float(np.median(sec)), 0) if sec else "-")
            v["nev"].append(f"{nev}/{nl}")
            v["lj"].append(f"{len(j)}/{len(lj)}" if lj else "-")
            v["le"].append(f_(float(np.median([x["events"] for x in j])), 0) if j else "-")
            v["ls"].append(f_(float(np.median([x["seconds"] for x in j])), 0) if j else "-")
        print(f"| {m_} | " + " | ".join(" / ".join(v[k]) for k in ("ev", "sec", "nev", "lj", "le", "ls")) + " |")
    print()
    print("## Side table: mid / up / root best-match F1, mean over closes (pooled per rep)\n")
    print("| method | mid | up | root |")
    print("|---|---|---|---|")
    for m_ in METHODS:
        cellsv = []
        for lv in ("mid", "up", "root"):
            xs = [[r["methods"][m_]["levels"][lv][2] for r in R if r["rep"] == rep and lv in r["methods"][m_]["levels"]] for rep in (1, 2)]
            cellsv.append(" / ".join(f_(float(np.mean(x))) if x else "-" for x in xs))
        print(f"| {m_} | " + " | ".join(cellsv) + " |")
    print()
    print("## Truth sets per cell (rep 1)\n")
    print("| cell | true sets (level, kind, size) |")
    print("|---|---|")
    for c in order:
        r = cells[c].get(1) or cells[c].get(2)
        print(f"| {c} | " + ", ".join(f"{n} ({v['level']}, {v['kind']}, {len(v['members'])})" for n, v in r["truth"].items()) + " |")
    print()


if __name__ == "__main__":
    if sys.argv[1] == "rows":
        kdir = Path(sys.argv[2])
        out = Path(sys.argv[3]) if len(sys.argv) > 3 else kdir / "grouping-scores.jsonl"
        with Pool(10) as pool, open(out, "w") as fh:
            for r in pool.imap_unordered(run_row, runs_of(kdir)):
                fh.write(json.dumps(r) + "\n")
                fh.flush()
        print(out)
    else:
        report(Path(sys.argv[2]))
