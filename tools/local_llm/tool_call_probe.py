#!/usr/bin/env python3
"""Probe tool-call compliance for an OpenAI-compatible endpoint."""

from __future__ import annotations

import argparse
import json
import socket
import urllib.error
import urllib.request
from typing import Any, Dict

from probe_common import parse_arguments


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Chat completions URL")
    parser.add_argument("--model", required=True, help="Model name")
    parser.add_argument("--tool-name", default="add", help="Tool name")
    parser.add_argument("--a", type=int, default=2, help="First operand")
    parser.add_argument("--b", type=int, default=3, help="Second operand")
    parser.add_argument("--timeout-sec", type=int, default=60, help="Request timeout")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")
    return parser.parse_args()


def validate_tool_call(message: Dict[str, Any], tool_name: str, a: int, b: int) -> tuple[bool, str]:
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
        with urllib.request.urlopen(request, timeout=args.timeout_sec) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace").strip()
        detail = body or "no error body"
        if args.json:
            print(json.dumps({"ok": False, "error": f"HTTP {exc.code} ({detail})"}))
        else:
            print(f"Tool-call probe failed: HTTP {exc.code} ({detail})")
        return 1
    except urllib.error.URLError as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": f"URL error ({exc})"}))
        else:
            print(f"Tool-call probe failed: URL error ({exc})")
        return 1
    except TimeoutError as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": f"timeout ({exc})"}))
        else:
            print(f"Tool-call probe failed: timeout ({exc})")
        return 1
    except socket.timeout as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": f"timeout ({exc})"}))
        else:
            print(f"Tool-call probe failed: timeout ({exc})")
        return 1

    message = data.get("choices", [{}])[0].get("message", {})
    ok, reason = validate_tool_call(message, args.tool_name, args.a, args.b)
    if ok:
        if args.json:
            print(json.dumps({"ok": True}))
        else:
            print("Tool-call compliant")
        return 0
    if args.json:
        print(json.dumps({"ok": False, "error": reason}))
    else:
        print(f"Tool-call invalid: {reason}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
