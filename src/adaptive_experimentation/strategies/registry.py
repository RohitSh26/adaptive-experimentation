from __future__ import annotations

from .base import Strategy
from .heuristic_strategy import HeuristicStrategy
from .thompson_strategy import ThompsonStrategy


def get_strategy(name: str) -> Strategy:
    if name == "heuristic":
        return HeuristicStrategy()
    if name == "thompson":
        return ThompsonStrategy()
    raise ValueError(f"unknown strategy: {name!r}")
