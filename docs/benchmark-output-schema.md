# Benchmark Output Schemas

These tools emit JSON meant to be diffable across runs. Each output includes a
`schema_version` field.

## `runtime_probe.py` (`schema_version: runtime-probe-v1`)
- File: `tools/local_llm/runtime_probe.py`
- Shape:
  - `results[]`: per-runtime+model tool-call + latency probes
  - `failures[]`: summarized failing entries
- Notes:
  - `avg_tokens_per_sec` may be `null` if the runtime omits `usage.completion_tokens`.

## `vram_bench.py` (`schema_version: vram-bench-v1`)
- File: `tools/local_llm/vram_bench.py`
- Shape:
  - `results[]`: per-model tool+latency with VRAM before/after samples
  - `failures[]`: summarized failing entries

