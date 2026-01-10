# Example Configs

These are sandboxed examples and may require validation against the current
router's supported transformers.

Validate structure + slot/model consistency with `make router-config-validate`.

## router-config.json
- Includes a local `ollama` provider and a live `anthropic` provider.
- Requires `ANTHROPIC_API_KEY` to be set for the Anthropic provider.
- Uses the `anthropic` transformer; validate support in your router build.
- Lists `llama3.1:latest`, `mistral:latest`, and `qwen2.5:7b-instruct` as validated Ollama models.

## router-config-openrouter.json
- Includes a local `ollama` provider and an `openrouter` provider.
- Requires `OPENROUTER_API_KEY` to be set for the OpenRouter provider.
- Uses the `openrouter` transformer; validate support in your router build.
- Example OpenRouter model IDs are placeholders and may change; verify against OpenRouter.
