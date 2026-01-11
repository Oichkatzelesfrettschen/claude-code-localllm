#!/usr/bin/env python3
"""Lint JSON files used by local-LLM tooling and docs examples.

This is a lightweight guardrail intended for CI and local verification.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path
from typing import Iterable, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pattern",
        action="append",
        default=[],
        help="Glob pattern(s) to lint (relative to repo root). May be repeated.",
    )
    return parser.parse_args()


def default_patterns() -> List[str]:
    return [
        "tools/local_llm/*.json",
        "docs/examples/*.json",
        "docs/*schema*.json",
    ]


def expand_patterns(patterns: Iterable[str], repo_root: Path) -> List[Path]:
    paths: List[Path] = []
    for pattern in patterns:
        for match in glob.glob(str(repo_root / pattern)):
            path = Path(match)
            if path.is_file():
                paths.append(path)
    return sorted(set(paths))


def lint_file(path: Path) -> str | None:
    try:
        raw = path.read_text(encoding="utf-8")
        json.loads(raw)
        return None
    except OSError as exc:
        return f"{path}: read failed ({exc})"
    except json.JSONDecodeError as exc:
        return f"{path}: invalid JSON ({exc})"


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    patterns = args.pattern or default_patterns()
    paths = expand_patterns(patterns, repo_root)
    if not paths:
        print("ERROR: no JSON files matched patterns", file=sys.stderr)
        for pattern in patterns:
            print(f"- {pattern}", file=sys.stderr)
        return 1

    errors: List[str] = []
    for path in paths:
        err = lint_file(path)
        if err:
            errors.append(err)

    if errors:
        print("ERROR: JSON lint failed", file=sys.stderr)
        for err in errors:
            print(err, file=sys.stderr)
        return 1

    print(f"OK: linted {len(paths)} JSON files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

