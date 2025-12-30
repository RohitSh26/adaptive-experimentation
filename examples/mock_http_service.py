from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

# In-memory state (demo only)
STATE = {
    "weights": {"A": 0.5, "B": 0.5},
    "observations": {
        "A": {"trials": 2000, "successes": 100},
        "B": {"trials": 2000, "successes": 300},
    },
}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: object) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = self.path

        # weights: /experiments/{experiment_id}/weights
        if "/weights" in path:
            return self._send(200, STATE["weights"])

        # observations: /experiments/{experiment_id}/observations?start=..&end=..
        if "/observations" in path:
            # We ignore window bounds for demo, but parse them to validate.
            q = parse_qs(urlparse(path).query)
            _ = int(q.get("start", ["0"])[0])
            _ = int(q.get("end", ["0"])[0])
            return self._send(200, STATE["observations"])

        return self._send(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = self.path
        if "/weights" not in path:
            return self._send(404, {"error": "not found"})

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        payload = json.loads(raw)

        weights = payload.get("weights")
        if not isinstance(weights, dict):
            return self._send(400, {"error": "payload must include object 'weights'"})

        STATE["weights"] = {str(k): float(v) for k, v in weights.items()}
        return self._send(200, {"ok": True, "weights": STATE["weights"]})

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        # Silence server logs for cleaner demo output.
        return


def main() -> None:
    host = "127.0.0.1"
    port = 8000
    print(f"Mock HTTP service running at http://{host}:{port}")
    HTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
