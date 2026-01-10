# Claims, Hypotheses, and Validation Notes

This file tracks factual claims made in the local-LLM docs, the corresponding
testable hypotheses, and the primary sources used to validate them.

Warnings are treated as errors: if a claim cannot be validated, mark it
unverified and avoid relying on it for decisions.

## Validated

| Claim | Testable hypothesis | Primary source | Status |
| --- | --- | --- | --- |
| Anthropic Commercial Terms restrict reverse engineering/competing uses | The Commercial Terms include a clause prohibiting reverse engineering, duplicating, or accessing the services to build a competing product | https://www.anthropic.com/legal/commercial-terms (Section D.4 “Use Restrictions”) | Verified |
| Claude API pricing example in roadmap matches published pricing | Sonnet 4.5 pricing is $3/MTok input and $15/MTok output for prompts ≤200K tokens | https://www.anthropic.com/pricing | Verified |
| `claude-code-router` exports env vars used for routing | `ccr activate` outputs `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` (and related env vars) | https://github.com/musistudio/claude-code-router | Verified |
| `claude-code-router` supports env-var interpolation in config | Router README documents `$VAR` / `${VAR}` interpolation in `~/.claude-code-router/config.json` | https://github.com/musistudio/claude-code-router | Verified |
| `claude-code-router` supports OpenRouter transformer | Router README includes an `openrouter` provider example using `transformer.use: [\"openrouter\"]` | https://github.com/musistudio/claude-code-router | Verified |
| LiteLLM provides an OpenAI-format proxy | LiteLLM docs/README describe an OpenAI-compatible proxy server (`/chat/completions`) | https://github.com/BerriAI/litellm | Verified |
| Mistral 7B Instruct v0.2 license is Apache-2.0 | HF metadata returns `license: apache-2.0` for `mistralai/Mistral-7B-Instruct-v0.2` | https://huggingface.co/api/models/mistralai/Mistral-7B-Instruct-v0.2 | Verified |
| Qwen2.5 7B Instruct license is Apache-2.0 | HF metadata returns `license: apache-2.0` for `Qwen/Qwen2.5-7B-Instruct` | https://huggingface.co/api/models/Qwen/Qwen2.5-7B-Instruct | Verified |
| Phi-3 Mini 4k Instruct license is MIT | HF metadata returns `license: mit` for `microsoft/Phi-3-mini-4k-instruct` | https://huggingface.co/api/models/microsoft/Phi-3-mini-4k-instruct | Verified |
| Llama 3 license forbids using outputs to improve other LLMs | The license includes a clause restricting use of outputs/results to improve other large language models | https://raw.githubusercontent.com/meta-llama/llama3/main/LICENSE (Section 1.b.v) | Verified |
| Llama 3 has a 700M MAU licensing trigger | The license includes additional commercial terms for entities over 700M MAU | https://raw.githubusercontent.com/meta-llama/llama3/main/LICENSE (Section 2) | Verified |

## Unverified (do not rely on these)

| Claim | Hypothesis | Status |
| --- | --- | --- |
| Specific DMCA takedown details | A primary source (court filing, takedown notice, or official statement) exists | Unverified |
| API access revocation anecdotes | A primary source exists (provider policy or public incident report) | Unverified |
