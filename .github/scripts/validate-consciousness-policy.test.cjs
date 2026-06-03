const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const repoRoot = path.join(__dirname, "..", "..");

function quotedValues(source) {
  return Array.from(source.matchAll(/["']([^"']+)["']/g), (match) => match[1]).sort();
}

function extractPythonSet(source, name) {
  const match = source.match(new RegExp(`${name}\\s*=\\s*\\{([^}]+)\\}`));
  assert.ok(match, `Expected Python set ${name}`);
  return quotedValues(match[1]);
}

function extractWorkflowArray(source, name) {
  const match = source.match(new RegExp(`const\\s+${name}\\s*=\\s*\\[([^\\]]+)\\]`));
  assert.ok(match, `Expected workflow array ${name}`);
  return quotedValues(match[1]);
}

function extractIssueFormTypeOptions(source) {
  const match = source.match(
    /id:\s*consciousness_type[\s\S]*?options:\s*\r?\n([\s\S]*?)\r?\n\s*validations:/
  );
  assert.ok(match, "Expected consciousness_type options in the Issue Form");
  return Array.from(match[1].matchAll(/^\s*-\s*([a-z-]+)\s*$/gm), (item) => item[1]).sort();
}

test("local validator accepts every payload type exposed by upload and promotion", () => {
  const validator = fs.readFileSync(
    path.join(repoRoot, ".github", "scripts", "validate_consciousness.py"),
    "utf8"
  );
  const promotionWorkflow = fs.readFileSync(
    path.join(repoRoot, ".github", "workflows", "consciousness_promote.yml"),
    "utf8"
  );
  const issueForm = fs.readFileSync(
    path.join(repoRoot, ".github", "ISSUE_TEMPLATE", "consciousness-upload.yml"),
    "utf8"
  );

  const uploadTypes = extractIssueFormTypeOptions(issueForm);
  const promotionTypes = extractWorkflowArray(promotionWorkflow, "VALID_TYPES");
  const validatorTypes = extractPythonSet(validator, "VALID_CONSCIOUSNESS_TYPES");

  assert.deepEqual(promotionTypes, uploadTypes);
  assert.deepEqual(validatorTypes, uploadTypes);
});
