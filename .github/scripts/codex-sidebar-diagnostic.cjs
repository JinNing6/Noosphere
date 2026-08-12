const MAX_REPORT_BYTES = 32 * 1024;
const GITHUB_LOGIN = /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$/;
const GITHUB_REPOSITORY = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;
const VERSION_TEXT = /^[A-Za-z0-9][A-Za-z0-9 ._()/:+-]{0,79}$/;
const SEMVER_TEXT = /^\d+(?:\.\d+){1,3}(?:[-+][A-Za-z0-9.-]+)?$/;
const PRIVATE_PATH_PATTERNS = [
  /\b[A-Za-z]:\\/,
  /\/(?:Users|home)\/[^/\s]+\//,
];
const SECRET_PATTERNS = [
  /\bgh[oprsu]_[A-Za-z0-9_]{20,}\b/,
  /\bgithub_pat_[A-Za-z0-9_]{20,}\b/,
  /\b(?:sk|xox[baprs])-[A-Za-z0-9-]{20,}\b/,
  /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/,
];

const TOP_LEVEL_KEYS = [
  "schema_version",
  "record_kind",
  "generated_at",
  "tool",
  "environment",
  "observation",
  "diagnosis",
  "action",
  "next_step",
  "privacy",
  "upstream",
];
const CLASSIFICATIONS = new Set([
  "legacy-single-layer-match",
  "second-layer-present",
  "no-persisted-project-order",
  "not-applicable-sort-mode",
  "unsupported-state-shape",
]);
const VALUE_KINDS = new Set(["missing", "null", "array", "object", "string"]);
const REPAIR_BLOCKERS = new Set([
  "second-order-layer",
  "recency-sort-not-selected",
  "legacy-order-already-empty",
  "unsupported-state-shape",
  "live-repair-is-windows-only",
  "codex-running",
]);
const EXPECTED_UPSTREAM = {
  primary_issue: "https://github.com/openai/codex/issues/31836",
  related_activity_issue: "https://github.com/openai/codex/issues/36300",
  related_task_issue: "https://github.com/openai/codex/issues/35090",
};

function finding(code, message) {
  return { code, message };
}

