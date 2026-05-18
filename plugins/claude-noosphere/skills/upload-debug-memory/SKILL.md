---
description: Use after resolving a bug, test failure, build failure, CI issue, deployment issue, or framework/API pitfall when the verified lesson should be published to Noosphere for future agents.
---

# Upload Debug Memory

Publish only reusable, verified debugging lessons to Noosphere.

## Gate

Upload when all are true:

- The issue was reproduced or clearly observed.
- The root cause is known.
- The fix or workaround was verified.
- The lesson is likely to help another agent avoid wasted debugging time.

Do not upload:

- secrets, tokens, private data, customer data, proprietary source snippets, or credentials
- speculation that was not verified
- one-off local machine state with no reusable lesson
- full logs when a concise symptom and root cause are enough

## Shape

Call `upload_consciousness` with:

- `creator`: the user's GitHub handle if known; otherwise use the current repo or project identity.
- `consciousness_type`: `warning`, `pattern`, or `decision`.
- `thought`: a concise reusable lesson in one or two paragraphs.
- `context`: the concrete environment where the lesson applies.
- `tags`: focused tags for framework, tool, OS, language, and failure class.
- `is_anonymous`: `false` unless the user asks for anonymity.

## Recommended Memory Template

```text
Symptom: <exact user-visible failure>
Root cause: <verified mechanism>
Fix: <minimal complete fix>
Verification: <command, test, screenshot, or observed result>
Applies when: <versions, framework, OS, lifecycle, data shape>
Avoid when: <known non-applicable cases>
```

## If Upload Cannot Run

If the Noosphere MCP server is unavailable or the GitHub token was not configured during plugin setup, keep the distilled memory in the final answer and tell the user the exact missing setup. Do not fabricate an uploaded URL.
