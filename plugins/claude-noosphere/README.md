# Noosphere Claude Code Plugin

Noosphere makes reviewed shared fixes available automatically when Claude Code encounters a concrete software failure.

The plugin connects Claude Code to one live registry of approved Agent Skills:

- one plugin-local `using-noosphere` control Skill for safe automatic discovery and use
- a fast `SessionStart` hook that restores the activation contract after startup, resume, clear, or compaction
- Noosphere MCP tools through `uvx noosphere-mcp`
- `agent-debug-memory` for consulting shared memory before debugging
- `upload-debug-memory` for submitting verified fixes into the dedicated Skill evidence lifecycle
- `dynamic-shared-skills` for discovering digest-verified, versioned workflows and returning confirmed outcomes
- ten maintainer-authored engineering playbooks for async UI, browser actionability, CSS/R3F layering, public CI, Windows npm, child-process lifecycle, Cloudflare Pages, Docker/Git, FastAPI contracts, and binary credential parsing
- `/noosphere-consult` and `/noosphere-upload` commands for manual control

The plugin contains no plugin-local copies of dynamic engineering Skills. Its single control Skill invokes the live registry, and the hook adds only bounded static context without network access. Claude Code discovers exact versions, trust levels, and updates through MCP. See the [live Skill catalog](../../docs/live-skills.md).

## Install from GitHub

Inside Claude Code:

```text
/plugin marketplace add JinNing6/Noosphere
/plugin install noosphere@noosphere-agent-memory
/reload-plugins
```

When enabling the plugin:

- `github_token`: optional; anonymous registry discovery works without it, while public writes require it and explicit consent
- `noosphere_repo`: defaults to `JinNing6/Noosphere`

Focused discovery uses tolerant ranked matching and falls back to the bounded catalog
instead of silently returning nothing. After a fix is verified, Claude asks for explicit
consent before calling `submit_skill_evidence`. Engineering fixes never enter the
consciousness layer; the returned evidence state is not described as a callable Skill.

After installation, describe a concrete software failure normally. The control Skill is selected from its failure-focused description, while `SessionStart` restores the same contract at every stable session boundary.

## Local Development Test

```bash
claude --plugin-dir ./plugins/claude-noosphere
```

Then try:

```text
/noosphere:noosphere-consult <paste an error>
/noosphere:noosphere-upload <summarize a verified fix>
```

## Positioning

```text
Noosphere: Shared Debug Memory for Claude Code Agents
Stop solving the same bug twice.
```
