# How to use adaptive-experimentation safely

This document explains how to use `adaptive-experimentation` correctly and safely
in real systems.

The goal of this library is **not** to be clever at all costs.
The goal is to make **gradual, explainable, and safe decisions**.

---

## What this library is (and is not)

### What it *is*
- A **decision engine** that computes the *next* set of traffic weights
- Designed to run in **batch** (hourly, daily, etc.)
- Strategy-agnostic and infrastructure-agnostic
- Safe by default

### What it *is not*
- Not a user-assignment system
- Not a full experimentation platform
- Not a personalization engine
- Not a statistical significance calculator

This library answers one question only:

> “Given recent aggregated results and previous weights, what should the next weights be?”

---

## Required inputs

You must provide:

### Observations
Aggregated per-variant results:
- `trials`: number of opportunities shown
- `successes`: number of desired outcomes

These should come from a **completed time window**, not live events.

### Previous weights
The weights that were used in the *previous* window:
- Keys must match variants exactly
- Values must sum to 1

Previous weights are required so the engine can:
- limit movement
- explain changes
- enforce safety constraints

---

## Where this fits in a real system

A typical system already has:
- user assignment logic (feature flags, config service)
- event logging (impressions, clicks, conversions)
- aggregation jobs (batch or streaming)

This library fits **after aggregation**:

1. Aggregate results for a window
2. Load previous weights
3. Compute new weights using this engine
4. Persist new weights
5. Use them for the next window

The engine never sees individual users.

---

## Choosing a strategy

### Heuristic strategy
- Deterministic
- Easy to reason about
- Good default when starting
- Recommended for initial adoption

### Thompson Sampling strategy
- Stochastic
- Balances exploration and exploitation
- Models uncertainty explicitly
- Supports reproducibility via `seed`

**Recommendation**
Start with `heuristic`.
Move to `thompson` only once your team is comfortable with adaptive behavior.

---

## Guardrails (why they matter)

Guardrails apply to *all* strategies.

### `min_trials`
Prevents movement when data is too small.
This avoids reacting to noise.

### `max_step`
Limits how much weights can change per run.
This prevents sharp traffic swings.

### `min_weight`
Ensures variants are never completely starved.
This keeps exploration alive.

Guardrails are the reason this library is safe in production.

---

## How often should you run this?

Do **not** run this per event.

Run it in **discrete windows**:
- hourly
- daily
- per deployment cycle

General guidance:
- High traffic → hourly
- Moderate traffic → every 6–24 hours
- Low traffic → daily or longer

Running too frequently leads to:
- noisy decisions
- frequent clamping
- confusing behavior

---

## Operational checklist

Log each run:
- window metadata
- total trials and successes
- previous weights
- proposed weights
- final weights
- explanation (hold / clamp / floor reasons)

Monitor:
- how often updates are held
- how often max_step is triggered
- long-term weight drift
- oscillations

---

## Common mistakes

- Running on tiny samples → results hold or clamp
- Forgetting to persist previous weights → unstable behavior
- Ignoring explanations → confusion during review
- Expecting per-user personalization → incorrect expectations

---

## Safe rollout pattern

When starting:
- use high `min_trials`
- use small `max_step`
- always set a non-zero `min_weight`

Relax constraints only after observing stable behavior.
