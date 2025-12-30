# Changelog

All notable changes to this project will be documented in this file.

This project follows a pragmatic pre-1.0 versioning approach:
breaking changes may occur in minor versions while the API stabilizes.

---

## [0.1.2] - 2025-12-30

### Added
- Streaming-style, windowed control loop example demonstrating how adaptive experimentation
  operates in real-world event-driven systems (e.g. Event Hubs, Kafka-style ingestion).
- File-based control loop example using local JSON files for zero-infrastructure demos.
- HTTP-based control loop example illustrating integration with external config and metrics services.
- Mock HTTP service to enable fully local, end-to-end testing of HTTP integrations.
- Integration protocols (`AllocationStore`, `ObservationSource`) and a reusable `run_once`
  control loop runner with comprehensive tests.
- Safety constraint presets (`safe`, `neutral`, `explore`) with documented recommended defaults.
- Deterministic execution support for Thompson Sampling via optional `seed` parameter.
- Reproducibility tests ensuring deterministic behavior does not regress.

### Changed
- Control loop CLI output now reports hold reasons from guardrails
  (`explanation.guardrails.hold_reason`) for greater clarity and correctness.
- Improved README positioning, examples, and reproducibility guidance.
- Expanded documentation to better explain operational usage and guardrail behavior.

### Docs
- Added reproducibility section explaining deterministic Thompson Sampling.
- Documented constraint presets and operational guidance.
- Added initial GitHub Pages documentation.
- Added multi-window visualization to illustrate learning dynamics over time.

---

## [0.1.1] - 2025-12-28

### Changed
- Added packaging metadata (keywords, classifiers) to improve discoverability.

---

## [0.1.0] - 2025-12-28

### Added
- Thompson Sampling strategy (Beta-Bernoulli) for binary outcomes.
- Safety-first guardrails (`min_trials`, `max_step`, `min_weight`) with clear explanations.
- Typed, immutable explanation schema (frozen dataclasses) with easy serialization.
- End-to-end examples:
  - Single-window demo
  - Multi-window simulation showing adaptive learning over time
- CI (GitHub Actions), formatting/linting (ruff), and tests (pytest).

### Changed
- `AllocationResult.explanation` is now a structured dataclass (typed explanation schema)
  instead of a loosely-typed dict. Use `dataclasses.asdict(result.explanation)` or
  `result.explanation.to_dict()` for JSON-friendly output.