#!/usr/bin/env python3
"""Run tool-call probes across a list of models."""

from __future__ import annotations

import argparse
import json
import socket
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List

from probe_common import create_add_tool_payload, validate_add_call


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Chat completions URL")
    parser.add_argument("--config", required=True, help="Path to models JSON")
    parser.add_argument("--timeout-sec", type=int, default=60, help="Request timeout")
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop after the first failure (default: continue and report all failures)",
    )
    return parser.parse_args()


def load_models(path: Path) -> List[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("models", []))


def probe_model(url: str, model: str, timeout_sec: int) -> tuple[bool, str]:
    payload = create_add_tool_payload(model)

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_sec) as response:
            raw = response.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            return False, f"non-JSON response ({exc})"
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace").strip()
        detail = body or "no error body"
        return False, f"HTTP {exc.code} ({detail})"
    except urllib.error.URLError as exc:
        return False, f"URL error ({exc})"
    except TimeoutError as exc:
        return False, f"timeout ({exc})"
    except socket.timeout as exc:
        return False, f"timeout ({exc})"

    message = data.get("choices", [{}])[0].get("message", {})
    return validate_add_call(message)


def main() -> int:
    args = parse_args()
    models = load_models(Path(args.config))
    if not models:
        raise ValueError("No models specified in config")

    failures: Dict[str, str] = {}
    for model in models:
        ok, reason = probe_model(args.url, model, timeout_sec=args.timeout_sec)
        if not ok:
            failures[model] = reason
            if args.fail_fast:
                print(f"{model}: FAIL ({reason})")
                return 1

    if failures:
        for model, reason in failures.items():
            print(f"{model}: FAIL ({reason})")
        return 1

    for model in models:
        print(f"{model}: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
