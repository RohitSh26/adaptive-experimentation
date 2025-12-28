from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .explanations import (
    AllocationExplanation,
    GuardrailExplanation,
    ObservationsSummary,
    StrategyExplanation,
)
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

        # Build typed explanation
        obs_summary = ObservationsSummary(
            num_variants=len(observations),
            total_trials=sum(o.trials for o in observations.values()),
            total_successes=sum(o.successes for o in observations.values()),
        )

        strategy_expl = StrategyExplanation(
            name=self.strategy,
            details=dict(strategy_result.explanation),
        )

        guardrails_expl = GuardrailExplanation(
            changed=bool(guardrail_expl.get("changed", True)),
            hold_reason=guardrail_expl.get("hold_reason"),
            guardrails_applied=tuple(
                guardrail_expl.get("guardrails_applied", ())),
            max_step_clamps=guardrail_expl.get("max_step_clamps"),
            min_weight_floors=guardrail_expl.get("min_weight_floors"),
        )

        explanation = AllocationExplanation(
            strategy=strategy_expl,
            observations=obs_summary,
            proposed_weights=dict(proposed),
            final_weights=dict(final_weights),
            guardrails=guardrails_expl,
        )

        return AllocationResult(weights=final_weights, explanation=explanation)
