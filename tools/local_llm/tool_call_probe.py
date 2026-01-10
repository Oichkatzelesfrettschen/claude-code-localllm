#!/usr/bin/env python3
"""Probe tool-call compliance for an OpenAI-compatible endpoint."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Chat completions URL")
    parser.add_argument("--model", required=True, help="Model name")
    parser.add_argument("--tool-name", default="add", help="Tool name")
    parser.add_argument("--a", type=int, default=2, help="First operand")
    parser.add_argument("--b", type=int, default=3, help="Second operand")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = {
        "model": args.model,
        "messages": [
            {
                "role": "user",
                "content": f"Call tool {args.tool_name} with a={args.a} and b={args.b}.",
            }
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": args.tool_name,
                    "description": "Add two integers",
                    "parameters": {
                        "type": "object",
                        "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                        "required": ["a", "b"],
                    },
                },
            }
        ],
        "tool_choice": "auto",
        "temperature": 0,
    }

    request = urllib.request.Request(
        args.url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace").strip()
        detail = body or "no error body"
        print(f"Tool-call probe failed: HTTP {exc.code} ({detail})")
        return 1

    message = data.get("choices", [{}])[0].get("message", {})
    tool_calls = message.get("tool_calls")

    if tool_calls:
        print("Tool-call compliant")
        return 0

    content = message.get("content", "")
    print("Tool-call missing; model returned content:", content)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
