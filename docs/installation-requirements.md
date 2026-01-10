# Installation Requirements

This repository is primarily documentation and plugin examples. Requirements
apply only when running the scripts, hooks, or dev tooling listed below. Treat
missing tools as errors before executing the related module.

## System Baseline (Audit Snapshot)
Detected on this machine (CachyOS / Arch):
- Found: `bun`, `python3`, `jq`, `git`, `gh`, `node`, `npm`, `make`, `curl`
- Found (containers): `docker`, `podman`, `devcontainer`
- Found (GPU/local-LLM): `nvidia-smi`, `nvcc`, `ollama`
- Installed (AUR/system): `devcontainer-cli` (`@devcontainers/cli`), `powershell-bin` (`pwsh`)
- Notes: `lttng-ust` is installed; `lttng-ust2.12` is optional and conflicts with `lttng-ust` on this system.

## Module Requirements

### Core Documentation
Files: `README.md`, `AGENTS.md`, `docs/`
- No runtime dependencies.

### Bun Automation Scripts
Files: `scripts/auto-close-duplicates.ts`, `scripts/backfill-duplicate-comments.ts`
- Required: `bun` in PATH.
- Required env: `GITHUB_TOKEN` (GitHub API access).
- Notes: These scripts call GitHub APIs over the network.

### Claude Commands (Repo-Local)
Files: `.claude/commands/*.md`
- `commit.md`, `commit-push-pr.md`:
  - Required: `git`
  - Required for PR flow: `gh` (GitHub CLI)
- `oncall-triage.md`:
  - Required: `gh`, `jq`

### Hookify Plugin
Files: `plugins/hookify/**/*`
- Required: `python3` (README calls out Python 3.7+).
- Optional (for shell-based hook examples): `jq`, `bash`.

### Security Guidance Plugin
Files: `plugins/security-guidance/hooks/security_reminder_hook.py`
- Required: `python3`.

### Ralph Wiggum Plugin
Files: `plugins/ralph-wiggum/**/*`
- Required: `bash`
- Required: `jq` (used by `hooks/stop-hook.sh`)
- Required: `git` (workflow depends on history and diffs)

### DevContainer Helper (Windows)
Files: `Script/run_devcontainer_claude_code.ps1`
- Required: `pwsh` (PowerShell 7+ recommended on Windows)
- Required: `devcontainer` CLI (`devcontainer-cli`)
- Required backend: `docker` or `podman`
- In-container: `zsh`, `claude` available in the devcontainer image

### Examples
Files: `examples/hooks/bash_command_validator_example.py`
- Required: `python3`

### Plugin Development Tooling (Docs and Examples)
Files: `plugins/plugin-dev/**`
- Required for running helper scripts: `bash`, `jq`
- Optional for examples: `node`, `python3`, `git`
- Notes: Many files are templates or reference docs; only install what you run.

## Installation Notes (CachyOS / Arch)
If you want me to install missing tools, provide a package list and whether you
prefer `pacman` or `yay`. I will not install anything without explicit targets.

### Current Install Notes
- `devcontainer-cli` was installed from AUR and emitted a warning about missing
  upstream PGP signatures. Treat this as a supply-chain risk; prefer a signed
  distribution if available.
- Verify the npm tarball integrity before relying on the CLI:
  `python3 tools/supply_chain/verify_npm_integrity.py --package @devcontainers/cli --version 0.80.3 --tarball /tmp/devcontainer-cli-0.80.3.tgz`
- `powershell-bin` was installed from `chaotic-aur` after importing and signing
  the Garuda builder key.
- Optional for PowerShell tracing: `lttng-ust2.12` (conflicts with `lttng-ust` on this system).
- vLLM packages are not installed yet; selection pending (`python-vllm-bin` vs `python-vllm` vs `python-vllm-cuda`).
  - `python-vllm-cuda` currently fails to resolve dependencies (`cuda-tools`, `gcc13-libs`) in AUR.

### Devcontainer CLI Alternatives (AUR)
- `devcontainer-cli` (installed)
- `devc`, `devc-bin` (alternatives)

Avoid using `--skippgpcheck` unless explicitly required; prefer integrity
verification (see `tools/supply_chain/verify_npm_integrity.py`).

## Local LLM Runtime (Planned)
- `ollama` (installed) for local model hosting.
- Start with `ollama serve` and verify with `ollama list`.
- Models are pulled on demand (example: `ollama pull qwen2.5:7b-instruct`).

## Router/Proxy (Planned)
- `@musistudio/claude-code-router` installed globally via npm.
- Config path: `~/.claude-code-router/config.json`

## Alternate Runtimes (Planned)
- vLLM for OpenAI-compatible serving on GPU.
  - Candidate packages: `python-vllm-bin`, `python-vllm`, `python-vllm-cuda`.
  - Hybrid runtime: `vllama` (vLLM + Ollama management).
  - Install and document the chosen package before enabling vLLM probes.

## Build/Validation Harness
- `make` and `curl` are required to run the `Makefile` targets.
