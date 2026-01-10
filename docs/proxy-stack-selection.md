# Proxy Stack Selection

## Decision Criteria
- Claude Code compatibility (Anthropic Messages API).
- Tool-call fidelity and streaming stability.
- Configuration UX (routing, presets, policy hooks).
- Operational footprint and ease of rollback.

## Candidates
### claude-code-router
Pros:
- Purpose-built for Claude Code routing.
- Supports multiple providers and routing profiles.
- Includes UI and CLI model management.
Cons:
- External project; not an Anthropic-supported component.

### LiteLLM Proxy
Pros:
- Broad provider coverage; strong docs.
- Can proxy Anthropic and OpenAI formats.
Cons:
- Additional config required to mimic Claude Code behavior.

## Selection (Phase 1)
Use **claude-code-router** for the proof of concept because it is tailored to
Claude Code workflows and already exposes routing profiles. Keep LiteLLM as a
fallback for environments that require a general-purpose gateway.

## Sources
- claude-code-router README: https://github.com/musistudio/claude-code-router
- LiteLLM README: https://github.com/BerriAI/litellm
