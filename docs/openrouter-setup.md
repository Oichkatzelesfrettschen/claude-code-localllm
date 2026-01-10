# OpenRouter Setup (Gemini + “Codex” models)

This repo’s routing approach uses `claude-code-router` as the external proxy.

Primary reference: https://github.com/musistudio/claude-code-router

## Environment variables
- `OPENROUTER_API_KEY`: required for OpenRouter provider routes.
- `ANTHROPIC_API_KEY`: required for direct Anthropic provider routes (if enabled).

Keep keys in your shell environment (not in repo files).

## Router config (example)
Use `docs/examples/router-config-openrouter.json` as a starting point for:
- Local (Ollama) as `default` / `background`
- OpenRouter Gemini as `longContext`
- OpenRouter “Codex-style” model as `think` (optional)

## Activate + run
1) Start Ollama: `ollama serve`
2) Start router: `ccr start`
3) Activate env vars: `eval "$(ccr activate)"`
4) Validate:
   - `make router-config-validate` (validates repo example configs)
   - `python3 tools/local_llm/validate_router_config.py --path ~/.claude-code-router/config.json --require-env`
   - `make tool-probe`
   - `make probe-suite`
   - `make runtime-probe`
