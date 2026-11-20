"""NPR (noisy partition refinement), cross-event layer, with the acceptance test as corrected by the user on
2026-11-18 (the first run's test is kept in npr_v1.py).

Model: every client belongs to one leaf; in an event a leaf is on or off; a non-NA member of an on leaf has x = 1
with probability 1 - m, of an off leaf with probability f. Input: the client x event matrix X (1 / 0 / NA).

Likelihoods of the full member vector of an event (no binomial coefficients; NA members left out):
  one leaf     P0(x_e) = pi (1-m0)^k m0^(n-k) + (1-pi) f0^k (1-f0)^(n-k)
  two leaves   P1(x_e) = sum over s in {00, 01, 10, 11} of pi_s prod_h [s_h = 1: (1-m1)^k_h m1^(n_h-k_h);
                                                                       s_h = 0: f1^k_h (1-f1)^(n_h-k_h)]
Each hypothesis has its own nuisance parameters:
  - alternative, for event t: the split, pi_s (+0.5 per state), m1, f1 (+0.5 smoothing; FLAG) fitted on events
    1..t-1 only; the first event of a group (no prefix) contributes factor 1 to the ratio (FLAG); a prefix with no
    split proposal uses the prefix's one-leaf fit as the predictive (FLAG);
  - null: (pi, m0, f0) = the maximum-likelihood fit of the one-leaf model on events 1..t, by EM from N_STARTS starts
    (m0 near 0.5 and near 0.05 among them); the best start is kept and reported.
E(t) = prod_{e<=t} P1(x_e; fit from e-1) / prod_{e<=t} P0(x_e; MLE at t). Accept at E >= 1 / alpha; groups tested
at one recursion level of one read: e-BH at alpha (FLAG). No pooled m, f across hypotheses.

Split proposal (procedure b, part of the alternative's own fit): e* = the event with k / n closest to 0.5 (n >= 2,
earliest on ties); g1 = members with 1 in e*, g2 = the rest (NA members start in g2; FLAG). Then at most 10 rounds:
m1, f1 from the two halves' majority profiles (z = 1 iff at least half of the non-NA members have 1), each client to
the half with the higher S_i(h) = sum over its non-NA events with z defined of x z log(1-m1) + (1-x) z log m1
+ x (1-z) log f1 + (1-x)(1-z) log(1-f1); ties to the half whose smallest client index is smaller (FLAG).
Reported groups: every node of the tree with >= 2 members, the root included (the k = 1 counterpart).
Variants: "bin" (as above), "na0" (NA treated as 0).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from scipy.special import logsumexp

ROUNDS = 10                 # (T) the note's iteration cap
PI_PRIOR = 0.5              # (FLAG) per-state pseudo-count of pi_s
RATE_PRIOR = 0.5            # (FLAG) pseudo-count for m1, f1
EPS = 1e-6                  # numerical floor for probabilities
EM_STARTS = ((0.5, 0.05, 0.05), (0.5, 0.5, 0.05), (0.3, 0.2, 0.2), (0.7, 0.05, 0.3), (0.5, 0.3, 0.01))   # (pi, m0, f0)
EM_ITERS, EM_TOL = 300, 1e-10


def _lp_on(k, n, m):
    return k * math.log(1 - m) + (n - k) * math.log(m)


def _lp_off(k, n, f):
    return k * math.log(f) + (n - k) * math.log(1 - f)


def profile(X: np.ndarray) -> np.ndarray:
    n = np.sum(~np.isnan(X), axis=0)
    k = np.nansum(X, axis=0)
    return np.where(n > 0, (k >= n / 2).astype(float), np.nan)


def half_rates(X: np.ndarray, masks) -> tuple[float, float]:
    """m1, f1 from the halves' majority profiles, +RATE_PRIOR smoothing."""
    mm = mn = ff = fn = 0.0
    for msk in masks:
        Xh = X[msk]
        z = profile(Xh)
        ok = ~np.isnan(Xh)
        on, off = z == 1, z == 0
        mm += np.sum((Xh == 0) & on[None, :])
        mn += np.sum(ok & on[None, :])
        ff += np.sum((Xh == 1) & off[None, :])
        fn += np.sum(ok & off[None, :])
    m = (mm + RATE_PRIOR) / (mn + 2 * RATE_PRIOR)
    f = (ff + RATE_PRIOR) / (fn + 2 * RATE_PRIOR)
    return float(np.clip(m, EPS, 1 - EPS)), float(np.clip(f, EPS, 1 - EPS))


