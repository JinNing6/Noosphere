const GITHUB_REPOSITORY_URL = /^https:\/\/github\.com\/([^/]+)\/([^/?#]+)\/?$/i;
const GITHUB_WORKFLOW_RUN_URL = /^https:\/\/github\.com\/([^/]+)\/([^/?#]+)\/actions\/runs\/(\d+)\/?$/i;
const COMMIT_SHA = /^[0-9a-f]{40}$/i;
const ARTIFACT_SHA256 = /^(?:sha256:)?[0-9a-f]{64}$/i;

function compactText(value, maxLength = 500) {
  return String(value || "").trim().slice(0, maxLength);
}

function normalizeArtifactDigest(value) {
  const digest = compactText(value, 80).toLowerCase();
  if (!digest) return "";
  return digest.startsWith("sha256:") ? digest : `sha256:${digest}`;
}

function validateEvidenceSource(value) {
  const source = value && typeof value === "object" ? value : {};
  const repositoryUrl = compactText(source.repository_url);
  const commitSha = compactText(source.commit_sha, 100).toLowerCase();
  const workflowRunUrl = compactText(source.workflow_run_url);
  const workflowJobName = compactText(source.workflow_job_name, 200);
  const workflowStepName = compactText(source.workflow_step_name, 200);
  const artifactSha256 = normalizeArtifactDigest(source.artifact_sha256);
  const repositoryMatch = repositoryUrl.match(GITHUB_REPOSITORY_URL);
  const workflowMatch = workflowRunUrl.match(GITHUB_WORKFLOW_RUN_URL);
  const missing = [];

  if (!repositoryMatch) missing.push("source.repository_url");
  if (!COMMIT_SHA.test(commitSha)) missing.push("source.commit_sha");
  if (!workflowMatch) missing.push("source.workflow_run_url");
  if (!workflowJobName) missing.push("source.workflow_job_name");
  if (!workflowStepName) missing.push("source.workflow_step_name");
  if (source.artifact_sha256 && !ARTIFACT_SHA256.test(compactText(source.artifact_sha256, 80))) {
    missing.push("source.artifact_sha256");
  }

  if (repositoryMatch && workflowMatch) {
    const repositoryIdentity = `${repositoryMatch[1]}/${repositoryMatch[2]}`.toLowerCase();
    const workflowIdentity = `${workflowMatch[1]}/${workflowMatch[2]}`.toLowerCase();
    if (repositoryIdentity !== workflowIdentity) missing.push("source.workflow_run_repository_match");
  }

  return {
    valid: missing.length === 0,
    missing: [...new Set(missing)],
    source: {
      repository_url: repositoryUrl,
      commit_sha: commitSha,
      workflow_run_url: workflowRunUrl,
      workflow_job_name: workflowJobName,
      workflow_step_name: workflowStepName,
      artifact_sha256: artifactSha256,
    },
    repository: repositoryMatch
      ? { owner: repositoryMatch[1], repo: repositoryMatch[2] }
      : null,
    workflow_run_id: workflowMatch ? Number.parseInt(workflowMatch[3], 10) : null,
  };
}

function failure(reason, findings, source = null) {
  return {
    status: "needs-evidence",
    reason,
    findings: [...new Set(findings.filter(Boolean))],
    ...(source ? { source } : {}),
  };
}

async function verifyEvidenceProvenance(payload, { github }) {
  const structural = validateEvidenceSource(payload?.source);
  if (!structural.valid) {
    return failure("invalid-source-metadata", structural.missing, structural.source);
  }

  const { owner, repo } = structural.repository;
  const runId = structural.workflow_run_id;
  const source = structural.source;

  try {
    const repositoryResponse = await github.rest.repos.get({ owner, repo });
    if (repositoryResponse.data.private) {
      return failure("repository-not-public", ["source.repository_url must be public"], source);
    }

    const commitResponse = await github.rest.repos.getCommit({
      owner,
      repo,
      ref: source.commit_sha,
    });
    if (String(commitResponse.data.sha || "").toLowerCase() !== source.commit_sha) {
      return failure("commit-mismatch", ["resolved commit does not match source.commit_sha"], source);
    }

    const runResponse = await github.rest.actions.getWorkflowRun({ owner, repo, run_id: runId });
    const run = runResponse.data || {};
    const runHeadSha = String(run.head_sha || "").toLowerCase();
    if (runHeadSha !== source.commit_sha) {
      return failure("workflow-commit-mismatch", ["workflow run head_sha does not match source.commit_sha"], source);
    }
    if (run.status !== "completed" || run.conclusion !== "success") {
      return failure("workflow-not-successful", [
        `workflow status=${compactText(run.status) || "unknown"}`,
        `workflow conclusion=${compactText(run.conclusion) || "unknown"}`,
      ], source);
    }

    const jobs = await github.paginate(github.rest.actions.listJobsForWorkflowRun, {
      owner,
      repo,
      run_id: runId,
      filter: "latest",
      per_page: 100,
    });
    const job = jobs.find((candidate) => candidate.name === source.workflow_job_name);
    if (!job) {
      return failure("job-not-found", [`successful job not found: ${source.workflow_job_name}`], source);
    }
    if (job.status !== "completed" || job.conclusion !== "success") {
      return failure("job-not-successful", [
        `job status=${compactText(job.status) || "unknown"}`,
        `job conclusion=${compactText(job.conclusion) || "unknown"}`,
      ], source);
    }
    const step = (job.steps || []).find((candidate) => candidate.name === source.workflow_step_name);
    if (!step) {
      return failure("step-not-found", [`successful step not found: ${source.workflow_step_name}`], source);
    }
    if (step.status !== "completed" || step.conclusion !== "success") {
      return failure("step-not-successful", [
        `step status=${compactText(step.status) || "unknown"}`,
        `step conclusion=${compactText(step.conclusion) || "unknown"}`,
      ], source);
    }

    return {
      status: "workflow-verified",
      source_repository: `${owner}/${repo}`,
      commit_sha: source.commit_sha,
      workflow_run_id: runId,
      workflow_run_url: source.workflow_run_url,
      workflow_job_name: source.workflow_job_name,
      workflow_step_name: source.workflow_step_name,
      artifact_sha256: source.artifact_sha256 || null,
      claim_boundary: "The named public GitHub job and step succeeded at the exact commit; semantic reproduction remains a separate review gate.",
    };
  } catch (error) {
    const status = Number(error?.status || 0);
    return failure(
      status === 404 ? "public-source-not-found" : "github-verification-unavailable",
      [`GitHub verification failed${status ? ` (${status})` : ""}`],
      source,
    );
  }
}

module.exports = {
  validateEvidenceSource,
  verifyEvidenceProvenance,
};
