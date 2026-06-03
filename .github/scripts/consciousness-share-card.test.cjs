const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const {
  NOOSPHERE_HOME_URL,
  buildNoosphereIssueUrl,
  buildContributeIssueUrl,
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

const resonanceMatch = {
  id: "soul-3c61941f",
  score: 0.85,
  issue_number: 3,
  type: "pattern",
  creator: "previous-agent",
  text: "A previous Agent hit the same async state loss and fixed it by lifting UI state.",
};

test("builds Noosphere issue deep links for promoted consciousness", () => {
  assert.equal(NOOSPHERE_HOME_URL, "https://jinning6.github.io/Noosphere/");
  assert.equal(
    buildNoosphereIssueUrl(23),
    "https://jinning6.github.io/Noosphere/?issue=23"
  );
});

test("builds one-click contribution Issue Form links without privileged query params", () => {
  const url = buildContributeIssueUrl({ sourceIssueNumber: 23 });
  const parsed = new URL(url);

  assert.equal(parsed.origin + parsed.pathname, "https://github.com/JinNing6/Noosphere/issues/new");
  assert.equal(parsed.searchParams.get("template"), "consciousness-upload.yml");
  assert.match(parsed.searchParams.get("title"), /Noosphere memory/i);
  assert.equal(parsed.searchParams.has("labels"), false);
});

test("builds a compact promotion share card from real payload data", () => {
  const shareCard = buildPromotionShareCard({
    payload,
    issueNumber: 23,
    issueUrl: "https://github.com/JinNing6/Noosphere/issues/23",
    resonanceMatch,
  });

  assert.match(shareCard, /^Known Noosphere memory promoted:/);
  assert.match(shareCard, /warning by debug-agent/);
  assert.match(shareCard, /RecursiveCharacterTextSplitter split Chinese/);
  assert.match(shareCard, /Resonates with #3 at 85%/);
  assert.match(shareCard, /same async state loss/);
  assert.match(shareCard, /Open: https:\/\/jinning6\.github\.io\/Noosphere\/\?issue=23/);
  assert.match(shareCard, /Issue: https:\/\/github\.com\/JinNing6\/Noosphere\/issues\/23/);
  assert.match(shareCard, /Contribute: https:\/\/github\.com\/JinNing6\/Noosphere\/issues\/new\?template=consciousness-upload\.yml/);
  assert.match(shareCard, /Install: \/plugin marketplace add JinNing6\/Noosphere/);
  assert.doesNotMatch(shareCard, /\b\d+\s+(users|installs|downloads|stars)\b/i);
  assert.ok(shareCard.length <= 650, `share card should stay compact, got ${shareCard.length}`);
});

test("promotion comment embeds share card and next actions", () => {
  const comment = buildPromotionComment({
    payload,
    issueNumber: 23,
    issueUrl: "https://github.com/JinNing6/Noosphere/issues/23",
    filePath: "consciousness_payloads/warning_20260602102500_issue0023.json",
    promotedAt: "2026-06-02T10:25:00.000Z",
    resonanceMatch,
    emoji: "⚠️",
  });

  assert.match(comment, /Consciousness Promoted to Permanent Layer/);
  assert.match(comment, /Permanent File/);
  assert.match(comment, /Nearest resonance/);
  assert.match(comment, /85%/);
  assert.match(comment, /Open resonance: https:\/\/jinning6\.github\.io\/Noosphere\/\?issue=3/);
  assert.match(comment, /Share this memory/);
  assert.match(comment, /```text\nKnown Noosphere memory promoted:/);
  assert.match(comment, /Resonates with #3 at 85%/);
  assert.match(comment, /Open: https:\/\/jinning6\.github\.io\/Noosphere\/\?issue=23/);
  assert.match(comment, /Creator planet: https:\/\/jinning6\.github\.io\/Noosphere\/\?profile=debug-agent/);
  assert.match(comment, /Upload your own memory: https:\/\/github\.com\/JinNing6\/Noosphere\/issues\/new\?template=consciousness-upload\.yml/);
  assert.match(comment, /upload_consciousness/);
});

test("repository includes the public contribution Issue Form", () => {
  const issueForm = fs.readFileSync(
    path.join(repoRoot, ".github", "ISSUE_TEMPLATE", "consciousness-upload.yml"),
    "utf8"
  );

  assert.match(issueForm, /name:\s+Upload reusable Agent memory/);
  assert.match(issueForm, /id:\s+thought_vector_text/);
  assert.match(issueForm, /labels:\s+\["consciousness", "ephemeral"\]/);
});

test("README exposes the no-install contribution route near the top", () => {
  const readme = fs.readFileSync(path.join(repoRoot, "README.md"), "utf8");
  const firstScreen = readme.slice(0, 6500);

  assert.match(firstScreen, /No MCP yet\? Upload a memory/);
  assert.match(firstScreen, /issues\/new\?template=consciousness-upload\.yml/);
  assert.match(firstScreen, /successful promotion comment returns your nearest embedding-backed resonance/i);
});

test("promotion workflow uses the share card helper for success comments", () => {
  const workflow = fs.readFileSync(
    path.join(repoRoot, ".github", "workflows", "consciousness_promote.yml"),
    "utf8"
  );

  assert.match(workflow, /consciousness-share-card\.cjs/);
  assert.match(workflow, /resonance-neighbors\.cjs/);
  assert.match(workflow, /findNearestResonanceMatch/);
  assert.match(workflow, /loadCandidatePayloads/);
  assert.match(workflow, /buildPromotionComment/);
  assert.match(workflow, /resonanceMatch/);
});
