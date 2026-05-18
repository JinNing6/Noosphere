---
description: Consult Noosphere shared debug memory before fixing a bug
argument-hint: [error, failing command, stack trace, or symptom]
---

Use the Noosphere MCP tool `consult_noosphere` to search shared agent debugging memory for:

```text
$ARGUMENTS
```

If the user did not provide enough context in `$ARGUMENTS`, infer the query from the current failure, recent terminal output, selected code, failing tests, or the user's latest message. Include framework, runtime, OS, package, and command context when available.

Treat returned memories as leads. Verify any proposed fix against this repository and the relevant official docs before changing code.
