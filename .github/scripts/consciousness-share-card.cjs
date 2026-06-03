const NOOSPHERE_HOME_URL = "https://jinning6.github.io/Noosphere/";
const GITHUB_REPO_URL = "https://github.com/JinNing6/Noosphere";
const CONTRIBUTION_ISSUE_TEMPLATE = "consciousness-upload.yml";
const SHARE_PROOF_ISSUE_TEMPLATE = "share-proof.yml";
const MARKETPLACE_INSTALL_COMMAND = "/plugin marketplace add JinNing6/Noosphere";

function compactLine(value, maxLength) {
  const normalized = String(value || "").replace(/\s+/g, " ").trim();
  if (normalized.length <= maxLength) return normalized;
  return `${normalized.slice(0, Math.max(0, maxLength - 3)).trimEnd()}...`;
}

function safeCreator(payload) {
  if (!payload || payload.is_anonymous) return "Anonymous";
  return compactLine(payload.creator_signature || "unknown", 48);
}

function buildNoosphereIssueUrl(issueNumber, baseUrl = NOOSPHERE_HOME_URL) {
  const parsedIssueNumber = Number.parseInt(String(issueNumber), 10);
  if (!Number.isFinite(parsedIssueNumber) || parsedIssueNumber <= 0) {
    throw new Error(`Invalid issue number: ${issueNumber}`);
  }

  const url = new URL(baseUrl);
  url.searchParams.set("issue", String(parsedIssueNumber));
  return url.toString();
}

function buildCreatorProfileUrl(payload, baseUrl = NOOSPHERE_HOME_URL) {
  if (!payload || payload.is_anonymous || !payload.creator_signature) return null;
  const url = new URL(baseUrl);
  url.searchParams.set("profile", String(payload.creator_signature).trim());
  return url.toString();
}

function buildContributeIssueUrl({ sourceIssueNumber } = {}) {
  const url = new URL(`${GITHUB_REPO_URL}/issues/new`);
  url.searchParams.set("template", CONTRIBUTION_ISSUE_TEMPLATE);

  const parsedIssueNumber = Number.parseInt(String(sourceIssueNumber || ""), 10);
  const suffix = Number.isFinite(parsedIssueNumber) && parsedIssueNumber > 0
    ? ` after reading Noosphere memory #${parsedIssueNumber}`
    : "";
  url.searchParams.set("title", `Upload Noosphere memory${suffix}`);

  return url.toString();
}

function buildShareProofIssueUrl({
  sourceIssueNumber,
  sourceIssueUrl,
  sourceMemory,
  memoryUrl,
  campaignHook,
  shareUrl,
} = {}) {
  const url = new URL(`${GITHUB_REPO_URL}/issues/new`);
  url.searchParams.set("template", SHARE_PROOF_ISSUE_TEMPLATE);

  const parsedIssueNumber = Number.parseInt(String(sourceIssueNumber || ""), 10);
  const hasIssueNumber = Number.isFinite(parsedIssueNumber) && parsedIssueNumber > 0;
  url.searchParams.set(
    "title",
    hasIssueNumber ? `Share proof: Noosphere memory #${parsedIssueNumber}` : "Share proof: Noosphere memory"
  );

  const resolvedMemory =
    sourceMemory ||
    memoryUrl ||
    (hasIssueNumber ? buildNoosphereIssueUrl(parsedIssueNumber) : "") ||
    sourceIssueUrl ||
    "";
  if (resolvedMemory) {
    url.searchParams.set("source_memory", compactLine(resolvedMemory, 180));
  }

  url.searchParams.set(
    "share_context",
    [
      campaignHook || "I shared this Noosphere memory publicly.",
      "Paste the public share URL after posting; Noosphere records reviewable proof only.",
    ].join(" ")
  );

  const normalizedShareUrl = String(shareUrl || "").trim();
  if (/^https?:\/\//i.test(normalizedShareUrl)) {
    url.searchParams.set("share_url", normalizedShareUrl);
  }

  return url.toString();
}

function formatResonancePercent(score) {
  const numericScore = Number.parseFloat(String(score || ""));
  if (!Number.isFinite(numericScore) || numericScore <= 0) return null;
  return `${Math.round(Math.min(1, numericScore) * 100)}%`;
}

