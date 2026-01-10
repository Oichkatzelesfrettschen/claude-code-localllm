---
name: router-backup
description: Create a timestamped backup of the router config
author: claude-code-localllm
allowed-tools: Read, Bash(cp:*), Bash(date:*), Bash(ls:*)
---

# /router-backup

1. Ensure `~/.claude-code-router/config.json` exists; if not, report a blocking error.
2. Create a timestamped backup alongside it:
   - `cp ~/.claude-code-router/config.json ~/.claude-code-router/config.json.$(date -Iseconds).bak`
3. List backups (most recent first) and report the created filename.

