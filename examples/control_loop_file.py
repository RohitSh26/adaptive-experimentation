from __future__ import annotations

import argparse
import json
import os
from collections.abc import Mapping
from dataclasses import asdict
from pathlib import Path

from adaptive_experimentation import Constraints, Observation
from adaptive_experimentation.explanations import AllocationExplanation
from adaptive_experimentation.integrations.control_loop import run_once
from adaptive_experimentation.integrations.protocols import AllocationStore, ObservationSource


class FileAllocationStore(AllocationStore):
    """Weights stored in a local JSON file (demo-only)."""

    def __init__(self, path: Path):
        self.path = path

    def read_weights(self, experiment_id: str) -> Mapping[str, float]:
        data = json.loads(self.path.read_text())
        if not isinstance(data, dict):
            raise ValueError("weights.json must be an object mapping variant_id -> float")
        return {str(k): float(v) for k, v in data.items()}

    def write_weights(
        self,
        experiment_id: str,
        weights: Mapping[str, float],
        explanation: AllocationExplanation,
    ) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(dict(weights), indent=2, sort_keys=True))


class FileObservationSource(ObservationSource):
    """Observations stored in a local JSON file (demo-only)."""

    def __init__(self, path: Path):
        self.path = path

    def read_observations(
        self,
        experiment_id: str,
        window_start_epoch_s: int,
        window_end_epoch_s: int,
    ) -> Mapping[str, Observation]:
        raw = json.loads(self.path.read_text())
        if not isinstance(raw, dict):
            raise ValueError(
                "observations.json must be an object mapping variant_id -> {trials, successes}"
            )
        out: dict[str, Observation] = {}
        for vid, obj in raw.items():
            if not isinstance(obj, dict):
                raise ValueError(f"observations[{vid}] must be an object")
            out[str(vid)] = Observation(trials=int(obj["trials"]), successes=int(obj["successes"]))
        return out


def _bar(p: float, width: int = 20) -> str:
    n = max(0, min(width, int(round(p * width))))
    return "█" * n + " " * (width - n)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a single control loop using file-based inputs."
    )
    parser.add_argument("--experiment-id", default="example_exp")
    parser.add_argument("--strategy", choices=["heuristic", "thompson"], default="heuristic")
    parser.add_argument("--constraints", choices=["safe", "neutral", "explore"], default="neutral")
    parser.add_argument(
        "--seed", type=int, default=None, help="Optional seed for deterministic runs (Thompson)."
    )
    parser.add_argument("--window-start", type=int, default=0)
    parser.add_argument("--window-end", type=int, default=60)

    parser.add_argument("--weights", default="examples/data/weights.json")
    parser.add_argument("--observations", default="examples/data/observations.json")
    parser.add_argument("--out-dir", default="examples/out")

    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    store = FileAllocationStore(path=Path(args.weights))
    source = FileObservationSource(path=Path(args.observations))

    constraints = {
        "safe": Constraints.safe_defaults(),
        "neutral": Constraints.neutral_defaults(),
        "explore": Constraints.explore_defaults(),
    }[args.constraints]

    result = run_once(
        experiment_id=args.experiment_id,
        window_start_epoch_s=args.window_start,
        window_end_epoch_s=args.window_end,
        store=store,
        source=source,
        strategy=args.strategy,
        constraints=constraints,
        seed=args.seed,
    )

    # Always write an explanation artifact for inspection.
    explanation_path = out_dir / "explanation.json"
    explanation_path.write_text(
        json.dumps(asdict(result.allocation.explanation), indent=2, sort_keys=True)
    )

    # Also copy updated weights to out dir (so we don't overwrite source file)
    weights_out_path = out_dir / "weights_updated.json"
    weights_out_path.write_text(json.dumps(result.allocation.weights, indent=2, sort_keys=True))

    changed = result.wrote_update
    top = sorted(result.allocation.weights.items(), key=lambda kv: kv[1], reverse=True)[:3]

    print(
        f"experiment={args.experiment_id} | strategy={args.strategy} | changed={changed} | "
        f"hold={result.allocation.explanation.guardrails.hold_reason or 'none'}"
    )
    for vid, w in top:
        print(f"  {vid}: {w:.4f} {_bar(w)}")

    print(f"\nWrote: {weights_out_path}")
    print(f"Wrote: {explanation_path}")


if __name__ == "__main__":
    # Avoid any surprises if someone runs from weird cwd.
    os.chdir(Path(__file__).resolve().parents[1])
    main()
