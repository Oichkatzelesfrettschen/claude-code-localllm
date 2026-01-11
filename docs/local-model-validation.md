# Local Model Validation Results

All probe runs set `temperature: 0` to reduce tool-selection randomness.

For a concise, reproducible summary by VRAM tier and runtime, see
`docs/model-tier-matrix.md`.

## VRAM-tier probe suites (Ollama)

These results come from `tools/local_llm/probe_suite.py` against Ollama’s
OpenAI-compatible endpoint (`/v1/chat/completions`) with strict `tool_calls`
validation.

Re-run:
- `python3 tools/local_llm/probe_suite.py --url http://127.0.0.1:11434/v1/chat/completions --config tools/local_llm/probe_models_2gb.json`
- `python3 tools/local_llm/probe_suite.py --url http://127.0.0.1:11434/v1/chat/completions --config tools/local_llm/probe_models_4gb.json`
- `python3 tools/local_llm/probe_suite.py --url http://127.0.0.1:11434/v1/chat/completions --config tools/local_llm/probe_models_8gb.json`
- `python3 tools/local_llm/probe_suite.py --url http://127.0.0.1:11434/v1/chat/completions --config tools/local_llm/probe_models_12gb.json`

### 2GB tier (validated)
- PASS: `qwen2.5:0.5b-instruct`, `qwen2.5:1.5b-instruct`, `llama3.2:1b`

### 4GB tier (validated)
- PASS: `llama3.2:3b`, `qwen2.5:3b-instruct`, `qwen2.5:1.5b-instruct`
- FAIL (tools unsupported by runtime): `gemma2:2b`

### 8GB tier (validated)
- PASS: `qwen2.5:7b-instruct`, `mistral:latest`, `llama3.1:latest`

### 12GB tier (validated)
- PASS: `qwen2.5:7b-instruct`, `llama3.1:latest`, `mistral:latest`

## llama.cpp (GGUF) validation
This uses `llama-server` (OpenAI-compatible) and the same strict `tool_calls` probe.

Validated:
- PASS: `Qwen/Qwen2.5-0.5B-Instruct-GGUF` (`qwen2.5-0.5b-instruct-q4_k_m.gguf`) with:
  - `tools/local_llm/runtimes/llamacpp_server.sh` (chat template: `chatml`)
  - `make llamacpp-tool-probe` (auto-detects `/v1/models`; uses a longer timeout)

## qwen2.5:7b-instruct (Ollama)
**Test:** OpenAI-style tool call via `/v1/chat/completions` with `tools[]`.

**Result:** The model returned a valid `tool_calls` array.

**Status:** Pass (tool-calling compliant).

**Notes:** Keep `temperature: 0` for consistent tool-call behavior.

## qwen2.5-coder:7b (Ollama)
**Test:** OpenAI-style tool call via `/v1/chat/completions` with `tools[]`.

**Result:** The model returned a JSON string in `message.content` instead of
`tool_calls`. This does not satisfy tool-call schema requirements.

**Status:** Fail (tool-calling not compliant with required schema).

**Notes:** `ollama show` reports tools capability, but responses still omit
`tool_calls` in OpenAI-compatible mode.

**Observed output:**
```
Tool-call missing; model returned content: {"name": "add", "arguments": {"a": 2, "b": 3}}
```

**Next actions:**
- Re-test with Ollama tool-calling settings (if supported).
- Try a different model/runtime with explicit tool-call support.
- Forced `tool_choice` still returns JSON in `message.content` (non-compliant).
- `/api/chat` streaming endpoint emits JSON text in `message.content`, not `tool_calls`.

## mistral:latest (Ollama)
**Test:** OpenAI-style tool call via `/v1/chat/completions` with `tools[]`.

**Result:** The model returned a valid `tool_calls` array.

**Status:** Pass (tool-calling compliant).

**Observed output:**
```
{"tool_calls":[{"function":{"name":"add","arguments":"{\"a\":2,\"b\":3}"}}]}
```

## phi3:latest (Ollama)
**Test:** OpenAI-style tool call via `/v1/chat/completions` with `tools[]`.

**Result:** Ollama rejects tool usage for this model.

**Status:** Fail (tools not supported by runtime).

**Observed output:**
```
Tool-call probe failed: HTTP 400 ({"error":{"message":"registry.ollama.ai/library/phi3:latest does not support tools","type":"api_error","param":null,"code":null}})
```

## llama3.1:latest (Ollama)
**Test:** OpenAI-style tool call via `/v1/chat/completions` with `tools[]`.

**Result:** The model returned a valid `tool_calls` array.

**Status:** Pass (tool-calling compliant).
