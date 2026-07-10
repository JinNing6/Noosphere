# Noosphere Codex Plugin

Noosphere turns debugging experience into shared agent memory and review-gated dynamic Skills for Codex.

The plugin bundles:

- Noosphere MCP tools through `uvx noosphere-mcp`
- `agent-debug-memory` for consulting shared memory before debugging
- `upload-debug-memory` for publishing verified lessons after a fix
- `dynamic-shared-skills` for discovering digest-verified, versioned workflows and returning confirmed outcomes

## Install

From any Codex environment:

```bash
codex plugin marketplace add JinNing6/Noosphere
```

Restart Codex, open the plugin directory, choose **Noosphere Agent Memory**, then install **Noosphere**.

## Auth

Set `GITHUB_TOKEN` in the environment where Codex starts. The token is forwarded to the Noosphere MCP server and is used to read and create public GitHub issues in `JinNing6/Noosphere`.

The bundled MCP config sets:

```json
{
  "NOOSPHERE_REPO": "JinNing6/Noosphere"
}
```

## Starter Prompts

```text
Consult Noosphere before fixing this bug.
Upload this fix as reusable debug memory.
Find an approved shared Skill for this failure and verify it before use.
```
