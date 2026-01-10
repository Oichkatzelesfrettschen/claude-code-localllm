# vLLM Setup (Docker, OpenAI-compatible)

This repo supports probing vLLM via its OpenAI-compatible server.

## Why Docker
On Arch/CachyOS, a containerized vLLM avoids AUR dependency churn and keeps the
runtime reproducible.

## Prerequisites
- `docker`
- NVIDIA Container Toolkit (so `docker run --gpus all ...` works)
- Network access to pull:
  - `vllm/vllm-openai` (pinned to specific digest for supply-chain security)
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

## Docker Image Security

The `vllm_docker.sh` script pins the Docker image to an immutable digest to prevent
supply-chain attacks where a compromised `latest` tag could introduce malicious code.

Current pinned digest (as of script version):
```
vllm/vllm-openai@sha256:6a43a2dfb6fb4681fe1732d7cd1a0834590b44b7d2bc483886883655468a4591
```

### Updating the Pinned Image

To update to a newer vLLM release:

1. Pull the latest tag and inspect the digest:
   ```bash
   docker pull vllm/vllm-openai:latest
   docker inspect vllm/vllm-openai:latest | jq -r '.[0].RepoDigests[0]'
   ```

2. Validate the image works with your models:
   ```bash
   # Test with a small model first
   docker run --rm --gpus all \
     -p 127.0.0.1:8000:8000 \
     vllm/vllm-openai@sha256:NEW_DIGEST_HERE \
     Qwen/Qwen2.5-1.5B-Instruct \
     --max-model-len 2048
   
   # Run tool-call probe
   python3 tools/local_llm/tool_call_probe.py \
     --url http://127.0.0.1:8000/v1/chat/completions \
     --model Qwen/Qwen2.5-1.5B-Instruct
   ```

3. Update the digest in `tools/local_llm/runtimes/vllm_docker.sh`.

4. Re-run the full probe suite to validate:
   ```bash
   make probe-suite  # or specific vLLM probe config
   ```

This process ensures you consciously review and validate each image update rather than
automatically trusting upstream changes.

