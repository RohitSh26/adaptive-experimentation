from __future__ import annotations

from collections.abc import Mapping

from ..types import Observation, VariantId, Weights


def propose_weights(
    observations: Mapping[VariantId, Observation],
    *,
    alpha: float = 1.0,
) -> Weights:
    """
    Propose raw weights proportional to smoothed observed success rate.

    raw_score = (successes + alpha) / (trials + 2 * alpha)
    """
    scores: dict[VariantId, float] = {}

    for vid, obs in observations.items():
        score = (obs.successes + alpha) / (obs.trials + 2.0 * alpha)
        scores[vid] = float(score)

    total = sum(scores.values())
    if total <= 0.0:
        # fallback to uniform weights
        n = len(scores)
        return {vid: 1.0 / n for vid in scores}

    return {vid: score / total for vid, score in scores.items()}
