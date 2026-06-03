import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const appSource = await readFile(new URL('../src/App.tsx', import.meta.url), 'utf8');
const componentSource = await readFile(new URL('../src/components/LaunchKit.tsx', import.meta.url), 'utf8');
const launchKitSource = await readFile(new URL('../src/utils/launchKit.ts', import.meta.url), 'utf8');
const cssSource = await readFile(new URL('../src/index.css', import.meta.url), 'utf8');
const packageSource = await readFile(new URL('../package.json', import.meta.url), 'utf8');
const readmeSource = await readFile(new URL('../../README.md', import.meta.url), 'utf8');

assert.match(
  appSource,
  /import\s+LaunchKit\s+from\s+'\.\/components\/LaunchKit'/,
  'homepage should import the launch kit',
);
assert.match(
  appSource,
  /<LaunchKit\s+dynamicNodes=\{dynamicNodes\}\s+onOpenUploader=\{handleOpenUploader\}\s*\/>/,
  'homepage should render the launch kit with real dynamic payload nodes and upload action',
);

assert.match(launchKitSource, /summarizeResonanceBoard/, 'launch kit should reuse the real live memory summary');
assert.match(launchKitSource, /createShareProofIssueUrl/, 'launch kit should route every shared post back to Share Proof');
assert.match(launchKitSource, /CONTRIBUTION_ACTION\.url/, 'launch kit should route new users to the no-token upload form');
assert.match(launchKitSource, /MARKETPLACE_INSTALL_COMMAND/, 'launch kit should include the install command');
assert.match(launchKitSource, /SHARE_PROOF_DISCLAIMER/, 'launch kit should carry the non-fabrication disclosure');
assert.match(launchKitSource, /LaunchKitPost\[\]/, 'launch kit should expose multiple channel-specific post templates');
assert.match(launchKitSource, /Claude Code/, 'launch kit should include a Claude Code-specific campaign post');
assert.match(launchKitSource, /Codex/, 'launch kit should include a Codex-specific campaign post');
assert.match(launchKitSource, /GitHub/, 'launch kit should include a GitHub/community campaign post');
assert.match(launchKitSource, /summary\.totalMemories/, 'launch kit copy should use live memory counts');
assert.match(launchKitSource, /summary\.mediaMemories/, 'launch kit copy should use live media counts');
assert.match(launchKitSource, /summary\.totalResonance/, 'launch kit copy should use live resonance counts');
assert.match(launchKitSource, /summary\.latestMemory/, 'launch kit copy should reference the latest real memory when available');
assert.doesNotMatch(
  launchKitSource,
  /\b(installs|downloads|reposts|referrals|retention|rewards)\s*[:=]\s*\d+/i,
  'launch kit source must not define fake adoption counters',
);

assert.match(componentSource, /Launch kit/, 'component should label the public launch surface');
assert.match(componentSource, /createLaunchKitPosts\(dynamicNodes\)/, 'component should generate posts from live nodes');
assert.match(componentSource, /navigator\.clipboard\.writeText/, 'component should provide copy buttons for launch posts');
assert.match(componentSource, /document\.execCommand\('copy'\)/, 'component should fall back when Clipboard API is restricted');
assert.match(componentSource, /onOpenUploader/, 'component should route launch viewers back into contribution');
assert.match(componentSource, /post\.proofUrl/, 'component should expose the Share Proof route for each post');
assert.match(componentSource, /post\.channel/, 'component should show each launch channel');
assert.doesNotMatch(
  componentSource,
  /\b\d+\s+(downloads|reposts|referrals|installs|users|retention|rewards)\b/i,
  'component must not render fake propagation metrics',
);

assert.match(cssSource, /\.launch-kit\b/, 'launch kit should have a stable CSS surface');
assert.match(cssSource, /\.launch-kit-post\b/, 'launch kit posts should have stable styling');
assert.match(cssSource, /@media \(max-width: 1180px\)[\s\S]*\.launch-kit/, 'launch kit should hide on constrained desktop/mobile layouts');

assert.match(packageSource, /"test:launch-kit":\s*"node scripts\/check_launch_kit\.mjs"/, 'frontend package should expose the launch kit check');

const firstScreen = readmeSource.slice(0, 6500);
assert.match(firstScreen, /Launch Kit/i, 'README first screen should announce the launch kit');
assert.match(firstScreen, /copy-ready/i, 'README should explain the launch kit output');
assert.match(firstScreen, /Share Proof/i, 'README launch note should route back to share proof');

console.log('launch kit ok: homepage exposes real-data copy-ready campaign posts');
