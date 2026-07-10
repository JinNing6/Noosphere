function positiveIssueNumber(value) {
  const parsed = Number.parseInt(String(value ?? ""), 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
}

function extractWithdrawalRequest(body) {
  const match = /<!-- WITHDRAWAL_REQUEST_START -->\s*```json\s*([\s\S]*?)\s*```\s*<!-- WITHDRAWAL_REQUEST_END -->/i.exec(
    String(body || ""),
  );
  if (!match) return null;
  try {
    const payload = JSON.parse(match[1]);
    return positiveIssueNumber(payload?.target_issue) ? payload : null;
  } catch {
    return null;
  }
}

function canonicalPromotionPath(payload, issueNumber) {
  const normalizedIssue = positiveIssueNumber(issueNumber);
  if (!normalizedIssue) throw new Error("A positive source Issue number is required");
  return `consciousness_payloads/memory_issue${String(normalizedIssue).padStart(4, "0")}.json`;
}

function findExistingPromotion(records, issueNumber) {
  const normalizedIssue = positiveIssueNumber(issueNumber);
  if (!normalizedIssue || !Array.isArray(records)) return null;

  return records.find((record) => (
    positiveIssueNumber(record?.payload?.promoted_from_issue) === normalizedIssue
  )) || null;
}

function buildTombstoneManifest(manifest, event) {
  const issueNumber = positiveIssueNumber(event?.issueNumber);
  if (!issueNumber) throw new Error("A positive withdrawn Issue number is required");

  const current = manifest && typeof manifest === "object" ? manifest : {};
  const records = Array.isArray(current.withdrawn_issues)
    ? current.withdrawn_issues.filter((item) => positiveIssueNumber(item?.issue_number))
    : [];

  if (records.some((item) => positiveIssueNumber(item.issue_number) === issueNumber)) {
    return { version: 1, withdrawn_issues: records };
  }

  records.push({
    issue_number: issueNumber,
    withdrawn_at: String(event.withdrawnAt || new Date().toISOString()),
    withdrawn_by: String(event.withdrawnBy || "unknown"),
  });
  records.sort((left, right) => left.issue_number - right.issue_number);
  return { version: 1, withdrawn_issues: records };
}

function isIssueTombstoned(manifest, issueNumber) {
  const normalizedIssue = positiveIssueNumber(issueNumber);
  if (!normalizedIssue || !Array.isArray(manifest?.withdrawn_issues)) return false;
  return manifest.withdrawn_issues.some((item) => (
    positiveIssueNumber(item?.issue_number) === normalizedIssue
  ));
}

function promotionCommentMarker(issueNumber) {
  const normalizedIssue = positiveIssueNumber(issueNumber);
  if (!normalizedIssue) throw new Error("A positive source Issue number is required");
  return `<!-- noosphere-promotion:issue-${normalizedIssue} -->`;
}

function hasPromotionComment(comments, issueNumber) {
  const marker = promotionCommentMarker(issueNumber);
  return Array.isArray(comments) && comments.some((comment) => (
    String(comment?.body || "").includes(marker)
  ));
}

module.exports = {
  buildTombstoneManifest,
  canonicalPromotionPath,
  extractWithdrawalRequest,
  findExistingPromotion,
  hasPromotionComment,
  isIssueTombstoned,
  positiveIssueNumber,
  promotionCommentMarker,
};
