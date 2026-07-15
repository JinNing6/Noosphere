const OUTCOME_START = "<!-- SKILL_OUTCOME_START -->";
const OUTCOME_END = "<!-- SKILL_OUTCOME_END -->";
const OUTCOMES = new Set(["success", "partial", "failure"]);

function extractSkillOutcome(body) {
  const pattern = new RegExp(`${OUTCOME_START}\\s*\\x60\\x60\\x60json\\s*([\\s\\S]*?)\\s*\\x60\\x60\\x60\\s*${OUTCOME_END}`);
  const match = pattern.exec(String(body || ""));
  if (!match) return null;
  try {
    return JSON.parse(match[1]);
  } catch {
    return null;
  }
}

function publicUrl(value) {
  try {
    const url = new URL(String(value || ""));
    const sensitiveQuery = [...url.searchParams.keys()].some((key) => (
      /(?:token|secret|signature|credential|auth|api[_-]?key)/i.test(key)
    ));
    return url.protocol === "https:" && !url.username && !url.password && !sensitiveQuery;
  } catch {
    return false;
  }
}

function findRelease(registry, payload) {
  const skill = (registry?.skills || []).find((entry) => entry.name === payload?.skill_name);
  const release = (skill?.releases || []).find((entry) => entry.version === payload?.skill_version);
  return { skill, release };
}

function validateSkillOutcome(payload, registry) {
  const errors = [];
  if (payload?.schema_version !== "1.0") errors.push("invalid outcome schema_version");
  if (!/^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/.test(String(payload?.outcome_id || ""))) {
    errors.push("invalid outcome_id");
  }
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(String(payload?.skill_name || ""))) {
    errors.push("invalid Skill name");
  }
  if (!/^\d+\.\d+\.\d+$/.test(String(payload?.skill_version || ""))) {
    errors.push("invalid Skill version");
  }
  if (!/^[a-f0-9]{64}$/.test(String(payload?.skill_sha256 || ""))) {
    errors.push("invalid Skill digest");
  }
  if (!OUTCOMES.has(payload?.outcome)) errors.push("invalid outcome value");
  const taskSummary = String(payload?.task_summary || "").trim();
  const verificationSummary = String(payload?.verification_summary || "").trim();
  if (!taskSummary || taskSummary.length > 2000) errors.push("task_summary must contain 1-2000 characters");
  if (!verificationSummary || verificationSummary.length > 4000) {
    errors.push("verification_summary must contain 1-4000 characters");
  }
  if (
    !Array.isArray(payload?.evidence_urls) || payload.evidence_urls.length > 10 ||
    !payload.evidence_urls.every((value) => typeof value === "string" && publicUrl(value))
  ) {
    errors.push("evidence_urls must contain only public HTTPS URLs");
  }
  const { skill, release } = findRelease(registry, payload);
  if (!skill || !release) errors.push("the referenced Skill release does not exist");
  else {
    if (release.status !== "active") errors.push("the referenced Skill release is not active");
    if (release.artifact?.sha256 !== payload.skill_sha256) errors.push("the Skill digest does not match the registry");
  }
  return { valid: errors.length === 0, errors, skill, release };
}

function stableOutcomeValue(payload) {
  return JSON.stringify({
    outcome_id: payload.outcome_id,
    skill_name: payload.skill_name,
    skill_version: payload.skill_version,
    skill_sha256: payload.skill_sha256,
    outcome: payload.outcome,
    task_summary: String(payload.task_summary).trim(),
    verification_summary: String(payload.verification_summary).trim(),
    evidence_urls: [...payload.evidence_urls].sort(),
  });
}

function recordApprovedSkillOutcome(registryInput, ledgerInput, payload, issue, options) {
  const registry = structuredClone(registryInput || {});
  const ledger = structuredClone(ledgerInput || { schema_version: "1.0", outcomes: [] });
  ledger.schema_version = "1.0";
  ledger.outcomes = Array.isArray(ledger.outcomes) ? ledger.outcomes : [];
  const validation = validateSkillOutcome(payload, registry);
  if (!validation.valid) throw new Error(validation.errors.join("; "));
  const reporter = String(issue?.user?.login || "").trim();
  if (!reporter) throw new Error("Outcome Issue must have an authenticated GitHub author");

  const existing = ledger.outcomes.find((entry) => entry.outcome_id === payload.outcome_id);
  if (existing) {
    if (stableOutcomeValue(existing) !== stableOutcomeValue(payload)) {
      throw new Error(`outcome_id ${payload.outcome_id} is already bound to different evidence`);
    }
    return { idempotent: true, registry, ledger, record: existing, updateNeeded: existing.outcome !== "success" };
  }

  const record = {
    ...JSON.parse(stableOutcomeValue(payload)),
    reporter,
    issue_number: Number(issue.number),
    issue_url: String(issue.html_url || ""),
    approved_by: String(options.reviewer),
    approved_at: String(options.approvedAt),
  };
  ledger.outcomes.push(record);
  ledger.outcomes.sort((left, right) => left.outcome_id.localeCompare(right.outcome_id));
  ledger.generated_at = options.approvedAt;

  const { skill, release } = findRelease(registry, payload);
  release.verification = release.verification || {};
  const releaseOutcomes = ledger.outcomes.filter((entry) => (
    entry.skill_name === payload.skill_name && entry.skill_version === payload.skill_version &&
    entry.skill_sha256 === payload.skill_sha256
  ));
  const successes = releaseOutcomes.filter((entry) => entry.outcome === "success");
  const failures = releaseOutcomes.filter((entry) => entry.outcome !== "success");
  release.verification.verified_outcomes = successes.length;
  release.verification.failed_outcomes = failures.length;
  release.verification.update_needed = failures.length > 0;
  const authors = new Set([
    ...(skill.originators || []),
    ...(release.provenance?.authors || []),
    release.provenance?.author,
  ].filter(Boolean).map((value) => String(value).toLowerCase()));
  const hasIndependentSuccess = successes.some((entry) => (
    !authors.has(entry.reporter.toLowerCase()) &&
    Array.isArray(entry.evidence_urls) &&
    entry.evidence_urls.length > 0
  ));
  if (hasIndependentSuccess && release.verification.level === "independently-reproduced") {
    release.verification.level = "outcome-proven";
  }
  registry.revision = Number(registry.revision || 0) + 1;
  registry.generated_at = options.approvedAt;
  return { idempotent: false, registry, ledger, record, updateNeeded: payload.outcome !== "success" };
}

module.exports = {
  OUTCOME_END,
  OUTCOME_START,
  extractSkillOutcome,
  recordApprovedSkillOutcome,
  validateSkillOutcome,
};
