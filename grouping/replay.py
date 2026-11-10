"""Run the ECG engine over an onset log (records or JSONL file), collect the
metrics of brief v1.1 §8.4, evaluate the scenario pass criteria and plot
L[f, n] versus time."""

from __future__ import annotations

import json
import math
from collections import Counter
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path

from .config import Config
from .engine import Engine, JsonlLogger
from .synth import same_access


@dataclass
class Result:
    cfg: dict
    series: dict[str, list[tuple]] = field(default_factory=dict)     # flow -> [(t, node, L)]
    snapshots: list[dict] = field(default_factory=list)              # engine.snapshot() at each event close
    cases: Counter = field(default_factory=Counter)
    events: list[dict] = field(default_factory=list)                 # per event: id, t, case, members, spans
    leaves: dict = field(default_factory=dict)                       # node id -> info at end
    final: dict = field(default_factory=dict)                        # snapshot at last event close
    engine: Engine | None = None

    def pairs(self, snap: dict | None = None) -> dict[tuple[str, str], str]:
        """Pairwise decision at a snapshot (default: close of the last event):
        SAME / DIFFERENT / UNCERTAIN."""
        snap = self.final if snap is None else snap
        A = self.cfg["A"]
        nodes = snap.get("nodes", {})
        out = {}
        flows = sorted(snap["flows"])

        def member(x):
            return x.get("member", x["L"] >= A)

        def confirmed(x):
            node = nodes.get(x["node"], nodes.get(str(x["node"])))
            return node is None or node["confirmed"]
        for f, g in combinations(flows, 2):
            a, b = snap["flows"][f], snap["flows"][g]
            if a["node"] is None or b["node"] is None or not member(a) or not member(b):
                out[(f, g)] = "UNCERTAIN"
            elif self.cfg.get("report_confirmed_only") and not (confirmed(a) and confirmed(b)):
                out[(f, g)] = "UNCERTAIN"
            else:
                out[(f, g)] = "SAME" if a["node"] == b["node"] else "DIFFERENT"
        return out

    def pairs_t(self) -> list[dict]:
        """Pairwise decisions after every event close: [{t, pairs: {"f|g": dec}}]."""
        return [{"t": s["t"], "pairs": {f"{f}|{g}": v for (f, g), v in self.pairs(s).items()}}
                for s in self.snapshots]

    def to_json(self) -> dict:
        return {"cfg": self.cfg, "cases": dict(self.cases), "events": self.events, "leaves": self.leaves,
                "series": self.series, "final": self.final,
                "pairs": {f"{f}|{g}": v for (f, g), v in self.pairs().items()}}


def run(records, cfg: Config, log_path: str | Path | None = None, keep_engine: bool = False,
        engine_factory=None) -> Result:
    logger = JsonlLogger(log_path) if log_path else None
    eng = engine_factory(records, cfg, log=logger) if engine_factory else Engine(cfg, logger)
    res = Result(cfg={**cfg.to_dict(), "A": cfg.A, "B": cfg.B})
    flows_seen: list[str] = []

    def on_close(engine: Engine, e, case):
        res.cases[case] += 1
        snap = engine.snapshot()
        res.snapshots.append(snap)
        for f, st in snap["flows"].items():
            res.series.setdefault(f, []).append((snap["t"], st["node"], st["L"]))
        res.events.append({"id": e.id, "t": snap["t"], "t0": e.t0, "case": case,
                           "members": sorted({m.flow for m in e.members}),
                           "span_al": max(m.t_al for m in e.members) - min(m.t_al for m in e.members),
                           "span_arrival": max(m.t_arrival for m in e.members) - e.t0})

    eng.on_event_closed.append(on_close)
    next_tick = 0.0
    for kind, t, obj in records:
        while next_tick <= t:
            eng.tick(next_tick)
            next_tick = round(next_tick + cfg.obs_window, 6)
        if kind == "meta":
            eng.on_meta(obj)
            flows_seen.append(obj.flow)
        elif kind == "obs":
            eng.on_obs(obj)
        else:
            eng.on_onset(obj)
    eng.finish()
    if logger:
        logger.close()
    res.final = res.snapshots[-1] if res.snapshots else eng.snapshot()
    for n, node in sorted(eng.nodes.items()):
        if node.kind != "root":
            res.leaves[n] = {"kind": node.kind, "parent": node.parent, "members": sorted(node.members),
                             "candidates": sorted(node.candidates), "children": sorted(node.children),
                             "support": node.support, "confirmed": node.confirmed,
                             "confirmed_t": node.confirmed_t, "confirmed_events": node.confirmed_events,
                             "created_t": node.created_t}
    if keep_engine:
        res.engine = eng
    return res


