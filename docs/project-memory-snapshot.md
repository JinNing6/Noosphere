# Noosphere Project Memory Snapshot

Last verified: 2026-07-27 (Asia/Shanghai)

## Reviewed Shared Skill Usage Metrics

- `list_shared_skills` now exposes per-Skill reviewed usage counts derived from the canonical registry Outcome counters. `usage` aggregates every immutable release, while `current_release_usage` reports the selected active version.
- The counting basis is explicitly `approved-outcome-reports`. It is an auditable lower bound and excludes discovery, downloads, and executions that were not submitted and approved; Noosphere still has no silent usage telemetry.
- `list_shared_skills(mine=true)` verifies the current GitHub token through the GitHub `/user` endpoint, filters against canonical registry originators/provenance, and returns an owner summary. Callers cannot provide another username or use a self-declared creator signature.
- A real authenticated read against public registry revision `5` resolved owner `JinNing6`, returned 15 contributed Skills, and reported one approved use: one success and zero non-success reports for `public-artifact-runtime-smoke-gate`.
- Verification includes 218 SDK tests, 24 repository tests, 102 Node workflow/supply-chain tests, registry/plugin validation, fatal Python lint, focused full Ruff checks, an MCP schema inspection showing 46 tools with the new optional `mine` field, and the authenticated remote read. This capability remains source-only until the still-pending `v0.9.1` GitHub/PyPI release.

## v0.9.1 Skill Evidence Flow — Merged and Live on `main`

- PR #68 merged as `ca50c947d7a36840bed49ee045363b29dd82b573`. Source `main`, the SDK/server manifests, and both plugin manifests now declare `0.9.1`; no GitHub Release or PyPI `0.9.1` has been published, so the public package remains `noosphere-mcp==0.9.0`.
- Engineering fixes now use the first-class, authenticated, consent-gated, idempotent `submit_skill_evidence` tool. `upload_consciousness` remains reserved for general thoughts and philosophical consciousness fragments. Issue #67 remains an historical consciousness record and was not silently migrated or reclassified.
- Skill Evidence is stored under `skill_evidence_payloads/`, excluded from `consciousness_payloads/` and the consciousness index, bound to the authenticated GitHub Issue author, and returned with an exact non-callable lifecycle state and stable URL. Community publication still requires two independent publishers; the separately reviewed maintainer track can publish only as `maintainer-validated` with zero claimed independent reproductions.
- The first live maintainer submission created Evidence Issue #69, then candidate Issue #70. Its initial label fan-out exposed duplicate serialized workflow events and four repeated pause comments. PR #71 merged as `51fbb51a61aa756c278d8db66844d7a6bb185b8d`; clients now create an unlabeled Evidence Issue, the workflow owns lifecycle labels, only `opened` and `trusted-review` execute the job, and pause comments use a stable idempotency marker.
- The second live community submission, Issue #72, verified the corrected experience: zero initial labels, one active opened run, one pause comment, one trusted-review run, and one success comment. It persisted only as `skill_evidence_payloads/memory_issue0072.json`, produced no consciousness payload and no candidate, and truthfully reports `awaiting-independent-evidence`.
- The first publication attempt for candidate #70 correctly staged the immutable artifact but failed because plugin and launch surfaces hardcoded a registry count of 14. PR #73 merged as `7afe510c78e290cd5d5e85cc0abf3b78d13325ce`; dynamic distribution surfaces no longer couple publication to a static count or revision.
- The retried publication run `30233830718` passed staging, registry/plugin validation, atomic commit, and decision recording. `shared-skill-evidence-routing@1.0.0` is live in registry revision `5` with SHA-256 `d69a9c9f749282711b5c0009816fe14d2643780d91a580a07a367d5d9f9d2b63`, byte size `2847`, one authenticated publisher, verification level `maintainer-validated`, and zero independent reproductions.
- A real anonymous query for `Agent shared engineering fix uploaded as consciousness instead of a callable Skill` returned `query_mode=ranked` and placed `shared-skill-evidence-routing@1.0.0` first with score `22`. `get_shared_skill` then fetched the exact artifact and verified the same SHA-256 against registry revision `5`.
- Verification evidence now includes 213 SDK tests, 55 repository Python tests, 102 Node workflow/supply-chain tests, registry/plugin validation, PR CI, a 46-tool Glama container handshake, three-platform validation-kit runs, two live Evidence submissions, one candidate review, one atomic Skill publication, and one real anonymous discovery/retrieval cycle.

## Launch Metadata Alignment

- Remote `main`, both source plugin manifests, the Claude marketplace manifest, SDK metadata, and server manifests declare `0.9.1`; PyPI and the latest GitHub Release remain at `0.9.0`. Explicit Claude plugin versions are cache keys, so completing distribution still requires a semantic `v0.9.1` release rather than relying on repository commits alone.
- Registry revision `5` contains 15 active Live Skills and 2 remaining verified Seeds. Plugin descriptions, badges, and launch copy intentionally use dynamic wording; repository validation checks registry entries and trust metadata directly instead of blocking growth on a mirrored count.
- The repository marketplace display name is `Noosphere Live Skills`, aligned with the current product category rather than the legacy Agent Memory entry point.
- The Codex plugin MCP companion file now uses the current `mcpServers` schema. The bundled plugin validator rejects the legacy `mcp_servers` spelling, and repository validation now guards this boundary.
- GitHub repository Topics are managed as public discovery metadata. The launch set targets Agent Skills, MCP, coding Agents, debugging, shared memory, supported Agent runtimes, and developer tooling.
- The public `noosphere-mcp==0.8.3` validation command was re-run on Windows 11 on 2026-07-20. The deterministic failure/fix boundary passed in 27.22 seconds of validation time and 29.42 seconds end to end.

