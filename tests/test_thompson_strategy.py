from adaptive_experimentation.strategies.thompson_strategy import ThompsonStrategy
from adaptive_experimentation.types import Observation


def test_thompson_is_reproducible_with_seed() -> None:
    obs = {
        "A": Observation(trials=1000, successes=100),
        "B": Observation(trials=1000, successes=200),
        "C": Observation(trials=1000, successes=50),
    }

    s = ThompsonStrategy()
    r1 = s.propose(obs, seed=123).proposed_weights
    r2 = s.propose(obs, seed=123).proposed_weights

    assert r1 == r2
    assert abs(sum(r1.values()) - 1.0) < 1e-9


def test_thompson_outputs_valid_weights() -> None:
    obs = {"A": Observation(trials=10, successes=2), "B": Observation(trials=10, successes=3)}
    s = ThompsonStrategy()
    r = s.propose(obs, seed=42)

    w = r.proposed_weights
    assert set(w.keys()) == {"A", "B"}
    assert 0.0 <= w["A"] <= 1.0
    assert 0.0 <= w["B"] <= 1.0
    assert abs(sum(w.values()) - 1.0) < 1e-9
    assert "posterior" in r.explanation
    assert "samples" in r.explanation
