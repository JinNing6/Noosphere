# Bundled Engineering Skills

Noosphere currently ships 13 maintainer-authored Agent Skills with both the Codex and Claude Code plugins. They are installable immediately and follow the open Agent Skills `SKILL.md` format.

Bundled Skills are not counted as independently reproduced dynamic Skills. The public dynamic registry remains governed by separate evidence, publisher-independence, review, immutable-release, outcome, and rollback gates.

## Install

Install the complete Noosphere plugin:

```bash
codex plugin marketplace add JinNing6/Noosphere
```

Or install one workflow through an Agent Skills-compatible installer:

```bash
npx skills add JinNing6/Noosphere --skill debug-async-ui
```

## Catalog

| Domain | Skill | Use it when |
|---|---|---|
| Agent runtime | `dynamic-shared-skills` | An Agent must discover, verify, apply, update, or report an approved shared Skill. |
| Agent runtime | `upload-debug-memory` | A verified fix should be converted into reusable Noosphere memory without exposing secrets. |
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

## Integrity And Updates

- Canonical bundled artifacts live under [`plugins/noosphere/skills/`](../plugins/noosphere/skills/).
- Claude Code receives the same named Skill set under [`plugins/claude-noosphere/skills/`](../plugins/claude-noosphere/skills/).
- The repository quality gate validates name/description constraints and rejects Codex/Claude catalog drift.
- The generated Skill Tree index records the exact SHA-256 and byte size of every bundled artifact.
- Bundled updates use normal reviewed repository commits. They do not mutate or impersonate immutable releases in [`shared_skills/registry.json`](../shared_skills/registry.json).

The format and trigger descriptions follow the [Agent Skills specification](https://agentskills.io/specification).
