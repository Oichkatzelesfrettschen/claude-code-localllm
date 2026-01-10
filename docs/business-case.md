# Business Case Template

## Inputs Required
- Monthly Claude input/output tokens by task class.
- Percentage of tasks eligible for local routing.
- Local cost per MTok (GPU cost model).

## How to Use
1) Populate `tools/local_llm/scenarios.json` with real token counts.
2) Run `make cost-model` to compute savings.
3) Record qualitative wins (privacy, latency, retention).

## Example Output
See `tools/local_llm/cost_model.py` CSV output for baseline vs hybrid savings.
