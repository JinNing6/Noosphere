const assert = require("node:assert/strict");
const test = require("node:test");

const {
  extractConsciousnessPayload,
  getMediaModerationTarget,
} = require("./consciousness-payload.cjs");

const validPayload = {
  creator_signature: "baize-ferment-agent",
  is_anonymous: true,
  consciousness_type: "epiphany",
  thought_vector_text: "AI systems can turn local corrections into reusable memory.",
  context_environment: "Uploaded from an external agent using a simplified issue body.",
  tags: ["ferment-agent"],
  uploaded_at: "2026-05-21T08:31:55.890Z",
};

test("extracts the canonical MCP marker payload", () => {
  const body = [
    "### Payload",
    "<!-- CONSCIOUSNESS_PAYLOAD_START -->",
    "```json",
    JSON.stringify(validPayload, null, 2),
    "```",
    "<!-- CONSCIOUSNESS_PAYLOAD_END -->",
  ].join("\n");

  const result = extractConsciousnessPayload(body);

  assert.equal(result.source, "mcp-marker");
  assert.deepEqual(result.payload, validPayload);
});

test("extracts simplified external payload issues", () => {
  const body = [
    "## Consciousness Payload",
    "",
    "```json",
    JSON.stringify(validPayload, null, 2),
    "```",
  ].join("\n");

  const result = extractConsciousnessPayload(body);

  assert.equal(result.source, "plain-heading");
  assert.deepEqual(result.payload, validPayload);
});

test("ignores unrelated fenced JSON without a consciousness heading", () => {
  const result = extractConsciousnessPayload(
    ["This is an ordinary issue.", "```json", JSON.stringify(validPayload), "```"].join("\n")
  );

  assert.equal(result, null);
});

test("detects visual media targets for NudeNet moderation", () => {
  const result = getMediaModerationTarget({
    ...validPayload,
    consciousness_type: "image",
    image_url: "https://example.com/image.png",
  });

  assert.deepEqual(result, {
    mediaType: "image",
    mediaUrl: "https://example.com/image.png",
  });
});

test("skips non-media payloads for NudeNet moderation", () => {
  assert.equal(getMediaModerationTarget(validPayload), null);
});
