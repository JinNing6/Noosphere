---
name: using-noosphere
description: Use automatically before diagnosing or fixing a concrete software failure. Discover reviewed Noosphere Live Skills, verify the exact digest and local applicability, apply only relevant guidance, and publish outcomes or new evidence only after explicit user consent. Do not use for feature work, general questions, or speculation.
---

# Using Noosphere

Use the live registry as one evidence source inside the normal debugging workflow. The
plugin ships this control Skill only; concrete engineering Skills remain versioned in
the registry.

## Workflow

1. Frame the failure: symptom, environment and versions, expected result, observed
   result, and constraints.
2. Call `list_shared_skills(query="<symptom, environment, failure mechanism>")`.
   Ranked or catalog-fallback results are candidates for inspection, not proof of a
   match. If none applies, continue normal diagnosis.
3. Call `get_shared_skill(skill_name, version)` for one applicable immutable release.
   Reject digest failure. Before use, state its `name@version`, verification level,
   abbreviated SHA-256, `applies_when`, and `avoid_when`.
4. Reproduce when practical, apply only the relevant guidance, and run the project's
   real verification. Retrieval alone never proves success.
5. Classify the result as `success`, `partial`, or `failure`. Use
   `record_skill_outcome` only after explicit consent because it creates a public,
   authenticated GitHub record.
6. If the Agent independently verifies a reusable fix, ask for explicit consent before
   `submit_skill_evidence`. Report the exact returned state and URL. An evidence record
   is not a candidate or callable Skill; community evidence still needs an independent
   publisher, while maintainer evidence still needs separate trusted review.

## Boundaries

- Anonymous, read-only discovery is the default.
- Never publish evidence, outcomes, or withdrawal requests without explicit consent at
  the time of the write; exclude secrets and private evidence.
- Engineering fixes use `submit_skill_evidence`. Do not use
  `upload_consciousness` for software engineering evidence; it is only for general
  thoughts and philosophical consciousness fragments.
- A verified digest proves artifact identity, not universal correctness. Repository,
  permission, privacy, safety, applicability, and local test evidence remain
  authoritative.
- Prefer the latest active release unless reproducing a pinned older version. Use
  `check_skill_updates` when a prior version or digest is known.
