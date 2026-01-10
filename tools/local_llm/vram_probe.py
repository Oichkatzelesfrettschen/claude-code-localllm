#!/usr/bin/env python3
"""Probe GPU VRAM pressure (NVIDIA via nvidia-smi).

This tool is intentionally dependency-free (stdlib only) and is designed to be
used as an input into routing/policy decisions.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass(frozen=True)
class GpuSample:
    index: int
    name: str
    total_mib: int
    used_mib: int
    free_mib: int
    utilization_gpu_pct: Optional[int]
    temperature_c: Optional[int]
    pstate: Optional[str]


def parse_int(value: str) -> Optional[int]:
    value = value.strip()
    if not value or value.lower() in {"n/a", "na"}:
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def parse_csv_line(line: str) -> List[str]:
    return [part.strip() for part in line.split(",")]


def sample_nvidia(timeout_sec: int) -> List[GpuSample]:
    exe = shutil.which("nvidia-smi")
    if not exe:
        raise RuntimeError("nvidia-smi not found in PATH")

    query = [
        "index",
        "name",
        "memory.total",
        "memory.used",
        "memory.free",
        "utilization.gpu",
        "temperature.gpu",
        "pstate",
    ]
    cmd = [
        exe,
        f"--query-gpu={','.join(query)}",
        "--format=csv,noheader,nounits",
    ]
    completed = subprocess.run(
        cmd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout_sec,
    )
    samples: List[GpuSample] = []
    for raw_line in completed.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = parse_csv_line(line)
        if len(parts) != len(query):
            raise RuntimeError(f"unexpected nvidia-smi output: {raw_line}")
        samples.append(
            GpuSample(
                index=int(parts[0]),
                name=parts[1],
                total_mib=int(float(parts[2])),
                used_mib=int(float(parts[3])),
                free_mib=int(float(parts[4])),
                utilization_gpu_pct=parse_int(parts[5]),
                temperature_c=parse_int(parts[6]),
                pstate=parts[7] or None,
            )
        )
    return samples


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-sec", type=int, default=2, help="nvidia-smi timeout")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = time.time()
    try:
        gpus = sample_nvidia(timeout_sec=args.timeout_sec)
    except Exception as exc:  # noqa: BLE001 - CLI tool: report error as JSON
        payload = {"ok": False, "error": str(exc), "timestamp": time.time()}
        print(json.dumps(payload, indent=2))
        return 1

    if not gpus:
        payload = {"ok": False, "error": "no GPUs detected", "timestamp": time.time()}
        print(json.dumps(payload, indent=2))
        return 1

    min_free_mib = min(g.free_mib for g in gpus)
    min_free_ratio = min(g.free_mib / g.total_mib for g in gpus if g.total_mib)
    payload = {
        "ok": True,
        "timestamp": time.time(),
        "duration_ms": int((time.time() - started) * 1000),
        "gpus": [asdict(g) for g in gpus],
        "min_free_mib": min_free_mib,
        "min_free_ratio": round(min_free_ratio, 4),
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

