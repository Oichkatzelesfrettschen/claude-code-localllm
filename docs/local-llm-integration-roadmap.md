# Local LLM Integration: Feasibility, Architecture, and Roadmap

## Status and Scope
This document turns the draft into a verified, actionable plan for adding local
LLM routing and delegation alongside Claude Code. It focuses on technically
feasible integration patterns, the legal/terms constraints that govern them, and
an execution roadmap that can be delivered as a plugin or proxy without
modifying proprietary core code.

## Audience, Success Metrics, and Timeline
**Audience:** Claude Code users (including local power users) with an end goal
of upstream readiness once a robust external proof of concept is validated.

**Success metrics (treat warnings as errors):**
- >= 95% tool-call success rate on selected task classes.
- No routing of restricted paths or secrets to local models.
- Measurable Claude token reduction with no quality regression.
- Reproducible installation and test steps on supported platforms.

**Timeline:** Phased delivery with gates; upstream proposal only after stable
pilot results and documented risk/terms review.

## Verified Constraints and Facts (Cited)
- Claude Code is proprietary. The repository license is "All rights reserved"
  and use is governed by Anthropic Commercial Terms. See `LICENSE.md` and the
  Terms section D.4 for use restrictions and reverse engineering limits.
- Claude Code includes proxy-related environment variables in release notes
  (for example `NO_PROXY` and `CLAUDE_CODE_PROXY_RESOLVES_HOSTS`). See
  `CHANGELOG.md`.
- Community routers exist. `claude-code-router` documents routing Claude Code
  to multiple providers and uses environment variables such as
  `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` when activating the router.
- LiteLLM provides an OpenAI-format proxy for multiple providers.
- Local model licenses vary. Examples:
  - Mistral 7B Instruct: Apache-2.0.
  - Qwen2.5 7B Instruct: Apache-2.0.
  - Phi-3 Mini Instruct: MIT.
  - Llama 3: Community license with restrictions (including limits on using
    outputs to improve other LLMs and a 700M MAU licensing trigger).

## Vision: Hybrid Routing, Not Forking
The goal is to keep users inside the Anthropic ecosystem while offloading
routine or sensitive tasks to local models. The integration should:
- Preserve Claude Code workflows and tool calls.
- Route safe, repetitive, or privacy-sensitive tasks to local models.
- Escalate complex reasoning or long-context work to Claude as needed.
- Be deployable without modifying proprietary core code.

## Architecture Overview (Proxy + Router)

```
User -> Claude Code (unchanged)
          |
          v
   Router/Policy Layer (local)
      |         |
      v         v
  Local LLM   Claude API
      |         |
      +-----> Synthesis
```

Core components:
1) **Router/Policy Engine**
   - Selects model based on task type, sensitivity, context length, and budget.
   - Exposes a `/models` registry for available local and remote models.
2) **Adapter Layer**
   - Translates Claude Messages API calls to OpenAI-style calls (and back) for
     local models.
   - Normalizes tool calling into a shared internal schema.
3) **Telemetry and Controls**
   - Routing logs, audit trails, and policy enforcement (PII guardrails).

## Delegation Patterns
### Pattern A: Claude Orchestrates Local Agents
- Claude handles planning and synthesis.
- Local LLMs handle predictable subtasks: lint summaries, doc updates, test
  generation, changelog drafts.
- Use when tasks depend on Claude-level reasoning but can offload execution.

### Pattern B: Local First With Escalation
- Local model does first pass.
- Escalate to Claude when triggers fire (low confidence, long context, tool
  errors, security-sensitive tasks).
- Use when minimizing API usage is primary.

## Task Classes and Sensitivity Tiers
| Tier | Examples | Default Route |
| --- | --- | --- |
| L0 (Safe) | Lint summaries, doc edits, changelog drafts | Local |
| L1 (Routine) | Simple refactors, formatting, test scaffolds | Local-first |
| L2 (Sensitive) | Cross-file changes, security-adjacent code | Claude-first |
| L3 (Restricted) | Secrets, auth flows, compliance or legal content | Claude-only |

## Escalation and Routing Triggers
- Tool-call failure or malformed tool output.
- Low confidence, high ambiguity, or long-context requirements.
- Sensitive files (credentials, auth, infra, proprietary algorithms).
- Repeated retries, latency spikes, or policy violations.

## Capability Requirements for Local Models
- Tool calling support (required for file edits, shell commands, MCP).
- Stable streaming responses for tool-use loops.
- Strong system prompt adherence to avoid tool misuse.
- Context length that matches expected task sizes (long-context routes should
  default to Claude unless validated).

