# Plugin UX Draft

## Commands
- `/models` — List available local and remote models with tool-call status.
- `/router status` — Show active route, config path, and health checks.
- `/router set <tier> <provider,model>` — Update routing for L0/L1/L2.
- `/router validate` — Run probe suite and policy checks.

## UX Principles
- Default to safe routes; warn before enabling local routing on sensitive paths.
- Show tool-call compliance status for each model.
- Require explicit confirmation for config edits.

## Outputs
Every command should return:
- Current routing table
- Model availability
- Last probe status
