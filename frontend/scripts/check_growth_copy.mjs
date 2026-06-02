import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import ts from 'typescript';

const growthCopyUrl = new URL('../src/utils/growthCopy.ts', import.meta.url);
const growthCopySource = await readFile(growthCopyUrl, 'utf8');
const growthCopyJs = ts.transpileModule(growthCopySource, {
  compilerOptions: {
    module: ts.ModuleKind.ES2022,
    target: ts.ScriptTarget.ES2022,
    verbatimModuleSyntax: true,
  },
}).outputText;
const growthCopy = await import(`data:text/javascript;base64,${Buffer.from(growthCopyJs).toString('base64')}`);

const {
  CLIPBOARD_ACTIONS,
  INSTALL_OPTIONS,
  NOOSPHERE_HOME_URL,
  SHARE_POST,
  createMemorySharePost,
  createMemoryShareUrl,
  readMemoryIdFromSearch,
} = growthCopy;

const actionById = new Map(CLIPBOARD_ACTIONS.map(action => [action.id, action]));
const installById = new Map(INSTALL_OPTIONS.map(option => [option.id, option]));

assert.equal(actionById.size, 3, 'homepage clipboard actions should include Claude, Codex, and Share');
assert.ok(actionById.has('claude'), 'Claude install action is missing');
assert.ok(actionById.has('codex'), 'Codex install action is missing');
assert.ok(actionById.has('share'), 'Share action is missing');

assert.equal(
  installById.get('claude')?.command,
  '/plugin marketplace add JinNing6/Noosphere\n/plugin install noosphere@noosphere-agent-memory\n/reload-plugins',
  'Claude install command should remain directly copyable',
);
assert.equal(
  installById.get('codex')?.command,
  'codex plugin marketplace add JinNing6/Noosphere',
  'Codex install command should remain directly copyable',
);

assert.equal(actionById.get('share')?.command, undefined, 'Share action should be resolved from the selected memory, not a generic static post');
assert.ok(SHARE_POST.includes('Noosphere'), 'share post should name the product');
assert.ok(/shared debug memory/i.test(SHARE_POST), 'share post should state the concrete developer pain');
assert.ok(SHARE_POST.includes('/plugin marketplace add JinNing6/Noosphere'), 'share post should include an install command');
assert.ok(SHARE_POST.includes(NOOSPHERE_HOME_URL), 'share post should include the public homepage');
assert.ok(SHARE_POST.length <= 240, `share post should be compact enough to repost, got ${SHARE_POST.length} chars`);
assert.doesNotMatch(SHARE_POST, /\b\d+\s+(users|installs|downloads|stars)\b/i, 'share post should not invent adoption metrics');

const crewaiMemoryUrl = createMemoryShareUrl('nsp-crewai-001');
assert.equal(
  crewaiMemoryUrl,
  `${NOOSPHERE_HOME_URL}?memory=nsp-crewai-001`,
  'memory share URL should deep-link to the selected debug memory',
);

const crewaiSharePost = createMemorySharePost({
  id: 'nsp-crewai-001',
  title: 'CrewAI multi-agent deadlock',
  fix: 'Run DAG cycle checks, enforce timeouts, and introduce a coordinator agent before execution.',
  outcome: 'task_completion_rate: 0% -> 95%',
});
assert.ok(crewaiSharePost.includes('CrewAI multi-agent deadlock'), 'memory share post should name the selected fix');
assert.ok(crewaiSharePost.includes('task_completion_rate: 0% -> 95%'), 'memory share post should include real proof when available');
assert.ok(crewaiSharePost.includes(crewaiMemoryUrl), 'memory share post should include the deep link URL');
assert.ok(crewaiSharePost.includes('/plugin marketplace add JinNing6/Noosphere'), 'memory share post should include the install command');
assert.ok(crewaiSharePost.length <= 280, `memory share post should fit social reposts, got ${crewaiSharePost.length} chars`);
assert.doesNotMatch(crewaiSharePost, /\b\d+\s+(users|installs|downloads|stars)\b/i, 'memory share post should not invent adoption metrics');
assert.equal(readMemoryIdFromSearch('?memory=nsp-openai-002'), 'nsp-openai-002', 'memory query param should initialize a selected debug memory');
assert.equal(readMemoryIdFromSearch('?utm_source=x&memory=nsp-langchain-001'), 'nsp-langchain-001', 'memory query param should work with other params');
assert.equal(readMemoryIdFromSearch('?memory='), null, 'blank memory query param should be ignored');
assert.equal(readMemoryIdFromSearch(''), null, 'missing memory query param should return null');

console.log(`growth copy ok: ${CLIPBOARD_ACTIONS.length} actions, generic ${SHARE_POST.length} chars, memory ${crewaiSharePost.length} chars`);
