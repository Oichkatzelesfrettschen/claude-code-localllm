---
name: router-diff
description: Diff current router config against the most recent backup
author: claude-code-localllm
allowed-tools: Read, Bash(ls:*), Bash(diff:*), Bash(head:*), Bash(sort:*), Bash(tail:*), Bash(printf:*)
---

# /router-diff

1. Locate the most recent backup matching `~/.claude-code-router/config.json.*.bak`.
2. If no backups exist, report a blocking error and suggest running `/router-backup` first.
3. Run a unified diff against the current config:
   - `diff -u <latest-backup> ~/.claude-code-router/config.json`
4. Summarize what changed in `Providers` and `Router`.

