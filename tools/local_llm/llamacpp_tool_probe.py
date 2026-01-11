#!/usr/bin/env python3
"""Probe llama.cpp OpenAI server without hardcoding the model ID.

llama-server typically advertises a single model in GET /v1/models. This helper
uses that model id and then invokes the standard tool-call probe.
"""

from __future__ import annotations

import argparse
import json
import runpy
import sys
import urllib.error
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


def fetch_first_model_id(url: str, timeout_sec: float) -> Optional[str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout_sec) as response:
            raw = response.read()
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        print(f"ERROR: failed to fetch models from {url}: {exc}", file=sys.stderr)
        return None
    except Exception as exc:
        print(f"ERROR: unexpected error fetching models from {url}: {exc}", file=sys.stderr)
        return None

    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid JSON from models endpoint {url}: {exc}", file=sys.stderr)
        return None
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
    model_id = fetch_first_model_id(models_url, timeout_sec=float(args.timeout_sec))
    if not model_id:
        print(f"ERROR: no model id found at {models_url}", file=sys.stderr)
        return 1

    repo_root = Path(__file__).resolve().parents[2]
    probe = repo_root / "tools/local_llm/tool_call_probe.py"
    argv = [
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

    prior_argv = sys.argv
    try:
        sys.argv = argv
        runpy.run_path(str(probe), run_name="__main__")
        return 0
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        if isinstance(code, int):
            return code
        return 1
    finally:
        sys.argv = prior_argv


if __name__ == "__main__":
    raise SystemExit(main())
