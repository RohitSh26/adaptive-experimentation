from __future__ import annotations

from collections.abc import Mapping

from ..types import Observation, VariantId, Weights
from .base import Strategy, StrategyResult


def _rng(seed: int | None):
    # Keep dependencies minimal: use stdlib random.
    import random

    return random.Random(seed)


def _beta_sample(rng, alpha: float, beta: float) -> float:
    # random.Random has betavariate(alpha, beta)
    return float(rng.betavariate(alpha, beta))


class ThompsonStrategy(Strategy):
    """
    Thompson Sampling for binary outcomes using a Beta-Bernoulli model.

    Posterior:
      alpha = prior_success + successes
      beta  = prior_failure  + (trials - successes)

    Proposed weights are proportional to one posterior draw per variant.
    """
    name = "thompson"

    def __init__(self, *, prior_success: float = 1.0, prior_failure: float = 1.0):
        if prior_success <= 0.0 or prior_failure <= 0.0:
            raise ValueError("priors must be > 0")
        self.prior_success = float(prior_success)
        self.prior_failure = float(prior_failure)

    def propose(
        self,
        observations: Mapping[VariantId, Observation],
        *,
        seed: int | None = None,
    ) -> StrategyResult:
        rng = _rng(seed)

        posterior: dict[VariantId, dict[str, float]] = {}
        samples: dict[VariantId, float] = {}

        for vid, obs in observations.items():
            failures = obs.trials - obs.successes
            alpha = self.prior_success + obs.successes
            beta = self.prior_failure + failures

            posterior[vid] = {"alpha": float(alpha), "beta": float(beta)}
            samples[vid] = _beta_sample(rng, float(alpha), float(beta))

        total = sum(samples.values())
        if total <= 0.0:
            # Extremely unlikely, but keep safe fallback.
            n = len(samples)
            proposed: Weights = {vid: 1.0 / n for vid in samples}
        else:
            proposed = {vid: s / total for vid, s in samples.items()}

        explanation: dict[str, object] = {
            "strategy": self.name,
            "priors": {"prior_success": self.prior_success, "prior_failure": self.prior_failure},
            "posterior": posterior,
            "samples": samples,
            "seed": seed,
        }

        return StrategyResult(proposed_weights=proposed, explanation=explanation)
