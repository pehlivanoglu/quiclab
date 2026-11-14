"""Synthetic onset-log generator and the six named scenarios (brief v1.1 §8).

A scenario is a resource tree, flows attached to access links (optionally a
private resource), per-resource stimulus schedules and a detection-delay
profile. The generator yields the records an onset log holds (meta, obs,
onset) in feed order, plus a ground-truth dict."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Iterator

import numpy as np

from .config import Config
from .types import FlowMeta, ObsSample, Onset

OBS_WINDOW = 0.020
TRAIL_S = 0.2          # observability: bytes sent over the trailing 200 ms
P_MISS = 0.1
EPISODE_S = (0.3, 1.0)
NOISE_RATE = 0.02
NOISY_RATE = 0.2
DURATION = 300.0


@dataclass(frozen=True)
class Profile:
    name: str
    d_min: float
    d_max: float
    sigma_arr: float
    sigma_onset: float
    config: dict = field(default_factory=dict)   # engine config overrides suited to the profile
    onset_tail: tuple[float, float] = (0.0, 0.0)  # (probability, sigma s): heavy tail of the onset error


PROFILES = {
    "ideal": Profile("ideal", 0.0, 0.0, 0.008, 0.008, {"delta": 0.03, "hold": 0.1}),
    # Onset error fitted (2026-11-11) to the measured same-group onset spread of the
    # v2-owd detector on the development set (|pair difference| p50 33 ms, p90 132 ms;
    # reports/grouping-episode): 84 % N(0, 26 ms), 16 % N(0, 130 ms) -> p50 33, p90 130.
    "realistic": Profile("realistic", 0.1, 0.5, 0.15, 0.026, {}, (0.16, 0.13)),
    # The profile used until 2026-11-11 (N(0, 60 ms): p50 57, p90 139 ms); kept to show
    # the limit of delta = 150 ms (grouping/README.md, "Synthetic profiles").
    "wide": Profile("wide", 0.1, 0.5, 0.15, 0.06, {}),
    "exact": Profile("exact", 0.0, 0.0, 0.0, 0.0, {"delta": 0.03, "hold": 0.1}),   # tests only
}


@dataclass
class FlowSpec:
    name: str
    access: str
    mrtt: float
    rendition: float
    ecn: bool = False
    private: str | None = None
    activity: list[tuple[float, float]] = field(default_factory=lambda: [(0.0, DURATION)])
    noise: float = NOISE_RATE
    migrate: tuple[float, str] | None = None   # (t, new access link)

    def access_at(self, t: float) -> str:
        if self.migrate and t >= self.migrate[0]:
            return self.migrate[1]
        return self.access

    def active_overlap(self, lo: float, hi: float) -> float:
        return sum(max(0.0, min(hi, b) - max(lo, a)) for a, b in self.activity)

    def sending(self, t: float) -> bool:
        return any(a <= t < b for a, b in self.activity)


@dataclass
class Scenario:
    id: str
    resources: dict[str, str | None]          # resource -> parent (None = top)
    flows: list[FlowSpec]
    stimuli: Callable[[np.random.Generator], dict[str, list[float]]]
    tracks: dict[str, str] = field(default_factory=dict)
    duration: float = DURATION
    note: str = ""

    def ancestors(self, res: str) -> list[str]:
        out = []
        while res is not None:
            out.append(res)
            res = self.resources[res]
        return out


# ── generator ────────────────────────────────────────────────────────────

def generate(sc: Scenario, profile: Profile, seed: int, p_miss: float = P_MISS) -> tuple[list, dict]:
    """Records in feed order: ("meta", t, FlowMeta) | ("obs", t, ObsSample) |
    ("onset", t, Onset), sorted by t with obs before onsets at equal t."""
    rng = np.random.default_rng(seed)
    flows = {f.name: f for f in sc.flows}
    rmax = max(f.rendition for f in sc.flows)
    d_f = {}
    for f in sc.flows:
        u = rng.uniform(profile.d_min, profile.d_max)
        # Higher renditions give more ACKs per RTT, hence earlier detection.
        d_f[f.name] = float(np.clip(u * (0.5 + 0.5 * (1 - f.rendition / rmax)), profile.d_min, profile.d_max))
    stim = sc.stimuli(rng)
    cands: list[tuple[float, str, str]] = []            # (T, flow, cause)
    for res, times in sorted(stim.items()):
        for T in times:
            for f in sc.flows:
                attached = res in sc.ancestors(f.access_at(T)) or res == f.private
                if attached:
                    cands.append((T, f.name, res))
    for f in sc.flows:
        if f.noise > 0:
            t = rng.exponential(1 / f.noise)
            while t < sc.duration:
                cands.append((t, f.name, "noise"))
                t += rng.exponential(1 / f.noise)
    cands.sort(key=lambda c: (c[0], c[1], c[2]))
    episodes: dict[str, list[tuple[float, float, str]]] = {f.name: [] for f in sc.flows}
    onsets: list[Onset] = []
    ep_end = {f.name: -1.0 for f in sc.flows}
    for T, name, cause in cands:
        f = flows[name]
        if T < ep_end[name] or not f.sending(T):
            continue
        if cause != "noise" and rng.uniform() < p_miss:
            continue
        t_true = T + f.mrtt / 2 + rng.uniform(0, 0.005)
        dur = rng.uniform(*EPISODE_S)
        ep_end[name] = t_true + dur
        episodes[name].append((t_true, t_true + dur, cause))
        p_tail, s_tail = profile.onset_tail
        wide = p_tail > 0 and rng.uniform() < p_tail   # no extra draw without a tail: other profiles keep their streams
        t_onset = t_true + rng.normal(0, s_tail if wide else profile.sigma_onset)
        t_arr = max(t_onset + 0.01, t_true + d_f[name] + rng.normal(0, profile.sigma_arr))
        track = sc.tracks.get(cause, "delay")
        mag = 1 + float(rng.lognormal(0.3, 0.3))
        onsets.append(Onset(name, t_onset, t_arr, track, mag))
    records: list = [("meta", 0.0, FlowMeta(f.name, f.mrtt, f.ecn, f.rendition)) for f in sc.flows]
    n_win = int(math.ceil(sc.duration / OBS_WINDOW))
    for f in sc.flows:
        eps = episodes[f.name]
        starts = np.array([a for a, _, _ in eps]) if eps else np.zeros(0)
        ends = np.array([b for _, b, _ in eps]) if eps else np.zeros(0)
        for i in range(n_win):
            t = round(i * OBS_WINDOW, 6)
            obs = f.active_overlap(t - TRAIL_S, t) >= 0.5 * TRAIL_S
            j = int(np.searchsorted(starts, t, side="right")) - 1
            in_ep = j >= 0 and t < ends[j]
            # observable = sending; the engine applies the in_episode condition at
            # t0 - delta itself (README: a fired flow is in_episode for half of its
            # own event window, so folding in_episode into observable breaks §4.3).
            records.append(("obs", t, ObsSample(f.name, t, bool(obs), bool(in_ep))))
    for o in onsets:
        records.append(("onset", o.t_arrival, o))
    order = {"meta": 0, "obs": 1, "onset": 2}
    records.sort(key=lambda r: (r[1], order[r[0]], r[2].flow))
    truth = {
        "scenario": sc.id, "profile": profile.name, "seed": seed, "duration": sc.duration,
        "resources": dict(sc.resources),
        "flows": {f.name: {"access": f.access, "access_end": f.access_at(sc.duration), "private": f.private,
                           "migrate": f.migrate, "mrtt": f.mrtt, "rendition": f.rendition,
                           "activity": f.activity, "noise": f.noise, "d_f": d_f[f.name]} for f in sc.flows},
        "stimuli": {k: [float(x) for x in v] for k, v in stim.items()},
        "episodes": {k: [(float(a), float(b), c) for a, b, c in v] for k, v in episodes.items()},
    }
    return records, truth


def same_access(truth: dict, f: str, g: str) -> bool:
    return truth["flows"][f]["access_end"] == truth["flows"][g]["access_end"]


def write_log(records: list, path) -> None:
    import json
    with open(path, "w") as fh:
        for kind, t, obj in records:
            fh.write(json.dumps({"kind": kind, **obj.__dict__}, sort_keys=True) + "\n")


def read_log(path) -> Iterator[tuple]:
    import json
    types = {"meta": FlowMeta, "obs": ObsSample, "onset": Onset}
    with open(path) as fh:
        for line in fh:
            d = json.loads(line)
            kind = d.pop("kind")
            obj = types[kind](**d)
            yield kind, (obj.t_arrival if kind == "onset" else getattr(obj, "t", 0.0)), obj


# ── stimulus schedules ───────────────────────────────────────────────────

def periodic(lo: float, hi: float, start: float = 10.0, end: float = DURATION):
    def gen(rng):
        out, t = [], start + rng.uniform(0, lo)
        while t < end:
            out.append(float(t))
            t += rng.uniform(lo, hi)
        return out
    return gen


def poisson(mean: float, start: float = 10.0, end: float = DURATION):
    def gen(rng):
        out, t = [], start + rng.exponential(mean)
        while t < end:
            out.append(float(t))
            t += rng.exponential(mean)
        return out
    return gen


def cycle(order: list[str], lo: float, hi: float, start: float = 10.0, end: float = DURATION):
    """Resources take turns in a fixed order with U(lo, hi) between stimuli."""
    def gen(rng):
        out = {r: [] for r in order}
        t, i = start, 0
        while t < end:
            out[order[i % len(order)]].append(float(t))
            t += rng.uniform(lo, hi)
            i += 1
        return out
    return gen


def combine(parts: dict[str, Callable]):
    def gen(rng):
        out = {}
        for res, g in sorted(parts.items()):
            out[res] = g(rng)
        return out
    return gen


# ── scenarios ────────────────────────────────────────────────────────────

def _three(prefix: str, access: str, start: int) -> list[FlowSpec]:
    rates = [1e6, 2.5e6, 5e6]
    return [FlowSpec(f"{prefix}{start + i}", access, 0.02 + 0.01 * i, rates[i]) for i in range(3)]


def s1() -> Scenario:
    return Scenario("S1", {"A": None}, _three("f", "A", 1), combine({"A": periodic(8, 12)}),
                    note="3 flows on one access link, stimuli every 8-12 s")


def s2() -> Scenario:
    return Scenario("S2", {"A": None, "B": None},
                    [FlowSpec("f1", "A", 0.02, 2.5e6), FlowSpec("f2", "B", 0.03, 2.5e6)],
                    combine({"A": poisson(10), "B": poisson(10)}),
                    note="2 flows on independent links, Poisson stimuli (mean 10 s)")


def s3() -> Scenario:
    flows = _three("f", "A", 1)
    flows[0].private = "P"
    return Scenario("S3", {"A": None, "P": None}, flows,
                    combine({"A": periodic(8, 12), "P": periodic(10, 15)}),
                    note="3 flows on one link; flow 1 also has a private resource (every 10-15 s)")


def s4() -> Scenario:
    return Scenario("S4", {"G": None, "A": "G", "B": "G"}, _three("f", "A", 1) + _three("f", "B", 4),
                    cycle(["A", "B", "G"], 8, 12),
                    note="2 access links x 3 flows under one aggregation link; stimuli cycle A / B / G")


def s5() -> Scenario:
    sc = s4()
    sc.id, sc.note = "S5", "S4 plus: f2 noisy (0.2 /s), f5 idle 100-200 s, f3 migrates A -> B at 150 s"
    by = {f.name: f for f in sc.flows}
    by["f2"].noise = NOISY_RATE
    by["f5"].activity = [(0.0, 100.0), (200.0, DURATION)]
    by["f3"].migrate = (150.0, "B")
    return sc


def s6() -> Scenario:
    res = {"R": None, "G1": "R", "G2": "R", "A1": "G1", "A2": "G1", "A3": "G2", "A4": "G2"}
    flows = []
    for i, a in enumerate(["A1", "A2", "A3", "A4"]):
        flows += _three("f", a, 1 + 3 * i)
    return Scenario("S6", res, flows, cycle(["A1", "A2", "A3", "A4", "G1", "G2", "R"], 5, 8),
                    note="4 access links under 2 aggregation links under one root link; stimuli cycle "
                         "A1 / A2 / A3 / A4 / G1 / G2 / R every 5-8 s")


SCENARIOS: dict[str, Callable[[], Scenario]] = {"S1": s1, "S2": s2, "S3": s3, "S4": s4, "S5": s5, "S6": s6}


def config_for(profile: Profile, base: Config | None = None, **overrides) -> Config:
    cfg = base or Config()
    return cfg.replace(**{**profile.config, **overrides})
