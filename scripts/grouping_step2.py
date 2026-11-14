#!/usr/bin/env python3
"""Part A (A1, A3) and Step 2 of the 2026-11-12 brief (read-only, development set,
single-queue AQMs, N1-N5 never opened).

    python3 scripts/grouping_step2.py a1       CAMPAIGN OUT/a1-rows.jsonl     # detector recall per event / time
    python3 scripts/grouping_step2.py a1-sum   OUT/a1-rows.jsonl.gz
    python3 scripts/grouping_step2.py a3       CAMPAIGN OUT/a3-rows.jsonl     # independent timing, clean members
    python3 scripts/grouping_step2.py a3-sum   OUT/a3-rows.jsonl.gz
    python3 scripts/grouping_step2.py step2    CAMPAIGN OUT/step2-rows.jsonl  # grouping inside one event
    python3 scripts/grouping_step2.py step2-sum OUT/step2-rows.jsonl.gz
    python3 scripts/grouping_step2.py plots    CAMPAIGN OUT/step2-rows.jsonl.gz OUT/

Constants (origin tag):
  BIN 5 ms (P: the OWD file's send-time grid); MARGIN 1 s (FLAG, as step 1);
  N_MIN 10 samples (FLAG); CONC_S 50 ms (FLAG, as step 1);
  MAX_ITER 10 (FLAG, brief); MAX_TEMPLATES 8 (FLAG: cap on data templates per event);
  MIN_MEMBERS 2 (T, brief); PENALTY_SCALES 0.5 / 1 / 2 (T, brief: sensitivity);
  OBS_SHARE 0.5 (FLAG: a participant is observable when >= half of the event's
  20 ms windows pass the adapter's sent-rate test, itself 50 % of the rendition over
  200 ms); NEG_SPAN (-1 s, +2 s) around an ECG event's t0 on negatives (FLAG);
  n_eff, f, G, penalty (M, per client / event).
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval as d  # noqa: E402
import grouping_adapter as ga  # noqa: E402
import grouping_template_study as ts  # noqa: E402
import gt1  # noqa: E402
import gt2  # noqa: E402
import gt_score  # noqa: E402
import shadow_v2_frozen  # noqa: E402

BIN, MARGIN, N_MIN, CONC_S = ts.BIN, 1.0, ts.N_MIN, ts.CONC_S
MAX_ITER, MAX_TEMPLATES, MIN_MEMBERS = 10, 8, 2
PENALTY_SCALES = (1.0, 0.5, 2.0, 0.0)   # 0: diagnostic only (accept any positive gain), not a proposal
OBS_SHARE = 0.5
NEG_SPAN = (-1.0, 2.0)
SINGLE_QUEUE = ("pfifo", "pie", "red", "codel")
CAMPAIGN_DIRS = "KMCJG"   # G only for the negatives


def runs_of(campaign: Path, groups: str) -> list[Path]:
    return [rd for g in sorted(campaign.iterdir()) if g.is_dir() and g.name[0] in groups and not g.name.startswith("N")
            for rd in sorted(g.glob("grp-*")) if rd.name.split("-")[-2] in SINGLE_QUEUE
            and (rd / "grouping" / "windows.json").exists()]


def read_jsonl(path: Path) -> list[dict]:
    return ts.read_jsonl(path)


def q3(v, f=".2f"):
    v = [x for x in v if x is not None and x == x]
    return " / ".join(format(x, f) for x in np.percentile(v, [10, 50, 90])) if v else "-"


# ═══ A1: detector recall per event and per congested time ═══════════════

def a1_row(rd: Path) -> list[dict]:
    run = ga.load_run(rd)
    windows = json.loads((rd / "grouping" / "windows.json").read_text())
    e1, l1 = gt1.run_truth(run, gt1.Params())
    e2, l2 = gt2.run_truth(run, gt2.Params())
    views = {"GT1": gt_score.client_view(run, [(e["hop"], e["start_s"], e["end_s"]) for e in e1], l1),
             "GT2": gt_score.client_view(run, [(e["queue_id"], e["t_on"], e["t_end"]) for e in e2], l2)}
    alarms = {s: [(a, b) for a, b, _ in v] for s, v in shadow_v2_frozen.episodes(run, "v2", mode="OWD", hold=True).items()}
    out = []
    for truth, view in views.items():
        for s, (eps, _) in view.items():
            al = [(a, b) for a, b in alarms.get(s, []) if a >= d.WARMUP_S]
            for a, b in eps:
                if a < d.WARMUP_S:
                    continue
                win = next((w for w in windows if s in w.get("expected", []) and w["start"] - 1 <= b and w["end"] + 2 >= a), None)
                lo, hi = a - d.PRE_ONSET_LEAD_S, min(b, a + d.SEARCH_S)
                covered = sum(max(0.0, min(b, y) - max(a, x)) for x, y in al)
                out.append({"truth": truth, "campaign": rd.parent.name, "type": rd.name.split("-")[1],
                            "aqm": rd.name.split("-")[-2], "client": s, "dur": b - a,
                            "u": (win or {}).get("u"), "scripted": win is not None,
                            "stimulus": (win or {}).get("stimulus_type"),
                            "det_start": any(lo <= x <= hi for x, _ in al),
                            "det_overlap": any(x <= b and y >= a for x, y in al),
                            "covered_s": covered})
    return out


def cmd_a1(campaign: Path, out: Path) -> None:
    with Pool(10) as pool, out.open("w") as fh:
        for rows in pool.imap_unordered(a1_row, runs_of(campaign, "KMCJ")):
            for r in rows:
                fh.write(json.dumps(r) + "\n")


def dur_bin(x):
    return "< 0.5 s" if x < 0.5 else "0.5-1 s" if x < 1 else "1-2 s" if x < 2 else ">= 2 s"


def cmd_a1_sum(path: Path) -> None:
    R = read_jsonl(path)
    print("# A1: detector recall (v2-owd) per event and per congested time\n")
    print("Unit: one (client, GT episode) in the client's link view (episodes of the egresses on its path, merged). "
          "Rules: *start* = an alarm starts in [t_on - 1 s, min(t_end, t_on + 10 s)] (the current figure); "
          "*overlap* = any alarm interval overlaps the episode; *time* = share of congested time covered by an alarm.\n")
    for truth in ("GT1", "GT2"):
        rs = [r for r in R if r["truth"] == truth]
        for title, key in (("all", lambda r: "all"), ("duration", lambda r: dur_bin(r["dur"])),
                           ("scripted or not", lambda r: "in a planned window" if r["scripted"] else "unscripted"),
                           ("severity u (planned capacity drops)", lambda r: f"u={r['u']}" if r["u"] else None),
                           ("scenario family", lambda r: f"{r['campaign']} {r['type']}")):
            by = defaultdict(list)
            for r in rs:
                k = key(r)
                if k is not None:
                    by[k].append(r)
            print(f"### {truth}: by {title}\n")
            print("| group | episodes | recall (start) | recall (overlap) | recall (time) | share of all episodes |\n|---|---|---|---|---|---|")
            for k in sorted(by, key=str):
                g = by[k]
                dur = sum(r["dur"] for r in g)
                print(f"| {k} | {len(g)} | {np.mean([r['det_start'] for r in g]):.2f} | {np.mean([r['det_overlap'] for r in g]):.2f} "
                      f"| {sum(r['covered_s'] for r in g) / dur if dur else float('nan'):.2f} | {len(g) / len(rs):.2f} |")
            print()


# ═══ shared: delay curves of one interval ═══════════════════════════════

def curves(run, series: dict, lo: float, hi: float) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    grid = np.arange(lo, hi, BIN)
    qs = {}
    for s, (t, v) in series.items():
        before = v[(t < lo) & (t >= 0)]
        if np.any(~np.isnan(before)):
            qs[s] = ts.on_grid(t, v, grid) - np.nanmin(before)
    return grid, qs


def f_fit(q: np.ndarray, s: np.ndarray | None) -> tuple[float, np.ndarray] | None:
    """RMS of the centred residual q - s (s None: the class-0 all-zero template)."""
    if s is None:
        ok = ~np.isnan(q)
        r = q[ok]
    else:
        ok = ~np.isnan(q) & ~np.isnan(s)
        r = q[ok] - s[ok]
    if len(r) < N_MIN:
        return None
    r = r - np.median(r)
    return float(np.sqrt(np.mean(r ** 2))), r


# ═══ A3: independent timing, wrong-group preference, clean members ═════

def a3_rows(rd: Path) -> list[dict]:
    run = d.Run(rd)
    windows = [w for w in json.loads((rd / "grouping" / "windows.json").read_text()) if len(w.get("expected", [])) >= 2]
    series = {s: ts.owd_series(run, s)["min"] for s in run.subs if run.sender_file(s, "owd").exists()}
    out = []
    for wi, w in enumerate(windows):
        lo, hi = w["start"] - MARGIN, w["end"] + MARGIN
        grid, qs = curves(run, series, lo, hi)
        exp = set(w["expected"])
        others = [u for u in windows if u is not w and u["start"] <= hi and u["end"] >= lo and set(u["expected"]) != exp]
        busy = {c for u in others for c in u["expected"]}
        clean = sorted(exp - busy)
        for i in sorted(exp & set(qs)):
            own, _ = ts.template(qs, exp - {i})
            row = {"run": rd.name, "type": rd.name.split("-")[1], "aqm": rd.name.split("-")[-2], "w": wi,
                   "target": w.get("target"), "client": i, "overlapped": bool(others), "i_busy": i in busy}
            if own is None:
                continue
            lf = ts.l_flat(qs[i], own)
            row["L_flat"] = lf["L_flat"] if lf else None
            wrong = []
            for u in others:
                if i in u["expected"]:
                    continue
                oth, _ = ts.template(qs, set(u["expected"]))
                sc = ts.l_score(qs[i], own, oth) if oth is not None else None
                if sc:
                    wrong.append(sc["L"])
            row["n_wrong"] = len(wrong)
            row["prefers_wrong"] = any(x < 0 for x in wrong) if wrong else None
            cm = [c for c in clean if c != i and c in qs]
            if not cm:
                row["clean"] = "unusable"
            else:
                cs, _ = ts.template(qs, set(cm))
                lc = ts.l_flat(qs[i], cs) if cs is not None else None
                row["clean"] = "ok" if lc else "unusable"
                row["L_flat_clean"] = lc["L_flat"] if lc else None
                cw = []
                for u in others:
                    if i in u["expected"]:
                        continue
                    um = [c for c in u["expected"] if c not in exp and not any(c in v["expected"] for v in others if v is not u)]
                    oth, _ = ts.template(qs, set(um)) if um else (None, 0)
                    sc = ts.l_score(qs[i], cs, oth) if oth is not None and cs is not None else None
                    if sc:
                        cw.append(sc["L"])
                row["prefers_wrong_clean"] = any(x < 0 for x in cw) if cw else None
            out.append(row)
    return out


def cmd_a3(campaign: Path, out: Path) -> None:
    runs = [rd for rd in runs_of(campaign, "M") if rd.name.split("-")[1] in ("indepfast", "indepslow")]
    with Pool(8) as pool, out.open("w") as fh:
        for rows in pool.imap_unordered(a3_rows, runs):
            for r in rows:
                fh.write(json.dumps(r) + "\n")


def cmd_a3_sum(path: Path) -> None:
    R = read_jsonl(path)
    print("# A3: independent-timing runs (M6 indepfast / indepslow, single-queue AQMs)\n")
    print("| set | SAME rows | L_flat p10 / p50 / p90 | > 11.5 | < 2 | rows with a wrong-group template | prefers a wrong group |")
    print("|---|---|---|---|---|---|---|")
    for lab, rs in (("all", R), ("event overlapped by another group's window", [r for r in R if r["overlapped"]]),
                    ("not overlapped", [r for r in R if not r["overlapped"]]),
                    ("indepfast", [r for r in R if r["type"] == "indepfast"]), ("indepslow", [r for r in R if r["type"] == "indepslow"])):
        v = np.array([r["L_flat"] for r in rs if r.get("L_flat") is not None])
        pw = [r["prefers_wrong"] for r in rs if r.get("prefers_wrong") is not None]
        print(f"| {lab} | {len(v)} | {q3(v, '.1f')} | {np.mean(v > ts.REF):.2f} | {np.mean(v < 2):.2f} | {len(pw)} "
              f"| {np.mean(pw) if pw else float('nan'):.2f} |")
    print("\n## Clean-member templates (members with no other group's window overlapping the event)\n")
    print("| set | rows | unusable (no clean member) | L_flat clean p10 / p50 / p90 | > 11.5 | < 2 | prefers a wrong group (clean templates) |")
    print("|---|---|---|---|---|---|---|")
    for lab, rs in (("all", R), ("overlapped", [r for r in R if r["overlapped"]])):
        ok = [r for r in rs if r.get("clean") == "ok"]
        v = np.array([r["L_flat_clean"] for r in ok if r.get("L_flat_clean") is not None])
        pw = [r["prefers_wrong_clean"] for r in ok if r.get("prefers_wrong_clean") is not None]
        print(f"| {lab} | {len(rs)} | {np.mean([r.get('clean') == 'unusable' for r in rs]):.2f} | {q3(v, '.1f')} "
              f"| {np.mean(v > ts.REF) if len(v) else float('nan'):.2f} | {np.mean(v < 2) if len(v) else float('nan'):.2f} "
              f"| {np.mean(pw) if pw else float('nan'):.2f} (n {len(pw)}) |")


# ═══ Step 2: grouping inside one event without labels ══════════════════

class Partition:
    def __init__(self, qs: dict[str, np.ndarray]):
        self.qs = qs
        self.comparisons = 0
        self.f0 = {}
        for s, q in qs.items():
            r = f_fit(q, None)
            self.comparisons += 1
            self.f0[s] = r[0] if r else None

    def fit(self, i: str, members: list[str]) -> float | None:
        """f(i, median of members), leave-one-out when i is a member."""
        m = [x for x in members if x != i]
        if not m:
            return None
        s, _ = ts.template(self.qs, set(m))
        if s is None:
            return None
        self.comparisons += 1
        r = f_fit(self.qs[i], s)
        return r[0] if r else None

    def assign(self, classes: list[list[str]], parts: list[str]) -> tuple[list[list[str]], int]:
        """Step 3: reassign to the best class (0 = flat), recompute medians, until stable."""
        for it in range(1, MAX_ITER + 1):
            new = [[] for _ in classes]
            zero = []
            for i in parts:
                best, bk = self.f0[i], -1
                for k, mem in enumerate(classes):
                    fk = self.fit(i, mem)   # leave-one-out when i is a member
                    if fk is not None and (best is None or fk < best):
                        best, bk = fk, k
                (zero if bk < 0 else new[bk]).append(i)
            new = [sorted(m) for m in new if len(m) >= MIN_MEMBERS]
            if sorted(map(tuple, new)) == sorted(map(tuple, classes)):
                return new, it
            classes = new
        return classes, MAX_ITER

    def cost(self, i: str, classes: list[list[str]]) -> tuple[float | None, int]:
        k = next((k for k, m in enumerate(classes) if i in m), -1)
        return (self.f0[i] if k < 0 else self.fit(i, classes[k])), k

    def residual(self, i: str, classes: list[list[str]]) -> np.ndarray | None:
        k = next((k for k, m in enumerate(classes) if i in m), -1)
        if k < 0:
            r = f_fit(self.qs[i], None)
        else:
            s, _ = ts.template(self.qs, set(classes[k]) - {i})
            r = f_fit(self.qs[i], s) if s is not None else None
        return r[1] if r else None


def split_attempt(P: "Partition", qs: dict, parts: list[str], classes: list[list[str]]):
    """Step 4 + the gain of step 5: seed a template with the worst-fitting participant
    and its nearest participant, reassign (step 3), return (trial classes, G, iterations)."""
    before = {i: P.cost(i, classes)[0] for i in parts}
    if not parts:
        return None
    seed = max(parts, key=lambda i: (before[i] or 0.0, i))
    others = [j for j in parts if j != seed]
    if not others:
        return None
    fj = {j: (lambda r: r[0] if r else None)(f_fit(qs[j], qs[seed])) for j in others}
    P.comparisons += len(others)
    cand = [j for j in others if fj[j] is not None]
    if not cand:
        return None
    near = min(cand, key=lambda j: (fj[j], j))
    trial = [[m for m in c if m not in (seed, near)] for c in classes] + [[seed, near]]
    trial = [c for c in trial if len(c) >= MIN_MEMBERS or c == [seed, near]]
    trial, it = P.assign(trial, parts)
    after = {i: P.cost(i, trial)[0] for i in parts}
    G = 0.0
    for i in parts:
        if before[i] and after[i]:
            r = P.residual(i, classes)
            ne = ts.n_eff(r) if r is not None and len(r) >= 3 else 1.0
            G += ne * math.log(before[i] / after[i])
    return trial, G, it


def base_partition(qs: dict) -> tuple["Partition", list[str], list[list[str]], list[int]]:
    """Steps 1-3: class 0 plus at most one data template."""
    P = Partition(qs)
    parts = sorted(s for s in qs if P.f0[s] is not None)
    first = [i for i in parts if (lambda f: f is not None and f < P.f0[i])(P.fit(i, parts))]
    classes, iters = ([first] if len(first) >= MIN_MEMBERS else []), []
    if classes:
        classes, it = P.assign(classes, parts)
        iters.append(it)
    return P, parts, classes, iters


def surrogate_gains(qs: dict, parts: list[str], classes: list[list[str]], n: int, rng) -> list[float]:
    """Null "one group": the data class keeps its template; each member's centred
    leave-one-out residual is given to another member (random derangement); the split
    step is run on each surrogate and its gain recorded."""
    if len(classes) != 1 or len(classes[0]) < 2:
        return []
    mem = classes[0]
    tmpl, _ = ts.template(qs, set(mem))
    res = {}
    for i in mem:
        loo, _ = ts.template(qs, set(mem) - {i})
        r = qs[i] - loo
        res[i] = r - np.nanmedian(r)
    out = []
    for _ in range(n):
        perm = list(mem)
        while len(mem) > 1 and any(a == b for a, b in zip(perm, mem)):
            rng.shuffle(perm)
        q2 = dict(qs)
        for i, j in zip(mem, perm):
            q2[i] = tmpl + res[j]
        P2 = Partition(q2)
        sp = split_attempt(P2, q2, parts, [list(mem)])
        out.append(sp[1] if sp else 0.0)
    return out


def partition_event(qs: dict[str, np.ndarray], scale: float) -> dict:
    P = Partition(qs)
    parts = sorted(s for s in qs if P.f0[s] is not None)
    n_tot = int(sum(np.sum(~np.isnan(qs[s])) for s in parts))
    attempts = []
    iters = []
    # step 2: initial data template from the participants that fit it better than class 0
    first = [i for i in parts if (lambda f: f is not None and f < P.f0[i])(P.fit(i, parts))]
    classes = [first] if len(first) >= MIN_MEMBERS else []
    if classes:
        classes, it = P.assign(classes, parts)
        iters.append(it)
    while len(classes) < MAX_TEMPLATES:
        sp = split_attempt(P, qs, parts, classes)
        if sp is None:
            break
        trial, G, it = sp
        new_members = [m for c in trial if c not in classes for m in c]   # empty: the new class dissolved (p = 1)
        ne_new = [ts.n_eff(P.residual(i, trial)) for i in new_members if P.residual(i, trial) is not None]
        p = statistics.median(ne_new) if ne_new else 1.0
        pen = scale * (p / 2) * math.log(max(n_tot, 2))
        acc = G > pen and len(trial) > len(classes)
        attempts.append({"G": G, "penalty": pen, "accepted": acc, "n_classes_before": len(classes)})
        if not acc:
            break
        classes = trial
        iters.append(it)
    zero = sorted(set(parts) - {m for c in classes for m in c})
    peaks = []
    for c in classes:
        tm, _ = ts.template(qs, set(c))
        peaks.append(float(np.nanmax(tm)) if tm is not None and np.any(~np.isnan(tm)) else None)
    return {"classes": classes, "zero": zero, "participants": parts, "attempts": attempts,
            "iterations": iters, "comparisons": P.comparisons, "peaks_ms": peaks}


def truth_partition(windows: list[dict], lo: float, hi: float, parts: list[str]) -> dict[str, frozenset]:
    ov = [w for w in windows if w["start"] <= hi and w["end"] >= lo and w.get("expected")]
    return {s: frozenset(w.get("hop") or w.get("target") for w in ov if s in w["expected"]) for s in parts}


def score_partition(res: dict, tp: dict[str, frozenset]) -> dict:
    lab = {s: k for k, c in enumerate(res["classes"]) for s in c}
    parts = res["participants"]
    pairs = [(a, b) for i, a in enumerate(parts) for b in parts[i + 1:]]
    t_same = {(a, b): bool(tp[a]) and tp[a] == tp[b] for a, b in pairs}
    p_same = {(a, b): a in lab and b in lab and lab[a] == lab[b] for a, b in pairs}
    tp_n = sum(t_same[x] and p_same[x] for x in pairs)
    groups = defaultdict(set)
    for s in parts:
        if tp[s]:
            groups[tp[s]].add(s)
    over = any(len({lab.get(s, -1) for s in g}) > 1 for g in groups.values())
    under = any(len({tp[s] for s in c}) > 1 for c in res["classes"])
    truth_sets = sorted(map(sorted, groups.values()))
    exact = sorted(map(sorted, res["classes"])) == truth_sets
    quiet = [s for s in parts if not tp[s]]
    cong = [s for s in parts if tp[s]]
    return {"exact": exact, "over": over, "under": under, "tp": tp_n, "fp": sum(p_same[x] and not t_same[x] for x in pairs),
            "fn": sum(t_same[x] and not p_same[x] for x in pairs), "n_truth_groups": len(groups),
            "group_sizes": sorted(len(g) for g in groups.values()),
            "quiet_in_0": sum(s in res["zero"] for s in quiet), "quiet": len(quiet),
            "cong_in_0": sum(s in res["zero"] for s in cong), "cong": len(cong),
            "multi_hop_clients": sum(len(tp[s]) > 1 for s in parts)}


def event_class(group: str, typ: str, cells: set[str], n_groups: int, nested: bool) -> str:
    """From the truth partition of the event (and the planned cells for naming)."""
    if group == "J1":
        return f"J1 {typ}"
    if nested:
        if typ.startswith("indep"):
            return "overlapping (independent timing)"
        return "nested (K1 a+up, K6 levels)" if group in ("K1", "K6") else "nested (other)"
    if n_groups >= 2:
        if cells & {"a+b", "A+C"}:
            return "concurrent (K1 a+b, K6 A+C)"
        if typ.startswith("indep"):
            return "overlapping (independent timing)"
        return "two groups, shifted or overlapping windows"
    if n_groups == 1:
        return "single group"
    return "no congested client in the truth"


def events_of(rd: Path, ecg_intervals: bool = False):
    """(row metadata, curves of the observable participants, truth partition) per event.
    ecg_intervals: event intervals from the ECG events (as G0) for every run (step 4 f)."""
    run = ga.load_run(rd)
    group, typ, aqm = rd.parent.name, rd.name.split("-")[1], rd.name.split("-")[-2]
    windows = json.loads((rd / "grouping" / "windows.json").read_text())
    series = {s: ts.owd_series(run, s)["min"] for s in run.subs if run.sender_file(s, "owd").exists()}
    rate = {s: run.topology["subscribers"].get(run.sid_of.get(s, s) if hasattr(run, "sid_of") else s, {}).get("rate_kbps")
            for s in run.subs}
    obs = {}
    for s in series:
        try:
            obs[s] = ga.sent_rate_obs(run, s, (rate.get(s) or 1000) * 1000, 0.5, run.duration)
        except Exception:   # noqa: BLE001 - no sent file: not observable
            obs[s] = None
    if group == "G0" or ecg_intervals:
        m = json.loads((rd / "grouping-d150-v2-owd" / "metrics.json").read_text()) \
            if (rd / "grouping-d150-v2-owd" / "metrics.json").exists() else {"events": []}
        events = [(e["t0"] + NEG_SPAN[0], e["t0"] + NEG_SPAN[1], {"ecg"}, len(e["members"])) for e in m["events"]]
    else:
        shared = sorted((w for w in windows if len(w.get("expected", [])) >= 2), key=lambda w: w["start"])
        events, used = [], set()
        for k, w in enumerate(shared):
            if k in used:
                continue
            same = [j for j, u in enumerate(shared) if j not in used and abs(u["start"] - w["start"]) <= CONC_S]
            used.update(same)
            ws = [shared[j] for j in same]
            events.append((min(u["start"] for u in ws) - MARGIN, max(u["end"] for u in ws) + MARGIN,
                           {u.get("cell") for u in ws}, None))
    for ei, (lo, hi, cells, n_ecg) in enumerate(events):
        grid, qs = curves(run, series, lo, hi)
        i0, i1 = int(max(lo, 0) / ga.OBS_WINDOW), int(hi / ga.OBS_WINDOW)
        qs = {s: q for s, q in qs.items()
              if obs.get(s) is not None and len(obs[s][i0:i1]) and np.mean(obs[s][i0:i1]) >= OBS_SHARE}
        if len(qs) < 2:
            continue
        tp = truth_partition([] if group == "G0" else windows, lo + MARGIN, hi - MARGIN, sorted(qs))
        nested = any(len(v) > 1 for v in tp.values())
        n_groups = len({v for v in tp.values() if v})
        ecls = "negative" if group == "G0" else event_class(group, typ, cells, n_groups, nested)
        row = {"campaign": group, "run": rd.name, "type": typ, "aqm": aqm, "event": ei, "lo": lo, "hi": hi,
               "cells": sorted(c for c in cells if c), "class": ecls, "n_ecg_members": n_ecg,
               "low_bitrate": any((rate.get(s) or 0) <= 1000 and tp[s] for s in qs),
               "rates": {s: rate.get(s) for s in qs}, "truth": {s: sorted(v) for s, v in tp.items()}}
        yield row, qs, tp


def step2_run(rd: Path) -> list[dict]:
    out = []
    for row, qs, tp in events_of(rd):
        for scale in PENALTY_SCALES:
            res = partition_event(qs, scale)
            row[f"x{scale:g}"] = {**{k: res[k] for k in ("classes", "zero", "attempts", "iterations", "comparisons", "peaks_ms")},
                                  **score_partition(res, tp)}
        out.append(row)
    return out


# ═══ Step 2b A: surrogate-calibrated split test ═════════════════════════

N_SURR = 200          # FLAG (brief); 100 / 500 on a subset
ALPHA = 0.01          # T (brief)


def step2b_run(args) -> list[dict]:
    rd, n_list = args
    out = []
    for row, qs, tp in events_of(rd):
        if row["class"] == "negative":
            continue
        P, parts, classes, _ = base_partition(qs)
        sp = split_attempt(P, qs, parts, classes) if classes else None
        g_obs = sp[1] if sp else None
        rng = np.random.default_rng([zlib_crc(rd.name), row["event"]])
        nmax = max(n_list)
        gs = surrogate_gains(qs, parts, classes, nmax, rng) if sp else []
        res = {}
        for n in n_list:
            g = gs[:n]
            if not g or g_obs is None:
                res[n] = {"p": None, "accept": False}
                continue
            p = (1 + sum(x >= g_obs for x in g)) / (1 + len(g))
            res[n] = {"p": p, "accept": bool(g_obs > np.quantile(g, 1 - ALPHA))}
        chosen = sp[0] if sp and res[n_list[0]]["accept"] else classes
        part = {"classes": chosen, "zero": sorted(set(parts) - {m for c in chosen for m in c}), "participants": parts}
        row["surr"] = {"G_obs": g_obs, "G_star_q99": float(np.quantile(gs, 0.99)) if gs else None,
                       "by_n": {str(n): v for n, v in res.items()}, **score_partition(part, tp)}
        row["n_truth_groups"] = len({v for v in tp.values() if v})
        out.append(row)
    return out


def zlib_crc(s: str) -> int:
    import zlib
    return zlib.crc32(s.encode())


def cmd_step2b(campaign: Path, out: Path, subset_every: int = 10) -> None:
    runs = runs_of(campaign, "KMCJ")
    args = [(rd, (N_SURR, 100, 500) if k % subset_every == 0 else (N_SURR,)) for k, rd in enumerate(runs)]
    with Pool(10) as pool, out.open("w") as fh:
        for rows in pool.imap_unordered(step2b_run, args):
            for r in rows:
                fh.write(json.dumps(r) + "\n")


def roc_auc(pos: list[float], neg: list[float]) -> float | None:
    """P(score of a two-group event > score of a one-group event); ties count half."""
    if not pos or not neg:
        return None
    x = np.array(pos + neg)
    import pandas as pd
    r = pd.Series(x).rank().values
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def cmd_step2b_sum(path: Path) -> None:
    R = read_jsonl(path)
    print("# Step 2b A: surrogate-calibrated split test\n")
    print(f"{len(R)} events with windows, single-queue AQMs. Null: the event's single data class keeps its template; "
          f"members' centred leave-one-out residuals are permuted among them (derangement); the split step runs on each "
          f"surrogate. Accept the extra template when the observed G exceeds the {1 - ALPHA:.2f} quantile of G* "
          f"({N_SURR} surrogates; only the first extra template is tested).\n")
    by = defaultdict(list)
    for r in R:
        by[r["class"]].append(r)
    print("| event class | events | exact | pair P | pair R | over-split | under-split | one-group events split | "
          "two-group events split | congested in class 0 |\n|---|---|---|---|---|---|---|---|---|---|")
    for k in sorted(by) + ["all"]:
        rs = R if k == "all" else by[k]
        x = [r["surr"] for r in rs]
        tp, fp, fn = (sum(v[c] for v in x) for c in ("tp", "fp", "fn"))
        one = [r for r in rs if r["n_truth_groups"] == 1]
        two = [r for r in rs if r["n_truth_groups"] >= 2]
        sp1 = [len(r["surr"]["classes"]) >= 2 if "classes" in r["surr"] else r["surr"]["by_n"][str(N_SURR)]["accept"] for r in one]
        sp2 = [r["surr"]["by_n"][str(N_SURR)]["accept"] for r in two]
        c, cz = sum(v["cong"] for v in x), sum(v["cong_in_0"] for v in x)
        print(f"| {k} | {len(rs)} | {np.mean([v['exact'] for v in x]):.2f} | {tp / (tp + fp) if tp + fp else float('nan'):.2f} "
              f"| {tp / (tp + fn) if tp + fn else float('nan'):.2f} | {sum(v['over'] for v in x)} | {sum(v['under'] for v in x)} "
              f"| {np.mean(sp1) if sp1 else float('nan'):.2f} (n {len(sp1)}) | {np.mean(sp2) if sp2 else float('nan'):.2f} (n {len(sp2)}) "
              f"| {cz / c if c else float('nan'):.2f} |")
    one = [r for r in R if r["n_truth_groups"] == 1 and r["surr"]["G_obs"] is not None]
    two = [r for r in R if r["n_truth_groups"] >= 2 and r["surr"]["G_obs"] is not None]
    a_g = roc_auc([r["surr"]["G_obs"] for r in two], [r["surr"]["G_obs"] for r in one])
    pv = lambda r: r["surr"]["by_n"][str(N_SURR)]["p"]
    a_p = roc_auc([-pv(r) for r in two if pv(r) is not None], [-pv(r) for r in one if pv(r) is not None])
    print(f"\nROC area, two-group vs one-group events (events with a split attempt: {len(two)} / {len(one)}): "
          f"raw G {a_g:.3f}, surrogate p-value {a_p:.3f}.\n")
    print("By class (two-group events of that class vs all one-group events):\n")
    print("| class | two-group events | AUC raw G | AUC p-value |\n|---|---|---|---|")
    for k in sorted(by):
        t = [r for r in by[k] if r["n_truth_groups"] >= 2 and r["surr"]["G_obs"] is not None]
        if t:
            print(f"| {k} | {len(t)} | {roc_auc([r['surr']['G_obs'] for r in t], [r['surr']['G_obs'] for r in one]):.3f} "
                  f"| {roc_auc([-pv(r) for r in t if pv(r) is not None], [-pv(r) for r in one if pv(r) is not None]):.3f} |")
    sub = [r for r in R if "100" in r["surr"]["by_n"]]
    print(f"\nSurrogate count on a subset ({len(sub)} events, every 10th run):\n")
    print("| surrogates | one-group events split | two-group events split | decision changes vs 200 |\n|---|---|---|---|")
    for n in ("100", "200", "500"):
        o = [r["surr"]["by_n"][n]["accept"] for r in sub if r["n_truth_groups"] == 1]
        t = [r["surr"]["by_n"][n]["accept"] for r in sub if r["n_truth_groups"] >= 2]
        ch = sum(r["surr"]["by_n"][n]["accept"] != r["surr"]["by_n"]["200"]["accept"] for r in sub)
        print(f"| {n} | {np.mean(o) if o else float('nan'):.2f} | {np.mean(t) if t else float('nan'):.2f} | {ch} |")


def cmd_step2(campaign: Path, out: Path) -> None:
    with Pool(10) as pool, out.open("w") as fh:
        for rows in pool.imap_unordered(step2_run, runs_of(campaign, CAMPAIGN_DIRS)):
            for r in rows:
                fh.write(json.dumps(r) + "\n")


def cmd_step2_sum(path: Path) -> None:
    R = read_jsonl(path)
    pos = [r for r in R if r["class"] != "negative"]
    neg = [r for r in R if r["class"] == "negative"]

    def block(rows, key, title, scale="x1"):
        by = defaultdict(list)
        for r in rows:
            k = key(r)
            if k is not None:
                by[k].append(r)
        print(f"### {title}\n")
        print("| group | events | exact | pair P | pair R | over-split | under-split | quiet in class 0 | congested in class 0 |")
        print("|---|---|---|---|---|---|---|---|---|")
        for k in sorted(by, key=str):
            rs = [r[scale] for r in by[k]]
            tp, fp, fn = (sum(x[c] for x in rs) for c in ("tp", "fp", "fn"))
            q, qz = sum(x["quiet"] for x in rs), sum(x["quiet_in_0"] for x in rs)
            c, cz = sum(x["cong"] for x in rs), sum(x["cong_in_0"] for x in rs)
            print(f"| {k} | {len(rs)} | {np.mean([x['exact'] for x in rs]):.2f} | {tp / (tp + fp) if tp + fp else float('nan'):.2f} "
                  f"| {tp / (tp + fn) if tp + fn else float('nan'):.2f} | {sum(x['over'] for x in rs)} | {sum(x['under'] for x in rs)} "
                  f"| {qz / q if q else float('nan'):.2f} | {cz / c if c else float('nan'):.2f} |")
        print()

    print("# Step 2: grouping inside one event without labels\n")
    print(f"{len({r['run'] for r in R})} runs, {len(pos)} events with windows, {len(neg)} negative events (G0, ECG event intervals).\n")
    block(pos, lambda r: "all", "All events (penalty x1)")
    block(pos, lambda r: r["class"], "By event class (penalty x1)")
    block(pos, lambda r: ("group sizes " + ("2" if r["x1"]["group_sizes"] and min(r["x1"]["group_sizes"]) == 2 else "3+"))
          if r["class"] == "single group" else None, "Single group: group size 2 vs 3+")
    print("### Congested clients placed in class 0, by client bitrate (penalty x1)\n")
    print("| bitrate kb/s | congested (event, client) | in class 0 |\n|---|---|---|")
    byr = defaultdict(lambda: [0, 0])
    for r in pos:
        for s_, v in r["truth"].items():
            if v:
                byr[r["rates"].get(s_)][0] += 1
                byr[r["rates"].get(s_)][1] += s_ in r["x1"]["zero"]
    for k in sorted(byr, key=lambda x: x or 0):
        print(f"| {k} | {byr[k][0]} | {byr[k][1] / byr[k][0]:.2f} |")
    print()
    block(pos, lambda r: r["aqm"], "By AQM")
    print("### Penalty sensitivity (all events with windows)\n")
    print("| penalty | exact | over-split | under-split | negatives: events with a data template | negatives: clients outside class 0 |")
    print("|---|---|---|---|---|---|")
    for sc in ("x1", "x0.5", "x2", "x0"):
        print(f"| {sc} | {np.mean([r[sc]['exact'] for r in pos]):.2f} | {sum(r[sc]['over'] for r in pos)} | "
              f"{sum(r[sc]['under'] for r in pos)} | {sum(bool(r[sc]['classes']) for r in neg)} / {len(neg)} | "
              f"{sum(sum(len(c) for c in r[sc]['classes']) for r in neg)} |")
    print("\n(x0 = accept any positive gain: a diagnostic upper bound of the split step, not a proposal.)\n")
    block(pos, lambda r: r["class"], "By event class, penalty x0 (diagnostic)", "x0")
    print("### G of the first extra-template attempt (penalty x1)\n")
    print("First attempt = the second data template (the first comes from step 2's initial median).\n")
    print("| truth | events | G p10 / p50 / p90 | penalty p50 | accepted |\n|---|---|---|---|---|")
    for lab, rs in (("one group", [r for r in pos if r["x1"]["n_truth_groups"] == 1]),
                    ("two groups", [r for r in pos if r["x1"]["n_truth_groups"] == 2]),
                    ("negatives", neg)):
        a = [r["x1"]["attempts"][0] for r in rs if r["x1"]["attempts"]]
        print(f"| {lab} | {len(a)} | {q3([x['G'] for x in a], '.1f')} | {np.median([x['penalty'] for x in a]) if a else float('nan'):.1f} "
              f"| {np.mean([x['accepted'] for x in a]) if a else float('nan'):.2f} |")
    print("\n### Nested events: what the procedure outputs\n")
    nest = [r for r in pos if r["x1"]["multi_hop_clients"] > 0]
    out = Counter()
    for r in nest:
        x = r["x1"]
        multi = [s for s, v in r["truth"].items() if len(v) > 1]
        lab = {s: k for k, c in enumerate(x["classes"]) for s in c}
        single = [s for s, v in r["truth"].items() if len(v) == 1]
        same_as_single = all(any(lab.get(m) is not None and lab.get(m) == lab.get(o) for o in single) for m in multi)
        out["two-hop clients share a class with one-hop clients" if same_as_single else "two-hop clients form their own class"] += 1
    for k, v in out.items():
        print(f"- {k}: {v} events")
    print(f"\n### Negatives (G0, single-queue)\n")
    for sc in ("x1",):
        n_data = sum(bool(r[sc]["classes"]) for r in neg)
        outside = sum(sum(len(c) for c in r[sc]["classes"]) for r in neg)
        print(f"{len(neg)} ECG event intervals; {n_data} got at least one data template; {outside} client placements "
              f"outside class 0 in total. By type:\n")
        by = defaultdict(list)
        for r in neg:
            by[r["type"]].append(r)
        print("| type | events | events with a data template | clients outside class 0 | ECG events with >= 2 members | data template peak ms p10 / p50 / p90 |\n|---|---|---|---|---|---|")
        for k in sorted(by):
            rs = by[k]
            print(f"| {k} | {len(rs)} | {sum(bool(r[sc]['classes']) for r in rs)} | {sum(sum(len(c) for c in r[sc]['classes']) for r in rs)} "
                  f"| {sum((r['n_ecg_members'] or 0) >= 2 for r in rs)} | {q3([p for r in rs for p in r[sc]['peaks_ms'] if p is not None], '.1f')} |")
        pk = [p for r in pos if r["class"] == "single group" for p in r["x1"]["peaks_ms"] if p is not None]
        print(f"\nFor comparison, single-group events with windows: data template peak ms p10 / p50 / p90 {q3(pk, '.1f')}.")
    print("\n### Cost\n")
    it = [i for r in R for i in r["x1"]["iterations"]]
    print(f"- iterations per assignment pass: {dict(sorted(Counter(it).items()))} (cap {MAX_ITER})")
    print(f"- template comparisons per event p10 / p50 / p90: {q3([r['x1']['comparisons'] for r in R], '.0f')}; "
          f"participants per event p50: {np.median([len(r['truth']) for r in R]):.0f}")


def cmd_plots(campaign: Path, path: Path, out_dir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    R = read_jsonl(path)
    picks = []
    for cls in ("single group", "concurrent (K1 a+b, K6 A+C)", "nested (K1 a+up, K6 levels)",
                "overlapping (independent timing)", "negative"):
        rs = [r for r in R if r["class"] == cls and r["aqm"] == "pfifo"]
        if cls == "negative":
            rs = [r for r in rs if r["x1"]["classes"]] or rs
        if rs:
            picks.append((cls, rs[len(rs) // 2]))
    for n, (cls, r) in enumerate(picks, 1):
        rd = campaign / r["campaign"] / r["run"]
        run = ga.load_run(rd)
        series = {s: ts.owd_series(run, s)["min"] for s in r["truth"]}
        grid, qs = curves(run, series, r["lo"], r["hi"])
        lab = {s: k + 1 for k, c in enumerate(r["x1"]["classes"]) for s in c}
        fig, ax = plt.subplots(figsize=(8, 3.4))
        for s, q in sorted(qs.items()):
            k = lab.get(s, 0)
            ax.plot(grid, q, ".", ms=2, color="0.6" if k == 0 else f"C{k - 1}",
                    label=f"{s}: class {k} (truth {','.join(r['truth'][s]) or 'quiet'})")
        x = r["x1"]
        ax.set_title(f"{cls}: {r['run']} [{r['lo']:.1f}, {r['hi']:.1f}] s; exact={x['exact']}, "
                     f"attempts G/pen " + ", ".join(f"{a['G']:.0f}/{a['penalty']:.0f}" for a in x["attempts"]), fontsize=7)
        ax.set_xlabel("run time s")
        ax.set_ylabel("queuing delay ms")
        ax.legend(fontsize=6, ncol=2)
        fig.tight_layout()
        f = out_dir / f"step2-example{n}.png"
        fig.savefig(f, dpi=120)
        plt.close(fig)
        print(f)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("a1", "a1-sum", "a3", "a3-sum", "step2", "step2-sum", "plots", "step2b", "step2b-sum",
                                    "neg", "neg-sum", "calm", "calm-sum", "d-items"))
    ap.add_argument("paths", nargs="+", type=Path)
    a = ap.parse_args(argv)
    {"a1": lambda: cmd_a1(*a.paths[:2]), "a1-sum": lambda: cmd_a1_sum(a.paths[0]),
     "a3": lambda: cmd_a3(*a.paths[:2]), "a3-sum": lambda: cmd_a3_sum(a.paths[0]),
     "step2": lambda: cmd_step2(*a.paths[:2]), "step2-sum": lambda: cmd_step2_sum(a.paths[0]),
     "plots": lambda: cmd_plots(*a.paths[:3]),
     "step2b": lambda: cmd_step2b(*a.paths[:2]), "step2b-sum": lambda: cmd_step2b_sum(a.paths[0]),
     "neg": lambda: cmd_neg(*a.paths[:2]), "neg-sum": lambda: cmd_neg_sum(a.paths[0]),
     "calm": lambda: cmd_calm(*a.paths[:2]), "calm-sum": lambda: cmd_calm_sum(a.paths[0]),
     "d-items": lambda: cmd_d_items(*a.paths[:3])}[a.cmd]()



# ═══ Step 2b B: negatives against a topology-based truth ════════════════

Q_TARGET_MS = 5.0      # T: a queue "formed" at GT1's CoDel target (gt1.TARGET_MS)


def egress_delay(run) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Router egress "from->to" -> (t, queue delay ms) from router-metrics (5 ms CSV if present)."""
    caps = d.capacity_series(run)
    out = {}
    for hop, csv in gt1.router_egresses(run):
        fine = csv.with_name(csv.stem + "-queue.csv")
        t, backlog, _, _ = gt1.load_samples(run, fine if fine.exists() else csv)
        cap = np.array([d.value_at(caps[hop], x) for x in t]) * 1e6
        out[f"{hop[0]}->{hop[1]}"] = (t, backlog * 8 / cap * 1000)
    return out


