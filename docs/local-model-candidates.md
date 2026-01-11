# Local Model Candidates and License Notes

All entries here must be validated against upstream sources before use.
Warnings are treated as errors; if a model lacks clear license metadata, do not
route tasks to it.

## Shortlist (Initial)
| Model | License | Notes | Source |
| --- | --- | --- | --- |
| Mistral 7B Instruct v0.2 | Apache-2.0 | Tool-call compliant in Ollama (tested) | HF model card |
| Qwen2.5 7B Instruct | Apache-2.0 | Tool-call compliant in Ollama (tested) | HF model card |
| Phi-3 Mini Instruct | MIT | Ollama reports tools unsupported (HTTP 400) | HF model card |
| Llama 3.1 | Community License | Tool-call compliant in Ollama (tested) | Llama 3 LICENSE |

## Validated by VRAM Tier (this machine)
This section is derived from probe results and is summarized in:
- `docs/model-tier-matrix.md`

### 2GB tier
- Ollama PASS: `qwen2.5:0.5b-instruct`, `qwen2.5:1.5b-instruct`, `llama3.2:1b`
- llama.cpp PASS: `Qwen/Qwen2.5-0.5B-Instruct-GGUF` (`qwen2.5-0.5b-instruct-q4_k_m.gguf`)

### 4GB tier
- Ollama PASS: `llama3.2:3b`, `qwen2.5:3b-instruct`, `qwen2.5:1.5b-instruct`
- Ollama FAIL (tools unsupported by runtime): `gemma2:2b`

### 8GB / 12GB tiers
- Ollama PASS: `qwen2.5:7b-instruct`, `mistral:latest`, `llama3.1:latest`
- Ollama FAIL (schema): `qwen2.5-coder:7b` (omits `tool_calls` under OpenAI-compatible endpoint)

### vLLM (Docker)
- vLLM PASS (`--tool-call-parser hermes`): `Qwen/Qwen2.5-0.5B-Instruct`, `Qwen/Qwen2.5-1.5B-Instruct`
- vLLM FAIL (`hermes`): `Qwen/Qwen2.5-Coder-1.5B-Instruct` (emits JSON in `message.content`, no `tool_calls`)

## License Requirements (Summary)
- **Apache-2.0 / MIT**: Generally permissive for commercial use.
- **Llama 3**: Requires attribution and prohibits using outputs to improve other
  LLMs; additional licensing required above 700M MAU.

## Tool-Calling Support (Validation Required)
Tool-call support depends on the runtime (e.g., Ollama, vLLM). Before routing:
1) Confirm the model supports tool calls in the target runtime.
2) Validate JSON schema fidelity and streaming stability.
3) Verify function/tool-call behavior with a round-trip test.

Note: `qwen2.5-coder:7b` returns JSON in `message.content` via Ollama and does
not emit `tool_calls`; keep it non-tool only unless validated in another runtime.

## Sources
- Mistral 7B Instruct model card: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
- Qwen2.5 7B Instruct model card: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct
- Qwen2.5 (small instruct) model cards:
  - https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct
  - https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct
  - https://huggingface.co/Qwen/Qwen2.5-3B-Instruct
- Qwen2.5 Coder (small) model card:
  - https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct
- Phi-3 Mini model card: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct
- Llama 3 license: https://github.com/meta-llama/llama3/blob/main/LICENSE
- Llama 3.2 (small instruct) model cards:
  - https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
  - https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct
- Llama 3.1 (8B instruct) model card:
  - https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct
- Gemma 2 model card:
  - https://huggingface.co/google/gemma-2-2b-it
- Ollama model library:
  - https://ollama.com/library/qwen2.5
  - https://ollama.com/library/llama3.2
  - https://ollama.com/library/mistral
  - https://ollama.com/library/gemma2
- GGUF model repos:
  - https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF
