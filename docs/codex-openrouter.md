# “Codex” via OpenRouter (Notes)

Interpretation: “Codex via OpenRouter” means using an OpenAI-style coding model
served through the OpenRouter OpenAI-compatible endpoint, so it can be used as
a router target alongside local runtimes.

## How it fits this repo
- Primary interactive agent remains Claude Code.
- `claude-code-router` handles routing to OpenRouter models (including “codex-like” coding models).
- Local models remain the default for safe tasks; “codex-like” models can be used as an intermediate tier or for specialized coding tasks.

## Configuration
Use the `openrouter` provider in `~/.claude-code-router/config.json`:
- `api_base_url`: `https://openrouter.ai/api/v1/chat/completions`
- `api_key`: `$OPENROUTER_API_KEY`
- `transformer`: `{ "use": ["openrouter"] }`

Example: `docs/examples/router-config-openrouter.json`

## Validation expectations
Treat tool calling as a hard requirement if you want these models to handle tool-using tasks:
- Must produce OpenAI-compatible `tool_calls`.
- Arguments must be valid JSON and match schema.

Use:
- `make tool-probe` (single model)
- `make probe-suite` (known-good set)

## Notes
OpenRouter model IDs change over time; keep examples as placeholders and validate against OpenRouter’s current catalog.

