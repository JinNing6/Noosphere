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
    return url.protocol === "https:" && !url.username && !url.password && !sensitiveQuery;
  } catch {
    return false;
  }
}

function buildModerationText(payload) {
  const evidence = normalizeEngineeringEvidence(payload?.evidence);
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
  ]
    .filter(([, value]) => value)
    .map(([label, value]) => `${label}: ${value}`)
    .join("\n");
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
  const publisher = compactText(payload?.publisher?.github_login, 64).toLowerCase();
  const hasPublisher = Boolean(publisher && publisher !== "unknown");
  const isVerified = payload?.trust?.status === "verified";
  const isScreened = payload?.trust?.status === "screened" && payload?.content_safety?.status === "passed";
  const isEngineeringMemory = ENGINEERING_MEMORY_TYPES.has(payload?.consciousness_type);

  return {
    eligible: isEngineeringMemory && (isVerified || isScreened) && hasPublisher && missing.length === 0,
    missing,
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
};
