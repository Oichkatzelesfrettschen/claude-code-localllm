# Repository Audit and Re-Audit

## Scope and Method
This audit is based on a full file listing, file-type counts, dependency
scanning (shebangs and command references), and targeted content reads of
scripts, hooks, and root documentation. Warnings are treated as errors.

## High-Level Summary
This repository is a documentation- and example-plugin bundle for Claude Code.
It now includes a minimal `Makefile` for validation utilities. It contains:
- Markdown docs describing plugins, commands, agents, and skills.
- A few executable scripts (Bun, Python, Bash, PowerShell).
- Minimal build harness (`Makefile`) for verification and probes.

## Top-Level Structure (Primary Roles)
- `README.md`, `CHANGELOG.md`, `LICENSE.md`, `SECURITY.md`: Product docs and
  policy.
- `.claude/commands/`: Repo-local Claude Code commands (Markdown with
  frontmatter).
- `plugins/`: Plugin examples (commands, skills, agents, hooks).
- `plugins/local-llm-router/`: New plugin for routing inspection and control.
- `scripts/`: Bun scripts for GitHub issue automation.
- `examples/`: Small hook examples.
- `.devcontainer/`: DevContainer config (used by PowerShell helper).
- `Script/`: PowerShell helper for DevContainer workflows.
- `docs/`: Roadmap, integration, and audit docs for local LLM work.
- `tools/`: Local LLM probes, policy engine, and supply-chain verification.

## File-Type Breakdown (Counts)
Based on a full recursive listing:
- Markdown: 133 files
- JSON: 31 files
- YAML: 16 files
- Shell scripts: 16 files
- Python: 20 files
- TypeScript: 2 files

## Executable Surfaces and Dependencies
### Bun scripts
`scripts/auto-close-duplicates.ts`, `scripts/backfill-duplicate-comments.ts`
- Dependencies: `bun`, network access, `GITHUB_TOKEN`.
- Risk: external API calls, requires token hygiene.

### Python hooks
`plugins/hookify/**/*`, `plugins/security-guidance/**/*`
- Dependencies: `python3` (Hookify docs indicate Python 3.7+).
- Risk: parsing hook input, relies on `jq` for JSON in shell scripts.

### Shell hooks
`plugins/ralph-wiggum/hooks/stop-hook.sh`
- Dependencies: `bash`, `jq`, `git`.
- Risk: stop-hook runs on session end; must remain robust.

### PowerShell helper
`Script/run_devcontainer_claude_code.ps1`
- Dependencies: `pwsh`, `devcontainer`, `docker` or `podman`.
- Risk: fails fast when dependencies missing.

## Interconnections
- `plugins/README.md` is the index for all plugin examples.
- `.claude/commands/` entries rely on `git` and `gh` to execute.
- Hookify docs reference Python regex and local `.claude` rule files.

## Known Gaps and Errors
- `Makefile` targets exist for probes and verification, but they are not wired into CI.
- `devcontainer` CLI was missing on this machine (now installed via AUR).
- `pwsh` was missing (now installed from `powershell-bin`).
- `gemini.md` exists and points at `claude-code-router` + OpenRouter examples; direct Gemini/Vertex paths should still be validated before relying on them for tool-using workloads.
- AUR `devcontainer-cli` emits a "Skipping verification of source file PGP
  signatures" warning. This is a supply-chain risk and must be documented.
- npm tarball integrity for `@devcontainers/cli@0.80.3` was verified against the
  registry integrity hash (see `tools/supply_chain/verify_npm_integrity.py`).
- `powershell-bin` lists optional dependency `lttng-ust2.12` (not installed).
  Attempted install required sudo input; pending user interaction.
  `lttng-ust2.12` conflicts with `lttng-ust` on this system.

## TODO/FIXME Scan
- No active TODO/FIXME in core scripts.
- References to TODOs exist in documentation examples only.

## Assertions and Testable Hypotheses (Validated)
| Assertion | Hypothesis | Source | Status |
| --- | --- | --- | --- |
| Claude Code is proprietary | License is all-rights-reserved | `LICENSE.md` | Verified |
| Proxy env vars exist | Proxy-related env vars appear in release notes | `CHANGELOG.md` | Verified |
| Router supports `ANTHROPIC_BASE_URL` | Router README documents env activation | `claude-code-router` README | Verified |
| Mistral/Qwen/Phi licenses | HF metadata reports Apache-2.0 or MIT | HF model API | Verified |
| Llama 3 restrictions | License forbids using outputs to improve other LLMs | Llama 3 LICENSE | Verified |

## Assertions from Draft That Remain Unverified
These claims were not found in primary sources and should not be used without
evidence:
- Alleged DMCA takedown details.
- Claims of API access revocation for external parties.
- Specific star counts or usage metrics without source citations.

## Re-Audit (Deeper View by Module)
### `plugins/`
- Primarily documentation and templates, not production code.
- Each plugin is self-contained and documents its own behavior.
- `local-llm-router` adds commands for inspecting and updating router config.

### `.claude/commands/`
- Command definitions rely on `git` and `gh`.
- Security posture depends on command `allowed-tools` restrictions.

### `scripts/`
- Scripts are operational and should be treated as production-grade; they make
  direct GitHub API calls and should be tested before use.

## Recommended Next Actions
1) Add a minimal build/test harness for new local-LLM integration utilities.
2) Document supply-chain risk for AUR `devcontainer-cli` or switch to a verified
   install path.
3) Codify routing policy as a separate config and validate with tests.
4) Expand runtime-aware routing (VRAM pressure, timeouts, and stable fallbacks).
