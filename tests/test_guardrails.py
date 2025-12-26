import pytest

from adaptive_experimentation.guardrails import apply_guardrails
from adaptive_experimentation.types import Constraints, Observation
from adaptive_experimentation.validation import ValidationError


def test_hold_when_min_trials_not_met() -> None:
    obs = {"A": Observation(trials=10, successes=2), "B": Observation(trials=10, successes=3)}
    prev = {"A": 0.5, "B": 0.5}
    proposed = {"A": 0.1, "B": 0.9}
    c = Constraints(min_trials=1000)

    weights, expl = apply_guardrails(
        observations=obs, previous_weights=prev, proposed_weights=proposed, constraints=c
    )
    assert weights == prev
    assert expl["changed"] is False
    assert expl["hold_reason"] == "min_trials_not_met"


def test_max_step_clamp_applied() -> None:
    obs = {
        "A": Observation(trials=2000, successes=200),
        "B": Observation(trials=2000, successes=300),
    }
    prev = {"A": 0.5, "B": 0.5}
    proposed = {"A": 0.0, "B": 1.0}
    c = Constraints(max_step=0.1, min_weight=0.0, min_trials=1000)

    weights, expl = apply_guardrails(
        observations=obs, previous_weights=prev, proposed_weights=proposed, constraints=c
    )
    # A can only move down to 0.4 and B up to 0.6 in one step, then normalize (already sums to 1)
    assert weights["A"] == pytest.approx(0.4)
    assert weights["B"] == pytest.approx(0.6)
    assert "max_step_clamps" in expl


def test_min_weight_floor_and_normalize() -> None:
    obs = {
        "A": Observation(trials=2000, successes=200),
        "B": Observation(trials=2000, successes=300),
        "C": Observation(trials=2000, successes=50),
    }
    prev = {"A": 1 / 3, "B": 1 / 3, "C": 1 / 3}
    proposed = {"A": 0.49, "B": 0.49, "C": 0.02}
    c = Constraints(min_weight=0.05, max_step=1.0, min_trials=1000)

    weights, expl = apply_guardrails(
        observations=obs, previous_weights=prev, proposed_weights=proposed, constraints=c
    )
    assert weights["C"] >= 0.05 - 1e-9
    assert abs(sum(weights.values()) - 1.0) < 1e-9
    assert "min_weight_floors" in expl


def test_infeasible_min_weight_raises() -> None:
    obs = {
        "A": Observation(trials=2000, successes=200),
        "B": Observation(trials=2000, successes=300),
    }
    prev = {"A": 0.5, "B": 0.5}
    proposed = {"A": 0.5, "B": 0.5}
    c = Constraints(min_weight=0.6, min_trials=1000)

    with pytest.raises(ValidationError):
        apply_guardrails(
            observations=obs,
            previous_weights=prev,
            proposed_weights=proposed,
            constraints=c,
        )
