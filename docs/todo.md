# TODO (Manual Tracker)

This file replaces the unavailable TODOwrite tool. Items are tracked manually.

## Active
### Next 30 steps (fine-grained)
1. [x] Define canonical task classes (L0–L3) with examples and escalation rules.
2. [x] Expand `tools/local_llm/policy_rules.json` denylist for OS/user secret paths (`~/.ssh`, `~/.gnupg`, keychains).
3. [x] Add a JSON schema for policy inputs/outputs (auditable routing decisions).
4. [x] Add a small “policy regression” fixture set (paths + expected routes) and a Make target.
5. [x] Add a “no secrets in logs” sanitizer for probe/policy outputs.
6. [ ] Document a default VRAM threshold strategy (ratio + MiB) and how to choose values.
7. [ ] Extend `tools/local_llm/policy_engine.py` to optionally route to a smaller local model under VRAM pressure.
8. [ ] Add a “capability registry” (context length, tool support, runtime compatibility, tier).
9. [ ] Add per-model metadata capture: `ollama show` + `ollama ps` snapshots into a JSON report.
10. [ ] Add a vLLM tool-call parser matrix (which parser works for which model IDs).
11. [ ] Validate vLLM tool-calls for at least 3 models (small, mid, coder) and record results.
12. [ ] Add a vLLM-only `runtime_probe` Make target (doesn’t require Ollama running).
13. [ ] Add a “one GPU runtime at a time” operational check (warn/error when both Ollama+vLLM are active).
14. [ ] Add a GGUF model shortlist for 2GB/4GB tiers (llama.cpp path) with primary-source links.
15. [ ] Validate at least one GGUF model tool-calling via `llama-server` and record results.
16. [ ] Add `llamacpp` runtime probe config example and document required chat template assumptions.
17. [ ] Tighten `docs/router-config-schema.json` notes and keep it aligned with `claude-code-router` config evolution.
18. [ ] Add `/router-validate` improvement: verify that router slots reference configured models.
19. [ ] Add `/router-backup` retention policy (keep last N backups, configurable).
20. [ ] Add a safe “local-first + OpenRouter + Claude escalation” reference config (documented rationale).
21. [ ] Verify OpenRouter model IDs used in examples against current OpenRouter catalog (do not hardcode stale IDs).
22. [ ] Document direct Gemini provider usage (AI Studio + Vertex) with validated endpoints and transformers.
23. [ ] Add an “agent offload template” for delegating tasks to external models (what to include/exclude).
24. [ ] Add a per-task “routing report” format and example output (why local vs remote).
25. [ ] Add a stable prompt set for latency probes and document variance sources.
26. [ ] Add failure-injection scenarios (timeout, malformed JSON, missing tool_calls) for probes.
27. [ ] Normalize benchmark outputs into a versioned JSON schema for diffing between runs.
28. [ ] Add “known limitations” doc section (unsupported models, tool parsers, VRAM contention).
29. [ ] Add a lightweight CI check (lint JSON + run `make router-config-validate`).
30. [ ] Re-audit and update `docs/repo-audit.md` + `docs/todo.md` after each milestone.

## Blockers
- `devcontainer-cli` AUR package lacks upstream PGP signatures.
- `lttng-ust2.12` conflicts with `lttng-ust` on this system (optional only; avoid unless tracing is required).

## Completed
- Synced `main` with upstream `anthropics/claude-code` (`upstream/main`).
- Added installation requirements doc.
- Added repo audit and routing policy docs.
- Selected claude-code-router for POC.
- Built router policy engine, probe suite, and benchmark harness.
- Validated tool-calling under Ollama:
  - PASS: `llama3.1:latest`, `mistral:latest`, `qwen2.5:7b-instruct`
  - FAIL: `phi3:latest` (runtime: tools unsupported), `qwen2.5-coder:7b` (schema: missing `tool_calls`)
- Added OpenRouter example config + docs (`docs/openrouter-setup.md`).
- Added router config validator + example validation Make target (`make router-config-validate`).
- Added VRAM probe + VRAM bench runner (`make vram-probe`, `make vram-bench`).
- Added VRAM-tier model catalogs and validated 2GB/4GB/8GB/12GB tier probe sets (Ollama).
- Added vLLM Docker runner + validated vLLM tool-calls for `Qwen/Qwen2.5-1.5B-Instruct` using `--tool-call-parser hermes`.
- Added llama.cpp runtime placeholder + docs (`docs/llamacpp-setup.md`).
