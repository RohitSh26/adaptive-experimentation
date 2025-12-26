from __future__ import annotations

from collections.abc import Mapping

from .types import Observation, VariantId


class ValidationError(ValueError):
    """Raised when inputs to the engine are invalid."""


def validate_observations(observations: Mapping[VariantId, Observation]) -> None:
    if not observations:
        raise ValidationError("observations must be non-empty")

    for vid, obs in observations.items():
        if not isinstance(vid, str) or not vid.strip():
            raise ValidationError(f"variant id must be a non-empty string; got {vid!r}")

        if obs.trials < 0:
            raise ValidationError(f"{vid}: trials must be >= 0; got {obs.trials}")

        if obs.successes < 0:
            raise ValidationError(f"{vid}: successes must be >= 0; got {obs.successes}")

        if obs.successes > obs.trials:
            raise ValidationError(
                f"{vid}: successes must be <= trials; got "
                f"successes={obs.successes}, trials={obs.trials}"
            )


def validate_previous_weights(
    previous_weights: Mapping[VariantId, float],
    *,
    observations: Mapping[VariantId, Observation],
    epsilon: float,
) -> None:
    if not previous_weights:
        raise ValidationError("previous_weights must be non-empty")

    obs_keys = set(observations.keys())
    w_keys = set(previous_weights.keys())
    if obs_keys != w_keys:
        missing = sorted(obs_keys - w_keys)
        extra = sorted(w_keys - obs_keys)
        msg = []
        if missing:
            msg.append(f"missing weights for variants: {missing}")
        if extra:
            msg.append(f"extra weights for unknown variants: {extra}")
        raise ValidationError(
            "previous_weights keys must match observations keys; " + "; ".join(msg)
        )

    total = 0.0
    for vid, w in previous_weights.items():
        if not (0.0 <= w <= 1.0):
            raise ValidationError(f"{vid}: weight must be between 0 and 1; got {w}")
        total += float(w)

    if abs(total - 1.0) > max(epsilon, 1e-6):
        raise ValidationError(f"previous_weights must sum to 1 (±tol); got {total}")
