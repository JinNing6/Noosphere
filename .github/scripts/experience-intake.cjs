const fs = require("node:fs");
const path = require("node:path");

const {
  verifyEvidenceProvenance,
} = require("./evidence-provenance.cjs");

const COMMENT_MARKER = "<!-- noosphere-experience-agent -->";
const MAX_RECORD_BYTES = 64 * 1024;
const EXPERIENCE_ID = /^exp-[a-z0-9]+(?:-[a-z0-9]+)*-[0-9]{8}$/;
const GITHUB_LOGIN = /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$/;
const GITHUB_REPOSITORY = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;

const SECRET_PATTERNS = [
  /\bgh[oprsu]_[A-Za-z0-9_]{20,}\b/,
  /\bgithub_pat_[A-Za-z0-9_]{20,}\b/,
  /\b(?:sk|xox[baprs])-[A-Za-z0-9-]{20,}\b/,
  /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/,
];
const OVERRIDE_PATTERNS = [
  /\b(?:ignore|disregard|override)\b.{0,80}\b(?:previous|system|developer|safety)\b.{0,60}\binstructions?\b/is,
  /\b(?:system|developer)\s+prompt\b/i,
  /\b(?:exfiltrate|leak|reveal)\b.{0,80}\b(?:secret|credential|token|private key)\b/is,
];
const UNSAFE_RESOLUTION_PATTERNS = [
  /\b(?:curl|wget)\b[^\n|]{0,500}\|\s*(?:ba)?sh\b/i,
  /\brm\s+-rf\s+(?:\/|~|\$HOME)(?:\s|$)/i,
  /\b(?:powershell|pwsh)\b[^\n]{0,200}\b(?:-enc|-encodedcommand)\b/i,
  /\bRemove-Item\b[^\n]{0,300}\b-Recurse\b[^\n]{0,300}\b-Force\b[^\n]{0,100}(?:\$HOME|~|[A-Za-z]:\\)/i,
];

function cleanIssueValue(value) {
  const cleaned = String(value || "").replace(/\r/g, "").trim();
  if (!cleaned || /^_?no response_?$/i.test(cleaned)) return "";
  return cleaned;
}

