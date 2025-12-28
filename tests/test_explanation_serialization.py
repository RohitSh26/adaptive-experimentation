from dataclasses import asdict

from adaptive_experimentation import Constraints, Engine, Observation


def test_explanation_is_serializable() -> None:
    engine = Engine(strategy="heuristic")

    r = engine.compute(
        observations={"A": Observation(trials=1000, successes=10), "B": Observation(
            trials=1000, successes=20)},
        previous_weights={"A": 0.5, "B": 0.5},
        constraints=Constraints(min_trials=1000, min_weight=0.0),
    )

    d = asdict(r.explanation)
    assert d["strategy"]["name"] in {"heuristic", "thompson"}
    assert "guardrails" in d
