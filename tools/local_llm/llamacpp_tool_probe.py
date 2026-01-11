#!/usr/bin/env python3
"""Probe llama.cpp OpenAI server without hardcoding the model ID.

llama-server typically advertises a single model in GET /v1/models. This helper
uses that model id and then invokes the standard tool-call probe.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Chat completions URL (e.g. http://127.0.0.1:8081/v1/chat/completions)")
    parser.add_argument("--timeout-sec", type=int, default=180, help="Request timeout (llama.cpp can be slow)")
    parser.add_argument("--tool-name", default="add")
    parser.add_argument("--a", type=int, default=2)
    parser.add_argument("--b", type=int, default=3)
    return parser.parse_args()


def models_url_from_chat_url(chat_url: str) -> str:
    parsed = urllib.parse.urlparse(chat_url)
    path = parsed.path
    if path.endswith("/v1/chat/completions"):
        path = path[: -len("/v1/chat/completions")] + "/v1/models"
    elif path.endswith("/chat/completions"):
        path = path[: -len("/chat/completions")] + "/models"
    else:
        # Best effort: assume /v1/models exists at the same host.
        path = "/v1/models"
    return urllib.parse.urlunparse(parsed._replace(path=path, query="", fragment=""))


def fetch_first_model_id(url: str) -> Optional[str]:
    with urllib.request.urlopen(url, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    data = payload.get("data", [])
    if not isinstance(data, list) or not data:
        return None
    first = data[0]
    if isinstance(first, dict) and isinstance(first.get("id"), str):
        return first["id"]
    return None


def main() -> int:
    args = parse_args()
    models_url = models_url_from_chat_url(args.url)
    model_id = fetch_first_model_id(models_url)
    if not model_id:
        print(f"ERROR: no model id found at {models_url}")
        return 1

    repo_root = Path(__file__).resolve().parents[2]
    probe = repo_root / "tools/local_llm/tool_call_probe.py"
    cmd = [
        sys.executable,
        str(probe),
        "--url",
        args.url,
        "--model",
        model_id,
        "--tool-name",
        args.tool_name,
        "--a",
        str(args.a),
        "--b",
        str(args.b),
        "--timeout-sec",
        str(args.timeout_sec),
    ]
    completed = subprocess.run(cmd, check=False, cwd=str(repo_root))
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())

