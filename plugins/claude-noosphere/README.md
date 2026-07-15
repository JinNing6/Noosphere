# Noosphere Claude Code Plugin

Noosphere gives Claude Code shared debug memory and review-gated dynamic Skills.

The plugin bundles 13 Agent Skills:

- Noosphere MCP tools through `uvx noosphere-mcp`
- `agent-debug-memory` for consulting shared memory before debugging
- `upload-debug-memory` for publishing verified lessons after a fix
- `dynamic-shared-skills` for discovering digest-verified, versioned workflows and returning confirmed outcomes
- ten maintainer-authored engineering playbooks for async UI, browser actionability, CSS/R3F layering, public CI, Windows npm, child-process lifecycle, Cloudflare Pages, Docker/Git, FastAPI contracts, and binary credential parsing
- `/noosphere-consult` and `/noosphere-upload` commands for manual control

See the [complete bundled Skill catalog](../../docs/bundled-skills.md).

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
/noosphere:agent-debug-memory
/noosphere:noosphere-consult <paste an error>
```

## Positioning

```text
Noosphere: Shared Debug Memory for Claude Code Agents
Stop solving the same bug twice.
```
