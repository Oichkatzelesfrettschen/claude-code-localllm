#!/usr/bin/env python3
"""Run failure-injection checks against the local probe scripts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import List, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18080)
    return parser.parse_args()


def run(cmd: List[str], expect_ok: bool) -> Tuple[bool, str]:
    completed = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = completed.stdout
    if "Traceback (most recent call last)" in out:
        return False, f"unexpected traceback in output for: {' '.join(cmd)}"
    ok = completed.returncode == 0
    if ok != expect_ok:
        return False, f"unexpected exit ({completed.returncode}) for: {' '.join(cmd)}\n{out}"
    return True, out.strip()


def wait_ready(url: str, timeout_sec: float = 10.0) -> bool:
    start = time.time()
    while time.time() - start < timeout_sec:
        try:
            subprocess.run(["curl", "-fsS", url], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            time.sleep(0.2)
    return False


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    base = f"http://{args.host}:{args.port}"
    url = f"{base}/v1/chat/completions"

    server = subprocess.Popen(
        [
            sys.executable,
            str(repo_root / "tools/local_llm/mock_openai_server.py"),
            "--host",
            args.host,
            "--port",
            str(args.port),
        ],
        cwd=str(repo_root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        if not wait_ready(f"{base}/v1/models"):
            print("ERROR: mock server did not start", file=sys.stderr)
            return 1

        checks: List[Tuple[List[str], bool]] = [
            # tool_call_probe graceful failures
            (
                [sys.executable, "tools/local_llm/tool_call_probe.py", "--url", url, "--model", "missing_tool_calls"],
                False,
            ),
            (
                [sys.executable, "tools/local_llm/tool_call_probe.py", "--url", url, "--model", "invalid_arguments_json"],
                False,
            ),
            ([sys.executable, "tools/local_llm/tool_call_probe.py", "--url", url, "--model", "http_500"], False),
            (
                [
                    sys.executable,
                    "tools/local_llm/tool_call_probe.py",
                    "--url",
                    url,
                    "--model",
                    "timeout",
                    "--timeout-sec",
                    "1",
                ],
                False,
            ),
            # success path
            ([sys.executable, "tools/local_llm/tool_call_probe.py", "--url", url, "--model", "ok"], True),
        ]

        for cmd, expect_ok in checks:
            ok, msg = run(cmd, expect_ok=expect_ok)
            if not ok:
                print(f"ERROR: {msg}", file=sys.stderr)
                return 1

        # probe_suite should report failures without traceback
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "models.json"
            cfg.write_text(json.dumps({"models": ["ok", "missing_tool_calls"]}), encoding="utf-8")
            ok, msg = run(
                [sys.executable, "tools/local_llm/probe_suite.py", "--url", url, "--config", str(cfg), "--timeout-sec", "2"],
                expect_ok=False,
            )
            if not ok:
                print(f"ERROR: {msg}", file=sys.stderr)
                return 1

        print("OK: failure injection checks passed")
        return 0
    finally:
        server.terminate()
        try:
            server.wait(timeout=2)
        except subprocess.TimeoutExpired:
            server.kill()


if __name__ == "__main__":
    raise SystemExit(main())
