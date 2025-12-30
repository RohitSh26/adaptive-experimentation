from __future__ import annotations

from adaptive_experimentation.engine import Engine
from adaptive_experimentation.types import Constraints, Observation


def test_thompson_is_deterministic_with_same_seed() -> None:
    engine = Engine(strategy="thompson")

    observations = {
        "A": Observation(trials=1000, successes=100),
        "B": Observation(trials=1000, successes=150),
        "C": Observation(trials=1000, successes=120),
    }

    prev = {"A": 0.33, "B": 0.33, "C": 0.34}
    constraints = Constraints.neutral_defaults()

    r1 = engine.compute(
        observations=observations,
        previous_weights=prev,
        constraints=constraints,
        seed=42,
    )

    r2 = engine.compute(
        observations=observations,
        previous_weights=prev,
        constraints=constraints,
        seed=42,
    )

    assert r1.weights == r2.weights
    assert r1.explanation.strategy.name == "thompson"
    assert r1.explanation.strategy.details["seed"] == 42


def test_thompson_different_seeds_can_produce_different_results() -> None:
    engine = Engine(strategy="thompson")

    observations = {
        "A": Observation(trials=1000, successes=100),
        "B": Observation(trials=1000, successes=150),
    }

    prev = {"A": 0.5, "B": 0.5}
    constraints = Constraints.neutral_defaults()

    r1 = engine.compute(
        observations=observations,
        previous_weights=prev,
        constraints=constraints,
        seed=1,
    )

    r2 = engine.compute(
        observations=observations,
        previous_weights=prev,
        constraints=constraints,
        seed=2,
    )

    # Not guaranteed to differ every time, but extremely likely
    assert r1.weights != r2.weights
