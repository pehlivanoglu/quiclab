"""Shared-bottleneck grouping from per-flow congestion onsets.
ECG (Event Co-occurrence Grouping, v1.2, frozen as a comparison method) and SETS (v1, frozen 2026-11-15:
grouping/FREEZE-sets-v1.md), which reuses ECG's event formation."""

from .config import Config
from .engine import Engine
from .sets_engine import SetsEngine
from .types import FlowMeta, ObsSample, Onset

__all__ = ["Config", "Engine", "FlowMeta", "ObsSample", "Onset", "SetsEngine"]
