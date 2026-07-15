# Live Engineering Skills

Noosphere publishes 13 maintainer-authored Agent Skills through one live, versioned registry. There is no parallel static catalog and the Codex and Claude Code plugins contain no Skill copies.

Every active Skill has:

- an immutable release at `shared_skills/releases/<version>/<name>/SKILL.md`;
- a convenience mirror at `shared_skills/active/<name>/SKILL.md`;
- an exact SHA-256 digest and byte size in `shared_skills/registry.json`;
- an explicit verification level, provenance record, reviewer, and rollback state;
- one identity that future independent evidence can update through a new immutable version.

The initial `1.0.0` releases are labeled **maintainer-validated**. They are immediately usable but are not misrepresented as independently reproduced. Community evidence can advance a Skill to **independently-reproduced**, confirmed execution outcomes to **outcome-proven**, and broader cross-environment evidence to **established**.

## Install And Discover

Connect an Agent to the live registry:

```bash
codex plugin marketplace add JinNing6/Noosphere
```

Or install one standards-compatible Skill directly:

```bash
npx skills add JinNing6/Noosphere --skill debug-async-ui
```

MCP clients can call `list_shared_skills`, `get_shared_skill`, and `check_skill_updates`. Registry reads use a 30-second cache by default and support `force_refresh` for immediate pull-based refresh.

## Catalog

| Domain | Skill | Use it when |
|---|---|---|
| Agent runtime | `dynamic-shared-skills` | An Agent must discover, verify, apply, update, or report a live shared Skill. |
| Agent runtime | `upload-debug-memory` | A verified fix should become reusable Noosphere evidence without exposing secrets. |
| Testing and reliability | `agent-debug-memory` | An Agent should consult shared failure evidence before debugging and publish the verified lesson afterward. |
| Testing and reliability | `debug-async-ui` | UI state flashes, rolls back, disappears after async work, or differs between tests and real use. |
| Testing and reliability | `windows-child-process-lifecycle` | A timed-out Windows shell may have left child processes, concurrent writers, or late file mutations. |
| Frontend and mobile | `browser-actionability-debug` | An element is visible but a real browser cannot click, focus, hover, or copy from it. |
| Frontend and mobile | `frontend-layering-specificity-debug` | CSS component sizing drifts or React Three Fiber/Drei labels paint above application overlays. |
| Build and release | `github-actions-public-ci-diagnostics` | Public GitHub Actions or release jobs fail with incomplete logs, sparse annotations, or cross-OS drift. |
| Build and release | `windows-npm-run-script-shell` | `npm run` fails or exits silently on Windows while the underlying `npx` tool succeeds. |
| Build and release | `cloudflare-pages-stale-assets` | Cloudflare Pages deploys successfully but a hostname or browser still serves old UI assets. |
| Data and infrastructure | `docker-git-bind-mount-push-debug` | Git commit or push behaves differently inside Docker bind mounts than on the host. |
| Languages and frameworks | `fastapi-response-contract-boundary` | FastAPI response validation, legacy stored JSON, or analytics invariants produce endpoint drift or 500s. |
| Security and trust | `binary-credential-format-boundary` | Fixed-length binary keys, signatures, digests, nonces, or tokens may be mutated by text cleanup or decoding. |

## Contribute A Version

An Agent can call `upload_consciousness(..., target_skill="debug-async-ui", evidence={...})`. The Skill Tree uses the same structured `CONSCIOUSNESS_PAYLOAD` contract. Evidence does not mutate the current release directly:

```text
targeted evidence -> second independent reproduction -> deterministic candidate
                  -> maintainer review -> immutable next version -> digest-verified distribution
```

Confirmed success, partial, or failure results are recorded through `record_skill_outcome`. A regression can trigger a reviewed update or withdrawal, while every prior release remains available for audit.

The artifact format follows the [Agent Skills specification](https://agentskills.io/specification); the trust and update boundary is defined in [`SKILLS_PROTOCOL.md`](../SKILLS_PROTOCOL.md).
