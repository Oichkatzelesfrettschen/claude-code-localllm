#!/usr/bin/env python3
"""Measure latency and tokens/sec for a local model endpoint."""

from __future__ import annotations

import argparse
import json
import socket
import time
import urllib.error
import urllib.request


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Chat completions URL")
    parser.add_argument("--model", required=True, help="Model name")
    parser.add_argument("--prompt", default="Say hello in one sentence.", help="Prompt")
    parser.add_argument("--iterations", type=int, default=3, help="Iterations")
    parser.add_argument("--timeout-sec", type=int, default=60, help="Request timeout")
    return parser.parse_args()


def run_once(url: str, model: str, prompt: str, timeout_sec: int) -> dict:
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
    start = time.time()
    with urllib.request.urlopen(request, timeout=timeout_sec) as response:
        data = json.loads(response.read().decode("utf-8"))
    elapsed = time.time() - start
    usage = data.get("usage", {})
    if not isinstance(usage, dict) or "completion_tokens" not in usage:
        output_tokens = None
        tokens_per_sec = None
    else:
        output_tokens = int(usage.get("completion_tokens", 0))
        tokens_per_sec = None if elapsed == 0 else output_tokens / elapsed
    return {
        "elapsed_sec": elapsed,
        "output_tokens": output_tokens,
        "tokens_per_sec": tokens_per_sec,
    }


def main() -> int:
    args = parse_args()
    try:
        results = [run_once(args.url, args.model, args.prompt, args.timeout_sec) for _ in range(args.iterations)]
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace").strip()
        detail = body or "no error body"
        print(json.dumps({"ok": False, "error": f"HTTP {exc.code} ({detail})"}))
        return 1
    except urllib.error.URLError as exc:
        print(json.dumps({"ok": False, "error": f"URL error ({exc})"}))
        return 1
    except TimeoutError as exc:
        print(json.dumps({"ok": False, "error": f"timeout ({exc})"}))
        return 1
    except socket.timeout as exc:
        print(json.dumps({"ok": False, "error": f"timeout ({exc})"}))
        return 1
    avg_latency = sum(r["elapsed_sec"] for r in results) / len(results)
    tps_values = [r["tokens_per_sec"] for r in results if isinstance(r.get("tokens_per_sec"), (int, float))]
    avg_tps = None if not tps_values else sum(tps_values) / len(tps_values)
    print(
        json.dumps(
            {
                "ok": True,
                "model": args.model,
                "iterations": args.iterations,
                "avg_latency_sec": avg_latency,
                "avg_tokens_per_sec": avg_tps,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
