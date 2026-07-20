# v0.9.0 Automatic Live Skill Demo

This document is the evidence boundary and shot list for:

- `assets/launch/noosphere-live-skills-v090-demo.gif`
- `assets/launch/noosphere-live-skills-v090-demo.mp4`
- `assets/launch/noosphere-live-skills-v090-social-preview.png`

## Claim Boundary

The demo is a time-compressed reconstruction built from real public `noosphere-mcp==0.9.0`
outputs captured on 2026-07-20. It demonstrates the automatic failure-time workflow defined
by the byte-identical Codex and Claude Code `using-noosphere` control Skill. It is not a
recording of an external user and does not claim independent reproduction.

The featured release is:

- Skill: `public-artifact-runtime-smoke-gate@1.0.0`
- Registry revision: `2`
- Verification level: `maintainer-validated`
- SHA-256: `09c9b9ec1925a2d624bf6f8efb2a92ce0bc41e1c2a4b64628b4d389c043836a1`

## Real Commands

The public package was queried without a GitHub token:

```powershell
uv run --isolated --with noosphere-mcp==0.9.0 python -
```

The Python process called `list_shared_skills("public artifact runtime", force_refresh=True)`
and `get_shared_skill("public-artifact-runtime-smoke-gate", "1.0.0", force_refresh=True)`.
Both calls returned the registry revision and exact digest shown above.

The deterministic validation was executed with:

```powershell
uvx --from noosphere-mcp==0.9.0 noosphere-validate public-artifact-runtime-smoke-gate
```

Observed result on the recorded environment:

| Field | Value |
|---|---|
| Result | `PASS` |
| Environment | `Windows 11 / AMD64 / Python 3.12.11` |
| Duration | `48.86s` |
| Source invocation | exit `0` |
| Installed failing artifact | exit `1` |
| Installed fixed artifact | exit `0`, version `1.0.1` |
| Failing artifact SHA-256 | `66742deca82583b5e4530edba9235bc193245ff0a3b12766a53a06089ef02099` |
| Fixed artifact SHA-256 | `d9aade68cae64234a5da2c848bbc868689e361bc41aebcd702baa23680963bef` |

No repository clone, validator-owned project, GitHub token, or external package index was
used by the deterministic fixture.

## Shot List

| Time | Evidence shown |
|---:|---|
| 0-3s | Source invocation succeeds while the exact installed failing artifact exits non-zero. |
| 3-7s | `using-noosphere` discovers the applicable immutable Skill from registry revision 2. |
| 7-10s | The Agent retrieves `1.0.0` and verifies its exact SHA-256. |
| 10-15s | The isolated fixture applies the artifact-runtime gate and proves failing versus fixed behavior. |
| 15-19s | The fixed artifact passes and the install-once product promise is shown. |

## Regeneration

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/render-v090-launch-assets.ps1
```

The renderer uses a local Edge or Chrome process and `ffmpeg`. Both processes run in the
foreground and exit before the script returns. Temporary scene frames are deleted only
after their resolved path is verified to be inside the operating-system temporary directory.
