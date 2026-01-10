#!/usr/bin/env python3
"""Run tool-call probes across a list of models."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

from probe_common import create_add_tool_payload, validate_add_call


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Chat completions URL")
    parser.add_argument("--config", required=True, help="Path to models JSON")
    return parser.parse_args()


def load_models(path: Path) -> List[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("models", []))


def probe_model(url: str, model: str) -> tuple[bool, str]:
    payload = create_add_tool_payload(model)

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
