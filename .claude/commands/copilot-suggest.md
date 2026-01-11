---
allowed-tools: Bash(gh auth status:*), Bash(gh copilot suggest:*), Bash(gh copilot explain:*)
description: Use GitHub Copilot CLI to suggest/explain commands
---

## Context

- Verify auth: !`gh auth status`

## Your task

Use `gh copilot` to help with the user’s request:

- For “how do I do X in the shell?”: run `gh copilot suggest` with an appropriate `--target` (shell, git, gh, etc.).
- For “what does this command/output mean?”: run `gh copilot explain`.

Return the suggested command(s) and any safety notes.

