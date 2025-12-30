from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from dataclasses import asdict
from urllib.request import Request, urlopen

from adaptive_experimentation import Constraints, Observation
from adaptive_experimentation.explanations import AllocationExplanation
from adaptive_experimentation.integrations.control_loop import run_once
from adaptive_experimentation.integrations.protocols import AllocationStore, ObservationSource


def _get_json(url: str, headers: Mapping[str, str]) -> object:
    req = Request(url, headers=dict(headers), method="GET")
    with urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)


def _post_json(url: str, headers: Mapping[str, str], payload: object) -> object:
    data = json.dumps(payload).encode("utf-8")
    req = Request(
        url,
        headers={**dict(headers), "Content-Type": "application/json"},
        data=data,
        method="POST",
    )
    with urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body) if body else {}


class HttpAllocationStore(AllocationStore):
    """Example: read/write weights from an HTTP service.

    Expected endpoints:
      GET  {base_url}/experiments/{experiment_id}/weights -> {"A": 0.5, "B": 0.5, ...}
      POST {base_url}/experiments/{experiment_id}/weights -> accepts {"weights": {...},
      "explanation": {...}}
    """

    def __init__(self, base_url: str, headers: Mapping[str, str] | None = None):
        self.base_url = base_url.rstrip("/")
        self.headers = dict(headers or {})

    def read_weights(self, experiment_id: str) -> Mapping[str, float]:
        url = f"{self.base_url}/experiments/{experiment_id}/weights"
        data = _get_json(url, self.headers)
        if not isinstance(data, dict):
            raise ValueError("weights endpoint must return an object mapping variant_id -> float")
        return {str(k): float(v) for k, v in data.items()}

    def write_weights(
        self,
        experiment_id: str,
        weights: Mapping[str, float],
        explanation: AllocationExplanation,
    ) -> None:
        url = f"{self.base_url}/experiments/{experiment_id}/weights"
        payload = {"weights": dict(weights), "explanation": asdict(explanation)}
        _post_json(url, self.headers, payload)


class HttpObservationSource(ObservationSource):
    """Example: fetch observations from an HTTP service.

    Expected endpoint:
      GET {base_url}/experiments/{experiment_id}/observations?start=...&end=...
        -> {"A": {"trials": 1000, "successes": 123}, ...}
    """

    def __init__(self, base_url: str, headers: Mapping[str, str] | None = None):
        self.base_url = base_url.rstrip("/")
        self.headers = dict(headers or {})

    def read_observations(
        self,
        experiment_id: str,
        window_start_epoch_s: int,
        window_end_epoch_s: int,
    ) -> Mapping[str, Observation]:
        url = (
            f"{self.base_url}/experiments/{experiment_id}/observations"
            f"?start={window_start_epoch_s}&end={window_end_epoch_s}"
        )
        raw = _get_json(url, self.headers)
        if not isinstance(raw, dict):
            raise ValueError(
                "observations endpoint must return an object mapping variant_id "
                "-> {trials, successes}"
            )
        out: dict[str, Observation] = {}
        for vid, obj in raw.items():
            if not isinstance(obj, dict):
                raise ValueError(f"observations[{vid}] must be an object")
            out[str(vid)] = Observation(trials=int(obj["trials"]), successes=int(obj["successes"]))
        return out


def main() -> None:
    parser = argparse.ArgumentParser(description="HTTP integration example (pattern/template).")
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument(
        "--base-url", required=True, help="Base URL for your config/metrics service."
    )
    parser.add_argument("--strategy", choices=["heuristic", "thompson"], default="thompson")
    parser.add_argument("--constraints", choices=["safe", "neutral", "explore"], default="neutral")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--window-start", type=int, required=True)
    parser.add_argument("--window-end", type=int, required=True)

    args = parser.parse_args()

    constraints = {
        "safe": Constraints.safe_defaults(),
        "neutral": Constraints.neutral_defaults(),
        "explore": Constraints.explore_defaults(),
    }[args.constraints]

    store = HttpAllocationStore(base_url=args.base_url)
    source = HttpObservationSource(base_url=args.base_url)

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

    print(
        f"changed={result.wrote_update} | "
        f"hold={result.allocation.explanation.guardrails.hold_reason} | "
        f"top={max(result.allocation.weights, key=result.allocation.weights.get)}"
    )


if __name__ == "__main__":
    main()
