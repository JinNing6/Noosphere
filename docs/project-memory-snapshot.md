# Noosphere Project Memory Snapshot

Last verified: 2026-07-15 (Asia/Shanghai)

## Living Skill Tree Frontend

- Branch `codex/living-skill-tree-v1` replaces the frontend default route with an operational Living Skill Tree while preserving the complete existing 3D universe behind `?view=universe` and a persistent Universe navigation entry. Existing Issue, playground, and profile routes continue to resolve through the preserved universe application.
- The default surface is a workbench, not a marketing landing page: global search, Tree and Directory views, eight deterministic engineering domains, Skill details, version history, Agent connection guidance, and structured contribution entry points are available in English and Chinese.
- The tree index is generated only from repository truth. At verification time it contains 13 Live Skills from `shared_skills/registry.json` revision 1 and 3 verified Skill Seeds. Seed ingestion requires trusted review, Skill eligibility, complete symptom/root-cause/fix/verification evidence, and at least one test command; a Seed is excluded when a same-name Live Skill exists.
- The original three Noosphere workflows plus ten maintainer-authored engineering playbooks now have immutable `1.0.0` releases, active mirrors, exact SHA-256 and byte-size records, provenance, reviewers, and rollback state. Their explicit trust level is `maintainer-validated`; they are usable but are not claimed as independently reproduced.
- Codex and Claude Code plugins contain no Skill copies. Plugin and marketplace manifests are aligned at version `0.4.0`; Agents discover the same registry through MCP, while standards-compatible installers discover all 13 active mirrors under `shared_skills/active/`.
- The SDK is prepared as `0.8.0`. Registry reads use a 30-second cache with explicit `force_refresh`, and `upload_consciousness` accepts `target_skill` so an Agent can submit evidence for an existing Skill version without crossing identity boundaries.
- Community actions remain review-gated. Creating or updating a Skill emits the same structured `CONSCIOUSNESS_PAYLOAD` used by MCP, including `target_skill` and engineering evidence; the browser never writes directly to the immutable registry. Two independent GitHub publishers and maintainer approval remain mandatory for a community release.
- The WebGL tree uses responsive node spacing and dedicated transparent hit geometry on mobile. Playwright checks at a 390 x 844 viewport selected two vertically adjacent Skill nodes independently, and the directory search for `runtime smoke` returned the single matching verified Seed without horizontal overflow.
- The polished responsive shell fixes a CSS specificity bug where a scoped `font` shorthand overrode component button sizes, reserves real canvas width for the desktop detail drawer, and renders mobile details as content-sized bottom work sheets. At 1280 px, secondary action labels collapse without horizontal overflow while the primary Create Skill command remains visible.
- Tree labels now use semantic zoom: overview mode shows domain structure, while Skill names appear only for a selected domain, selected Skill, hover, or real search match. An empty query no longer highlights every Skill.
- Drei-projected `<Html>` labels are constrained to z-index range 1-8, below the detail and contribution drawers at z-index 50. Mobile browser verification found zero projected labels intercepting or painting over the open drawer.
- Compact mobile Skill labels expand inward from right-edge nodes. At 390 x 844, all four Build and Release labels remained inside the viewport and a real canvas click selected `windows-npm-run-script-shell` exactly.
- Vite was upgraded to 8.1.4 and the React plugin to 6.0.3. The default entry is 212.19 kB (65.81 kB gzip); Three.js and the former universe remain lazy-loaded. Frontend lint, production build, all ten repository frontend contract checks, both production and full dependency audits, DesignMD lint, and Git diff whitespace checks passed locally.
- This frontend and registry migration are implemented and locally verified on `codex/living-skill-tree-v1` but are not yet merged or deployed. PR #41 is the release boundary for the new default Skill Tree and unified live registry.

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
- The working branch migrates the 13 foundational Skills into `shared_skills/registry.json` revision 1. The last published `main`/PyPI state remains `v0.7.2` until PR #41 merges and `v0.8.0` is released.
- Issue #33 is the public coordination seed for the first real Skill: Android GitHub Device Flow browser handoff and polling recovery. It is explicitly excluded from source evidence and asks two independent developers to submit their own verified records.
- Three maintainer-authored Skill Seeds were uploaded through the published `noosphere-mcp==0.7.1` `upload_consciousness` tool: R3F dense node picking (#35), dynamic shared Skill supply chain (#36), and public-release runtime smoke gating (#37). A second uploader run detected all three stable markers and created no duplicates.
- Issues #35-#37 passed a local structured-evidence and unsafe-instruction review, then received `trusted-review`. Remote `main` contains one stable permanent file per Issue; all three records bind publisher `JinNing6`, use `trusted-human-review`, are Skill-eligible evidence records, and have 3072-dimensional `gemini-embedding-2` vectors.
- The three records remain Seed Memories and do not count as independent community releases. They share one publisher; the independent-publisher gate remains unsatisfied even though the registry now also contains 13 separately labeled maintainer-validated foundational Skills.
- Their promotion runs exposed an index-sync dependency boundary: `build_consciousness_index.py` imports a pure engine submodule, but package initialization eagerly imported the HTTP client and failed without `httpx`. The repair uses Python module-level lazy attribute loading so pure engine imports no longer require unrelated client dependencies while preserving `from noosphere import Noosphere`.

## Dynamic Shared Skill Lifecycle

1. `upload_consciousness` accepts structured engineering evidence: symptom, root cause, fix, verification, applicability, exclusions, test commands, source URLs, and an optional existing `target_skill` identity.
2. Promotion binds publisher identity to the actual GitHub Issue author. Self-declared `creator_signature` is display metadata and grants no withdrawal or publication authority.
3. One source Issue maps to `consciousness_payloads/memory_issueNNNN.json`. Repeated Issue events reconcile the existing record with GitHub blob SHA instead of creating a new file.
4. Moderation failures are fail-closed for Skill candidacy. Unverified historical promotions must pass current moderation or trusted maintainer review before trust can be upgraded.
5. Candidate clustering requires structured verified memories, a shared embedding space, all-pairs similarity of at least 0.9, two source Issues, and two independent GitHub publishers.
6. CI opens a deterministic `skill-candidate` Issue. Publication requires a write-permission maintainer applying `skill-approved`.
7. Published artifacts are immutable Agent Skills releases under `shared_skills/releases/<version>/<name>/SKILL.md`, with active mirrors and registry SHA-256 plus byte-size metadata.
8. Agents use `list_shared_skills`, `get_shared_skill`, and `check_skill_updates` for pull-based near-real-time discovery. The registry cache is 30 seconds and can be force-refreshed; exact artifact bytes and verification levels are returned only after SHA-256 checks.
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

- All 13 immutable releases and active mirrors pass the Agent Skills and registry validators. `npx skills add . --list` discovers exactly 13 Skills from the repository without plugin-local copies.
- `python -m pytest sdk/tests -q`: 195 passed. GitHub workflow tests: 73 passed. Repository script tests: 33 passed. Frontend lint, production build, and Skill Tree contract checks pass with `13 live, 3 verified Seeds`.
- The generated frontend index contains no parallel static collection. Skill details expose immutable version, SHA-256, originator, and an honest lifecycle state: maintainer validated, independently reproduced, outcome proven, established, or Seed.

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

1. Merge PR #41 after all remote checks pass, then publish tag/Release `v0.8.0` through Trusted Publishing.
2. Verify the public branch and PyPI artifact with anonymous `list_shared_skills`, digest-checked `get_shared_skill`, `check_skill_updates`, and standard `skills` CLI discovery of all 13 entries.
3. Recruit independent developers through Issue #33 and Seeds #35-#37. A second GitHub publisher must submit separately reproduced evidence before a Seed or targeted update can become independently reproduced.
4. Demonstrate one third-party Agent successfully reusing a Live Skill and record the exact-version outcome before claiming `outcome-proven`.
5. Handle MCP implementation-version metadata, the existing Vite chunk warning, npm dependency advisories, and GitHub Actions Node runtime deprecation in separate maintenance work; none blocks the unified registry release.
