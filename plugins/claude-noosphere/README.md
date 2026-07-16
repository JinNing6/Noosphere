# Noosphere Claude Code Plugin

Noosphere gives Claude Code shared debug memory and review-gated dynamic Skills.

The plugin connects Claude Code to one live registry containing 13 Agent Skills:

- Noosphere MCP tools through `uvx noosphere-mcp`
- `agent-debug-memory` for consulting shared memory before debugging
- `upload-debug-memory` for publishing verified lessons after a fix
- `dynamic-shared-skills` for discovering digest-verified, versioned workflows and returning confirmed outcomes
- ten maintainer-authored engineering playbooks for async UI, browser actionability, CSS/R3F layering, public CI, Windows npm, child-process lifecycle, Cloudflare Pages, Docker/Git, FastAPI contracts, and binary credential parsing
- `/noosphere-consult` and `/noosphere-upload` commands for manual control

The plugin contains no plugin-local Skill copies. Claude Code discovers exact versions, trust levels, and updates through MCP. See the [live Skill catalog](../../docs/live-skills.md).

## Install from GitHub

Inside Claude Code:

```text
/plugin marketplace add JinNing6/Noosphere
/plugin install noosphere@noosphere-agent-memory
/reload-plugins
```

When enabling the plugin, provide:

- `github_token`: GitHub token used by `noosphere-mcp`
- `noosphere_repo`: defaults to `JinNing6/Noosphere`

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
