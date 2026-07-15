# Noosphere Project Memory Snapshot

Last verified: 2026-07-15 (Asia/Shanghai)

## Living Skill Tree Frontend

- Branch `codex/living-skill-tree-v1` replaces the frontend default route with an operational Living Skill Tree while preserving the complete existing 3D universe behind `?view=universe` and a persistent Universe navigation entry. Existing Issue, playground, and profile routes continue to resolve through the preserved universe application.
- The default surface is a workbench, not a marketing landing page: global search, Tree and Directory views, eight deterministic engineering domains, Skill details, version history, Agent connection guidance, and structured contribution entry points are available in English and Chinese.
- The tree index is generated only from repository truth. At verification time it contains 0 published dynamic Skills, 3 bundled repository Skills, and 3 verified Skill Seeds. Seed ingestion requires trusted review, Skill eligibility, complete symptom/root-cause/fix/verification evidence, and at least one test command; a Seed is excluded when a same-name published Skill exists.
- Community actions remain review-gated. Creating a Skill, proposing a domain, or submitting a new version opens a structured GitHub Issue; the browser never writes directly to the immutable Skill registry or claims that an unreviewed proposal is published.
- The WebGL tree uses responsive node spacing and dedicated transparent hit geometry on mobile. Playwright checks at a 390 x 844 viewport selected two vertically adjacent Skill nodes independently, and the directory search for `runtime smoke` returned the single matching verified Seed without horizontal overflow.
- The polished responsive shell fixes a CSS specificity bug where a scoped `font` shorthand overrode component button sizes, reserves real canvas width for the desktop detail drawer, and renders mobile details as content-sized bottom work sheets. At 1280 px, secondary action labels collapse without horizontal overflow while the primary Create Skill command remains visible.
- Tree labels now use semantic zoom: overview mode shows domain structure, while Skill names appear only for a selected domain, selected Skill, hover, or real search match. An empty query no longer highlights every Skill.
- Drei-projected `<Html>` labels are constrained to z-index range 1-8, below the detail and contribution drawers at z-index 50. Mobile browser verification found zero projected labels intercepting or painting over the open drawer.
- Vite was upgraded to 8.1.4 and the React plugin to 6.0.3. The default entry is 211.66 kB (65.61 kB gzip); Three.js and the former universe remain lazy-loaded. Frontend lint, production build, all ten repository frontend contract checks, both production and full dependency audits, DesignMD lint, and Git diff whitespace checks passed locally.
- This frontend is implemented and locally verified but is not yet merged or deployed. The shared Skill registry remains honestly empty until independent evidence and maintainer approval publish the first immutable dynamic Skill.

## Current Engineering State

- PR #39 merged the launch-proof work as commit `384d1e18ff7452236aeb80cd4705e0de83fee53e`. Tag `v0.7.2` is published on PyPI; Trusted Publishing run `29139140157` completed the build, OIDC publish, exact PyPI install verification, and Pages refresh dispatch successfully.
- Anonymous startup and anonymous consultation are now separate tested contracts. `consult_noosphere` uses the generated repository public index in anonymous mode, completing a read-only search in one cacheable request without consuming the unauthenticated GitHub REST API budget across dozens of permanent files.
- Authenticated consultation retains the existing fresh-Issue plus canonical-permanent-file path and local hybrid semantic search. Anonymous consultation deliberately uses lightweight BM25 and does not initialize or download the local sentence-transformer model.
- The published wheel adds `noosphere-query`, exposed as `uvx --from noosphere-mcp noosphere-query "your error"`. An exact-version, isolated, token-free install from public PyPI queried the public `main` index successfully and returned verified Issue #35 with root cause, fix, and verification evidence. The first run took about 9.2 seconds including installation of 64 packages.
- The generated public index now carries public publisher, trust, and structured engineering-evidence fields while continuing to omit raw embedding vectors and credentials.
- English and Chinese README first screens now lead with the dynamic shared Skill thesis, honest registry state, supported Agent runtimes, one read-only command, and real registry/evidence paths. The Android App and 3D universe are explicitly positioned as second-layer network visualization.
- A reproducible 20.00-second Agent Debug Memory demo now shows the Issue #35 failure, Noosphere query, evidence-backed fix, and passing regression. The GIF is 159,984 bytes and the MP4 is 98,387 bytes; source and regeneration instructions live in `docs/demo-script-20s.md` and `scripts/render-launch-demo.ps1`.

