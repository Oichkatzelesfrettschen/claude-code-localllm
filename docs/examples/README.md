# Example Configs

These are sandboxed examples and may require validation against the current
router's supported transformers.

## router-config.json
- Includes a local `ollama` provider and a live `anthropic` provider.
- Requires `ANTHROPIC_API_KEY` to be set for the Anthropic provider.
- Uses the `anthropic` transformer; validate support in your router build.
- Lists `llama3.1:latest`, `mistral:latest`, and `qwen2.5:7b-instruct` as validated Ollama models.