function isPlainObject(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function hasExactKeys(value, expected) {
  if (!isPlainObject(value)) return false;
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  return actual.length === wanted.length
    && actual.every((key, index) => key === wanted[index]);
}

function isBoundedCount(value) {
  return Number.isInteger(value) && value >= 0 && value <= 100_000;
}

function isBoolean(value) {
  return value === true || value === false;
}

function isDateTime(value) {
  return typeof value === "string"
    && value.length <= 50
    && !Number.isNaN(Date.parse(value));
}

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

function extractDiagnosticIssue(body) {
  const sections = parseMarkdownSections(body);
  const value = sections.get(normalizeLabel("Generated sidebar diagnostic JSON"));
  if (value === undefined) {
    return { relevant: false, report: null, findings: [] };
  }
  const payload = extractFencedJson(value);
  if (!payload) {
    return {
      relevant: true,
      report: null,
      findings: [finding("DIAGNOSTIC_JSON_MISSING", "The generated diagnostic field is empty.")],
    };
  }
  const declaration = sections.get(normalizeLabel("Public submission declaration")) || "";
  const checkedDeclarations = declaration.match(/-\s*\[[xX]\]/g) || [];
  if (checkedDeclarations.length < 3) {
    return {
      relevant: true,
      report: null,
      findings: [finding(
        "DIAGNOSTIC_PUBLIC_CONSENT_MISSING",
        "All real-state, redaction, and public identity declarations must remain checked.",
      )],
    };
  }
  if (Buffer.byteLength(payload, "utf8") > MAX_REPORT_BYTES) {
    return {
      relevant: true,
      report: null,
      findings: [finding("DIAGNOSTIC_TOO_LARGE", `The report exceeds ${MAX_REPORT_BYTES} bytes.`)],
    };
  }
  try {
    return { relevant: true, report: JSON.parse(payload), findings: [] };
  } catch {
    return {
      relevant: true,
      report: null,
      findings: [finding("DIAGNOSTIC_JSON_INVALID", "The generated diagnostic is not valid JSON.")],
    };
  }
}

function validateDiagnostic(report) {
  const findings = [];
  if (!hasExactKeys(report, TOP_LEVEL_KEYS)) {
    return [finding(
      "DIAGNOSTIC_SCHEMA_MISMATCH",
      "The report must contain exactly the fields emitted by codex-sidebar-doctor 0.1.0.",
    )];
  }

  const serialized = JSON.stringify(report);
  if (Buffer.byteLength(serialized, "utf8") > MAX_REPORT_BYTES) {
    findings.push(finding("DIAGNOSTIC_TOO_LARGE", `The report exceeds ${MAX_REPORT_BYTES} bytes.`));
  }
  if (PRIVATE_PATH_PATTERNS.some((pattern) => pattern.test(serialized))) {
    findings.push(finding("DIAGNOSTIC_PRIVATE_PATH_DETECTED", "The report contains an absolute local path."));
  }
  if (SECRET_PATTERNS.some((pattern) => pattern.test(serialized))) {
    findings.push(finding("DIAGNOSTIC_SECRET_DETECTED", "The report contains credential-shaped content."));
  }

  if (report.schema_version !== 1
      || report.record_kind !== "codex-sidebar-diagnostic"
      || !isDateTime(report.generated_at)) {
    findings.push(finding("DIAGNOSTIC_PROTOCOL_MISMATCH", "The diagnostic protocol identity or timestamp is invalid."));
  }

  if (!hasExactKeys(report.tool, ["name", "version", "published_recovery"])
      || report.tool.name !== "codex-sidebar-doctor"
      || report.tool.version !== "0.1.0"
      || report.tool.published_recovery !== "codex-project-recency-sort-recovery@1.0.0") {
    findings.push(finding("DIAGNOSTIC_TOOL_MISMATCH", "The report was not emitted by the supported doctor version."));
  }

  const environmentKeys = [
    "os",
    "powershell_version",
    "codex_version",
    "live_state",
    "codex_process_running",
  ];
  if (!hasExactKeys(report.environment, environmentKeys)) {
    findings.push(finding("DIAGNOSTIC_ENVIRONMENT_INVALID", "The environment object is malformed."));
  } else {
    if (!["windows", "macos", "linux", "unknown"].includes(report.environment.os)
        || !SEMVER_TEXT.test(String(report.environment.powershell_version || ""))
        || !isBoolean(report.environment.live_state)
        || !isBoolean(report.environment.codex_process_running)) {
      findings.push(finding("DIAGNOSTIC_ENVIRONMENT_INVALID", "The environment fields are invalid."));
    }
    if (!VERSION_TEXT.test(String(report.environment.codex_version || ""))) {
      findings.push(finding("DIAGNOSTIC_CODEX_VERSION_REQUIRED", "A bounded Codex build/version string is required."));
    }
    if (report.environment.live_state !== true) {
      findings.push(finding("DIAGNOSTIC_LIVE_STATE_REQUIRED", "Public intake accepts live-state diagnoses, not copied fixtures."));
    }
  }

  if (!hasExactKeys(report.observation, ["stale_ordering_observed", "scope"])
      || report.observation.stale_ordering_observed !== true
      || !["project-groups", "tasks-within-project", "both", "unsure"].includes(
        report.observation.scope,
      )) {
    findings.push(finding(
      "DIAGNOSTIC_OBSERVATION_REQUIRED",
      "The submitter must attest the observed stale-ordering scope.",
    ));
  }

  const diagnosisKeys = [
    "classification",
    "mode",
    "project_sort_mode",
    "top_level_order_present",
    "top_level_order_kind",
    "top_level_order_count",
    "second_layer_present",
    "second_layer_kind",
    "second_layer_count",
    "repair_supported",
    "repair_blockers",
  ];
  if (!hasExactKeys(report.diagnosis, diagnosisKeys)) {
    findings.push(finding("DIAGNOSTIC_RESULT_INVALID", "The diagnosis object is malformed."));
  } else {
    const diagnosis = report.diagnosis;
    if (!CLASSIFICATIONS.has(diagnosis.classification)
        || !(diagnosis.mode === null || typeof diagnosis.mode === "string")
        || !(diagnosis.project_sort_mode === null || typeof diagnosis.project_sort_mode === "string")
        || !isBoolean(diagnosis.top_level_order_present)
        || !VALUE_KINDS.has(diagnosis.top_level_order_kind)
        || !isBoundedCount(diagnosis.top_level_order_count)
        || !isBoolean(diagnosis.second_layer_present)
        || !VALUE_KINDS.has(diagnosis.second_layer_kind)
        || !isBoundedCount(diagnosis.second_layer_count)
        || !isBoolean(diagnosis.repair_supported)
        || !Array.isArray(diagnosis.repair_blockers)
        || diagnosis.repair_blockers.some((item) => !REPAIR_BLOCKERS.has(item))
        || new Set(diagnosis.repair_blockers).size !== diagnosis.repair_blockers.length) {
      findings.push(finding("DIAGNOSTIC_RESULT_INVALID", "One or more diagnosis fields are invalid."));
    } else {
      let consistent = true;
      if (diagnosis.classification === "legacy-single-layer-match") {
        consistent = diagnosis.mode === "project"
          && diagnosis.project_sort_mode === "updated_at"
          && diagnosis.top_level_order_kind === "array"
          && diagnosis.top_level_order_count > 0
          && diagnosis.second_layer_present === false;
      } else if (diagnosis.classification === "second-layer-present") {
        consistent = diagnosis.mode === "project"
          && diagnosis.project_sort_mode === "updated_at"
          && diagnosis.second_layer_present === true
          && diagnosis.second_layer_count > 0
          && diagnosis.repair_supported === false
          && diagnosis.repair_blockers.includes("second-order-layer");
      } else if (diagnosis.classification === "no-persisted-project-order") {
        consistent = diagnosis.mode === "project"
          && diagnosis.project_sort_mode === "updated_at"
          && diagnosis.top_level_order_count === 0
          && diagnosis.second_layer_present === false
          && diagnosis.repair_supported === false;
      } else if (diagnosis.classification === "not-applicable-sort-mode") {
        consistent = diagnosis.mode !== "project" || diagnosis.project_sort_mode !== "updated_at";
      }
      if (diagnosis.classification !== "legacy-single-layer-match"
          && diagnosis.repair_supported !== false) {
        consistent = false;
      }
      if (diagnosis.repair_supported && diagnosis.repair_blockers.length > 0) {
        consistent = false;
      }
      if (!diagnosis.top_level_order_present
          && (diagnosis.top_level_order_kind !== "missing"
              || diagnosis.top_level_order_count !== 0)) {
        consistent = false;
      }
      if (diagnosis.second_layer_present && diagnosis.second_layer_count === 0) {
        consistent = false;
      }
      if (!consistent) {
        findings.push(finding("DIAGNOSTIC_CLASSIFICATION_INCONSISTENT", "The classification conflicts with its bounded state facts."));
      }
      if (report.environment.codex_process_running
          && !diagnosis.repair_blockers.includes("codex-running")) {
        findings.push(finding("DIAGNOSTIC_CLASSIFICATION_INCONSISTENT", "A running Codex process must block repair."));
      }
    }
  }

  if (!hasExactKeys(report.action, [
    "requested",
    "status",
    "backup_created",
    "post_repair_classification",
  ])
      || report.action.requested !== false
      || report.action.status !== "not-requested"
      || report.action.backup_created !== false
      || report.action.post_repair_classification !== null) {
    findings.push(finding("DIAGNOSTIC_READ_ONLY_REQUIRED", "Public diagnostic intake accepts read-only reports only."));
  }

  if (!hasExactKeys(report.next_step, ["kind", "message"])
      || !["review-repair", "stop-before-repair", "collect-redacted-evidence", "no-action"].includes(report.next_step.kind)
      || typeof report.next_step.message !== "string"
      || report.next_step.message.length < 20
      || report.next_step.message.length > 500) {
    findings.push(finding("DIAGNOSTIC_NEXT_STEP_INVALID", "The next-step object is malformed."));
  }

  const privacyKeys = [
    "contains_project_names",
    "contains_project_paths",
    "contains_thread_ids",
    "contains_conversation_content",
    "contains_ordered_identifiers",
  ];
  if (!hasExactKeys(report.privacy, privacyKeys)
      || privacyKeys.some((key) => report.privacy[key] !== false)) {
    findings.push(finding("DIAGNOSTIC_PRIVACY_BOUNDARY_FAILED", "Every generated privacy flag must remain false."));
  }

  if (!hasExactKeys(report.upstream, Object.keys(EXPECTED_UPSTREAM))
      || Object.entries(EXPECTED_UPSTREAM).some(([key, value]) => report.upstream[key] !== value)) {
    findings.push(finding("DIAGNOSTIC_UPSTREAM_MISMATCH", "The bounded upstream issue references were changed."));
  }

  return findings;
}

function sourceIssueIdentity(issue, repository) {
  const login = String(issue?.user?.login || "").trim();
  const number = Number(issue?.number);
  const url = String(issue?.html_url || "").trim();
  if (!GITHUB_LOGIN.test(login)
      || !GITHUB_REPOSITORY.test(String(repository || ""))
      || !Number.isInteger(number)
      || number < 1) {
    throw new Error("The authenticated GitHub Issue identity is missing or invalid.");
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
  };
}

function prepareDiagnosticIssue({ report, issue, repository, acceptedAt }) {
  const findings = validateDiagnostic(report);
  let sourceIssue;
  try {
    sourceIssue = sourceIssueIdentity(issue, repository);
  } catch (error) {
    findings.push(finding("DIAGNOSTIC_IDENTITY_INVALID", error.message));
  }
  if (findings.length || !sourceIssue) {
    return { ready: false, findings, record: null, path: "" };
  }
  const acceptedTimestamp = String(acceptedAt || "");
  if (!isDateTime(acceptedTimestamp)) {
    return {
      ready: false,
      findings: [finding("DIAGNOSTIC_ACCEPTED_AT_INVALID", "The repository acceptance timestamp is invalid.")],
      record: null,
      path: "",
    };
  }
  const record = JSON.parse(JSON.stringify(report));
  record.submission = {
    status: "accepted",
    review_mode: "automated-policy",
    reviewer: "github-sidebar-diagnostic-agent-v1",
    accepted_at: acceptedTimestamp,
    reporter: issue.user.login,
    source_issue: sourceIssue,
    independent_reproduction: false,
  };
  return {
    ready: true,
    findings: [],
    record,
    path: `community_evidence/codex-sidebar/issue-${sourceIssue.issue_number}.json`,
  };
}

module.exports = {
  MAX_REPORT_BYTES,
  extractDiagnosticIssue,
  prepareDiagnosticIssue,
  validateDiagnostic,
};
