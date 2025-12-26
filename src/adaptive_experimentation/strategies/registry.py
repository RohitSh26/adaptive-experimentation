from __future__ import annotations

from .base import Strategy
from .heuristic_strategy import HeuristicStrategy


def get_strategy(name: str) -> Strategy:
    if name == "heuristic":
        return HeuristicStrategy()
    raise ValueError(f"unknown strategy: {name!r}")
