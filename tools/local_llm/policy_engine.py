#!/usr/bin/env python3
"""Evaluate routing policy based on task metadata."""

from __future__ import annotations

import argparse
import fnmatch
import json
from pathlib import Path
from typing import List, Dict, Any


def load_rules(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def match_any(path: str, patterns: List[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def evaluate(
    paths: List[str],
    token_count: int,
    rules: Dict[str, Any],
) -> Dict[str, str]:
    denylist = rules.get("denylist_paths", [])
    sensitive = rules.get("sensitive_paths", [])
    threshold = int(rules.get("long_context_threshold_tokens", 0))

    for path in paths:
        if match_any(path, denylist):
            return {"route": "claude_only", "reason": "denylist_path"}

    for path in paths:
        if match_any(path, sensitive):
            return {"route": "claude_first", "reason": "sensitive_path"}

    if threshold and token_count > threshold:
        return {"route": "claude_first", "reason": "long_context"}

    return {"route": "local", "reason": "default_safe"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", required=True, help="Path to policy rules JSON")
    parser.add_argument("--paths", nargs="+", required=True, help="File paths")
    parser.add_argument("--tokens", type=int, default=0, help="Total tokens")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rules = load_rules(Path(args.rules))
    decision = evaluate(args.paths, args.tokens, rules)
    print(json.dumps(decision))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
