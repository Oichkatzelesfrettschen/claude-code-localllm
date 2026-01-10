# Local LLM Master Roadmap (Consolidated)

This consolidates:
- Strategy + phases: `docs/local-llm-integration-roadmap.md`
- Operational steps: `docs/local-llm-setup.md`, `docs/operator-runbook.md`
- Current backlog: `docs/todo.md`
- Offload strategy: `docs/offload-playbook.md`

## Current State (Snapshot)
- Upstream sync: `main` tracks `anthropics/claude-code` (`upstream/main`).
- Working branch: `local-llm-integration` (docs + probes + plugin).
- Local tool-call validation (Ollama): VRAM-tier PASS sets recorded in `docs/local-model-validation.md` (2GB/4GB/8GB/12GB).
- vLLM tool-call validation (Docker): PASS `Qwen/Qwen2.5-1.5B-Instruct` with `--enable-auto-tool-choice` + `--tool-call-parser hermes` (see `docs/vllm-setup.md`).
- Operational constraint: avoid running GPU-accelerated Ollama and vLLM simultaneously unless VRAM is explicitly budgeted.

## Completed Milestones (this repo)
- `Makefile` harness for probes and verification targets.
- Tool-call probe suite with strict conformance checks (`tools/local_llm/*probe*.py`).
- Policy engine with optional VRAM-aware escalation inputs (`tools/local_llm/policy_engine.py`).
- NVIDIA VRAM snapshot tool (`tools/local_llm/vram_probe.py`).
- VRAM bench runner (`tools/local_llm/vram_bench.py`) and `make vram-bench`.
- Router-management plugin (`plugins/local-llm-router/`).
- Router config validator (`tools/local_llm/validate_router_config.py`) and `make router-config-validate`.
- vLLM Docker runner (`tools/local_llm/runtimes/vllm_docker.sh`) + docs (`docs/vllm-setup.md`).
- llama.cpp server placeholder (`tools/local_llm/runtimes/llamacpp_server.sh`) + docs (`docs/llamacpp-setup.md`).

## North Star
Local-first for safe/routine work, with deterministic escalation to Claude for:
- Sensitive paths / restricted data
- Tool-call instability
- Long-context requirements
- High VRAM pressure / runtime instability

## Backlog (30 items, ordered by dependency)

### A. Foundations
- [ ] Define canonical “task class” labels (L0–L3) and mapping rules.
- [ ] Expand denylist patterns to include OS/user secrets conventions (`~/.ssh`, `~/.gnupg`, `keychain`, etc.).
- [ ] Add a single JSON schema for routing policy inputs/outputs (decisions are auditable).
- [ ] Add a golden “policy regression” fixture set (paths + expected routes).
- [ ] Add a “no secrets in logs” sanitizer for policy/tooling output.

### B. CUDA + VRAM Awareness
- [x] Implement `tools/local_llm/vram_probe.py` (NVIDIA first; degrade gracefully).
- [ ] Define thresholds: free VRAM %, fragmentation heuristics, and low-vram mode detection.
- [ ] Thread VRAM pressure into routing decisions (e.g., prefer smaller model or escalate).
- [x] Add a benchmark mode that logs VRAM before/after each probe iteration.
- [ ] Document GPU prerequisites and driver/CUDA expectations in `docs/installation-requirements.md`.

### C. Runtime Matrix Expansion
- [x] Decide vLLM deployment mode: Docker (preferred) vs native packages (optional).
- [x] Add a vLLM entry to `tools/local_llm/runtime_matrix.json` (disabled by default).
- [ ] Extend `runtime_probe.py` to validate both `/v1/chat/completions` and streaming (when enabled).
- [x] Add “tool-call conformance” checks beyond presence of `tool_calls` (JSON validity, args schema).
- [ ] Add a small “model capability registry” (context length, tool support, cost, VRAM footprint).

### D. Router/Proxy Integration
- [x] Extend `plugins/local-llm-router` with a `/router-validate` command (schema + required keys).
- [x] Add a `/router-backup` command with timestamped backups.
- [x] Add a `/router-diff` command to show what changed vs last backup.
- [ ] Document hardening: bind host `127.0.0.1` unless API key is configured.
- [x] Add a “safe default” router config example for local-first + Claude escalation.

### E. Local-First Orchestration + Escalation
- [ ] Define escalation triggers (tool failures, schema mismatch, VRAM pressure, long context).
- [ ] Add a “synthesis” pattern: local agent drafts → Claude validates/merges when required.
- [ ] Add a per-task “routing report” (why local vs Claude) to improve auditability.
- [ ] Add a minimal “agent offload” template (what to delegate vs keep on Claude).

### F. Verification + Quality Gates
- [ ] Make `make probe-suite` a required pre-merge check for local-LLM changes.
- [ ] Add `make probe-suite-candidates` as a docs-only “known failing” target (non-blocking).
- [ ] Stabilize latency probe prompts and document variance sources (cold start, batching, VRAM mode).
- [ ] Add a small “failure injection” mode (timeouts, invalid JSON, partial tool output).
- [ ] Record benchmark outputs in a consistent JSON schema (for diffing between runs).

### G. Documentation + Hygiene
- [x] Create `gemini.md` only after validating a supported routing path (router or LiteLLM).
- [ ] Consolidate “what is production vs reference” boundaries in `docs/repo-audit.md`.
- [ ] Document reproducible setup steps end-to-end (Arch/CachyOS) with exact package names.
- [ ] Add a “known limitations” section (unsupported models, licensing constraints, unsupported configs).
- [ ] Run a re-audit after each milestone and update `docs/todo.md` accordingly.
