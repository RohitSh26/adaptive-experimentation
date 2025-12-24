# Adaptive Experimentation

A safe, infrastructure-agnostic Python library for **adaptive traffic allocation** in experimentation.

This project helps Search, Recommendations, and Personalization teams
learn which variant performs better **while an experiment is running**,
and safely shift more traffic toward better-performing options.

## What this library is
- A **pure decision engine** for adaptive experimentation
- Config-agnostic (no feature flags, no infra assumptions)
- Designed for **batch or near-batch** updates (e.g. Databricks, Airflow)
- Safe by default (guardrails, explainability)

## What this library is not
- Not an experiment platform
- Not a feature flag system
- Not infra- or cloud-specific
- Not real-time streaming only

## Core idea
Given:
- Variant performance observations
- Current traffic allocation
- Safety constraints

Produce:
- New traffic weights
- Clear explanation for why they changed

## Status
🚧 **Early development** — API is not yet stable.

## License
Apache-2.0