def path_egresses(run, s: str, recorded) -> set[str]:
    return {f"{a}->{b}" for a, b in d.path_hops(run, run.pub, s)} & set(recorded)


def class_ok(run, members, delay, lo, hi) -> tuple[bool, list[str]]:
    """A data class is right when its members share a recorded router egress whose
    queue reached Q_TARGET_MS inside [lo, hi]."""
    common = set.intersection(*[path_egresses(run, m, delay) for m in members]) if members else set()
    formed = [h for h in sorted(common)
              if np.any((delay[h][0] >= lo) & (delay[h][0] <= hi) & (delay[h][1] >= Q_TARGET_MS))]
    return bool(formed), formed


def neg_rows(rd: Path) -> list[dict]:
    run = ga.load_run(rd)
    delay = egress_delay(run)
    rows = [r for r in STEP2_ROWS.get(rd.name, [])]
    out = []
    for r in rows:
        x = r["x1"]
        verdict = []
        for c in x["classes"]:
            ok, formed = class_ok(run, c, delay, r["lo"], r["hi"])
            verdict.append({"members": c, "ok": ok, "hops": formed,
                            "has_ctrl": "sub-ctrl" in c})
        out.append({"run": rd.name, "type": r["type"], "aqm": r["aqm"], "event": r["event"], "classes": verdict})
    # ECG's confirmed SAME pairs at the end of the run (v2-owd, delta 0.15)
    m_path = rd / "grouping-d150-v2-owd" / "metrics.json"
    pairs = []
    if m_path.exists():
        m = json.loads(m_path.read_text())
        hop_eps = ga.gt1_hop_episodes(run)
        for p, v in m["pairwise"]["pairs"].items():
            if v["decided"] != "SAME":
                continue
            a, b = p.split("|")
            common = path_egresses(run, a, delay) & path_egresses(run, b, delay)
            gt1_hops = [h for h in sorted(common) if hop_eps.get(h)]
            pairs.append({"pair": p, "common_hops": sorted(common), "gt1_episode_hops": gt1_hops, "ok": bool(gt1_hops)})
    out.append({"run": rd.name, "type": rd.name.split("-")[1], "aqm": rd.name.split("-")[-2], "ecg_pairs": pairs})
    return out


