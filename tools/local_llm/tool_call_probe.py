#!/usr/bin/env python3
"""Probe tool-call compliance for an OpenAI-compatible endpoint."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Chat completions URL")
    parser.add_argument("--model", required=True, help="Model name")
    parser.add_argument("--tool-name", default="add", help="Tool name")
    parser.add_argument("--a", type=int, default=2, help="First operand")
    parser.add_argument("--b", type=int, default=3, help="Second operand")
    return parser.parse_args()


def parse_arguments(raw: Any) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    if raw is None:
        return None, "missing arguments"
    if isinstance(raw, dict):
        return raw, None
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            return None, f"arguments not valid JSON ({exc})"
        if not isinstance(parsed, dict):
            return None, "arguments JSON is not an object"
        return parsed, None
    return None, f"unsupported arguments type: {type(raw).__name__}"


def validate_tool_call(message: Dict[str, Any], tool_name: str, a: int, b: int) -> Tuple[bool, str]:
    tool_calls = message.get("tool_calls")
    if not tool_calls:
        content = message.get("content", "")
        return False, f"missing tool_calls (content={content})"

    first = tool_calls[0] if isinstance(tool_calls, list) else None
    if not isinstance(first, dict):
        return False, "tool_calls[0] is not an object"

    function = first.get("function")
    if not isinstance(function, dict):
        return False, "tool_calls[0].function missing or invalid"

    name = function.get("name")
    if name != tool_name:
        return False, f"unexpected function name ({name})"

    args, err = parse_arguments(function.get("arguments"))
    if err:
        return False, err

    got_a = args.get("a")
    got_b = args.get("b")
    if got_a != a or got_b != b:
        return False, f"unexpected arguments (a={got_a}, b={got_b})"

    return True, "ok"


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
    ok, reason = validate_tool_call(message, args.tool_name, args.a, args.b)
    if ok:
        print("Tool-call compliant")
        return 0
    print(f"Tool-call invalid: {reason}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
