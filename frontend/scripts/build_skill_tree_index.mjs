import { createHash } from 'node:crypto';
import { readFile, readdir, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const frontendDirectory = path.resolve(scriptDirectory, '..');
const repositoryRoot = path.resolve(frontendDirectory, '..');
const outputPath = path.join(frontendDirectory, 'public', 'skill-tree-index.json');

function parseFrontMatter(content, sourcePath) {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) {
    throw new Error(`Missing front matter: ${sourcePath}`);
  }

  const fields = {};
  for (const line of match[1].split(/\r?\n/)) {
    const separator = line.indexOf(':');
    if (separator < 1) continue;
    const key = line.slice(0, separator).trim();
    const value = line.slice(separator + 1).trim().replace(/^['"]|['"]$/g, '');
    fields[key] = value;
  }

  if (!fields.name || !fields.description) {
    throw new Error(`Skill front matter requires name and description: ${sourcePath}`);
  }
  return fields;
}

async function readStaticSkills() {
  const skillsRoot = path.join(repositoryRoot, 'plugins', 'noosphere', 'skills');
  const entries = await readdir(skillsRoot, { withFileTypes: true });
  const skills = [];

  for (const entry of entries.filter((item) => item.isDirectory()).sort((a, b) => a.name.localeCompare(b.name))) {
    const sourcePath = path.join(skillsRoot, entry.name, 'SKILL.md');
    const artifact = await readFile(sourcePath);
    const content = artifact.toString('utf8');
    const frontMatter = parseFrontMatter(content, sourcePath);
    skills.push({
      name: frontMatter.name,
      description: frontMatter.description,
      source_path: path.relative(repositoryRoot, sourcePath).replaceAll('\\', '/'),
      sha256: createHash('sha256').update(artifact).digest('hex'),
      size_bytes: artifact.byteLength,
    });
  }

  return skills;
}

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

function validateRegistry(registry) {
  if (registry?.schema_version !== '1.0' || !Number.isInteger(registry?.revision) || !Array.isArray(registry?.skills)) {
    throw new Error('shared_skills/registry.json does not match schema version 1.0');
  }
  for (const skill of registry.skills) {
    if (!skill?.name || !skill?.latest || !Array.isArray(skill?.releases)) {
      throw new Error(`Malformed published Skill registry entry: ${skill?.name || 'unknown'}`);
    }
  }
}

const registryPath = path.join(repositoryRoot, 'shared_skills', 'registry.json');
const registry = JSON.parse(await readFile(registryPath, 'utf8'));
validateRegistry(registry);

const [staticSkills, verifiedSeeds] = await Promise.all([
  readStaticSkills(),
  readVerifiedSeeds(),
]);
const publishedNames = new Set(registry.skills.map((skill) => skill.name));
const unpublishedSeeds = verifiedSeeds.filter((seed) => !publishedNames.has(seed.name));

for (const [kind, records] of [['published', registry.skills], ['static', staticSkills], ['seed', unpublishedSeeds]]) {
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
  static_skills: staticSkills,
  verified_seeds: unpublishedSeeds,
  counts: {
    published: registry.skills.length,
    static: staticSkills.length,
    seeds: unpublishedSeeds.length,
  },
};

await mkdir(path.dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(index, null, 2)}\n`, 'utf8');
console.log(`Built ${path.relative(repositoryRoot, outputPath)}: ${index.counts.published} published, ${index.counts.static} static, ${index.counts.seeds} verified Seeds.`);
