from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from adaptive_experimentation.engine import Engine
from adaptive_experimentation.types import AllocationResult, Constraints

if TYPE_CHECKING:
    from collections.abc import Mapping

    from adaptive_experimentation.types import Observation

    from .protocols import AllocationStore, ObservationSource


@dataclass(frozen=True)
class ControlLoopRunResult:
    """Result of a single control loop execution."""

    experiment_id: str
    window_start_epoch_s: int
    window_end_epoch_s: int
    previous_weights: dict[str, float]
    allocation: AllocationResult
    wrote_update: bool


def _max_abs_diff(a: Mapping[str, float], b: Mapping[str, float]) -> float:
    """Return the maximum absolute difference across keys (assumes keys match)."""
    return max(abs(a[k] - b[k]) for k in a)


def _assert_variant_key_match(
    *,
    observations: Mapping[str, Observation],
    previous_weights: Mapping[str, float],
) -> None:
    """Fail fast if variant IDs don't match between inputs.

    This is intentionally strict to avoid accidental traffic drops or silent
    behavior changes when variants are missing.
    """
    obs_keys = set(observations.keys())
    prev_keys = set(previous_weights.keys())

    if obs_keys != prev_keys:
        missing_in_obs = sorted(prev_keys - obs_keys)
        extra_in_obs = sorted(obs_keys - prev_keys)
        raise ValueError(
            "Variant ID mismatch between observations and previous_weights. "
            f"missing_in_observations={missing_in_obs} extra_in_observations={extra_in_obs}"
        )


def run_once(
    *,
    experiment_id: str,
    window_start_epoch_s: int,
    window_end_epoch_s: int,
    store: AllocationStore,
    source: ObservationSource,
    strategy: str = "thompson",
    constraints: Constraints | None = None,
) -> ControlLoopRunResult:
    """Run one safe allocation update cycle.

    Steps:
      1) Read current weights from AllocationStore
      2) Read aggregated observations from ObservationSource for the time window
      3) Compute next weights using the Engine + strategy
      4) Write weights back only if they changed (within tolerance)

    Notes:
      - Strictly requires that observation variant IDs match previous weights.
      - Keeps the library infrastructure-agnostic: stores/sources are injected.
    """
    prev = dict(store.read_weights(experiment_id))
    obs = source.read_observations(experiment_id, window_start_epoch_s, window_end_epoch_s)

    _assert_variant_key_match(observations=obs, previous_weights=prev)

    engine = Engine(strategy=strategy)
    result = engine.compute(
        observations=obs,
        previous_weights=prev,
        constraints=constraints or Constraints(),
        last_updated_at_epoch_s=None,
        now_epoch_s=None,
    )

    tol = 1e-12
    wrote = False
    if _max_abs_diff(result.weights, prev) > tol:
        store.write_weights(experiment_id, result.weights, result.explanation)
        wrote = True

    return ControlLoopRunResult(
        experiment_id=experiment_id,
        window_start_epoch_s=window_start_epoch_s,
        window_end_epoch_s=window_end_epoch_s,
        previous_weights=prev,
        allocation=result,
        wrote_update=wrote,
    )
