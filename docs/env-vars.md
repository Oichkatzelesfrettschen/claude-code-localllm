# Environment Variable Strategy

Use `ccr activate` to emit environment variables for the current shell. For
persistent configuration, add the output to your shell profile.

## Variables
- `ANTHROPIC_BASE_URL` -> Router endpoint (Claude Code calls route here).
- `ANTHROPIC_AUTH_TOKEN` -> Router API key (if configured).
- `ANTHROPIC_API_KEY` -> Required for Anthropic provider routes (think/longContext).
- `OPENROUTER_API_KEY` -> Required for OpenRouter provider routes (Gemini / OpenAI-style models).
- `NO_PROXY` -> Avoid proxying local endpoints.

## Recommended Usage
```
eval "$(ccr activate)"
```

## Per-Project Overrides
Use project-local shell scripts or direnv to scope routing:
```
export ANTHROPIC_BASE_URL="http://127.0.0.1:3456"
export NO_PROXY="127.0.0.1,localhost"
```
