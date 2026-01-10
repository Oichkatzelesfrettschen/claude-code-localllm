# TODO (Manual Tracker)

This file replaces the unavailable TODOwrite tool. Items are tracked manually.

## Active
- Implement VRAM-aware routing inputs (GPU memory pressure -> route/escalate).
- Add vLLM runtime and run `runtime_probe` against vLLM endpoints (OpenAI-compatible).
- Keep candidate-only probe suite docs-only for now; revisit for CI after runtime validation.
- Investigate `qwen2.5-coder:7b` tool-call compliance under alternate runtimes.
- Decide vLLM packaging path (`python-vllm-bin` vs `python-vllm` vs containerized vLLM).
- Create `gemini.md` after validating the proxy/routing story with primary sources (LiteLLM / router docs).

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
