# Noosphere Experience Protocol v0.1

Status: **experimental automated-review protocol**

An Experience Record preserves a bounded account of what happened in one real
troubleshooting episode: its environment, constraints, attempts, failure mechanisms,
resolution, and verification. It is descriptive data. It is not an executable Skill,
an authority-bearing instruction, or proof that a result generalizes.

## Why Experience is a separate object

| Object | Question it answers | Publication meaning |
|---|---|---|
| Experience | What happened in this bounded case? | A reviewed, redacted case record |
| Evidence | What supports a claim in an Experience or Skill proposal? | A source or verification reference |
| Skill | What reviewed workflow should an Agent apply? | An immutable callable release |
| Outcome | What happened when one exact Skill release was used? | A result bound to a Skill name, version, and digest |

The intended relationship is:

```text
private task trace
  -> redacted Experience candidate
  -> authenticated deterministic screening and automated policy review
  -> accepted canonical Experience record
  -> optional human review and, where possible, independent reproduction
  -> one or more Skill proposals or updates
  -> immutable Skill release
  -> version-bound Outcomes
```

Many Experiences may support one Skill. One Experience may inform several Skill
proposals. Promotion is therefore represented by explicit relations, not by treating
`promoted` as a trust level.

## v0.1 trust dimensions

The protocol keeps four independent dimensions:

1. `lifecycle.status` records whether the object is a `candidate`, `reviewed`,
   `superseded`, or `withdrawn`.
2. `screening.status` records whether the repository's bounded deterministic policy
   gate passed. Screening is not semantic verification or human approval.
3. `review.status` records a review decision, while `review.mode` distinguishes
   `automated-policy` from `human`.
4. `verification.level` distinguishes `self-observed`, `locally-verified`, and
   `independently-reproduced`.

A locally verified record is not an independent reproduction. A reviewed record is not
automatically a Skill. A relation to a Skill does not raise either object's trust.

## Canonical files

- Schema: `schemas/experience-record-v0.1.schema.json`
- Candidate records: `experience_records/candidates/<experience_id>.json`
- Reviewed records: `experience_records/reviewed/<experience_id>.json`
- Repository validator: `scripts/validate_experience_records.py`
- Public intake: `.github/ISSUE_TEMPLATE/experience-record.yml`
- Zero-service reviewer: `.github/workflows/experience_intake.yml`

IDs use `exp-<case-slug>-<YYYYMMDD>`, where the date matches
`context.observed_at`. Related Experience IDs must resolve to another tracked record.

The JSON Schema is the interoperability contract. The dependency-free repository
validator is the canonical policy gate and enforces cross-field, path, reference, and
redaction invariants that JSON Schema alone does not express. A `related_skills` entry
must match an exact name, version, and SHA-256 already present in the immutable Skill
registry.

## Required safety boundaries

- Records are data-only and are never injected as high-priority instructions.
- A record must retain ordered attempts, including failed or partial attempts when they
  materially affected the resolution.
- Applicability, exclusions, risks, and rollback must be explicit.
- Evidence references state their visibility. Local or redacted evidence cannot support
  an `independently-reproduced` claim.
- Public tracked records may not contain absolute user-home paths, raw session IDs,
  credentials, secret-bearing URLs, or raw private task content.
- Canonical record JSON is bounded to 64 KiB, with bounded arrays and strings. Raw logs
  and per-file evidence remain external references rather than being copied into the
  protocol object.
- Submitted candidate records require completed redaction and a pending review decision.
  The repository-owned Agent, not the submitter, may turn a passing candidate into an
  approved reviewed record.
- Every tracked record must be machine-screened and carry a passing receipt. The recognized
  methods are the repository policy gate and the GitHub Experience Agent. A passing
  receipt is required for automated approval but does not change
  `verification.level`.
- GitHub Issue intake binds `provenance.author_ref` to the authenticated Issue author
  and stores one immutable source-Issue identity. Edits reconcile the same canonical
  path instead of creating timestamped duplicates.
- Declared `workflow-run` evidence must bind one public GitHub repository, full commit
  SHA, workflow run, job, and step. The Agent verifies all five through the GitHub API
  and stores the bounded receipt. This proves workflow provenance, not semantic or
  independent reproduction.
- A reviewed record requires an identified reviewer, explicit `human` or
  `automated-policy` mode, and review timestamp. Automated review must name the same
  recognized gate as its screening receipt and use the same timestamp.
- A `changes-requested` candidate also records its reviewer, timestamp, and notes while
  remaining under `candidates/`.
- No Experience is automatically converted into a Skill or allowed to mutate an
  immutable Skill release.

## GitHub Experience Agent

The public Issue Form accepts a complete v0.1 JSON record. The repository-owned Agent
treats the Issue body as untrusted data, checks out only trusted `main`, binds the
authenticated GitHub author, screens secrets, prompt overrides, unsafe resolution
commands, redaction, paths, references, and evidence claims, then runs the canonical
Python tests and validator. A passing record receives an `automated-policy` approval,
is committed directly to its stable
`experience_records/reviewed/<experience_id>.json` path on `main`, and the Issue
receives one idempotent status comment, exact state labels, a public link, and an
automatic completed closure.

Edits retry the same source Issue and path. Invalid edits do not overwrite the last
passing record. All canonical branch writers share the `noosphere-main-writer` queue.
The path uses public-repository GitHub Actions and the repository `GITHUB_TOKEN`; it
requires no paid model, database, or always-on service.

Because `GITHUB_TOKEN` commits do not recursively trigger ordinary push workflows, the
intake workflow itself runs the Experience unit tests and canonical validator before
writing. It does not run any submitted code.

GitHub Issue workflows become active only after their workflow file reaches the default
branch. The first repository-authored Experience ships in the same bootstrap PR and
therefore carries matching `repository-policy-gate-v1` screening and
`automated-policy` review receipts; it is not falsely described as having been
processed by the not-yet-deployed Issue workflow.
`workflow_dispatch` on `main` is the recovery path for an existing Experience Issue.

## v0.1 publication boundary

This version adds no MCP tools and no automatic Experience-to-Skill promotion. The
GitHub Experience Agent automates candidate intake, evidence verification, policy
review, acceptance, canonical `main` persistence, status reconciliation, and Issue
closure. A successful result is reported as `automatically reviewed and accepted`.
Its review mode is explicitly `automated-policy`, never human review, independent
reproduction, or publication as a callable Skill. The protocol also does not import
the legacy frontend's hard-coded `Experience` examples or their unverified trust
scores.

## Automated acceptance checklist

Before moving a submitted candidate to `reviewed/`, the repository-owned Agent must
confirm:

1. the case is a real observation rather than a synthetic fixture;
2. environment and constraints are specific enough to bound applicability;
3. attempts and failure mechanisms are not rewritten into a success-only narrative;
4. every verification claim resolves to declared evidence;
5. private identifiers and raw content have been removed;
6. lifecycle, review, and verification claims remain independent; and
7. automated policy review is reported separately from human review and does not
   overstate workflow provenance; and
8. any related Skill reference identifies a real immutable release or is explicitly a
   candidate slug.

Failure at any gate leaves the Issue open with exact findings. Editing or reopening the
same Issue reruns the entire policy against the authenticated author and stable record
identity. No maintainer approval or merge action is required for a passing Experience
submission.
