# Logging and Tracing

## claude-code-router Logs
Default log paths (per router docs):
- `~/.claude-code-router/logs/` (server-level logs)
- `~/.claude-code-router/claude-code-router.log` (routing decisions)

## Required Fields
Every routing decision should include:
- model, route, task class
- policy outcome (allow/deny/escalate)
- error category (if any)

## Action
Ensure `LOG` and `LOG_LEVEL` are set in `~/.claude-code-router/config.json`.
