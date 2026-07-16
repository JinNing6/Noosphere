import { readFile, readdir, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { validateRegistry } from './skill_tree_registry_contract.mjs';

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const frontendDirectory = path.resolve(scriptDirectory, '..');
const repositoryRoot = path.resolve(frontendDirectory, '..');
const outputPath = path.join(frontendDirectory, 'public', 'skill-tree-index.json');

function seedNameFromPayload(payload, sourcePath) {
  const contextMatch = String(payload.context_environment || '').match(/seed-skill:([a-z0-9-]+)/i);
  if (contextMatch) return contextMatch[1].toLowerCase();

  const tags = Array.isArray(payload.tags) ? payload.tags : [];
  const namedTag = tags.find((tag) => tag !== 'seed-skill' && /^[a-z0-9]+(?:-[a-z0-9]+)+$/.test(tag));
  if (namedTag) return namedTag;
  throw new Error(`Unable to derive Seed name: ${sourcePath}`);
}

async function readVerifiedSeeds() {
  const payloadRoot = path.join(repositoryRoot, 'consciousness_payloads');
  const entries = await readdir(payloadRoot, { withFileTypes: true });
  const seeds = [];

  for (const entry of entries.filter((item) => item.isFile() && item.name.endsWith('.json'))) {
    const sourcePath = path.join(payloadRoot, entry.name);
    const payload = JSON.parse(await readFile(sourcePath, 'utf8'));
    const tags = Array.isArray(payload.tags) ? payload.tags : [];
    const isVerifiedSeed = tags.includes('seed-skill')
      && payload.trust?.status === 'verified'
      && payload.skill_candidate?.eligible === true;
    if (!isVerifiedSeed) continue;

    const issueNumber = Number(payload.publisher?.source_issue);
    if (!Number.isInteger(issueNumber) || issueNumber <= 0) {
      throw new Error(`Verified Seed is missing a source Issue: ${sourcePath}`);
    }

    const evidence = {
      symptom: String(payload.evidence?.symptom || ''),
      root_cause: String(payload.evidence?.root_cause || ''),
      fix: String(payload.evidence?.fix || ''),
      verification: String(payload.evidence?.verification || ''),
      applies_when: String(payload.evidence?.applies_when || ''),
      avoid_when: String(payload.evidence?.avoid_when || ''),
      test_commands: Array.isArray(payload.evidence?.test_commands) ? payload.evidence.test_commands : [],
      source_urls: Array.isArray(payload.evidence?.source_urls) ? payload.evidence.source_urls : [],
    };
    for (const field of ['symptom', 'root_cause', 'fix', 'verification']) {
      if (evidence[field].trim().length < 20) {
        throw new Error(`Verified Seed has insufficient ${field} evidence: ${sourcePath}`);
      }
    }
    if (evidence.test_commands.length === 0) {
      throw new Error(`Verified Seed requires at least one test command: ${sourcePath}`);
    }

    seeds.push({
      name: seedNameFromPayload(payload, sourcePath),
      description: String(payload.thought_vector_text || ''),
      context: String(payload.context_environment || ''),
      tags,
      creator: String(payload.publisher?.github_login || payload.creator_signature || ''),
      source_issue: issueNumber,
      source_url: `https://github.com/JinNing6/Noosphere/issues/${issueNumber}`,
      source_path: path.relative(repositoryRoot, sourcePath).replaceAll('\\', '/'),
      uploaded_at: String(payload.uploaded_at || ''),
      evidence,
    });
  }

  return seeds.sort((a, b) => a.source_issue - b.source_issue);
}

const registryPath = path.join(repositoryRoot, 'shared_skills', 'registry.json');
const registry = JSON.parse(await readFile(registryPath, 'utf8'));
validateRegistry(registry);

const verifiedSeeds = await readVerifiedSeeds();
const publishedNames = new Set(registry.skills.map((skill) => skill.name));
const unpublishedSeeds = verifiedSeeds.filter((seed) => !publishedNames.has(seed.name));

for (const [kind, records] of [['published', registry.skills], ['seed', unpublishedSeeds]]) {
  const names = records.map((record) => record.name);
  if (new Set(names).size !== names.length) {
    throw new Error(`Duplicate ${kind} Skill names would make the tree ambiguous`);
  }
}

const index = {
  schema_version: '1.0',
  generated_at: new Date().toISOString(),
  source: {
    repository: 'JinNing6/Noosphere',
    registry_path: 'shared_skills/registry.json',
    registry_revision: registry.revision,
  },
  published_skills: registry.skills,
  verified_seeds: unpublishedSeeds,
  counts: {
    published: registry.skills.length,
    seeds: unpublishedSeeds.length,
  },
};

await mkdir(path.dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(index, null, 2)}\n`, 'utf8');
console.log(`Built ${path.relative(repositoryRoot, outputPath)}: ${index.counts.published} live, ${index.counts.seeds} verified Seeds.`);
