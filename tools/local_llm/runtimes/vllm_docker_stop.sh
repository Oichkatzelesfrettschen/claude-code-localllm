#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="${CONTAINER_NAME:-vllm-openai}"
docker rm -f "${CONTAINER_NAME}"