def _scores(X, z, m, f):
    lm, l1m, lf, l1f = math.log(m), math.log1p(-m), math.log(f), math.log1p(-f)
    zz, ok = np.nan_to_num(z), ~np.isnan(z)
    a = np.where(ok, l1m * zz + lf * (1 - zz), 0.0)
    b = np.where(ok, lm * zz + l1f * (1 - zz), 0.0)
    return np.nan_to_num(X == 1).astype(float) @ a + (X == 0).astype(float) @ b


def propose(X: np.ndarray):
    """(mask of g1, m1, f1) or None."""
    n = np.sum(~np.isnan(X), axis=0)
    k = np.nansum(X, axis=0)
    ok = n >= 2
    if not ok.any():
        return None
    e = int(np.argmin(np.where(ok, np.abs(k / np.maximum(n, 1) - 0.5), np.inf)))
    g1 = X[:, e] == 1
    if g1.all() or not g1.any():
        return None
    for _ in range(ROUNDS):
        m, f = half_rates(X, (g1, ~g1))
        s1, s2 = _scores(X, profile(X[g1]), m, f), _scores(X, profile(X[~g1]), m, f)
        first1 = np.flatnonzero(g1)[0] < np.flatnonzero(~g1)[0]
        new = np.where(s1 == s2, first1, s1 > s2)
        if new.all() or not new.any():
            return None
        if np.array_equal(new, g1):
            break
        g1 = new
    m, f = half_rates(X, (g1, ~g1))
    return g1, m, f


def em_null(k: np.ndarray, n: np.ndarray):
    """MLE of (pi, m0, f0) of the one-leaf mixture by EM from EM_STARTS; returns (loglik, params, start index)."""
    best = (-np.inf, None, None)
    for si, (pi, m, f) in enumerate(EM_STARTS):
        prev = -np.inf
        for _ in range(EM_ITERS):
            lon = math.log(pi) + k * math.log(1 - m) + (n - k) * math.log(m)
            loff = math.log1p(-pi) + k * math.log(f) + (n - k) * math.log1p(-f)
            tot = np.logaddexp(lon, loff)
            ll = float(np.sum(tot))
            r = np.exp(lon - tot)
            pi = float(np.clip(r.mean(), EPS, 1 - EPS))
            m = float(np.clip(np.sum(r * (n - k)) / max(np.sum(r * n), EPS), EPS, 1 - EPS))
            f = float(np.clip(np.sum((1 - r) * k) / max(np.sum((1 - r) * n), EPS), EPS, 1 - EPS))
            if ll - prev < EM_TOL:
                break
            prev = ll
        lon = math.log(pi) + k * math.log(1 - m) + (n - k) * math.log(m)
        loff = math.log1p(-pi) + k * math.log(f) + (n - k) * math.log1p(-f)
        ll = float(np.sum(np.logaddexp(lon, loff)))
        if ll > best[0]:
            best = (ll, (pi, m, f), si)
    return best


