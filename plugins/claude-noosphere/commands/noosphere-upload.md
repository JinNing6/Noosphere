---
description: Submit a verified debugging lesson as Shared Skill evidence
argument-hint: [short summary of the solved bug or lesson]
---

Distill the resolved issue into reusable Shared Skill evidence. Ask for explicit consent
to create the public GitHub record, then call `submit_skill_evidence`.

Use this input as the focus:

```text
$ARGUMENTS
```

Only submit if the issue was observed, the root cause is known, the fix was verified,
and the user authorizes this specific public write. Never include secrets, credentials,
private source code, customer data, or full logs when a concise symptom and root cause
are enough.

Include a lowercase kebab-case Skill name, symptom, root cause, fix, verification,
applicability boundaries, real test commands, optional external public source URLs, and
focused tags. Use the community publication track unless an authenticated repository
maintainer explicitly chooses the maintainer track.

Report the returned evidence URL and lifecycle state exactly. Do not describe an
evidence record as a published or callable Skill. Never route engineering evidence
through `upload_consciousness`.
