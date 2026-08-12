const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const {
  extractDiagnosticIssue,
  prepareDiagnosticIssue,
  validateDiagnostic,
} = require("./codex-sidebar-diagnostic.cjs");


function validDiagnostic(overrides = {}) {
  const payload = {
    schema_version: 1,
    record_kind: "codex-sidebar-diagnostic",
    generated_at: "2026-08-12T08:00:00.0000000+00:00",
    tool: {
      name: "codex-sidebar-doctor",
      version: "0.1.0",
      published_recovery: "codex-project-recency-sort-recovery@1.0.0",
    },
    environment: {
      os: "windows",
      powershell_version: "7.5.2",
      codex_version: "26.803.41515 (build 6321)",
      live_state: true,
      codex_process_running: true,
    },
    observation: {
      stale_ordering_observed: true,
      scope: "project-groups",
    },
    diagnosis: {
      classification: "second-layer-present",
      mode: "project",
      project_sort_mode: "updated_at",
      top_level_order_present: true,
      top_level_order_kind: "array",
      top_level_order_count: 40,
      second_layer_present: true,
      second_layer_kind: "array",
      second_layer_count: 40,
      repair_supported: false,
      repair_blockers: ["second-order-layer", "codex-running"],
    },
    action: {
      requested: false,
      status: "not-requested",
      backup_created: false,
      post_repair_classification: null,
    },
    next_step: {
      kind: "collect-redacted-evidence",
      message: "A newer ordering layer is present. Do not apply the legacy repair; export this redacted diagnosis for the cross-platform update.",
    },
    privacy: {
      contains_project_names: false,
      contains_project_paths: false,
      contains_thread_ids: false,
      contains_conversation_content: false,
      contains_ordered_identifiers: false,
    },
    upstream: {
      primary_issue: "https://github.com/openai/codex/issues/31836",
      related_activity_issue: "https://github.com/openai/codex/issues/36300",
      related_task_issue: "https://github.com/openai/codex/issues/35090",
    },
  };
  return Object.assign(payload, overrides);
}


function issueBody(payload, checked = true) {
  const mark = checked ? "x" : " ";
  return [
    "### Generated sidebar diagnostic JSON",
    "",
    "```json",
    JSON.stringify(payload, null, 2),
    "```",
    "",
    "### Public submission declaration",
    "",
    `- [${mark}] I personally observed stale Codex sidebar ordering in the scope recorded by this live-state report.`,
    `- [${mark}] I reviewed the generated report and it contains no project names, paths, task identifiers, or conversation content.`,
    `- [${mark}] I consent to automatic validation and public storage under my authenticated GitHub identity.`,
  ].join("\n");
}


test("accepts a consistent doctor report without treating it as an Experience", () => {
  assert.deepEqual(validateDiagnostic(validDiagnostic()), []);

  const issue = {
    number: 91,
    user: { login: "example-user" },
    html_url: "https://github.com/JinNing6/Noosphere/issues/91",
    created_at: "2026-08-12T08:01:00Z",
    updated_at: "2026-08-12T08:01:00Z",
  };
  const result = prepareDiagnosticIssue({
    report: validDiagnostic(),
    issue,
    repository: "JinNing6/Noosphere",
    acceptedAt: "2026-08-12T08:02:00Z",
  });

  assert.equal(result.ready, true);
  assert.equal(result.path, "community_evidence/codex-sidebar/issue-91.json");
  assert.equal(result.record.record_kind, "codex-sidebar-diagnostic");
  assert.equal(result.record.submission.reporter, "example-user");
  assert.equal(result.record.submission.review_mode, "automated-policy");
  assert.equal(result.record.submission.source_issue.issue_number, 91);
  assert.equal(result.record.submission.independent_reproduction, false);
});


test("extracts only the generated JSON after all public declarations are checked", () => {
  const extracted = extractDiagnosticIssue(issueBody(validDiagnostic()));
  assert.equal(extracted.relevant, true);
  assert.deepEqual(extracted.findings, []);
  assert.equal(extracted.report.diagnosis.classification, "second-layer-present");

  const unchecked = extractDiagnosticIssue(issueBody(validDiagnostic(), false));
  assert.equal(unchecked.report, null);
  assert.equal(unchecked.findings[0].code, "DIAGNOSTIC_PUBLIC_CONSENT_MISSING");
});