# ── metrics ──────────────────────────────────────────────────────────────

def pairwise_metrics(res: Result, truth: dict) -> dict:
    pairs = res.pairs()
    tp = fp = fn = tn = unc = 0
    for (f, g), d in pairs.items():
        same = same_access(truth, f, g)
        if d == "UNCERTAIN":
            unc += 1
        elif d == "SAME":
            tp += same
            fp += not same
        else:
            fn += same
            tn += not same
    decided = tp + fp + fn + tn
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "uncertain": unc,
            "precision": tp / (tp + fp) if tp + fp else None,
            "recall": tp / (tp + fn) if tp + fn else None,
            "coverage": decided / len(pairs) if pairs else None}


def drift(res: Result, f: str, g: str) -> float:
    """Max L or cand that f reached toward a node containing g (members or candidates)."""
    best = 0.0
    for snap in res.snapshots:
        for n, node in snap["nodes"].items():
            if node["kind"] != "leaf" or g not in node["members"] + node["candidates"]:
                continue
            st = snap["flows"][f]
            if st["node"] == int(n):
                best = max(best, st["L"])
            best = max(best, st["cand"].get(n, st["cand"].get(int(n), 0.0)))
    return best


def span_stats(res: Result) -> dict:
    multi = [e for e in res.events if len(e["members"]) > 1]
    if not multi:
        return {}
    al = sorted(e["span_al"] for e in multi)
    arr = sorted(e["span_arrival"] for e in multi)
    q = lambda xs, p: xs[min(len(xs) - 1, int(p * len(xs)))]
    return {"n": len(multi), "span_al_p50": q(al, .5), "span_al_max": al[-1],
            "span_arrival_p50": q(arr, .5), "span_arrival_max": arr[-1]}


def metrics(res: Result, truth: dict) -> dict:
    flows = sorted(truth["flows"])
    out = {"cases": dict(res.cases), "pairwise": pairwise_metrics(res, truth), "spans": span_stats(res),
           "leaves": res.leaves, "final": {f: res.final["flows"][f] for f in flows if f in res.final["flows"]}}
    if truth["scenario"] == "S2":
        out["drift"] = max(drift(res, flows[0], flows[1]), drift(res, flows[1], flows[0]))
    return out


# ── pass criteria (brief §8.2) ───────────────────────────────────────────

def _leaf_of(snap: dict, flows: list[str], A: float) -> int | None:
    nodes = {snap["flows"][f]["node"] for f in flows}
    if len(nodes) != 1 or None in nodes:
        return None
    return nodes.pop() if all(snap["flows"][f]["L"] >= A for f in flows) else None


def _multi_events(res: Result):
    return [e for e in res.events if len(e["members"]) > 1]


def _events_until_leaf(res: Result, flows: list[str], A: float) -> int | None:
    """Multi-flow events closed until all flows are L >= A in one leaf."""
    n = 0
    for e, snap in zip(res.events, res.snapshots):
        n += len(e["members"]) > 1
        if _leaf_of(snap, flows, A) is not None:
            return n
    return None


def _no_false_leaf(snap: dict, groups: list[list[str]]) -> bool:
    """No confirmed leaf mixes flows of two truth groups. Provisional leaves
    (support < A) are evidence buffers, not reported structure (v1.2 rule 2),
    so a coincidence pair that has not confirmed does not count."""
    member_of = {f: i for i, g in enumerate(groups) for f in g}
    for node in snap["nodes"].values():
        if node["kind"] == "leaf" and node["confirmed"] and len({member_of.get(f, -1) for f in node["members"]}) > 1:
            return False
    return True


def _confirmed_leaf_for(res: Result, group: list[str]) -> dict | None:
    for n, leaf in res.leaves.items():
        if leaf["kind"] == "leaf" and leaf["confirmed"] and set(leaf["members"]) == set(group):
            return {"id": n, **leaf}
    return None