function buildResonanceShareLine(resonanceMatch) {
  if (!resonanceMatch) return null;

  const percent = formatResonancePercent(resonanceMatch.score);
  const issueNumber = Number.parseInt(String(resonanceMatch.issue_number || ""), 10);
  if (!percent || !Number.isFinite(issueNumber) || issueNumber <= 0) return null;

  const text = compactLine(resonanceMatch.text || "another Noosphere memory", 88);
  return `Resonates with #${issueNumber} at ${percent}: ${text}`;
}

function buildPromotionShareCard({ payload, issueNumber, issueUrl, resonanceMatch }) {
  const type = compactLine(payload?.consciousness_type || "consciousness", 32);
  const creator = safeCreator(payload);
  const thought = compactLine(payload?.thought_vector_text || "A consciousness fragment joined Noosphere.", 112);
  const resonanceLine = buildResonanceShareLine(resonanceMatch);
  const proofUrl = buildShareProofIssueUrl({
    sourceIssueNumber: issueNumber,
    sourceIssueUrl: issueUrl,
    campaignHook: "I shared this Noosphere memory.",
  });

  const lines = [
    `Known Noosphere memory promoted: ${type} by ${creator}`,
    `Signal: ${thought}`,
  ];
  if (resonanceLine) {
    lines.push(resonanceLine);
  }
  lines.push(
    `Open: ${buildNoosphereIssueUrl(issueNumber)}`,
    `Issue: ${issueUrl}`,
    `Contribute: ${buildContributeIssueUrl({ sourceIssueNumber: issueNumber })}`,
    `Proof: ${proofUrl}`,
    `Install: ${MARKETPLACE_INSTALL_COMMAND}`,
  );

  return lines.join("\n");
}

function buildPromotionResonanceSection(resonanceMatch) {
  const percent = formatResonancePercent(resonanceMatch?.score);
  const issueNumber = Number.parseInt(String(resonanceMatch?.issue_number || ""), 10);
  if (!percent || !Number.isFinite(issueNumber) || issueNumber <= 0) return "";

  const type = compactLine(resonanceMatch.type || "memory", 32);
  const creator = compactLine(resonanceMatch.creator || "Anonymous", 48);
  const text = compactLine(resonanceMatch.text || "another Noosphere memory", 160);

  return (
    `\n### Nearest resonance\n\n` +
    `Your memory resonates ${percent} with #${issueNumber} (${type} by ${creator}): ${text}\n` +
    `- Open resonance: ${buildNoosphereIssueUrl(issueNumber)}\n`
  );
}

function parsePositiveIssueNumber(value, label) {
  const parsed = Number.parseInt(String(value || ""), 10);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    throw new Error(`A valid ${label} issue number is required`);
  }
  return parsed;
}

function buildResonanceBacklinkMarker({ newIssueNumber, matchedIssueNumber }) {
  const parsedNewIssueNumber = parsePositiveIssueNumber(newIssueNumber, "new");
  const parsedMatchedIssueNumber = parsePositiveIssueNumber(matchedIssueNumber, "matched");
  return `<!-- noosphere-resonance-backlink:new=${parsedNewIssueNumber};matched=${parsedMatchedIssueNumber} -->`;
}

function hasResonanceBacklinkComment(comments, { newIssueNumber, matchedIssueNumber }) {
  const marker = buildResonanceBacklinkMarker({ newIssueNumber, matchedIssueNumber });
  if (!Array.isArray(comments)) return false;
  return comments.some((comment) => String(comment?.body || "").includes(marker));
}

