import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import ts from 'typescript';

const issueDeepLinkUrl = new URL('../src/utils/issueDeepLink.ts', import.meta.url);
const issueDeepLinkSource = await readFile(issueDeepLinkUrl, 'utf8');
const issueDeepLinkJs = ts.transpileModule(issueDeepLinkSource, {
  compilerOptions: {
    module: ts.ModuleKind.ES2022,
    target: ts.ScriptTarget.ES2022,
    verbatimModuleSyntax: true,
  },
}).outputText;
const issueDeepLink = await import(`data:text/javascript;base64,${Buffer.from(issueDeepLinkJs).toString('base64')}`);

const {
  createNoosphereIssueUrl,
  findNodeByIssueNumber,
  readIssueNumberFromSearch,
} = issueDeepLink;

assert.equal(readIssueNumberFromSearch('?issue=23'), 23, 'issue query param should parse to a number');
assert.equal(readIssueNumberFromSearch('?profile=debug-agent&issue=18'), 18, 'issue query param should work with other params');
assert.equal(readIssueNumberFromSearch('?issue='), null, 'blank issue query param should be ignored');
assert.equal(readIssueNumberFromSearch('?issue=abc'), null, 'non-numeric issue query param should be ignored');
assert.equal(readIssueNumberFromSearch('?issue=-1'), null, 'negative issue query param should be ignored');
assert.equal(readIssueNumberFromSearch(''), null, 'missing issue query param should return null');

assert.equal(
  createNoosphereIssueUrl(23),
  'https://jinning6.github.io/Noosphere/?issue=23',
  'Noosphere issue URL should match promotion share card links',
);

const nodes = [
  { id: 'soul-a', issueNumber: 17, title_en: 'First' },
  { id: 'soul-b', issueNumber: 23, title_en: 'Target' },
  { id: 'soul-c', title_en: 'No issue' },
];
assert.deepEqual(findNodeByIssueNumber(nodes, 23), nodes[1], 'deep link should select the matching dynamic consciousness node');
assert.equal(findNodeByIssueNumber(nodes, 999), null, 'missing issue should not select a node');

console.log('issue deeplink ok: parsed issue params and matched dynamic nodes');
