# Strategy Interface Design

A Strategy proposes raw allocation weights before guardrails are applied.

The Engine:
1) validates inputs
2) calls a strategy to propose weights (+ strategy explanation)
3) applies guardrails
4) merges explanations

This keeps strategies simple and guardrails centralized.

---

## 1. Strategy Contract (v0)

Inputs:
- observations: mapping of variant -> Observation
- seed: optional int (for reproducible sampling)
- strategy_params: optional dict-like configuration (future)

Outputs:
- proposed_weights: dict variant -> float (not necessarily guardrail-safe)
- strategy_explanation: dict (sampling details, priors, etc.)

The Engine is responsible for:
- validation
- guardrails
- final normalization
- producing the final AllocationResult

---

## 2. Strategies

### 2.1 Heuristic
- deterministic
- proposes weights proportional to smoothed CTR

### 2.2 Thompson (Beta-Bernoulli)
- stochastic
- samples from posterior Beta distributions and normalizes samples into weights
- seed supported for reproducibility

---

## 3. Strategy Selection

Engine will support:
- "heuristic"
- "thompson"

Unknown strategy -> error.

