# adaptive-experimentation

**Adaptive, safe, and explainable traffic allocation for online experiments.**

`adaptive-experimentation` is a lightweight Python library for **adaptive A/B testing** and **multi-armed bandit–style experimentation**, designed to be:

- Infrastructure-agnostic  
- Safe by default  
- Explainable  
- Composable  

This library is intentionally **boring first, smart second** — prioritizing correctness, clarity, and trust.

---

## Why this exists

Traditional A/B testing has a tradeoff:

- You learn, but you don’t optimize during the experiment  
- You waste traffic on losing variants  

Pure bandit systems fix that, but often:
- move too aggressively  
- are hard to explain  
- feel risky in production  

**This library sits in the middle**:

> Learn continuously, adapt gradually, and never violate safety constraints.

---

## Core concepts

- **Observations**: aggregated results per variant (trials, successes)  
- **Strategy**: how new weights are proposed  
- **Guardrails**: safety rules that control movement  
- **Engine**: orchestrates validation → strategy → guardrails → explanation  

---

## Installation

```bash
pip install adaptive-experimentation
````

Python 3.10+ required.

### Quick start
### Heuristic strategy (deterministic)
```python
from adaptive_experimentation import Engine, Constraints, Observation

engine = Engine(strategy="heuristic")

result = engine.compute(
    observations={
        "A": Observation(trials=2000, successes=120),
        "B": Observation(trials=2000, successes=180),
    },
    previous_weights={"A": 0.5, "B": 0.5},
    constraints=Constraints(
        min_trials=1000,
        max_step=0.1,
        min_weight=0.05,
    ),
)

print(result.weights)
print(result.explanation)
```

### Thompson Sampling (bandit strategy)

```python
from adaptive_experimentation import Engine, Constraints, Observation

engine = Engine(strategy="thompson")

result = engine.compute(
    observations={
        "A": Observation(trials=2000, successes=120),
        "B": Observation(trials=2000, successes=180),
    },
    previous_weights={"A": 0.5, "B": 0.5},
    constraints=Constraints(min_trials=1000),
    seed=42,
)

print(result.weights)
print(result.explanation["strategy_explanation"])
```

### Why Thompson Sampling?
- Balances exploration and exploitation
- Models uncertainty explicitly
- Widely used in production systems
- Still governed by the same guardrails


### Guardrails (safety by default)

| Guardrail    | Purpose                           |
| ------------ | --------------------------------- |
| `min_trials` | Prevent movement on tiny samples  |
| `max_step`   | Limit how much weights can change |
| `min_weight` | Ensure variants are never starved |
| `epsilon`    | Numerical stability               |


If guardrails prevent a change, the engine explains why.

## Explainability
Every result includes:
- strategy used
- proposed weights (pre-guardrails)
- posterior parameters (Thompson)
- sampled values (Thompson)
- guardrail decisions
- final weights
This makes the system auditable and production-safe.

## What this library does not do
- No continuous reward modeling (yet)
- No contextual bandits
- No user-level assignment
- No infra-specific integrations
This is a decision engine, not a full experimentation platform.

## Design philosophy
- Simple first, powerful later
- Safe defaults over clever behavior
- Explicit over implicit
- Explainability is a feature

If you’ve ever said:
“I like bandits, but I don’t trust them in prod yet”
This library is for you.

## Roadmap
- Typed explanation schema
- Optional early-movement policies
- Cooldown enforcement
- Continuous reward strategies
- Databricks / batch-job examples

## License
Apache 2.0

## Contributing
>Issues, ideas, and PRs are welcome. 
Design discussions are encouraged before large changes.