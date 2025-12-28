# Changelog

All notable changes to this project will be documented in this file.

This project follows a pragmatic pre-1.0 versioning approach:
breaking changes may occur in minor versions while the API stabilizes.

## [0.1.0] - 2025-12-28

### Added
- Thompson Sampling strategy (Beta-Bernoulli) for binary outcomes.
- Safety-first guardrails (min_trials, max_step, min_weight) with clear explanations.
- Typed, immutable explanation schema (frozen dataclasses) with easy serialization.
- End-to-end examples:
  - Single-window demo
  - Multi-window simulation showing adaptive learning over time
- CI (GitHub Actions), formatting/linting (ruff), and tests (pytest).

### Changed
- `AllocationResult.explanation` is now a structured dataclass (typed explanation schema)
  instead of a loosely-typed dict. Use `dataclasses.asdict(result.explanation)` or
  `result.explanation.to_dict()` for JSON-friendly output.

## [0.1.1] - 2025-12-28

### Changed
- Added packaging metadata (keywords, classifiers) to improve discoverability.