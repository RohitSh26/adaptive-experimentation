from adaptive_experimentation import Constraints, Engine, Observation


def test_engine_thompson_is_reproducible_with_seed() -> None:
    engine = Engine(strategy="thompson")
    observations = {
        "A": Observation(trials=2000, successes=100),
        "B": Observation(trials=2000, successes=300),
    }
    prev = {"A": 0.5, "B": 0.5}
    constraints = Constraints(min_trials=1000, max_step=1.0, min_weight=0.0)

    r1 = engine.compute(
        observations=observations, previous_weights=prev, constraints=constraints, seed=7
    )
    r2 = engine.compute(
        observations=observations, previous_weights=prev, constraints=constraints, seed=7
    )

    assert r1.weights == r2.weights
    assert r1.explanation.strategy.name == "thompson"


def test_engine_thompson_still_holds_under_min_trials_policy_x() -> None:
    engine = Engine(strategy="thompson")
    observations = {
        "A": Observation(trials=10, successes=2),
        "B": Observation(trials=10, successes=3),
    }
    prev = {"A": 0.5, "B": 0.5}
    constraints = Constraints(min_trials=1000)

    r = engine.compute(
        observations=observations, previous_weights=prev, constraints=constraints, seed=1
    )
    assert r.weights == prev
    assert r.explanation.guardrails.changed is False
    assert r.explanation.guardrails.hold_reason == "min_trials_not_met"