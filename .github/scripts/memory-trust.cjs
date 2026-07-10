const ENGINEERING_MEMORY_TYPES = new Set(["warning", "pattern", "decision"]);
const REQUIRED_EVIDENCE_FIELDS = [
  "symptom",
  "root_cause",
  "fix",
  "verification",
  "applies_when",
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
  const missing = REQUIRED_EVIDENCE_FIELDS.filter((field) => !evidence[field]);
  const publisher = compactText(payload?.publisher?.github_login, 64).toLowerCase();
  const hasPublisher = Boolean(publisher && publisher !== "unknown");
  const isVerified = payload?.trust?.status === "verified";
  const isEngineeringMemory = ENGINEERING_MEMORY_TYPES.has(payload?.consciousness_type);

  return {
    eligible: isEngineeringMemory && isVerified && hasPublisher && missing.length === 0,
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
  isTrustedReviewerPermission,
  normalizeEngineeringEvidence,
};
