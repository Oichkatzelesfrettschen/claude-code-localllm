#!/usr/bin/env bash
set -euo pipefail

# Run vLLM's OpenAI-compatible server in Docker.
# Default model is small to reduce download + VRAM footprint.
#
# Requirements:
# - docker (or podman with docker-compat)
# - NVIDIA Container Toolkit for --gpus all
#
# Usage:
#   tools/local_llm/runtimes/vllm_docker.sh [MODEL_ID]
#
# Environment:
#   PORT=8000
#   CONTAINER_NAME=vllm-openai
#   HF_CACHE_DIR=~/.cache/huggingface
#   MAX_MODEL_LEN=4096
#   GPU_MEM_UTIL=0.80
#   RM_ON_EXIT=0
#   ENABLE_AUTO_TOOL_CHOICE=1
#   TOOL_CALL_PARSER=hermes

MODEL_ID="${1:-Qwen/Qwen2.5-1.5B-Instruct}"
PORT="${PORT:-8000}"
CONTAINER_NAME="${CONTAINER_NAME:-vllm-openai}"
HF_CACHE_DIR="${HF_CACHE_DIR:-$HOME/.cache/huggingface}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-4096}"
GPU_MEM_UTIL="${GPU_MEM_UTIL:-0.80}"
RM_ON_EXIT="${RM_ON_EXIT:-0}"
ENABLE_AUTO_TOOL_CHOICE="${ENABLE_AUTO_TOOL_CHOICE:-1}"
TOOL_CALL_PARSER="${TOOL_CALL_PARSER:-hermes}"

mkdir -p "${HF_CACHE_DIR}"

docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true

rm_flag=()
if [[ "${RM_ON_EXIT}" == "1" ]]; then
  rm_flag+=(--rm)
fi

exec docker run \
  --gpus all \
  --name "${CONTAINER_NAME}" \
  "${rm_flag[@]}" \
  -p "127.0.0.1:${PORT}:8000" \
  -v "${HF_CACHE_DIR}:/root/.cache/huggingface" \
  -e HF_HOME=/root/.cache/huggingface \
  vllm/vllm-openai:latest \
  "${MODEL_ID}" \
  --served-model-name "${MODEL_ID}" \
  --host 0.0.0.0 \
  --port 8000 \
  --dtype auto \
  --max-model-len "${MAX_MODEL_LEN}" \
  --gpu-memory-utilization "${GPU_MEM_UTIL}" \
  $( [[ "${ENABLE_AUTO_TOOL_CHOICE}" == "1" ]] && printf '%s' "--enable-auto-tool-choice --tool-call-parser ${TOOL_CALL_PARSER}" )
