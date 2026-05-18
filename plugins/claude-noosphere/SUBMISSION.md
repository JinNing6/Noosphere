# Claude Plugin Submission Notes

## Listing

Name:

```text
Noosphere
```

Tagline:

```text
Shared Debug Memory for Claude Code Agents
```

Short description:

```text
Stop solving the same bug twice. Noosphere lets Claude Code consult and publish reusable debugging memories through MCP.
```

Long description:

```text
Noosphere turns verified debugging lessons into shared agent memory. Claude Code can consult past warnings, patterns, and decisions before fixing a bug, then upload the distilled lesson after the fix is verified. The plugin bundles the noosphere-mcp server, Claude Code skills, and manual slash commands for explicit memory search and upload.
```

## Review Notes

- Plugin manifest: `.claude-plugin/plugin.json`
- Marketplace manifest: `../../.claude-plugin/marketplace.json`
- MCP server: `uvx noosphere-mcp`
- Required user configuration: `github_token`
- Default memory repository: `JinNing6/Noosphere`
- Privacy policy: `../../PRIVACY.md`
- License: `../../LICENSE`

## Test Commands

```bash
claude plugin validate ./plugins/claude-noosphere
claude plugin validate .
claude --plugin-dir ./plugins/claude-noosphere
```

Inside Claude Code:

```text
/noosphere:agent-debug-memory
/noosphere:noosphere-consult <paste an error>
/noosphere:noosphere-upload <summarize a verified fix>
```
