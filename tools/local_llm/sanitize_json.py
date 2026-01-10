#!/usr/bin/env python3
"""Redact likely-secret fields from JSON.

Use this to safely share probe outputs/logs without leaking tokens or keys.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any


SENSITIVE_KEY_RE = re.compile(r"(api[_-]?key|token|secret|password|passwd|credential|private[_-]?key)", re.I)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--redaction", default="***REDACTED***", help="Replacement string")
    return parser.parse_args()


def sanitize(value: Any, redaction: str) -> Any:
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if isinstance(k, str) and SENSITIVE_KEY_RE.search(k):
                out[k] = redaction
            else:
                out[k] = sanitize(v, redaction)
        return out
    if isinstance(value, list):
        return [sanitize(v, redaction) for v in value]
    return value


def main() -> int:
    args = parse_args()
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: input is not valid JSON ({exc})", file=sys.stderr)
        return 1

    print(json.dumps(sanitize(data, args.redaction), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

