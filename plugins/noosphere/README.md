# Noosphere Codex Plugin

Noosphere makes reviewed shared fixes available automatically when Codex encounters a concrete software failure.

The plugin connects Codex to one live registry of approved Agent Skills:

- one plugin-local `using-noosphere` control Skill that triggers discovery, digest verification, applicability checks, and project verification
- six context-efficient Live Skills MCP tools through the backward-compatible
  `uvx noosphere-mcp` entry point with `NOOSPHERE_MCP_PROFILE=skills`
- `agent-debug-memory` for consulting shared memory before debugging
- `upload-debug-memory` for submitting verified fixes into the dedicated Skill evidence lifecycle
- `dynamic-shared-skills` for discovering digest-verified, versioned workflows and returning confirmed outcomes
- ten maintainer-authored engineering playbooks for async UI, browser actionability, CSS/R3F layering, public CI, Windows npm, child-process lifecycle, Cloudflare Pages, Docker/Git, FastAPI contracts, and binary credential parsing

The plugin contains no plugin-local copies of dynamic engineering Skills. The single control Skill is implicitly invokable and all concrete fixes remain in the live registry. Codex discovers exact versions, trust levels, and updates through MCP. See the [live Skill catalog](../../docs/live-skills.md).

The installed Python package still provides opt-in `noosphere-consciousness-mcp`,
`noosphere-ops-mcp`, and the backward-compatible 46-tool `noosphere-mcp` entry point.
They are not loaded into ordinary debugging conversations.

## Install

From any Codex environment:

```bash
codex plugin marketplace add JinNing6/Noosphere
```

Restart Codex, open the plugin directory, choose **Noosphere Live Skills**, then install **Noosphere**.

After installation, describe a real bug, failing test, build failure, package fault, or runtime incident normally. Codex will invoke `using-noosphere` when its failure trigger matches; no manual slash command is required.

## Optional Auth

Anonymous registry discovery works without a token. Focused queries use tolerant ranked
matching and fall back to the bounded catalog instead of silently returning nothing.
Catalog results include reviewed Outcome counts as a lower-bound usage metric. With a
token, `list_shared_skills(mine=true)` verifies the current GitHub identity and returns
that contributor's published Skills and lifetime reported-use totals.
Set `GITHUB_TOKEN` only for fresh Issue-layer reads or an explicitly approved public
write. Verified engineering fixes use `submit_skill_evidence`; they never enter the
consciousness layer. The token is forwarded to the Noosphere MCP server and is never
required for the default read-only path.

The plugin MCP config sets:

```json
{
  "NOOSPHERE_REPO": "JinNing6/Noosphere"
}
```

## Starter Prompts

```text
Fix this failing build.
Submit this verified fix as reusable Shared Skill evidence.
Find an approved shared Skill for this failure and verify it before use.
```
