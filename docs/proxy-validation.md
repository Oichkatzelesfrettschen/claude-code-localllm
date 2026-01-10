# Proxy Validation Results

## claude-code-router + Ollama (llama3.1:latest)
**Test:** Anthropic Messages API request to `http://127.0.0.1:3456/v1/messages`
with a tool definition.

**Result:** Router returned a valid `tool_use` block.

**Status:** Pass (end-to-end tool call through proxy works).
