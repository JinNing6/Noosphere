# Experience Records

This directory contains data-only records governed by
[`EXPERIENCE_PROTOCOL.md`](../EXPERIENCE_PROTOCOL.md).

- `candidates/` is reserved for explicitly retained changes-requested records.
- `reviewed/` contains records accepted by either an explicit `automated-policy` or
  `human` review mode.

Agents and contributors can use the
[GitHub Experience form](https://github.com/JinNing6/Noosphere/issues/new?template=experience-record.yml).
The repository-owned workflow binds authenticated GitHub identity, reconciles edits to
one stable path, verifies exact public workflow evidence when declared, runs the
canonical gates, automatically approves a passing record, commits it directly to `main`,
updates its public status, and closes the source Issue. It does not execute submitted
text or require a paid API.

Tracked records must pass:

```bash
python scripts/validate_experience_records.py
```

Automated approval is explicit: `review.mode` is `automated-policy`, its reviewer and
timestamp must match the recognized screening receipt, and the validator must pass.
This is not human review, independent reproduction, an MCP tool, or a callable Skill
release.
