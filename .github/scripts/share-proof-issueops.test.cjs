const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const repoRoot = path.join(__dirname, "..", "..");

function readRepoFile(...parts) {
  return fs.readFileSync(path.join(repoRoot, ...parts), "utf8");
}

test("repository exposes a public Share Proof Issue Form", () => {
  const issueForm = readRepoFile(".github", "ISSUE_TEMPLATE", "share-proof.yml");

  assert.match(issueForm, /name:\s+Record Noosphere share proof/);
  assert.match(issueForm, /description:\s+Submit a public URL where Noosphere or a Noosphere memory was shared\./);
  assert.match(issueForm, /title:\s+"Share proof: "/);
  assert.match(issueForm, /labels:\s+\["share-proof"\]/);
  assert.match(issueForm, /id:\s+share_url/);
  assert.match(issueForm, /label:\s+Public share URL/);
  assert.match(issueForm, /validations:\s*\r?\n\s+required:\s+true/);
  assert.match(issueForm, /id:\s+source_memory/);
  assert.match(issueForm, /id:\s+share_context/);
  assert.match(issueForm, /downloads, reposts, referrals, retention, rewards, or install counts/);
});

test("label initializer creates the share-proof label used by the public form", () => {
  const workflow = readRepoFile(".github", "workflows", "init_labels.yml");

  assert.match(workflow, /name:\s+'share-proof'/);
  assert.match(workflow, /description:\s+'Public Noosphere share proof'/);
});

test("Share Proof IssueOps workflow is a safe comment-only loop", () => {
  const workflow = readRepoFile(".github", "workflows", "share_proof_issueops.yml");

  assert.match(workflow, /on:\s*\r?\n\s+issues:\s*\r?\n\s+types:\s+\[opened, edited, labeled\]/);
  assert.match(workflow, /permissions:\s*\r?\n\s+contents:\s+read\s*\r?\n\s+issues:\s+write/);
  assert.match(workflow, /contains\(github\.event\.issue\.labels\.\*\.name, 'share-proof'\)/);
  assert.match(workflow, /startsWith\(github\.event\.issue\.title, 'Share proof:'\)/);
  assert.match(workflow, /contains\(github\.event\.issue\.body, '### Public share URL'\)/);
  assert.match(workflow, /uses:\s+actions\/github-script@v7/);
  assert.match(workflow, /github\.rest\.issues\.listComments/);
  assert.match(workflow, /github\.rest\.issues\.createComment/);
  assert.match(workflow, /noosphere-share-proof:issue=/);
  assert.match(workflow, /context\.payload\.issue\.html_url/);
  assert.match(workflow, /No downloads, reposts, referrals, retention, rewards, or install counts are inferred/);
  assert.match(workflow, /issues\/new\?template=consciousness-upload\.yml/);
  assert.match(workflow, /\/plugin marketplace add JinNing6\/Noosphere/);
  assert.match(workflow, /share_consciousness/);
  assert.doesNotMatch(workflow, /actions\/checkout/);
  assert.doesNotMatch(workflow, /^\s*run:/m);
  assert.doesNotMatch(workflow, /\bnode\b/);
  assert.doesNotMatch(workflow, /\bpython\b/);
  assert.doesNotMatch(workflow, /\bnpm\b/);
  assert.doesNotMatch(workflow, /\bpip\b/);
  assert.doesNotMatch(workflow, /\bgit\s+(clone|checkout|commit|push|pull)\b/);
});

test("README first screen links to the Share Proof Issue Form", () => {
  const readme = readRepoFile("README.md");
  const firstScreen = readme.slice(0, 6500);

  assert.match(firstScreen, /Shared it publicly\? Record proof/);
  assert.match(firstScreen, /issues\/new\?template=share-proof\.yml/);
  assert.match(firstScreen, /Noosphere does not infer downloads, reposts, referrals, retention, rewards, or install counts from a URL/);
});

test("full README mirror also documents the Share Proof route", () => {
  const readme = readRepoFile("docs", "README_full.md");
  const firstScreen = readme.slice(0, 6500);

  assert.match(firstScreen, /Shared it publicly\? Record proof/);
  assert.match(firstScreen, /issues\/new\?template=share-proof\.yml/);
});
