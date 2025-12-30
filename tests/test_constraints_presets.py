from __future__ import annotations

from adaptive_experimentation.types import Constraints


def test_constraints_safe_defaults_values() -> None:
    c = Constraints.safe_defaults()
    assert c.min_trials == 2000
    assert c.max_step == 0.05
    assert c.min_weight == 0.02


def test_constraints_neutral_defaults_values() -> None:
    c = Constraints.neutral_defaults()
    assert c.min_trials == 1000
    assert c.max_step == 0.10
    assert c.min_weight == 0.01


def test_constraints_explore_defaults_values() -> None:
    c = Constraints.explore_defaults()
    assert c.min_trials == 300
    assert c.max_step == 0.20
    assert c.min_weight == 0.005
