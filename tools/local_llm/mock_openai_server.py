#!/usr/bin/env python3
"""Minimal OpenAI-compatible mock server for probe testing.

Implements:
- POST /v1/chat/completions
- GET  /v1/models

Behavior is controlled by the requested "model" string.
"""

from __future__ import annotations

import argparse
import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18080)
    return parser.parse_args()


def read_json(handler: BaseHTTPRequestHandler) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    length = int(handler.headers.get("Content-Length", "0") or "0")
    raw = handler.rfile.read(length).decode("utf-8", errors="replace")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON ({exc})"
    if not isinstance(data, dict):
        return None, "request JSON is not an object"
    return data, None


def send_json(handler: BaseHTTPRequestHandler, status: int, payload: Dict[str, Any]) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    server_version = "mock-openai/0.1"

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        # Silence default logging (tests assert on clean output).
        return

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/v1/models":
            self.send_response(404)
            self.end_headers()
            return
        send_json(
            self,
            200,
            {
                "object": "list",
                "data": [
                    {"id": "ok", "object": "model", "owned_by": "mock"},
                    {"id": "missing_tool_calls", "object": "model", "owned_by": "mock"},
                ],
            },
        )

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/chat/completions":
            self.send_response(404)
            self.end_headers()
            return

        data, err = read_json(self)
        if err:
            send_json(self, 400, {"error": {"message": err}})
            return

        model = str((data or {}).get("model", "ok"))
        if model == "timeout":
            time.sleep(5)
            send_json(self, 200, {"choices": [{"message": {"role": "assistant", "content": "late"}}]})
            return

        if model == "http_500":
            send_json(self, 500, {"error": {"message": "simulated server error"}})
            return

        if model == "missing_tool_calls":
            send_json(
                self,
                200,
                {"choices": [{"message": {"role": "assistant", "content": "{\"name\":\"add\"}"}}]},
            )
            return

        if model == "invalid_arguments_json":
            send_json(
                self,
                200,
                {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "tool_calls": [
                                    {"function": {"name": "add", "arguments": "{not json"}}
                                ],
                            }
                        }
                    ]
                },
            )
            return

        # Default: valid tool call.
        send_json(
            self,
            200,
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "tool_calls": [
                                {"function": {"name": "add", "arguments": {"a": 2, "b": 3}}}
                            ],
                        }
                    }
                ],
                "usage": {"completion_tokens": 4},
            },
        )


def main() -> int:
    args = parse_args()
    server = HTTPServer((args.host, args.port), Handler)
    print(f"listening on http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

