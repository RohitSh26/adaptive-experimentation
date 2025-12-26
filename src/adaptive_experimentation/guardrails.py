from __future__ import annotations

from collections.abc import Mapping

from .types import Constraints, Observation, VariantId, Weights
from .validation import ValidationError


def _normalize(weights: Mapping[VariantId, float], *, epsilon: float) -> Weights:
    total = float(sum(weights.values()))
    if total <= epsilon:
        raise ValidationError(f"cannot normalize weights with non-positive sum: {total}")
    return {k: float(v) / total for k, v in weights.items()}


def apply_guardrails(
    *,
    observations: Mapping[VariantId, Observation],
    previous_weights: Mapping[VariantId, float],
    proposed_weights: Mapping[VariantId, float],
    constraints: Constraints,
) -> tuple[Weights, dict[str, object]]:
    """
    Apply guardrails to proposed weights and return (final_weights, explanation_delta).
    """
    n = len(observations)
    if n == 0:
        raise ValidationError("observations must be non-empty")

    # Feasibility check for min_weight
    if n * constraints.min_weight > 1.0 + constraints.epsilon:
        raise ValidationError(
            f"min_weight={constraints.min_weight} is infeasible for {n} variants "
            f"(n * min_weight must be <= 1)"
        )

    # Minimum evidence: hold steady if any variant lacks trials
    insufficient = [vid for vid, obs in observations.items() if obs.trials < constraints.min_trials]
    if insufficient:
        return (
            dict(previous_weights),
            {
                "changed": False,
                "hold_reason": "min_trials_not_met",
                "min_trials": constraints.min_trials,
                "variants_below_min_trials": sorted(insufficient),
                "guardrails_applied": ["min_trials_hold"],
            },
        )

    # Clamp per-variant step change
    clamped: dict[VariantId, float] = {}
    clamp_hits: dict[VariantId, dict[str, float]] = {}
    for vid, prev in previous_weights.items():
        raw = float(proposed_weights.get(vid, prev))
        lo = max(0.0, float(prev) - constraints.max_step)
        hi = min(1.0, float(prev) + constraints.max_step)
        new = min(max(raw, lo), hi)
        clamped[vid] = new
        if abs(new - raw) > constraints.epsilon:
            clamp_hits[vid] = {"raw": raw, "clamped": new, "lo": lo, "hi": hi}

        # Apply min_weight floor (hard floor with redistribution)
    floored: dict[VariantId, float] = dict(clamped)
    floor_hits: dict[VariantId, dict[str, float]] = {}

    floored_ids = set()
    for vid, w in floored.items():
        if w + constraints.epsilon < constraints.min_weight:
            floor_hits[vid] = {"before": w, "after": constraints.min_weight}
            floored[vid] = constraints.min_weight
            floored_ids.add(vid)

    if floored_ids:
        fixed_mass = sum(floored[vid] for vid in floored_ids)
        remaining = 1.0 - fixed_mass

        if remaining < -constraints.epsilon:
            raise ValidationError(
                "min_weight floor exceeded total mass; check feasibility/rounding"
            )

        free_ids = [vid for vid in floored.keys() if vid not in floored_ids]

        if free_ids:
            base = sum(max(floored[vid], 0.0) for vid in free_ids)
            if base <= constraints.epsilon:
                # If nothing to distribute proportionally, split remaining evenly
                per = remaining / len(free_ids) if free_ids else 0.0
                for vid in free_ids:
                    floored[vid] = per
            else:
                for vid in free_ids:
                    floored[vid] = remaining * (floored[vid] / base)
        # If no free_ids, all mass is fixed by floors; remaining should be ~0

        normalized = dict(floored)
    else:
        # No floors triggered; normal normalization is fine
        normalized = _normalize(floored, epsilon=constraints.epsilon)

    # Determine if changed materially
    changed = any(
        abs(float(normalized[v]) - float(previous_weights[v])) > max(constraints.epsilon, 1e-9)
        for v in normalized
    )

    explanation = {
        "changed": changed,
        "guardrails_applied": ["max_step_clamp", "min_weight_floor", "normalize"],
    }
    if clamp_hits:
        explanation["max_step_clamps"] = clamp_hits
    if floor_hits:
        explanation["min_weight_floors"] = floor_hits

    return normalized, explanation
