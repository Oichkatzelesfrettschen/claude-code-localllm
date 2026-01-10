# vLLM Setup (Docker, OpenAI-compatible)

This repo supports probing vLLM via its OpenAI-compatible server.

## Why Docker
On Arch/CachyOS, a containerized vLLM avoids AUR dependency churn and keeps the
runtime reproducible.

## Prerequisites
- `docker`
- NVIDIA Container Toolkit (so `docker run --gpus all ...` works)
- Network access to pull:
  - `vllm/vllm-openai:latest`
  - Model weights from Hugging Face Hub (some models require `HF_TOKEN`)

## Start vLLM
This repo includes a helper:
- `tools/local_llm/runtimes/vllm_docker.sh`

Example (small model, tool-calls enabled):
```
tools/local_llm/runtimes/vllm_docker.sh Qwen/Qwen2.5-1.5B-Instruct
```

Wait until `curl http://127.0.0.1:8000/v1/models` succeeds.

## Tool calling (important)
vLLM requires tool-choice support to be enabled at server start:
- `--enable-auto-tool-choice`
- `--tool-call-parser ...`

The helper enables this by default with `TOOL_CALL_PARSER=hermes` (override via
env if needed).

## Probing vLLM
Single-model tool-call probe:
```
python3 tools/local_llm/tool_call_probe.py \
  --url http://127.0.0.1:8000/v1/chat/completions \
  --model Qwen/Qwen2.5-1.5B-Instruct
```

Runtime probe (vLLM only):
```
jq '{latency_prompt:.latency_prompt,iterations:.iterations,timeout_sec:.timeout_sec,runtimes:(.runtimes|map(select(.name=="vllm")|.enabled=true|.models=["Qwen/Qwen2.5-1.5B-Instruct"]))}' \
  tools/local_llm/runtime_matrix.json > /tmp/runtime_matrix_vllm_only.json
python3 tools/local_llm/runtime_probe.py --config /tmp/runtime_matrix_vllm_only.json
```

## VRAM contention warning
If Ollama is using GPU acceleration, running vLLM simultaneously can cause
`cudaMalloc failed: out of memory` errors in Ollama. Treat this as a blocking
operational constraint: run one GPU runtime at a time unless you explicitly
budget VRAM for both.

## Stop vLLM
```
tools/local_llm/runtimes/vllm_docker_stop.sh
```

