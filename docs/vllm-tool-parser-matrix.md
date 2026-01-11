# vLLM Tool-Call Parser Matrix (Empirical Notes)

This doc records observed behavior for vLLM tool calling when using
`--enable-auto-tool-choice` plus a chosen `--tool-call-parser`.

Context: tool-call probes in this repo require OpenAI-compatible `tool_calls`
with valid JSON arguments.

## Qwen/Qwen2.5-1.5B-Instruct

Server: `vllm/vllm-openai:latest` (Docker), `MAX_MODEL_LEN=4096`, `GPU_MEM_UTIL=0.70`.

| Parser | Result | Notes |
| --- | --- | --- |
| `hermes` | PASS | Produces OpenAI `tool_calls`; passes `tools/local_llm/tool_call_probe.py`. |
| `pythonic` | FAIL | Emits `<tool_call> ... </tool_call>` in `message.content` (no `tool_calls`). |
| `openai` | FAIL | Returned HTTP 500: `OpenAIToolParser requires token IDs and does not support text-based extraction.` |

## Next models to validate
- Qwen/Qwen2.5-7B-Instruct (likely: `hermes` or `qwen3_*` parsers; validate)
- A coder-tuned model (tool calling may differ)
- A Mistral instruct model (try `mistral` parser)

