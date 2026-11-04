"""ECG configuration (brief v1.1 §7). Every default is overridable from a dict
or a JSON file; derived values (delta_max, sigma_min, L_cap) follow delta / A
unless set explicitly."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path


@dataclass
class Config:
    delta: float = 0.300            # onset co-occurrence tolerance on aligned time (s)
    delta_max: float | None = None  # max event span; default 2*delta
    hold: float = 1.0               # wall-clock hold after t0 + delta_max for late detectors (s)
    align_mode: str = "half_mrtt"   # half_mrtt | none | table
    align_table: dict[str, float] = field(default_factory=dict)
    obs_mode: str = "sent_rate"     # producer-side: sent_rate | cwnd
    obs_fraction: float = 0.5       # producer-side: share of rendition over 200 ms
    theta_J: float = 0.7
    theta_cov: float = 0.7
    s_split_weight: float = 8.0
    alpha_err: float = 0.01
    beta_err: float = 0.05
    p_det: float = 0.8
    p_fa_floor: float = 0.03
    lambda_init: float = 0.02
    lambda_tau: float = 60.0
    tau: float = 300.0
    decay_period: float = 10.0
    sigma_min: float | None = None  # default delta/2
    k_cand: int = 3
    obs_window: float = 0.020
    L_cap: float | None = None      # ceiling on L and cand; default 2*A (see README: migration)
    w_cap_frac: float = 0.55        # per-event positive cap as a fraction of A (README: why not 1/2)
    dissolve_support: float = 0.5
    seed: int = 0
    enable_priming: bool = False    # Phase 2: must be False
    enable_slow_path: bool = False  # Phase 4: must be False

    def __post_init__(self) -> None:
        if self.delta_max is None:
            self.delta_max = 2 * self.delta
        if self.sigma_min is None:
            self.sigma_min = self.delta / 2
        if self.enable_priming or self.enable_slow_path:
            raise ValueError("priming / slow path are later phases and must stay disabled")
        if self.align_mode not in ("half_mrtt", "none", "table"):
            raise ValueError(f"align_mode {self.align_mode!r}")

    @property
    def A(self) -> float:
        return math.log((1 - self.beta_err) / self.alpha_err)

    @property
    def B(self) -> float:
        return math.log(self.beta_err / (1 - self.alpha_err))

    @property
    def l_cap(self) -> float:
        return self.L_cap if self.L_cap is not None else 2 * self.A

    @classmethod
    def from_dict(cls, d: dict) -> "Config":
        names = {f.name for f in fields(cls)}
        unknown = sorted(set(d) - names)
        if unknown:
            raise KeyError(f"unknown config keys: {unknown}")
        return cls(**d)

    @classmethod
    def from_json(cls, path: str | Path) -> "Config":
        return cls.from_dict(json.loads(Path(path).read_text()))

    def to_dict(self) -> dict:
        return asdict(self)

    def replace(self, **kw) -> "Config":
        d = self.to_dict()
        # Derived fields follow the new delta / A unless the caller sets them.
        for k in ("delta_max", "sigma_min"):
            if "delta" in kw and k not in kw:
                d[k] = None
        d.update(kw)
        return Config.from_dict(d)