## Implementation Options Matrix
| Option | Description | Pros | Cons | Best Fit |
| --- | --- | --- | --- | --- |
| Proxy only | Run a router/proxy that emulates Anthropic API | No core changes; fast | Unsupported; extra hop | Short-term |
| Plugin + proxy | Add a plugin that manages routing rules + proxy config | Better UX; can add `/models` UI | Still external | Medium-term |
| Upstream core change | Provider abstraction in Claude Code | Best UX | Low likelihood; strategic risk | Long-term/low chance |

## Compliance and Risk Notes
- The license and Terms restrict reverse engineering and competing uses.
  Integration should remain at the API/proxy layer and avoid modifications to
  proprietary binaries. (See `LICENSE.md` and Anthropic Commercial Terms D.4.)
- Using third-party models may trigger additional licensing or attribution
  obligations (for example Llama 3 attribution requirements).
- Treat any proxy solution as "unsupported" unless Anthropic explicitly
  documents the configuration.

## Roadmap (Phased With Decision Gates)
### Phase 0: Discovery and Policy (1-2 weeks)
- Inventory current Claude Code usage by task class.
- Define a routing policy (what stays on Claude vs local).
- Legal review of Anthropic Terms + target model licenses.
**Gate:** Legal/Policy approval + task taxonomy.

### Phase 1: Proof of Concept (2-4 weeks)
- Stand up `claude-code-router` or LiteLLM proxy locally.
- Validate tool calling and streaming with 2-3 local models.
- Implement a simple routing config (background tasks local).
**Gate:** >= 80% success rate on chosen tasks.

### Phase 2: Reliability and Safety (3-6 weeks)
- Add structured logging, tracing, and failure fallbacks.
- Build a "safe task list" and an escalation policy.
- Establish SLAs for latency and error rates.
**Gate:** Failure and rollback behavior validated.

### Phase 3: UX and /models Registry (4-6 weeks)
- Create a plugin that:
  - surfaces local models in a `/models` registry view,
  - edits router configs safely,
  - sets environment variables (with explicit opt-in).
- Add documentation and a "safe default" config.
**Gate:** User testing + docs complete.

### Phase 4: Optimization and Scale (ongoing)
- Add cost controls, caching, and local batch routing.
- Expand model catalog with license tracking metadata.
- Evaluate upstream proposal only if business case is strong.

## Testing and Validation Plan
- **Translation Tests:** Anthropic Messages API <-> OpenAI format round-trip.
- **Tool Call E2E:** Verify tool calls pass through proxy without schema loss.
- **Failure Injection:** Timeouts, malformed tool responses, streaming errors.
- **Regression Suite:** Compare outputs for identical tasks across routes.
- **Security Review:** Confirm local routing does not bypass permission rules.

## Business Case Framework (With Real Pricing)
Use current Anthropic pricing and your internal cost model for local inference:
- Claude pricing reference: `https://www.anthropic.com/pricing`
  (example: Sonnet 4.5 input $3/MTok, output $15/MTok).
- Local model cost per MTok:
  `cost = (GPU_hourly_cost / tokens_per_hour) * 1,000,000`
  + energy + ops overhead.

Example decision model:
1) **Baseline**: Current monthly Claude token usage and cost.
2) **Shift %**: % of tasks moved to local models (by task class).
3) **Delta**: Cost saved on Claude tokens minus local infra costs.
4) **Qualitative**: Faster feedback loops, privacy wins, lower server load.

Business outcomes to track:
- Cost per resolved task.
- Developer throughput (tasks/hour).
- Reduction in Claude token usage without quality loss.
- Adoption and retention (developers keep Claude as default).

## Open Questions and Decision Gates
- What task classes are safe to route locally without quality regression?
- Which models are licensed for the target deployment scenario?
- What escalation thresholds (confidence, latency, failures) are acceptable?
- Is there a legal green light for proxy routing in the intended use case?

## Sources
- `LICENSE.md`
- `CHANGELOG.md`
- Anthropic Commercial Terms (D.4): https://www.anthropic.com/legal/commercial-terms
- Anthropic Pricing: https://www.anthropic.com/pricing
- Claude Code Router README: https://github.com/musistudio/claude-code-router
- LiteLLM README: https://github.com/BerriAI/litellm
- Mistral 7B Instruct model card (license metadata): https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
- Qwen2.5 7B Instruct model card (license metadata): https://huggingface.co/Qwen/Qwen2.5-7B-Instruct
- Phi-3 Mini model card (license metadata): https://huggingface.co/microsoft/Phi-3-mini-4k-instruct
- Llama 3 license: https://github.com/meta-llama/llama3/blob/main/LICENSE
