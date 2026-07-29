import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const README_URL = new URL('../../README.md', import.meta.url);
const FULL_README_URL = new URL('../../docs/README_full.md', import.meta.url);
const INDEX_URL = new URL('../public/consciousness_index.json', import.meta.url);
const WIKI_URL = new URL('../src/data/wikipedia_cache.json', import.meta.url);
const KNOWLEDGE_URL = new URL('../src/data/knowledge.ts', import.meta.url);

const HERO_PATTERN =
  /<p><em>Upload epiphanies, resonate with [^<]+? all via MCP\.<\/em><\/p>/;
const SNAPSHOT_BLOCK_PATTERN =
  /<!-- noosphere-live-snapshot:start -->[\s\S]*?<!-- noosphere-live-snapshot:end -->/;
const DEMO_CAPTION_PATTERN =
  /<sub>[^\r\n<]*(?:consciousness fragments|public memories)[^\r\n<]*Click any node to explore<\/sub>/;

const readJson = async (url) => JSON.parse(await readFile(url, 'utf8'));

export async function loadGrowthSnapshotInputs() {
  const [index, wiki, knowledgeSource] = await Promise.all([
    readJson(INDEX_URL),
    readJson(WIKI_URL),
    readFile(KNOWLEDGE_URL, 'utf8'),
  ]);

  return { index, wiki, knowledgeSource };
}

export function computeGrowthSnapshot({ index, wiki, knowledgeSource }) {
  const wikiMarker = knowledgeSource.indexOf('const WIKI_NODES');
  const hardcodedSection = wikiMarker === -1 ? knowledgeSource : knowledgeSource.slice(0, wikiMarker);
  const hardcodedWikiUrls = new Set(
    Array.from(hardcodedSection.matchAll(/wiki_url:\s*'([^']+)'/g), (match) => match[1]),
  );

  const matterNodes = (knowledgeSource.match(/id:\s*'matter-/g) || []).length;
  const lifeNodes = (knowledgeSource.match(/id:\s*'life-/g) || []).length;
  const wikiNodes = Object.values(wiki).filter((entry) => !hardcodedWikiUrls.has(entry.wiki_url)).length;
  const publicMemories = index.length;
  const mediaMemories = index.filter((entry) => entry.media_type).length;
  const latestIssue = Math.max(...index.map((entry) => entry.issue_number || 0));
  const visibleNodes = matterNodes + lifeNodes + wikiNodes + publicMemories;

  return {
    publicMemories,
    mediaMemories,
    visibleNodes,
    latestIssue,
  };
}

export function formatGrowthSnapshot(metrics) {
  const mediaLabel = `${metrics.mediaMemories} media ${metrics.mediaMemories === 1 ? 'memory' : 'memories'}`;
  return `${metrics.publicMemories} public memories - ${mediaLabel} - ${metrics.visibleNodes} visible 3D nodes - latest issue #${metrics.latestIssue}`;
}

function detectLineEnding(content) {
  return content.includes('\r\n') ? '\r\n' : '\n';
}

export function buildSnapshotBlock(metrics, lineEnding = '\n') {
  return [
    '<!-- noosphere-live-snapshot:start -->',
    `**Live network snapshot:** ${formatGrowthSnapshot(metrics)}.<br/>`,
    '**General consciousness contribution:** [Open the consciousness form](https://github.com/JinNing6/Noosphere/issues/new?template=consciousness-upload.yml). Engineering fixes use the [Skill Evidence form](https://github.com/JinNing6/Noosphere/issues/new?template=skill-proposal.yml).',
    '<!-- noosphere-live-snapshot:end -->',
  ].join(lineEnding);
}

export function applyGrowthSnapshot(content, metrics) {
  const lineEnding = detectLineEnding(content);
  let next = content.replace(
    HERO_PATTERN,
    `<p><em>Upload epiphanies, resonate with ${metrics.publicMemories} public memories, drive collective wisdom evolution - all via MCP.</em></p>`,
  );

  if (!SNAPSHOT_BLOCK_PATTERN.test(next)) {
    throw new Error('Missing noosphere live snapshot marker block');
  }
  next = next.replace(SNAPSHOT_BLOCK_PATTERN, buildSnapshotBlock(metrics, lineEnding));

  next = next.replace(
    DEMO_CAPTION_PATTERN,
    `<sub>${metrics.publicMemories} public memories - ${metrics.visibleNodes} visible 3D nodes - Click any node to explore</sub>`,
  );

  return next;
}

async function updateFile(fileUrl, metrics, { check } = {}) {
  const current = await readFile(fileUrl, 'utf8');
  const next = applyGrowthSnapshot(current, metrics);
  const changed = next !== current;

  if (changed && !check) {
    await writeFile(fileUrl, next, 'utf8');
  }

  return changed;
}

export async function updateReadmeGrowthSnapshots({ check = false } = {}) {
  const metrics = computeGrowthSnapshot(await loadGrowthSnapshotInputs());
  const results = await Promise.all([
    updateFile(README_URL, metrics, { check }),
    updateFile(FULL_README_URL, metrics, { check }),
  ]);

  return {
    metrics,
    changed: results.some(Boolean),
  };
}

async function main() {
  const check = process.argv.includes('--check');
  const result = await updateReadmeGrowthSnapshots({ check });
  const snapshot = formatGrowthSnapshot(result.metrics);

  if (check && result.changed) {
    console.error(`README growth snapshot is stale: ${snapshot}`);
    return 1;
  }

  console.log(
    `${result.changed ? 'updated' : 'current'} README growth snapshot: ${snapshot}`,
  );
  return 0;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main()
    .then((code) => {
      process.exitCode = code;
    })
    .catch((error) => {
      console.error(error.message);
      process.exitCode = 1;
    });
}
