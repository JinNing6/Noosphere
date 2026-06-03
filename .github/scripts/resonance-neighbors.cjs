const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");

function compactLine(value, maxLength = 140) {
  const normalized = String(value || "").replace(/\s+/g, " ").trim();
  if (normalized.length <= maxLength) return normalized;
  return `${normalized.slice(0, Math.max(0, maxLength - 3)).trimEnd()}...`;
}

function normalizedEmbedding(value) {
  if (!Array.isArray(value) || value.length === 0) return null;

  const vector = [];
  for (const item of value) {
    if (typeof item !== "number" || !Number.isFinite(item)) return null;
    vector.push(item);
  }

  const norm = Math.sqrt(vector.reduce((sum, item) => sum + item * item, 0));
  return norm > 0 ? vector : null;
}

function cosineSimilarity(left, right) {
  if (!Array.isArray(left) || !Array.isArray(right) || left.length !== right.length) return null;

  let dot = 0;
  let leftNorm = 0;
  let rightNorm = 0;
  for (let index = 0; index < left.length; index += 1) {
    dot += left[index] * right[index];
    leftNorm += left[index] * left[index];
    rightNorm += right[index] * right[index];
  }

  if (leftNorm <= 0 || rightNorm <= 0) return null;
  return dot / (Math.sqrt(leftNorm) * Math.sqrt(rightNorm));
}

function stableSoulId(text) {
  const normalized = compactLine(text, 30000);
  if (!normalized) return null;
  const hash = crypto.createHash("md5").update(normalized).digest("hex").slice(0, 8);
  return `soul-${hash}`;
}

function payloadIssueNumber(payload) {
  const candidates = [
    payload?.promoted_from_issue,
    payload?.issue_number,
    payload?.issueNumber,
  ];

  for (const candidate of candidates) {
    const parsed = Number.parseInt(String(candidate || ""), 10);
    if (Number.isFinite(parsed) && parsed > 0) return parsed;
  }

  return null;
}

function payloadText(payload) {
  return compactLine(payload?.thought_vector_text || payload?.text || "", 160);
}

function payloadCreator(payload) {
  if (!payload || payload.is_anonymous) return "Anonymous";
  return compactLine(payload.creator_signature || payload.creator || "Anonymous", 48);
}

function isSelfMatch(currentPayload, candidatePayload, options = {}) {
  const excludedIssueNumber = Number.parseInt(String(options.excludeIssueNumber || ""), 10);
  const candidateIssueNumber = payloadIssueNumber(candidatePayload);
  if (
    Number.isFinite(excludedIssueNumber) &&
    excludedIssueNumber > 0 &&
    candidateIssueNumber === excludedIssueNumber
  ) {
    return true;
  }

  const currentIssueNumber = payloadIssueNumber(currentPayload);
  if (currentIssueNumber && candidateIssueNumber && currentIssueNumber === candidateIssueNumber) {
    return true;
  }

  const currentText = String(currentPayload?.thought_vector_text || currentPayload?.text || "").trim();
  const candidateText = String(candidatePayload?.thought_vector_text || candidatePayload?.text || "").trim();
  return Boolean(currentText && candidateText && currentText === candidateText);
}

function toResonanceMatch(candidatePayload, score) {
  const text = payloadText(candidatePayload);
  return {
    id: stableSoulId(text) || stableSoulId(JSON.stringify(candidatePayload)) || "soul-unknown",
    score: Math.round(Math.min(1, Math.max(0, score)) * 10000) / 10000,
    issue_number: payloadIssueNumber(candidatePayload),
    type: compactLine(candidatePayload?.consciousness_type || candidatePayload?.type || "memory", 32),
    creator: payloadCreator(candidatePayload),
    text,
  };
}

function findNearestResonanceMatch(currentPayload, candidatePayloads, options = {}) {
  const currentEmbedding = normalizedEmbedding(currentPayload?.embedding);
  if (!currentEmbedding || !Array.isArray(candidatePayloads)) return null;

  let best = null;
  for (const candidatePayload of candidatePayloads) {
    if (isSelfMatch(currentPayload, candidatePayload, options)) continue;

    const candidateEmbedding = normalizedEmbedding(candidatePayload?.embedding);
    if (!candidateEmbedding) continue;

    const score = cosineSimilarity(currentEmbedding, candidateEmbedding);
    if (score === null || score <= 0) continue;

    if (!best || score > best.score) {
      best = toResonanceMatch(candidatePayload, score);
    }
  }

  return best;
}

function loadCandidatePayloads(dir = path.join(process.env.GITHUB_WORKSPACE || process.cwd(), "consciousness_payloads")) {
  let fileNames;
  try {
    fileNames = fs.readdirSync(dir).filter((name) => name.endsWith(".json")).sort();
  } catch {
    return [];
  }

  const payloads = [];
  for (const fileName of fileNames) {
    const filePath = path.join(dir, fileName);
    try {
      payloads.push(JSON.parse(fs.readFileSync(filePath, "utf8")));
    } catch {
      // Ignore corrupt historical payloads; promotion should not block on old data.
    }
  }

  return payloads;
}

module.exports = {
  compactLine,
  cosineSimilarity,
  findNearestResonanceMatch,
  loadCandidatePayloads,
  normalizedEmbedding,
  stableSoulId,
};
