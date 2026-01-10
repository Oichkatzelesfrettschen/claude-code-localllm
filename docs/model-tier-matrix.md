# Model Tier Matrix (Validated)

This is a reproducible summary of tool-call validation runs performed with the
repo’s probes.

## Probe definition
“Tool-call compliant” means the model returns OpenAI-compatible `tool_calls`
with valid JSON arguments matching the declared schema (see
`tools/local_llm/tool_call_probe.py` and `tools/local_llm/runtime_probe.py`).

## Ollama (OpenAI-compatible endpoint)
Endpoint: `http://127.0.0.1:11434/v1/chat/completions`

Validated tiers (configs in `tools/local_llm/`):
- 2GB: `qwen2.5:0.5b-instruct`, `qwen2.5:1.5b-instruct`, `llama3.2:1b`
- 4GB: `llama3.2:3b`, `qwen2.5:3b-instruct`, `qwen2.5:1.5b-instruct`
- 8GB: `qwen2.5:7b-instruct`, `mistral:latest`, `llama3.1:latest`
- 12GB: `qwen2.5:7b-instruct`, `llama3.1:latest`, `mistral:latest`

Known failures:
- `gemma2:2b` (Ollama rejects tools for this model)
- `phi3:latest` (tools unsupported by runtime)
- `qwen2.5-coder:7b` (omits `tool_calls` in OpenAI-compatible mode)

Re-run (per tier):
```
python3 tools/local_llm/probe_suite.py --url http://127.0.0.1:11434/v1/chat/completions --config tools/local_llm/probe_models_2gb.json
python3 tools/local_llm/probe_suite.py --url http://127.0.0.1:11434/v1/chat/completions --config tools/local_llm/probe_models_4gb.json
python3 tools/local_llm/probe_suite.py --url http://127.0.0.1:11434/v1/chat/completions --config tools/local_llm/probe_models_8gb.json
python3 tools/local_llm/probe_suite.py --url http://127.0.0.1:11434/v1/chat/completions --config tools/local_llm/probe_models_12gb.json
```

## vLLM (Docker OpenAI-compatible server)
Endpoint: `http://127.0.0.1:8000/v1/chat/completions`

Validated:
- PASS: `Qwen/Qwen2.5-1.5B-Instruct` when started with:
  - `--enable-auto-tool-choice`
  - `--tool-call-parser hermes`

Re-run:
```
tools/local_llm/runtimes/vllm_docker.sh Qwen/Qwen2.5-1.5B-Instruct
python3 tools/local_llm/tool_call_probe.py --url http://127.0.0.1:8000/v1/chat/completions --model Qwen/Qwen2.5-1.5B-Instruct
```

Operational note: running vLLM concurrently with GPU-accelerated Ollama can
exhaust VRAM and crash Ollama (treat as a blocking constraint).

## llama.cpp (OpenAI-compatible server)
Placeholder support is wired in `tools/local_llm/runtime_matrix.json` as
runtime `llamacpp`. Validation depends on the chosen GGUF model and chat
template (see `docs/llamacpp-setup.md`).

