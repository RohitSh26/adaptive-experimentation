![CI](https://github.com/rohitsh26/adaptive-experimentation/actions/workflows/ci.yml/badge.svg)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Latest Release](https://img.shields.io/github/v/release/rohitsh26/adaptive-experimentation)

# adaptive-experimentation

A **safety-first, explainable engine** for adaptive traffic allocation using
multi-armed bandits and experimentation techniques.

This library helps teams **learn which variants perform better over time**
while protecting users and the business through conservative defaults,
guardrails, and clear explanations.

---

## Why this exists

Most experimentation and bandit libraries focus on **maximizing reward as fast
as possible**.

In production systems, that can be dangerous.

Teams often need:
- predictable behavior
- gradual movement
- protection against low-signal data
- clear explanations for *why* traffic changed (or didn’t)

**adaptive-experimentation** is designed for those realities.

---

## What this library does (and does not do)

### ✅ What it does
- Computes **safe traffic allocations** across variants
- Learns from observations over time
- Supports **Thompson Sampling** and heuristic strategies
- Enforces **guardrails** (minimum data, max movement, minimum exposure)
- Produces **typed, explainable decisions**
- Remains **infrastructure-agnostic**

### ❌ What it does not do
- Assign users to variants
- Store experiment data
- Replace your feature flag or experimentation platform
- Optimize aggressively without safety constraints

This library focuses on **decision logic only**.

---

## Core design principles

1. **Safety by default**  
   If there is not enough data, the system holds steady.

2. **Explainability is first-class**  
   Every decision includes a structured explanation of:
   - strategy used
   - constraints applied
   - clamping, floors, and holds

3. **Infrastructure-agnostic**  
   Works with batch jobs, streaming systems, notebooks, or services.

4. **Small, composable surface area**  
   Easy to reason about. Easy to test. Easy to trust.

---

## Quick start (end-to-end example)

```python
from adaptive_experimentation import Engine, Observation, Constraints

engine = Engine(strategy="thompson")

observations = {
    "A": Observation(trials=1_000, successes=50),   # 5%
    "B": Observation(trials=1_000, successes=120),  # 12%
    "C": Observation(trials=1_000, successes=60),   # 6%
}

previous_weights = {
    "A": 0.33,
    "B": 0.33,
    "C": 0.34,
}

constraints = Constraints(
    min_trials=500,
    max_step=0.1,
    min_weight=0.05,
)

result = engine.compute(
    observations=observations,
    previous_weights=previous_weights,
    constraints=constraints,
)

print(result.weights)
print(result.explanation)
```

The engine:

- evaluates observed performance
- proposes new weights
- applies guardrails
- explains exactly what happened

---

### Strategies
#### Thompson Sampling (Beta-Bernoulli)

- Suitable for binary outcomes (click / no-click, success / failure)
- Balances exploration and exploitation probabilistically
- Conservative when data is sparse
---

#### Heuristic strategy

- Simple, deterministic baseline
- Useful for debugging and controlled rollouts

More strategies can be added without changing the engine API.

---

### Guardrails (safety by default)

Guardrails protect against overreaction and unintended exposure:

- min_trials
  Prevents movement until enough data is observed
- max_step
  Limits how much weights can change in one update
- min_weight
  Ensures all variants retain minimum exposure

When guardrails apply, the explanation explicitly records why.

---

## Choosing Constraints (Guardrail Presets)

If you're not sure where to start, use the built-in presets:

| Preset | When to use | Behavior |
|---|---|---|
| `Constraints.safe_defaults()` | Production / high-risk surfaces | Slow movement, holds longer, very stable |
| `Constraints.neutral_defaults()` | Default starting point | Balanced learning vs stability |
| `Constraints.explore_defaults()` | Low-risk / high-traffic environments | Faster movement, still guarded |

Example:

```python
from adaptive_experimentation import Constraints, Engine, Observation

engine = Engine(strategy="thompson")

constraints = Constraints.neutral_defaults()

result = engine.compute(
    observations={
        "A": Observation(trials=2000, successes=120),
        "B": Observation(trials=2000, successes=150),
    },
    previous_weights={"A": 0.5, "B": 0.5},
    constraints=constraints,
)
```

Tip: Constraints apply per control-loop run. If you run the loop more frequently (e.g., every 5 minutes vs hourly), the same max_step will result in faster overall movement.

---

### Examples

See the `examples/` directory:

- `end_to_end.py` — single-window decision
- `multi_window.py` — learning over time with CSV output

These examples simulate real operational patterns, not toy cases.

### What learning looks like over time

Below is a visualization from the multi-window simulation showing how traffic
weights evolve as the system gathers more data.

![Weights over time](docs/assets/weights_over_time.png)


---
### Who should use this

- Teams running A/B or multivariate experiments
- Search, ranking, or recommendation systems
- Feature rollout and personalization pipelines
- Data scientists who need explainable decisions

---

### Who should not use this

- If you want a hosted experimentation platform
- If you need user assignment or persistence
- If you want aggressive, unconstrained optimization

---

### Status & roadmap

### Current status: Alpha (v0.1.x)

Planned improvements:

- Additional strategies (continuous rewards, contextual bandits)
- Strategy interface stabilization
- Visualization helpers for examples
- Optional validation integrations (e.g. Pydantic)

Breaking changes may occur while the API stabilizes.
---

### License
Apache 2.0

### Contributing
>Issues, ideas, and PRs are welcome. 
Design discussions are encouraged before large changes.