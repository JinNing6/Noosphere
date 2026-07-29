const COMMENT_MARKER = "<!-- noosphere-skill-evidence-pr-adapter -->";

function compactText(value, maxLength = 200000) {
  return String(value || "").replace(/\r/g, "").slice(0, maxLength);
}

function hasValidSkillFrontmatter(content) {
  const match = /^---\n([\s\S]*?)\n---(?:\n|$)/.exec(content);
  if (!match) return false;
  return /^name:\s*[a-z0-9]+(?:-[a-z0-9]+)*\s*$/m.test(match[1])
    && /^description:\s*\S.+$/m.test(match[1]);
}

function hasWorkflowEvidence(content) {
  return /https:\/\/github\.com\/[^/\s]+\/[^/\s]+\/actions\/runs\/\d+/i.test(content)
    && /\b[0-9a-f]{40}\b/i.test(content);
}

function hasNonemptyVerification(content) {
  const heading = /^(?:#{1,6}\s+)?verification(?: evidence)?\s*:?\s*$/im;
  const match = heading.exec(content);
  if (!match) return false;
  const remainder = content.slice(match.index + match[0].length);
  const section = remainder.split(/^#{1,6}\s+/m, 1)[0].trim();
  return Boolean(section && !/^[-*_`\s]*$/m.test(section));
}

function inspectSkillEvidencePullRequest({ files, fileContents = {} }) {
  const rootSkill = (files || []).find((file) => (
    String(file.filename || "").toLowerCase() === "skill.md" && file.status !== "removed"
  ));
  if (!rootSkill) return { relevant: false, findings: [] };

  const content = compactText(fileContents[rootSkill.filename]);
  const findings = [{
    code: "UNSUPPORTED_ROOT_SKILL_PATH",
    message: "A repository-root SKILL.md is not a publishable Shared Skill path.",
  }];
  if (!hasValidSkillFrontmatter(content)) {
    findings.push({
      code: "INVALID_SKILL_FRONTMATTER",
      message: "SKILL.md must start with YAML frontmatter containing kebab-case name and description fields.",
    });
  }
  if (!hasWorkflowEvidence(content)) {
    findings.push({
      code: "PUBLIC_WORKFLOW_EVIDENCE_MISSING",
      message: "No exact public GitHub workflow run and 40-character commit SHA were found.",
    });
  }
  if (!hasNonemptyVerification(content)) {
    findings.push({
      code: "VERIFICATION_INCOMPLETE",
      message: "The verification section is missing or empty.",
    });
  }

  return {
    relevant: true,
    route: "skill-evidence-form",
    findings,
    labels: ["skill-evidence-pr-routed", "skill-evidence-incomplete"],
  };
}

async function listPullRequestsForReconciliation({
  eventName,
  eventPullRequest,
  github,
  owner,
  repo,
}) {
  if (eventName === "pull_request_target") {
    return eventPullRequest ? [eventPullRequest] : [];
  }
  return github.paginate(github.rest.pulls.list, {
    owner,
    repo,
    state: "open",
    per_page: 100,
  });
}

function renderSkillEvidencePullRequestComment(result, { formUrl }) {
  if (!result?.relevant) return "";
  const findings = result.findings
    .map((finding) => `- \`${finding.code}\`: ${finding.message}`)
    .join("\n");
  return [
    "## Shared Skill evidence route",
    "",
    "Thanks for contributing a reusable engineering lesson. This PR cannot be accepted as a published Skill in its current form:",
    "",
    findings,
    "",
    `Please submit the evidence through the [Shared Skill evidence form](${formUrl}). The form is accepted immediately and GitHub Actions automatically verifies the exact public commit, workflow run, job, and step without a paid service.`,
    "",
    "A verified evidence record is still non-callable until independent evidence and maintainer publication gates are satisfied.",
    "",
    COMMENT_MARKER,
  ].join("\n");
}

module.exports = {
  COMMENT_MARKER,
  inspectSkillEvidencePullRequest,
  listPullRequestsForReconciliation,
  renderSkillEvidencePullRequestComment,
};
