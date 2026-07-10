# Noosphere Claude Code Plugin

Noosphere gives Claude Code shared debug memory and review-gated dynamic Skills.

The plugin bundles:

- Noosphere MCP tools through `uvx noosphere-mcp`
- `agent-debug-memory` for consulting shared memory before debugging
- `upload-debug-memory` for publishing verified lessons after a fix
- `dynamic-shared-skills` for discovering digest-verified, versioned workflows and returning confirmed outcomes
- `/noosphere-consult` and `/noosphere-upload` commands for manual control

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