def check(sc_id: str, res: Result, truth: dict) -> tuple[bool, dict]:
    A, B = res.cfg["A"], res.cfg["B"]
    final = res.final
    d: dict = {}
    if sc_id == "S1":
        flows = ["f1", "f2", "f3"]
        d["events_to_leaf"] = _events_until_leaf(res, flows, A)
        d["same_leaf_end"] = _leaf_of(final, flows, A) is not None
        d["no_false_leaf"] = _no_false_leaf(final, [flows])
        ok = d["events_to_leaf"] is not None and d["events_to_leaf"] <= 3 and d["same_leaf_end"] and d["no_false_leaf"]
    elif sc_id == "S2":
        # drift = the largest L / cand the pair ever accumulated (two coincidences
        # at the per-event cap already exceed A). The pass criterion follows the
        # visibility rule (v1.2 rule 2): the pair must never be *reported* SAME.
        d["drift"] = max(drift(res, "f1", "f2"), drift(res, "f2", "f1"))
        d["reported_same_closes"] = sum(res.pairs(s).get(("f1", "f2")) == "SAME" for s in res.snapshots)
        ok = d["reported_same_closes"] == 0
    elif sc_id == "S3":
        st = final["flows"]["f1"]
        eps = truth["episodes"]["f1"]
        # Truth: episodes not caused by the shared link. Noise onsets are solo
        # onsets too; the engine cannot (and should not) tell them from private
        # congestion, so they count as private. The P-only figure is reported too.
        d["true_private_fraction"] = sum(c != "A" for _, _, c in eps) / len(eps) if eps else 0.0
        d["true_private_fraction_P_only"] = sum(c == "P" for _, _, c in eps) / len(eps) if eps else 0.0
        tot = st["solo"] + st["together"]
        d["private_fraction"] = st["solo"] / tot if tot else 0.0
        d["f1_member"] = st["node"] is not None and st["L"] >= A
        d["others_member"] = all(final["flows"][f]["node"] == st["node"] and final["flows"][f]["L"] >= A
                                 for f in ("f2", "f3"))
        ok = d["f1_member"] and d["others_member"] and abs(d["private_fraction"] - d["true_private_fraction"]) <= 0.15
    elif sc_id in ("S4", "S5"):
        ga, gb = ["f1", "f2", "f3"], ["f4", "f5", "f6"]
        if sc_id == "S5":
            ga, gb = ["f1", "f2"], ["f3", "f4", "f5", "f6"]
        la, lb = _confirmed_leaf_for(res, ga), _confirmed_leaf_for(res, gb)
        d["leaf_A"], d["leaf_B"] = la and la["id"], lb and lb["id"]
        d["cases"] = dict(res.cases)
        def groups_at(t: float) -> list[list[str]]:
            if sc_id == "S5" and t < 150:
                return [["f1", "f2", "f3"], ["f4", "f5", "f6"]]
            return [ga, gb]
        d["never_merged"] = all(_no_false_leaf(s, groups_at(s["t"])) for s in res.snapshots)
        ok = la is not None and lb is not None and d["never_merged"]
        if sc_id == "S4":
            # Aggregation events after both leaves were confirmed must be GLOBAL.
            tc = max(la["confirmed_t"], lb["confirmed_t"]) if ok else math.inf
            agg = [e for e in res.events if e["t0"] > tc - 1 and len(e["members"]) >= 5]
            d["agg_after_confirm"] = Counter(e["case"] for e in agg)
            ok = ok and agg and all(e["case"] == "GLOBAL" for e in agg)
        else:
            f2 = [e for e in res.events if "f2" in e["members"] and len(e["members"]) > 1]
            d["f2_events_to_member"] = _events_until_leaf(res, ["f1", "f2"], A)
            d["f2_joined_t"] = next((s["t"] for s in res.snapshots
                                     if s["flows"]["f2"]["node"] is not None and s["flows"]["f2"]["L"] >= A), None)
            # Events whose onset window lies inside the idle interval (f5 sends nothing).
            idle = [s for e, s in zip(res.events, res.snapshots) if 100.5 < e["t0"] < 199.5]
            before = [s for e, s in zip(res.events, res.snapshots) if e["t0"] <= 100.5]
            apart0 = before[-1]["flows"]["f5"]["apart"] if before else 0.0
            d["f5_apart_idle"] = max((s["flows"]["f5"]["apart"] - apart0 for s in idle), default=0.0)
            d["f5_member_idle"] = all(s["flows"]["f5"]["node"] is not None for s in idle)
            b_events = [e for e in res.events if e["t0"] > 150 and len(e["members"]) >= 2
                        and set(e["members"]) & {"f4", "f5", "f6"} and not set(e["members"]) & {"f1", "f2"}]
            third = b_events[2]["t"] if len(b_events) >= 3 else math.inf
            snap3 = next((s for s in res.snapshots if s["t"] >= third), res.final)
            f3 = snap3["flows"]["f3"]
            d["f3_in_B_by_3rd_B_event"] = f3["node"] is not None and f3["node"] == lb["id"] if lb else False
            d["f3_L_by_3rd"] = f3["L"]
            ok = ok and d["f5_apart_idle"] <= 0 and d["f5_member_idle"] and d["f3_in_B_by_3rd_B_event"] \
                and f3["L"] >= A
    elif sc_id == "S6":
        groups = [[f"f{1 + 3 * i + j}" for j in range(3)] for i in range(4)]
        leaves = [_confirmed_leaf_for(res, g) for g in groups]
        d["leaves"] = [l and l["id"] for l in leaves]
        internals = {n: l for n, l in res.leaves.items() if l["kind"] == "internal"}
        d["internal_children"] = {n: l["children"] for n, l in internals.items()}
        want = [{leaves[0]["id"], leaves[1]["id"]}, {leaves[2]["id"], leaves[3]["id"]}] if all(leaves) else []
        d["internals_ok"] = len(internals) == 2 and all(set(l["children"]) in want for l in internals.values())
        d["cases"] = dict(res.cases)
        d["no_false_leaf"] = _no_false_leaf(final, groups)
        g1 = [e for e in res.events if len(e["members"]) in (5, 6) and set(e["members"]) <= set(groups[0] + groups[1])]
        root = [e for e in res.events if len(e["members"]) >= 10]
        d["G1_cases"] = Counter(e["case"] for e in g1)
        d["root_cases"] = Counter(e["case"] for e in root)
        ok = all(leaves) and d["internals_ok"] and d["no_false_leaf"] and \
            all(e["case"] in ("B", "GLOBAL") for e in root) and any(e["case"] == "GLOBAL" for e in root)
    else:
        raise KeyError(sc_id)
    return bool(ok), d


