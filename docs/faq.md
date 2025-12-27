# Frequently Asked Questions

### What problem does this library solve?
It helps you **adapt traffic allocation safely over time** using aggregated results.

---

### Is this a replacement for A/B testing?
No. It complements A/B testing by reducing opportunity cost during experiments.

---

### Why didn’t my weights change?
Common reasons:
- `min_trials` not met
- `max_step` limited movement
- `min_weight` floor applied

The explanation tells you exactly why.

---

### Why are `previous_weights` required?
They allow:
- bounded movement
- explainability
- stability across runs

Without them, safe adaptation is impossible.

---

### How do I choose guardrails?
Start conservative:
- high `min_trials`
- low `max_step`
- non-zero `min_weight`

Tune later based on stability.

---

### How often should I run the engine?
In batch:
- hourly for high traffic
- daily for moderate traffic
- longer windows for low traffic

Never per event.

---

### Why are Thompson results different each run?
Thompson Sampling is stochastic by design.
Use `seed` to make runs reproducible.

---

### Does this do personalization?
No. This operates at the **variant level**, not user level.

---

### Can it optimize revenue?
Not directly. Current strategies assume binary outcomes
(e.g. click / no click).

---

### What if my data arrives late?
Run the engine only after the window is complete.
Late data should be handled upstream.

---

### Can I add or remove variants mid-run?
It’s safer to treat that as a new experiment
and reset weights intentionally.