## Automatic Live Skill Bootstrap

- PR #54 merged as `079177057f4a8458c07aac6827ef2b585475c221`. GitHub Release `v0.9.0` and PyPI `noosphere-mcp==0.9.0` are public.
- The product entry point is now install-once Agent behavior rather than a manual query command. When a concrete software engineering failure is present, the Agent frames the failure, discovers the live registry, retrieves one applicable immutable version, verifies its SHA-256, checks local applicability, applies the relevant guidance, and runs the real project verification.
- Codex and Claude Code contain one byte-identical plugin-local control Skill named `using-noosphere`. It contains no concrete engineering fix and is not a parallel registry. Repository validation permits only this control Skill and rejects any additional plugin-local Skill as a dynamic artifact copy.
- Codex enables implicit invocation through `agents/openai.yaml`. Claude Code declares the Skill in its manifest and runs a dependency-free, no-network `SessionStart` hook at startup, resume, clear, and compaction to restore the activation contract without fetching or executing community content during session initialization.
- Anonymous read-only discovery remains the default and does not require a GitHub token. A public memory upload, Outcome, or withdrawal request remains authenticated and requires explicit user consent at the time of the write. Digest identity never replaces local applicability checks or local verification.
- The English and Chinese repository first screens now lead with Codex and Claude Code installation, then preserve the zero-configuration query, deterministic validation command, evidence paths, Android App, and 3D universe as secondary surfaces.
- Local release-candidate verification passed 208 SDK tests, 36 repository tests, 97 Node workflow and supply-chain tests, Ruff checks and formatting, registry and migration validation, the Codex plugin validator, `claude plugin validate`, and Skill Creator validation. The built `noosphere_mcp-0.9.0-py3-none-any.whl` installed into a clean environment with no GitHub token, advertised `serverInfo.version=0.9.0`, returned all 45 tools in 4.911 seconds, and passed the deterministic public-artifact validation in 36.36 seconds. CI change detection now routes every file under both plugin roots through the shared Skill gate, including hook-only and manifest-only updates. Final PR #54 quality run `29723493617` passed Python, shared Skill, Glama container, CLA, and the public-artifact matrix on Ubuntu in 26 seconds, Windows in 54 seconds, and macOS in 40 seconds.
- Trusted Publishing run `29724085639` passed package build, SDK and supply-chain tests, OIDC publication, exact public PyPI installation, anonymous `initialize + tools/list`, validation-kit execution, and Pages dispatch. Pages run `29724171300` deployed the merge commit successfully. PyPI publishes Wheel SHA-256 `fe37999f6365a9e6cff84d40b678dc127007dfd13d17a40c536baf0f47940eaf` and sdist SHA-256 `db1f70cb4a24e9e3959d773baa8d03ae36134783a2e73dfb634a3bb9a5f322f1`.
- A separate exact-version, token-free `uvx --isolated --from noosphere-mcp==0.9.0 noosphere-query "public artifact runtime smoke gate"` run resolved the public package and returned verified Issue #37 engineering evidence from the canonical public index.

## Living Skill #001 Public Release

- PR #49 merged as `852da74a39e42d4bed082de32bb78715229f34cd`. GitHub Release `v0.8.3` and PyPI `noosphere-mcp==0.8.3` are public. Registry revision 2 contains 14 active Skills and the generated tree contains 2 remaining verified Seeds; historical Seed #37 is projected through its release evidence instead of appearing twice.
- `public-artifact-runtime-smoke-gate@1.0.0` is explicitly `maintainer-validated`, with one publisher, zero independent reproductions, zero verified external outcomes, source Issue #37, a public deterministic fixture, immutable artifact SHA-256 `09c9b9ec1925a2d624bf6f8efb2a92ce0bc41e1c2a4b64628b4d389c043836a1`, and byte size 5,086. No external or community validation is claimed.
- `uvx --from noosphere-mcp==0.8.3 noosphere-validate public-artifact-runtime-smoke-gate` reproduces the failure, applies the Skill, verifies the fixed artifact, emits canonical evidence, and generates a prefilled GitHub Issue Form link. The user only reviews the result and explicitly signs the independent-validation declaration; no repository clone, validator-owned project, GitHub token, MCP configuration, package-index account, or manual JSON transfer is required.
- PR quality run `29561588483` passed the real credential-free validation on Ubuntu in 24 seconds, macOS in 39 seconds, and Windows in 51 seconds, plus Python, frontend, Glama container, CLA, and shared Skill supply-chain gates. The earlier failed run `29561296443` was a PowerShell parsing error in an inline result-check command; the actual Windows validation had passed. A shell-portable Python checker and three focused regression tests removed that workflow boundary.
- Trusted Publishing run `29561781788` passed build, SDK and supply-chain tests, OIDC publication, exact public PyPI installation, anonymous MCP `initialize + tools/list`, growth-ledger tools, `noosphere-query`, and the token-free validation path. The public Linux runtime exposed 45 tools in 0.903 seconds and completed the validation path in 4.38 seconds. Pages deployment run `29561886125` also completed successfully.
- PyPI publishes Wheel SHA-256 `3fdf8a14f6d9d6383054a8c5ad6156fdbfea9ec681f16a6bbdd715ef27be909a` and sdist SHA-256 `796aa6e7a7107179870c0f68c400cd44656593b2f0ab89a1aecb28b8931df030`. Local release-candidate verification also passed 208 SDK tests, 28 repository tests, 93 Node supply-chain tests, registry and migration checks, Ruff, frontend lint, production build, and Skill Tree checks.
- External validation was deliberately removed as a launch prerequisite. The operating plan is now to use the public Skill against ten real external release failures, offer the 60-second reproducer as immediate help, and upgrade the trust level only when affected maintainers submit authenticated evidence through the existing gates.

