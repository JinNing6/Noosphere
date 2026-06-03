import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const readJson = async (url) => JSON.parse(await readFile(url, 'utf8'));

const repoReadme = await readFile(new URL('../../README.md', import.meta.url), 'utf8');
const fullReadme = await readFile(new URL('../../docs/README_full.md', import.meta.url), 'utf8');
const index = await readJson(new URL('../public/consciousness_index.json', import.meta.url));
const wiki = await readJson(new URL('../src/data/wikipedia_cache.json', import.meta.url));
const knowledgeSource = await readFile(new URL('../src/data/knowledge.ts', import.meta.url), 'utf8');

const hardcodedSection = knowledgeSource.slice(0, knowledgeSource.indexOf('const WIKI_NODES'));
const hardcodedWikiUrls = new Set(
  Array.from(hardcodedSection.matchAll(/wiki_url:\s*'([^']+)'/g), (match) => match[1]),
);

const matterNodes = (knowledgeSource.match(/id:\s*'matter-/g) || []).length;
const lifeNodes = (knowledgeSource.match(/id:\s*'life-/g) || []).length;
const wikiNodes = Object.values(wiki).filter((entry) => !hardcodedWikiUrls.has(entry.wiki_url)).length;
const visibleNodes = matterNodes + lifeNodes + wikiNodes + index.length;
const mediaMemories = index.filter((entry) => entry.media_type).length;
const latestIssue = Math.max(...index.map((entry) => entry.issue_number || 0));

const mediaLabel = `${mediaMemories} media ${mediaMemories === 1 ? 'memory' : 'memories'}`;
const snapshot = `${index.length} public memories - ${mediaLabel} - ${visibleNodes} visible 3D nodes - latest issue #${latestIssue}`;
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

console.log(`readme growth claims ok: ${snapshot}`);
