#!/usr/bin/env python3
"""Run tool-call probes across a list of models."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Chat completions URL")
    parser.add_argument("--config", required=True, help="Path to models JSON")
    return parser.parse_args()


def load_models(path: Path) -> List[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("models", []))

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


def validate_add_call(message: Dict[str, Any]) -> Tuple[bool, str]:
    tool_calls = message.get("tool_calls")
    if not tool_calls:
        content = message.get("content", "")
        return False, f"missing tool_calls (content={content})"
    if not isinstance(tool_calls, list) or not tool_calls:
        return False, "tool_calls is not a non-empty list"
    first = tool_calls[0]
    if not isinstance(first, dict):
        return False, "tool_calls[0] is not an object"
    function = first.get("function")
    if not isinstance(function, dict):
        return False, "tool_calls[0].function missing or invalid"
    if function.get("name") != "add":
        return False, f"unexpected function name ({function.get('name')})"
    args, err = parse_arguments(function.get("arguments"))
    if err:
        return False, err
    if args.get("a") != 2 or args.get("b") != 3:
        return False, f"unexpected arguments (a={args.get('a')}, b={args.get('b')})"
    return True, "ok"


def probe_model(url: str, model: str) -> Tuple[bool, str]:
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Call tool add with a=2 and b=3."}
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "add",
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
        url,
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
        return False, f"HTTP {exc.code} ({detail})"

    message = data.get("choices", [{}])[0].get("message", {})
    return validate_add_call(message)


def main() -> int:
    args = parse_args()
    models = load_models(Path(args.config))
    if not models:
        raise ValueError("No models specified in config")

    failures: Dict[str, str] = {}
    for model in models:
        ok, reason = probe_model(args.url, model)
        if not ok:
            failures[model] = reason

    if failures:
        for model, reason in failures.items():
            print(f"{model}: FAIL ({reason})")
        return 1

    for model in models:
        print(f"{model}: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
