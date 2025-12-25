from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

VariantId = str
Weights = dict[VariantId, float]


@dataclass(frozen=True, slots=True)
class Observation:
    """
    Aggregated binary-outcome observation for a variant.
    trials: number of opportunities (e.g., impressions)
    successes: number of positive outcomes (e.g., clicks)
    """
    trials: int
    successes: int


@dataclass(frozen=True, slots=True)
class Constraints:
    """
    Safe-by-default guardrails. See docs/guardrails.md for design intent.
    """
    min_weight: float = 0.05
    max_step: float = 0.10
    min_trials: int = 1000
    cooldown_seconds: int = 1800
    epsilon: float = 1e-9


@dataclass(frozen=True, slots=True)
class AllocationResult:
    weights: Weights
    explanation: Mapping[str, object]