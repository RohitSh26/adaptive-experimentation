# examples/end_to_end.py
from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from adaptive_experimentation import Constraints, Engine, Observation


def _normalize(weights: dict[str, float]) -> dict[str, float]:
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("weights must sum to > 0")
    return {k: v / total for k, v in weights.items()}


def simulate_window(
    *,
    variants: tuple[str, ...],
    impressions: int,
    base_ctr: float,
    winner: str,
    lift: float,
    seed: int,
    assignment_weights: dict[str, float],
) -> dict[str, Observation]:
    """
    Simulate a single time window:
      - choose a variant per impression using assignment_weights
      - generate click using per-variant CTR
      - aggregate to Observation(trials, successes)
    """
    import random

    rng = random.Random(seed)

    # CTR per variant
    ctr: dict[str, float] = {v: base_ctr for v in variants}
    if winner in ctr:
        ctr[winner] = max(0.0, min(1.0, base_ctr + lift))

    # Prepare weighted sampling
    weights = _normalize(dict(assignment_weights))
    variant_list = list(variants)
    weight_list = [weights[v] for v in variant_list]

    trials = {v: 0 for v in variants}
    successes = {v: 0 for v in variants}

    for _ in range(impressions):
        v = rng.choices(variant_list, weights=weight_list, k=1)[0]
        trials[v] += 1
        if rng.random() < ctr[v]:
            successes[v] += 1

    observations: dict[str, Observation] = {
        v: Observation(trials=trials[v], successes=successes[v]) for v in variants
    }
    return observations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="End-to-end example: simulate window -> aggregate -> compute next weights."
    )
    parser.add_argument(
        "--strategy",
        choices=["heuristic", "thompson"],
        default="thompson",
        help="Allocation strategy to use.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed used for simulation and (for Thompson) reproducible sampling.",
    )
    parser.add_argument(
        "--variants",
        type=int,
        default=3,
        help="Number of variants (A, B, C...).",
    )
    parser.add_argument(
        "--impressions",
        type=int,
        default=50_000,
        help="Total impressions in the simulated window.",
    )
    parser.add_argument(
        "--base-ctr",
        type=float,
        default=0.06,
        help="Base click-through rate.",
    )
    parser.add_argument(
        "--winner",
        type=str,
        default="B",
        help="Variant with positive lift (default: B).",
    )
    parser.add_argument(
        "--lift",
        type=float,
        default=0.02,
        help="CTR lift applied to the winner variant (base_ctr + lift).",
    )
    parser.add_argument(
        "--min-trials",
        type=int,
        default=5_000,
        help="Guardrail: minimum trials required before weights can change.",
    )
    parser.add_argument(
        "--max-step",
        type=float,
        default=0.10,
        help="Guardrail: maximum absolute change allowed per run.",
    )
    parser.add_argument(
        "--min-weight",
        type=float,
        default=0.05,
        help="Guardrail: minimum weight floor per variant.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="next_weights.json",
        help="Where to write next weights (JSON).",
    )
    args = parser.parse_args()

    # Build variant ids: A, B, C, ...
    variants = tuple(chr(ord("A") + i) for i in range(args.variants))
    if args.winner not in variants:
        raise SystemExit(
            f"--winner must be one of {variants}, got {args.winner!r}")

    # Start with uniform previous weights
    previous_weights = {v: 1.0 / len(variants) for v in variants}

    # Simulate one window of data using the previous weights as assignment weights
    observations = simulate_window(
        variants=variants,
        impressions=args.impressions,
        base_ctr=args.base_ctr,
        winner=args.winner,
        lift=args.lift,
        seed=args.seed,
        assignment_weights=previous_weights,
    )

    # Compute next weights
    engine = Engine(strategy=args.strategy)
    constraints = Constraints(
        min_trials=args.min_trials,
        max_step=args.max_step,
        min_weight=args.min_weight,
    )

    result = engine.compute(
        observations=observations,
        previous_weights=previous_weights,
        constraints=constraints,
        seed=args.seed,  # important for Thompson reproducibility
    )

    # Pretty print summary
    total_trials = sum(o.trials for o in observations.values())
    total_successes = sum(o.successes for o in observations.values())
    print("\n=== Simulated window ===")
    print(f"variants: {variants}")
    print(f"impressions: {args.impressions}")
    print(
        f"base_ctr: {args.base_ctr:.4f} | winner: {args.winner} | lift: {args.lift:.4f}")
    print(
        f"total trials: {total_trials} | total successes: {total_successes}\n")

    print("Per-variant observed CTR:")
    for v in variants:
        o = observations[v]
        ctr = (o.successes / o.trials) if o.trials else 0.0
        print(
            f"  {v}: trials={o.trials:6d} successes={o.successes:5d} ctr={ctr:.4%}")

    print("\n=== Allocation ===")
    print(f"strategy: {result.explanation.strategy.name}")
    print(f"previous weights: {previous_weights}")
    print(f"proposed weights: {dict(result.explanation.proposed_weights)}")
    print(f"final weights:    {result.weights}")

    gr = result.explanation.guardrails
    print("\n=== Guardrails ===")
    print(f"changed: {gr.changed}")
    if gr.hold_reason:
        print(f"hold_reason: {gr.hold_reason}")
    if gr.guardrails_applied:
        print(f"guardrails_applied: {list(gr.guardrails_applied)}")
    if gr.max_step_clamps:
        print(f"max_step_clamps: {dict(gr.max_step_clamps)}")
    if gr.min_weight_floors:
        print(f"min_weight_floors: {dict(gr.min_weight_floors)}")

    # Write next weights to JSON (what a real system would persist to config storage)
    payload = {
        "next_weights": result.weights,
        "explanation": asdict(result.explanation),
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)

    print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