- The dynamic shared Skills implementation was merged through PR #31 as merge commit `48426f7d6fff29e836afc4aab2745d4cbf20516d` after all CLA, Python, Node, registry, migration, and supply-chain checks passed.
- Tag `v0.7.0` was published to PyPI through Trusted Publishing. A real clean `uvx` MCP handshake then exposed that the preflight gate incorrectly treated a missing optional `GITHUB_TOKEN` as fatal, so anonymous read-only startup was unavailable despite the documented contract.
- PR #32 fixed the anonymous startup regression and was merged as commit `6da816ee69c8c621ba8b84044f9be16361332df5`. Missing credentials now enter degraded anonymous read-only mode, while an explicitly configured invalid token remains fatal.
- Tag `v0.7.1` was published successfully through Trusted Publishing run `29085299535`; build, OIDC publish, exact PyPI install verification, and Pages refresh dispatch all passed.
- A public-index-only environment reported `noosphere.__version__ == 0.7.1`. A separate exact-version `uvx --from noosphere-mcp==0.7.1 noosphere-mcp` process with `GITHUB_TOKEN` removed completed the MCP handshake and returned all 45 tools, including all five dynamic shared Skill tools.
- MCP `serverInfo.version` currently reports the underlying `mcp` implementation version because FastMCP supplies its framework default. Distribution version verification is independent and correct; explicitly advertising the Noosphere package version is a non-blocking metadata follow-up.
- `shared_skills/registry.json` is intentionally empty until a candidate satisfies the evidence and independent-publisher gates and receives maintainer approval.
- Issue #33 is the public coordination seed for the first real Skill: Android GitHub Device Flow browser handoff and polling recovery. It is explicitly excluded from source evidence and asks two independent developers to submit their own verified records.
- Three maintainer-authored Skill Seeds were uploaded through the published `noosphere-mcp==0.7.1` `upload_consciousness` tool: R3F dense node picking (#35), dynamic shared Skill supply chain (#36), and public-release runtime smoke gating (#37). A second uploader run detected all three stable markers and created no duplicates.
- Issues #35-#37 passed a local structured-evidence and unsafe-instruction review, then received `trusted-review`. Remote `main` contains one stable permanent file per Issue; all three records bind publisher `JinNing6`, use `trusted-human-review`, are Skill-eligible evidence records, and have 3072-dimensional `gemini-embedding-2` vectors.
- The three records remain Seed Memories, not published Skills. They share one publisher, so the independent-publisher gate correctly leaves `shared_skills/registry.json` at revision 0 with zero Skills.
- Their promotion runs exposed an index-sync dependency boundary: `build_consciousness_index.py` imports a pure engine submodule, but package initialization eagerly imported the HTTP client and failed without `httpx`. The repair uses Python module-level lazy attribute loading so pure engine imports no longer require unrelated client dependencies while preserving `from noosphere import Noosphere`.

## Dynamic Shared Skill Lifecycle

1. `upload_consciousness` accepts structured engineering evidence: symptom, root cause, fix, verification, applicability, exclusions, test commands, and source URLs.
2. Promotion binds publisher identity to the actual GitHub Issue author. Self-declared `creator_signature` is display metadata and grants no withdrawal or publication authority.
3. One source Issue maps to `consciousness_payloads/memory_issueNNNN.json`. Repeated Issue events reconcile the existing record with GitHub blob SHA instead of creating a new file.
4. Moderation failures are fail-closed for Skill candidacy. Unverified historical promotions must pass current moderation or trusted maintainer review before trust can be upgraded.
5. Candidate clustering requires structured verified memories, a shared embedding space, all-pairs similarity of at least 0.9, two source Issues, and two independent GitHub publishers.
6. CI opens a deterministic `skill-candidate` Issue. Publication requires a write-permission maintainer applying `skill-approved`.
7. Published artifacts are immutable Agent Skills releases under `shared_skills/releases/<version>/<name>/SKILL.md`, with active mirrors and registry SHA-256 plus byte-size metadata.
8. Agents use `list_shared_skills`, `get_shared_skill`, and `check_skill_updates` for pull-based near-real-time discovery. Exact artifact bytes are verified before Skill content is returned.
9. Authenticated feedback uses `record_skill_outcome`. `request_shared_skill_withdrawal` only opens a request; a trusted maintainer must approve withdrawal. Withdrawal preserves the immutable artifact and rolls `latest` back atomically.

## Trust And Safety Boundaries

- Ordinary community memories are returned with an explicit untrusted-data warning.
- Candidate text is rejected for instruction-override, destructive command, encoded shell, private-key, and secret-like patterns; the candidate digest must match the reviewed body.
- Publish and withdrawal workflows serialize through one concurrency group and commit release, active mirror, and registry changes atomically.
- Permanent-memory promotion and withdrawal share one serialized workflow group, and both persistent-state groups use full queues so rapid events are not silently replaced while pending.
- Plugin instructions require local applicability checks, local verification, and explicit user approval before public GitHub writes or destructive operations.
- Permanent-memory withdrawal uses an author-bound request plus `consciousness_tombstones.json`; the SDK and public index both exclude tombstoned records and fail closed when an existing tombstone manifest cannot be read safely.

## Permanent Data State

- Historical migration is merged on remote `main` and remains idempotent on re-check.
- Physical permanent payload files: 44.
- Public indexed memories after the repaired synchronization: 41.
- Source-Issue-backed canonical records: 19.
- Legacy records without source Issue metadata left untouched: 25.
- Duplicate promotion files removed: 20.
- Active tombstoned Issue records at snapshot time: 0.
- The label initializer completed successfully and all 11 required memory, candidate, approval, outcome, and withdrawal labels exist.

## Verification Evidence

- `python -m pytest sdk/tests -q`: 194 passed for the published `v0.7.2` release.
- `node --test .github/scripts/*.test.cjs`: 71 passed after preserving the first-screen contribution, resonance-loop, and Share Proof contracts.
- Repository script tests: 18 passed, including launch-surface truthfulness, generated evidence projection, PyPI verifier, migration, and registry validation.
- Frontend `npm run lint` and `npm run build`: passed; Vite retains its existing large-chunk warning and npm reports 2 low plus 1 moderate dependency advisories.
- Built `noosphere_mcp-0.7.2.tar.gz` and `noosphere_mcp-0.7.2-py3-none-any.whl`; wheel inspection confirmed both `noosphere-mcp` and `noosphere-query` console entry points and the packaged `query_cli.py` module.
- Anonymous query regression: the generated canonical index returned `verified`, `Root cause`, `Fix`, `Verification`, and `Issue #35`; the temporary local HTTP server was shut down after the test.
- Public release smoke test: `uvx --isolated --from noosphere-mcp==0.7.2 noosphere-query ...` ran with both GitHub token variables removed, fetched the canonical index from public `main`, and returned all five required Issue #35 evidence markers. PyPI reports `0.7.2` as the current version.
- The reusable Windows CLI Unicode failure pattern is captured in the validated global Skill `python-cli-windows-console-encoding`: preserve the negotiated console encoding, replace unsupported glyphs, and avoid forcing UTF-8 when the parent decoder still uses a legacy code page.

- `python -m pytest sdk/tests -q`: 188 passed.
- `node --test .github/scripts/*.test.cjs`: 71 passed.
- Repository script unit tests: 27 passed.
- Shared Skill registry validator: passed.
- Permanent promotion canonicalization check: passed with no pending writes or deletes.
- Critical Ruff gate and focused shared-Skill Ruff/format checks: passed. Windows checks explicitly preserved CRLF checkout line endings; remote CI uses canonical LF.
- Local and release-workflow builds produced `noosphere_mcp-0.7.1.tar.gz` and `noosphere_mcp-0.7.1-py3-none-any.whl` successfully.
- Anonymous public-artifact smoke test: MCP initialization succeeded, `tools/list` returned 45 tools, no dynamic Skill tool was missing, and `GITHUB_TOKEN` was absent from the process environment.
- `python -S scripts/build_consciousness_index.py` passed with site-packages disabled and generated 41 unique public memories, proving the indexer no longer relies on installed `httpx` through package import side effects.
- The idempotent Seed uploader was run twice: first run created Issues #35-#37; second run returned `existing` for all three and created no additional Issue.
- Reusable methods are captured in validated global Skills `dynamic-shared-skill-supply-chain` and `release-runtime-smoke-gate`.
- GitHub Actions currently emits a Node.js 20 deprecation warning for pinned action runtimes that GitHub forces onto Node.js 24. It is non-blocking but should be removed in a maintenance PR.

## Required Deployment Steps

1. Recruit independent developers through Issue #33 and the three public Seed Memories (#35-#37). At least one other GitHub publisher must submit a separately reproduced, semantically matching evidence record before any Seed can form a candidate.
2. Let the workflow generate the deterministic candidate, inspect both independent evidence records, and apply `skill-approved` only after the security and applicability review passes.
3. Demonstrate one third-party Agent discovering and successfully reusing the published Skill; record the outcome through `record_skill_outcome` before large-scale promotion.
4. Do not describe the registry as having live published Skills until the first approved release appears in `shared_skills/registry.json` on remote `main`.
5. Handle MCP implementation-version metadata, the existing Vite chunk warning, npm dependency advisories, and GitHub Actions Node runtime deprecation in separate maintenance work; none changes the honest zero-Skill registry state.
