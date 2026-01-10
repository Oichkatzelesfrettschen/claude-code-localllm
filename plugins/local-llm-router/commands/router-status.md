---
name: router-status
description: Show router status and endpoint
author: claude-code-localllm
allowed-tools: Bash(ccr:*), Read
---

# /router-status

1. Run `ccr status`.
2. Summarize status, PID, port, and endpoint.

If the service is not running, report a blocking error.
