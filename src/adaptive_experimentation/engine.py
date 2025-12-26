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
        seed: int | None = None,
        last_updated_at_epoch_s: int | None = None,
        now_epoch_s: int | None = None,
    ) -> AllocationResult:
        """
        Compute new weights based on observations, prior weights, and guardrails.

        Note: Implementation intentionally deferred. Epic #3 will implement a minimal strategy.
        """
        if constraints is None:
            constraints = Constraints()

        # Validate inputs
        from .guardrails import apply_guardrails
        from .validation import validate_observations, validate_previous_weights

        validate_observations(observations)
        validate_previous_weights(
            previous_weights,
            observations=observations,
            epsilon=constraints.epsilon,
        )

        # Propose raw weights via selected strategy
        from .strategies.registry import get_strategy

        strategy = get_strategy(self.strategy)
        strategy_result = strategy.propose(observations, seed=seed)
        proposed = strategy_result.proposed_weights

        # Apply guardrails
        final_weights, guardrail_expl = apply_guardrails(
            observations=observations,
            previous_weights=previous_weights,
            proposed_weights=proposed,
            constraints=constraints,
        )

        explanation: dict[str, object] = {
            "strategy": self.strategy,
            "strategy_explanation": dict(strategy_result.explanation),
            "observations_summary": {
                "num_variants": len(observations),
                "total_trials": sum(o.trials for o in observations.values()),
                "total_successes": sum(o.successes for o in observations.values()),
            },
            "proposed_weights": dict(proposed),
        }
        explanation.update(guardrail_expl)

        return AllocationResult(weights=final_weights, explanation=explanation)
