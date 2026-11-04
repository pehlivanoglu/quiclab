"""Event Co-occurrence Grouping (ECG): shared-bottleneck grouping from per-flow
congestion onsets. Phase 1 (brief v1.1): engine, synthetic harness, replay."""

from .config import Config
from .engine import Engine
from .types import FlowMeta, ObsSample, Onset

__all__ = ["Config", "Engine", "FlowMeta", "ObsSample", "Onset"]