## Living Skill #001 External Proof Sprint

- Issue #51 is the single public tracker for the external proof sprint. Ten active public failures were screened against the source-versus-public-artifact boundary; the board records reproduction, fix PR, maintainer response, and Noosphere Outcome separately so project activity cannot be mistaken for independent trust evidence.
- The first target, `mattdav/okflint#2`, was reproduced from the exact public artifact with `uvx --isolated --from okflint==0.3.0 okflint --help`. The released environment installed only `okflint` and `pyyaml`, then exited 1 with `ModuleNotFoundError: No module named 'beartype'` even though the CLI imports `beartype` at runtime.
- Upstream PR `mattdav/okflint#4` moves `beartype` from the development group into declared runtime dependencies and adds an installed-Wheel smoke gate to pull-request CI and the PyPI release workflow. The gate builds the Wheel, installs it into a fresh virtual environment without development dependencies, runs `uv pip check`, and starts the installed `okflint` entry point.
- Local verification of the proposed upstream fix passed Ruff, mypy, 267 tests with 94% coverage, clean-Wheel metadata inspection, dependency consistency, and `okflint --help` in an isolated environment containing only `okflint`, `pyyaml`, and `beartype`.
- The upstream maintainer has not yet confirmed or merged the fix. No independent reproduction or verified external Outcome has been added to `public-artifact-runtime-smoke-gate@1.0.0`; its trust level remains `maintainer-validated`. The next concierge target is `TSchonleber/brainctl#159` while PR #4 awaits review.

## Glama MCP Directory Recovery

- Glama's public server record was stale and unhealthy at diagnosis time: its API returned `tools: []`, treated `GITHUB_TOKEN` and `NOOSPHERE_REPO` as required, and the rendered schema still exposed only three legacy tools. The repository `glama.json` remains valid against Glama's current schema, so metadata syntax was not the failure.
- The failure was reproduced at the public-artifact boundary. A fresh `noosphere-mcp==0.8.1` environment installed 64 packages including Torch, Transformers, SciPy, NumPy, and Sentence Transformers; cold import took 72.67 seconds and a complete MCP handshake still had not returned after 244 seconds. Reusing the installed environment completed `initialize + tools/list` in 0.81 seconds and returned all 45 tools, proving the server contract was healthy but the directory scanner's cold-start budget was exceeded.
- Release `0.8.2` moves the local Sentence Transformers stack behind the `semantic` extra and keeps the default install on `mcp>=1.27,<2` plus `httpx`. Precomputed cross-modal vector search remains available without NumPy through an exact standard-library cosine fallback; installing the extra retains NumPy acceleration and local multilingual embedding generation.
- FastMCP 1.x is explicitly bound to the Noosphere package version so `initialize.serverInfo.version` no longer reports the MCP SDK version. The PyPI post-publish verifier now creates a second clean environment, installs the exact public artifact with dependencies, removes optional GitHub credentials, and requires a real `initialize + tools/list` response with the exact release version and 45 tools within 30 seconds.
- Local candidate verification passed: 206 SDK tests, 25 repository script tests, 93 Node supply-chain tests, and focused plus critical Ruff checks. A newly built `0.8.2` Wheel installed 34 lightweight distributions with none of `torch`, `transformers`, `sentence-transformers`, `scipy`, or `numpy`; its anonymous MCP handshake returned 45 tools in 0.86 seconds and reported version `0.8.2`.
- PR #45 merged as `79354887ec438ddd783fa53e0b3de542d00c13e5`. GitHub Release `v0.8.2` and PyPI `noosphere-mcp==0.8.2` are public. Trusted Publishing run `29479171135` passed build, tests, OIDC publication, and the strengthened exact public-artifact gate; the clean Linux runtime returned all 45 tools in 0.803 seconds with `serverInfo.version=0.8.2`. The published Wheel SHA-256 is `9480e191b0cd120b19ca94568aa3c23e8841ef5c64beb8c1418e243021461f5b`, and the sdist SHA-256 is `14daa6912c20fc219419d52f186e929d56745d134a3f90e05224c464603ee123`.
- Pages deployment run `29479280016` completed successfully from the release commit.
- A second Glama build notification after `0.8.2` proved that the cold-dependency repair was necessary but not sufficient. The public Glama page had synchronized the current GitHub release timestamp while its runtime snapshot still exposed the legacy three-tool release; the public API continued to return `tools: []` and the old required environment schema. This isolates the remaining failure to Glama's source-container build or runtime discovery stage rather than repository ingestion.
- The source-build failure is reproducible: `uvx --from . noosphere-mcp` at the monorepo root exits because the root is not a Python project, while `uvx --from ./sdk noosphere-mcp` builds successfully. Glama documents that directory releases build Docker images from repository source and that maintainers configure a Dockerfile, build steps, CMD, and environment schema in the server admin page.
- Branch `codex/glama-docker-build` adds a deterministic root `Dockerfile` that installs the lightweight SDK source from `sdk/`, runs as a non-root user, defaults `NOOSPHERE_REPO`, and launches `noosphere-mcp` in exec form. `.dockerignore` limits the build context to `README.md`, `LICENSE`, `sdk/pyproject.toml`, and the Python package. Registry and Smithery manifests now explicitly keep both configuration fields optional.
- The matching minimal source context installed cleanly and completed an anonymous `initialize + tools/list` handshake in 1.096 seconds with all 45 tools and `serverInfo.version=0.8.2`. PR CI now builds the actual Docker image on Linux with networking disabled at runtime and enforces the same 30-second anonymous protocol discovery contract.
- PR #47 Linux CI run `29489446322` built the repository-root image successfully. The resulting container ran with networking disabled and no GitHub token, completed `initialize + tools/list`, and exposed all 45 tools with `serverInfo.version=0.8.2`; the accompanying Python quality gate also passed.
- Follow-up run `29489548001` exposed a separate verification-harness race: the original probe wrote `initialize`, `notifications/initialized`, and `tools/list` in one batch and immediately closed stdin. The image still built successfully, but the server sometimes observed EOF after returning `initialize` and before processing `tools/list`. This explains why the same container test passed once and failed once without a runtime-code change.
- The shared public-artifact and container probe now follows the MCP lifecycle interactively: send `initialize`, wait for response `id=1`, send the initialized notification and `tools/list`, wait for response `id=2`, and only then close stdin. Reader threads drain stdout and stderr independently, reject non-JSON stdout, preserve a single bounded deadline, and terminate the child process tree on failure.
- The interactive regression suite passes 17 tests with `ResourceWarning` promoted to an error. Five consecutive source-runtime probes each returned 45 tools, and a new exact public install of `noosphere-mcp==0.8.2` completed the same anonymous handshake in 0.942 seconds.
- PR #47 run `29490131861` passed the corrected gate on GitHub's Linux runner. It rebuilt the repository-root Docker image, ran it with networking disabled and no optional credentials, completed the ordered MCP lifecycle, and discovered all 45 tools; the Python quality gate and CLA check also passed.
- PR #47 merged into `main` as `a4e9f77a1779d3e55d6c13bb066f998bc05e3994`. Immediately after the merge, the public Glama API still returned `tools: []`, the legacy description, and both environment variables as required. Glama's official release process requires a maintainer to configure the Dockerfile Admin build spec, click `Deploy`, and create a Glama Release after the test passes; a GitHub release or repository push does not replace that account-scoped step.
- Final recovery therefore requires one Glama admin deployment using the checked-in repository-root Dockerfile, followed by `Make Release`. Completion requires the public Glama API to expose 45 tools, optional authentication, and current metadata.

