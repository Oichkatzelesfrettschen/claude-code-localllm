#!/usr/bin/env bash
set -euo pipefail

# Start llama.cpp's OpenAI-compatible server (llama-server).
#
# Requirements:
# - llama.cpp built with `llama-server` in PATH
# - A GGUF model file on disk
#
# Usage:
#   tools/local_llm/runtimes/llamacpp_server.sh /path/to/model.gguf
#
# Environment:
#   HOST=127.0.0.1
#   PORT=8081
#   CTX=4096
#   GPU_LAYERS=0

MODEL_PATH="${1:-}"
if [[ -z "${MODEL_PATH}" ]]; then
  echo "Usage: $0 /path/to/model.gguf" >&2
  exit 1
fi

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8081}"
CTX="${CTX:-4096}"
GPU_LAYERS="${GPU_LAYERS:-0}"

LLAMA_SERVER_BIN="$(command -v llama-server || true)"
if [[ -z "${LLAMA_SERVER_BIN}" && -x "/opt/llama-cpp/bin/llama-server" ]]; then
  LLAMA_SERVER_BIN="/opt/llama-cpp/bin/llama-server"
fi
if [[ -z "${LLAMA_SERVER_BIN}" ]]; then
  echo "ERROR: llama-server not found in PATH." >&2
  echo "Hint (Arch/chaotic-aur): export PATH=/opt/llama-cpp/bin:\\$PATH" >&2
  exit 1
fi

exec "${LLAMA_SERVER_BIN}" \
  --host "${HOST}" \
  --port "${PORT}" \
  --model "${MODEL_PATH}" \
  --ctx-size "${CTX}" \
  --n-gpu-layers "${GPU_LAYERS}" \
  --chat-template chatml \
  --metrics
