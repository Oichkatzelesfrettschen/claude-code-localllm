#!/usr/bin/env python3
"""Measure latency and tokens/sec for a local model endpoint."""

from __future__ import annotations

import argparse
import json
import time
import urllib.request


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Chat completions URL")
    parser.add_argument("--model", required=True, help="Model name")
    parser.add_argument("--prompt", default="Say hello in one sentence.", help="Prompt")
    parser.add_argument("--iterations", type=int, default=3, help="Iterations")
    return parser.parse_args()


def run_once(url: str, model: str, prompt: str) -> dict:
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
    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read().decode("utf-8"))
    elapsed = time.time() - start
    usage = data.get("usage", {})
    output_tokens = int(usage.get("completion_tokens", 0))
    tokens_per_sec = 0.0 if elapsed == 0 else output_tokens / elapsed
    return {
        "elapsed_sec": elapsed,
        "output_tokens": output_tokens,
        "tokens_per_sec": tokens_per_sec,
    }


def main() -> int:
    args = parse_args()
    results = [run_once(args.url, args.model, args.prompt) for _ in range(args.iterations)]
    avg_latency = sum(r["elapsed_sec"] for r in results) / len(results)
    avg_tps = sum(r["tokens_per_sec"] for r in results) / len(results)
    print(
        json.dumps(
            {
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
