from adaptive_experimentation.strategies.heuristic import propose_weights
from adaptive_experimentation.types import Observation


def test_heuristic_prefers_higher_ctr() -> None:
    obs = {
        "A": Observation(trials=1000, successes=100),  # 10%
        "B": Observation(trials=1000, successes=200),  # 20%
    }

    weights = propose_weights(obs)

    assert weights["B"] > weights["A"]
    assert abs(sum(weights.values()) - 1.0) < 1e-9


def test_heuristic_uniform_when_no_trials() -> None:
    obs = {
        "A": Observation(trials=0, successes=0),
        "B": Observation(trials=0, successes=0),
    }

    weights = propose_weights(obs)

    assert weights["A"] == weights["B"] == 0.5
