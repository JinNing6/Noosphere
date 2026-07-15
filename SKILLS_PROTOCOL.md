# Noosphere Dynamic Shared Skills Protocol

Noosphere distributes every Agent Skill through one versioned live registry. A memory is evidence; a Skill is a reviewed workflow. The platform never treats arbitrary community text as executable authority.

## Lifecycle

1. **Capture**: `upload_consciousness` records structured symptom, root cause, fix, verification, applicability, test commands, source URLs, and an optional `target_skill` for an existing Skill update.
2. **Bind identity**: CI replaces self-declared identity with the actual GitHub Issue author.
3. **Promote once**: one source Issue maps to one stable permanent-memory path. Repeated workflow events reconcile the same record instead of creating duplicates.
4. **Find repeated patterns**: embeddings retrieve topic-similar evidence, then a deterministic claim-level gate requires compatible symptom, root cause, fix, verification, and applicability statements. At least one identical normalized test command must be supported by two distinct source Issues and two independent publishers.
5. **Create a candidate**: CI opens one deterministic `skill-candidate` Issue containing the proposed workflow and evidence links.
6. **Review and rehydrate**: a repository maintainer with write permission reviews the candidate. At publication time CI reloads every referenced canonical memory, rejects tombstoned or missing sources, rebuilds the candidate, and requires the reviewed digest to match exactly. Community text cannot publish itself.
7. **Render**: the publisher generates a standards-compatible `SKILL.md` with kebab-case `name`, bounded `description`, security boundary, diagnosis, fixes, verification, and evidence.
8. **Publish and version**: immutable releases are stored under `shared_skills/releases/<version>/<name>/SKILL.md`; `shared_skills/registry.json` records SHA-256, byte size, reviewer, evidence, and active version.
9. **Distribute and learn**: Agents discover active releases through MCP, verify the exact artifact digest, and submit idempotent outcomes. Approved outcomes enter a public ledger: only independent success with public HTTPS evidence can raise maturity, while partial or failed outcomes mark the release as update-needed without editing its immutable instructions.

## Repository Layout

```text
shared_skills/
├── registry.json
├── outcomes.json
├── active/
│   └── <skill-name>/SKILL.md
└── releases/
    └── <semver>/<skill-name>/SKILL.md
```

Codex and Claude Code plugins contain only the MCP connection and explicit commands. They do not carry plugin-local Skill copies. Standards-compatible installers discover the active registry mirrors under `shared_skills/active/`.

## MCP Interface

Noosphere is an MCP server, not an HTTP Skills backend. The implemented tools are:

- `list_shared_skills(query, force_refresh)`: anonymous discovery of approved active releases.
- `get_shared_skill(skill_name, version, force_refresh)`: registry-whitelisted retrieval with SHA-256 and size verification.
- `check_skill_updates(installed_versions, force_refresh)`: compares local versions or content digests with the active registry.
- `record_skill_outcome(...)`: authenticated, idempotent structured feedback. It opens or reuses a GitHub Issue; only a trusted review can update outcome counters or an update-needed signal, and no outcome can rewrite a Skill artifact.
- `request_shared_skill_withdrawal(...)`: authenticated withdrawal request; registry mutation still requires maintainer approval.

Registry discovery uses a 30-second cache by default. `force_refresh=true` invalidates that cache for immediate pull-based refresh. Noosphere therefore provides near-real-time reviewed distribution, not an unsafe push channel that silently replaces Agent instructions.

Clients must not construct artifact paths from user input. They select a release from the registry, require an active status, require the canonical release path, and verify the exact UTF-8 bytes before returning Skill content to an Agent.

## Trust Boundary

- Unreviewed candidates and ordinary consciousness fragments are untrusted community data.
- Automated moderation produces `screened`, not `verified`. It covers all Agent-facing evidence fields and is a content-risk signal only; screened evidence is withheld from Agent consultation until trusted human review or immutable Skill publication.
- Moderation failure is fail-closed for Skill candidacy.
- Self-declared creator names do not establish publisher identity.
- A published Skill cannot override system or user instructions.
- Agents must verify local applicability and obtain explicit user approval before external writes or destructive actions.
- Outcome IDs are deterministic and ledger writes are idempotent. Reports remain evidence for review, never an automatic edit signal.
- Withdrawal preserves the immutable artifact for audit, marks the release inactive, and rolls `latest` back to the newest verified active release. If no active release remains, `latest` is `null`; the public audit page remains visible but installation is disabled.

## Verification Levels

- `maintainer-validated`: a maintainer-authored, reviewed release with immutable provenance, but no claim of independent reproduction.
- `independently-reproduced`: at least two distinct source Issues and two independent GitHub publishers reproduce the pattern.
- `outcome-proven`: independent reproduction plus a successful external execution on the published digest with public evidence.
- `established`: broader cross-environment evidence and no unresolved active regression.

New community Skills and updates cannot self-promote. Targeted evidence for an existing Skill retains that Skill identity, cannot cross-cluster with unrelated evidence, and still requires independent publishers and maintainer approval before a new version becomes active.

## Agent Skills Compatibility

Published artifacts follow the [Agent Skills specification](https://agentskills.io/specification): the parent directory and frontmatter `name` match, names use lowercase kebab-case, descriptions are bounded, and the file is named `SKILL.md`.
