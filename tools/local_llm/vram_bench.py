#!/usr/bin/env python3
"""Run probes while sampling VRAM before/after each model.

Goal: make VRAM pressure observable and comparable across models and runs.
This is a simple orchestrator around existing probes:
- vram_probe.py (NVIDIA via nvidia-smi)
- tool_call_probe.py (strict tool_calls conformance)
- latency_probe.py
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="OpenAI-compatible /v1/chat/completions endpoint")
    parser.add_argument("--config", required=True, help="JSON file with {\"models\": [..]}")
    parser.add_argument("--output", help="Write JSON output to this path")
    parser.add_argument("--timeout-sec", type=int, default=60, help="Per-request timeout")
    parser.add_argument("--iterations", type=int, default=3, help="Latency iterations per model")
    parser.add_argument("--allow-missing-vram", action="store_true", help="Do not fail if vram_probe fails")
    return parser.parse_args()


def run_json(cmd: List[str]) -> Dict[str, Any]:
    completed = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout = completed.stdout.strip()
    if completed.returncode != 0 and not stdout:
        return {"ok": False, "error": completed.stderr.strip() or "command failed"}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        return {"ok": False, "error": f"non-json output ({exc})", "raw": stdout[:1000]}


def sample_vram() -> Dict[str, Any]:
    return run_json(["python3", "tools/local_llm/vram_probe.py"])


def probe_tool(url: str, model: str, timeout_sec: int) -> Dict[str, Any]:
    return run_json(
        [
            "python3",
            "tools/local_llm/tool_call_probe.py",
            "--url",
            url,
            "--model",
            model,
            "--json",
            "--timeout-sec",
            str(timeout_sec),
        ]
    )


def probe_latency(url: str, model: str, timeout_sec: int, iterations: int) -> Dict[str, Any]:
    return run_json(
        [
            "python3",
            "tools/local_llm/latency_probe.py",
            "--url",
            url,
            "--model",
            model,
            "--timeout-sec",
            str(timeout_sec),
            "--iterations",
            str(iterations),
        ]
    )


def main() -> int:
    args = parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    models = config.get("models", [])
    if not isinstance(models, list) or not models or not all(isinstance(m, str) and m.strip() for m in models):
        print(json.dumps({"ok": False, "error": "config must contain non-empty models[]"}, indent=2))
        return 1

    started = time.time()
    results: List[Dict[str, Any]] = []
    failures: List[Dict[str, str]] = []

    for model in models:
        before = sample_vram()
        if not before.get("ok") and not args.allow_missing_vram:
            failures.append({"model": model, "error": f"vram_probe failed: {before.get('error')}"})
            continue

        tool = probe_tool(args.url, model, args.timeout_sec)
        latency = probe_latency(args.url, model, args.timeout_sec, args.iterations)

        time.sleep(0.25)
        after = sample_vram()
        if not after.get("ok") and not args.allow_missing_vram:
            failures.append({"model": model, "error": f"vram_probe failed: {after.get('error')}"})
            continue

        before_free = before.get("min_free_mib") if before.get("ok") else None
        after_free = after.get("min_free_mib") if after.get("ok") else None
        free_drop_mib: Optional[int] = None
        if isinstance(before_free, (int, float)) and isinstance(after_free, (int, float)):
            free_drop_mib = int(before_free - after_free)

        entry = {
            "model": model,
            "tool": tool,
            "latency": latency,
            "vram_before": before,
            "vram_after": after,
            "min_free_drop_mib": free_drop_mib,
        }
        results.append(entry)

        if not tool.get("ok") or not latency.get("ok"):
            failures.append({"model": model, "error": tool.get("error") or latency.get("error") or "probe failed"})

    payload = {
        "schema_version": "vram-bench-v1",
        "ok": not failures,
        "timestamp": time.time(),
        "duration_sec": round(time.time() - started, 3),
        "url": args.url,
        "config": args.config,
        "results": results,
        "failures": failures,
    }
    output = json.dumps(payload, indent=2)
    print(output)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
