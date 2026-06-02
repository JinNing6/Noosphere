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
  SHARE_POST,
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

assert.equal(actionById.get('share')?.command, SHARE_POST, 'Share action should copy the public share post');
assert.ok(SHARE_POST.includes('Noosphere'), 'share post should name the product');
assert.ok(/shared debug memory/i.test(SHARE_POST), 'share post should state the concrete developer pain');
assert.ok(SHARE_POST.includes('/plugin marketplace add JinNing6/Noosphere'), 'share post should include an install command');
assert.ok(SHARE_POST.includes('https://jinning6.github.io/Noosphere/'), 'share post should include the public homepage');
assert.ok(SHARE_POST.length <= 240, `share post should be compact enough to repost, got ${SHARE_POST.length} chars`);
assert.doesNotMatch(SHARE_POST, /\b\d+\s+(users|installs|downloads|stars)\b/i, 'share post should not invent adoption metrics');

console.log(`growth copy ok: ${CLIPBOARD_ACTIONS.length} actions, share post ${SHARE_POST.length} chars`);
