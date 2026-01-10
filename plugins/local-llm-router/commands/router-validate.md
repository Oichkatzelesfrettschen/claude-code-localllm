---
name: router-validate
description: Validate router config for consistency and safety
author: claude-code-localllm
allowed-tools: Read, Bash(python3:*), Bash(ccr:*), Bash(cat:*), Bash(ls:*), Bash(env:*), Bash(printenv:*)
---

# /router-validate

1. Confirm the router config path with the user (default `~/.claude-code-router/config.json`).
2. Validate the config file using the repo validator:
   - `python3 tools/local_llm/validate_router_config.py --path ~/.claude-code-router/config.json --require-env`
3. If validation fails, summarize the blocking errors and do not proceed with router changes.
4. If validation passes, optionally run `ccr restart` and re-check `ccr status`.

