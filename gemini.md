# Gemini Routing Notes (claude-code-localllm)

This repo’s local-LLM routing work assumes an external router/proxy. For Gemini
support, the primary reference is `claude-code-router`:
https://github.com/musistudio/claude-code-router

## Key Points (from primary sources)
- `claude-code-router` lists **Gemini** as a supported provider and ships a built-in
  `gemini` transformer, plus `vertex-gemini` for Vertex authentication.
- `claude-code-router` supports environment-variable interpolation in
  `~/.claude-code-router/config.json`, including `GEMINI_API_KEY`.

## Practical Options

### Option A: Gemini via OpenRouter (simplest)
Use the `openrouter` provider with a Gemini model ID (example from router docs:
`google/gemini-2.5-pro-preview`) and the `openrouter` transformer.

Pros: avoids Gemini-specific endpoints/auth flows.  
Cons: routes through OpenRouter (not direct Gemini API).

### Option B: Direct Gemini provider (Google AI Studio)
Configure a provider that uses a Gemini API key (`GEMINI_API_KEY`) and the
router’s built-in `gemini` transformer.

Pros: direct Gemini API key.  
Cons: endpoint/auth details must match the router’s current implementation.

### Option C: Vertex Gemini
Use the router’s `vertex-gemini` transformer when you want Vertex-based auth.

## Safety Notes
- Keep API keys in environment variables (not in committed files).
- Prefer routing `think` / `longContext` to Claude unless Gemini behavior is
  validated for your tool-use workload.

## Local config example
See `docs/examples/router-config-openrouter.json`.

## Validation
- Validate router config examples: `make router-config-validate`
- Validate local tool calling (Ollama): `make tool-probe` and `make probe-suite`
