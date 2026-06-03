import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const appSource = await readFile(new URL('../src/App.tsx', import.meta.url), 'utf8');
const componentSource = await readFile(new URL('../src/components/TractionProofPanel.tsx', import.meta.url), 'utf8');
const dataSource = await readFile(new URL('../src/utils/tractionProof.ts', import.meta.url), 'utf8');
const cssSource = await readFile(new URL('../src/index.css', import.meta.url), 'utf8');
const packageSource = await readFile(new URL('../package.json', import.meta.url), 'utf8');
const deployWorkflow = await readFile(new URL('../../.github/workflows/deploy-pages.yml', import.meta.url), 'utf8');
const readmeSource = await readFile(new URL('../../README.md', import.meta.url), 'utf8');

assert.match(
  appSource,
  /import\s+TractionProofPanel\s+from\s+'\.\/components\/TractionProofPanel'/,
  'homepage should import the public traction proof panel',
);
assert.match(
  appSource,
  /<TractionProofPanel\s+onOpenUploader=\{handleOpenUploader\}\s*\/>/,
  'homepage should render traction proof with the upload recovery action',
);

assert.match(dataSource, /traction_proof\.json/, 'traction proof data should load the generated public JSON');
assert.match(dataSource, /real_contributor_identities/, 'traction proof should expose real contributor progress');
assert.match(dataSource, /public share proof/, 'traction proof should name the current public proof bridge');
assert.match(dataSource, /No downloads, reposts, referrals, retention, rewards, or install counts are inferred/, 'traction proof must carry non-fabrication disclosure');
assert.match(dataSource, /createTractionProofPost/, 'traction proof should expose copy-ready public proof text');
assert.doesNotMatch(dataSource, /\b(installs|downloads|reposts|referrals|retention|rewards)\s*[:=]\s*\d+/i, 'traction proof source must not define fake adoption counters');

assert.match(componentSource, /fetchTractionProof\(\)/, 'component should fetch real traction proof data');
assert.match(componentSource, /Traction proof/, 'component should label the public traction surface');
assert.match(componentSource, /snapshot\.repo\.stars/, 'component should show real GitHub star count from the snapshot');
assert.match(componentSource, /snapshot\.share_proof\.reviewable_public_urls/, 'component should show real reviewable proof count');
assert.match(componentSource, /snapshot\.target_progress\.real_contributor_identities/, 'component should show real contributor identities');
assert.match(componentSource, /snapshot\.bottleneck\.stage/, 'component should name the weakest proof bridge');
assert.match(componentSource, /createTractionProofPost/, 'component should expose a copy-ready proof report');
assert.match(componentSource, /onOpenUploader/, 'component should route viewers back into contribution');
assert.match(componentSource, /next_action_url/, 'component should link back to campaign or share-proof action');
assert.doesNotMatch(componentSource, /\b\d+\s+(downloads|reposts|referrals|installs|users|retention|rewards)\b/i, 'component must not render fake propagation metrics');

assert.match(cssSource, /\.traction-proof-panel\b/, 'traction proof panel should have a stable CSS surface');
assert.match(cssSource, /\.traction-proof-metrics\b/, 'traction proof metrics should have stable styling');
assert.match(cssSource, /@media \(max-width: 1180px\)[\s\S]*\.traction-proof-panel/, 'traction proof should hide on constrained layouts');

assert.match(packageSource, /"test:traction-proof":\s*"node scripts\/check_traction_proof\.mjs"/, 'frontend package should expose the traction proof check');
assert.match(deployWorkflow, /contents:\s+read/, 'Pages build should be allowed to read public repository metadata');
assert.match(deployWorkflow, /issues:\s+read/, 'Pages build should be allowed to read public proof issues');
assert.match(deployWorkflow, /pull-requests:\s+read/, 'Pages build should be allowed to read public pull requests');
assert.match(deployWorkflow, /Build traction proof/, 'Pages workflow should generate traction_proof.json before build');
assert.match(deployWorkflow, /python scripts\/build_traction_proof\.py/, 'Pages workflow should call the traction proof builder');

const firstScreen = readmeSource.slice(0, 7200);
assert.match(firstScreen, /Traction Proof/i, 'README first screen should announce the public traction proof surface');
assert.match(firstScreen, /traction_proof\.json/, 'README should document the real public traction artifact');
assert.match(firstScreen, /GitHub REST API/i, 'README should state public repo metrics come from GitHub REST API');
assert.match(firstScreen, /No downloads, reposts, referrals, retention, rewards, or install counts are inferred/, 'README should disclose traction proof limits');

console.log('traction proof ok: homepage exposes real public repository and IssueOps proof data');
