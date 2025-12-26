from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from ..types import Observation, VariantId, Weights


@dataclass(frozen=True, slots=True)
class StrategyResult:
    proposed_weights: Weights
    explanation: Mapping[str, object]


class Strategy:
    name: str

    def propose(
        self,
        observations: Mapping[VariantId, Observation],
        *,
        seed: int | None = None,
    ) -> StrategyResult:
        raise NotImplementedError
