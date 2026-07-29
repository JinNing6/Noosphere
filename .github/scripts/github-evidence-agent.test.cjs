const assert = require("node:assert/strict");
const test = require("node:test");

const { extractConsciousnessPayload } = require("./consciousness-payload.cjs");
const { clusterEligibleMemories, buildSkillCandidate } = require("./dynamic-skills.cjs");
const { verifyEvidenceProvenance } = require("./evidence-provenance.cjs");
const {
  assessSkillEligibility,
  bindVerifiedPublisher,
  screenSkillEvidenceDeterministically,
} = require("./memory-trust.cjs");

function formBody({ owner, issue }) {
  const repository = `https://github.com/${owner}/browser-reproduction`;
  const sha = String(issue).padStart(40, "0");
  return [
    "### Skill name", "browser-actionability-debug",
    "### Domain branch", "Frontend & Mobile",
    "### What this Skill solves", "Diagnose visible controls that real pointer input cannot activate.",
    "### Reproducible failure symptom", "A visible browser control cannot be clicked by the regression test.",
    "### Root cause", "A transparent decorative overlay intercepts pointer events before the control.",
    "### Reusable fix", "Remove pointer events from the decorative layer and preserve the control hit target.",
    "### Verification evidence", "The browser regression clicks the control and observes the expected state transition.",
    "### Applies when", "A real browser paints the control but pointer input does not reach it.",
    "### Do not apply when", "Application state intentionally disables the control.",
    "### Test commands", "```shell\nnode --test tests/browser-actionability.test.cjs\n```",
    "### Source repository URL", repository,
    "### Exact commit SHA", sha,
    "### Successful workflow run URL", `${repository}/actions/runs/${issue}`,
    "### Verification job name", "browser-regression",
    "### Verification step name", "Run browser regression",
    "### Artifact SHA-256", "_No response_",
    "### Public evidence URLs", `${repository}/issues/${issue}`,
  ].join("\n\n");
}

function githubFor(payload) {
  return {
    rest: {
      repos: {
        get: async () => ({ data: { private: false } }),
        getCommit: async () => ({ data: { sha: payload.source.commit_sha } }),
      },
      actions: {
        getWorkflowRun: async () => ({
          data: {
            head_sha: payload.source.commit_sha,
            status: "completed",
            conclusion: "success",
          },
        }),
        listJobsForWorkflowRun: Symbol("listJobsForWorkflowRun"),
      },
    },
    paginate: async () => [{
      name: payload.source.workflow_job_name,
      status: "completed",
      conclusion: "success",
      steps: [{
        name: payload.source.workflow_step_name,
        status: "completed",
        conclusion: "success",
      }],
    }],
  };
}

async function acceptedRecord({ owner, issue }) {
  const extracted = extractConsciousnessPayload(formBody({ owner, issue }));
  const payload = bindVerifiedPublisher(extracted.payload, {
    number: issue,
    user: { login: owner },
    author_association: "NONE",
  });
  payload.creator_signature = payload.publisher.github_login;
  const screen = screenSkillEvidenceDeterministically(payload);
  assert.equal(screen.status, "passed");
  payload.content_safety = { status: "passed", method: screen.method };
  payload.trust = { status: "screened", method: "deterministic-policy-screening" };
  payload.machine_verification = await verifyEvidenceProvenance(payload, {
    github: githubFor(payload),
  });
  payload.skill_candidate = assessSkillEligibility(payload);
  payload.memory_id = `memory-issue-${issue}`;
  payload.promoted_from_issue = issue;
  return payload;
}

test("zero-cost form records can reach the independent candidate gate without model keys", async () => {
  const left = await acceptedRecord({ owner: "alice", issue: 101 });
  const right = await acceptedRecord({ owner: "bob", issue: 102 });

  assert.equal(left.machine_verification.status, "workflow-verified");
  assert.deepEqual(left.skill_candidate, { eligible: true, missing: [] });

  const clusters = clusterEligibleMemories([left, right]);
  assert.equal(clusters.length, 1);
  const candidate = buildSkillCandidate(clusters[0]);
  assert.equal(candidate.name, "browser-actionability-debug");
  assert.deepEqual(candidate.publishers, ["alice", "bob"]);
  assert.equal(candidate.embedding_model, "deterministic-claim-v1");
});
