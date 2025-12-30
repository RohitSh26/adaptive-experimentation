from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .explanations import AllocationExplanation

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

    @classmethod
    def safe_defaults(cls) -> Constraints:
        """Conservative, production-friendly defaults.

        Use when:
          - user/business risk is high
          - traffic is moderate and you want stability
          - you prefer holding rather than moving on early noise

        Behavior:
          - requires substantial evidence before shifting traffic
          - limits movement per window
          - maintains a minimum exposure for each variant
        """
        return cls(min_trials=2000, max_step=0.05, min_weight=0.02)

    @classmethod
    def neutral_defaults(cls) -> Constraints:
        """Balanced defaults (recommended starting point for most teams).

        Use when:
          - you want meaningful learning speed without being overly aggressive
          - you are comfortable with gradual traffic movement

        Behavior:
          - moderate evidence threshold
          - moderate movement per window
          - keeps exploration alive via a small minimum weight floor
        """
        return cls(min_trials=1000, max_step=0.10, min_weight=0.01)

    @classmethod
    def explore_defaults(cls) -> Constraints:
        """Faster-moving defaults, still guarded.

        Use when:
          - risk is low (pre-prod, internal tools, low-impact surfaces)
          - traffic is high (each window collects lots of trials)
          - you want to converge faster

        Behavior:
          - lower evidence threshold
          - larger movement per window
          - very small minimum exposure to avoid starvation
        """
        return cls(min_trials=300, max_step=0.20, min_weight=0.005)


@dataclass(frozen=True, slots=True)
class AllocationResult:
    weights: Mapping[VariantId, float]
    explanation: AllocationExplanation
