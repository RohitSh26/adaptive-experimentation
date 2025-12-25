# Core API Design

This document defines the public API contract for the `adaptive-experimentation` library.

The API is designed to be:
- infrastructure-agnostic
- batch-friendly
- safe by default
- explainable

---

## 1. Primary Entry Point

The main entry point is an `Engine` that computes new traffic weights.

Conceptually:

Input:
- aggregated observations per variant
- previous weights
- constraints (guardrails)
- strategy selection (how to compute weights)

Output:
- new weights
- explanation (for auditing and trust)

---

## 2. VariantId

A `VariantId` is a string key.

Examples:
- "ranker_v1"
- "ranker_v2"
- "control"
- "treatment_a"

---

## 3. Observation Model

The library will start by supporting the common binary-reward case:

- trials: number of exposures / opportunities
- successes: number of positive outcomes (e.g., clicks)

### Observation
- trials: int (>= 0)
- successes: int (0 <= successes <= trials)

Notes:
- Observations are aggregated upstream.
- The library does not do attribution or logging.

---

## 4. Weights Model

### Weights
- mapping of VariantId -> float
- each weight must be between 0 and 1
- weights must sum to 1 (within tolerance)

Weights represent traffic allocation for future assignments.

---

## 5. Constraints (Guardrails)

Constraints are a bundle of rules applied during allocation:

Minimum set:
- min_weight: float (e.g. 0.05)  
  Ensures exploration floor for every active variant.
- max_step: float (e.g. 0.10)  
  Limits how much a weight can change in one update.
- min_trials: int (e.g. 1000)  
  Prevents reallocating based on tiny samples.
- epsilon: float (e.g. 1e-9)  
  Numerical safety for normalization.

Constraints must be deterministic and explainable.

---

## 6. Strategy

A Strategy defines how raw weights are proposed before guardrails.

For Epic #2 we only define the interface.

Examples of strategies (future):
- "heuristic"
- "thompson"
- "ucb"

---

## 7. Result / Explainability

The engine returns:

### AllocationResult
- weights: Weights
- explanation: dict[str, object]

Explainability should include:
- which strategy ran
- summary stats per variant
- what constraints were applied
- whether allocation was changed or held

---

## 8. Proposed Python API (v0)

```python
from adaptive_experimentation import Engine, Constraints, Observation

engine = Engine(strategy="heuristic")

result = engine.compute(
    observations={
        "A": Observation(trials=1000, successes=120),
        "B": Observation(trials=1000, successes=150),
    },
    previous_weights={"A": 0.5, "B": 0.5},
    constraints=Constraints(),
)

print(result.weights)
print(result.explanation)
```

Notes:
- previous_weights is required (explicit is better than implicit)
- constraints has safe defaults
- Engine is pure: no side effects, no persistence

