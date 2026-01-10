# Task Classification (L0–L3)

This repo uses a simple, auditable task classification scheme to decide when a
request may be handled by a local model vs. when it must escalate to Claude.

## L0 — Public / sanitized
- Inputs: public docs, sanitized logs, non-sensitive refactors, formatting.
- Allowed: local-first.
- Escalate to Claude: any tool-call failure, policy warning, or uncertainty.

Examples:
- “Update README formatting”
- “Summarize `docs/benchmarks.md`”

## L1 — Routine engineering
- Inputs: typical app code changes without secrets/auth/compliance scope.
- Allowed: local-first with strict tool-call requirements.
- Escalate: repeated tool failures, multi-file uncertainty, or VRAM pressure.

Examples:
- “Refactor helper function in `tools/local_llm/*`”
- “Add a new Make target with minimal changes”

## L2 — Security-adjacent / multi-file / higher risk
- Inputs: multi-file changes, build system changes, supply-chain risk, deployment.
- Default: Claude-first.
- Local allowed only with explicit approval + audited diffs.

Examples:
- “Change router/proxy defaults”
- “Modify supply-chain verification scripts”

## L3 — Secrets / auth / compliance
- Inputs: credentials, tokens, auth flows, key material, private keys, sensitive configs.
- Route: Claude-only (no local).

Examples:
- “Edit `.env` or `~/.ssh/*`”
- “Rotate API keys / credentials”

## Primary signals
Classification should be based on:
1) File paths (denylist/sensitive patterns)
2) Task intent (auth/security/compliance vs routine)
3) Runtime health (tool-call compliance + VRAM pressure)

