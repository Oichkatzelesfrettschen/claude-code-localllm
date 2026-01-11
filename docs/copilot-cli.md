# GitHub Copilot CLI (local tool)

This machine has both:
- `gh copilot` (GitHub CLI `copilot` command)
- `copilot` (standalone Copilot CLI binary)

These are optional helpers and are **not** wired into Claude Code routing.

## Repo-local Claude command
This repo includes a helper command for invoking `gh copilot` from Claude Code:
- `.claude/commands/copilot-suggest.md`

## Quick checks
- `gh copilot --help`
- `copilot --help`
- `gh auth status`

## Authentication
- `gh copilot` uses GitHub auth; if it errors, re-auth with the Copilot scope:
  - `gh auth login -s copilot`
- The standalone `copilot` CLI has its own auth flow; follow its `--help` prompts.

## Safety
- Treat outputs as suggestions; don’t auto-apply changes without review.
- Never paste secrets; follow `SECURITY.md`.
