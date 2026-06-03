import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const appSource = await readFile(new URL('../src/App.tsx', import.meta.url), 'utf8');
const cssSource = await readFile(new URL('../src/index.css', import.meta.url), 'utf8');

assert.match(
  appSource,
  /import\s+LiveResonanceBoard\s+from\s+'\.\/components\/LiveResonanceBoard'/,
  'homepage should import the live resonance board',
);
assert.match(
  appSource,
  /<LiveResonanceBoard\s+dynamicNodes=\{dynamicNodes\}\s+onOpenUploader=\{handleOpenUploader\}\s*\/>/,
  'homepage should render the live resonance board with real dynamic payload nodes and upload action',
);
assert.match(cssSource, /\.resonance-board\b/, 'resonance board should have a stable CSS surface');
assert.match(cssSource, /\.resonance-share-button\b/, 'resonance board should expose a styled share button');

const boardSource = await readFile(new URL('../src/utils/resonanceBoard.ts', import.meta.url), 'utf8');
const componentSource = await readFile(new URL('../src/components/LiveResonanceBoard.tsx', import.meta.url), 'utf8');

assert.match(boardSource, /export function summarizeResonanceBoard/, 'resonance board should centralize real-data summary logic');
assert.match(boardSource, /export function createResonanceBoardSharePost/, 'resonance board should centralize share copy generation');
assert.match(boardSource, /strongestResonance/, 'summary should expose the strongest embedding-backed resonance pair');
assert.match(boardSource, /totalMemories:\s*nodes\.length/, 'summary should count real dynamic memories');
assert.match(boardSource, /mediaMemories:\s*nodes\.filter/, 'summary should count real media memories from nodes');
assert.match(boardSource, /totalResonance:\s*nodes\.reduce/, 'summary should sum real resonance counts from nodes');
assert.match(boardSource, /createNoosphereIssueUrl/, 'share post should deep-link to real promoted issue pages');
assert.match(boardSource, /Strongest resonance:/, 'share post should include the strongest public resonance edge');
assert.match(boardSource, /CONTRIBUTION_ACTION\.url/, 'share post should include the no-token upload route');
assert.match(boardSource, /MARKETPLACE_INSTALL_COMMAND/, 'share post should include the install command');
assert.doesNotMatch(boardSource, /\b(users|installs|downloads|stars)\b/i, 'share logic should not invent adoption metrics');

assert.match(componentSource, /summarizeResonanceBoard\(dynamicNodes\)/, 'component should summarize the live dynamic nodes');
assert.match(componentSource, /createResonanceBoardSharePost\(summary\)/, 'component should copy a generated share post');
assert.match(componentSource, /onOpenUploader/, 'component should route viewers back into contribution');
assert.match(componentSource, /summary\.topCreators(?:\.slice\([^)]*\))?\.map/, 'component should expose real top creators');
assert.match(componentSource, /summary\.typeRows(?:\.slice\([^)]*\))?\.map/, 'component should expose real type distribution');
assert.match(componentSource, /summary\.latestMemory/, 'component should expose the latest real memory');
assert.match(componentSource, /summary\.strongestResonance/, 'component should show the strongest embedding-backed resonance pair');
assert.match(componentSource, /Strongest resonance/, 'component should label the strongest resonance surface');

console.log('resonance board ok: live board source is wired to real dynamic memory data');
