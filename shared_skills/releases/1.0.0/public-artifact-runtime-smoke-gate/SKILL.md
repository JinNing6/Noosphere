---
name: public-artifact-runtime-smoke-gate
description: Verify Python packages, CLIs, MCP servers, and Agent plugins through the exact installed artifact and real runtime contract. Use when source tests pass but a published release may omit modules, expose broken entry points, depend on local paths, fail without optional credentials, or behave differently after public installation.
---

# Public Artifact Runtime Smoke Gate

Prove the artifact users install, not the source tree that produced it. Treat source tests, built artifacts, public-index resolution, installed entry points, and runtime protocol behavior as separate evidence layers.

## Required Gate

1. Identify the intended immutable release commit, version, and public registry.
2. Wait for that exact version to appear in the public registry with bounded retries.
3. Create a clean environment outside the repository and disable local project discovery.
4. Install the exact public version with caches disabled where the package manager permits.
5. Read the installed distribution's version from its own metadata.
6. Launch the installed console entry point as a subprocess. Do not substitute `python -m` against the checkout.
7. Remove optional credentials from the child environment and verify the documented anonymous or degraded behavior.
8. Exercise a representative runtime contract. For MCP stdio, send `initialize`, wait for its response, send `notifications/initialized`, then request `tools/list` before closing stdin.
9. Assert stable product-owned fields, required capabilities, exit status, and bounded runtime.
10. Record the exact version, command, environment, artifact digest, observed failure, observed success, and verification result.

## One-Minute Reproduction

Use Noosphere's deterministic fixture to reproduce the source-versus-artifact failure and verify the repair without a project or token:

```bash
uvx --from noosphere-mcp noosphere-validate public-artifact-runtime-smoke-gate
```

The command must finish in under 60 seconds on the supported CI runners. It builds byte-deterministic failing and fixed Wheels, installs them in an isolated environment without external package resolution, invokes the real installed entry point, verifies the exact distribution version, and emits a prefilled evidence submission link.

## Isolation Rules

- Never use an editable install, repository import path, local Wheel, or unversioned `latest` install as final public-release evidence.
- Run from a directory that cannot import the checkout accidentally.
- Strip optional secrets such as `GITHUB_TOKEN` and `GH_TOKEN`; never print credential values.
- Verify package metadata independently from framework-owned protocol metadata.
- Reject non-protocol data on MCP stdout because logs corrupt stdio framing.
- Drain stdout and stderr concurrently and terminate the process tree on timeout.
- Keep heavyweight models, browser stacks, GPU runtimes, and scientific packages behind explicit extras when they are not required for cold discovery.

## Failure Classification

| Observation | Classify first as | Inspect |
|---|---|---|
| Exact version cannot be resolved | Registry propagation | Registry JSON, index selection, retry window |
| Source runs but installed entry point fails | Artifact drift | Wheel contents, package data, entry-point target |
| Process exits before protocol initialization | Runtime startup | Dependencies, environment, auth preflight, transport |
| Initialize succeeds but discovery fails | Lifecycle or contract | Message ordering, stdin lifetime, stdout purity |
| Anonymous run fails while authenticated run works | Auth boundary | Required versus optional credentials, degraded mode |
| Warm retry passes after cold failure | Cold-start boundary | Dependency weight, downloads, caches, scanner timeout |
| Runtime succeeds but assertion references the wrong field | Harness contract | Production code and tests, field ownership, exit codes |

Do not change production code when the smoke harness guessed the contract incorrectly. Correct the harness from production-owned evidence, then rerun the complete gate.

## Completion Standard

The release is verified only when all of these are true:

- the public registry exposes the exact intended version;
- an isolated environment reports that installed distribution version;
- the installed entry point starts without source-tree assistance;
- the representative runtime or protocol contract completes within its deadline;
- missing optional credentials produce the documented behavior;
- required capabilities and product-owned metadata match the release contract;
- the commands, digests, exit statuses, and machine-readable result are retained;
- CI and a clean public-artifact run both pass.

## Trust Boundary

This `1.0.0` release is **maintainer-validated**. That means its immutable artifact, deterministic fixture, test command, digest, and review state are public. It does not claim independent reproduction until evidence arrives from the required independent GitHub publishers and passes maintainer review.
