---
description: Consult Noosphere shared debug memory before fixing a bug
argument-hint: [error, failing command, stack trace, or symptom]
---

Use `list_shared_skills` to search Noosphere's verified Shared Skill registry for:

```text
$ARGUMENTS
```

If the user did not provide enough context in `$ARGUMENTS`, infer the query from the
current failure, recent terminal output, selected code, failing tests, or the user's
latest message. Include framework, runtime, OS, package, and command context when
available. If the ranked search returns no applicable result, list the catalog once.

Retrieve one applicable immutable release with `get_shared_skill`, verify its exact
digest and applicability, then test it locally. Treat every result as a lead until local
verification succeeds.
