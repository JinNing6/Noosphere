const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const {
  assessSkillEligibility,
  bindVerifiedPublisher,
  buildModerationText,
  isTrustedReviewerPermission,
} = require("./memory-trust.cjs");

const completeEvidence = {
  symptom: "Mobile WebView taps the visible glow but no detail opens.",
  root_cause: "The visual bloom footprint is larger than the raycast hit mesh.",
  fix: "Use a synchronized invisible hit mesh and preserve instanceId mapping.",
  verification: "Android ADB tap regression selects the projected instance and opens detail.",
  applies_when: "React Three Fiber InstancedMesh targets inside Android WebView.",
  avoid_when: "The failure is caused by a DOM overlay intercepting pointer events.",
  test_commands: ["node reports/android-app-node-pick-regression.cjs"],
  source_urls: ["https://github.com/JinNing6/Noosphere/issues/28"],
};

test("binds publisher identity to the GitHub Issue author, not the claimed creator", () => {
  const payload = bindVerifiedPublisher(
    { creator_signature: "spoofed-maintainer" },
    { number: 42, user: { login: "actual-author" }, author_association: "NONE" },
  );

  assert.equal(payload.creator_signature, "spoofed-maintainer");
  assert.deepEqual(payload.publisher, {
    github_login: "actual-author",
    issue_author_association: "NONE",
    source_issue: 42,
  });
});

test("missing GitHub author identity cannot satisfy the Skill publisher gate", () => {
  const payload = bindVerifiedPublisher(
    {
      consciousness_type: "warning",
      trust: { status: "verified" },
      evidence: completeEvidence,
    },
    { number: 42, user: null, author_association: "NONE" },
  );

  assert.equal(payload.publisher.github_login, "");
  assert.equal(assessSkillEligibility(payload).eligible, false);
});

test("requires structured engineering evidence before a memory can become a Skill candidate", () => {
  const assessment = assessSkillEligibility({
    consciousness_type: "warning",
    trust: { status: "verified" },
    publisher: { github_login: "author" },
    evidence: { symptom: "Only a symptom exists." },
  });

  assert.equal(assessment.eligible, false);
  assert.deepEqual(assessment.missing, [
    "root_cause",
    "fix",
    "verification",
    "applies_when",
    "test_commands",
    "source_urls",
  ]);
});

test("marks verified engineering memories with complete evidence as candidate eligible", () => {
  const assessment = assessSkillEligibility({
    consciousness_type: "pattern",
    trust: { status: "verified" },
    publisher: { github_login: "author" },
    evidence: completeEvidence,
  });

  assert.deepEqual(assessment, { eligible: true, missing: [] });
});

test("screened evidence is candidate-eligible without being marked human-verified", () => {
  const assessment = assessSkillEligibility({
    consciousness_type: "pattern",
    trust: { status: "screened" },
    content_safety: { status: "passed" },
    publisher: { github_login: "author" },
    evidence: completeEvidence,
  });

  assert.deepEqual(assessment, { eligible: true, missing: [] });
});

test("requires public HTTPS evidence URLs", () => {
  const assessment = assessSkillEligibility({
    consciousness_type: "pattern",
    trust: { status: "verified" },
    publisher: { github_login: "author" },
    evidence: { ...completeEvidence, source_urls: ["http://example.com/private"] },
  });

  assert.equal(assessment.eligible, false);
  assert.ok(assessment.missing.includes("public_https_source_urls"));

  const credentialed = assessSkillEligibility({
    consciousness_type: "pattern",
    trust: { status: "verified" },
    publisher: { github_login: "author" },
    evidence: { ...completeEvidence, source_urls: ["https://example.com/evidence?token=secret"] },
  });
  assert.equal(credentialed.eligible, false);
});

test("moderation text includes every Agent-facing evidence field", () => {
  const text = buildModerationText({
    thought_vector_text: "Reusable lesson",
    context_environment: "Public package runtime",
    evidence: completeEvidence,
  });

  for (const value of Object.values(completeEvidence).flat()) {
    assert.match(text, new RegExp(String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }
});

test("only repository write-level permissions can perform a trusted review", () => {
  assert.equal(isTrustedReviewerPermission("admin"), true);
  assert.equal(isTrustedReviewerPermission("maintain"), true);
  assert.equal(isTrustedReviewerPermission("write"), true);
  assert.equal(isTrustedReviewerPermission("triage"), false);
  assert.equal(isTrustedReviewerPermission("read"), false);
});

test("promotion workflow binds publisher, evaluates evidence, and fails closed", () => {
  const workflow = fs.readFileSync(
    path.join(__dirname, "..", "workflows", "consciousness_promote.yml"),
    "utf8",
  );

  assert.match(workflow, /bindVerifiedPublisher/);
  assert.match(workflow, /assessSkillEligibility/);
  assert.match(workflow, /buildModerationText/);
  assert.match(workflow, /status: 'screened'/);
  assert.match(workflow, /status: 'passed'/);
  assert.match(workflow, /isTrustedReviewerPermission/);
  assert.match(workflow, /needs-review/);
  assert.match(workflow, /hasVerifiedExisting/);
  assert.match(workflow, /Object\.assign\(payload, bindVerifiedPublisher\(payload, issue\)\)/);
  assert.match(workflow, /sha: existingFile\.sha/);
  assert.doesNotMatch(workflow, /Boolean\(trustedReview \|\| existingPromotion\)/);
  assert.doesNotMatch(workflow, /!existingPromotion && payload\.skill_candidate/);
  assert.doesNotMatch(workflow, /fail-open/);
  assert.doesNotMatch(workflow, /method: 'automated-content-screening'/);
});