# ── plot ─────────────────────────────────────────────────────────────────

INK, INK_2, MUTED, GRID, SURFACE = "#1f1f1e", "#5f5e58", "#a3a29a", "#e6e5df", "#fcfcfb"
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#6250d6", "#e87ba4", "#e34948", "#5f5e58",
           "#0f7f8f", "#b9641c", "#8c3fa0", "#3a7d44"]


def plot_L(res: Result, path: str | Path, title: str = "") -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    flows = sorted(res.series)
    A, B = res.cfg["A"], res.cfg["B"]
    fig, ax = plt.subplots(figsize=(11, 3.6), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    for i, f in enumerate(flows):
        pts = res.series[f]
        col = PALETTE[i % len(PALETTE)]
        # Break the line where the flow changes node.
        xs, ys, last = [], [], None
        for t, node, L in pts:
            if last is not None and node != last:
                ax.plot(xs, ys, color=col, linewidth=1.2)
                xs, ys = [], []
            xs.append(t)
            ys.append(L)
            last = node
        ax.plot(xs, ys, color=col, linewidth=1.2, label=f)
        moves = [(t, L) for (t, n0, L), (_, n1, _) in zip(pts, pts[1:] + [pts[-1]]) if n0 != n1]
        if moves:
            ax.scatter([t for t, _ in moves], [L for _, L in moves], color=col, s=14, zorder=3)
    ax.axhline(A, color=MUTED, linewidth=0.8, linestyle="--")
    ax.axhline(B, color=MUTED, linewidth=0.8, linestyle=":")
    ax.text(ax.get_xlim()[1], A, " A", color=INK_2, fontsize=7, va="center")
    ax.text(ax.get_xlim()[1], B, " B", color=INK_2, fontsize=7, va="center")
    ax.set_xlabel("log time (s)", color=INK_2, fontsize=8)
    ax.set_ylabel("L[f, node]", color=INK_2, fontsize=8)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.tick_params(colors=INK_2, labelsize=7, length=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if flows:
        ax.legend(ncol=min(6, len(flows)), fontsize=7, frameon=False, loc="upper left", labelcolor=INK)
    ax.set_title(title or "membership log-odds per flow (dots: node change)", fontsize=9, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def dump(obj, path: str | Path) -> None:
    Path(path).write_text(json.dumps(obj, indent=1, sort_keys=True, default=_default))


def _default(o):
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    if isinstance(o, Counter):
        return dict(o)
    if isinstance(o, tuple):
        return list(o)
    raise TypeError(type(o))
