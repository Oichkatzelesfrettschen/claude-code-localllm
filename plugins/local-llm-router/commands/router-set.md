---
name: router-set
description: Update a routing slot in the router config (with confirmation)
author: claude-code-localllm
allowed-tools: Read, Edit, Bash(jq:*), Bash(cp:*), Bash(mv:*), Bash(ccr:*)
---

# /router-set

1. Ask the user to confirm the change (slot + provider,model).
2. Read `~/.claude-code-router/config.json`.
3. Create a backup: `cp ~/.claude-code-router/config.json ~/.claude-code-router/config.json.bak`.
4. Use `jq` to update the router slot and write a temp file, then move it into place.
5. Run `ccr restart` to reload the router.
6. Show the updated routing map.

If any step fails, restore from the backup and report a blocking error.
