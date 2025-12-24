# Concepts and Terminology

This document defines the core concepts used throughout the
**adaptive-experimentation** project.

The goal is to ensure shared understanding across Search,
Personalization, and Experimentation teams.

---

## 1. The Problem We Are Solving

Traditional A/B testing fixes traffic allocation at the start
of an experiment and waits until the end to make decisions.

This leads to:
- Long periods where users see clearly worse variants
- Lost opportunity while experiments run
- Slow feedback loops for Search and Personalization systems

Adaptive experimentation addresses this by:
- Observing outcomes during the experiment
- Gradually shifting more traffic toward better-performing variants
- Continuing to explore alternatives safely

---

## 2. Variant

A **Variant** is a discrete option being evaluated.

Examples:
- Different ranking algorithms
- Different recommendation models
- Different feature configurations
- Different UI treatments

In this library:
- A variant is identified by a **string ID**
- The library does not know or care what the variant does
- Variants are treated as abstract options

---

## 3. Observation

An **Observation** represents aggregated performance data
for a variant over a time window.

Typical examples:
- Impressions and clicks
- Requests and conversions
- Attempts and successes

Important properties:
- Observations are **aggregated**, not per-user
- Observations are assumed to be computed upstream
- The library does not perform attribution or logging

---

## 4. Weight (Traffic Allocation)

A **Weight** represents the fraction of future traffic
that should be assigned to a variant.

Properties:
- Weights are values between 0 and 1
- All weights must sum to 1
- Weights apply to **future assignments**, not past users

Example:
A: 0.5
B: 0.3
C: 0.2
---

## 5. Allocation

**Allocation** is the process of determining weights
based on observations and constraints.

This library:
- Computes new allocations
- Does NOT assign users to variants
- Does NOT persist allocations

---

## 6. Constraints (Guardrails)

**Constraints** are safety rules that limit how allocations
are allowed to change.

Examples:
- Minimum exploration floor (e.g. every variant gets ≥ 5%)
- Maximum step change per update
- Minimum data requirements before reallocating

Constraints are:
- First-class concepts
- Applied deterministically
- Always explainable

---

## 7. Explainability

Every allocation decision should be explainable.

Explainability includes:
- Which variant performed best
- Why weights changed (or did not change)
- Which constraints were applied
- Whether the signal was strong or weak

This is critical for:
- Trust
- Debugging
- Production adoption

---

## 8. Batch-Oriented Assumption

This library assumes **batch or near-batch** usage.

Examples:
- Hourly jobs
- Daily jobs
- Offline analysis

It does NOT assume:
- Streaming events
- Real-time updates
- Per-request learning

---

## 9. What This Library Is Not

This library is NOT:
- An experiment platform
- A feature flag system
- A user assignment service
- An event ingestion pipeline
- A real-time decision engine

Those concerns belong outside this project.

---

## 10. Design Philosophy

This project prioritizes:
- Safety over speed
- Clarity over cleverness
- Explainability over raw optimization
- Incremental adoption over big-bang changes

