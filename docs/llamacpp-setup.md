# llama.cpp Setup (OpenAI-compatible server)

For very low VRAM footprints (2GB/4GB), `llama.cpp` + GGUF quantizations are
often more practical than vLLM.

## Prerequisites
- `llama-server` available in PATH (from a local `llama.cpp` build or a package)
- A GGUF model file (quantized)

## Start server
This repo includes a helper:
```
tools/local_llm/runtimes/llamacpp_server.sh /path/to/model.gguf
```

Defaults:
- Endpoint: `http://127.0.0.1:8081/v1/chat/completions`
- Context: `CTX=4096`
- GPU layers: `GPU_LAYERS=0` (CPU-only by default)

## Probe
```
python3 tools/local_llm/tool_call_probe.py \
  --url http://127.0.0.1:8081/v1/chat/completions \
  --model local-gguf
```

## Notes
- Tool-call compliance depends heavily on the model + chat template.
- Use `tools/local_llm/runtime_probe.py` with a temporary config that enables
  the `llamacpp` runtime once you have a known-good GGUF model.