function normalizeLabel(value) {
  return String(value || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function parseMarkdownSections(body) {
  const text = String(body || "");
  const matches = [...text.matchAll(/^###\s+(.+?)\s*$/gm)];
  const sections = new Map();
  for (let index = 0; index < matches.length; index += 1) {
    const start = matches[index].index + matches[index][0].length;
    const end = index + 1 < matches.length ? matches[index + 1].index : text.length;
    sections.set(normalizeLabel(matches[index][1]), cleanIssueValue(text.slice(start, end)));
  }
  return sections;
}

function extractFencedJson(value) {
  const text = cleanIssueValue(value);
  const fence = /```(?:json)?[ \t]*\n([\s\S]*?)```/i.exec(text);
  return cleanIssueValue(fence ? fence[1] : text);
}

function finding(code, message) {
  return { code, message };
}

function extractExperienceIssue(body) {
  const sections = parseMarkdownSections(body);
  const value = sections.get(normalizeLabel("Experience record JSON"));
  if (value === undefined) {
    return { relevant: false, record: null, findings: [] };
  }
  const payload = extractFencedJson(value);
  if (!payload) {
    return {
      relevant: true,
      record: null,
      findings: [finding("EXPERIENCE_JSON_MISSING", "The Experience record JSON field is empty.")],
    };
  }
  const declaration = sections.get(normalizeLabel("Public submission declaration")) || "";
  const checkedDeclarations = declaration.match(/-\s*\[[xX]\]/g) || [];
  if (checkedDeclarations.length < 3) {
    return {
      relevant: true,
      record: null,
      findings: [finding(
        "EXPERIENCE_PUBLIC_CONSENT_MISSING",
        "All real-case, redaction, and public identity declarations must remain checked.",
      )],
    };
  }
  if (Buffer.byteLength(payload, "utf8") > MAX_RECORD_BYTES) {
    return {
      relevant: true,
      record: null,
      findings: [finding("EXPERIENCE_TOO_LARGE", `The record exceeds ${MAX_RECORD_BYTES} bytes.`)],
    };
  }
  try {
    const record = JSON.parse(payload);
    return { relevant: true, record, findings: [] };
  } catch {
    return {
      relevant: true,
      record: null,
      findings: [finding("EXPERIENCE_JSON_INVALID", "The Experience record field is not valid JSON.")],
    };
  }
}

function sourceIssueIdentity(issue, repository) {
  const login = String(issue?.user?.login || "").trim();
  const number = Number(issue?.number);
  const url = String(issue?.html_url || "").trim();
  if (!GITHUB_LOGIN.test(login)) {
    throw new Error("The authenticated GitHub Issue author is missing or invalid.");
  }
  if (!GITHUB_REPOSITORY.test(String(repository || ""))) {
    throw new Error("The repository identity is missing or invalid.");
  }
  if (!Number.isInteger(number) || number < 1) {
    throw new Error("The GitHub Issue number is missing or invalid.");
  }
  const expectedUrl = `https://github.com/${repository}/issues/${number}`;
  if (url !== expectedUrl) {
    throw new Error("The GitHub Issue URL does not match the repository and Issue number.");
  }
  return {
    provider: "github",
    repository,
    issue_number: number,
    url,
    author_ref: `github:${login.toLowerCase()}`,
  };
}

function serializedRecord(record) {
  try {
    return JSON.stringify(record);
  } catch {
    return "";
  }
}

function screenExperienceRecord(record) {
  const findings = [];
  if (!record || typeof record !== "object" || Array.isArray(record)) {
    return [finding("EXPERIENCE_OBJECT_REQUIRED", "The Experience record must be a JSON object.")];
  }
  const serialized = serializedRecord(record);
  if (!serialized) {
    return [finding("EXPERIENCE_NOT_SERIALIZABLE", "The Experience record cannot be serialized.")];
  }
  if (Buffer.byteLength(serialized, "utf8") > MAX_RECORD_BYTES) {
    findings.push(finding("EXPERIENCE_TOO_LARGE", `The canonical record exceeds ${MAX_RECORD_BYTES} bytes.`));
  }
  if (record.schema_version !== "0.1" || record.record_kind !== "experience") {
    findings.push(finding("EXPERIENCE_PROTOCOL_MISMATCH", "schema_version must be 0.1 and record_kind must be experience."));
  }
  if (!EXPERIENCE_ID.test(String(record.experience_id || ""))) {
    findings.push(finding("EXPERIENCE_ID_INVALID", "experience_id must use exp-<slug>-<YYYYMMDD>."));
  }
  if (record?.lifecycle?.status !== "candidate") {
    findings.push(finding("EXPERIENCE_LIFECYCLE_INVALID", "Automated intake accepts candidate records only."));
  }
  if (record?.review?.status !== "pending") {
    findings.push(finding("EXPERIENCE_REVIEW_INVALID", "Submitted records must leave the review decision pending for the Experience Agent."));
  }
  if (!["applied", "not-required"].includes(record?.redaction?.status)) {
    findings.push(finding("EXPERIENCE_REDACTION_INCOMPLETE", "Redaction must be applied or explicitly not required."));
  }
  for (const pattern of SECRET_PATTERNS) {
    if (pattern.test(serialized)) {
      findings.push(finding("EXPERIENCE_SECRET_DETECTED", "Credential-shaped content is not accepted."));
      break;
    }
  }
  for (const pattern of OVERRIDE_PATTERNS) {
    if (pattern.test(serialized)) {
      findings.push(finding("EXPERIENCE_INSTRUCTION_OVERRIDE", "Instruction-override or credential-exfiltration language is not accepted."));
      break;
    }
  }
  const resolutionSteps = Array.isArray(record?.resolution?.steps)
    ? record.resolution.steps.join("\n")
    : "";
  for (const pattern of UNSAFE_RESOLUTION_PATTERNS) {
    if (pattern.test(resolutionSteps)) {
      findings.push(finding("EXPERIENCE_UNSAFE_RESOLUTION", "The proposed resolution contains an unsafe command pattern."));
      break;
    }
  }
  return findings;
}

function loadExperienceRecords(repositoryRoot) {
  const records = [];
  for (const directory of ["candidates", "reviewed"]) {
    const root = path.join(repositoryRoot, "experience_records", directory);
    if (!fs.existsSync(root)) continue;
    for (const name of fs.readdirSync(root).sort()) {
      if (!name.endsWith(".json")) continue;
      const recordPath = path.join(root, name);
      const stats = fs.lstatSync(recordPath);
      if (stats.isSymbolicLink() || !stats.isFile() || stats.size > MAX_RECORD_BYTES) continue;
      try {
        records.push({
          path: path.posix.join("experience_records", directory, name),
          record: JSON.parse(fs.readFileSync(recordPath, "utf8")),
        });
      } catch {
        // The canonical Python validator reports malformed tracked records.
      }
    }
  }
  return records;
}

function sameSourceIssue(record, sourceIssue) {
  const candidate = record?.provenance?.source_issue;
  return candidate?.provider === "github"
    && String(candidate.repository || "").toLowerCase() === sourceIssue.repository.toLowerCase()
    && Number(candidate.issue_number) === sourceIssue.issue_number;
}

function prepareExperienceIssue({
  record,
  issue,
  repository,
  existingRecords = [],
}) {
  const findings = screenExperienceRecord(record);
  let sourceIssue;
  try {
    sourceIssue = sourceIssueIdentity(issue, repository);
  } catch (error) {
    findings.push(finding("EXPERIENCE_IDENTITY_INVALID", error.message));
  }
  if (findings.length || !sourceIssue) {
    return { ready: false, findings, record: null, path: "" };
  }

  const sourceMatch = existingRecords.find((entry) => sameSourceIssue(entry.record, sourceIssue));
  const idMatch = existingRecords.find((entry) => entry.record?.experience_id === record.experience_id);
  if (sourceMatch && sourceMatch.record.experience_id !== record.experience_id) {
    return {
      ready: false,
      findings: [finding("EXPERIENCE_ID_IMMUTABLE", `Issue #${sourceIssue.issue_number} is already bound to ${sourceMatch.record.experience_id}.`)],
      record: null,
      path: "",
    };
  }
  if (idMatch && !sameSourceIssue(idMatch.record, sourceIssue)) {
    return {
      ready: false,
      findings: [finding("EXPERIENCE_ID_COLLISION", `${record.experience_id} is already owned by another source.`)],
      record: null,
      path: "",
    };
  }

  const eventTimestamp = String(issue.updated_at || issue.created_at || "").trim();
  const prepared = JSON.parse(JSON.stringify(record));
  prepared.lifecycle.status = "reviewed";
  prepared.lifecycle.updated_at = eventTimestamp;
  if (sourceMatch?.record?.lifecycle?.created_at) {
    prepared.lifecycle.created_at = sourceMatch.record.lifecycle.created_at;
  }
  prepared.provenance.author_ref = sourceIssue.author_ref;
  prepared.provenance.source_issue = {
    provider: sourceIssue.provider,
    repository: sourceIssue.repository,
    issue_number: sourceIssue.issue_number,
    url: sourceIssue.url,
  };
  prepared.screening = {
    status: "passed",
    method: "github-experience-agent-v1",
    screened_at: eventTimestamp,
    findings: [],
  };
  prepared.review = {
    status: "approved",
    mode: "automated-policy",
    reviewer: "github-experience-agent-v1",
    reviewed_at: eventTimestamp,
    notes: "Automatically approved after authenticated identity binding, deterministic policy screening, declared workflow-evidence verification, and canonical repository validation.",
  };

  return {
    ready: true,
    findings: [],
    record: prepared,
    path: `experience_records/reviewed/${prepared.experience_id}.json`,
    previousPath: sourceMatch?.path || "",
  };
}

async function verifyExperienceWorkflowEvidence(record, { github, verifiedAt }) {
  const output = JSON.parse(JSON.stringify(record));
  const findings = [];
  for (const evidence of output.evidence || []) {
    if (evidence?.kind !== "workflow-run") {
      delete evidence.source;
      delete evidence.machine_verification;
      continue;
    }
    if (!evidence.source || evidence.url !== evidence.source.workflow_run_url) {
      findings.push(finding(
        "EXPERIENCE_WORKFLOW_SOURCE_INVALID",
        `${evidence.evidence_id || "workflow evidence"} must bind url to source.workflow_run_url.`,
      ));
      continue;
    }
    const verification = await verifyEvidenceProvenance({ source: evidence.source }, { github });
    if (verification.status !== "workflow-verified") {
      findings.push(finding(
        "EXPERIENCE_WORKFLOW_NOT_VERIFIED",
        `${evidence.evidence_id || "workflow evidence"}: ${verification.reason || "verification failed"}.`,
      ));
      continue;
    }
    evidence.machine_verification = {
      ...verification,
      verified_at: verifiedAt,
    };
  }
  return { record: output, findings };
}

function compactValidationOutput(value) {
  return String(value || "").replace(/\r/g, "").trim().slice(0, 4000);
}

function renderExperienceIntakeComment({
  state,
  findings = [],
  recordUrl = "",
  validationOutput = "",
  issueNumber,
}) {
  const lines = ["## GitHub Experience Agent", ""];
  if (state === "accepted") {
    lines.push(
      "Status: **automatically reviewed and accepted**",
      "",
      `The Experience passed the complete automated review policy and was committed to \`main\` at [its stable public path](${recordUrl}).`,
      "",
      "- GitHub author identity was bound from the authenticated Issue author.",
      "- Declared workflow evidence, when present, was checked against the exact public repository, commit, run, job, and step.",
      "- Canonical schema, privacy, safety, evidence, and repository policy gates passed.",
      "- The Issue was completed automatically; no maintainer merge step remains.",
      "- Automated acceptance is not human review, independent reproduction, or publication as a callable Skill.",
    );
  } else {
    lines.push("Status: **changes requested**", "");
    for (const item of findings) {
      lines.push(`- \`${item.code}\`: ${item.message}`);
    }
    const output = compactValidationOutput(validationOutput);
    if (output) {
      lines.push("", "<details><summary>Canonical validator output</summary>", "", "```text", output, "```", "", "</details>");
    }
    lines.push("", "Edit this Issue to retry. Any previously recorded version remains unchanged until the edited record passes.");
  }
  lines.push("", `Source Issue: #${issueNumber}`, "", COMMENT_MARKER);
  return lines.join("\n");
}

module.exports = {
  COMMENT_MARKER,
  MAX_RECORD_BYTES,
  extractExperienceIssue,
  loadExperienceRecords,
  prepareExperienceIssue,
  renderExperienceIntakeComment,
  screenExperienceRecord,
  sourceIssueIdentity,
  verifyExperienceWorkflowEvidence,
};
