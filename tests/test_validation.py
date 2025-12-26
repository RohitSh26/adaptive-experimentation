import pytest

from adaptive_experimentation.types import Observation
from adaptive_experimentation.validation import (
    ValidationError,
    validate_observations,
    validate_previous_weights,
)


def test_validate_observations_success() -> None:
    validate_observations({"A": Observation(trials=10, successes=2)})


def test_validate_observations_empty() -> None:
    with pytest.raises(ValidationError):
        validate_observations({})


def test_validate_observations_successes_gt_trials() -> None:
    with pytest.raises(ValidationError):
        validate_observations({"A": Observation(trials=10, successes=20)})


def test_validate_previous_weights_keys_must_match() -> None:
    obs = {"A": Observation(trials=10, successes=2)}
    with pytest.raises(ValidationError):
        validate_previous_weights({"B": 1.0}, observations=obs, epsilon=1e-9)


def test_validate_previous_weights_sum_to_one() -> None:
    obs = {"A": Observation(trials=10, successes=2), "B": Observation(trials=10, successes=2)}
    with pytest.raises(ValidationError):
        validate_previous_weights({"A": 0.7, "B": 0.7}, observations=obs, epsilon=1e-9)
