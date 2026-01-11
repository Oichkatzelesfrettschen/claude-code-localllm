# GGUF Shortlist (llama.cpp path)

Goal: identify small-footprint local models that can run under constrained VRAM
using `llama.cpp` (GGUF quantizations).

Important: **tool calling is not yet validated** for these GGUF models under
this repo’s strict OpenAI `tool_calls` probe. Many instruct chat templates emit
`<tool_call>...</tool_call>` in plain text; that may require an adapter layer
or a different probe mode.

## 2GB tier candidates
- `Qwen/Qwen2.5-0.5B-Instruct-GGUF` (license tag: Apache-2.0)
  - https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF
- `Qwen/Qwen2.5-1.5B-Instruct-GGUF` (license tag: Apache-2.0)
  - https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF
- `unsloth/Llama-3.2-1B-Instruct-GGUF` (license tag: Llama 3.2)
  - https://huggingface.co/unsloth/Llama-3.2-1B-Instruct-GGUF

## 4GB tier candidates
- `Qwen/Qwen2.5-1.5B-Instruct-GGUF`
  - https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF
- (Optional) `Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF` (coding-tuned; validate tool output)
  - https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF

## Quantization guidance (rules of thumb)
- Start with `Q4_K_M` or `Q5_K_M` for a strong size/quality tradeoff.
- Use `Q8_0` only if you have headroom; it can exceed the “2GB tier” goal even on small models.

## Next validation steps (planned)
1) Pick one GGUF file from the shortlist (start with Qwen 0.5B or 1.5B).
2) Start `llama-server` using `tools/local_llm/runtimes/llamacpp_server.sh`.
3) Run `python3 tools/local_llm/tool_call_probe.py` against `http://127.0.0.1:8081/v1/chat/completions`.
4) If output lands in `message.content` (no `tool_calls`), add an adapter/probe mode to parse `<tool_call>` blocks.

