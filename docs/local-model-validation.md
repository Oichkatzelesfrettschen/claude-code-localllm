# Local Model Validation Results

All probe runs set `temperature: 0` to reduce tool-selection randomness.

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
