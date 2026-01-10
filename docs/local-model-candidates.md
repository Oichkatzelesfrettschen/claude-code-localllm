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
- Phi-3 Mini model card: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct
- Llama 3 license: https://github.com/meta-llama/llama3/blob/main/LICENSE
