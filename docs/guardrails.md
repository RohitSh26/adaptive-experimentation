# Guardrails (Constraints) Design

Guardrails are safety rules that prevent adaptive experimentation from making
unstable, risky, or noisy allocation changes.

This library is **safe by default**:
- guardrails are enabled by default
- callers can loosen them intentionally, but must do so explicitly
- all guardrail effects must be explainable

---

## 1. Principles

1) Safety over speed  
2) Deterministic behavior  
3) Small changes over sudden jumps  
4) Always leave room for exploration  
5) Always produce an explanation (even when holding steady)

---

## 2. Guardrail Catalog (v0)

### 2.1 Minimum Exploration Floor (`min_weight`)
**Definition**
- Each active variant must receive at least `min_weight` traffic.

**Purpose**
- Prevents the system from starving variants too early.
- Supports continuous learning and protects against early noise.

**Default (proposal)**
- `min_weight = 0.05` (5%)

**Notes**
- If there are N variants, `N * min_weight` must be <= 1.
- If not feasible, the engine must fail fast with a clear error.

---

### 2.2 Maximum Step Change (`max_step`)
**Definition**
- The allocation for a variant cannot change by more than `max_step`
  in a single update.
- This applies per-variant, per update.

Example:
- previous A = 0.30
- max_step = 0.10
- new A must be in [0.20, 0.40]

**Purpose**
- Prevents thrashing and sudden traffic shifts.
- Makes changes gradual and safer for production.

**Default (proposal)**
- `max_step = 0.10` (10 percentage points)

---

### 2.3 Minimum Evidence (`min_trials`)
**Definition**
- Do not reallocate based on a variant until it has at least `min_trials`
  observations (trials).

**Purpose**
- Prevents allocation changes from tiny samples.
- Reduces “winner by noise” behavior early in tests.

**Default (proposal)**
- `min_trials = 1000`

**Behavior**
- If any variant is below `min_trials`, the engine may:
  (A) hold allocations steady, OR
  (B) allow only very small movement
For v0, we choose:
- **Hold steady** (simple + safe)

---

### 2.4 Cooldown (`cooldown_seconds`)
**Definition**
- A minimum amount of time must pass between allocation updates.

**Purpose**
- Prevents updating too frequently (causes instability and noise chasing).
- Supports batch-oriented operation.

**Default (proposal)**
- `cooldown_seconds = 1800` (30 minutes)

**Note**
This library is stateless, so cooldown requires a timestamp input:
- `last_updated_at` (optional) and `now` (optional)

For v0:
- Cooldown is supported as an optional input.
- If not provided, cooldown is not enforced.

---

### 2.5 Weight Normalization (`normalize`)
**Definition**
- After applying other constraints, weights are normalized so they sum to 1.

**Purpose**
- Ensures consistent and valid output.

**Default**
- Always on.

---

### 2.6 Numerical Safety (`epsilon`)
**Definition**
- Small tolerance used for numerical stability and sum-to-one checks.

**Default (proposal)**
- `epsilon = 1e-9`

---

## 3. Guardrail Application Order (v0)

1) Validate inputs (non-negative, successes <= trials, weights sum to 1, etc.)
2) Check feasibility (N * min_weight <= 1)
3) If min_trials not met -> HOLD (return previous weights)
4) Apply strategy to propose raw weights
5) Apply max_step clamping
6) Apply min_weight floor
7) Normalize to sum to 1
8) Produce explanation (what happened and why)

---

## 4. Hold Behavior

When guardrails block reallocation, the engine returns:
- `weights = previous_weights`
- explanation clearly stating:
  - reason for hold (e.g. insufficient trials, cooldown not met)
  - which thresholds were not met

Holding steady is a valid and expected outcome.

---

## 5. Explainability Requirements

The result explanation should include at minimum:
- strategy name
- input summary (N variants, totals)
- whether allocation changed or held
- guardrails applied
- hold reason (if held)
- any clamping/flooring that materially changed raw weights

---

## 6. Defaults Summary (v0 proposals)

- min_weight: 0.05
- max_step: 0.10
- min_trials: 1000
- cooldown_seconds: 1800 (optional enforcement)
- epsilon: 1e-9
- normalize: always

