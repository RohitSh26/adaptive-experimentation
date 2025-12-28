from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any

from .types import VariantId


@dataclass(frozen=True, slots=True)
class StrategyExplanation:
    """
    Strategy-specific explanation output.
    
    details keys vary by strategy:
    - heuristic: {"alpha": float, "seed_used": bool, ...}
    - thompson: {"priors": {...}, "posterior": {...}, "samples": {...}, "seed": int | None}
    """
    name: str
    details: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class ObservationsSummary:
    """
    Summary statistics about the observations provided.
    """
    num_variants: int
    total_trials: int
    total_successes: int


@dataclass(frozen=True, slots=True)
class GuardrailExplanation:
    """
    Explanation of guardrail application.
    """
    changed: bool
    hold_reason: str | None
    guardrails_applied: tuple[str, ...]
    max_step_clamps: Mapping[VariantId, Mapping[str, float]] | None = None
    min_weight_floors: Mapping[VariantId, Mapping[str, float]] | None = None


@dataclass(frozen=True, slots=True)
class AllocationExplanation:
    """
    Explanation of the allocation computation.
    """
    strategy: StrategyExplanation
    observations: ObservationsSummary
    proposed_weights: Mapping[VariantId, float]
    final_weights: Mapping[VariantId, float]
    guardrails: GuardrailExplanation

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
