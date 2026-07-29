const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const {
  COMMENT_MARKER,
  inspectSkillEvidencePullRequest,
  listPullRequestsForReconciliation,
  renderSkillEvidencePullRequestComment,
} = require("./skill-evidence-pr-adapter.cjs");

test("routes the reviewed PR #64 shape to the evidence form", () => {
  const fixture = JSON.parse(fs.readFileSync(
    path.join(__dirname, "fixtures", "pr64-review-fixture.json"),
    "utf8",
  ));
  const result = inspectSkillEvidencePullRequest(fixture);

  assert.equal(fixture.source_pr, 64);
  assert.equal(result.relevant, true);
  assert.equal(result.route, "skill-evidence-form");
  assert.deepEqual(result.findings.map((finding) => finding.code), [
    "UNSUPPORTED_ROOT_SKILL_PATH",
    "INVALID_SKILL_FRONTMATTER",
    "PUBLIC_WORKFLOW_EVIDENCE_MISSING",
    "VERIFICATION_INCOMPLETE",
  ]);
});

test("ignores ordinary code pull requests", () => {
  const result = inspectSkillEvidencePullRequest({
    files: [{ filename: "sdk/noosphere/server.py", status: "modified" }],
  });

  assert.deepEqual(result, { relevant: false, findings: [] });
});

test("deployment push backfills existing Open PRs including PR #64", async () => {
  const calls = [];
  const openPullRequests = [{ number: 64, state: "open" }, { number: 81, state: "open" }];
  const github = {
    rest: { pulls: { list: Symbol("listPullRequests") } },
    paginate: async (method, options) => {
      calls.push({ method, options });
      return openPullRequests;
    },
  };

  const result = await listPullRequestsForReconciliation({
    eventName: "push",
    github,
    owner: "JinNing6",
    repo: "Noosphere",
  });

  assert.deepEqual(result, openPullRequests);
  assert.equal(result.some((pullRequest) => pullRequest.number === 64), true);
  assert.deepEqual(calls[0].options, {
    owner: "JinNing6",
    repo: "Noosphere",
    state: "open",
    per_page: 100,
  });
});

test("live PR events reconcile only the triggering PR", async () => {
  const eventPullRequest = { number: 99 };
  const result = await listPullRequestsForReconciliation({
    eventName: "pull_request_target",
    eventPullRequest,
    github: { paginate: async () => assert.fail("must not sweep on a live PR event") },
    owner: "JinNing6",
    repo: "Noosphere",
  });

  assert.deepEqual(result, [eventPullRequest]);
});

test("renders one stable actionable adapter comment", () => {
  const result = inspectSkillEvidencePullRequest({
    files: [{ filename: "SKILL.md", status: "added" }],
    fileContents: { "SKILL.md": "# A prose contribution" },
  });
  const comment = renderSkillEvidencePullRequestComment(result, {
    formUrl: "https://github.com/JinNing6/Noosphere/issues/new?template=skill-proposal.yml",
  });

  assert.match(comment, /Shared Skill evidence form/);
  assert.match(comment, /automatically verifies the exact public commit/);
  assert.ok(comment.endsWith(COMMENT_MARKER));
});

test("adapter workflow checks out only the base commit and never executes PR code", () => {
  const workflow = fs.readFileSync(
    path.join(__dirname, "..", "workflows", "skill_evidence_pr_adapter.yml"),
    "utf8",
  );

  assert.match(workflow, /pull_request_target:/);
  assert.match(workflow, /push:\s*\n\s+branches: \[main\]/);
  assert.match(workflow, /workflow_dispatch:/);
  assert.match(workflow, /\.github\/workflows\/skill_evidence_pr_adapter\.yml/);
  assert.match(workflow, /\.github\/scripts\/skill-evidence-pr-adapter\.cjs/);
  assert.match(workflow, /ref: \$\{\{ github\.event\.pull_request\.base\.sha \|\| github\.sha \}\}/);
  assert.match(workflow, /persist-credentials: false/);
  assert.match(workflow, /pull-requests: write/);
  assert.match(workflow, /github\.event_name != 'workflow_dispatch' \|\| github\.ref == 'refs\/heads\/main'/);
  assert.match(workflow, /listPullRequestsForReconciliation/);
  assert.match(workflow, /eventName: context\.eventName/);
  assert.match(workflow, /Status: resolved/);
  assert.match(workflow, /removeLabel/);
  assert.match(workflow, /github-actions\[bot\]/);
  assert.doesNotMatch(workflow, /pull_request\.head\.sha \}\}/);
  assert.doesNotMatch(workflow, /\brun:/);
});
