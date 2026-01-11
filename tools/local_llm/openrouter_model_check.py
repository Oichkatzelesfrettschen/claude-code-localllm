#!/usr/bin/env python3
"""Validate OpenRouter model IDs referenced by a claude-code-router config.

This prevents stale example configs by checking configured model IDs against
OpenRouter's public models catalog.
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="docs/examples/router-config-openrouter.json",
        help="Path to a claude-code-router config.json to validate.",
    )
    parser.add_argument(
        "--catalog-url",
        default="https://openrouter.ai/api/v1/models",
        help="OpenRouter models catalog URL.",
    )
    parser.add_argument(
        "--provider-name",
        default="openrouter",
        help="Provider name in config whose model IDs should be validated.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("config JSON is not an object")
    return data


def fetch_model_ids(url: str) -> Set[str]:
    with urllib.request.urlopen(url, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    data = payload.get("data", [])
    if not isinstance(data, list):
        raise ValueError("catalog JSON 'data' is not a list")
    ids: Set[str] = set()
    for item in data:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            ids.add(item["id"])
    return ids


def extract_provider_models(config: Dict[str, Any], provider_name: str) -> Tuple[List[str], str | None]:
    providers = config.get("Providers", [])
    if not isinstance(providers, list):
        return [], "config Providers is not a list"
    for provider in providers:
        if not isinstance(provider, dict):
            continue
        if provider.get("name") != provider_name:
            continue
        models = provider.get("models", [])
        if not isinstance(models, list) or not all(isinstance(m, str) for m in models):
            return [], f"provider '{provider_name}' models is not a string list"
        return list(models), None
    return [], f"provider '{provider_name}' not found"


def summarize_missing(missing: Iterable[str]) -> str:
    items = list(missing)
    if not items:
        return ""
    bullets = "\n".join(f"- {m}" for m in items)
    return f"Missing model IDs:\n{bullets}"


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    config = load_json(config_path)

    models, err = extract_provider_models(config, args.provider_name)
    if err:
        print(f"ERROR: {err}")
        return 1
    if not models:
        print(f"ERROR: provider '{args.provider_name}' has no models configured")
        return 1

    catalog_ids = fetch_model_ids(args.catalog_url)
    missing = sorted({m for m in models if m not in catalog_ids})
    if missing:
        print(f"ERROR: {config_path} contains stale OpenRouter model IDs")
        print(summarize_missing(missing))
        print(f"Catalog: {args.catalog_url}")
        return 1

    print(f"OK: {len(models)} OpenRouter model IDs validated against catalog")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

