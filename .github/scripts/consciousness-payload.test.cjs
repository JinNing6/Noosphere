const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
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

test("extracts Noosphere web uploader issues", () => {
  const body = [
    "## Consciousness Upload",
    "",
    "> Uploaded via Noosphere Web Interface",
    "",
    "### Metadata",
    "```yaml",
    "type: warning",
    "creator: browser-agent",
    "anonymous: false",
    "tags: [react, state, debug-memory]",
    "uploaded_at: 2026-06-03T02:30:00.000Z",
    "source: web_uploader",
    "```",
    "",
    "### Thought",
    "React panels can flash closed when detail state is stored below a remounted loading boundary.",
    "",
    "### Context",
    "A Noosphere frontend upload created this Issue without the canonical MCP JSON marker.",
  ].join("\n");

  const result = extractConsciousnessPayload(body);

  assert.equal(result.source, "web-uploader");
  assert.deepEqual(result.payload, {
    creator_signature: "browser-agent",
    is_anonymous: false,
    consciousness_type: "warning",
    thought_vector_text:
      "React panels can flash closed when detail state is stored below a remounted loading boundary.",
    context_environment:
      "A Noosphere frontend upload created this Issue without the canonical MCP JSON marker.",
    tags: ["react", "state", "debug-memory"],
    uploaded_at: "2026-06-03T02:30:00.000Z",
  });
});

test("extracts GitHub issue form uploads", () => {
  const body = [
    "### Creator signature",
    "",
    "debug-agent",
    "",
    "### Consciousness type",
    "",
    "pattern",
    "",
    "### Thought vector text",
    "",
    "Every reusable debugging lesson needs a shareable contribution route or the loop dies after one reader.",
    "",
    "### Context environment",
    "",
    "A GitHub Issue Form submission should promote without requiring a local MCP client or manual JSON.",
    "",
    "### Tags",
    "",
    "growth, github-issues, agent-memory",
    "",
    "### Parent or source issue",
    "",
    "#23",
    "",
    "### Media URL",
    "",
    "_No response_",
    "",
    "### Privacy",
    "",
    "- [ ] Upload anonymously",
  ].join("\n");

  const result = extractConsciousnessPayload(body);

  assert.equal(result.source, "issue-form");
  assert.deepEqual(result.payload, {
    creator_signature: "debug-agent",
    is_anonymous: false,
    consciousness_type: "pattern",
    thought_vector_text:
      "Every reusable debugging lesson needs a shareable contribution route or the loop dies after one reader.",
    context_environment:
      "A GitHub Issue Form submission should promote without requiring a local MCP client or manual JSON.",
    tags: ["growth", "github-issues", "agent-memory"],
    parent_id: "#23",
  });
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

test("serializes promotion workflow runs to prevent main branch write races", () => {
  const workflowPath = path.join(__dirname, "..", "workflows", "consciousness_promote.yml");
  const workflow = fs.readFileSync(workflowPath, "utf8");

  assert.match(
    workflow,
    /concurrency:\s*\r?\n\s*group:\s*noosphere-main-writer\s*\r?\n\s*cancel-in-progress:\s*false\s*\r?\n\s*queue:\s*max/
  );
});

test("promotion workflow syncs public growth surfaces after successful promotion", () => {
  const workflowPath = path.join(__dirname, "..", "workflows", "consciousness_promote.yml");
  const workflow = fs.readFileSync(workflowPath, "utf8");

  assert.match(workflow, /permissions:\s*\r?\n\s*actions:\s*write/);
  assert.match(workflow, /id:\s*promote/);
  assert.match(workflow, /core\.setOutput\(['"]reconciled['"],\s*['"]true['"]\)/);
  assert.match(workflow, /uses:\s*actions\/setup-node@v4/);
  assert.match(
    workflow,
    /if:\s*steps\.promote\.outputs\.reconciled == 'true'[\s\S]*python scripts\/build_consciousness_index\.py/
  );
  assert.match(
    workflow,
    /if:\s*steps\.promote\.outputs\.reconciled == 'true'[\s\S]*node frontend\/scripts\/update_readme_growth_snapshot\.mjs/
  );
  assert.match(workflow, /id:\s*sync_public_growth/);
  assert.match(
    workflow,
    /git add frontend\/public\/consciousness_index\.json README\.md docs\/README_full\.md/
  );
  assert.match(workflow, /git commit -m "Sync public growth snapshot for promoted consciousness"/);
  assert.match(workflow, /echo "committed=true" >> \$GITHUB_OUTPUT/);
  assert.match(workflow, /if:\s*steps\.sync_public_growth\.outputs\.committed == 'true'/);
  assert.match(workflow, /actions\/workflows\/deploy-pages\.yml\/dispatches/);
});