## Living Skill #001 Validation Kit

- PR #43 merged the first zero-setup independent validation command into `main` as commit `0b9c8e4b3cabe18fbd53c91be9a49351a46115a6`: `uvx --from noosphere-mcp noosphere-validate public-artifact-runtime-smoke-gate`.
- The validation kit requires Python 3.10+ and `uv`, but no repository clone, validator-owned project, GitHub token, MCP configuration, or package-index account. After the CLI itself is resolved, its reproduction installs only local deterministic fixture Wheels with package-index access disabled.
- The fixture proves the source-versus-artifact boundary end to end: source invocation passes; a byte-deterministic Wheel exposes a console entry point while omitting its runtime module and fails after real installation; a fixed Wheel includes the module, reports exact installed version `1.0.1`, and passes through the same entry point.
- Generated evidence contains environment, exit codes, immutable SHA-256 digests, the canonical shared test command, and two public source URLs inside the existing `CONSCIOUSNESS_PAYLOAD` markers. The dedicated `validate-skill.yml` form accepts this block and preserves the current author binding, moderation, canonical rehydration, independent-publisher, claim-agreement, and maintainer-review gates.
- The general memory contribution form remains available as a secondary path. The README first screen now gives the deterministic Skill validation route the primary contribution CTA without removing existing upload or Share Proof flows.
- Local release-candidate verification passed on Windows 11 with Python 3.12.11 and 3.13.5. A clean no-dependency install of the built `noosphere_mcp-0.8.1-py3-none-any.whl` exposed `noosphere-validate 0.8.1` and completed the full reproduction in 6.91 seconds. The fixture digests were stable at failing `66742deca82583b5e4530edba9235bc193245ff0a3b12766a53a06089ef02099` and fixed `d9aade68cae64234a5da2c848bbc868689e361bc41aebcd702baa23680963bef`.
- GitHub Release `v0.8.1` is published from the merge commit. Trusted Publishing run `29477337001` passed the build, SDK and supply-chain tests, PyPI OIDC upload, exact public-install verification, and Pages dispatch. Pages runs `29477306928` and `29477472959` both completed successfully for the merge commit.
- PyPI reports `noosphere-mcp==0.8.1` with Wheel SHA-256 `648be0f0118e3eaeb5dc79836e38c50066bda3e48acfdb528cbccfa92ca17178` and sdist SHA-256 `be4fa79da12563a0e9d4fa11f8ebcae0ec8662c81a9c2fa728de35cef0b12ddb`.
- A token-free, repository-external run resolved the exact public `0.8.1` package from the official PyPI Simple Index and completed the full validation in 7.80 seconds with the same fixture digests. The public `validate-skill.yml` Issue Form returned HTTP 200. A short initial index-propagation delay was observed immediately after publication and resolved without a package change.

