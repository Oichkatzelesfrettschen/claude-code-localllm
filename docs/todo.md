# TODO (Manual Tracker)

This file replaces the unavailable TODOwrite tool. Items are tracked manually.

## Active
- Install optional `lttng-ust2.12` for PowerShell tracing (sudo prompt pending).
- Keep candidate-only probe suite docs-only for now; revisit for CI after runtime validation.
- Investigate `qwen2.5-coder:7b` tool-call compliance under alternate runtimes.
- Install vLLM runtime and run `runtime_probe` against vLLM endpoints.
- Resolve `python-vllm-cuda` dependency failures (`cuda-tools`, `gcc13-libs`) or switch to `python-vllm-bin`.

## Blockers
- `devcontainer-cli` AUR package lacks upstream PGP signatures.
- `lttng-ust2.12` install blocked by sudo and conflicts with `lttng-ust`.

## Completed
- Added installation requirements doc.
- Added repo audit and routing policy docs.
- Selected claude-code-router for POC.
- Built router policy engine, probe suite, and benchmark harness.
- Validated tool-calling for Mistral (pass) and Phi (fail) in Ollama.
