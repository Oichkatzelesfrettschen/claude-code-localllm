#!/usr/bin/env python3
"""Guardrail against running multiple GPU runtimes simultaneously.

Rationale: vLLM + GPU-accelerated Ollama can exhaust VRAM and crash the Ollama
runner (cudaMalloc OOM). Treat this as a blocking condition unless explicitly
overridden.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from typing import List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow",
        action="store_true",
        help="Allow concurrent GPU runtimes (also allowed if ALLOW_CONCURRENT_GPU=1).",
    )
    return parser.parse_args()


def docker_running_vllm() -> bool:
    exe = shutil.which("docker")
    if not exe:
        return False
    completed = subprocess.run(
        [exe, "ps", "--format", "{{.Image}} {{.Names}}"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if completed.returncode != 0:
        return False
    for line in completed.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if "vllm/vllm-openai" in line or line.endswith(" vllm-openai") or line.endswith(" vllm"):
            return True
    return False


def main() -> int:
    args = parse_args()
    allow = args.allow or os.environ.get("ALLOW_CONCURRENT_GPU") == "1"

    vllm_running = docker_running_vllm()
    if vllm_running and not allow:
        print(
            "ERROR: vLLM container appears to be running; stop it before running GPU-accelerated Ollama probes "
            "(or set ALLOW_CONCURRENT_GPU=1)."
        )
        return 1

    if vllm_running and allow:
        print("WARN: concurrent GPU runtimes allowed (ALLOW_CONCURRENT_GPU=1); expect VRAM contention.")
    else:
        print("OK: no conflicting vLLM container detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

