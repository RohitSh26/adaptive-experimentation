# Design Philosophy

This project is intentionally conservative.

Many experimentation and bandit libraries optimize aggressively by default.
In production systems, this can lead to instability, user harm, or hard-to-explain
outcomes.

## Core beliefs

### Safety beats speed
If there is insufficient data, the system should **hold**, not guess.

### Explanations are mandatory
Every allocation decision should answer:
- Why did weights change?
- Why didn’t they change?
- What constraints applied?

### Infrastructure should be optional
This library does not assume streaming systems, feature flags, or specific vendors.

### Learning happens over windows
Traffic allocation should evolve gradually over discrete observation windows,
not on every event.

---

This philosophy drives:
- guardrails
- strategy interfaces
- typed explanation schemas
