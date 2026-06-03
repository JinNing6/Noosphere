import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const dockSource = await readFile(new URL('../src/components/AhaMomentDock.tsx', import.meta.url), 'utf8');
const cssSource = await readFile(new URL('../src/index.css', import.meta.url), 'utf8');

assert.match(
  dockSource,
  /import\s+\{[^}]*CONTRIBUTION_ACTION[^}]*\}\s+from\s+'..\/utils\/growthCopy'/s,
  'homepage dock should import the canonical contribution action',
);
assert.match(dockSource, /href=\{CONTRIBUTION_ACTION\.url\}/, 'homepage dock should render a real issue-form link');
assert.match(dockSource, /target="_blank"/, 'public issue-form link should open in a new tab');
assert.match(dockSource, /rel="noopener noreferrer"/, 'public issue-form link should prevent opener/referrer leakage');
assert.match(dockSource, /\{CONTRIBUTION_ACTION\.label\}/, 'homepage CTA should use the canonical contribution label');
assert.match(dockSource, /\{CONTRIBUTION_ACTION\.idleLabel\}/, 'homepage CTA should show why no install/token is needed');

assert.match(
  cssSource,
  /\.aha-install-actions\s+(button,\s*)?\.aha-install-actions\s+a/s,
  'install action styles should cover both copy buttons and the contribution link',
);
assert.match(cssSource, /text-decoration:\s*none/, 'contribution link should be styled as a polished action, not an underlined raw link');

console.log('homepage contribution CTA ok: issue-form link is visible, safe, and styled');
