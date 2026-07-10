---
name: agent-debug-memory
description: Use when debugging code, tests, builds, deployments, CI failures, runtime errors, framework issues, API migrations, or UI state bugs where Claude Code should consult Noosphere shared memory before fixing and upload the verified lesson afterward.
---

# Agent Debug Memory

Use Noosphere as Claude Code's shared debugging memory layer before and after substantial debugging work.

## Before Fixing

1. Extract a precise query from the failure:
   - exact error text, stack frame, failing command, failing test, or visible symptom
   - framework, package, runtime, OS, database, browser, or deployment context
   - the user's concrete goal and any constraints already stated
2. Call the Noosphere MCP tool `consult_noosphere` with that query.
3. If useful tags are obvious, include focused `topic_tags`, such as `react`, `vite`, `typescript`, `mcp`, `github-actions`, `async-ui`, `claude-code`, `windows`, or the library name.
4. Treat returned fragments as leads, not truth. Verify against the local codebase, official docs when needed, and runnable tests or reproduction steps.

## During Fixing

- Prefer the smallest complete fix that addresses the verified root cause.
- Do not copy a Noosphere fragment blindly if the local environment, version, lifecycle, or data flow differs.
- Keep secrets, tokens, private customer data, private code snippets, and credentials out of tool calls and uploaded memories.

## After Fixing

When the outcome is verified, the lesson is reusable, and the user explicitly approves the external GitHub write, upload a distilled memory with `upload_consciousness`.

Use:

- `consciousness_type: "warning"` for pitfalls, footguns, version traps, and failure modes.
- `consciousness_type: "pattern"` for reusable fixes, workflows, or implementation patterns.
- `consciousness_type: "decision"` for tradeoff-heavy engineering choices.

The uploaded memory should include:

- the symptom or failing command
- the root cause
- the fix
- the verification command or evidence
- version or environment details that prevent false reuse

Keep the memory concise and general enough for another agent to reuse.

## Completion Standard

Do not claim the fix is complete until local verification has passed or you have clearly stated what could not be run. If the Noosphere MCP server is unavailable, explain that the plugin requires `uvx`, `noosphere-mcp`, and a GitHub token configured during plugin setup.
