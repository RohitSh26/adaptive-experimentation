from __future__ import annotations

from dataclasses import dataclass

import pytest

from adaptive_experimentation.integrations.control_loop import run_once
from adaptive_experimentation.integrations.protocols import AllocationStore, ObservationSource
from adaptive_experimentation.types import Constraints, Observation


@dataclass
class _MemStore(AllocationStore):
    weights: dict[str, float]
    writes: list[dict[str, float]]

    def read_weights(self, experiment_id: str) -> dict[str, float]:
        return dict(self.weights)

    def write_weights(self, experiment_id: str, weights: dict[str, float], explanation) -> None:  # type: ignore[override]
        self.weights = dict(weights)
        self.writes.append(dict(weights))


@dataclass
class _MemSource(ObservationSource):
    observations: dict[str, Observation]

    def read_observations(
        self,
        experiment_id: str,
        window_start_epoch_s: int,
        window_end_epoch_s: int,
    ) -> dict[str, Observation]:
        return dict(self.observations)


def test_control_loop_strict_key_mismatch_raises() -> None:
    store = _MemStore(weights={"A": 0.5, "B": 0.5}, writes=[])
    source = _MemSource(observations={"A": Observation(trials=10, successes=1)})

    with pytest.raises(ValueError, match="Variant ID mismatch"):
        run_once(
            experiment_id="exp1",
            window_start_epoch_s=0,
            window_end_epoch_s=60,
            store=store,
            source=source,
            strategy="heuristic",
        )


def test_control_loop_writes_when_changed() -> None:
    store = _MemStore(weights={"A": 0.5, "B": 0.5}, writes=[])
    source = _MemSource(
        observations={
            "A": Observation(trials=2000, successes=100),  # 5%
            "B": Observation(trials=2000, successes=300),  # 15%
        }
    )

    constraints = Constraints(min_trials=1000, max_step=0.2, min_weight=0.0)

    result = run_once(
        experiment_id="exp1",
        window_start_epoch_s=0,
        window_end_epoch_s=60,
        store=store,
        source=source,
        strategy="heuristic",
        constraints=constraints,
    )

    assert result.wrote_update is True
    assert len(store.writes) == 1
    assert result.allocation.weights["B"] > 0.5


def test_control_loop_does_not_write_when_unchanged_due_to_hold() -> None:
    store = _MemStore(weights={"A": 0.5, "B": 0.5}, writes=[])
    # Not enough trials to move with safe defaults (min_trials default)
    source = _MemSource(
        observations={
            "A": Observation(trials=10, successes=1),
            "B": Observation(trials=10, successes=2),
        }
    )

    result = run_once(
        experiment_id="exp1",
        window_start_epoch_s=0,
        window_end_epoch_s=60,
        store=store,
        source=source,
        strategy="heuristic",
        constraints=Constraints(min_trials=1000, max_step=0.2, min_weight=0.0),
    )

    assert result.wrote_update is False
    assert store.writes == []
    assert result.allocation.weights == {"A": 0.5, "B": 0.5}
