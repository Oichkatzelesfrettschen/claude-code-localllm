#!/usr/bin/env python3
"""Verify an npm tarball integrity hash against the registry metadata.

Usage:
  python tools/supply_chain/verify_npm_integrity.py \
    --package @devcontainers/cli \
    --version 0.80.3 \
    --tarball /path/to/cli-0.80.3.tgz
"""

import argparse
import base64
import hashlib
import json
import sys
import urllib.request


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True, help="npm package name")
    parser.add_argument("--version", required=True, help="npm package version")
    parser.add_argument("--tarball", required=True, help="path to tarball")
    parser.add_argument(
        "--registry",
        default="https://registry.npmjs.org",
        help="npm registry base URL",
    )
    return parser.parse_args()


def fetch_integrity(registry: str, package: str, version: str) -> str:
    url = f"{registry.rstrip('/')}/{package}"
    with urllib.request.urlopen(url) as response:
        payload = json.loads(response.read().decode("utf-8"))
    dist = payload.get("versions", {}).get(version, {}).get("dist", {})
    integrity = dist.get("integrity")
    if not integrity:
        raise ValueError(f"No dist.integrity for {package}@{version}")
    return integrity


def compute_integrity(tarball_path: str) -> str:
    hasher = hashlib.sha512()
    with open(tarball_path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    digest = base64.b64encode(hasher.digest()).decode("utf-8")
    return f"sha512-{digest}"


def main() -> int:
    args = parse_args()
    expected = fetch_integrity(args.registry, args.package, args.version)
    actual = compute_integrity(args.tarball)
    if expected != actual:
        print("Integrity mismatch", file=sys.stderr)
        print(f"expected: {expected}", file=sys.stderr)
        print(f"actual:   {actual}", file=sys.stderr)
        return 1
    print("Integrity verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
