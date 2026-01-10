# Routing Policy (Draft v0)

Treat any policy warning as a hard failure. Routes must be deterministic and
auditable. All paths and patterns are case-sensitive unless noted.

## Policy Goals
- Keep sensitive or restricted data on Claude.
- Use local models only for safe, bounded tasks.
- Escalate on uncertainty or tool-call instability.
- Preserve tool-permission rules and audit trails.

Task classes are defined in `docs/task-classification.md`.

## Tier Rules (Default)
| Tier | Allowed Data | Default Route | Escalation |
| --- | --- | --- | --- |
| L0 | Public or sanitized content | Local | On any tool error |
| L1 | Routine code edits | Local-first | Claude on retries |
| L2 | Security-adjacent or multi-file | Claude-first | Claude-only if sensitive |
| L3 | Secrets, auth, compliance | Claude-only | No local |

**Local model requirement:** Must pass tool-call probes (e.g., `llama3.1:latest`
via Ollama). Models that only return JSON in `message.content` are disallowed
for tool-using tasks.

## Path-Based Restrictions
Always route to Claude if any file path matches:
- `.env`, `.env.*`, `**/secrets/**`, `**/credentials/**`
- `**/auth/**`, `**/security/**`, `**/infra/**`
- `**/.git/**`, `**/.ssh/**`, `**/.gnupg/**`
- `**/config/**` if it contains tokens or access keys

## Escalation Triggers
- Tool-call failure or malformed tool output.
- Streaming or schema mismatch in tool calls.
- Context length exceeds configured threshold.
- Model reports low confidence or violates system prompt.
- Low free VRAM or runtime instability on the local GPU.
- Any policy violation or missing dependency.

Use `make vram-probe` and `make vram-bench` to make VRAM pressure observable
and treat regressions as blocking.

## Example Policy Evaluation
```
task: "Update README formatting"
paths: ["README.md"]
classification: L0
route: local

task: "Refactor auth middleware"
paths: ["src/auth/middleware.ts"]
classification: L3 (auth path)
route: Claude-only
```

## Required Config Inputs
- `long_context_threshold_tokens`
- `local_models[]` with capability flags
- `claude_models[]` with pricing
- `denylist_paths[]` and `denylist_patterns[]`
- `escalation_retry_limit`
- Optional runtime inputs:
  - `min_free_vram_mib` / `min_free_vram_ratio` (set to `0` to disable)
