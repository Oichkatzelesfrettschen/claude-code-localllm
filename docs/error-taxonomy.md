# Error Taxonomy and Retry Policy (Draft)

Warnings are treated as errors. Any error with a security or policy impact
forces escalation to Claude.

## Error Categories
1) **Transport**
   - Timeouts, connection errors, DNS failures.
2) **Adapter/Schema**
   - Invalid JSON, mismatched tool-call schema, missing fields.
3) **Policy**
   - Denylisted paths, restricted data, or policy violations.
4) **Model**
   - Tool-call hallucinations, low-confidence output, unsupported tools.
   - Runtime error: `does not support tools` (HTTP 400 from Ollama).
5) **Runtime**
   - Local model out of memory, missing model, server unavailable.

## Retry and Escalation Rules
- **Transport**: Retry locally up to 2 times, then escalate to Claude.
- **Adapter/Schema**: No retry; escalate immediately.
- **Policy**: Block or route to Claude-only.
- **Model**: Retry once locally; if still invalid, escalate.
- **Runtime**: Switch to fallback local model; if unavailable, escalate.

## Logging Requirements
Every error must include:
- `error_category`
- `route`
- `model`
- `task_class`
- `path_list` (redacted if sensitive)
