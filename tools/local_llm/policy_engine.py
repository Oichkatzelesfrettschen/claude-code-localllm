#!/usr/bin/env python3
"""Evaluate routing policy based on task metadata."""

from __future__ import annotations

import argparse
import fnmatch
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


def load_rules(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    normalized = normalized.replace("//", "/")
    return normalized


def match_any(path: str, patterns: List[str]) -> bool:
    normalized = normalize_path(path)
    return any(fnmatch.fnmatch(normalized, normalize_path(pattern)) for pattern in patterns)


def evaluate(
    paths: List[str],
    token_count: int,
    rules: Dict[str, Any],
    vram_free_mib: Optional[int] = None,
    vram_free_ratio: Optional[float] = None,
) -> Dict[str, str]:
    denylist = rules.get("denylist_paths", [])
    sensitive = rules.get("sensitive_paths", [])
    threshold = int(rules.get("long_context_threshold_tokens", 0))
    min_free_mib = int(rules.get("min_free_vram_mib", 0) or 0)
    min_free_ratio = float(rules.get("min_free_vram_ratio", 0) or 0)

    for path in paths:
        if match_any(path, denylist):
            return {"route": "claude_only", "reason": "denylist_path"}

    for path in paths:
        if match_any(path, sensitive):
            return {"route": "claude_first", "reason": "sensitive_path"}

    if threshold and token_count > threshold:
        return {"route": "claude_first", "reason": "long_context"}

    if (min_free_mib or min_free_ratio) and (vram_free_mib is None and vram_free_ratio is None):
        return {"route": "claude_first", "reason": "missing_vram_signal"}

    if min_free_mib and vram_free_mib is not None and vram_free_mib < min_free_mib:
        return {"route": "claude_first", "reason": "low_vram"}

    if min_free_ratio and vram_free_ratio is not None and vram_free_ratio < min_free_ratio:
        return {"route": "claude_first", "reason": "low_vram"}

    return {"route": "local", "reason": "default_safe"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", required=True, help="Path to policy rules JSON")
    parser.add_argument("--paths", nargs="+", required=True, help="File paths")
    parser.add_argument("--tokens", type=int, default=0, help="Total tokens")
    parser.add_argument("--vram-sample", help="Optional JSON file from tools/local_llm/vram_probe.py")
    parser.add_argument("--vram-free-mib", type=int, help="Override: free VRAM (MiB)")
    parser.add_argument("--vram-free-ratio", type=float, help="Override: free VRAM ratio (0-1)")
    return parser.parse_args()


def load_vram_signal(path: Path) -> Tuple[Optional[int], Optional[float]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    free_mib = data.get("min_free_mib")
    free_ratio = data.get("min_free_ratio")
    free_mib_int = int(free_mib) if isinstance(free_mib, (int, float)) else None
    free_ratio_float = float(free_ratio) if isinstance(free_ratio, (int, float)) else None
    return free_mib_int, free_ratio_float


def main() -> int:
    args = parse_args()
    rules = load_rules(Path(args.rules))
    vram_free_mib = args.vram_free_mib
    vram_free_ratio = args.vram_free_ratio
    if args.vram_sample:
        sample_free_mib, sample_free_ratio = load_vram_signal(Path(args.vram_sample))
        if vram_free_mib is None:
            vram_free_mib = sample_free_mib
        if vram_free_ratio is None:
            vram_free_ratio = sample_free_ratio

    decision = evaluate(
        args.paths,
        args.tokens,
        rules,
        vram_free_mib=vram_free_mib,
        vram_free_ratio=vram_free_ratio,
    )
    print(json.dumps(decision))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
