const assert = require("node:assert/strict");
const test = require("node:test");

const { renderSkillCandidateBody } = require("./dynamic-skills.cjs");
const { buildCanonicalSkillCandidates, planCandidateIssueSync } = require("./skill-candidate-sync.cjs");

function memory(issue, publisher) {
  return {
    memory_id: `memory-issue-${issue}`,
    promoted_from_issue: issue,
    consciousness_type: "pattern",
    context_environment: "A public package runtime smoke test",
    tags: ["build-release", "artifact-runtime"],
    embedding: [1, issue / 1000],
    embedding_model: "gemini-embedding-2",
    publisher: { github_login: publisher },
    trust: { status: "verified" },
    skill_candidate: { eligible: true, missing: [] },
    evidence: {
      symptom: "The package passes CI but fails after installation from the public registry.",
      root_cause: "The release test used the source tree instead of the immutable public artifact.",
      fix: "Install the exact public version in an empty directory and execute its real entry point.",
      verification: "Initialize the installed MCP server and request tools/list from a clean process.",
      applies_when: "Publishing Python packages, CLIs, MCP servers, or Agent plugins.",
      avoid_when: "The artifact has not been published yet.",
      test_commands: ["uvx noosphere-mcp"],
      source_urls: [`https://github.com/JinNing6/Noosphere/issues/${issue}`],
    },
  };
}

test("embedding recovery rebuilds canonical candidates and excludes tombstones", () => {
  const memories = [memory(1, "alice"), memory(2, "bob")];
  assert.equal(buildCanonicalSkillCandidates(memories, { withdrawn_issues: [] }).length, 1);
  assert.equal(buildCanonicalSkillCandidates(memories, { withdrawn_issues: [{ issue_number: 2 }] }).length, 0);
});

test("embedding recovery rebuilds separately reviewed maintainer evidence", () => {
  const source = {
    ...memory(67, "repo-maintainer"),
    record_kind: "skill-evidence",
    publication_track: "maintainer",
    proposed_skill: "public-artifact-recovery",
    trust: { status: "verified", reviewer: "second-maintainer" },
  };
  const candidates = buildCanonicalSkillCandidates(
    [source],
    { withdrawn_issues: [] },
  );

  assert.equal(candidates.length, 1);
  assert.equal(candidates[0].publication_track, "maintainer");
  assert.equal(candidates[0].name, "public-artifact-recovery");
});

test("candidate sync creates missing, updates drifted, and supersedes stale Issues", () => {
  const candidate = buildCanonicalSkillCandidates([memory(1, "alice"), memory(2, "bob")], { withdrawn_issues: [] })[0];
  const missing = planCandidateIssueSync([candidate], []);
  assert.deepEqual(missing.create, [candidate]);

  const stale = { ...candidate, candidate_sha256: "0".repeat(64) };
  const issue = { number: 7, state: "open", body: renderSkillCandidateBody(stale) };
  assert.equal(planCandidateIssueSync([candidate], [issue]).update.length, 1);
  assert.deepEqual(planCandidateIssueSync([], [issue]).supersede, [issue]);

  const duplicate = { number: 8, state: "open", body: renderSkillCandidateBody(stale) };
  const duplicatePlan = planCandidateIssueSync([candidate], [duplicate, issue]);
  assert.equal(duplicatePlan.update[0].issue.number, 7);
  assert.deepEqual(duplicatePlan.supersede.map((item) => item.number), [8]);
});
