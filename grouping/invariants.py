"""Invariants of brief v1.1 §8.3, checked after every event close. Attach with
`Invariants(engine)`; violations raise AssertionError with the event id."""

from __future__ import annotations

from .engine import ROOT, Engine
from .types import Event


class Invariants:
    def __init__(self, eng: Engine):
        self.eng = eng
        self.cap = eng.cfg.w_cap_frac * eng.A + 1e-9
        self.before = eng.snapshot()
        eng.on_event_closed.append(self.after_event)
        eng.on_decay.append(self.after_decay)
        self.n_checked = 0
        prev = eng._log

        def log(rec: dict) -> None:
            if rec.get("type") == "evidence" and rec.get("kind") in ("L", "cand"):
                assert rec["w"] <= self.cap, f"inv8: w={rec['w']} > cap at event {rec['event_id']}"
            prev(rec)
        eng._log = log

    # ── hooks ────────────────────────────────────────────────────────────

    def after_decay(self, eng: Engine) -> None:
        self.before = eng.snapshot()

    def after_event(self, eng: Engine, e: Event, case: str) -> None:
        after = eng.snapshot()
        b, a = self.before, after
        M = sorted({m.flow for m in e.members})
        tag = f"event {e.id} ({case})"
        # Flows an event may touch: M, members/candidates of the leaves M's flows
        # belong to or are candidates of (as they stood before the event).
        allowed = set(M)
        for f in M:
            st = b["flows"].get(f)
            if not st:
                continue
            for n in [st["node"]] + [int(k) for k in st["cand"]]:
                node = b["nodes"].get(n) if n is not None else None
                if node and node["kind"] == "leaf":
                    allowed |= set(node["members"]) | set(node["candidates"])
        for f, sa in a["flows"].items():
            sb = b["flows"].get(f, {"node": None, "L": 0.0, "cand": {}, "solo": 0.0, "together": 0.0, "apart": 0.0})
            changed = (sa["L"] != sb["L"] or sa["cand"] != sb["cand"] or sa["solo"] != sb["solo"])
            if changed:
                assert f in allowed or f in eng.last_dissolved, f"inv2: {f} changed outside touched set at {tag}"
            if f in allowed and eng.last_observable.get(f) is False and f not in eng.last_dissolved:
                same = all(sa[k] == sb[k] for k in ("L", "cand", "solo", "together", "apart"))
                # A node move is allowed: it only re-keys evidence already earned.
                assert same or sa["node"] != sb["node"], f"inv3: unobservable {f} changed at {tag}"
        leaves_with = {}
        for n, node in a["nodes"].items():
            if node["kind"] == "leaf":
                for f in node["members"]:
                    leaves_with.setdefault(f, []).append(n)
        for f, ls in leaves_with.items():
            assert len(ls) == 1, f"inv1: {f} in leaves {ls} at {tag}"
            assert a["flows"][f]["node"] == ls[0], f"inv1: {f} node mismatch at {tag}"
        if case in ("B", "GLOBAL"):
            # Leaves are never merged by case B: no leaf afterwards holds two or
            # more members from each of two leaves that existed before. (A single
            # flow may still migrate, join its leaf or drop to uncertain.)
            before_leaves = [set(x["members"]) for x in b["nodes"].values() if x["kind"] == "leaf"]
            for z in (set(x["members"]) for x in a["nodes"].values() if x["kind"] == "leaf"):
                donors = [x for x in before_leaves if len(x & z) >= 2]
                assert len(donors) <= 1, f"inv4: leaves merged during {tag}"
        assert ROOT in a["nodes"] and a["nodes"][ROOT]["kind"] == "root", f"inv5: no root at {tag}"
        for n, node in a["nodes"].items():
            if n == ROOT:
                assert node["parent"] is None
                continue
            assert node["parent"] in a["nodes"], f"inv5: {n} parent missing at {tag}"
            assert n in a["nodes"][node["parent"]]["children"], f"inv5: {n} not in parent's children at {tag}"
            seen, cur = set(), n
            while cur is not None:
                assert cur not in seen, f"inv5: cycle at {n} at {tag}"
                seen.add(cur)
                cur = a["nodes"][cur]["parent"]
        total = sum(len(x["members"]) for x in a["nodes"].values() if x["kind"] == "leaf")
        with_node = sum(1 for st in a["flows"].values() if st["node"] is not None)
        assert total == with_node, f"inv6: {total} members vs {with_node} flows with node at {tag}"
        self.before = after
        self.n_checked += 1
