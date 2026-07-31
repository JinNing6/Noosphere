# Experience Records

This directory contains data-only records governed by
[`EXPERIENCE_PROTOCOL.md`](../EXPERIENCE_PROTOCOL.md).

- `candidates/` contains redacted records awaiting human review.
- `reviewed/` is reserved for records that pass the protocol checklist.

Tracked records must pass:

```bash
python scripts/validate_experience_records.py
```

Moving a file is not sufficient to approve it. Its lifecycle and review fields must be
updated by an identified reviewer, and the validator must pass. Experience Records are
not MCP tools and are never callable Skill releases.
