const START_MARKER = "<!-- CONSCIOUSNESS_PAYLOAD_START -->";
const END_MARKER = "<!-- CONSCIOUSNESS_PAYLOAD_END -->";
const SKILL_DOMAIN_TAGS = new Map([
  ["agent runtime", "agent-runtime"],
  ["mcp tools", "mcp-tools"],
  ["build release", "build-release"],
  ["testing reliability", "testing-reliability"],
  ["security trust", "security-trust"],
  ["frontend mobile", "frontend-mobile"],
  ["data infrastructure", "data-infrastructure"],
  ["languages frameworks", "languages-frameworks"],
]);

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

function normalizeLabel(value) {
  return String(value || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function cleanIssueValue(value) {
  const cleaned = String(value || "")
    .replace(/\r/g, "")
    .split("\n")
    .map(line => line.replace(/^>\s?/, ""))
    .join("\n")
    .trim();

  if (!cleaned || /^_?no response_?$/i.test(cleaned)) return "";
  return cleaned;
}

function parseTags(value) {
  const cleaned = cleanIssueValue(value).replace(/^\[/, "").replace(/\]$/, "");
  if (!cleaned) return [];

  return cleaned
    .split(/[,\n]/)
    .map(tag => tag.replace(/[`#]/g, "").trim())
    .filter(Boolean);
}

function parseIssueFormLines(value) {
  const fenced = extractFencedBody(value);
  const cleaned = cleanIssueValue(fenced || value);
  if (!cleaned) return [];
  return [...new Set(cleaned
    .split(/\r?\n/)
    .map((line) => line.replace(/^[-*]\s+/, "").trim())
    .filter(Boolean))];
}

function parseBoolean(value) {
  return /\btrue\b|\byes\b|-\s*\[[xX]\]/i.test(String(value || ""));
}

function parseMarkdownSections(body) {
  const text = String(body || "");
  const headingPattern = /^###\s+(.+?)\s*$/gm;
  const matches = [...text.matchAll(headingPattern)];
  const sections = new Map();

  for (let i = 0; i < matches.length; i += 1) {
    const label = normalizeLabel(matches[i][1]);
    const start = matches[i].index + matches[i][0].length;
    const end = i + 1 < matches.length ? matches[i + 1].index : text.length;
    sections.set(label, text.slice(start, end).trim());
  }

  return sections;
}

function getSection(sections, ...labels) {
  for (const label of labels) {
    const value = sections.get(normalizeLabel(label));
    if (value !== undefined) return cleanIssueValue(value);
  }
  return "";
}

function extractFencedBody(value) {
  const match = /```(?:[a-zA-Z0-9_+.-]+)?[ \t]*\r?\n?([\s\S]*?)```/.exec(String(value || ""));
  return match ? match[1].trim() : "";
}

function parseSimpleMetadata(block) {
  const metadata = {};
  for (const rawLine of String(block || "").split(/\r?\n/)) {
    const line = rawLine.trim();
    const match = /^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$/.exec(line);
    if (!match) continue;
    metadata[match[1]] = match[2].replace(/^['"]|['"]$/g, "").trim();
  }
  return metadata;
}

function normalizeConsciousnessType(value) {
  return cleanIssueValue(value).split(/\s+/)[0].toLowerCase();
}

function withMediaFields(payload, mediaUrl, mediaCategory) {
  if (!mediaUrl) return payload;

  if (payload.consciousness_type === "image") {
    payload.image_url = mediaUrl;
    if (mediaCategory) payload.image_category = mediaCategory;
  } else if (payload.consciousness_type === "video") {
    payload.video_url = mediaUrl;
    if (mediaCategory) payload.video_genre = mediaCategory;
  } else if (payload.consciousness_type === "voice") {
    payload.audio_url = mediaUrl;
    if (mediaCategory) payload.audio_species = mediaCategory;
  }

  return payload;
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

function extractWebUploaderPayload(body) {
  const text = String(body || "");
  if (!/^##\s+Consciousness Upload\b/im.test(text)) return null;

  const sections = parseMarkdownSections(text);
  const metadata = parseSimpleMetadata(extractFencedBody(getSection(sections, "Metadata")));
  const consciousnessType = normalizeConsciousnessType(metadata.type);
  const thought = getSection(sections, "Thought");
  const context = getSection(sections, "Context");
  const creator = cleanIssueValue(metadata.creator);

  if (!creator || !consciousnessType || !thought || !context) return null;

  const payload = {
    creator_signature: creator,
    is_anonymous: parseBoolean(metadata.anonymous),
    consciousness_type: consciousnessType,
    thought_vector_text: thought,
    context_environment: context,
    tags: parseTags(metadata.tags),
  };

  if (metadata.uploaded_at) payload.uploaded_at = metadata.uploaded_at;
  if (metadata.parent_id) payload.parent_id = metadata.parent_id;

  return { payload, source: "web-uploader" };
}

function extractIssueFormPayload(body) {
  const sections = parseMarkdownSections(body);
  const creator = getSection(sections, "Creator signature");
  const consciousnessType = normalizeConsciousnessType(getSection(sections, "Consciousness type"));
  const thought = getSection(sections, "Thought vector text");
  const context = getSection(sections, "Context environment");

  if (!creator || !consciousnessType || !thought || !context) return null;

  const payload = {
    creator_signature: creator,
    is_anonymous: parseBoolean(getSection(sections, "Privacy")),
    consciousness_type: consciousnessType,
    thought_vector_text: thought,
    context_environment: context,
    tags: parseTags(getSection(sections, "Tags")),
  };

  const parentId = getSection(sections, "Parent or source issue");
  if (parentId) payload.parent_id = parentId;

  const mediaUrl = getSection(sections, "Media URL");
  const mediaCategory = getSection(sections, "Media category");
  return { payload: withMediaFields(payload, mediaUrl, mediaCategory), source: "issue-form" };
}

function extractSkillProposalPayload(body) {
  const sections = parseMarkdownSections(body);
  const skillName = getSection(sections, "Skill name").toLowerCase();
  const symptom = getSection(sections, "Reproducible failure symptom");
  const rootCause = getSection(sections, "Root cause");
  const fix = getSection(sections, "Reusable fix");
  const verification = getSection(sections, "Verification evidence");
  const appliesWhen = getSection(sections, "Applies when");

  if (!skillName || !(symptom || rootCause || fix || verification || appliesWhen)) {
    return null;
  }

  const summary = getSection(sections, "What this Skill solves") || fix || symptom;
  const domain = SKILL_DOMAIN_TAGS.get(normalizeLabel(getSection(sections, "Domain branch")));
  const repositoryUrl = getSection(sections, "Source repository URL");
  const commitSha = getSection(sections, "Exact commit SHA");
  const workflowRunUrl = getSection(sections, "Successful workflow run URL");
  const workflowJobName = getSection(sections, "Verification job name");
  const workflowStepName = getSection(sections, "Verification step name");
  const artifactSha256 = getSection(sections, "Artifact SHA-256");

  const payload = {
    schema_version: 4,
    record_kind: "skill-evidence",
    publication_track: "community",
    creator_signature: "github-issue-author",
    consciousness_type: "pattern",
    thought_vector_text: summary,
    context_environment: symptom || appliesWhen || summary,
    tags: [domain, "skill-evidence"].filter(Boolean),
    proposed_skill: skillName,
    evidence: {
      symptom,
      root_cause: rootCause,
      fix,
      verification,
      applies_when: appliesWhen,
      avoid_when: getSection(sections, "Do not apply when"),
      test_commands: parseIssueFormLines(getSection(sections, "Test commands")),
      source_urls: parseIssueFormLines(getSection(sections, "Public evidence URLs")),
    },
    source: {
      repository_url: repositoryUrl,
      commit_sha: commitSha,
      workflow_run_url: workflowRunUrl,
      workflow_job_name: workflowJobName,
      workflow_step_name: workflowStepName,
      artifact_sha256: artifactSha256,
    },
  };

  for (const value of [repositoryUrl, workflowRunUrl]) {
    if (value && !payload.evidence.source_urls.includes(value)) {
      payload.evidence.source_urls.push(value);
    }
  }
  return { payload, source: "skill-proposal-form" };
}

function extractConsciousnessPayload(body) {
  return (
    extractMarkerPayload(body) ||
    extractPlainHeadingPayload(body) ||
    extractWebUploaderPayload(body) ||
    extractSkillProposalPayload(body) ||
    extractIssueFormPayload(body)
  );
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
