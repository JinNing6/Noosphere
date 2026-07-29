const ENGINEERING_MEMORY_TYPES = new Set(["warning", "pattern", "decision"]);
const REQUIRED_EVIDENCE_FIELDS = [
  "symptom",
  "root_cause",
  "fix",
  "verification",
  "applies_when",
  "test_commands",
  "source_urls",
];
const TRUSTED_REVIEWER_PERMISSIONS = new Set(["admin", "maintain", "write"]);
const { validateEvidenceSource } = require("./evidence-provenance.cjs");
const DETERMINISTIC_RISK_PATTERNS = [
  ["private-key", /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/i],
  ["github-token", /\bgh[pousr]_[A-Za-z0-9]{20,}\b/],
  ["aws-access-key", /\bAKIA[0-9A-Z]{16}\b/],
  ["credential-assignment", /\b(?:api[_-]?key|access[_-]?token|password|client[_-]?secret)\s*[:=]\s*["']?[A-Za-z0-9_./+=-]{12,}/i],
  ["instruction-override", /\b(?:ignore|disregard|override)\b.{0,40}\b(?:previous|prior|system|developer)\b.{0,24}\binstructions?\b/is],
  ["secret-exfiltration", /\b(?:exfiltrat(?:e|ion)|reveal|upload|send)\b.{0,50}\b(?:secret|credential|token|private key|environment variable)s?\b/is],
  ["remote-shell-pipe", /\b(?:curl|wget)\b[^\n|]{0,300}\|\s*(?:sudo\s+)?(?:ba|z|k)?sh\b/i],
  ["encoded-powershell", /\bpowershell(?:\.exe)?\b[^\n]{0,120}\s-(?:enc|encodedcommand)\b/i],
  ["expression-execution", /\b(?:invoke-expression|iex)\b/i],
  ["destructive-root-delete", /\brm\s+-[a-z]*r[a-z]*f[a-z]*\s+(?:--\s+)?(?:\/|~|\$HOME)\b/i],
];

function compactText(value, maxLength = 4000) {
  return String(value || "").replace(/\r/g, "").trim().slice(0, maxLength);
}

function normalizeStringList(value, maxItems = 12, maxLength = 500) {
  if (!Array.isArray(value)) return [];
  return [...new Set(value.map((item) => compactText(item, maxLength)).filter(Boolean))]
    .slice(0, maxItems);
}

function normalizeEngineeringEvidence(value) {
  const evidence = value && typeof value === "object" ? value : {};
  return {
    symptom: compactText(evidence.symptom),
    root_cause: compactText(evidence.root_cause),
    fix: compactText(evidence.fix),
    verification: compactText(evidence.verification),
    applies_when: compactText(evidence.applies_when),
    avoid_when: compactText(evidence.avoid_when),
    test_commands: normalizeStringList(evidence.test_commands),
    source_urls: normalizeStringList(evidence.source_urls),
  };
}

function isPublicEvidenceUrl(value) {
  try {
    const url = new URL(String(value || ""));
    const sensitiveQuery = [...url.searchParams.keys()].some((key) => (
      /(?:token|secret|signature|credential|auth|api[_-]?key)/i.test(key)
    ));
    const sensitiveFragment = /(?:token|secret|signature|credential|auth|api[_-]?key)\s*=/i.test(
      decodeURIComponent(url.hash || ""),
    );
    return url.protocol === "https:" && !url.username && !url.password &&
      !sensitiveQuery && !sensitiveFragment;
  } catch {
    return false;
  }
}

function buildModerationText(payload) {
  const evidence = normalizeEngineeringEvidence(payload?.evidence);
  const source = payload?.source && typeof payload.source === "object" ? payload.source : {};
  return [
    ["thought", compactText(payload?.thought_vector_text)],
    ["context", compactText(payload?.context_environment)],
    ["symptom", evidence.symptom],
    ["root_cause", evidence.root_cause],
    ["fix", evidence.fix],
    ["verification", evidence.verification],
    ["applies_when", evidence.applies_when],
    ["avoid_when", evidence.avoid_when],
    ["test_commands", evidence.test_commands.join("\n")],
    ["source_urls", evidence.source_urls.join("\n")],
    ["source_repository", compactText(source.repository_url, 500)],
    ["source_commit", compactText(source.commit_sha, 100)],
    ["workflow_run", compactText(source.workflow_run_url, 500)],
    ["workflow_job", compactText(source.workflow_job_name, 200)],
    ["workflow_step", compactText(source.workflow_step_name, 200)],
    ["artifact_sha256", compactText(source.artifact_sha256, 100)],
  ]
    .filter(([, value]) => value)
    .map(([label, value]) => `${label}: ${value}`)
    .join("\n");
}

function screenSkillEvidenceDeterministically(payload) {
  const text = buildModerationText(payload);
  const findings = DETERMINISTIC_RISK_PATTERNS
    .filter(([, pattern]) => pattern.test(text))
    .map(([code]) => code);
  return {
    status: findings.length ? "rejected" : "passed",
    method: "deterministic-policy-v1",
    findings,
  };
}

function bindVerifiedPublisher(payload, issue) {
  return {
    ...payload,
    publisher: {
      github_login: compactText(issue?.user?.login, 64),
      issue_author_association: compactText(issue?.author_association, 32) || "NONE",
      source_issue: Number.parseInt(String(issue?.number || ""), 10),
    },
  };
}

function assessSkillEligibility(payload) {
  const evidence = normalizeEngineeringEvidence(payload?.evidence);
  const missing = REQUIRED_EVIDENCE_FIELDS.filter((field) => (
    Array.isArray(evidence[field]) ? evidence[field].length === 0 : !evidence[field]
  ));
  if (evidence.source_urls.length && !evidence.source_urls.every(isPublicEvidenceUrl)) {
    missing.push("public_https_source_urls");
  }
  if (Number(payload?.schema_version || 0) >= 4) {
    const sourceAssessment = validateEvidenceSource(payload?.source);
    missing.push(...sourceAssessment.missing);
    const skillIdentity = compactText(payload?.target_skill || payload?.proposed_skill, 100);
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(skillIdentity) || skillIdentity.length > 64) {
      missing.push("proposed_skill_or_target_skill");
    }
    if (payload?.machine_verification?.status !== "workflow-verified") {
      missing.push("machine_verification.workflow-verified");
    }
  }
  const publisher = compactText(payload?.publisher?.github_login, 64).toLowerCase();
  const hasPublisher = Boolean(publisher && publisher !== "unknown");
  const isVerified = payload?.trust?.status === "verified";
  const isScreened = payload?.trust?.status === "screened" && payload?.content_safety?.status === "passed";
  const isEngineeringMemory = ENGINEERING_MEMORY_TYPES.has(payload?.consciousness_type);

  return {
    eligible: isEngineeringMemory && (isVerified || isScreened) && hasPublisher && missing.length === 0,
    missing: [...new Set(missing)],
  };
}

function isTrustedReviewerPermission(permission) {
  return TRUSTED_REVIEWER_PERMISSIONS.has(String(permission || "").toLowerCase());
}

module.exports = {
  ENGINEERING_MEMORY_TYPES,
  REQUIRED_EVIDENCE_FIELDS,
  assessSkillEligibility,
  bindVerifiedPublisher,
  buildModerationText,
  isPublicEvidenceUrl,
  isTrustedReviewerPermission,
  normalizeEngineeringEvidence,
  screenSkillEvidenceDeterministically,
};
