import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const appSource = await readFile(new URL('../src/UniverseApp.tsx', import.meta.url), 'utf8');
const componentSource = await readFile(new URL('../src/components/ShareProofWall.tsx', import.meta.url), 'utf8');
const dataSource = await readFile(new URL('../src/utils/shareProofs.ts', import.meta.url), 'utf8');
const cssSource = await readFile(new URL('../src/index.css', import.meta.url), 'utf8');
const packageSource = await readFile(new URL('../package.json', import.meta.url), 'utf8');
const deployWorkflow = await readFile(new URL('../../.github/workflows/deploy-pages.yml', import.meta.url), 'utf8');
const readmeSource = await readFile(new URL('../../README.md', import.meta.url), 'utf8');

assert.match(
  appSource,
  /import\s+ShareProofWall\s+from\s+'\.\/components\/ShareProofWall'/,
  'Universe surface should import the share proof wall',
);
assert.match(appSource, /<ShareProofWall\s*\/>/, 'Universe surface should render the share proof wall');

assert.match(dataSource, /share_proofs\.json/, 'share proof data should load the generated public JSON');
assert.match(dataSource, /reviewable_public_urls/, 'share proof summary should expose real reviewable URL count');
assert.match(dataSource, /missing_or_invalid_urls/, 'share proof summary should disclose invalid proof count');
assert.match(dataSource, /No downloads, reposts, referrals, retention, rewards, or install counts are inferred/, 'share proof data must carry non-fabrication disclosure');
assert.doesNotMatch(dataSource, /\b(installs|downloads|reposts|referrals|retention|rewards)\s*[:=]\s*\d+/i, 'share proof data must not define fake adoption counters');

assert.match(componentSource, /fetchShareProofIndex\(\)/, 'component should fetch real share proof data');
assert.match(componentSource, /Share proof wall/, 'component should label the public surface');
assert.match(componentSource, /summary\.reviewable_public_urls/, 'component should show real reviewable URL count');
assert.match(componentSource, /proof\.share_url/, 'component should link to public proof URLs');
assert.match(componentSource, /proof\.issue_url/, 'component should link to reviewable GitHub Issues');
assert.match(componentSource, /createShareProofWallPost/, 'component should expose copy-ready share text');
assert.match(componentSource, /Open Share Proof Form/, 'component should route viewers back into the proof loop');
assert.doesNotMatch(componentSource, /\b\d+\s+(downloads|reposts|referrals|installs|users|retention|rewards)\b/i, 'component must not render fake propagation metrics');

assert.match(cssSource, /\.share-proof-wall\b/, 'share proof wall should have a stable CSS surface');
assert.match(cssSource, /\.share-proof-card\b/, 'share proof entries should have stable styling');

assert.match(packageSource, /"test:share-proof":\s*"node scripts\/check_share_proof_wall\.mjs"/, 'frontend package should expose the share proof check');
assert.match(deployWorkflow, /issues:\s+read/, 'Pages build should be allowed to read public proof issues with GITHUB_TOKEN');
assert.match(deployWorkflow, /Build share proof index/, 'Pages workflow should generate share_proofs.json before build');
assert.match(deployWorkflow, /python scripts\/build_share_proof_index\.py/, 'Pages workflow should call the share proof builder');

assert.match(readmeSource, /Share Proof Wall/i, 'README should announce the public proof wall');
assert.match(readmeSource, /share_proofs\.json/, 'README should document the real proof data artifact');
assert.match(readmeSource, /No downloads, reposts, referrals, retention, rewards, or install counts are inferred/, 'README should disclose proof limits');

console.log('share proof wall ok: homepage is wired to real public issue proof data');
