# Benchmarks and Probes

## Cost Model
Run the cost model against the sample scenarios:
```
make cost-model
```

## Supply Chain Verification
Verify devcontainer CLI tarball integrity:
```
make verify-devcontainer
```

## Tool-Call Probe
Probe tool-call compliance (requires `ollama serve`):
```
make tool-probe
```

## Policy Check
Run the routing policy engine with sample paths:
```
make policy-check
```

## Probe Suite
Run tool-call probes across multiple models:
```
make probe-suite
```

Candidate-only probes (docs/manual, not CI yet):
```
make probe-suite-candidates
```

## Runtime Probe
Run tool-call and latency probes across configured runtimes:
```
make runtime-probe
```
Capture JSON output for comparison:
```
python3 tools/local_llm/runtime_probe.py \
  --config tools/local_llm/runtime_matrix.json \
  --output /tmp/runtime_probe.json
```

## Latency Probe
Measure average latency and tokens/sec:
```
make latency-probe
```