test("rejects inconsistent classification, unsafe action claims, and private paths", () => {
  const inconsistent = validDiagnostic();
  inconsistent.diagnosis.second_layer_present = false;
  assert.ok(
    validateDiagnostic(inconsistent).some(
      (item) => item.code === "DIAGNOSTIC_CLASSIFICATION_INCONSISTENT",
    ),
  );

  const repaired = validDiagnostic();
  repaired.action = {
    requested: true,
    status: "applied",
    backup_created: true,
    post_repair_classification: "no-persisted-project-order",
  };
  assert.ok(
    validateDiagnostic(repaired).some(
      (item) => item.code === "DIAGNOSTIC_READ_ONLY_REQUIRED",
    ),
  );

  const leaking = validDiagnostic();
  leaking.next_step.message = "Inspect C:\\Users\\Alice\\private-project";
  assert.ok(
    validateDiagnostic(leaking).some(
      (item) => item.code === "DIAGNOSTIC_PRIVATE_PATH_DETECTED",
    ),
  );
});


test("requires a real version, live state, and all privacy flags to remain false", () => {
  const noVersion = validDiagnostic();
  noVersion.environment.codex_version = null;
  assert.ok(
    validateDiagnostic(noVersion).some(
      (item) => item.code === "DIAGNOSTIC_CODEX_VERSION_REQUIRED",
    ),
  );

  const copiedState = validDiagnostic();
  copiedState.environment.live_state = false;
  assert.ok(
    validateDiagnostic(copiedState).some(
      (item) => item.code === "DIAGNOSTIC_LIVE_STATE_REQUIRED",
    ),
  );

  const privacyClaim = validDiagnostic();
  privacyClaim.privacy.contains_thread_ids = true;
  assert.ok(
    validateDiagnostic(privacyClaim).some(
      (item) => item.code === "DIAGNOSTIC_PRIVACY_BOUNDARY_FAILED",
    ),
  );

  const noObservation = validDiagnostic();
  noObservation.observation = {
    stale_ordering_observed: false,
    scope: null,
  };
  assert.ok(
    validateDiagnostic(noObservation).some(
      (item) => item.code === "DIAGNOSTIC_OBSERVATION_REQUIRED",
    ),
  );
});


test("rejects spoofed issue identity and uses a stable issue-number path", () => {
  const issue = {
    number: 91,
    user: { login: "example-user" },
    html_url: "https://github.com/another/repository/issues/91",
    created_at: "2026-08-12T08:01:00Z",
    updated_at: "2026-08-12T08:01:00Z",
  };
  const result = prepareDiagnosticIssue({
    report: validDiagnostic(),
    issue,
    repository: "JinNing6/Noosphere",
    acceptedAt: "2026-08-12T08:02:00Z",
  });
  assert.equal(result.ready, false);
  assert.equal(result.findings[0].code, "DIAGNOSTIC_IDENTITY_INVALID");
});


test("workflow uses trusted main, the shared writer queue, and direct deterministic gates", () => {
  const repositoryRoot = path.resolve(__dirname, "..", "..");
  const workflow = fs.readFileSync(
    path.join(repositoryRoot, ".github", "workflows", "codex_sidebar_diagnostic.yml"),
    "utf8",
  );
  const form = fs.readFileSync(
    path.join(repositoryRoot, ".github", "ISSUE_TEMPLATE", "codex-sidebar-diagnostic.yml"),
    "utf8",
  );
  const doctor = fs.readFileSync(
    path.join(
      repositoryRoot,
      "tools",
      "codex-sidebar-doctor",
      "Invoke-CodexSidebarDoctor.ps1",
    ),
    "utf8",
  );

  assert.match(workflow, /group: noosphere-main-writer/);
  assert.match(workflow, /ref: main/);
  assert.match(workflow, /permissions:\n\s+contents: write\n\s+issues: write/);
  assert.match(workflow, /node --test \.github\/scripts\/codex-sidebar-diagnostic\.test\.cjs/);
  assert.match(workflow, /git push origin HEAD:main/);
  assert.doesNotMatch(workflow, /pull_request_target/);
  assert.match(form, /Generated sidebar diagnostic JSON/);
  assert.match(form, /Public submission declaration/);
  assert.match(form, /automatic validation and public storage/);
  assert.match(doctor, /'```json'/);
  assert.match(doctor, /'```'/);
  assert.doesNotMatch(doctor, /@"[\s\S]*```json/);
});