STEP2_ROWS: dict = {}


def _init_neg(path: str) -> None:
    global STEP2_ROWS
    STEP2_ROWS = defaultdict(list)
    for r in read_jsonl(Path(path)):
        if r["class"] == "negative":
            STEP2_ROWS[r["run"]].append(r)


def cmd_neg(campaign: Path, out: Path) -> None:
    rows_path = out.parent / "step2-rows.jsonl.gz"
    runs = [rd for rd in runs_of(campaign, "G")]
    with Pool(10, initializer=_init_neg, initargs=(str(rows_path),)) as pool, out.open("w") as fh:
        for rows in pool.imap_unordered(neg_rows, runs):
            for r in rows:
                fh.write(json.dumps(r) + "\n")


def cmd_neg_sum(path: Path) -> None:
    R = read_jsonl(path)
    ev = [r for r in R if "classes" in r]
    ec = [r for r in R if "ecg_pairs" in r]
    print("# Step 2b B: negatives (G0) against a topology-based truth\n")
    print(f"A data class is right when its members share a recorded router egress whose queue reached {Q_TARGET_MS:g} ms "
          "(GT1 target) inside the event interval; wrong otherwise (sub-ctrl with anyone; branches without a formed "
          "common upstream queue). Step 2 placements at penalty x1.\n")
    print("| type | events | data classes | right | wrong | wrong classes containing sub-ctrl |\n|---|---|---|---|---|---|")
    by = defaultdict(list)
    for r in ev:
        by[r["type"]].append(r)
    tot = [0, 0, 0, 0, 0]
    for k in sorted(by):
        cl = [c for r in by[k] for c in r["classes"]]
        row = [len(by[k]), len(cl), sum(c["ok"] for c in cl), sum(not c["ok"] for c in cl), sum((not c["ok"]) and c["has_ctrl"] for c in cl)]
        tot = [a + b for a, b in zip(tot, row)]
        print(f"| {k} | " + " | ".join(map(str, row)) + " |")
    print("| all | " + " | ".join(map(str, tot)) + " |")
    print("\n## ECG's confirmed SAME pairs on G0 (end of run, delta 0.15, v2-owd)\n")
    print("A pair is right when the two clients share a recorded router egress with at least one GT1 episode in the run.\n")
    print("| type | AQM | SAME pairs | right | wrong | wrong pairs |\n|---|---|---|---|---|---|")
    n = [0, 0]
    for r in sorted(ec, key=lambda x: (x["type"], x["aqm"])):
        if not r["ecg_pairs"]:
            continue
        ok = sum(p["ok"] for p in r["ecg_pairs"])
        n[0] += ok
        n[1] += len(r["ecg_pairs"]) - ok
        print(f"| {r['type']} | {r['aqm']} | {len(r['ecg_pairs'])} | {ok} | {len(r['ecg_pairs']) - ok} | "
              f"{', '.join(p['pair'] for p in r['ecg_pairs'] if not p['ok']) or '-'} |")
    print(f"\nTotal: {n[0]} right, {n[1]} wrong.")


