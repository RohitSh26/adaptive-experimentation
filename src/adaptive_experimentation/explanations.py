from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any

from .types import VariantId


@dataclass(frozen=True, slots=True)
class StrategyExplanation:
    name: str
    details: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class ObservationsSummary:
    num_variants: int
    total_trials: int
    total_successes: int


@dataclass(frozen=True, slots=True)
class GuardrailExplanation:
    changed: bool
    hold_reason: str | None
    guardrails_applied: tuple[str, ...]
    max_step_clamps: Mapping[VariantId, Mapping[str, float]] | None = None
    min_weight_floors: Mapping[VariantId, Mapping[str, float]] | None = None


@dataclass(frozen=True, slots=True)
class AllocationExplanation:
    strategy: StrategyExplanation
    observations: ObservationsSummary
    proposed_weights: Mapping[VariantId, float]
    final_weights: Mapping[VariantId, float]
    guardrails: GuardrailExplanation

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
