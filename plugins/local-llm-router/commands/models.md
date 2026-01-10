---
name: models
description: List configured providers and models
author: claude-code-localllm
allowed-tools: Bash(jq:*), Bash(cat:*), Read
---

# /models

1. Read `~/.claude-code-router/config.json`.
2. Use `jq` to list provider names and their models.
3. Summarize the current router map (default/background/think/longContext).

If the config file is missing, report a blocking error.
