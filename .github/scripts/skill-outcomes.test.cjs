const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const {
  extractSkillOutcome,
  recordApprovedSkillOutcome,
  validateSkillOutcome,
} = require("./skill-outcomes.cjs");

function fixture(outcome = "success") {
  const sha = "a".repeat(64);
  return {
    registry: {
      schema_version: "1.0",
      revision: 1,
      skills: [{
        name: "runtime-smoke-gate",
        originators: ["originator"],
        latest: "1.0.0",
        releases: [{
          version: "1.0.0",
          status: "active",
          source_count: 2,
          publisher_count: 2,
          artifact: { sha256: sha },
          verification: { level: "independently-reproduced", verified_outcomes: 0 },
          provenance: { authors: ["originator", "validator"] },
        }],
      }],
    },
    payload: {
      schema_version: "1.0",
      outcome_id: "outcome-001",
      skill_name: "runtime-smoke-gate",
      skill_version: "1.0.0",
      skill_sha256: sha,
      outcome,
      task_summary: "Ran the public artifact in a clean environment.",
      verification_summary: "Initialize and tools/list completed successfully.",
      evidence_urls: ["https://github.com/JinNing6/Noosphere/issues/37"],
    },
  };
}

test("extracts and validates a structured outcome marker", () => {
  const { registry, payload } = fixture();
  const body = `<!-- SKILL_OUTCOME_START -->\n\`\`\`json\n${JSON.stringify(payload)}\n\`\`\`\n<!-- SKILL_OUTCOME_END -->`;
  assert.deepEqual(extractSkillOutcome(body), payload);
  assert.equal(validateSkillOutcome(payload, registry).valid, true);
});

test("approved external success advances outcome maturity and is idempotent", () => {
  const { registry, payload } = fixture();
  const issue = { number: 90, html_url: "https://github.com/x/y/issues/90", user: { login: "external-user" } };
  const first = recordApprovedSkillOutcome(registry, { schema_version: "1.0", outcomes: [] }, payload, issue, {
    reviewer: "maintainer",
    approvedAt: "2026-07-15T00:00:00Z",
  });
  assert.equal(first.registry.skills[0].releases[0].verification.level, "outcome-proven");
  assert.equal(first.registry.skills[0].releases[0].verification.verified_outcomes, 1);
  const repeated = recordApprovedSkillOutcome(first.registry, first.ledger, payload, issue, {
    reviewer: "maintainer",
    approvedAt: "2026-07-15T00:01:00Z",
  });
  assert.equal(repeated.idempotent, true);
  assert.equal(repeated.registry.revision, 2);
});

test("success without public evidence is recorded but cannot become outcome-proven", () => {
  const { registry, payload } = fixture();
  payload.evidence_urls = [];
  const result = recordApprovedSkillOutcome(
    registry,
    { schema_version: "1.0", outcomes: [] },
    payload,
    { number: 94, html_url: "https://github.com/x/y/issues/94", user: { login: "external-user" } },
    { reviewer: "maintainer", approvedAt: "2026-07-15T00:00:00Z" },
  );

  assert.equal(result.registry.skills[0].releases[0].verification.level, "independently-reproduced");
  assert.equal(result.registry.skills[0].releases[0].verification.verified_outcomes, 1);
});

test("maintainer-validated releases cannot skip independent reproduction maturity", () => {
  const { registry, payload } = fixture();
  const release = registry.skills[0].releases[0];
  release.verification.level = "maintainer-validated";
  release.source_count = 1;
  release.publisher_count = 1;
  const result = recordApprovedSkillOutcome(
    registry,
    { schema_version: "1.0", outcomes: [] },
    payload,
    { number: 95, html_url: "https://github.com/x/y/issues/95", user: { login: "external-user" } },
    { reviewer: "maintainer", approvedAt: "2026-07-15T00:00:00Z" },
  );

  assert.equal(result.registry.skills[0].releases[0].verification.level, "maintainer-validated");
});

test("failure records an update-needed signal without mutating the Skill artifact", () => {
  const { registry, payload } = fixture("failure");
  const beforeArtifact = structuredClone(registry.skills[0].releases[0].artifact);
  const result = recordApprovedSkillOutcome(
    registry,
    { schema_version: "1.0", outcomes: [] },
    payload,
    { number: 91, html_url: "https://github.com/x/y/issues/91", user: { login: "external-user" } },
    { reviewer: "maintainer", approvedAt: "2026-07-15T00:00:00Z" },
  );
  const release = result.registry.skills[0].releases[0];
  assert.equal(result.updateNeeded, true);
  assert.equal(release.verification.update_needed, true);
  assert.deepEqual(release.artifact, beforeArtifact);
});

test("rejects digest drift and conflicting reuse of an outcome id", () => {
  const { registry, payload } = fixture();
  assert.equal(validateSkillOutcome({ ...payload, skill_sha256: "b".repeat(64) }, registry).valid, false);
  const first = recordApprovedSkillOutcome(
    registry,
    { schema_version: "1.0", outcomes: [] },
    payload,
    { number: 92, html_url: "https://github.com/x/y/issues/92", user: { login: "external-user" } },
    { reviewer: "maintainer", approvedAt: "2026-07-15T00:00:00Z" },
  );
  assert.throws(() => recordApprovedSkillOutcome(
    first.registry,
    first.ledger,
    { ...payload, outcome: "failure" },
    { number: 93, html_url: "https://github.com/x/y/issues/93", user: { login: "external-user" } },
    { reviewer: "maintainer", approvedAt: "2026-07-15T00:01:00Z" },
  ), /different evidence/);
});

test("rejects malformed or unbounded outcome payloads at the workflow boundary", () => {
  const { registry, payload } = fixture();
  assert.equal(validateSkillOutcome({ ...payload, schema_version: "2.0" }, registry).valid, false);
  assert.equal(validateSkillOutcome({ ...payload, task_summary: "x".repeat(2001) }, registry).valid, false);
  assert.equal(validateSkillOutcome({ ...payload, evidence_urls: ["http://example.com"] }, registry).valid, false);
});

test("outcome workflow separates intake from trusted ledger mutation", () => {
  const workflow = fs.readFileSync(
    path.join(__dirname, "..", "workflows", "skill_outcome.yml"),
    "utf8",
  );
  assert.match(workflow, /needs-outcome-review/);
  assert.match(workflow, /skill-outcome-approved/);
  assert.match(workflow, /getCollaboratorPermissionLevel/);
  assert.match(workflow, /recordApprovedSkillOutcome/);
  assert.match(workflow, /shared_skills\/outcomes\.json/);
  assert.match(workflow, /skill-update-needed/);
});
