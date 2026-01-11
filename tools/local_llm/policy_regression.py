#!/usr/bin/env python3
"""Policy regression check against a set of fixtures.

Treat mismatches as blocking errors.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import policy_engine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fixtures",
        default="tools/local_llm/policy_fixtures.json",
        help="Path to fixture JSON",
    )
    return parser.parse_args()


def load_json(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("fixtures root must be an object")
    return data


def main() -> int:
    args = parse_args()
    fixtures_path = Path(args.fixtures)
    fixtures = load_json(fixtures_path)
    rules_path = Path(str(fixtures.get("rules", "tools/local_llm/policy_rules.json")))
    rules = policy_engine.load_rules(rules_path)

    cases = fixtures.get("cases", [])
    if not isinstance(cases, list) or not cases:
        raise ValueError("fixtures must include a non-empty cases[]")

    failures: List[str] = []
    for idx, case in enumerate(cases):
        if not isinstance(case, dict):
            failures.append(f"case[{idx}] is not an object")
            continue
        name = str(case.get("name", f"case[{idx}]"))
        paths = case.get("paths", [])
        tokens = int(case.get("tokens", 0))
        expected = case.get("expected", {})
        if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
            failures.append(f"{name}: paths must be string array")
            continue
        if not isinstance(expected, dict):
            failures.append(f"{name}: expected must be an object")
            continue

        decision = policy_engine.evaluate(paths, tokens, rules)
        if decision != expected:
            failures.append(f"{name}: expected {expected} got {decision}")

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print(f"OK: {len(cases)} policy fixtures passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
