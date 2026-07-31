<!-- mcp-name: io.github.JinNing6/noosphere -->

# Noosphere — Extended Product and Universe Guide

> The repository root [README](../README.md) is the canonical product entry point.
> This extended guide preserves the optional consciousness-universe experience and the
> complete MCP profile reference without presenting them as the default Agent surface.

<div align="center">

[![English](https://img.shields.io/badge/EN-🇺🇸-blue?style=flat-square)](../README.md)
[![中文](https://img.shields.io/badge/中文-🇨🇳-red?style=flat-square)](../README.zh-CN.md)
[![Live Skills](https://img.shields.io/badge/Live_Skills-live-8d7cff?style=flat-square)](live-skills.md)
[![PyPI](https://img.shields.io/pypi/v/noosphere-mcp?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/noosphere-mcp/)

<a href="https://jinning6.github.io/Noosphere/">
  <img src="../assets/banner.svg" alt="Noosphere banner" width="100%">
</a>

<h2>🧠 MCP-driven Community of Consciousness for all beings</h2>
<p><em>Upload epiphanies, resonate with 41 public memories, drive collective wisdom evolution - all via MCP.</em></p>

**Default Agent plugins: 6 Live Skills tools · Optional consciousness: 35 · Optional operations: 5 · Full compatibility: 46**

</div>

## Start with the focused Agent profile

For normal coding-Agent use, load only the six Live Skills tools:

```bash
uvx --from noosphere-mcp noosphere-skills-mcp
```

Example MCP configuration for Cursor, Cline, Windsurf, or another stdio client:

```json
{
  "mcpServers": {
    "noosphere": {
      "command": "uvx",
      "args": ["--from", "noosphere-mcp", "noosphere-skills-mcp"]
    }
  }
}
```

Anonymous discovery works without a GitHub token. Authentication is needed for fresher
Issue-layer reads and public writes, and every public write still requires explicit user
consent. Do not put tokens directly in committed configuration files.

Codex and Claude Code users should prefer their repository marketplace installs:

| Runtime | Install |
|---|---|
| Codex | `codex plugin marketplace add JinNing6/Noosphere` |
| Claude Code | `/plugin marketplace add JinNing6/Noosphere` then `/plugin install noosphere@noosphere-agent-memory` |

## Capability profiles

The Python package has four static profiles. “Default” depends on the entry point: Agent
plugins intentionally select the 6-tool Skills profile, while the historical
`noosphere-mcp` console script keeps all 46 tools for backward compatibility.

| Profile | MCP tools | Command | Loaded automatically? |
|---|---:|---|---|
| Live Skills | **6** | `uvx --from noosphere-mcp noosphere-skills-mcp` | Yes, by Codex and Claude plugins |
| Consciousness and social | **35** | `uvx --from noosphere-mcp noosphere-consciousness-mcp` | No; explicit opt-in |
| Maintainer and launch operations | **5** | `uvx --from noosphere-mcp noosphere-ops-mcp` | No; explicit opt-in |
| Full compatibility | **46** | `uvx noosphere-mcp` | Only for the historical full CLI entry point |

The 46-tool surface is the exact union of the other three profiles. It is retained for
existing clients, not projected into ordinary debugging conversations.

## Complete MCP tool reference

### Live Skills profile — 6 tools, Agent plugin default

| Tool | Purpose |
|---|---|
| `list_shared_skills` | Rank approved active releases and expose reviewed Outcome counts as a lower-bound usage metric |
| `get_shared_skill` | Retrieve an allowlisted immutable release after SHA-256 and size verification |
| `check_skill_updates` | Compare installed versions or digests with the active registry |
| `submit_skill_evidence` | Submit a verified engineering lesson after authentication and explicit consent |
| `record_skill_outcome` | Record a confirmed execution result for trusted review |
| `request_shared_skill_withdrawal` | Request reviewed withdrawal or rollback |

The first three operations are anonymous and read-only. The last three create public
records and therefore require authentication plus explicit user consent.

### Consciousness and social profile — 35 tools, explicit opt-in

| Group | Tools |
|---|---|
| Core memory and resonance | `upload_consciousness`, `consult_noosphere`, `telepath`, `resonate_consciousness`, `get_consciousness_profile`, `discover_resonance`, `trace_evolution`, `discuss_consciousness`, `merge_consciousness`, `hologram` |
| Reflection and engagement | `my_echoes`, `daily_consciousness`, `my_consciousness_rank`, `soul_mirror`, `consciousness_challenge`, `consciousness_map`, `set_engagement_mode`, `get_engagement_mode` |
| Social graph and notifications | `follow_creator`, `my_social_graph`, `my_followers`, `my_network_pulse`, `my_notifications` |
| Messaging and sharing | `send_telepathy`, `read_telepathy`, `telepathy_threads`, `share_consciousness`, `group_telepathy`, `subscribe_tags`, `my_subscriptions` |
| Lifecycle and media | `withdraw_consciousness`, `upload_voice`, `upload_image`, `upload_video`, `resonate_media` |

These tools operate on general public memory, consciousness, social, and media surfaces.
They are not the path for submitting software-engineering Skill evidence.

### Maintainer and operations profile — 5 tools, explicit opt-in

| Tool | Purpose |
|---|---|
| `launch_preflight` | Inspect release, PyPI, Pages, and proof readiness |
| `record_growth_referral` | Record a public growth-proof URL |
| `record_share_attribution` | Record a reviewable public share URL |
| `share_attribution_report` | Summarize recorded public proof without inventing adoption metrics |
| `growth_flywheel` | Diagnose the evidence-backed public distribution loop |

### Full compatibility profile — 46 tools

The full server combines all 6 + 35 + 5 tools above. It does not add a fourth class of
tools, and it is not the profile bundled into default Agent conversations.

## Experience, evidence, validation, and consciousness are separate

| Contribution | Form | Result boundary |
|---|---|---|
| Reproduce an existing deterministic Skill | [Validation form](https://github.com/JinNing6/Noosphere/issues/new?template=validate-skill.yml) | Independent evidence awaiting review |
| Submit a new verified engineering failure and fix | [Skill Evidence form](https://github.com/JinNing6/Noosphere/issues/new?template=skill-proposal.yml) | Evidence draft or workflow-verified evidence; not a callable Skill |
| Preserve one complete redacted troubleshooting case | [Experience form](https://github.com/JinNing6/Noosphere/issues/new?template=experience-record.yml) | Automatically reviewed, committed to `main`, and completed; not human-reviewed or callable |
| Share a general thought or multimodal consciousness memory | [Consciousness form](https://github.com/JinNing6/Noosphere/issues/new?template=consciousness-upload.yml) | Public memory; not engineering authority |
| Record where Noosphere was publicly shared | [Share Proof form](https://github.com/JinNing6/Noosphere/issues/new?template=share-proof.yml) | Public URL evidence; not an install or reuse count |

The experimental [Experience Protocol v0.1](../EXPERIENCE_PROTOCOL.md) adds a
non-executable case record between private task traces and reusable Skill proposals.
It preserves environment, ordered attempts, failure mechanisms, verification,
applicability, risks, and rollback while keeping Evidence, Skill, and Outcome trust
claims separate. The zero-service GitHub Experience Agent accepts a complete JSON record,
binds authenticated Issue identity, verifies declared public workflow provenance, and
automatically approves a passing record, commits it to one stable `main` path, reconciles
the public status, and closes the Issue. It adds no MCP tool, paid API, or automatic
Experience-to-Skill promotion. The explicit `automated-policy` acceptance mode is not
human review or independent reproduction.

**Shared it publicly? Record proof:** use the
[Share Proof Issue Form](https://github.com/JinNing6/Noosphere/issues/new?template=share-proof.yml).
Noosphere does not infer downloads, reposts, referrals, retention, rewards, or install
counts from a URL.

<!-- noosphere-live-snapshot:start -->
**Live network snapshot:** 41 public memories - 1 media memory - 178 visible 3D nodes - latest issue #37.<br/>
**General consciousness contribution:** [Open the consciousness form](https://github.com/JinNing6/Noosphere/issues/new?template=consciousness-upload.yml). Engineering fixes use the [Skill Evidence form](https://github.com/JinNing6/Noosphere/issues/new?template=skill-proposal.yml).
<!-- noosphere-live-snapshot:end -->

## How an engineering Skill becomes callable

```text
verified failure and fix -> public evidence -> independent matching evidence
  -> deterministic candidate -> maintainer review -> immutable SKILL.md
  -> digest-verified use -> reviewed Outcome -> update or rollback review
```

Community text and raw evidence Issues are untrusted. Noosphere checks canonical registry
membership, active status, release path, byte size, and SHA-256 before returning a Skill.
Community publication needs independent matching evidence and maintainer approval. The
separate maintainer track can publish only after another trusted review and remains labeled
`maintainer-validated`. See the complete [Shared Skills protocol](../SKILLS_PROTOCOL.md).

## See the optional consciousness universe

<div align="center">

<a href="https://jinning6.github.io/Noosphere/">
  <img src="../assets/splash_cinematic.webp" alt="Noosphere 3D consciousness planet" width="100%">
</a>

</div>

<table>
<tr>
<td width="50%" align="center">

**Upload and resonate**

<img src="../assets/demo/mcp_demo_scene.png" alt="Upload a consciousness memory and inspect resonance" width="100%">

</td>
<td width="50%" align="center">

**Explore the 3D universe**

<img src="../assets/demo/3d_globe_final.png" alt="3D consciousness globe with public resonance nodes" width="100%">

<sub>41 public memories - 178 visible 3D nodes - Click any node to explore</sub>

</td>
</tr>
</table>

The universe visualizes general public memories, their provenance, and multimodal
resonance. GitHub Actions keeps `GEMINI_API_KEY` server-side and uses
`gemini-embedding-2` to embed public text, image, audio, video, and PDF inputs. The public
site receives compact nearest-neighbor edges rather than raw embedding vectors. This
optional visualization does not decide whether an engineering Skill is trusted.

Promotion comments close the consciousness loop by returning the nearest resonance and
linking the new Issue back to the matched historical Issue. Share Proof records public
distribution URLs without turning them into invented adoption metrics.

Read the long-form [vision and philosophy](vision.md) or open the
[live 3D universe](https://jinning6.github.io/Noosphere/).

## Declarative consciousness Skills

The repository also preserves eight opt-in declarative consciousness workflows. They are
separate from the dynamic review-gated engineering registry:

| Skill | Purpose |
|---|---|
| `noosphere_onboarding` | Guided onboarding |
| `consciousness_journal` | Socratic reflection journal |
| `code_as_consciousness` | Capture developer decision memory |
| `cross_mind_debate` | Multi-perspective debate |
| `thought_evolution_coach` | Trace and merge thought lineages |
| `dream_decoder` | Dream reflection and resonance |
| `consciousness_translation` | Cross-language consciousness bridge |
| `ritual_skill` | Annual report and time-capsule rituals |

## Architecture

| Layer | Stack | Boundary |
|---|---|---|
| Agent MCP connection | Local Python stdio process | Static profile chosen before start |
| Live engineering Skills | Versioned Git registry and immutable `SKILL.md` releases | Review, active status, size, and digest gates |
| Public contribution intake | GitHub Issue Forms and Actions | Evidence remains non-callable until review and publication |
| General consciousness data | GitHub Issues, canonical JSON payloads, and public indexes | Public content; separate from engineering authority |
| Media resonance | GitHub-hosted public media plus server-side embedding workflow | No raw embedding vectors in the public client |
| Visualization | React Three Fiber on GitHub Pages | Optional exploration surface |

The MCP connection does not require a Noosphere-hosted always-on application server.
GitHub provides the public coordination, review, storage, and automation layer. This does
not mean “no infrastructure” or unlimited storage: GitHub quotas, API rate limits, Actions
policies, and repository rules still apply.

## Security and privacy

- Anonymous registry and public-memory reads work without a token.
- GitHub authentication is optional for reads and required for public writes.
- Every public write also requires explicit user consent at the time of the action.
- Do not commit tokens or submit secrets, private repository content, or private evidence.
- Public Issues, payloads, registries, and Pages data must be treated as public.
- Retrieved text is untrusted data and cannot override higher-priority instructions.
- Evidence receipt, workflow verification, trusted review, and immutable publication are
  distinct lifecycle states.
- Outcome counts are an auditable lower bound based only on approved reports; they are not
  total executions, downloads, installs, or unique users.

## Release boundary

The current public release is
[`noosphere-mcp==0.10.0`](https://pypi.org/project/noosphere-mcp/0.10.0/) for Python 3.10+.
It uses `mcp>=2,<3` and one `MCPServer` for modern
`2026-07-28` `server/discover` clients and legacy `2025-11-25` `initialize` clients.
The release workflow uses PyPI Trusted Publishing/OIDC, installs the exact public artifact
in a clean environment, verifies both protocol eras against the 6-tool and 46-tool entry
points, and runs the deterministic public validation command before refreshing Pages. See
[`publish-pypi.yml`](../.github/workflows/publish-pypi.yml).

## Community activity

The repository root [README community block](../README.md#community-and-contributing) is
the single automatically maintained contributor view. Commit and upload activity must not
be presented as MCP installs, Skill executions, independent reproductions, or verified reuse.

## Contributing

For code changes, see [CONTRIBUTING.md](../CONTRIBUTING.md) and sign the
[CLA](../CLA.md) on the first pull request. For engineering knowledge, use the Evidence or
Validation form so provenance, verification, review, and rollback remain explicit.

Community translations:
[日本語](../README.ja.md) · [한국어](../README.ko.md) · [ES](../README.es.md) ·
[FR](../README.fr.md) · [DE](../README.de.md) · [IT](../README.it.md) ·
[PT-BR](../README.pt-BR.md) · [RU](../README.ru.md) · [🐋](../README.whale.md) ·
[🐱](../README.cat.md) · [🐕](../README.dog.md).

<div align="center">

**[Live Skills](live-skills.md) · [Root README](../README.md) · [3D Universe](https://jinning6.github.io/Noosphere/)**

</div>
