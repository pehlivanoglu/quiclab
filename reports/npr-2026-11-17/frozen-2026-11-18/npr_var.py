"""Variants of the corrected NPR test (user, 2026-11-18), measured next to it; npr.py itself is unchanged.

V-A  bounded null: the null's EM fit restricted to m0 <= m_max and f0 <= f_max (projected EM: each M-step clipped to
     the bounds; FLAG), and the alternative's m1, f1 clipped to the same bounds.
V-B  past-fitted null: each event's P0(x_e) from the null's EM fit on the group's earlier events only. The
     universal-inference guarantee does NOT cover this variant (the denominator is not the null's maximum
     likelihood on the data being tested), so its false-split share is an empirical number only.
V-C  confidence tiers: the corrected test (and V-A) read with the acceptance threshold E >= 1 / alpha for alpha in
     TIER_ALPHAS (E >= 1, 2, 5, 20, 100); no new test.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

import npr

TIER_ALPHAS = (1.0, 0.5, 0.2, 0.1, 0.05, 0.01)   # E >= 1, 2, 5, 10, 20, 100 (0.1 and 0.01 are the sensitivity alphas)


def em_null_bounded(k, n, m_max, f_max):
    best = (-np.inf, None, None)
    for si, (pi, m, f) in enumerate(npr.EM_STARTS):
        m, f = min(m, m_max), min(f, f_max)
        prev = -np.inf
        for _ in range(npr.EM_ITERS):
            lon = math.log(pi) + k * math.log(1 - m) + (n - k) * math.log(m)
            loff = math.log1p(-pi) + k * math.log(f) + (n - k) * math.log1p(-f)
            tot = np.logaddexp(lon, loff)
            ll = float(np.sum(tot))
            r = np.exp(lon - tot)
            pi = float(np.clip(r.mean(), npr.EPS, 1 - npr.EPS))
            m = float(np.clip(np.sum(r * (n - k)) / max(np.sum(r * n), npr.EPS), npr.EPS, m_max))
            f = float(np.clip(np.sum((1 - r) * k) / max(np.sum((1 - r) * n), npr.EPS), npr.EPS, f_max))
            if ll - prev < npr.EM_TOL:
                break
            prev = ll
        lon = math.log(pi) + k * math.log(1 - m) + (n - k) * math.log(m)
        loff = math.log1p(-pi) + k * math.log(f) + (n - k) * math.log1p(-f)
        ll = float(np.sum(np.logaddexp(lon, loff)))
        if ll > best[0]:
            best = (ll, (pi, m, f), si)
    return best


@dataclass
class ReaderA(npr.Reader):
    m_max: float = 0.20
    f_max: float = 0.05

    def _alt_factor(self, g, e):
        key = (g, e)
        if key in self.cache:
            return self.cache[key]
        keep_hr, keep_em = npr.half_rates, npr.em_null
        mx, fx = self.m_max, self.f_max

        def hr(X, masks):
            m, f = keep_hr(X, masks)
            return min(m, mx), min(f, fx)
        npr.half_rates = hr
        npr.em_null = lambda k, n: em_null_bounded(k, n, mx, fx)
        try:
            return super()._alt_factor(g, e)
        finally:
            npr.half_rates, npr.em_null = keep_hr, keep_em

    def evalue(self, g, T):
        keep = npr.em_null
        npr.em_null = lambda k, n: em_null_bounded(k, n, self.m_max, self.f_max)
        try:
            return super().evalue(g, T)
        finally:
            npr.em_null = keep


@dataclass
class ReaderB(npr.Reader):
    def evalue(self, g, T):
        rows = np.array(g)
        num = den = 0.0
        ks, ns, first = [], [], True
        for e in range(T):
            xe = self.X[e][rows]
            if not (~np.isnan(xe)).any():
                continue
            fac = self._alt_factor(g, e)
            k, n = float(np.nansum(xe)), float(np.sum(~np.isnan(xe)))
            if first or fac is None:
                first = False
                ks.append(k), ns.append(n)
                continue
            _, (pi, m, f), si = npr.em_null(np.array(ks), np.array(ns))
            self.em_starts.append(si)
            den += float(np.logaddexp(math.log(pi) + npr._lp_on(k, n, m), math.log1p(-pi) + npr._lp_off(k, n, f)))
            num += fac
            ks.append(k), ns.append(n)
        return math.exp(min(700.0, num - den)) if ks else 1.0


def make(spec: str, clients):
    """spec: "corr" (the corrected test), "A-m0.20-f0.05", "B"."""
    if spec == "corr":
        return npr.Reader(clients)
    if spec == "B":
        return ReaderB(clients)
    if spec.startswith("A-"):
        _, m, f = spec.split("-")
        return ReaderA(clients, m_max=float(m[1:]), f_max=float(f[1:]))
    raise ValueError(spec)
