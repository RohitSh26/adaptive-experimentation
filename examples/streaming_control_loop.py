from __future__ import annotations

import argparse
import random
import time
from collections.abc import Mapping
from dataclasses import dataclass

from adaptive_experimentation import Constraints, Observation
from adaptive_experimentation.explanations import AllocationExplanation
from adaptive_experimentation.integrations.control_loop import run_once
from adaptive_experimentation.integrations.protocols import AllocationStore, ObservationSource


@dataclass
class InMemoryStore(AllocationStore):
    weights: dict[str, float]
    writes: int = 0

    def read_weights(self, experiment_id: str) -> Mapping[str, float]:
        return dict(self.weights)

    def write_weights(
        self,
        experiment_id: str,
        weights: Mapping[str, float],
        explanation: AllocationExplanation,
    ) -> None:
        self.weights = dict(weights)
        self.writes += 1


@dataclass
class WindowedAggregator(ObservationSource):
    """Aggregates a continuous stream into windowed Observation counts.

    In production, this would usually read from a datastore populated by stream processors.
    Here we keep it in-memory to demonstrate the control loop pattern.
    """

    counts: dict[str, Observation]

    def read_observations(
        self,
        experiment_id: str,
        window_start_epoch_s: int,
        window_end_epoch_s: int,
    ) -> Mapping[str, Observation]:
        # Return a snapshot (don't hand out internal references)
        return {k: Observation(v.trials, v.successes) for k, v in self.counts.items()}

    def reset_window(self) -> None:
        for k in list(self.counts.keys()):
            self.counts[k] = Observation(trials=0, successes=0)


def _bar(p: float, width: int = 24) -> str:
    n = max(0, min(width, int(round(p * width))))
    return "█" * n + " " * (width - n)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Streaming-style control loop simulation (windowed updates)."
    )
    parser.add_argument("--strategy", choices=["heuristic", "thompson"], default="thompson")
    parser.add_argument("--constraints", choices=["safe", "neutral", "explore"], default="neutral")
    parser.add_argument(
        "--seed", type=int, default=42, help="Seed for deterministic Thompson (optional)."
    )
    parser.add_argument("--variants", type=int, default=5)
    parser.add_argument("--winner", default="B")
    parser.add_argument("--base_ctr", type=float, default=0.10)
    parser.add_argument(
        "--winner_lift",
        type=float,
        default=0.03,
        help="Absolute CTR lift for winner (e.g. 0.03 => +3%).",
    )

    parser.add_argument("--events_per_second", type=int, default=200)
    parser.add_argument("--window_seconds", type=int, default=10)
    parser.add_argument("--windows", type=int, default=12)
    args = parser.parse_args()

    rng = random.Random(args.seed)

    # Variant IDs like A, B, C...
    vids = [chr(ord("A") + i) for i in range(args.variants)]
    if args.winner not in vids:
        raise SystemExit(f"--winner must be one of: {vids}")

    # CTRs per variant (winner gets a lift)
    ctr: dict[str, float] = {v: args.base_ctr for v in vids}
    ctr[args.winner] = min(0.99, args.base_ctr + args.winner_lift)

    # Initial weights: uniform
    store = InMemoryStore(weights={v: 1.0 / len(vids) for v in vids})

    # Aggregator starts with 0 counts
    source = WindowedAggregator(counts={v: Observation(trials=0, successes=0) for v in vids})

    constraints = {
        "safe": Constraints.safe_defaults(),
        "neutral": Constraints.neutral_defaults(),
        "explore": Constraints.explore_defaults(),
    }[args.constraints]

    experiment_id = "streaming_example"

    print(
        f"variants={vids} winner={args.winner} base_ctr={args.base_ctr:.3f} "
        f"winner_ctr={ctr[args.winner]:.3f}"
    )
    print(
        f"strategy={args.strategy} constraints={args.constraints} "
        f"window_seconds={args.window_seconds} "
        f"windows={args.windows}\n"
    )

    for w in range(args.windows):
        # Simulate a "stream" for one window: we emit events continuously
        start = int(time.time())
        end = start + args.window_seconds

        # Generate events for this window
        total_events = args.events_per_second * args.window_seconds
        for _ in range(total_events):
            # route event to a variant based on current weights
            r = rng.random()
            cum = 0.0
            chosen = vids[-1]
            for v in vids:
                cum += store.weights[v]
                if r <= cum:
                    chosen = v
                    break

            # exposure
            obs = source.counts[chosen]
            source.counts[chosen] = Observation(trials=obs.trials + 1, successes=obs.successes)

            # click based on CTR
            if rng.random() < ctr[chosen]:
                obs2 = source.counts[chosen]
                source.counts[chosen] = Observation(
                    trials=obs2.trials, successes=obs2.successes + 1
                )

        # Run the control loop once per window
        result = run_once(
            experiment_id=experiment_id,
            window_start_epoch_s=start,
            window_end_epoch_s=end,
            store=store,
            source=source,
            strategy=args.strategy,
            constraints=constraints,
            seed=args.seed if args.strategy == "thompson" else None,
        )

        hold = result.allocation.explanation.guardrails.hold_reason or "none"
        changed = result.wrote_update

        top = sorted(result.allocation.weights.items(), key=lambda kv: kv[1], reverse=True)[:3]
        print(f"window {w:02d} | changed={changed} | hold={hold}")
        for v, wt in top:
            print(f"  {v} {wt:.3f} {_bar(wt)}")
        print("")

        # Reset window counts (new window)
        source.reset_window()

    print(f"writes={store.writes} final_top={max(store.weights, key=store.weights.get)}")
    print("final_weights:", store.weights)


if __name__ == "__main__":
    main()
