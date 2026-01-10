# Repository Guidelines

## Project Structure & Module Organization
- `docs/` holds the local-LLM roadmap, audits, and operational runbooks.
- `tools/local_llm/` contains probe, policy, and benchmark tooling.
- `plugins/` hosts example plugins with `.claude-plugin/` metadata and READMEs.
- `.claude/commands/` stores repo-local Claude commands (Markdown + YAML frontmatter).
- `scripts/` contains Bun-based automation (TypeScript).
- `examples/` provides hook validators and sample router configs.
- `Script/` includes PowerShell helpers (devcontainer launcher).
- `.devcontainer/` defines containerized dev environments.
- `Makefile` bundles validation targets for tooling and probes.

## Build, Test, and Development Commands
- `make tool-probe`: validate tool-call compliance for `OLLAMA_MODEL`.
- `make probe-suite`: required-model probe suite (should pass).
- `make probe-suite-candidates`: candidate-model probe suite (expected to fail until models pass).
- `make latency-probe`: run a simple latency benchmark.
- `make runtime-probe`: run tool-call + latency probes across runtimes.
- `make policy-check`: validate routing policy rules.
- `make verify-devcontainer`: verify the devcontainer CLI tarball integrity.
- `bun run scripts/auto-close-duplicates.ts`: GitHub issue automation.
- `GITHUB_TOKEN=... bun run scripts/backfill-duplicate-comments.ts`: backfill comments.
- `pwsh Script/run_devcontainer_claude_code.ps1`: launch devcontainer (Windows).

## Coding Style & Naming Conventions
- TypeScript scripts use 2-space indentation, `async`/`await`, and explicit typing.
- Plugin and command names are kebab-case (for example, `plugins/local-llm-router/`).
- Markdown files with YAML frontmatter keep frontmatter at the top.
- Update `docs/installation-requirements.md` when adding new dependencies.

## Testing Guidelines
- No unit test framework is configured; run the relevant script or Make target.
- Treat warnings as errors and document failures in `docs/local-model-validation.md`.
- For local LLM changes, run `make tool-probe` and `make probe-suite`.

## Commit & Pull Request Guidelines
- Prefer Conventional Commit format (`type: summary`).
- PRs include a summary, validation notes, and linked issues.
- Update `CHANGELOG.md` for user-visible changes and keep plugin READMEs current.

## Security & Configuration Tips
- Never commit secrets; use env vars (`GITHUB_TOKEN`, `ANTHROPIC_API_KEY`).
- Follow `SECURITY.md` for vulnerability reporting.
- Avoid hardcoded API keys in router configs; use placeholders.