def pi_states(X1, X2) -> dict:
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
    clients: list[str]
    variant: str = "bin"
    X: list = field(default_factory=list)
    cache: dict = field(default_factory=dict)        # (group, e) -> log predictive factor of the alternative
    em_starts: list = field(default_factory=list)    # winning EM start per null fit (reported)

    def add(self, col: np.ndarray) -> None:
        if self.variant == "na0":
            col = np.nan_to_num(col, nan=0.0)
        self.X.append(col.astype(float))

    def _mat(self, rows, upto):
        return np.array([c[rows] for c in self.X[:upto]]).T if upto else np.zeros((len(rows), 0))

    def _alt_factor(self, g: tuple, e: int):
        """log P1(x_e | alternative fitted on the group's events before e); None for the group's first event."""
        key = (g, e)
        if key in self.cache:
            return self.cache[key]
        rows = np.array(g)
        xe = self.X[e][rows]
        ok = ~np.isnan(xe)
        pre = self._mat(rows, e)
        keep = np.sum(~np.isnan(pre), axis=0) > 0
        pre = pre[:, keep]
        val = None
        if ok.any() and pre.shape[1]:
            prop = propose(pre)
            if prop is None:
                kk, nn = np.nansum(pre, axis=0), np.sum(~np.isnan(pre), axis=0)
                _, (pi, m, f), _ = em_null(kk, nn)
                k, n = float(np.nansum(xe)), float(ok.sum())
                val = float(np.logaddexp(math.log(pi) + _lp_on(k, n, m), math.log1p(-pi) + _lp_off(k, n, f)))
            else:
                split, m1, f1 = prop
                pis = pi_states(pre[split], pre[~split])
                terms = []
                parts = [(xe[split], ), (xe[~split], )]
                kn = [(float(np.nansum(p[0])), float(np.sum(~np.isnan(p[0])))) for p in parts]
                for (s1, s2), w in pis.items():
                    t = math.log(w)
                    for (k, n), s in zip(kn, (s1, s2)):
                        if n:
                            t += _lp_on(k, n, m1) if s else _lp_off(k, n, f1)
                    terms.append(t)
                val = float(logsumexp(terms))
        self.cache[key] = val
        return val

    def evalue(self, g: tuple, T: int) -> float:
        rows = np.array(g)
        num, ks, ns, first = 0.0, [], [], True
        for e in range(T):
            xe = self.X[e][rows]
            if not (~np.isnan(xe)).any():
                continue
            fac = self._alt_factor(g, e)
            if first or fac is None:
                first = False
                continue                       # the group's first event: factor 1 (both sides left out)
            num += fac
            ks.append(float(np.nansum(xe)))
            ns.append(float(np.sum(~np.isnan(xe))))
        if not ks:
            return 1.0
        ll0, _, si = em_null(np.array(ks), np.array(ns))
        self.em_starts.append(si)
        return math.exp(min(700.0, num - ll0))

    def read(self, alphas=(0.05,)) -> dict:
        T = len(self.X)
        ever = np.flatnonzero(np.nansum(np.array(self.X), axis=0) > 0) if T else np.array([], int)
        root = tuple(int(i) for i in ever)
        out, e_root = {}, None
        evals: dict = {}
        for a in alphas:
            nodes = [root] if len(root) >= 2 else []
            level = list(nodes)
            while level:
                tests = []
                for g in level:
                    if g not in evals:
                        evals[g] = self.evalue(g, T)
                    tests.append((g, evals[g]))
                    if g == root:
                        e_root = evals[g]
                K = len(tests)
                order = sorted(tests, key=lambda z: -z[1])
                kstar = max((i + 1 for i, (_, E) in enumerate(order) if E >= K / (a * (i + 1))), default=0)
                nxt = []
                for g, _ in order[:kstar]:
                    prop = propose(self._mat(np.array(g), T))
                    if prop is None:
                        continue
                    split = prop[0]
                    for h in (tuple(x for x, s in zip(g, split) if s), tuple(x for x, s in zip(g, split) if not s)):
                        if len(h) >= 2:
                            nodes.append(h)
                            nxt.append(h)
                level = nxt
            out[a] = [tuple(self.clients[i] for i in g) for g in nodes]
        return {"groups": out, "E_root": e_root}
