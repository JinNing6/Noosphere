# GitHub Evidence and Experience Agents

The GitHub Evidence Agent is the zero-service intake path for Shared Skill evidence. A contributor submits one GitHub Issue Form; repository-owned GitHub Actions parses it, checks deterministic safety rules, validates public GitHub provenance, and records an eligible evidence item without a paid model or a maintainer-applied intake label.

The companion GitHub Experience Agent accepts a complete Experience Protocol v0.1 JSON
record. It binds the authenticated Issue author, checks privacy and policy invariants,
verifies exact public GitHub workflow evidence when declared, and commits a passing
machine-screened candidate directly to one stable `experience_records/candidates/`
path. It never turns screening into human approval or Experience into a callable Skill.

## What the Agent accepts

The form requires:

- a reproducible symptom, root cause, reusable fix, applicability boundary, verification explanation, and exact test command;
- a public GitHub repository and full 40-character commit SHA;
- a successful GitHub Actions run from that same repository and commit;
- the exact successful job and step names;
- public evidence URLs, plus an optional artifact SHA-256.

The verifier resolves the public repository and commit through the GitHub API, then requires the named workflow run, job, and step to have completed successfully at that exact commit. This establishes `workflow-verified` provenance. It does not prove that the submitted prose is semantically correct or that another person independently reproduced the result.

## Lifecycle states

1. **Accepted draft**: opening the Issue succeeds. Missing or invalid evidence is labeled `skill-evidence-incomplete`; the Issue remains editable and an edit automatically reruns validation.
2. **Workflow verified**: the source commit and named successful job/step match. The record is deterministically screened and stored under `skill_evidence_payloads/`.
3. **Candidate**: community evidence still needs a matching test command from a second GitHub publisher. Maintainer-track evidence follows its separately reviewed path.
4. **Published**: a maintainer reviews and publishes an immutable, digest-bound release. Only this state is callable by Agents.

These states deliberately prevent “uploaded,” “machine checked,” and “published” from being treated as synonyms.

For Experience, the corresponding states are:

1. **Accepted Issue draft**: the public Issue exists and can be edited.
2. **Machine screened**: structure, privacy, safety, references, and declared workflow
   provenance pass; failures return exact changes requested.
3. **Recorded candidate**: the passing record is committed to its stable public path.
4. **Human reviewed**: a separate reviewer may later move the record to `reviewed/`.

Machine-screened and recorded are intentionally not synonyms for human-reviewed,
independently reproduced, or published Skill.

Matching workflow-verified V4 records with the same explicit Skill identity use deterministic claim comparison and do not require an embedding API. An embedding may still support other repository features, but it is not an intake or candidate-routing dependency for this path.

## Pull request adapter

`pull_request_target` inspects repository-root `SKILL.md` contributions as untrusted text. It checks out only the trusted base commit, never runs fork code, and posts one idempotent comment linking to the evidence form. The deployment push that first adds or later changes the adapter automatically scans every existing Open PR, so event triggers do not leave older contributions stranded; `workflow_dispatch` on `main` remains a recovery path. PR #64 is retained as a structural regression fixture and will be included in that first sweep: root path, invalid Agent Skills frontmatter, missing public workflow evidence, and incomplete verification must all route to the form rather than merge.

## Cost and operating boundary

The MVP uses standard GitHub-hosted runners in a public repository, the repository `GITHUB_TOKEN`, Issue Forms, and REST API metadata. It does not require a database, always-on server, larger runner, artifact storage, OpenAI key, or Gemini key for Skill Evidence intake. GitHub billing and quota rules still apply if the repository becomes private, larger runners are selected, or paid storage/services are added later.

## Security boundary

- Fork code is never checked out or executed by the privileged PR adapter.
- Evidence text is treated as untrusted and scanned for credential material, instruction overrides, exfiltration language, remote shell pipes, encoded PowerShell, and destructive root deletion.
- Public HTTPS URLs cannot contain credential-like query parameters.
- Machine screening grants `screened`, never `verified` human trust.
- A successful external workflow proves only the named public CI event at the exact commit; independent reproduction and publication remain separate gates.