function buildResonanceBacklinkComment({
  payload,
  newIssueNumber,
  newIssueUrl,
  resonanceMatch,
}) {
  const percent = formatResonancePercent(resonanceMatch?.score);
  const matchedIssueNumber = Number.parseInt(String(resonanceMatch?.issue_number || ""), 10);
  if (!percent || !Number.isFinite(matchedIssueNumber) || matchedIssueNumber <= 0) {
    throw new Error("A valid resonance match issue number and score are required");
  }

  const parsedNewIssueNumber = parsePositiveIssueNumber(newIssueNumber, "new");
  const marker = buildResonanceBacklinkMarker({
    newIssueNumber: parsedNewIssueNumber,
    matchedIssueNumber,
  });

  const newThought = compactLine(payload?.thought_vector_text || "A new Noosphere memory", 112);
  const matchedThought = compactLine(resonanceMatch.text || "this Noosphere memory", 112);
  const contributeUrl = buildContributeIssueUrl({ sourceIssueNumber: matchedIssueNumber });
  const proofUrl = buildShareProofIssueUrl({
    sourceIssueNumber: parsedNewIssueNumber,
    sourceMemory: `${buildNoosphereIssueUrl(parsedNewIssueNumber)} resonated with ${buildNoosphereIssueUrl(matchedIssueNumber)}`,
    campaignHook: `I shared bridge #${parsedNewIssueNumber} -> #${matchedIssueNumber}.`,
  });

  const shareCard = [
    `Noosphere resonance bridge: #${parsedNewIssueNumber} resonated with #${matchedIssueNumber} at ${percent}`,
    `New: ${newThought}`,
    `Original: ${matchedThought}`,
    `Open new: ${buildNoosphereIssueUrl(parsedNewIssueNumber)}`,
    `Open original: ${buildNoosphereIssueUrl(matchedIssueNumber)}`,
    `Contribute: ${contributeUrl}`,
    `Proof: ${proofUrl}`,
    `Install: ${MARKETPLACE_INSTALL_COMMAND}`,
  ].join("\n");

  return (
    `### New resonance detected\n\n` +
    `A new memory #${parsedNewIssueNumber} resonated ${percent} with this memory #${matchedIssueNumber}.\n\n` +
    `- Open new memory: ${buildNoosphereIssueUrl(parsedNewIssueNumber)}\n` +
    `- Open this memory: ${buildNoosphereIssueUrl(matchedIssueNumber)}\n` +
    `- Source Issue: ${newIssueUrl}\n` +
    `- Continue the chain: ${contributeUrl}\n\n` +
    `- Record proof after sharing this bridge: ${proofUrl}\n\n` +
    `Raw embedding vectors are not exposed; this is a compact nearest-neighbor edge.\n\n` +
    `Share this bridge:\n\n` +
    "```text\n" +
    `${shareCard}\n` +
    "```\n\n" +
    marker
  );
}

function buildPromotionComment({
  payload,
  issueNumber,
  issueUrl,
  filePath,
  promotedAt,
  emoji,
  resonanceMatch,
}) {
  const type = payload?.consciousness_type || "consciousness";
  const shareCard = buildPromotionShareCard({ payload, issueNumber, issueUrl, resonanceMatch });
  const profileUrl = buildCreatorProfileUrl(payload);
  const profileLine = profileUrl ? `\n- Creator planet: ${profileUrl}` : "";
  const contributeUrl = buildContributeIssueUrl({ sourceIssueNumber: issueNumber });
  const proofUrl = buildShareProofIssueUrl({
    sourceIssueNumber: issueNumber,
    sourceIssueUrl: issueUrl,
    campaignHook: "I shared this Noosphere memory.",
  });
  const resonanceSection = buildPromotionResonanceSection(resonanceMatch);

  return (
    `✅ **Consciousness Promoted to Permanent Layer!**\n\n` +
    `Your ${emoji || "🧠"} ${type} thought has been validated and promoted.\n\n` +
    `- 🗂️ **Permanent File**: \`${filePath}\`\n` +
    `- 📅 **Promoted at**: ${promotedAt}\n` +
    `- 🌐 Open in Noosphere: ${buildNoosphereIssueUrl(issueNumber)}` +
    `${profileLine}\n` +
    `- Upload your own memory: ${contributeUrl}\n` +
    `- Record public share proof: ${proofUrl}\n` +
    `${resonanceSection}\n` +
    `### Share this memory\n\n` +
    "```text\n" +
    `${shareCard}\n` +
    "```\n\n" +
    `Next action: open the contribution form above, or install Noosphere with \`${MARKETPLACE_INSTALL_COMMAND}\` and use \`upload_consciousness\` when your Agent solves a reusable failure.\n\n` +
    `Your consciousness now lives permanently in the Noosphere. 🌐`
  );
}

module.exports = {
  CONTRIBUTION_ISSUE_TEMPLATE,
  GITHUB_REPO_URL,
  MARKETPLACE_INSTALL_COMMAND,
  NOOSPHERE_HOME_URL,
  SHARE_PROOF_ISSUE_TEMPLATE,
  buildContributeIssueUrl,
  buildCreatorProfileUrl,
  buildNoosphereIssueUrl,
  buildShareProofIssueUrl,
  buildPromotionComment,
  buildPromotionResonanceSection,
  buildPromotionShareCard,
  buildResonanceBacklinkMarker,
  buildResonanceBacklinkComment,
  hasResonanceBacklinkComment,
  compactLine,
};
