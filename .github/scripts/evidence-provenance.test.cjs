const assert = require("node:assert/strict");
const test = require("node:test");

const {
  validateEvidenceSource,
  verifyEvidenceProvenance,
} = require("./evidence-provenance.cjs");

const source = {
  repository_url: "https://github.com/example/reproduction",
  commit_sha: "0123456789abcdef0123456789abcdef01234567",
  workflow_run_url: "https://github.com/example/reproduction/actions/runs/12345",
  workflow_job_name: "browser-regression",
  workflow_step_name: "Run browser regression",
  artifact_sha256: "a".repeat(64),
};

function buildGithub(overrides = {}) {
  const jobs = overrides.jobs || [{
    name: "browser-regression",
    status: "completed",
    conclusion: "success",
    steps: [{ name: "Run browser regression", status: "completed", conclusion: "success" }],
  }];
  return {
    rest: {
      repos: {
        get: async () => ({ data: { private: false } }),
        getCommit: async () => ({ data: { sha: source.commit_sha } }),
      },
      actions: {
        getWorkflowRun: async () => ({
          data: { head_sha: source.commit_sha, status: "completed", conclusion: "success" },
        }),
        listJobsForWorkflowRun: Symbol("listJobsForWorkflowRun"),
      },
    },
    paginate: async () => jobs,
    ...overrides.github,
  };
}

test("normalizes exact public GitHub workflow provenance", () => {
  const result = validateEvidenceSource(source);

  assert.equal(result.valid, true);
  assert.equal(result.source.artifact_sha256, `sha256:${"a".repeat(64)}`);
  assert.deepEqual(result.repository, { owner: "example", repo: "reproduction" });
  assert.equal(result.workflow_run_id, 12345);
});

test("rejects a workflow URL from a different repository", () => {
  const result = validateEvidenceSource({
    ...source,
    workflow_run_url: "https://github.com/attacker/other/actions/runs/12345",
  });

  assert.equal(result.valid, false);
  assert.ok(result.missing.includes("source.workflow_run_repository_match"));
});

test("rejects a commit value longer than one full SHA instead of truncating it", () => {
  const result = validateEvidenceSource({
    ...source,
    commit_sha: `${source.commit_sha}0`,
  });

  assert.equal(result.valid, false);
  assert.ok(result.missing.includes("source.commit_sha"));
});

test("verifies a successful named job and step at the exact commit", async () => {
  const result = await verifyEvidenceProvenance({ source }, { github: buildGithub() });

  assert.equal(result.status, "workflow-verified");
  assert.equal(result.commit_sha, source.commit_sha);
  assert.equal(result.workflow_job_name, source.workflow_job_name);
  assert.match(result.claim_boundary, /semantic reproduction remains a separate review gate/);
});

test("fails closed when the workflow run is for another commit", async () => {
  const github = buildGithub();
  github.rest.actions.getWorkflowRun = async () => ({
    data: { head_sha: "f".repeat(40), status: "completed", conclusion: "success" },
  });

  const result = await verifyEvidenceProvenance({ source }, { github });

  assert.equal(result.status, "needs-evidence");
  assert.equal(result.reason, "workflow-commit-mismatch");
});

test("fails closed when the submitter-named step did not succeed", async () => {
  const result = await verifyEvidenceProvenance({ source }, {
    github: buildGithub({
      jobs: [{
        name: "browser-regression",
        status: "completed",
        conclusion: "success",
        steps: [{ name: "Run browser regression", status: "completed", conclusion: "failure" }],
      }],
    }),
  });

  assert.equal(result.status, "needs-evidence");
  assert.equal(result.reason, "step-not-successful");
});

test("reports unavailable public evidence without leaking provider errors", async () => {
  const github = buildGithub();
  github.rest.repos.get = async () => {
    const error = new Error("sensitive upstream detail");
    error.status = 404;
    throw error;
  };

  const result = await verifyEvidenceProvenance({ source }, { github });

  assert.equal(result.status, "needs-evidence");
  assert.equal(result.reason, "public-source-not-found");
  assert.doesNotMatch(JSON.stringify(result), /sensitive upstream detail/);
});
