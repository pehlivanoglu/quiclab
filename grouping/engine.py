"""ECG engine (brief v1.1 §4–§6).

Driven by three inputs in time order: FlowMeta, ObsSample (every obs_window per
flow) and Onset (in t_arrival order), plus tick(t) every obs_window of log
time. Events are clusters of aligned onsets; at event close the tree is
matched (cases A, A-superset, B/GLOBAL, C, D, SOLO) and sequential evidence
L[f, node] / cand[f, node] is updated. No pairwise flow loops: only the event
members, the touched leaves and their candidate sets are visited.

Deviations from the brief are listed in README.md ("ambiguities").
"""

from __future__ import annotations

import json
import math
from collections import Counter, deque
from statistics import median
from typing import Callable, Iterable

import numpy as np

from .config import Config
from .types import (ConfirmedShared, Event, FlowMeta, FlowState, Member, Node, ObsSample, Onset,
                    Private)

ROOT = 0


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


class Engine:
    def __init__(self, cfg: Config, log: Callable[[dict], None] | None = None):
        self.cfg = cfg
        self.A, self.B, self.cap = cfg.A, cfg.B, cfg.l_cap
        self.rng = np.random.default_rng(cfg.seed)
        self._log = log or (lambda rec: None)
        self.meta: dict[str, FlowMeta] = {}
        self.state: dict[str, FlowState] = {}
        self.obs: dict[str, deque[ObsSample]] = {}
        self.nodes: dict[int, Node] = {ROOT: Node(id=ROOT, kind="root", parent=None)}
        self._next_node = 1
        self.open_events: list[Event] = []
        self._event_seq = 0
        self.now = 0.0
        self._next_decay = cfg.decay_period
        self.outputs: list = []
        self.closed_events = 0
        self.last_close: tuple[float, int] | None = None   # (t, event id)
        self.on_event_closed: list[Callable[["Engine", Event, str], None]] = []
        self.on_decay: list[Callable[["Engine"], None]] = []
        self.last_observable: dict[str, bool] = {}
        self.last_dissolved: list[str] = []   # flows released by dissolution in the last event
        self._obs_horizon = cfg.delta + cfg.delta_max + cfg.hold + 0.5

    # ── inputs ───────────────────────────────────────────────────────────

    def _ensure(self, flow: str) -> FlowState:
        st = self.state.get(flow)
        if st is None:
            st = self.state[flow] = FlowState(lambda_bg=self.cfg.lambda_init)
            self.obs[flow] = deque()
            self.meta.setdefault(flow, FlowMeta(flow=flow, mrtt=0.0))
        return st

    def on_meta(self, m: FlowMeta) -> None:
        self.meta[m.flow] = m
        self._ensure(m.flow)

    def on_obs(self, s: ObsSample) -> None:
        st = self._ensure(s.flow)
        dq = self.obs[s.flow]
        dq.append(s)
        lim = s.t - self._obs_horizon
        while dq and dq[0].t < lim:
            dq.popleft()
        st.in_episode = s.in_episode
        if st.episode_since is not None and not s.in_episode and s.t >= st.episode_since:
            st.episode_since = None

    def on_onset(self, o: Onset) -> None:
        st = self._ensure(o.flow)
        if st.episode_since is not None:
            self._log({"type": "onset_ignored", "t": o.t_arrival, "flow": o.flow, "reason": "in_episode"})
            return
        st.episode_since = o.t_onset
        # Background onset rate: exponentially weighted count of all onsets.
        if st.lambda_t is not None:
            st.lambda_bg *= math.exp(-(o.t_arrival - st.lambda_t) / self.cfg.lambda_tau)
        st.lambda_bg += 1 / self.cfg.lambda_tau
        st.lambda_t = o.t_arrival
        t_al = self._align(o)
        best, best_d = None, None
        for e in self.open_events:
            d = abs(t_al - e.t0)
            if d <= self.cfg.delta and t_al <= e.t0 + self.cfg.delta_max \
                    and all(m.flow != o.flow for m in e.members) and (best is None or d < best_d):
                best, best_d = e, d
        if best is None:
            self._event_seq += 1
            best = Event(id=self._event_seq, t0=t_al)
            self.open_events.append(best)
            self.open_events.sort(key=lambda e: (e.t0, e.id))
        best.members.append(Member(o.flow, t_al, o.t_arrival, o.track, o.magnitude, o.primed))
        best.closes_at = best.t0 + self.cfg.delta_max + self.cfg.hold
        self._log({"type": "onset", "t": o.t_arrival, "flow": o.flow, "t_onset": o.t_onset,
                   "t_al": t_al, "event_id": best.id})

    def tick(self, t: float) -> None:
        self.now = t
        while self._next_decay <= t:
            self._decay(self._next_decay)
            self._next_decay += self.cfg.decay_period
        due = sorted((e for e in self.open_events if e.closes_at <= t), key=lambda e: (e.closes_at, e.t0, e.id))
        for e in due:
            self.open_events.remove(e)
            self._close(e)

    def finish(self) -> None:
        """Close everything still open (end of a log)."""
        last = max([e.closes_at for e in self.open_events] + [self.now])
        self.tick(last + 1e-9)

    # ── alignment / observability / weights ──────────────────────────────

    def _align(self, o: Onset) -> float:
        mode = self.cfg.align_mode
        if mode == "half_mrtt":
            return o.t_onset - self.meta[o.flow].mrtt / 2
        if mode == "table":
            return o.t_onset - self.cfg.align_table.get(o.flow, 0.0)
        return o.t_onset

    def _observable(self, g: str, e: Event) -> bool:
        lo, hi = e.t0 - self.cfg.delta, e.t0 + self.cfg.delta
        inside, ok, before = 0, 0, None
        for s in self.obs.get(g, ()):
            if s.t <= lo:
                before = s
            if lo <= s.t <= hi:
                inside += 1
                ok += s.observable
                if s.intervened:
                    return False
            elif s.t > hi:
                break
        if inside == 0 or ok * 2 < inside:
            return False
        if before is None:
            # No sample before the window: use the first sample inside it.
            before = next((s for s in self.obs[g] if s.t >= lo), None)
        return before is not None and not before.in_episode

    def _p_fa(self, g: str, t: float) -> float:
        st = self.state[g]
        lam = st.lambda_bg
        if st.lambda_t is not None and t > st.lambda_t:
            lam *= math.exp(-(t - st.lambda_t) / self.cfg.lambda_tau)
        return min(0.5, max(self.cfg.p_fa_floor, 1 - math.exp(-lam * 2 * self.cfg.delta)))

    def _w_neg(self, g: str, e: Event) -> float:
        return math.log((1 - self.cfg.p_det) / (1 - self._p_fa(g, e.t0)))

    def _w_pos(self, g: str, n: int, e: Event, m: Member) -> tuple[float, dict]:
        cfg = self.cfg
        base = math.log(cfg.p_det / self._p_fa(g, e.t0))
        lag = m.t_al - e.t0
        mu, sigma, cnt = self.state[g].lag.get(n, (0.0, 0.0, 0))
        c_lag = 1.0 if cnt < 2 else math.exp(-0.5 * ((lag - mu) / max(sigma, cfg.sigma_min)) ** 2)
        ecn = self.meta[g].ecn_capable
        peers = [x.track for x in e.members if x.flow != g and self.meta[x.flow].ecn_capable == ecn]
        if peers:
            top = Counter(peers).most_common()
            best_n = top[0][1]
            majority = sorted(t for t, c in top if c == best_n)[0]
            c_track = 1.0 if m.track == majority else 0.5
        else:
            c_track = 1.0
        med = median(x.magnitude for x in e.members)
        ratio = m.magnitude / med if med > 0 else 1.0
        c_mag = 1.0 if 1 / 3 <= ratio <= 3 else 0.7
        raw = base * c_lag * c_track * c_mag
        w = min(self.cfg.w_cap_frac * self.A, raw)
        return w, {"base": base, "c_lag": c_lag, "c_track": c_track, "c_mag": c_mag, "capped": w < raw}

    def _update_lag(self, g: str, n: int, lag: float) -> None:
        mu, sigma, cnt = self.state[g].lag.get(n, (0.0, 0.0, 0))
        if cnt == 0:
            self.state[g].lag[n] = (lag, 0.0, 1)
            return
        d = lag - mu
        mu += 0.3 * d
        var = 0.7 * sigma * sigma + 0.3 * d * d
        self.state[g].lag[n] = (mu, math.sqrt(var), cnt + 1)

    # ── evidence bookkeeping ─────────────────────────────────────────────

    def _add_L(self, f: str, w: float, e: Event, case: str, n: int, comps: dict | None = None) -> None:
        st = self.state[f]
        before = st.L
        st.L = min(self.cap, st.L + w)
        if w > 0:
            st.together += 1
        elif w < 0:
            st.apart += 1
        self._log({"type": "evidence", "kind": "L", "t": self.now, "event_id": e.id, "case": case, "flow": f,
                   "node": n, "w": w, "components": comps or {}, "L_before": before, "L_after": st.L})

    def _add_cand(self, f: str, n: int, w: float, e: Event, case: str, comps: dict | None = None) -> None:
        st, node = self.state[f], self.nodes[n]
        before = st.cand.get(n, 0.0)
        after = min(self.cap, before + w)
        if after <= self.B:
            st.cand.pop(n, None)
            node.candidates.discard(f)
        else:
            if n not in st.cand and len(st.cand) >= self.cfg.k_cand:
                drop = min(st.cand, key=lambda k: (st.cand[k], -k))
                if st.cand[drop] >= after:
                    self._log({"type": "evidence", "kind": "cand_dropped", "t": self.now, "event_id": e.id,
                               "case": case, "flow": f, "node": n, "w": w})
                    return
                del st.cand[drop]
                self.nodes[drop].candidates.discard(f)
            st.cand[n] = after
            node.candidates.add(f)
        self._log({"type": "evidence", "kind": "cand", "t": self.now, "event_id": e.id, "case": case, "flow": f,
                   "node": n, "w": w, "components": comps or {}, "L_before": before, "L_after": after})

    def _add_support(self, n: int, w: float, e: Event, case: str) -> None:
        node = self.nodes[n]
        node.support += w
        node.n_events += 1
        self._set_confirmed(node, e)

    def _set_confirmed(self, node: Node, e: Event | None) -> None:
        if not node.confirmed and node.support >= self.A:
            node.confirmed = True
            if node.confirmed_t is None:
                node.confirmed_t, node.confirmed_events = self.now, node.n_events
            self._log({"type": "tree", "op": "confirm", "t": self.now, "node": node.id,
                       "event_id": e.id if e else None, "support": node.support})
        elif node.confirmed and node.support < self.A / 2:
            node.confirmed = False
            self._log({"type": "tree", "op": "unconfirm", "t": self.now, "node": node.id, "support": node.support})

    # ── tree helpers ─────────────────────────────────────────────────────

    def _new_node(self, kind: str, parent: int, e: Event) -> Node:
        n = Node(id=self._next_node, kind=kind, parent=parent, created_t=self.now, created_event=e.id)
        self._next_node += 1
        self.nodes[n.id] = n
        self.nodes[parent].children.add(n.id)
        return n

    def leaves(self) -> list[Node]:
        return [n for n in sorted(self.nodes.values(), key=lambda x: x.id) if n.kind == "leaf"]

    def _ancestors(self, n: int) -> list[int]:
        out, cur = [], self.nodes[n].parent
        while cur is not None:
            out.append(cur)
            cur = self.nodes[cur].parent
        return out

    def _lca(self, ids: list[int]) -> int:
        chains = [[i] + self._ancestors(i) for i in ids]
        common = set(chains[0]).intersection(*chains[1:])
        return next(x for x in chains[0] if x in common)

    def _subtree_flows(self, n: int) -> list[str]:
        node = self.nodes[n]
        if node.kind == "leaf":
            return sorted(node.members | node.candidates)
        out = []
        for c in sorted(node.children):
            out += self._subtree_flows(c)
        return out

    def _nset(self, n: Node) -> list[str]:
        return sorted(n.members | n.candidates)

    def _hypothesis(self, n: int) -> set[str]:
        node = self.nodes[n]
        return node.members | {c for c in node.candidates if self.state[c].node is None}

    # ── event close ──────────────────────────────────────────────────────

    def _close(self, e: Event) -> None:
        self.closed_events += 1
        self.last_close = (self.now, e.id)
        seen, mem = set(), {}
        for m in sorted(e.members, key=lambda m: (m.t_al, m.flow)):
            if m.flow not in seen:
                seen.add(m.flow)
                mem[m.flow] = m
        M = sorted(mem)
        obs_cache: dict[str, bool] = {}
        self.last_dissolved = []

        def observable(g: str) -> bool:
            if g not in obs_cache:
                obs_cache[g] = self._observable(g, e)
            return obs_cache[g]

        touched: list[int] = []
        for f in M:
            st = self.state[f]
            for n in [st.node] + sorted(st.cand):
                if n is not None and self.nodes[n].kind == "leaf" and n not in touched:
                    touched.append(n)
        info = {}
        for n in touched:
            node = self.nodes[n]
            nset = self._nset(node)
            nobs = [g for g in nset if observable(g)]
            inter = [g for g in M if g in nobs]
            union = len(set(M) | set(nobs))
            J = len(inter) / union if union else 0.0
            cov = len(inter) / len(nobs) if nobs else 0.0
            info[n] = (nset, nobs, J, cov)

        case = "SOLO"
        if len(M) == 1:
            self._solo(e, M[0], touched, info, observable)
        else:
            case = self._match(e, M, mem, touched, info, observable)
        spans = {"span_al": max(m.t_al for m in e.members) - min(m.t_al for m in e.members),
                 "span_arrival": max(m.t_arrival for m in e.members) - e.t0}
        self._log({"type": "event", "id": e.id, "t": self.now, "t0": e.t0, "case": case, "members": M,
                   "touched": touched, "observable": {g: v for g, v in sorted(obs_cache.items())}, **spans})
        flows = set(M)
        for n in touched:
            if n in self.nodes:
                flows |= self.nodes[n].members | self.nodes[n].candidates
        self._transitions(e, sorted(flows))
        self._dissolve(e)
        self.last_observable = dict(obs_cache)
        for cb in self.on_event_closed:
            cb(self, e, case)

    def _match(self, e, M, mem, touched, info, observable) -> str:
        cfg = self.cfg
        # Leaves that share flows are competing hypotheses for the same flows, not
        # a hierarchy. Among covered leaves keep the better supported one of any
        # overlapping pair (confirmed first, then support); the loser gets nothing.
        # Overlap is judged on members plus unassigned candidates: a member of A
        # that is a candidate of B is a possible migration, not two hypotheses.
        hyp = {n: self._hypothesis(n) for n in touched}
        # A leaf with a single observable flow cannot be "covered": one flow
        # firing is not evidence about a group (coincidence pairs would otherwise
        # be covered whenever their other flow is idle or in an episode).
        covered = []
        for n in sorted((n for n in touched if info[n][3] >= cfg.theta_cov and len(info[n][1]) >= 2),
                        key=lambda n: (not self.nodes[n].confirmed, -self.nodes[n].support, n)):
            if not any(hyp[n] & hyp[k] for k in covered):
                covered.append(n)
        covered.sort()
        # Case B is tested first: an aggregation event with one missed flow would
        # otherwise match the fully fired leaf as case A (J = 3/5) and turn the
        # other leaf's flows into its candidates.
        if len(covered) >= 2:
            return self._case_b(e, M, mem, covered, info, observable)
        A_cands = [n for n in touched if info[n][2] >= cfg.theta_J]
        if A_cands:
            n = max(A_cands, key=lambda n: (info[n][2], -n))
            self._apply_leaf(e, n, M, mem, info[n], observable, "A")
            return "A"
        if len(touched) == 1:
            n = touched[0]
            nset, nobs, J, cov = info[n]
            if cov == 1.0 and len(nobs) >= 2 and set(M) > set(nobs):
                self._apply_leaf(e, n, M, mem, info[n], observable, "A-superset")
                return "A-superset"
        if len(touched) == 1:
            n = touched[0]
            nset, nobs, J, cov = info[n]
            if set(M) < set(nobs):
                return self._case_c(e, n, M, mem, info[n], observable)
        self._case_d(e, M, mem, observable)
        return "D"

    def _apply_leaf(self, e, n, M, mem, inf, observable, case, add_extras: bool = True) -> None:
        """Positive evidence for fired members/candidates, extras become
        candidates, minority rule for silent members, negative evidence for
        silent candidates (when the group as a whole fired)."""
        node = self.nodes[n]
        nset, nobs, J, cov = inf
        fired_in = [f for f in M if f in node.members or f in node.candidates]
        extras = [f for f in M if f not in node.members and f not in node.candidates]
        ws = {f: self._w_pos(f, n, e, mem[f]) for f in M}
        if fired_in:
            self._add_support(n, sum(ws[f][0] for f in fired_in) / len(fired_in), e, case)
        for f in fired_in:
            if not observable(f):
                continue
            if f in node.members:
                self._add_L(f, ws[f][0], e, case, n, ws[f][1])
                self._update_lag(f, n, mem[f].t_al - e.t0)
            else:
                self._add_cand(f, n, ws[f][0], e, case, ws[f][1])
        for f in extras if add_extras else ():
            if observable(f):
                self._add_cand(f, n, ws[f][0], e, case, ws[f][1])
        k, m = len([f for f in M if f in nobs]), len(nobs)
        silent = [g for g in nobs if g not in mem]
        if k * 2 >= m:
            for g in silent:
                if g in node.members:
                    self._add_L(g, self._w_neg(g, e), e, case, n)
                else:
                    self._add_cand(g, n, self._w_neg(g, e), e, case)
        else:
            for f in fired_in:
                if f in node.members and observable(f):
                    self._add_L(f, 0.5 * self._w_neg(f, e), e, case + ":minority", n)
                    self.state[f].solo += 1
        if node.confirmed:
            out = ConfirmedShared(n, [f for f in M if f in node.members], [g for g in silent if g in node.members],
                                  sigmoid(min(min((self.state[f].L for f in node.members), default=0.0), self.A)),
                                  self.now, sorted({mem[f].track for f in M}))
            self.outputs.append(out)
            self._log({"type": "output", "kind": "CONFIRMED_SHARED", "t": self.now, "event_id": e.id, **out.__dict__})

    def _case_b(self, e, M, mem, covered, info, observable) -> str:
        # Leaves with fewer than two observable flows cannot vote on GLOBAL.
        all_leaves = [n.id for n in self.leaves() if (n.members or n.candidates)
                      and not (n.id in info and len(info[n.id][1]) < 2)]
        confirmed = [n for n in all_leaves if self.nodes[n].confirmed]
        cov_set = set(covered)
        is_global = (len(confirmed) >= 2 and set(confirmed) <= cov_set) or \
                    (len(all_leaves) >= 2 and set(all_leaves) <= cov_set)
        if is_global:
            w = sum(self._w_pos(f, ROOT, e, mem[f])[0] for f in M) / len(M)
            self._add_support(ROOT, w, e, "GLOBAL")
            self._log({"type": "tree", "op": "global", "t": self.now, "event_id": e.id, "covered": covered, "w": w})
            return "GLOBAL"
        P = self._lca(covered)
        pnode = self.nodes[P]
        others = [c for c in sorted(pnode.children) if c not in cov_set]
        silent_other = any(any(observable(g) and g not in mem for g in self._subtree_flows(c)) for c in others)
        if P == ROOT or silent_other:
            new = self._new_node("internal", P, e)
            olds = []
            for n in covered:
                old = self.nodes[n].parent
                self.nodes[old].children.discard(n)
                self.nodes[n].parent = new.id
                new.children.add(n)
                if old not in (P, new.id) and old not in olds:
                    olds.append(old)
            for old in olds:
                self._splice(old, e)
            pnode.sub_patterns[frozenset(M)] = pnode.sub_patterns.get(frozenset(M), 0.0)
            self._log({"type": "tree", "op": "new_internal", "t": self.now, "event_id": e.id, "node": new.id,
                       "parent": P, "children": covered})
            P, pnode = new.id, new
        w = sum(self._w_pos(f, P, e, mem[f])[0] for f in M) / len(M)
        self._add_support(P, w, e, "B")
        pnode.sub_patterns[frozenset(M)] = pnode.sub_patterns.get(frozenset(M), 0.0) + w
        inside = set()
        for n in covered:
            inside |= self.nodes[n].members | self.nodes[n].candidates
            self._apply_leaf(e, n, M, mem, info[n], observable, "B", add_extras=False)
        for f in M:
            if f not in inside and observable(f):
                wf, comps = self._w_pos(f, P, e, mem[f])
                self._add_cand(f, P, wf, e, "B", comps)
        return "B"

    def _case_c(self, e, n, M, mem, inf, observable) -> str:
        node = self.nodes[n]
        nset, nobs, J, cov = inf
        key = frozenset(M)
        ws = {f: self._w_pos(f, n, e, mem[f]) for f in M}
        w = sum(v[0] for v in ws.values()) / len(ws)
        node.sub_patterns[key] = node.sub_patterns.get(key, 0.0) + w
        node.n_events += 1
        for f in M:
            if not observable(f):
                continue
            if f in node.members:
                self._add_L(f, ws[f][0], e, "C", n, ws[f][1])
                self._update_lag(f, n, mem[f].t_al - e.t0)
            else:
                self._add_cand(f, n, ws[f][0], e, "C", ws[f][1])
        k, m = len([f for f in M if f in nobs]), len(nobs)
        if k * 2 >= m:
            for g in nobs:
                if g not in mem and g in node.members:
                    self._add_L(g, self._w_neg(g, e), e, "C", n)
        else:
            for f in M:
                if f in node.members and observable(f):
                    self._add_L(f, 0.5 * self._w_neg(f, e), e, "C:minority", n)
                    self.state[f].solo += 1
        if node.sub_patterns[key] >= self.cfg.s_split_weight:
            self._split(e, node, set(M))
        return "C"

    def _split(self, e: Event, node: Node, part: set[str]) -> None:
        a = self._new_node("leaf", node.id, e)
        b = self._new_node("leaf", node.id, e)
        a.members, b.members = node.members & part, node.members - part
        a.candidates, b.candidates = node.candidates & part, node.candidates - part
        a.support = node.sub_patterns.get(frozenset(part), 0.0)
        b.support = node.support
        for leaf in (a, b):
            for f in sorted(leaf.members):
                st = self.state[f]
                st.node = leaf.id
                if node.id in st.lag:
                    st.lag[leaf.id] = st.lag[node.id]
            for f in sorted(leaf.candidates):
                st = self.state[f]
                st.cand[leaf.id] = st.cand.pop(node.id)
            self._set_confirmed(leaf, e)
        node.kind, node.members, node.candidates, node.sub_patterns = "internal", set(), set(), {}
        self._log({"type": "tree", "op": "split", "t": self.now, "event_id": e.id, "node": node.id,
                   "a": {"id": a.id, "flows": self._nset(a)}, "b": {"id": b.id, "flows": self._nset(b)}})

    def _case_d(self, e, M, mem, observable) -> None:
        new = self._new_node("leaf", ROOT, e)
        ws = {f: self._w_pos(f, new.id, e, mem[f]) for f in M}
        self._add_support(new.id, sum(v[0] for v in ws.values()) / len(ws), e, "D")
        self._log({"type": "tree", "op": "new_leaf", "t": self.now, "event_id": e.id, "node": new.id, "flows": M})
        for f in M:
            if observable(f):
                self._add_cand(f, new.id, ws[f][0], e, "D", ws[f][1])

    def _solo(self, e: Event, f: str, touched: list[int], info: dict, observable) -> None:
        """A flow fired alone. Minority rule against each leaf it belongs to or
        is a candidate of: if the leaf has >= 2 other observable flows, f is the
        odd one out (0.5 * w_neg, solo); if it has exactly one, that silent flow
        gets w_neg (the only negative evidence a provisional pair can receive)."""
        st = self.state[f]
        if not observable(f):
            self._log({"type": "output", "kind": "PRIVATE", "t": self.now, "event_id": e.id, "flow": f,
                       "observable": False})
            return
        st.solo += 1
        for n in touched:
            node = self.nodes[n]
            nset, nobs, J, cov = info[n]
            silent = [g for g in nobs if g != f]
            if len(silent) >= 2:
                if f in node.members:
                    self._add_L(f, 0.5 * self._w_neg(f, e), e, "SOLO", n)
            else:
                for g in silent:
                    if g in node.members:
                        self._add_L(g, self._w_neg(g, e), e, "SOLO", n)
                    else:
                        self._add_cand(g, n, self._w_neg(g, e), e, "SOLO")
        self.outputs.append(Private(f, e.t0))
        self._log({"type": "output", "kind": "PRIVATE", "t": self.now, "event_id": e.id, "flow": f, "observable": True})

    # ── transitions / dissolution / decay ────────────────────────────────

    def _transitions(self, e: Event, flows: Iterable[str]) -> None:
        for f in flows:
            st = self.state[f]
            for n in [k for k in st.cand if k not in self.nodes]:
                del st.cand[n]
            leaf_cands = {n: v for n, v in st.cand.items() if self.nodes[n].kind == "leaf"}
            best = max(leaf_cands, key=lambda n: (leaf_cands[n], -n)) if leaf_cands else None
            if best is not None and leaf_cands[best] >= self.A and leaf_cands[best] > st.L:
                self._move(e, f, best, leaf_cands[best])
            elif st.node is not None and st.L <= self.B:
                old = st.node
                self.nodes[old].members.discard(f)
                st.node, st.L = None, 0.0
                self._log({"type": "tree", "op": "leave", "t": self.now, "event_id": e.id, "flow": f, "node": old})

    def _move(self, e: Event, f: str, n: int, value: float) -> None:
        st = self.state[f]
        old = st.node
        if old is not None:
            self.nodes[old].members.discard(f)
        for k in list(st.cand):
            self.nodes[k].candidates.discard(f)
        st.cand = {}
        st.node, st.L, st.together, st.apart = n, value, 0.0, 0.0
        self.nodes[n].members.add(f)
        self._log({"type": "tree", "op": "move", "t": self.now, "event_id": e.id, "flow": f, "from": old,
                   "to": n, "L": value})

    def _dissolve(self, e: Event | None, candidates: Iterable[int] | None = None) -> None:
        ids = sorted(candidates) if candidates is not None else sorted(self.nodes)
        for n in ids:
            node = self.nodes.get(n)
            if node is None or node.kind != "leaf":
                continue
            if node.support < self.cfg.dissolve_support or len(node.members | node.candidates) < 2:
                for f in sorted(node.members):
                    self.state[f].node, self.state[f].L = None, 0.0
                    self.last_dissolved.append(f)
                for f in sorted(node.candidates):
                    self.state[f].cand.pop(n, None)
                    self.last_dissolved.append(f)
                parent = node.parent
                self.nodes[parent].children.discard(n)
                del self.nodes[n]
                self._log({"type": "tree", "op": "dissolve", "t": self.now, "event_id": e.id if e else None,
                           "node": n, "flows": sorted(node.members | node.candidates)})
                self._splice(parent, e)

    def _splice(self, n: int, e: Event | None) -> None:
        node = self.nodes.get(n)
        while node is not None and node.kind == "internal" and len(node.children) < 2:
            parent = node.parent
            for c in sorted(node.children):
                self.nodes[c].parent = parent
                self.nodes[parent].children.add(c)
            self.nodes[parent].children.discard(n)
            for f, st in sorted(self.state.items()):
                if st.cand.pop(n, None) is not None:
                    self.last_dissolved.append(f)
            del self.nodes[n]
            self._log({"type": "tree", "op": "splice", "t": self.now, "event_id": e.id if e else None, "node": n})
            n, node = parent, self.nodes.get(parent)

    def _decay(self, t: float) -> None:
        k = math.exp(-self.cfg.decay_period / self.cfg.tau)
        for f in sorted(self.state):
            st = self.state[f]
            st.L *= k
            st.solo *= k
            st.together *= k
            st.apart *= k
            for n in list(st.cand):
                st.cand[n] *= k
        for n in sorted(self.nodes):
            node = self.nodes[n]
            node.support *= k
            for key in node.sub_patterns:
                node.sub_patterns[key] *= k
            self._set_confirmed(node, None)
        self._log({"type": "decay", "t": t, "factor": k})
        self._dissolve(None)
        for cb in self.on_decay:
            cb(self)

    # ── queries ──────────────────────────────────────────────────────────

    def conf(self, L: float) -> float:
        return sigmoid(min(L, self.A))

    def query(self, f: str) -> dict:
        st = self.state.get(f)
        if st is None or st.node is None:
            return {"status": "UNCERTAIN"}
        node = self.nodes[st.node]
        tot = st.solo + st.together
        return {"status": "MEMBER" if st.L >= self.A else "UNCERTAIN", "leaf": st.node, "L": st.L,
                "conf": self.conf(st.L), "private_fraction": st.solo / tot if tot else 0.0,
                "ancestors": [(a, self.nodes[a].support) for a in self._ancestors(st.node)],
                "peers": sorted(node.members - {f})}

    def query_pair(self, f: str, g: str) -> dict:
        a, b = self.state.get(f), self.state.get(g)
        if a is None or b is None or a.node is None or b.node is None or a.L < self.A or b.L < self.A:
            return {"status": "UNCERTAIN"}
        lca = self._lca([a.node, b.node])
        level = 0 if a.node == b.node else max(self._ancestors(a.node).index(lca),
                                                self._ancestors(b.node).index(lca)) + 1
        return {"status": "SAME" if level == 0 else "DIFFERENT", "lca": lca,
                "conf": min(self.conf(a.L), self.conf(b.L)), "level": level}

    def snapshot(self) -> dict:
        """Per-flow (node, L, cand) and tree summary; for tools and tests."""
        return {"t": self.now,
                "flows": {f: {"node": st.node, "L": st.L, "cand": dict(sorted(st.cand.items())),
                              "solo": st.solo, "together": st.together, "apart": st.apart}
                          for f, st in sorted(self.state.items())},
                "nodes": {n: {"kind": x.kind, "parent": x.parent, "members": sorted(x.members),
                              "candidates": sorted(x.candidates), "children": sorted(x.children),
                              "support": x.support, "confirmed": x.confirmed}
                          for n, x in sorted(self.nodes.items())}}


class JsonlLogger:
    """Deterministic JSONL writer: sorted keys, rounded floats."""

    def __init__(self, path):
        self.f = open(path, "w")

    def __call__(self, rec: dict) -> None:
        self.f.write(json.dumps(_round(rec), sort_keys=True) + "\n")

    def close(self) -> None:
        self.f.close()


def _round(x):
    if isinstance(x, float):
        return round(x, 6)
    if isinstance(x, dict):
        return {str(k): _round(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set, frozenset)):
        return [_round(v) for v in (sorted(x) if isinstance(x, (set, frozenset)) else x)]
    return x
