# Thompson Sampling (Beta-Bernoulli) Design

This document defines the Thompson Sampling strategy for **binary outcomes**
(click/no-click, convert/no-convert, etc.) using a Beta-Bernoulli model.

---

## 1. Why Thompson Sampling

Thompson Sampling balances:
- exploration (try all variants sometimes)
- exploitation (use the best-performing variant more often)

It does this by modeling uncertainty:
- variants with little data remain uncertain and still get traffic
- variants with strong evidence get more traffic

---

## 2. Data Model (Binary Outcomes)

Each variant has aggregated observations:
- trials: number of opportunities
- successes: number of positive outcomes

Failures are computed as:
- failures = trials - successes

The unknown parameter is:
- θ = probability of success (e.g., CTR)

---

## 3. Prior (Beta Distribution)

We maintain a Beta distribution over θ:

- θ ~ Beta(α, β)

Where:
- α = prior_success + successes
- β = prior_failure + failures

Default priors (v0 proposal):
- prior_success = 1.0
- prior_failure = 1.0

This is a mild, symmetric prior and is easy to explain.

---

## 4. Thompson Sampling Procedure (Batch)

Given aggregated observations:

1) For each variant, compute posterior:
   α_i = prior_success + successes_i
   β_i = prior_failure + (trials_i - successes_i)

2) Sample once from each posterior:
   s_i ~ Beta(α_i, β_i)

3) Convert samples into proposed weights:
   weight_i = s_i / sum(s)

Notes:
- This produces a stochastic proposal.
- Guardrails still apply (min_trials hold, max_step clamp, min_weight floor, normalize).

---

## 5. Explainability (Required Fields)

The explanation object should include:
- strategy: "thompson"
- priors: {prior_success, prior_failure}
- per-variant posterior params: {alpha, beta}
- per-variant sampled values: {sample}
- proposed_weights (pre-guardrails)
- guardrail explanation merged in (hold/clamp/floor/etc.)

Explainability must make it clear why a variant got more/less traffic:
- higher sample
- more confident posterior (narrower distribution)
- or guardrails prevented movement

---

## 6. Determinism / Reproducibility

Because Thompson Sampling is stochastic, we support:
- seed: optional integer

If seed is provided:
- sampling is reproducible across runs.

---

## 7. Scope

In-scope for v0:
- binary outcomes only (Beta-Bernoulli)

Out of scope (future):
- continuous rewards
- multi-objective rewards
- contextual bandits / per-segment bandits

