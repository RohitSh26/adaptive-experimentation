from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .types import AllocationResult, Constraints, Observation, VariantId


@dataclass(frozen=True, slots=True)
class Engine:
    """
    Computes new traffic allocation weights for adaptive experimentation.

    This class is intentionally stateless and infrastructure-agnostic.
    """
    strategy: str = "heuristic"

    def compute(
        self,
        *,
        observations: Mapping[VariantId, Observation],
        previous_weights: Mapping[VariantId, float],
        constraints: Constraints | None = None,
        last_updated_at_epoch_s: int | None = None,
        now_epoch_s: int | None = None,
    ) -> AllocationResult:
        """
        Compute new weights based on observations, prior weights, and guardrails.

        Note: Implementation intentionally deferred. Epic #3 will implement a minimal strategy.
        """
        if constraints is None:
            constraints = Constraints()

        raise NotImplementedError(
            "Engine.compute is not implemented yet (design skeleton)."
        )