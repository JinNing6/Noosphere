# Noosphere Project Memory Snapshot

Last verified: 2026-07-10 (Asia/Shanghai)

## Current Engineering State

- The dynamic shared Skills implementation is split into three reviewable local commits on branch `codex/dynamic-shared-skills-v1` in a dedicated worktree.
- The implementation has not been pushed, merged into remote `main`, or released to PyPI at the time of this snapshot.
- SDK metadata is prepared as `noosphere-mcp` version `0.7.0` with 45 MCP tools.
- `shared_skills/registry.json` is intentionally empty until a candidate satisfies the evidence and independent-publisher gates and receives maintainer approval.

## Dynamic Shared Skill Lifecycle

1. `upload_consciousness` accepts structured engineering evidence: symptom, root cause, fix, verification, applicability, exclusions, test commands, and source URLs.
2. Promotion binds publisher identity to the actual GitHub Issue author. Self-declared `creator_signature` is display metadata and grants no withdrawal or publication authority.
3. One source Issue maps to `consciousness_payloads/memory_issueNNNN.json`. Repeated Issue events reconcile the existing record with GitHub blob SHA instead of creating a new file.
4. Moderation failures are fail-closed for Skill candidacy. Unverified historical promotions must pass current moderation or trusted maintainer review before trust can be upgraded.
5. Candidate clustering requires structured verified memories, a shared embedding space, all-pairs similarity of at least 0.9, two source Issues, and two independent GitHub publishers.
6. CI opens a deterministic `skill-candidate` Issue. Publication requires a write-permission maintainer applying `skill-approved`.
7. Published artifacts are immutable Agent Skills releases under `shared_skills/releases/<version>/<name>/SKILL.md`, with active mirrors and registry SHA-256 plus byte-size metadata.
8. Agents use `list_shared_skills`, `get_shared_skill`, and `check_skill_updates` for pull-based near-real-time discovery. Exact artifact bytes are verified before Skill content is returned.
9. Authenticated feedback uses `record_skill_outcome`. `request_shared_skill_withdrawal` only opens a request; a trusted maintainer must approve withdrawal. Withdrawal preserves the immutable artifact and rolls `latest` back atomically.

## Trust And Safety Boundaries

- Ordinary community memories are returned with an explicit untrusted-data warning.
- Candidate text is rejected for instruction-override, destructive command, encoded shell, private-key, and secret-like patterns; the candidate digest must match the reviewed body.
- Publish and withdrawal workflows serialize through one concurrency group and commit release, active mirror, and registry changes atomically.
- Permanent-memory promotion and withdrawal share one serialized workflow group, and both persistent-state groups use full queues so rapid events are not silently replaced while pending.
- Plugin instructions require local applicability checks, local verification, and explicit user approval before public GitHub writes or destructive operations.
- Permanent-memory withdrawal uses an author-bound request plus `consciousness_tombstones.json`; the SDK and public index both exclude tombstoned records and fail closed when an existing tombstone manifest cannot be read safely.

## Permanent Data State

- Historical migration was applied locally and is idempotent on re-check.
- Physical permanent payload files: 41.
- Public indexed memories: 38, unchanged after migration.
- Source-Issue-backed canonical records: 16.
- Legacy records without source Issue metadata left untouched: 25.
- Duplicate promotion files removed: 20.
- Active tombstoned Issue records at snapshot time: 0.

## Verification Evidence

- `python -m pytest sdk/tests -q`: 185 passed.
- `node --test .github/scripts/*.test.cjs`: 71 passed.
- Repository script unit tests: 27 passed.
- Shared Skill registry validator: passed.
- Permanent promotion canonicalization check: passed with no pending writes or deletes.
- Critical Ruff gate and focused shared-Skill Ruff/format checks: passed.
- Seven changed GitHub Actions workflows and six JSON manifests parsed successfully.
- Package build produced `noosphere_mcp-0.7.0.tar.gz` and `noosphere_mcp-0.7.0-py3-none-any.whl` successfully.
- Reusable supply-chain review method was captured and validated as global Skill `dynamic-shared-skill-supply-chain`.

## Required Deployment Steps

1. Review and merge or push `codex/dynamic-shared-skills-v1` to remote `main`.
2. Run `.github/workflows/init_labels.yml` once so all candidate, review, outcome, and withdrawal labels exist.
3. Publish tag or GitHub Release `v0.7.0`; Trusted Publishing will run all SDK, workflow, migration, and registry gates before PyPI publication.
4. Collect at least two independently authored, structured memories for one repeated failure pattern; review the generated candidate and apply `skill-approved` only after evidence inspection.
5. Do not describe the registry as having live published Skills until the first approved release appears in `shared_skills/registry.json` on remote `main`.
