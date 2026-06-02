const NOOSPHERE_HOME_URL = "https://jinning6.github.io/Noosphere/";
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

function buildPromotionShareCard({ payload, issueNumber, issueUrl }) {
  const type = compactLine(payload?.consciousness_type || "consciousness", 32);
  const creator = safeCreator(payload);
  const thought = compactLine(payload?.thought_vector_text || "A consciousness fragment joined Noosphere.", 112);

  return [
    `Known Noosphere memory promoted: ${type} by ${creator}`,
    `Signal: ${thought}`,
    `Open: ${buildNoosphereIssueUrl(issueNumber)}`,
    `Issue: ${issueUrl}`,
    `Install: ${MARKETPLACE_INSTALL_COMMAND}`,
  ].join("\n");
}

function buildPromotionComment({
  payload,
  issueNumber,
  issueUrl,
  filePath,
  promotedAt,
  emoji,
}) {
  const type = payload?.consciousness_type || "consciousness";
  const shareCard = buildPromotionShareCard({ payload, issueNumber, issueUrl });
  const profileUrl = buildCreatorProfileUrl(payload);
  const profileLine = profileUrl ? `\n- Creator planet: ${profileUrl}` : "";

  return (
    `✅ **Consciousness Promoted to Permanent Layer!**\n\n` +
    `Your ${emoji || "🧠"} ${type} thought has been validated and promoted.\n\n` +
    `- 🗂️ **Permanent File**: \`${filePath}\`\n` +
    `- 📅 **Promoted at**: ${promotedAt}\n` +
    `- 🌐 Open in Noosphere: ${buildNoosphereIssueUrl(issueNumber)}` +
    `${profileLine}\n\n` +
    `### Share this memory\n\n` +
    "```text\n" +
    `${shareCard}\n` +
    "```\n\n" +
    `Next action: install Noosphere with \`${MARKETPLACE_INSTALL_COMMAND}\`, then use \`upload_consciousness\` when your Agent solves a reusable failure.\n\n` +
    `Your consciousness now lives permanently in the Noosphere. 🌐`
  );
}

module.exports = {
  MARKETPLACE_INSTALL_COMMAND,
  NOOSPHERE_HOME_URL,
  buildCreatorProfileUrl,
  buildNoosphereIssueUrl,
  buildPromotionComment,
  buildPromotionShareCard,
  compactLine,
};
