const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const {
  buildTombstoneManifest,
  canonicalPromotionPath,
  extractWithdrawalRequest,
  findExistingPromotion,
  hasPromotionComment,
  isIssueTombstoned,
  promotionCommentMarker,
} = require("./promotion-integrity.cjs");

test("uses one deterministic promotion path per source issue", () => {
  assert.equal(
    canonicalPromotionPath({ consciousness_type: "Warning" }, 27),
    "consciousness_payloads/memory_issue0027.json",
  );
  assert.equal(
    canonicalPromotionPath({ consciousness_type: "pattern" }, 27),
    "consciousness_payloads/memory_issue0027.json",
  );
});

test("finds a legacy promotion so labeled events cannot create a duplicate", () => {
  const records = [
    {
      path: "consciousness_payloads/warning_20260101_issue0027.json",
      sha: "legacy-sha",
      payload: { promoted_from_issue: 27 },
    },
    {
      path: "consciousness_payloads/pattern_issue0028.json",
      sha: "other-sha",
      payload: { promoted_from_issue: 28 },
    },
  ];

  assert.deepEqual(findExistingPromotion(records, 27), records[0]);
});

test("uses a stable marker to reconcile the promotion success comment", () => {
  const marker = promotionCommentMarker(27);
  assert.equal(marker, "<!-- noosphere-promotion:issue-27 -->");
  assert.equal(hasPromotionComment([{ body: `done\n${marker}` }], 27), true);
  assert.equal(hasPromotionComment([{ body: "unrelated" }], 27), false);
});

test("builds an idempotent tombstone manifest", () => {
  const initial = {
    version: 1,
    withdrawn_issues: [
      { issue_number: 10, withdrawn_at: "2026-01-01T00:00:00Z" },
    ],
  };

  const first = buildTombstoneManifest(initial, {
    issueNumber: 11,
    withdrawnAt: "2026-02-01T00:00:00Z",
    withdrawnBy: "maintainer",
  });
  const second = buildTombstoneManifest(first, {
    issueNumber: 11,
    withdrawnAt: "2026-03-01T00:00:00Z",
    withdrawnBy: "maintainer",
  });

  assert.deepEqual(second, first);
  assert.deepEqual(first.withdrawn_issues.map((item) => item.issue_number), [10, 11]);
  assert.equal(isIssueTombstoned(first, 11), true);
  assert.equal(isIssueTombstoned(first, 12), false);
});

test("extracts a structured author-bound withdrawal request", () => {
  const body = [
    "<!-- WITHDRAWAL_REQUEST_START -->",
    "```json",
    JSON.stringify({ target_issue: 27, requested_by: "author" }),
    "```",
    "<!-- WITHDRAWAL_REQUEST_END -->",
  ].join("\n");

  assert.deepEqual(extractWithdrawalRequest(body), {
    target_issue: 27,
    requested_by: "author",
  });
  assert.equal(extractWithdrawalRequest("unrelated"), null);
});

test("promotion workflow reuses an existing source Issue promotion", () => {
  const workflow = fs.readFileSync(
    path.join(__dirname, "..", "workflows", "consciousness_promote.yml"),
    "utf8",
  );

  assert.match(workflow, /findExistingPromotion/);
  assert.match(workflow, /canonicalPromotionPath/);
  assert.match(workflow, /existingPromotion\?\.path/);
  assert.match(workflow, /hasPromotionComment/);
  assert.match(workflow, /git fetch origin main/);
  assert.doesNotMatch(workflow, /skipping duplicate write[\s\S]*?return;/);
});

test("withdrawal workflow writes the permanent tombstone manifest", () => {
  const workflow = fs.readFileSync(
    path.join(__dirname, "..", "workflows", "consciousness_withdraw.yml"),
    "utf8",
  );

  assert.match(workflow, /buildTombstoneManifest/);
  assert.match(workflow, /getCollaboratorPermissionLevel/);
  assert.match(workflow, /isTrustedReviewerPermission/);
  assert.match(workflow, /consciousness_tombstones\.json/);
  assert.match(workflow, /label\.name\s*==\s*'withdrawn'/);
  assert.match(workflow, /build_consciousness_index\.py/);
  assert.match(workflow, /deploy-pages\.yml\/dispatches/);
});

test("promotion and withdrawal serialize the same permanent-memory state", () => {
  const workflowsDir = path.join(__dirname, "..", "workflows");
  const promotion = fs.readFileSync(
    path.join(workflowsDir, "consciousness_promote.yml"),
    "utf8",
  );
  const withdrawal = fs.readFileSync(
    path.join(workflowsDir, "consciousness_withdraw.yml"),
    "utf8",
  );

  for (const workflow of [promotion, withdrawal]) {
    assert.match(workflow, /group: noosphere-main-writer/);
    assert.match(workflow, /queue: max/);
  }
});
