# Success Metrics

## Quality
- Tool-call success rate >= 95% for L0/L1 tasks.
- No policy violations (denylist paths never routed local).

## Latency
- Local-first tasks: p95 < 2x baseline local inference time.
- Proxy overhead <= 200 ms p95.

## Cost
- >= 30% reduction in Claude token spend for eligible tasks.
- Local cost per MTok documented and reproducible.

## Measurement
- Use `tools/local_llm/tool_call_probe.py` for compliance.
- Use `make runtime-probe` to compare runtimes and capture latency metrics.
- Use Makefile targets for repeatable checks.
