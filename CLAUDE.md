# Project Guidance (claude-code-localllm)

This repository tracks experiments and tooling to run Claude Code with a local-LLM router/proxy (local-first with escalation).

## Quality Bar
- Treat warnings as errors: if a tool/run emits warnings, either fix or explicitly document why it is acceptable.
- Prefer verified, reproducible workflows over demos or hardcoded examples.
- Never commit secrets; use environment variables (see `SECURITY.md`).

## Documentation Discipline
- When adding or changing any dependency, update `docs/installation-requirements.md`.
- Keep `docs/todo.md` current (this repo does not have a TODOwrite tool).
- If a doc makes a factual claim, add a primary source link or mark it unverified.

## Validation Commands
- Supply chain: `make verify-devcontainer`
- Router config examples: `make router-config-validate`
- Policy engine: `make policy-check`
- Local model tool calling (requires `ollama serve`): `make tool-probe` and `make probe-suite`
- Latency baseline (requires `ollama serve`): `make latency-probe`
- VRAM deltas around probes (NVIDIA): `make vram-bench VRAM_BENCH_CONFIG=tools/local_llm/probe_models_4gb.json`

## Local LLM Quickstart
See `docs/local-llm-setup.md` and `docs/operator-runbook.md`.