## Living Skill Tree Frontend

- Branch `codex/living-skill-tree-v1` replaces the frontend default route with an operational Living Skill Tree while preserving the complete existing 3D universe behind `?view=universe` and a persistent Universe navigation entry. Existing Issue, playground, and profile routes continue to resolve through the preserved universe application.
- The default surface is a workbench, not a marketing landing page: global search, Tree and Directory views, eight deterministic engineering domains, Skill details, version history, Agent connection guidance, and structured contribution entry points are available in English and Chinese.
- The tree index is generated only from repository truth. At verification time it contains 13 Live Skills from `shared_skills/registry.json` revision 1 and 3 verified Skill Seeds. Seed ingestion requires trusted review, Skill eligibility, complete symptom/root-cause/fix/verification evidence, and at least one test command; a Seed is excluded when a same-name Live Skill exists.
- The original three Noosphere workflows plus ten maintainer-authored engineering playbooks now have immutable `1.0.0` releases, active mirrors, exact SHA-256 and byte-size records, provenance, reviewers, and rollback state. Their explicit trust level is `maintainer-validated`; they are usable but are not claimed as independently reproduced.
- At the `v0.8.0` Skill Tree release, Codex and Claude Code plugins contained no Skill copies, plugin manifests were still at `0.4.0`, and standards-compatible installers discovered 13 active mirrors. The current `0.8.3` launch metadata and 14-Skill registry state are recorded in the alignment section above.
- The SDK is prepared as `0.8.0`. Registry reads use a 30-second cache with explicit `force_refresh`, and `upload_consciousness` accepts `target_skill` so an Agent can submit evidence for an existing Skill version without crossing identity boundaries.
- Community actions remain review-gated. Creating or updating a Skill emits the same structured `CONSCIOUSNESS_PAYLOAD` used by MCP, including `target_skill` and engineering evidence; the browser never writes directly to the immutable registry. Two independent GitHub publishers, claim-level agreement, shared executable verification, canonical evidence rehydration, and maintainer approval are mandatory for a community release.
- The WebGL tree uses responsive node spacing and dedicated transparent hit geometry on mobile. Playwright checks at a 390 x 844 viewport selected two vertically adjacent Skill nodes independently, and the directory search for `runtime smoke` returned the single matching verified Seed without horizontal overflow.
- The polished responsive shell fixes a CSS specificity bug where a scoped `font` shorthand overrode component button sizes, reserves real canvas width for the desktop detail drawer, and renders mobile details as content-sized bottom work sheets. At 1280 px, secondary action labels collapse without horizontal overflow while the primary Create Skill command remains visible.
- Tree labels now use semantic zoom: overview mode shows domain structure, while Skill names appear only for a selected domain, selected Skill, hover, or real search match. An empty query no longer highlights every Skill.
- Drei-projected `<Html>` labels are constrained to z-index range 1-8, below the detail and contribution drawers at z-index 50. Mobile browser verification found zero projected labels intercepting or painting over the open drawer.
- Compact mobile Skill labels expand inward from right-edge nodes. At 390 x 844, all four Build and Release labels remained inside the viewport and a real canvas click selected `windows-npm-run-script-shell` exactly.
- Vite was upgraded to 8.1.4 and the React plugin to 6.0.3. The default entry is 212.19 kB (65.81 kB gzip); Three.js and the former universe remain lazy-loaded. Frontend lint, production build, all ten repository frontend contract checks, both production and full dependency audits, DesignMD lint, and Git diff whitespace checks passed locally.
- PR #41 merged the frontend and registry migration into `main` as commit `3bf3611124d3464b66715fada88f2861ed065f6b`. The default Skill Tree and unified live registry are now the released `v0.8.0` source state.

## Current Engineering State