# ═══ Step 2b C: short shared queues in calm periods ══════════════════════

PEAK_MARGIN = 0.5      # FLAG: interval around a queue peak handed to the step 2 procedure
CALM_TYPES = ("calm065", "calmsplit", "calmtree8", "calmuneven")


def calm_rows(rd: Path) -> list[dict]:
    run = ga.load_run(rd)
    delay = egress_delay(run)
    series = {s: ts.owd_series(run, s)["min"] for s in run.subs if run.sender_file(s, "owd").exists()}
    rate = {s: run.topology["subscribers"].get(s, {}).get("rate_kbps") for s in run.subs}
    obs = {s: ga.sent_rate_obs(run, s, (rate.get(s) or 1000) * 1000, 0.5, run.duration) for s in series}
    peaks = []
    for h, (t, q) in delay.items():
        on = (q >= Q_TARGET_MS) & (t >= d.WARMUP_S)
        i = 0
        while i < len(on):
            if not on[i]:
                i += 1
                continue
            j = i
            while j + 1 < len(on) and on[j + 1]:
                j += 1
            peaks.append((h, float(t[i]), float(t[j]), float(q[i:j + 1].max())))
            i = j + 1
    minutes = (run.duration - d.WARMUP_S) / 60
    out = []
    for h, a, b, qmax in peaks:
        lo, hi = a - PEAK_MARGIN, b + PEAK_MARGIN
        others = [p for p in peaks if p[0] != h and p[1] <= hi and p[2] >= lo]
        grid, qs = curves(run, series, lo, hi)
        i0, i1 = int(max(lo, 0) / ga.OBS_WINDOW), int(hi / ga.OBS_WINDOW)
        qs = {s: q for s, q in qs.items() if len(obs[s][i0:i1]) and np.mean(obs[s][i0:i1]) >= OBS_SHARE}
        behind = sorted(s for s in qs if h in path_egresses(run, s, delay))
        row = {"run": rd.name, "type": rd.name.split("-")[1], "aqm": rd.name.split("-")[-2], "hop": h,
               "start": a, "dur": b - a, "peak_ms": qmax, "per_min": len(peaks) / minutes,
               "other_egress_peak": bool(others), "behind": behind}
        if len(qs) >= 2 and behind:
            res = partition_event(qs, 1.0)
            lab = {s: k for k, c in enumerate(res["classes"]) for s in c}
            ks = {lab.get(s) for s in behind}
            together = len(behind) >= 2 and len(ks) == 1 and None not in ks
            k0 = next(iter(ks)) if together else None
            apart = all(lab.get(s) != k0 for s in qs if s not in behind) if together else None
            row.update({"classes": res["classes"], "together": together, "apart": apart,
                        "behind_in_0": sum(s in res["zero"] for s in behind), "n_behind": len(behind),
                        "outsiders_grouped": sum(s not in behind and s in lab for s in qs)})
        out.append(row)
    return out


