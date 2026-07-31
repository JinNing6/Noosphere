# Experience Records

This directory contains data-only records governed by
[`EXPERIENCE_PROTOCOL.md`](../EXPERIENCE_PROTOCOL.md).

- `candidates/` contains redacted, machine-screened records awaiting human review.
- `reviewed/` is reserved for records that pass the protocol checklist.

Agents and contributors can use the
[GitHub Experience form](https://github.com/JinNing6/Noosphere/issues/new?template=experience-record.yml).
The repository-owned workflow binds authenticated GitHub identity, reconciles edits to
one stable path, verifies exact public workflow evidence when declared, runs the
canonical gates, and commits a passing candidate directly to `main`. It does not execute
submitted text or require a paid API.

Tracked records must pass:

```bash
python scripts/validate_experience_records.py
```

Machine screening and recording are not approval. Moving a file is not sufficient to
approve it: lifecycle and review fields must be updated by an identified human reviewer,
and the validator must pass. Experience Records are not MCP tools and are never callable
Skill releases.
