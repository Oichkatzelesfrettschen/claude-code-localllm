# CUDA Local Runtime Architecture (Draft)

Goal: make local inference reliable on consumer GPUs (e.g., 12GB VRAM) by
making routing decisions *aware of runtime health and VRAM pressure*.

## Components

1) **Runtime(s)**
- **Ollama (CUDA)**: baseline local runtime with OpenAI-compatible endpoint used by probes.
- **vLLM (CUDA)**: optional secondary runtime for higher throughput / OpenAI compatibility (planned).

2) **Telemetry**
- **VRAM probe**: a lightweight local utility that samples GPU memory pressure (`nvidia-smi`).
- **Runtime probe**: existing `tools/local_llm/runtime_probe.py` for tool-call + latency checks.

3) **Policy**
- **Path safety**: denylist/sensitive paths route to Claude.
- **Context safety**: long-context routes to Claude.
- **Runtime safety**: low free VRAM (or repeated runtime failures) escalates to Claude.

## VRAM-Aware Routing (initial)

Inputs:
- `free_vram_mib`, `total_vram_mib` (from VRAM probe)
- optional `min_free_vram_mib` / `min_free_vram_ratio` thresholds (policy rules)

Decision:
- If free VRAM is below threshold → `claude_first` with reason `low_vram`.
- Otherwise follow existing path/context rules.

## Next Extensions
- Add a model capability registry (expected VRAM footprint per model).
- Prefer smaller local model under pressure rather than immediate escalation.
- Record VRAM deltas during probes to detect fragmentation/caching regressions.

