from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from adaptive_experimentation.explanations import AllocationExplanation
from adaptive_experimentation.types import Observation


class AllocationStore(Protocol):
    """Where allocation weights are read from / written to.

    This could be a feature flag system, config service, database, etc.
    Implementations should treat writes as atomic for a single experiment.
    """

    def read_weights(self, experiment_id: str) -> Mapping[str, float]:
        """Return current weights for the given experiment_id."""
        ...

    def write_weights(
        self,
        experiment_id: str,
        weights: Mapping[str, float],
        explanation: AllocationExplanation,
    ) -> None:
        """Persist new weights for experiment_id along with an explanation."""
        ...


class ObservationSource(Protocol):
    """Where aggregated observations (trials/successes) come from.

    Implementations are expected to return already-aggregated counts per variant
    for the requested time window.
    """

    def read_observations(
        self,
        experiment_id: str,
        window_start_epoch_s: int,
        window_end_epoch_s: int,
    ) -> Mapping[str, Observation]:
        """Return observations per variant for the requested window."""
        ...
