# Local-First Offload Playbook (Draft)

Purpose: make the **local model** the default executor for safe, bounded work,
while using **Claude** as the escalation/synthesis path for high-risk or
high-uncertainty tasks.

## What to Offload to Local (good fits)
- Formatting and mechanical refactors in non-sensitive paths.
- Generating test scaffolds (when the repo already has a test harness).
- Summarizing diffs, changelog drafts, and documentation edits.
- Running probes/benchmarks and reporting results.

## What to Keep on Claude (default)
- Auth/security/infra changes (path-based sensitivity).
- Multi-file architectural changes with unclear blast radius.
- Legal/compliance or license interpretation beyond primary sources.
- Long-context analysis (large repos, many files, deep refactors).

## Escalation Triggers (fail closed)
- Any tool-call schema failure or repeated tool retries.
- Any denylisted or sensitive paths in the change set.
- Context length threshold exceeded.
- VRAM pressure below threshold (or runtime instability / OOM).

## Concrete “Local Primary” Configuration (router)
With `claude-code-router`, the practical pattern is:
- Route `default` and `background` to a local tool-call-compliant model.
- Route `think` and `longContext` to Claude.

See `docs/examples/router-config.json` and `docs/local-llm-setup.md`.

