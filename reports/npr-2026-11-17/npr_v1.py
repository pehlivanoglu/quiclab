# Frozen copy of the first NPR run (2026-11-17): pooled m, f from the untested candidate tree. Kept for D1.
"""NPR (noisy partition refinement), cross-event layer only (STEP 1 of the user's note, 2026-11-17).

Model: every client belongs to one leaf; in an event a leaf is on or off; a non-NA member of an on leaf has x = 1
with probability 1 - m, of an off leaf with probability f. State: the client x event matrix X only (1 / 0 / NA).

Read procedure at a read after event T (alpha (P)):
  a. G0 = the clients that ever had x = 1.
  b. Split proposal for a group g: the event e* where k / n over g is closest to 0.5 (earliest on ties); g1 = members
     with 1 in e*, g2 = the rest (members with 0, and NA members: FLAG). At most 10 rounds: profile z_h,e = 1 iff at
     least half of the non-NA members of h have 1 (undefined without a non-NA member); each client goes to the half
     with the higher S_i(h) = sum over its non-NA events with z defined of x z log(1-m) + (1-x) z log m
     + x (1-z) log f + (1-x)(1-z) log(1-f). Ties: the half whose smallest client index is smaller (FLAG). A half that
     empties: no split.
  c. Sequential split test: E(T) = prod_{e <= T} p1(x_e | split and pi_s fitted on events < e) / prod_{e <= T}
     p0(x_e | pi MLE on events <= T); p0 = pi B(k; n, 1-m) + (1-pi) B(k; n, f); p1 = sum over the four states of
     pi_s B(k1; n1, s1) B(k2; n2, s2). Events where g has no non-NA member are skipped. pi_s from the prefix's
     profile states with +0.5 per state (FLAG); before any split can be fitted p1 uses the prefix's one-leaf fit
     (factor ~ 1). m, f for the factor of event e: the values of the read after event e - 1 (FLAG: this makes
     every factor depend only on events < e, so it is computed once). Accept when E >= 1 / alpha; groups tested
     at the same recursion level of one read: e-BH at level alpha (FLAG: per level).
  d. Recurse on accepted halves. The tree's nodes with >= 2 members are the reported groups, the root included
     (the unsplit group is the k = 1 counterpart).
  e. m, f pooled over the groups with >= 3 members of the read's candidate tree (the recursive split proposals,
     untested; FLAG): m = (z = 1, x = 0) / (z = 1, x non-NA),
     f = (z = 0, x = 1) / (z = 0, x non-NA); clipped to [M_MIN, M_MAX] (FLAG) so the logs are finite.
Variants: "bin" (binomial), "bb" (beta-binomial with rho (P) from STEP 0b's method of moments), "na0" (NA as 0).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from scipy.special import betaln, gammaln, logsumexp

M_MIN, M_MAX = 0.001, 0.45   # (FLAG) clip for m and f
ROUNDS = 10                  # (T) the note's iteration cap
PI_PRIOR = 0.5               # (FLAG) per-state pseudo-count of pi_s
PI_GRID = np.linspace(0.001, 0.999, 999)


def _logbinom(k, n, p):
    return gammaln(n + 1) - gammaln(k + 1) - gammaln(n - k + 1) + k * np.log(p) + (n - k) * np.log1p(-p)


def _logbb(k, n, p, rho):
    if rho <= 1e-9:
        return _logbinom(k, n, p)
    a, b = p * (1 - rho) / rho, (1 - p) * (1 - rho) / rho
    return gammaln(n + 1) - gammaln(k + 1) - gammaln(n - k + 1) + betaln(k + a, n - k + b) - betaln(a, b)


@dataclass
class Params:
    m: float = 0.1
    f: float = 0.05
    rho: float = 0.0          # 0 = binomial

    def lb(self, k, n, on: bool):
        p = 1 - self.m if on else self.f
        return _logbb(k, n, p, self.rho) if self.rho > 0 else _logbinom(k, n, p)


def profile(X: np.ndarray) -> np.ndarray:
    """z per event over the rows of X (values 1 / 0 / nan): 1 / 0, nan when no row is non-NA."""
    n = np.sum(~np.isnan(X), axis=0)
    k = np.nansum(X, axis=0)
    return np.where(n > 0, (k >= n / 2).astype(float), np.nan)


def scores(X: np.ndarray, z: np.ndarray, p: Params) -> np.ndarray:
    lm, l1m, lf, l1f = math.log(p.m), math.log1p(-p.m), math.log(p.f), math.log1p(-p.f)
    zz = np.nan_to_num(z)
    ok = ~np.isnan(z)
    a = np.where(ok, l1m * zz + lf * (1 - zz), 0.0)       # x = 1
    b = np.where(ok, lm * zz + l1f * (1 - zz), 0.0)       # x = 0
    x1 = np.nan_to_num(X == 1).astype(float)
    x0 = (X == 0).astype(float)
    return x1 @ a + x0 @ b


def propose(X: np.ndarray, p: Params) -> np.ndarray | None:
    """Boolean mask of g1 over the rows of X, or None."""
    n = np.sum(~np.isnan(X), axis=0)
    k = np.nansum(X, axis=0)
    ok = n >= 2
    if not ok.any():
        return None
    r = np.where(ok, np.abs(k / np.maximum(n, 1) - 0.5), np.inf)
    e = int(np.argmin(r))
    g1 = X[:, e] == 1
    if g1.all() or not g1.any():
        return None
    for _ in range(ROUNDS):
        s1, s2 = scores(X, profile(X[g1]), p), scores(X, profile(X[~g1]), p)
        first1 = np.flatnonzero(g1)[0] < np.flatnonzero(~g1)[0]
        new = np.where(s1 == s2, first1, s1 > s2)
        if new.all() or not new.any():
            return None
        if np.array_equal(new, g1):
            break
        g1 = new
    return g1


def ll0(k, n, p: Params, pi_grid=PI_GRID):
    """Log-likelihood per pi on the grid, summed over events (arrays k, n)."""
    if len(k) == 0:
        return np.zeros(len(pi_grid))
    on = p.lb(k, n, True)
    off = p.lb(k, n, False)
    return np.array([np.sum(np.logaddexp(math.log(q) + on, math.log1p(-q) + off)) for q in pi_grid])


def ll1_event(k1, n1, k2, n2, pis, p: Params) -> float:
    terms = []
    for (s1, s2), w in pis.items():
        t = math.log(w)
        if n1:
            t += float(p.lb(k1, n1, s1))
        if n2:
            t += float(p.lb(k2, n2, s2))
        terms.append(t)
    return float(logsumexp(terms))


def pi_states(X1: np.ndarray, X2: np.ndarray) -> dict:
    z1, z2 = profile(X1), profile(X2)
    c = {(a, b): PI_PRIOR for a in (True, False) for b in (True, False)}
    for a, b in zip(z1, z2):
        if np.isnan(a) or np.isnan(b):
            continue
        c[(bool(a), bool(b))] += 1
    tot = sum(c.values())
    return {s: v / tot for s, v in c.items()}


@dataclass
class Reader:
    """Reads one run's growing X. clients: row order (index = id order for ties). events are appended in order."""
    clients: list[str]
    variant: str = "bin"
    rho: float = 0.0
    X: list = field(default_factory=list)              # per event: array over clients (1 / 0 / nan)
    pm: list = field(default_factory=list)              # (events seen at the read, Params after the read)
    cache: dict = field(default_factory=dict)          # (group, e) -> log p1 factor

    def add(self, col: np.ndarray) -> None:
        if self.variant == "na0":
            col = np.nan_to_num(col, nan=0.0)
        self.X.append(col.astype(float))

    def _mat(self, rows, upto):
        return np.array([c[rows] for c in self.X[:upto]]).T   # rows x events

    def _factor(self, g: tuple, e: int) -> float:
        key = (g, e)
        if key in self.cache:
            return self.cache[key]
        p = next((q for T, q in reversed(self.pm) if T <= e), Params(rho=self.rho))   # last read before event e
        rows = np.array(g)
        xe = self.X[e][rows]
        ok = ~np.isnan(xe)
        val = None
        if ok.any():
            pre = self._mat(rows, e) if e > 0 else np.zeros((len(rows), 0))
            split = propose(pre, p) if pre.shape[1] else None
            if split is None:
                # one-leaf predictive fit on the prefix (pi MLE), so the factor is ~1 against p0
                k, n = np.nansum(pre, axis=0), np.sum(~np.isnan(pre), axis=0)
                sel = n > 0
                q = PI_GRID[int(np.argmax(ll0(k[sel], n[sel], p)))] if sel.any() else 0.5
                kk, nn = float(np.nansum(xe)), float(ok.sum())
                val = float(np.logaddexp(math.log(q) + p.lb(kk, nn, True), math.log1p(-q) + p.lb(kk, nn, False)))
            else:
                pis = pi_states(pre[split], pre[~split])
                x1, x2 = xe[split], xe[~split]
                k1, n1 = float(np.nansum(x1)), float(np.sum(~np.isnan(x1)))
                k2, n2 = float(np.nansum(x2)), float(np.sum(~np.isnan(x2)))
                val = ll1_event(k1, n1, k2, n2, pis, p)
        self.cache[key] = val
        return val

    def evalue(self, g: tuple, T: int, p: Params) -> float:
        rows = np.array(g)
        num, ks, ns = 0.0, [], []
        for e in range(T):
            xe = self.X[e][rows]
            if not (~np.isnan(xe)).any():
                continue
            num += self._factor(g, e)
            ks.append(float(np.nansum(xe)))
            ns.append(float(np.sum(~np.isnan(xe))))
        if not ks:
            return 1.0
        den = float(np.max(ll0(np.array(ks), np.array(ns), p)))
        return math.exp(min(700.0, num - den))

    def estimate(self, groups: list[tuple], T: int) -> Params:
        mm = mn = ff = fn = 0.0
        big = [g for g in groups if len(g) >= 3]
        for g in big:
            Xg = self._mat(np.array(g), T)
            z = profile(Xg)
            for j in range(Xg.shape[1]):
                if np.isnan(z[j]):
                    continue
                col = Xg[:, j]
                okc = ~np.isnan(col)
                if z[j] == 1:
                    mm += np.sum(col[okc] == 0)
                    mn += okc.sum()
                else:
                    ff += np.sum(col[okc] == 1)
                    fn += okc.sum()
        m = mm / mn if mn else 0.1
        f = ff / fn if fn else 0.05
        return Params(m=float(np.clip(m, M_MIN, M_MAX)), f=float(np.clip(f, M_MIN, M_MAX)), rho=self.rho)

    def _candidate_leaves(self, root: tuple, T: int, p: Params, depth: int = 0) -> list[tuple]:
        if len(root) < 2 or depth > 20:
            return [root]
        split = propose(self._mat(np.array(root), T), p)
        if split is None:
            return [root]
        h1 = tuple(x for x, s in zip(root, split) if s)
        h2 = tuple(x for x, s in zip(root, split) if not s)
        return self._candidate_leaves(h1, T, p, depth + 1) + self._candidate_leaves(h2, T, p, depth + 1)

    def read(self, alphas=(0.05,)) -> dict:
        """Read after the last added event. Returns {alpha: [groups as tuples of client names]} and the root E."""
        T = len(self.X)
        p_prev = self.pm[-1][1] if self.pm else Params(rho=self.rho)
        ever = np.flatnonzero(np.nansum(np.array(self.X), axis=0) > 0) if T else np.array([], int)
        root = tuple(int(i) for i in ever)
        # m, f for this read: pooled over the groups (>= 3 members) of the candidate tree, i.e. the recursive
        # split proposals without any test (FLAG: estimating them on the unsplit group mixes leaves and inflates
        # m and f, which removes the test's power)
        cand = self._candidate_leaves(root, T, p_prev) if len(root) >= 2 else []
        p_prev = self.estimate(cand, T) if any(len(g) >= 3 for g in cand) else p_prev
        out, e_root = {}, None
        nodes_all = {}
        for a in alphas:
            nodes = [root] if len(root) >= 2 else []
            level = [root] if len(root) >= 2 else []
            while level:
                tests = []
                for g in level:
                    E = self.evalue(g, T, p_prev)
                    if g == root and e_root is None:
                        e_root = E
                    tests.append((g, E))
                # e-BH at level alpha over this recursion level
                K = len(tests)
                order = sorted(tests, key=lambda z: -z[1])
                kstar = max((i + 1 for i, (_, E) in enumerate(order) if E >= K / (a * (i + 1))), default=0)
                accepted = [g for g, _ in order[:kstar]]
                nxt = []
                for g in accepted:
                    split = propose(self._mat(np.array(g), T), p_prev)
                    if split is None:
                        continue
                    h1 = tuple(x for x, s in zip(g, split) if s)
                    h2 = tuple(x for x, s in zip(g, split) if not s)
                    for h in (h1, h2):
                        if len(h) >= 2:
                            nodes.append(h)
                            nxt.append(h)
                level = nxt
            nodes_all[a] = nodes
            out[a] = [tuple(self.clients[i] for i in g) for g in nodes]
        self.pm.append((T, p_prev))
        return {"groups": out, "E_root": e_root, "m": self.pm[-1][1].m, "f": self.pm[-1][1].f}
