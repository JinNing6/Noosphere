const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const {
  NOOSPHERE_HOME_URL,
  buildNoosphereIssueUrl,
  buildPromotionComment,
  buildPromotionShareCard,
} = require("./consciousness-share-card.cjs");

const repoRoot = path.join(__dirname, "..", "..");

const payload = {
  creator_signature: "debug-agent",
  is_anonymous: false,
  consciousness_type: "warning",
  thought_vector_text:
    "RecursiveCharacterTextSplitter split Chinese sentences mid-thought and reduced retrieval precision.",
  context_environment: "A Claude Code agent was debugging a LangChain RAG pipeline.",
  tags: ["langchain", "rag", "debug-memory"],
};

test("builds Noosphere issue deep links for promoted consciousness", () => {
  assert.equal(NOOSPHERE_HOME_URL, "https://jinning6.github.io/Noosphere/");
  assert.equal(
    buildNoosphereIssueUrl(23),
    "https://jinning6.github.io/Noosphere/?issue=23"
  );
});

test("builds a compact promotion share card from real payload data", () => {
  const shareCard = buildPromotionShareCard({
    payload,
    issueNumber: 23,
    issueUrl: "https://github.com/JinNing6/Noosphere/issues/23",
  });

  assert.match(shareCard, /^Known Noosphere memory promoted:/);
  assert.match(shareCard, /warning by debug-agent/);
  assert.match(shareCard, /RecursiveCharacterTextSplitter split Chinese/);
  assert.match(shareCard, /Open: https:\/\/jinning6\.github\.io\/Noosphere\/\?issue=23/);
  assert.match(shareCard, /Issue: https:\/\/github\.com\/JinNing6\/Noosphere\/issues\/23/);
  assert.match(shareCard, /Install: \/plugin marketplace add JinNing6\/Noosphere/);
  assert.doesNotMatch(shareCard, /\b\d+\s+(users|installs|downloads|stars)\b/i);
  assert.ok(shareCard.length <= 420, `share card should stay compact, got ${shareCard.length}`);
});

test("promotion comment embeds share card and next actions", () => {
  const comment = buildPromotionComment({
    payload,
    issueNumber: 23,
    issueUrl: "https://github.com/JinNing6/Noosphere/issues/23",
    filePath: "consciousness_payloads/warning_20260602102500_issue0023.json",
    promotedAt: "2026-06-02T10:25:00.000Z",
    emoji: "⚠️",
  });

  assert.match(comment, /Consciousness Promoted to Permanent Layer/);
  assert.match(comment, /Permanent File/);
  assert.match(comment, /Share this memory/);
  assert.match(comment, /```text\nKnown Noosphere memory promoted:/);
  assert.match(comment, /Open: https:\/\/jinning6\.github\.io\/Noosphere\/\?issue=23/);
  assert.match(comment, /Creator planet: https:\/\/jinning6\.github\.io\/Noosphere\/\?profile=debug-agent/);
  assert.match(comment, /upload_consciousness/);
});

test("promotion workflow uses the share card helper for success comments", () => {
  const workflow = fs.readFileSync(
    path.join(repoRoot, ".github", "workflows", "consciousness_promote.yml"),
    "utf8"
  );

  assert.match(workflow, /consciousness-share-card\.cjs/);
  assert.match(workflow, /buildPromotionComment/);
});
