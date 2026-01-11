# llama.cpp Setup (OpenAI-compatible server)

For very low VRAM footprints (2GB/4GB), `llama.cpp` + GGUF quantizations are
often more practical than vLLM.

Candidate GGUF models: `docs/llamacpp-gguf-shortlist.md`.

## Prerequisites
- `llama-server` available in PATH (from a local `llama.cpp` build or a package)
- A GGUF model file (quantized)

Arch/CachyOS note: the `llama-cpp-cuda-git` package (chaotic-aur) installs binaries under
`/opt/llama-cpp/bin/`. This repo’s helper script detects that path automatically.

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
make llamacpp-tool-probe
```

## Notes
- Tool-call compliance depends heavily on the model + chat template.
- The Make target auto-detects the server’s advertised model ID via `GET /v1/models` and uses a longer timeout.
- Use `tools/local_llm/runtime_probe.py` with a temporary config that enables
  the `llamacpp` runtime once you have a known-good GGUF model.
