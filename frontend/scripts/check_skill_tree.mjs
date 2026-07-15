import { execFileSync } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const frontendDirectory = path.resolve(scriptDirectory, '..');

execFileSync(process.execPath, [path.join(scriptDirectory, 'build_skill_tree_index.mjs')], {
  cwd: frontendDirectory,
  stdio: 'inherit',
});

const index = JSON.parse(await readFile(path.join(frontendDirectory, 'public', 'skill-tree-index.json'), 'utf8'));
const expectedCounts = {
  published: index.published_skills.length,
  static: index.static_skills.length,
  seeds: index.verified_seeds.length,
};
if (JSON.stringify(index.counts) !== JSON.stringify(expectedCounts)) {
  throw new Error(`Skill index counts do not match source arrays: ${JSON.stringify(index.counts)}`);
}

const records = [...index.published_skills, ...index.static_skills, ...index.verified_seeds];
const identities = records.map((record) => `${record.name}:${record.source_path || record.latest || ''}`);
if (new Set(identities).size !== identities.length) {
  throw new Error('Skill Tree index contains duplicate identities');
}

const foundingBundledSkills = [
  'binary-credential-format-boundary',
  'browser-actionability-debug',
  'cloudflare-pages-stale-assets',
  'debug-async-ui',
  'docker-git-bind-mount-push-debug',
  'fastapi-response-contract-boundary',
  'frontend-layering-specificity-debug',
  'github-actions-public-ci-diagnostics',
  'windows-child-process-lifecycle',
  'windows-npm-run-script-shell',
];
const bundledByName = new Map(index.static_skills.map((skill) => [skill.name, skill]));
for (const name of foundingBundledSkills) {
  const skill = bundledByName.get(name);
  if (!skill) throw new Error(`Missing founding bundled Skill: ${name}`);
  if (!/^[a-f0-9]{64}$/.test(skill.sha256) || !Number.isInteger(skill.size_bytes) || skill.size_bytes <= 0) {
    throw new Error(`Bundled Skill lacks immutable artifact metadata: ${name}`);
  }
}

for (const seed of index.verified_seeds) {
  for (const field of ['symptom', 'root_cause', 'fix', 'verification']) {
    if (seed.evidence?.[field]?.trim().length < 20) throw new Error(`${seed.name} lacks ${field} evidence`);
  }
  if (!Array.isArray(seed.evidence?.test_commands) || seed.evidence.test_commands.length === 0) {
    throw new Error(`${seed.name} lacks executable verification commands`);
  }
}

const appSource = await readFile(path.join(frontendDirectory, 'src', 'App.tsx'), 'utf8');
if (!appSource.includes("lazy(() => import('./UniverseApp'))") || !appSource.includes('return <SkillTreeApp />')) {
  throw new Error('Default Skills route or lazy legacy Universe route is missing');
}

const detailSource = await readFile(path.join(frontendDirectory, 'src', 'features', 'skill-tree', 'SkillDetailPanel.tsx'), 'utf8');
if (!detailSource.includes("record.kind === 'published' || record.kind === 'bundled'")) {
  throw new Error('Seed install honesty gate is missing');
}

const treeAppSource = await readFile(path.join(frontendDirectory, 'src', 'features', 'skill-tree', 'SkillTreeApp.tsx'), 'utf8');
if (!treeAppSource.includes('if (nextQuery.trim()) setSelectedDomainId(null)')) {
  throw new Error('Global search must clear a stale domain filter');
}
if (!treeAppSource.includes("hasQuery ? new Set(matchingRecords.map((record) => record.id)) : new Set<string>()")) {
  throw new Error('An empty query must not visually promote every Skill as a match');
}
if (!treeAppSource.includes('skill-app-panel-open')) {
  throw new Error('Wide layouts must reserve the tree surface for an open detail panel');
}

const sceneSource = await readFile(path.join(frontendDirectory, 'src', 'features', 'skill-tree', 'SkillTreeScene.tsx'), 'utf8');
if (!sceneSource.includes('zIndexRange={TREE_LABEL_Z_RANGE}')) {
  throw new Error('Projected tree labels must remain below DOM drawers');
}
if (!sceneSource.includes("skill-tree-skill-label-compact")) {
  throw new Error('Compact tree labels must expand inward from right-edge nodes');
}

const styleSource = await readFile(path.join(frontendDirectory, 'src', 'features', 'skill-tree', 'skill-tree.css'), 'utf8');
if (styleSource.includes('.skill-app select { font: inherit;')) {
  throw new Error('A high-specificity font shorthand would override component button sizes');
}
if (!styleSource.includes('.skill-app select { font-family: inherit; letter-spacing: 0; }')) {
  throw new Error('Skill controls must inherit the product typeface without overriding component sizes');
}
if (!styleSource.includes('.skill-tree-skill-label-compact > span { transform: translateX(-100%); text-align: right; }')) {
  throw new Error('Compact Skill labels must remain inside the mobile viewport');
}

const contributionSource = await readFile(path.join(frontendDirectory, 'src', 'features', 'skill-tree', 'SkillContributionPanel.tsx'), 'utf8');
for (const field of ['applies_when', 'avoid_when', 'test_commands', 'source_urls']) {
  if (!contributionSource.includes(field)) throw new Error(`Contribution flow is missing ${field}`);
}
if (!contributionSource.includes("/^https:\\/\\//i.test(value.trim())")) {
  throw new Error('Contribution flow must require at least one public HTTPS evidence URL');
}

console.log(`Skill Tree checks passed: ${expectedCounts.published} published, ${expectedCounts.static} bundled, ${expectedCounts.seeds} verified Seeds.`);
