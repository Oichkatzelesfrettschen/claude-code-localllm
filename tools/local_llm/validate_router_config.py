#!/usr/bin/env python3
"""Validate a claude-code-router config.json for internal consistency.

This validator is intentionally dependency-free (no jsonschema). It enforces:
- Required sections exist (`Providers`, `Router`)
- Provider names are unique and models are declared
- Router slots reference `provider,model` pairs that exist in Providers
- Basic safety: if HOST is public, APIKEY must be set
- Optional: require referenced env vars to be present
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ENV_REF_RE = re.compile(r"^\$(\w+)$|^\$\{(\w+)\}$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        default=str(Path.home() / ".claude-code-router" / "config.json"),
        help="Path to config.json (default: ~/.claude-code-router/config.json)",
    )
    parser.add_argument(
        "--require-env",
        action="store_true",
        help="Fail if any $VARS referenced by api_key are missing from the environment",
    )
    parser.add_argument(
        "--allow-public-host-without-apikey",
        action="store_true",
        help="Allow HOST=0.0.0.0 (or non-localhost) without APIKEY (not recommended)",
    )
    return parser.parse_args()


def die(errors: List[str]) -> int:
    for error in errors:
        print(f"ERROR: {error}")
    return 1


def load_json(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("config root must be a JSON object")
    return data


def require_type(errors: List[str], key: str, value: Any, expected_type: type) -> None:
    if not isinstance(value, expected_type):
        errors.append(f"{key} must be {expected_type.__name__}")


def env_refs(value: str) -> Optional[str]:
    match = ENV_REF_RE.match(value.strip())
    if not match:
        return None
    return match.group(1) or match.group(2)


def is_public_host(host: str) -> bool:
    host = host.strip().lower()
    if host in {"127.0.0.1", "localhost"}:
        return False
    if host.startswith("127."):
        return False
    return True


def validate_provider(provider: Any, idx: int, errors: List[str]) -> Optional[Dict[str, Any]]:
    if not isinstance(provider, dict):
        errors.append(f"Providers[{idx}] must be an object")
        return None
    name = provider.get("name")
    api_base_url = provider.get("api_base_url")
    api_key = provider.get("api_key")
    models = provider.get("models")
    if not isinstance(name, str) or not name.strip():
        errors.append(f"Providers[{idx}].name must be a non-empty string")
    if not isinstance(api_base_url, str) or not api_base_url.strip():
        errors.append(f"Providers[{idx}].api_base_url must be a non-empty string")
    if not isinstance(api_key, str) or not api_key.strip():
        errors.append(f"Providers[{idx}].api_key must be a non-empty string")
    if not isinstance(models, list) or not models or not all(isinstance(m, str) and m.strip() for m in models):
        errors.append(f"Providers[{idx}].models must be a non-empty string array")
    return provider


def iter_router_slots(router: Dict[str, Any]) -> Iterable[Tuple[str, str]]:
    for slot, value in router.items():
        if slot == "longContextThreshold":
            continue
        if isinstance(value, str):
            yield slot, value


def parse_route(value: str) -> Optional[Tuple[str, str]]:
    if "," not in value:
        return None
    provider, model = value.split(",", 1)
    provider = provider.strip()
    model = model.strip()
    if not provider or not model:
        return None
    return provider, model


def main() -> int:
    args = parse_args()
    config_path = Path(args.path).expanduser()
    errors: List[str] = []

    if not config_path.exists():
        return die([f"config not found: {config_path}"])

    try:
        config = load_json(config_path)
    except Exception as exc:  # noqa: BLE001
        return die([f"failed to parse JSON ({config_path}): {exc}"])

    providers = config.get("Providers")
    router = config.get("Router")
    if providers is None:
        errors.append("missing required key: Providers")
    if router is None:
        errors.append("missing required key: Router")

    if errors:
        return die(errors)

    if not isinstance(providers, list) or not providers:
        errors.append("Providers must be a non-empty array")
        return die(errors)
    if not isinstance(router, dict) or not router:
        errors.append("Router must be a non-empty object")
        return die(errors)

    parsed_providers: List[Dict[str, Any]] = []
    for idx, provider in enumerate(providers):
        parsed = validate_provider(provider, idx, errors)
        if parsed is not None:
            parsed_providers.append(parsed)

    if errors:
        return die(errors)

    by_name: Dict[str, Dict[str, Any]] = {}
    for provider in parsed_providers:
        name = str(provider["name"]).strip()
        if name in by_name:
            errors.append(f"duplicate provider name: {name}")
            continue
        by_name[name] = provider

    # Basic safety: do not allow binding publicly without an API key.
    host = config.get("HOST")
    apikey = config.get("APIKEY")
    if isinstance(host, str) and host.strip() and is_public_host(host):
        if not isinstance(apikey, str) or not apikey.strip():
            if not args.allow_public_host_without_apikey:
                errors.append("HOST is public but APIKEY is missing; refuse unsafe config")

    # Validate router slot references.
    for slot, value in iter_router_slots(router):
        parsed = parse_route(value)
        if not parsed:
            errors.append(f"Router.{slot} must be \"provider,model\" (got {value!r})")
            continue
        provider_name, model = parsed
        provider = by_name.get(provider_name)
        if provider is None:
            errors.append(f"Router.{slot} references unknown provider: {provider_name}")
            continue
        models = provider.get("models", [])
        if isinstance(models, list) and model not in models:
            errors.append(f"Router.{slot} references model not in Providers[{provider_name}].models: {model}")

    # Validate env var references (common: api_key values are "$VAR").
    if args.require_env:
        for provider in parsed_providers:
            api_key = str(provider.get("api_key", "")).strip()
            ref = env_refs(api_key)
            if ref and not os.environ.get(ref):
                errors.append(f"Providers[{provider.get('name')}].api_key references missing env var: {ref}")

    if errors:
        return die(errors)

    print("OK: router config validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

