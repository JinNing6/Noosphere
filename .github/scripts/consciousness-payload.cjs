const START_MARKER = "<!-- CONSCIOUSNESS_PAYLOAD_START -->";
const END_MARKER = "<!-- CONSCIOUSNESS_PAYLOAD_END -->";

function stripJsonFence(block) {
  let normalized = String(block || "").trim();

  if (normalized.startsWith("```json")) {
    normalized = normalized.slice("```json".length).trim();
  } else if (normalized.startsWith("```")) {
    normalized = normalized.slice("```".length).trim();
  }

  if (normalized.endsWith("```")) {
    normalized = normalized.slice(0, -3).trim();
  }

  return normalized;
}

function tryParsePayload(block) {
  const json = stripJsonFence(block);
  if (!json) return null;

  try {
    return JSON.parse(json);
  } catch {
    return null;
  }
}

function extractMarkerPayload(body) {
  const text = String(body || "");
  const startIdx = text.indexOf(START_MARKER);
  const endIdx = text.indexOf(END_MARKER);

  if (startIdx === -1 || endIdx === -1 || endIdx <= startIdx) {
    return null;
  }

  const block = text.slice(startIdx + START_MARKER.length, endIdx);
  const payload = tryParsePayload(block);
  return payload ? { payload, source: "mcp-marker" } : null;
}

function extractPlainHeadingPayload(body) {
  const text = String(body || "");
  const headingPattern = /^#{1,6}\s+(?:.*\s)?Consciousness Payload\b.*$/gim;
  const heading = headingPattern.exec(text);

  if (!heading) return null;

  const afterHeading = text.slice(heading.index + heading[0].length);
  const fence = /```(?:json)?\s*([\s\S]*?)```/i.exec(afterHeading);
  if (!fence) return null;

  const payload = tryParsePayload(fence[1]);
  return payload ? { payload, source: "plain-heading" } : null;
}

function extractConsciousnessPayload(body) {
  return extractMarkerPayload(body) || extractPlainHeadingPayload(body);
}

function getMediaModerationTarget(payload) {
  if (!payload || !["image", "video"].includes(payload.consciousness_type)) {
    return null;
  }

  const mediaUrlKey = payload.consciousness_type === "video" ? "video_url" : "image_url";
  const mediaUrl = payload[mediaUrlKey];
  if (!mediaUrl) return null;

  return {
    mediaType: payload.consciousness_type,
    mediaUrl,
  };
}

module.exports = {
  START_MARKER,
  END_MARKER,
  extractConsciousnessPayload,
  getMediaModerationTarget,
  stripJsonFence,
};
