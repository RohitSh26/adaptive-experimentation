import pytest

from adaptive_experimentation import Constraints, Engine, Observation


def test_engine_moves_toward_better_variant_when_enough_data() -> None:
    engine = Engine(strategy="heuristic")

    observations = {
        "A": Observation(trials=2000, successes=100),  # 5%
        "B": Observation(trials=2000, successes=300),  # 15%
    }
    prev = {"A": 0.5, "B": 0.5}

    constraints = Constraints(min_trials=1000, max_step=0.2, min_weight=0.0)

    result = engine.compute(
        observations=observations, previous_weights=prev, constraints=constraints
    )

    assert result.weights["B"] > 0.5
    assert result.explanation["strategy"] == "heuristic"
    assert "proposed_weights" in result.explanation
    assert abs(sum(result.weights.values()) - 1.0) < 1e-9


def test_engine_holds_when_min_trials_not_met() -> None:
    engine = Engine(strategy="heuristic")

    observations = {
        "A": Observation(trials=10, successes=1),
        "B": Observation(trials=10, successes=2),
    }
    prev = {"A": 0.5, "B": 0.5}

    constraints = Constraints(min_trials=1000)

    result = engine.compute(
        observations=observations, previous_weights=prev, constraints=constraints
    )

    assert result.weights == prev
    assert result.explanation["changed"] is False
    assert result.explanation["hold_reason"] == "min_trials_not_met"


def test_engine_applies_max_step() -> None:
    engine = Engine(strategy="heuristic")

    observations = {
        "A": Observation(trials=5000, successes=10),
        "B": Observation(trials=5000, successes=1000),
    }
    prev = {"A": 0.5, "B": 0.5}

    constraints = Constraints(min_trials=1000, max_step=0.05, min_weight=0.0)

    result = engine.compute(
        observations=observations, previous_weights=prev, constraints=constraints
    )

    # B should not jump beyond 0.55 in one step
    assert result.weights["B"] == pytest.approx(0.55)
    assert result.weights["A"] == pytest.approx(0.45)
