#!/usr/bin/env python3
"""Run tool-call and latency probes across multiple runtimes."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to runtime config")
    parser.add_argument("--output", help="Optional JSON output path")
    return parser.parse_args()


def load_config(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("runtimes", [])
    data.setdefault("latency_prompt", "Say hello in one sentence.")
    data.setdefault("iterations", 3)
    data.setdefault("timeout_sec", 60)
    return data

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


def probe_tool_calls(url: str, model: str, timeout_sec: int) -> Dict[str, Any]:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Call tool add with a=2 and b=3."}],
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
        with urllib.request.urlopen(request, timeout=timeout_sec) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace").strip()
        detail = body or "no error body"
        return {"ok": False, "error": f"HTTP {exc.code} ({detail})"}
    except urllib.error.URLError as exc:
        return {"ok": False, "error": f"URL error ({exc})"}
    except TimeoutError as exc:
        return {"ok": False, "error": f"timeout ({exc})"}

    message = data.get("choices", [{}])[0].get("message", {})
    ok, reason = validate_add_call(message)
    if ok:
        return {"ok": True}
    return {"ok": False, "error": reason}


def probe_latency(url: str, model: str, prompt: str, iterations: int, timeout_sec: int) -> Dict[str, Any]:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 64,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    results: List[Dict[str, float]] = []
    for _ in range(iterations):
        start = time.time()
        try:
            with urllib.request.urlopen(request, timeout=timeout_sec) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace").strip()
            detail = body or "no error body"
            return {"ok": False, "error": f"HTTP {exc.code} ({detail})"}
        except urllib.error.URLError as exc:
            return {"ok": False, "error": f"URL error ({exc})"}
        except TimeoutError as exc:
            return {"ok": False, "error": f"timeout ({exc})"}
        elapsed = time.time() - start
        usage = data.get("usage", {})
        output_tokens = int(usage.get("completion_tokens", 0))
        tokens_per_sec = 0.0 if elapsed == 0 else output_tokens / elapsed
        results.append(
            {
                "elapsed_sec": elapsed,
                "output_tokens": output_tokens,
                "tokens_per_sec": tokens_per_sec,
            }
        )

    avg_latency = sum(r["elapsed_sec"] for r in results) / len(results)
    avg_tps = sum(r["tokens_per_sec"] for r in results) / len(results)
    return {
        "ok": True,
        "avg_latency_sec": avg_latency,
        "avg_tokens_per_sec": avg_tps,
        "iterations": iterations,
    }


def main() -> int:
    args = parse_args()
    config = load_config(Path(args.config))
    results: List[Dict[str, Any]] = []
    failures: List[Dict[str, str]] = []

    for runtime in config["runtimes"]:
        if runtime.get("enabled") is False:
            continue
        name = runtime.get("name", "unknown")
        url = runtime.get("url")
        models = runtime.get("models", [])
        if not url or not models:
            failures.append({"runtime": name, "error": "missing url or models"})
            continue

        for model in models:
            tool_result = probe_tool_calls(url, model, config["timeout_sec"])
            latency_result = probe_latency(
                url, model, config["latency_prompt"], config["iterations"], config["timeout_sec"]
            )
            entry = {
                "runtime": name,
                "url": url,
                "model": model,
                "tool_calls": tool_result,
                "latency": latency_result,
            }
            results.append(entry)
            if not tool_result.get("ok") or not latency_result.get("ok"):
                failures.append(
                    {
                        "runtime": name,
                        "model": model,
                        "error": tool_result.get("error") or latency_result.get("error") or "unknown error",
                    }
                )

    summary = {"results": results, "failures": failures}
    output = json.dumps(summary, indent=2)
    print(output)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
