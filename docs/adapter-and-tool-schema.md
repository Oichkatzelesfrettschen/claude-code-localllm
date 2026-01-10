# Adapter and Tool-Call Normalization (Draft)

This document defines a neutral internal schema for tool calls and the mapping
to/from Anthropic Messages API and OpenAI-style chat completions.

## Internal Tool-Call Schema (Canonical)
```
{
  "id": "call_123",
  "name": "tool_name",
  "arguments": { "key": "value" },
  "result": { "ok": true, "data": "..." },
  "status": "pending|completed|failed"
}
```

## Anthropic -> Internal
- `content` blocks with `type: "tool_use"` map to:
  - `id` <- `tool_use.id`
  - `name` <- `tool_use.name`
  - `arguments` <- `tool_use.input`
- Tool results (tool output) map to `result` and set `status`.

## OpenAI -> Internal
- `tool_calls[]` entries map to:
  - `id` <- `tool_call.id`
  - `name` <- `tool_call.function.name`
  - `arguments` <- JSON.parse(`tool_call.function.arguments`)
- Tool results map to `result` and set `status`.

## Internal -> Anthropic
Create `content` blocks:
```
{ "type": "tool_use", "id": "...", "name": "...", "input": {...} }
```

## Internal -> OpenAI
Create `tool_calls[]`:
```
{
  "id": "...",
  "type": "function",
  "function": { "name": "...", "arguments": "{...json...}" }
}
```

## Edge Cases (Must Be Tested)
- Multiple tool calls in one assistant turn.
- Streaming tool calls interleaved with text.
- Invalid JSON in tool arguments.
- Partial tool output (chunked streaming).

## Observed Edge Cases
- Some models return tool-call JSON in `message.content` instead of `tool_calls`
  (non-compliant with OpenAI tool-call schema).
