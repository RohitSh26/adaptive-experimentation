from adaptive_experimentation import AllocationResult, Constraints, Engine, Observation


def test_public_api_imports() -> None:
    _ = Engine(strategy="heuristic")
    _ = Constraints()
    _ = Observation(trials=10, successes=2)
    assert AllocationResult
