import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const appSource = await readFile(new URL('../src/UniverseApp.tsx', import.meta.url), 'utf8');
const componentSource = await readFile(new URL('../src/components/TractionProofPanel.tsx', import.meta.url), 'utf8');
const dataSource = await readFile(new URL('../src/utils/tractionProof.ts', import.meta.url), 'utf8');
const cssSource = await readFile(new URL('../src/index.css', import.meta.url), 'utf8');
const packageSource = await readFile(new URL('../package.json', import.meta.url), 'utf8');
const deployWorkflow = await readFile(new URL('../../.github/workflows/deploy-pages.yml', import.meta.url), 'utf8');
const readmeSource = await readFile(new URL('../../README.md', import.meta.url), 'utf8');
const growthProofIssueForm = await readFile(new URL('../../.github/ISSUE_TEMPLATE/growth-proof.yml', import.meta.url), 'utf8').catch(() => '');

assert.match(
  appSource,
  /import\s+TractionProofPanel\s+from\s+'\.\/components\/TractionProofPanel'/,
  'Universe surface should import the public traction proof panel',
);
assert.match(
  appSource,
  /<TractionProofPanel\s+onOpenUploader=\{handleOpenUploader\}\s*\/>/,
  'Universe surface should render traction proof with the upload recovery action',
);

assert.match(dataSource, /traction_proof\.json/, 'traction proof data should load the generated public JSON');
assert.match(dataSource, /real_contributor_identities/, 'traction proof should expose real contributor progress');
assert.match(dataSource, /latest_velocity/, 'traction proof should expose historical velocity deltas');
assert.match(dataSource, /traction_history\.json/, 'traction proof should link to the append-only public history artifact');
assert.match(dataSource, /first_proof_action/, 'traction proof should expose the first public proof action kit');
assert.match(dataSource, /growth_issue_form_url/, 'traction proof should link to the Growth Issue Form');
assert.match(dataSource, /share_proof_form_url/, 'traction proof should link to the Share Proof Issue Form');
assert.match(dataSource, /created_growth_issue_url_placeholder/, 'traction proof should ask for the created Growth Issue proof URL');
assert.match(dataSource, /created_share_proof_issue_url_placeholder/, 'traction proof should ask for the created Share Proof Issue URL');
assert.match(dataSource, /commands_after_submission/, 'traction proof should expose exact ledger commands after issue submission');
assert.match(dataSource, /copy_ready_public_proof_post/, 'traction proof should expose a compact copy-ready public proof post');
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
assert.match(componentSource, /snapshot\.history\.latest_velocity/, 'component should render velocity from real snapshot history');
assert.match(componentSource, /Velocity/, 'component should label the historical velocity surface');
assert.match(componentSource, /First proof/, 'component should label the first public proof action kit');
assert.match(componentSource, /snapshot\.first_proof_action\.growth_issue_form_url/, 'component should link to Growth Issue Form');
assert.match(componentSource, /snapshot\.first_proof_action\.share_proof_form_url/, 'component should link to Share Proof Issue Form');
assert.match(componentSource, /copy_ready_public_proof_post/, 'component should copy the compact first proof post');
assert.match(componentSource, /createTractionProofPost/, 'component should expose a copy-ready proof report');
assert.match(componentSource, /onOpenUploader/, 'component should route viewers back into contribution');
assert.match(componentSource, /next_action_url/, 'component should link back to campaign or share-proof action');
assert.doesNotMatch(componentSource, /\b\d+\s+(downloads|reposts|referrals|installs|users|retention|rewards)\b/i, 'component must not render fake propagation metrics');

assert.match(cssSource, /\.traction-proof-panel\b/, 'traction proof panel should have a stable CSS surface');
assert.match(cssSource, /\.traction-proof-metrics\b/, 'traction proof metrics should have stable styling');
assert.match(cssSource, /\.traction-proof-first-proof\b/, 'first proof action kit should have a stable CSS surface');
assert.match(cssSource, /@media \(max-width: 1180px\)[\s\S]*\.traction-proof-panel/, 'traction proof should hide on constrained layouts');

assert.match(packageSource, /"test:traction-proof":\s*"node scripts\/check_traction_proof\.mjs"/, 'frontend package should expose the traction proof check');
assert.match(deployWorkflow, /contents:\s+read/, 'Pages build should be allowed to read public repository metadata');
assert.match(deployWorkflow, /issues:\s+read/, 'Pages build should be allowed to read public proof issues');
assert.match(deployWorkflow, /pull-requests:\s+read/, 'Pages build should be allowed to read public pull requests');
assert.match(deployWorkflow, /Build traction proof/, 'Pages workflow should generate traction_proof.json before build');
assert.match(deployWorkflow, /python scripts\/build_traction_proof\.py/, 'Pages workflow should call the traction proof builder');

const historyWorkflow = await readFile(new URL('../../.github/workflows/record-traction-history.yml', import.meta.url), 'utf8');
assert.match(historyWorkflow, /workflow_dispatch:/, 'traction history recording should be explicit and manual');
assert.match(historyWorkflow, /contents:\s+write/, 'traction history workflow should be able to commit the append-only history file');
assert.match(historyWorkflow, /python scripts\/record_traction_history\.py/, 'traction history workflow should append the generated snapshot');
assert.match(historyWorkflow, /frontend\/public\/traction_history\.json/, 'traction history workflow should commit the reviewable public history artifact');

assert.match(growthProofIssueForm, /name:\s+Record Noosphere growth proof/, 'Growth Issue Form should exist');
assert.match(growthProofIssueForm, /labels:\s+\["growth-proof"\]/, 'Growth Issue Form should declare the growth-proof label');
assert.match(growthProofIssueForm, /id:\s+public_source_url/, 'Growth Issue Form should collect a public source URL');
assert.match(growthProofIssueForm, /id:\s+target_contributors/, 'Growth Issue Form should collect a target contributor count');
assert.match(growthProofIssueForm, /record_growth_referral/, 'Growth Issue Form should show the next ledger command');
assert.doesNotMatch(growthProofIssueForm, /\b(downloads|reposts|referrals|retention|rewards|installs)\s*[:=]\s*\d+/i, 'Growth Issue Form must not define fake adoption counters');

assert.match(readmeSource, /Traction Proof/i, 'README should retain documentation for the Universe traction proof surface');
assert.match(readmeSource, /traction_proof\.json/, 'README should document the real public traction artifact');
assert.match(readmeSource, /traction_history\.json/, 'README should document the append-only traction history artifact');
assert.match(readmeSource, /First Proof/i, 'README should document the first proof action kit');
assert.match(readmeSource, /growth-proof\.yml/, 'README should link the Growth Proof Issue Form');
assert.match(readmeSource, /share-proof\.yml/, 'README should link the Share Proof Issue Form');
assert.match(readmeSource, /velocity/i, 'README should explain that historical velocity comes from real snapshots');
assert.match(readmeSource, /GitHub REST API/i, 'README should state public repo metrics come from GitHub REST API');
assert.match(readmeSource, /No downloads, reposts, referrals, retention, rewards, or install counts are inferred/, 'README should disclose traction proof limits');

console.log('traction proof ok: Universe exposes real public repository and IssueOps proof data');
