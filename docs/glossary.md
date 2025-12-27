# Glossary

**Variant**  
One option in an experiment (A, B, C, etc.).

**Trial**  
One opportunity for a variant to succeed.

**Success**  
A desired outcome (click, conversion, etc.).

**Observation**  
Aggregated trials and successes for a variant.

**Weight**  
Fraction of traffic assigned to a variant.

**Previous weights**  
Weights used in the last window.

**Proposed weights**  
Weights suggested by a strategy before guardrails.

**Final weights**  
Weights after guardrails are applied.

**Guardrails**  
Safety rules that constrain movement.

**min_trials**  
Minimum data required before changing weights.

**max_step**  
Maximum allowed change per run.

**min_weight**  
Minimum traffic a variant must receive.

**Exploration**  
Trying less-proven variants to learn.

**Exploitation**  
Favoring variants that perform well.

**Thompson Sampling**  
A strategy that samples from uncertainty-aware beliefs
to balance exploration and exploitation.

**Beta-Bernoulli**  
A model for estimating the probability of success
from binary outcomes.

**Seed**  
A value used to make stochastic decisions reproducible.
