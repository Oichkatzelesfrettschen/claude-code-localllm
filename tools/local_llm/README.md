# Local LLM Tools

## cost_model.py
Compute Claude vs local cost scenarios from `scenarios.json`:
```
python3 tools/local_llm/cost_model.py --config tools/local_llm/scenarios.json
```

## tool_call_probe.py
Validate tool-call compliance for a local model endpoint:
```
python3 tools/local_llm/tool_call_probe.py \
  --url http://127.0.0.1:11434/v1/chat/completions \
  --model qwen2.5-coder:7b
```

## policy_engine.py
Evaluate routing policy for file paths:
```
python3 tools/local_llm/policy_engine.py \
  --rules tools/local_llm/policy_rules.json \
  --paths README.md
```

## probe_suite.py
Run tool-call probes across a model list:
```
python3 tools/local_llm/probe_suite.py \
  --url http://127.0.0.1:11434/v1/chat/completions \
  --config tools/local_llm/probe_models.json
```

Candidate models (expected to fail until validated):
```
python3 tools/local_llm/probe_suite.py \
  --url http://127.0.0.1:11434/v1/chat/completions \
  --config tools/local_llm/probe_models_candidates.json
```

## latency_probe.py
Measure latency and tokens/sec:
```
python3 tools/local_llm/latency_probe.py \
  --url http://127.0.0.1:11434/v1/chat/completions \
  --model llama3.1:latest
```

## runtime_probe.py
Run tool-call + latency probes across runtimes:
```
python3 tools/local_llm/runtime_probe.py \
  --config tools/local_llm/runtime_matrix.json \
  --output /tmp/runtime_probe.json
```