def cmd_calm(campaign: Path, out: Path) -> None:
    runs = [rd for rd in runs_of(campaign, "G") if rd.name.split("-")[1] in CALM_TYPES]
    with Pool(10) as pool, out.open("w") as fh:
        for rows in pool.imap_unordered(calm_rows, runs):
            for r in rows:
                fh.write(json.dumps(r) + "\n")


def cmd_calm_sum(path: Path) -> None:
    R = read_jsonl(path)
    print("# Step 2b C: short shared queues in calm runs (no detector)\n")
    print(f"Queue peak = contiguous time with the egress queue delay >= {Q_TARGET_MS:g} ms (router-metrics; 5 ms CSV on "
          f"split / tree8 / uneven, 25 ms on base). Each peak's interval (+/- {PEAK_MARGIN:g} s) goes through the step 2 "
          "procedure (penalty x1). Placement right: the clients behind the peaking egress share one data class "
          "(together) and no other client is in it (apart).\n")
    print("| type | egress | peaks | per min (this egress) | peak ms p10 / p50 / p90 | duration ms p10 / p50 / p90 | "
          "together | together and apart | behind clients left in class 0 | with another egress peaking |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    by = defaultdict(list)
    for r in R:
        by[(r["type"], r["hop"])].append(r)
    dur_min = {}
    for r in R:
        dur_min[r["run"]] = r["per_min"]
    for k in sorted(by):
        rs = by[k]
        sc = [r for r in rs if "together" in r and r["n_behind"] >= 2]
        nb = sum(r.get("n_behind", 0) for r in sc)
        runs = {r["run"] for r in rs}
        # run minutes = all peaks of the run / its per-minute rate; per egress rate = this egress's peaks / minutes
        minutes = sum(sum(x["run"] == u for x in R) / dur_min[u] for u in runs)
        print(f"| {k[0]} | {k[1]} | {len(rs)} | {len(rs) / minutes:.1f} "
              f"| {q3([r['peak_ms'] for r in rs], '.1f')} | {q3([r['dur'] * 1000 for r in rs], '.0f')} "
              f"| {np.mean([r['together'] for r in sc]) if sc else float('nan'):.2f} "
              f"| {np.mean([bool(r['together'] and r['apart']) for r in sc]) if sc else float('nan'):.2f} "
              f"| {sum(r['behind_in_0'] for r in sc) / nb if nb else float('nan'):.2f} "
              f"| {np.mean([r['other_egress_peak'] for r in rs]):.2f} |")
    print("\nPlacement by peak size (all calm types, peaks with >= 2 observable clients behind the egress):\n")
    print("| peak ms | peaks | together | together and apart | behind clients in class 0 |\n|---|---|---|---|---|")
    for lab, lo, hi in (("5-10", 5, 10), ("10-20", 10, 20), ("20-50", 20, 50), (">= 50", 50, 1e9)):
        sc = [r for r in R if "together" in r and r["n_behind"] >= 2 and lo <= r["peak_ms"] < hi]
        nb = sum(r["n_behind"] for r in sc)
        if sc:
            print(f"| {lab} | {len(sc)} | {np.mean([r['together'] for r in sc]):.2f} "
                  f"| {np.mean([bool(r['together'] and r['apart']) for r in sc]):.2f} | {sum(r['behind_in_0'] for r in sc) / nb:.2f} |")


# ═══ Step 2b D: group size 2, iteration cap ═════════════════════════════

def cmd_d_items(campaign: Path, path: Path, out_dir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    R = read_jsonl(path)
    two = [r for r in R if r["class"] == "single group" and r["x1"]["group_sizes"] == [2]]
    print("# Step 2b D\n")
    print(f"## Single-group events with a truth group of 2: {len(two)}\n")
    print("| campaign / type | events | exact | both members in class 0 | one in class 0 |\n|---|---|---|---|---|")
    by = defaultdict(list)
    for r in two:
        by[f"{r['campaign']} {r['type']}"].append(r)
    for k in sorted(by):
        rs = by[k]
        print(f"| {k} | {len(rs)} | {sum(r['x1']['exact'] for r in rs)} | {sum(r['x1']['cong_in_0'] == 2 for r in rs)} "
              f"| {sum(r['x1']['cong_in_0'] == 1 for r in rs)} |")
    bad = [r for r in two if r["x1"]["cong_in_0"] > 0][:2]
    for n, r in enumerate(bad, 1):
        run = ga.load_run(campaign / r["campaign"] / r["run"])
        series = {s: ts.owd_series(run, s)["min"] for s in r["truth"]}
        grid, qs = curves(run, series, r["lo"], r["hi"])
        qs = {s: q for s, q in qs.items() if s in r["truth"]}
        P, parts, classes, _ = base_partition(qs)
        pair = [s for s, v in r["truth"].items() if v]
        print(f"\n### Example {n}: {r['run']} [{r['lo']:.1f}, {r['hi']:.1f}] s, truth pair {pair}\n")
        print("| client | truth | f(class 0) | f(median of all others) | f(the other pair member) | placed |\n|---|---|---|---|---|---|")
        lab = {s: k + 1 for k, c in enumerate(r["x1"]["classes"]) for s in c}
        for s in parts:
            other = [p for p in pair if p != s]
            fo = f_fit(qs[s], qs[other[0]])[0] if other and f_fit(qs[s], qs[other[0]]) else None
            fa = P.fit(s, parts)
            print(f"| {s} | {','.join(r['truth'][s]) or 'quiet'} | {P.f0[s]:.1f} | {fa if fa is None else round(fa, 1)} "
                  f"| {'-' if fo is None else round(fo, 1)} | class {lab.get(s, 0)} |")
        fig, ax = plt.subplots(figsize=(8, 3.2))
        for s, q in sorted(qs.items()):
            k = lab.get(s, 0)
            ax.plot(grid, q, ".", ms=2, color="0.6" if k == 0 else f"C{k - 1}",
                    label=f"{s}: class {k} (truth {','.join(r['truth'][s]) or 'quiet'})")
        ax.set_title(f"group of 2: {r['run']} [{r['lo']:.1f}, {r['hi']:.1f}] s", fontsize=8)
        ax.set_xlabel("run time s")
        ax.set_ylabel("queuing delay ms")
        ax.legend(fontsize=6, ncol=2)
        fig.tight_layout()
        f = out_dir / f"step2b-pair{n}.png"
        fig.savefig(f, dpi=120)
        plt.close(fig)
        print(f"\n{f}")
    cap = [r for r in R if MAX_ITER in r["x1"]["iterations"]]
    print(f"\n## Assignment passes at the iteration cap ({MAX_ITER}): {sum(r['x1']['iterations'].count(MAX_ITER) for r in R)} "
          f"passes in {len(cap)} events\n")
    print("| event class | events |\n|---|---|")
    for k, v in Counter(r["class"] for r in cap).most_common():
        print(f"| {k} | {v} |")
    print("\n| campaign / type | events |\n|---|---|")
    for k, v in Counter(f"{r['campaign']} {r['type']} {r['aqm']}" for r in cap).most_common(12):
        print(f"| {k} | {v} |")


if __name__ == "__main__":
    main(sys.argv[1:])