- GitHub Release `v0.8.0` was published on 2026-07-16 from merge commit `3bf3611124d3464b66715fada88f2861ed065f6b`. Trusted Publishing run `29475218973` passed package and supply-chain tests, built wheel and sdist, published through PyPI OIDC, verified a public exact-version install, and dispatched the Pages refresh.
- PyPI reports `noosphere-mcp==0.8.0` as the latest version. The Release publishes the 45-tool MCP server and the unified registry containing 13 active maintainer-validated Skills plus 3 verified Seeds.
- A separate token-free post-release check installed the exact public package, read registry revision 1 with 13 Skills, digest-verified `agent-debug-memory@1.0.0`, and detected `update-available` from an older installed version. `npx --yes skills add JinNing6/Noosphere --list` independently discovered the same 13 public Skills.
- Label initialization run `29475143610` completed successfully on `main`; all 27 required memory, review, candidate, outcome, update, and withdrawal labels are present.
- Pages deployment runs `29475130777` and `29475326752` both completed successfully from merge commit `3bf3611124d3464b66715fada88f2861ed065f6b`.
- Creating the `v0.8.0` GitHub Release emitted both `release` and automatic tag `push` events because the workflow accepted both. Duplicate run `29475218962` was canceled before any PyPI upload. The release workflow is being restricted to the single `release.published` entry point so future immutable versions cannot race.

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
- Published versions through `0.8.1` report the underlying `mcp` implementation version because FastMCP supplies its framework default. Release candidate `0.8.2` explicitly advertises the Noosphere package version and verifies it through a real public-artifact MCP handshake.
- The 13 foundational Skills are live in `shared_skills/registry.json` revision 1 and distributed by `noosphere-mcp==0.8.0`.
- Issue #33 is the public coordination seed for the first real Skill: Android GitHub Device Flow browser handoff and polling recovery. It is explicitly excluded from source evidence and asks two independent developers to submit their own verified records.
- Three maintainer-authored Skill Seeds were uploaded through the published `noosphere-mcp==0.7.1` `upload_consciousness` tool: R3F dense node picking (#35), dynamic shared Skill supply chain (#36), and public-release runtime smoke gating (#37). A second uploader run detected all three stable markers and created no duplicates.
- Issues #35-#37 passed a local structured-evidence and unsafe-instruction review, then received `trusted-review`. Remote `main` contains one stable permanent file per Issue; all three records bind publisher `JinNing6`, use `trusted-human-review`, are Skill-eligible evidence records, and have 3072-dimensional `gemini-embedding-2` vectors.
- The three records remain Seed Memories and do not count as independent community releases. They share one publisher; the independent-publisher gate remains unsatisfied even though the registry now also contains 13 separately labeled maintainer-validated foundational Skills.
- Their promotion runs exposed an index-sync dependency boundary: `build_consciousness_index.py` imports a pure engine submodule, but package initialization eagerly imported the HTTP client and failed without `httpx`. The repair uses Python module-level lazy attribute loading so pure engine imports no longer require unrelated client dependencies while preserving `from noosphere import Noosphere`.

## Dynamic Shared Skill Lifecycle

1. `upload_consciousness` accepts structured engineering evidence: symptom, root cause, fix, verification, applicability, exclusions, test commands, source URLs, and an optional existing `target_skill` identity.
2. Promotion binds publisher identity to the actual GitHub Issue author. Self-declared `creator_signature` is display metadata and grants no withdrawal or publication authority.
3. One source Issue maps to `consciousness_payloads/memory_issueNNNN.json`. Repeated Issue events reconcile the existing record with GitHub blob SHA instead of creating a new file.
4. Moderation failures are fail-closed for Skill candidacy. Automated checks cover thought, context, every engineering-evidence field, commands, and URLs, but grant only `screened`; only trusted human review grants `verified`. Public consultation and the generated memory index withhold Agent-facing evidence from `screened` records.
5. Candidate clustering uses embedding similarity only for retrieval. A second deterministic gate requires claim-level agreement across symptom, root cause, fix, verification, and applicability, plus at least one normalized test command shared by two independent GitHub publishers and public HTTPS evidence URLs.
6. CI opens a deterministic `skill-candidate` Issue. Publication requires a write-permission maintainer applying `skill-approved`, a workflow-created `skill-candidate` Issue, and exact reconstruction from non-tombstoned canonical memory files before the reviewed digest can publish.
7. Published artifacts are immutable Agent Skills releases under `shared_skills/releases/<version>/<name>/SKILL.md`, with active mirrors and registry SHA-256 plus byte-size metadata.
8. Agents use `list_shared_skills`, `get_shared_skill`, and `check_skill_updates` for pull-based near-real-time discovery. The registry cache is 30 seconds and can be force-refreshed; exact artifact bytes and verification levels are returned only after SHA-256 checks.
9. Authenticated feedback uses deterministic Outcome IDs and reuses an existing Issue only when its full structured payload matches exactly; marker-only or conflicting Issues cannot spoof idempotency. Approved outcomes enter `shared_skills/outcomes.json`; only an independent success with public HTTPS evidence can advance a release to `outcome-proven`, while partial/failure outcomes set `update_needed` without mutating immutable instructions. `request_shared_skill_withdrawal` remains separately review-gated.

## Trust And Safety Boundaries

- Ordinary community memories are returned with an explicit untrusted-data warning.
- Candidate text is rejected for instruction-override, destructive command, encoded shell, private-key, and secret-like patterns; the candidate digest must match the reviewed body.
- Every workflow that writes persistent state to `main` uses the shared `noosphere-main-writer` queue, covering promotion, memory withdrawal, embedding backfill, Skill publication/withdrawal, approved Outcomes, traction snapshots, and contributor rankings.
- Embedding backfill rebuilds the complete canonical candidate set, creates missing review Issues, updates drifted candidates, and closes stale candidates as superseded.
- Withdrawal of the final active release sets `latest: null`; the frontend retains a withdrawn audit record, removes the install command, and the Pages build remains valid.
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
- The label initializer defines 27 repository labels in total, including every memory, candidate, approval, Outcome review, update-needed, supersession, and withdrawal state. The six new Outcome/candidate-state labels must be initialized on remote `main` after PR #41 merges.

## Verification Evidence

- All 13 immutable releases and active mirrors pass the Agent Skills and registry validators. `npx skills add . --list` discovers exactly 13 Skills from the repository without plugin-local copies.
- `python -m pytest sdk/tests -q`: 198 passed. GitHub workflow and supply-chain tests: 91 passed. Repository unit tests: 13 passed. Shared Skill registry and Outcome ledger validation passed. Frontend lint, production build, and Skill Tree contract checks pass with `13 live, 3 verified Seeds`.
- The generated frontend index contains no parallel static collection. Skill details expose immutable version, SHA-256, originator, and an honest lifecycle state: maintainer validated, independently reproduced, outcome proven, established, withdrawn, or Seed. A withdrawn-only Skill remains auditable but cannot be installed.

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
- Critical Ruff gate and focused shared-Skill Ruff/format checks: passed. Skill artifact digests are defined over Git-canonical LF bytes, enforced by `.gitattributes` and a CRLF/LF regression test so Windows validation matches Linux CI and GitHub raw artifacts.
- Local and release-workflow builds produced `noosphere_mcp-0.7.1.tar.gz` and `noosphere_mcp-0.7.1-py3-none-any.whl` successfully.
- Anonymous public-artifact smoke test: MCP initialization succeeded, `tools/list` returned 45 tools, no dynamic Skill tool was missing, and `GITHUB_TOKEN` was absent from the process environment.
- `python -S scripts/build_consciousness_index.py` passed with site-packages disabled and generated 41 unique public memories, proving the indexer no longer relies on installed `httpx` through package import side effects.
- The idempotent Seed uploader was run twice: first run created Issues #35-#37; second run returned `existing` for all three and created no additional Issue.
- Reusable methods are captured in validated global Skills `dynamic-shared-skill-supply-chain` and `release-runtime-smoke-gate`.
- GitHub Actions currently emits a Node.js 20 deprecation warning for pinned action runtimes that GitHub forces onto Node.js 24. It is non-blocking but should be removed in a maintenance PR.

## First Recorded Skill Outcome And External Proof Sprint

- On 2026-07-21, authenticated Outcome Issue #57 recorded the first approved public
  execution result for `public-artifact-runtime-smoke-gate@1.0.0`. Its stable Outcome ID is
  `okflint-0.3.0-to-0.3.1-20260721`, its result is `success`, and it is bound to the immutable
  release SHA-256 `09c9b9ec1925a2d624bf6f8efb2a92ce0bc41e1c2a4b64628b4d389c043836a1`.
- The exact public `okflint==0.3.0` artifact reproduced the missing-runtime-dependency failure:
  `uvx --isolated --from okflint==0.3.0 okflint --help` exited `1` with
  `ModuleNotFoundError: No module named 'beartype'`. The upstream maintainer independently
  landed the equivalent remediation in `d727ceb`, closed the affected Issue as completed,
  and released `v0.3.1`; the exact `0.3.1` command exited `0`.
- Contributor PR `mattdav/okflint#4` was closed as superseded after the upstream release. Its
  closing note explicitly avoids claiming that the maintainer adopted the PR. Outcome #57
  likewise records technical success without claiming independent Agent reuse or upstream
  use of Noosphere.
- The approved Outcome workflow advanced the public registry from revision `2` to revision
  `3` and the public Outcome ledger from `0` to `1`. The release now reports one verified
  success, zero failed outcomes, and `update_needed: false`. The reporter and approver are
  both `JinNing6`, so the verification level correctly remains `maintainer-validated`.
- External Proof Sprint Issue #51 now has three of three selected failures reproduced. For
  `brainctl==2.8.0`, a base install followed by `brainctl-mcp --help` exited `1` with a raw
  missing-`mcp` traceback, while `brainctl[mcp]==2.8.0` exited `0`. For `ahrena-mcp==0.1.0a1`,
  an isolated editable install exited `0` while its source path existed, exited `1` with
  `ModuleNotFoundError: No module named 'ahrena_mcp'` after that path was moved, and returned
  to `0` after the exact path was restored.
- Upstream `TSchonleber/brainctl#170` is now open from commit `7466aca`. It routes the
  `brainctl-mcp` console script through a narrow optional-dependency boundary, returns an
  exact `[mcp]` pip/pipx remediation with no traceback for a base-only install, preserves
  unrelated import failures, and clarifies the README install choice. Twenty-six related
  tests passed. A built `2.8.0` Wheel then proved base install exit `1`, hint present, no
  traceback, while the same Wheel installed with `[mcp]` exited `0` on `--help`.
- Upstream `guardiatechnology/ahrena#376` is now open with one GitHub-signed, Verified commit,
  `5512984`. Adopter installs use a self-contained `pipx install --force <path>`; installer
  reruns detect and automatically migrate legacy editable installs, conservatively repair an
  unreadable install mode, and preserve the previous behavior for a healthy non-editable
  install. Four focused regressions pass. An isolated real pipx lifecycle reproduced the old
  source-removal failure at exit `1`, applied the installer migration, removed both old and
  new source directories, and then kept `ahrena-mcp --help` healthy at exit `0`.
- Both upstream workflow runs currently report `action_required` with zero jobs because a
  maintainer must approve Actions for a first-time external contributor. This is neither a
  failing test result nor green CI. Both upstream Issues and PRs remain open, there is no
  maintainer response or merge claim, no Noosphere Outcome has been recorded for either case,
  and the Skill correctly remains `maintainer-validated`.
- The first recorded Outcome is a success and does not justify a `1.1.0` Skill update. The
  first externally evidenced partial or failed Outcome must still become a reviewed,
  immutable update candidate rather than mutating `1.0.0`.

## Synchronized Distribution Strategy

- On 2026-07-21, the launch strategy moved from a finite channel sequence plus manual Issue
  discovery to a proof-led synchronized distribution loop. Active Issue discovery remains a
  cold-start evidence-production method; it is not the long-term acquisition engine.
- The operating loop is: verified event -> canonical evidence packet -> channel-native media
  wave -> one install-and-use path -> public Outcome or maintainer response -> next verified
  event. Identical mass cross-posting is explicitly excluded.
- The product north star remains `Weekly External Verified Reuses`. Stars, views, downloads,
  and post impressions remain diagnostic reach signals and cannot be treated as installs,
  people, or successful reuse.
- The GitHub API baseline captured at 2026-07-21 15:59 +08:00 was 18 Stars, 1 fork, and 39
  repository views from 19 unique visitors in the current 14-day window. Top referrers were
  `github.com` at 6 views / 1 unique, Baidu at 1 / 1, and Google at 1 / 1.
- The public proof ledgers contained 0 Share Proof Issues and 0 Growth Proof Issues at that
  baseline. Outcome #57 remained the only recorded Skill Outcome and was maintainer-reported,
  so it did not raise the `maintainer-validated` trust level.
- The first synchronized packet is
  `docs/distribution-waves/live-skill-proof-20260721.md`. It combines the released okflint
  repair with open upstream brainctl PR #170 and Ahrena PR #376 while preserving their exact
  review and workflow-approval states.
- The strategy introduces no tracking SDK, cookies, fingerprinting, or inferred adoption
  metrics. Measurement uses public post URLs, GitHub's bounded 14-day traffic/referrer API,
  upstream maintainer actions, and exact-version Outcomes.
- PR #60 merged the synchronized distribution system into `main` as
  `62780cee0d2e2a5af42ecd712033fba9a3d85f38`. The first public surface is
  [Discussion #61](https://github.com/JinNing6/Noosphere/discussions/61), published in the
  repository's Show and tell category at 2026-07-21 16:37 +08:00.
- [Share Proof #62](https://github.com/JinNing6/Noosphere/issues/62) records Discussion #61
  against External Proof Sprint Issue #51. Share Proof IssueOps completed successfully, so the
  first `content -> public URL -> evidence ledger` segment is verified and the live reviewable
  Share Proof count is now 1. This proves publication only, not installs or reuse.

## Required Deployment Steps

1. After a final review of current `main`, publish GitHub Release `v0.9.1` so Trusted Publishing
   can build and verify the exact public PyPI artifact with all 46 MCP tools. Do not describe
   the source merge or live registry update as a PyPI release before that workflow succeeds.
2. Monitor and respond to review on `brainctl#170` and `Ahrena#376`. Their first workflow runs
   require upstream maintainer approval before jobs can start; do not describe `action_required`
   as a failure or a pass. Record a new Outcome only after public maintainer response, merge,
   release verification, or independently authenticated evidence. Outcome #57 is already
   recorded; do not present it as independent Noosphere reuse.
3. Upgrade `public-artifact-runtime-smoke-gate` or `shared-skill-evidence-routing` from `maintainer-validated` only after a second GitHub publisher submits independently reproduced evidence. Claim `outcome-proven` only after an exact-version third-party Agent reuse is recorded with public evidence.
4. Convert the first external failed or partial outcome into a reviewed immutable next version and demonstrate `check_skill_updates` plus digest-verified retrieval. This version transition, not raw Skill count, is the first proof of a Living Skill network.
5. Complete the separate Glama admin deployment and release so its public directory record exposes the current 46-tool source runtime rather than the stale legacy snapshot.
6. Handle the existing Vite chunk warning, npm dependency advisories, and GitHub Actions Node runtime deprecation in separate maintenance work; none blocks the `v0.9.1` release or the external-issue campaign.

## Concentrated v0.9.0 Launch Surface

- On 2026-07-20 the concentrated developer launch was prepared from remote `main` commit
  `71947ae1016a100f40ba525976151d3e244a6e50` on branch
  `codex/v090-concentrated-launch`. The older dirty Android/frontend workspace was left
  untouched in a separate worktree.
- The English and Chinese README first screens now use one promise:
  `Install once. One Agent learns. Every Agent inherits the Skill.` / `安装一次。一个 Agent
  学会，所有 Agent 继承这个 Skill。` The first screen leads with install commands,
  automatic failure-time discovery, exact artifact verification, and one real Skill case.
- The launch demo uses real public `noosphere-mcp==0.9.0` outputs. Anonymous queries returned
  registry revision `2` and `public-artifact-runtime-smoke-gate@1.0.0` with exact SHA-256
  `09c9b9ec1925a2d624bf6f8efb2a92ce0bc41e1c2a4b64628b4d389c043836a1`.
- The deterministic validation passed on `Windows 11 / AMD64 / Python 3.12.11` in `48.86s`:
  source invocation exit `0`, installed failing artifact exit `1`, and installed fixed
  artifact exit `0` with version `1.0.1`. This is maintainer validation, not external
  independent reproduction.
- Generated launch assets are reproducible from `scripts/render-v090-launch-assets.ps1`:
  a 1280 x 640 PNG social preview below GitHub's 1 MB limit, a 19-second 1280 x 720 H.264
  `yuv420p` MP4, and a 960 x 540 animated GIF. The renderer binds browser descendants to a
  Windows kill-on-close Job Object and leaves no matching child process after completion.
- `docs/launch-copy.md` and `docs/launch-pack.md` now define one-message, one-CTA launch copy
  and a 72-hour English-then-Chinese release sequence. The Android application and original
  3D universe remain secondary product surfaces and do not block the developer launch.
- Verification after the launch-surface update: `208` SDK tests passed with an isolated
  pytest base directory; `22` repository unit tests passed; README local links and images
  resolve; launch-surface truthfulness tests pass; the social preview is `1280 x 640 / 95 KB`;
  the MP4 is `19.0s / 1280 x 720 / yuv420p`; and no renderer process remains.
- After merge, upload `assets/launch/noosphere-live-skills-v090-social-preview.png` through
  GitHub repository Settings, then execute the 72-hour channel sequence. Do not change the
  current trust claim from `maintainer-validated` until linked independent evidence exists.
