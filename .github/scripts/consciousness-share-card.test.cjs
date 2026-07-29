const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const {
  NOOSPHERE_HOME_URL,
  buildNoosphereIssueUrl,
  buildContributeIssueUrl,
  buildShareProofIssueUrl,
  buildPromotionComment,
  buildPromotionShareCard,
  buildResonanceBacklinkMarker,
  buildResonanceBacklinkComment,
  hasResonanceBacklinkComment,
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

test("builds one-click Share Proof Issue Form links without privileged query params", () => {
  const url = buildShareProofIssueUrl({
    sourceIssueNumber: 23,
    campaignHook: "Shared after a Claude Code Agent reused this debug memory.",
  });
  const parsed = new URL(url);

  assert.equal(parsed.origin + parsed.pathname, "https://github.com/JinNing6/Noosphere/issues/new");
  assert.equal(parsed.searchParams.get("template"), "share-proof.yml");
  assert.equal(parsed.searchParams.get("title"), "Share proof: Noosphere memory #23");
  assert.equal(parsed.searchParams.get("source_memory"), "https://jinning6.github.io/Noosphere/?issue=23");
  assert.match(parsed.searchParams.get("share_context"), /Claude Code Agent reused this debug memory/);
  assert.match(parsed.searchParams.get("share_context"), /public share URL/i);
  assert.equal(parsed.searchParams.has("share_url"), false);
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
  assert.match(shareCard, /Proof: https:\/\/github\.com\/JinNing6\/Noosphere\/issues\/new\?template=share-proof\.yml/);
  assert.match(shareCard, /source_memory=https%3A%2F%2Fjinning6\.github\.io%2FNoosphere%2F%3Fissue%3D23/);
  assert.match(shareCard, /Install: \/plugin marketplace add JinNing6\/Noosphere/);
  assert.doesNotMatch(shareCard, /\b\d+\s+(users|installs|downloads|stars)\b/i);
  assert.ok(shareCard.length <= 950, `share card should stay compact, got ${shareCard.length}`);
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
  assert.match(comment, /Record public share proof: https:\/\/github\.com\/JinNing6\/Noosphere\/issues\/new\?template=share-proof\.yml/);
  assert.match(comment, /upload_consciousness/);
});

test("resonance backlink comment reactivates the matched historical issue", () => {
  const comment = buildResonanceBacklinkComment({
    payload,
    newIssueNumber: 23,
    newIssueUrl: "https://github.com/JinNing6/Noosphere/issues/23",
    resonanceMatch,
  });

  assert.match(comment, /New resonance detected/);
  assert.match(comment, /85%/);
  assert.match(comment, /new memory #23/);
  assert.match(comment, /this memory #3/);
  assert.match(comment, /Open new memory: https:\/\/jinning6\.github\.io\/Noosphere\/\?issue=23/);
  assert.match(comment, /Open this memory: https:\/\/jinning6\.github\.io\/Noosphere\/\?issue=3/);
  assert.match(comment, /Continue the chain: https:\/\/github\.com\/JinNing6\/Noosphere\/issues\/new\?template=consciousness-upload\.yml/);
  assert.match(comment, /Record proof after sharing this bridge: https:\/\/github\.com\/JinNing6\/Noosphere\/issues\/new\?template=share-proof\.yml/);
  assert.match(comment, /```text\nNoosphere resonance bridge:/);
  assert.match(comment, /Proof: https:\/\/github\.com\/JinNing6\/Noosphere\/issues\/new\?template=share-proof\.yml/);
  assert.match(comment, /Install: \/plugin marketplace add JinNing6\/Noosphere/);
  assert.match(comment, /<!-- noosphere-resonance-backlink:new=23;matched=3 -->/);
  assert.doesNotMatch(comment, /\b\d+\s+(users|installs|downloads|stars|referrals)\b/i);
});

test("resonance backlink markers make historical issue comments idempotent", () => {
  const marker = buildResonanceBacklinkMarker({
    newIssueNumber: 23,
    matchedIssueNumber: 3,
  });

  assert.equal(marker, "<!-- noosphere-resonance-backlink:new=23;matched=3 -->");
  assert.equal(
    hasResonanceBacklinkComment(
      [
        { body: "Unrelated comment" },
        { body: `Earlier bridge\n\n${marker}` },
      ],
      { newIssueNumber: 23, matchedIssueNumber: 3 }
    ),
    true
  );
  assert.equal(
    hasResonanceBacklinkComment(
      [{ body: "<!-- noosphere-resonance-backlink:new=22;matched=3 -->" }],
      { newIssueNumber: 23, matchedIssueNumber: 3 }
    ),
    false
  );
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

test("README separates no-install engineering evidence from consciousness near the top", () => {
  const readme = fs.readFileSync(path.join(repoRoot, "README.md"), "utf8");
  const firstScreen = readme.slice(0, 6500);

  assert.match(firstScreen, /issues\/new\?template=skill-proposal\.yml/);
  assert.match(firstScreen, /issues\/new\?template=validate-skill\.yml/);
  assert.match(firstScreen, /issues\/new\?template=consciousness-upload\.yml/);
  assert.match(firstScreen, /not engineering Skill authority/i);
  assert.match(firstScreen, /successful consciousness promotion comment returns the nearest\s+embedding-backed resonance/i);
  assert.match(firstScreen, /matched historical Issue gets a backlink comment/i);
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
  assert.match(workflow, /buildResonanceBacklinkComment/);
  assert.match(workflow, /hasResonanceBacklinkComment/);
  assert.match(workflow, /github\.rest\.issues\.listComments/);
  assert.match(workflow, /resonanceMatch/);
  assert.match(workflow, /issue_number: resonanceMatch\.issue_number/);
});
