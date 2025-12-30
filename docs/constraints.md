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