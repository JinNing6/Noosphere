import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

import {
  applyGrowthSnapshot,
  computeGrowthSnapshot,
  formatGrowthSnapshot,
} from './update_readme_growth_snapshot.mjs';

const readJson = async (url) => JSON.parse(await readFile(url, 'utf8'));

const repoReadme = await readFile(new URL('../../README.md', import.meta.url), 'utf8');
const fullReadme = await readFile(new URL('../../docs/README_full.md', import.meta.url), 'utf8');
const packageJson = await readJson(new URL('../package.json', import.meta.url));
const index = await readJson(new URL('../public/consciousness_index.json', import.meta.url));
const wiki = await readJson(new URL('../src/data/wikipedia_cache.json', import.meta.url));
const knowledgeSource = await readFile(new URL('../src/data/knowledge.ts', import.meta.url), 'utf8');
const metrics = computeGrowthSnapshot({ index, wiki, knowledgeSource });
const snapshot = formatGrowthSnapshot(metrics);
const staleScaleClaims = /\b(?:315\+\s+consciousness fragments|237\s+consciousness fragments)\b/i;
const inventedAdoptionClaims = /\b\d+\s+(?:users|installs|downloads)\b/i;

for (const [name, content] of [
  ['README.md', repoReadme],
  ['docs/README_full.md', fullReadme],
]) {
  assert.doesNotMatch(content, staleScaleClaims, `${name} should not keep stale historical scale claims`);
  assert.match(
    content,
    new RegExp(`resonate with ${index.length} public memories`, 'i'),
    `${name} hero should use the current public memory count`,
  );
  assert.ok(content.includes(snapshot), `${name} should expose the current real live snapshot: ${snapshot}`);
  assert.doesNotMatch(content, inventedAdoptionClaims, `${name} should not invent adoption metrics`);
}

assert.match(
  repoReadme,
  /<!-- noosphere-live-snapshot:start -->[\s\S]*<!-- noosphere-live-snapshot:end -->/,
  'README.md should expose a bounded live snapshot block near the top',
);
assert.match(
  repoReadme,
  /Open the GitHub Issue Form/,
  'README.md live onboarding should keep the no-MCP contribution path visible',
);
assert.equal(
  packageJson.scripts['update:readme-growth'],
  'node scripts/update_readme_growth_snapshot.mjs',
  'package.json should expose a one-command repair path for README growth snapshots',
);
await readFile(new URL('./update_readme_growth_snapshot.mjs', import.meta.url), 'utf8');
const driftedReadme = repoReadme
  .replace(/resonate with \d+ public memories/, 'resonate with 999 public memories')
  .replace(snapshot, '999 public memories - 9 media memories - 999 visible 3D nodes - latest issue #999');
const repairedReadme = applyGrowthSnapshot(driftedReadme, metrics);
assert.match(
  repairedReadme,
  new RegExp(`resonate with ${metrics.publicMemories} public memories`, 'i'),
  'README growth updater should repair stale hero counts',
);
assert.ok(
  repairedReadme.includes(snapshot),
  'README growth updater should repair stale live snapshot counts',
);
const crlfReadme = repoReadme.replace(/\r?\n/g, '\r\n');
assert.equal(
  applyGrowthSnapshot(crlfReadme, metrics),
  crlfReadme,
  'README growth updater should preserve CRLF files without dirtying the worktree',
);
const updaterCheck = spawnSync(
  process.execPath,
  [fileURLToPath(new URL('./update_readme_growth_snapshot.mjs', import.meta.url)), '--check'],
  { cwd: fileURLToPath(new URL('..', import.meta.url)), encoding: 'utf8' },
);
assert.equal(updaterCheck.status, 0, updaterCheck.stderr || updaterCheck.stdout);
assert.match(
  updaterCheck.stdout,
  new RegExp(`current README growth snapshot: ${snapshot.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`),
  'README growth updater should expose a non-silent --check mode',
);

console.log(`readme growth claims ok: ${snapshot}`);
