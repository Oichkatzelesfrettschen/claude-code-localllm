# Local LLM Router Plugin

This plugin provides commands to inspect and manage local LLM routing for the
claude-code-router proof of concept.

## Commands
- `/models` - list configured providers and models.
- `/router-status` - show router status and endpoint.
- `/router-set` - update routing slots with confirmation and backup.

## Requirements
- `@musistudio/claude-code-router` installed and running.
- Local model runtime (for example `ollama`) if routing to local models.
