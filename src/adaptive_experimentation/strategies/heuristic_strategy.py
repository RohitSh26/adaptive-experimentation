from __future__ import annotations

from collections.abc import Mapping

from ..types import Observation, VariantId
from .base import Strategy, StrategyResult
from .heuristic import propose_weights


class HeuristicStrategy(Strategy):
    name = "heuristic"

    def propose(
        self,
        observations: Mapping[VariantId, Observation],
        *,
        seed: int | None = None,
    ) -> StrategyResult:
        weights = propose_weights(observations)
        return StrategyResult(
            proposed_weights=weights,
            explanation={"strategy": self.name, "alpha": 1.0, "seed_used": seed is not None},
        )
