# examples/multi_window.py
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict

from adaptive_experimentation import Constraints, Engine, Observation


def _maybe_plot(weights_csv: str, out_png: str = "weights_over_time.png") -> None:
    """Optional: plot weights over time to a PNG if matplotlib is installed."""
    try:
        import matplotlib.pyplot as plt
    except Exception:
        print("matplotlib not installed; skipping plot.")
        return

    rows = []
    with open(weights_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    if not rows:
        print("No rows found; skipping plot.")
        return

    meta = {"window", "strategy", "total_trials", "total_successes"}
    variant_cols = [c for c in rows[0].keys() if c not in meta]

    x = [int(r["window"]) for r in rows]
    for v in variant_cols:
        y = [float(r[v]) for r in rows]
        plt.plot(x, y, label=v)

    plt.xlabel("window")
    plt.ylabel("weight")
    plt.title("Weights over time")
    plt.legend(loc="best")
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()
    print(f"Wrote: {out_png}")


def _bar(x: float, width: int = 24) -> str:
    # simple ASCII bar for weights in [0,1]
    filled = int(round(max(0.0, min(1.0, x)) * width))
    return "█" * filled + " " * (width - filled)


def _print_window_summary(
    *,
    window: int,
    min_trails_seen: int,
    weights: dict[str, float],
    changed: bool,
    hold_reason: str | None,
    top_k: int = 3,
) -> None:
    ranked = sorted(weights.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
    parts = []
    for v, w in ranked:
        parts.append(f"{v} {w:.3f} {_bar(w, 18)}")
    msg = f"window {window:02d} | min_trails_seen={min_trails_seen} | changed={changed}"
    if hold_reason:
        msg += f" | hold={hold_reason}"
    msg += " | top: " + "  ".join(parts)
    print(msg)


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
    lifts: dict[str, float],
    seed: int,
    assignment_weights: dict[str, float],
) -> dict[str, Observation]:
    """Simulate a window, then aggregate to Observation(trials, successes)."""
    import random

    rng = random.Random(seed)

    # CTR per variant = base + lift (clamped to [0,1])
    ctr: dict[str, float] = {}
    for v in variants:
        ctr[v] = max(0.0, min(1.0, base_ctr + lifts.get(v, 0.0)))

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

    return {v: Observation(trials=trials[v], successes=successes[v]) for v in variants}


def main() -> int:
    p = argparse.ArgumentParser(
        description="Multi-window simulation: run N windows, update weights each window, write CSV."
    )
    p.add_argument("--strategy", choices=["heuristic", "thompson"], default="thompson")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--windows", type=int, default=30)
    p.add_argument("--variants", type=int, default=5)
    p.add_argument("--impressions-per-window", type=int, default=50_000)
    p.add_argument("--base-ctr", type=float, default=0.06)

    # Simple lift model: one winner + optional runner-up
    p.add_argument("--winner", type=str, default="B")
    p.add_argument("--winner-lift", type=float, default=0.02)
    p.add_argument("--runner-up", type=str, default="")
    p.add_argument("--runner-up-lift", type=float, default=0.01)

    # Guardrails
    p.add_argument("--min-trials", type=int, default=3_000)
    p.add_argument("--max-step", type=float, default=0.10)
    p.add_argument("--min-weight", type=float, default=0.05)

    # Outputs
    p.add_argument("--weights-csv", type=str, default="weights_over_time.csv")
    p.add_argument("--explanations-jsonl", type=str, default="explanations_over_time.jsonl")

    args = p.parse_args()

    variants = tuple(chr(ord("A") + i) for i in range(args.variants))
    if args.winner not in variants:
        raise SystemExit(f"--winner must be one of {variants}, got {args.winner!r}")
    if args.runner_up and args.runner_up not in variants:
        raise SystemExit(f"--runner-up must be one of {variants}, got {args.runner_up!r}")

    lifts: dict[str, float] = {args.winner: args.winner_lift}
    if args.runner_up:
        lifts[args.runner_up] = args.runner_up_lift

    engine = Engine(strategy=args.strategy)
    constraints = Constraints(
        min_trials=args.min_trials,
        max_step=args.max_step,
        min_weight=args.min_weight,
    )

    # Start uniformly
    weights: dict[str, float] = {v: 1.0 / len(variants) for v in variants}

    # Prepare CSV output
    with (
        open(args.weights_csv, "w", newline="", encoding="utf-8") as f_csv,
        open(args.explanations_jsonl, "w", encoding="utf-8") as f_jsonl,
    ):
        writer = csv.DictWriter(
            f_csv,
            fieldnames=["window", "strategy", "total_trials", "total_successes", *variants],
        )
        writer.writeheader()

        for w in range(args.windows):
            # Deterministic window seed per window for reproducibility
            window_seed = args.seed + w

            observations = simulate_window(
                variants=variants,
                impressions=args.impressions_per_window,
                base_ctr=args.base_ctr,
                lifts=lifts,
                seed=window_seed,
                assignment_weights=weights,
            )

            min_trials_seen = min(o.trials for o in observations.values())

            result = engine.compute(
                observations=observations,
                previous_weights=weights,
                constraints=constraints,
                seed=window_seed,  # also makes Thompson reproducible per window
            )

            _print_window_summary(
                window=w,
                min_trails_seen=min_trials_seen,
                weights=dict(result.weights),
                changed=result.explanation.guardrails.changed,
                hold_reason=result.explanation.guardrails.hold_reason,
                top_k=min(3, len(variants)),
            )

            total_trials = sum(o.trials for o in observations.values())
            total_successes = sum(o.successes for o in observations.values())

            # Write CSV row
            row = {
                "window": w,
                "strategy": result.explanation.strategy.name,
                "total_trials": total_trials,
                "total_successes": total_successes,
            }
            for v in variants:
                row[v] = result.weights[v]
            writer.writerow(row)

            # Write explanation JSONL (one json object per line)
            payload = {
                "window": w,
                "previous_weights": weights,
                "final_weights": result.weights,
                "explanation": asdict(result.explanation),
            }
            f_jsonl.write(json.dumps(payload) + "\n")

            # Feed forward
            weights = dict(result.weights)

    print(f"Wrote: {args.weights_csv}")
    print(f"Wrote: {args.explanations_jsonl}")
    print("Tip: open the CSV to see weights converging over time.")
    _maybe_plot(args.weights_csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
