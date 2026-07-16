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
Noosphere turns verified debugging lessons into shared agent memory and live, review-gated Agent Skills. Claude Code can discover 13 versioned foundational Skills, verify exact digests, check updates, report execution outcomes, and upload reproducible evidence for a new version through MCP. The plugin contains the MCP connection and manual slash commands, while Skills remain in one public immutable registry.
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
/noosphere:noosphere-consult <paste an error>
/noosphere:noosphere-upload <summarize a verified fix>
```

## Official Directory Submission Checklist

Official submission targets:

1) https://claude.com/docs/plugins/submit  
2) `claude.ai/settings/plugins/submit` (or `platform.claude.com/plugins/submit`)  
   - If these links are not reachable directly, open through an authenticated Claude session and navigate to **Settings → Plugins → Submit**.
   - Official short-link: `https://clau.de/plugin-directory-submission` (docs redirect; clicks from there open the same in-app form)

Do this in order:

1. Confirm the plugin is a public repo.
2. Confirm manifest and package structure:
   - `plugins/claude-noosphere/.claude-plugin/plugin.json`
   - `plugins/claude-noosphere/commands/*`
   - `plugins/claude-noosphere/.mcp.json`
3. Validate locally:

   ```bash
   claude plugin validate ./plugins/claude-noosphere
   ```

4. Prepare public review links:
   - Plugin repo: `https://github.com/JinNing6/Noosphere`
   - Privacy policy: `/PRIVACY.md`
   - License: `/LICENSE`
5. Submit through an in-app form, using:
   - GitHub link: `https://github.com/JinNing6/Noosphere`
   - Or upload a ZIP with plugin folder and required manifests.
6. Use this summary:

   ```text
   Noosphere: shared debug memory for Claude Code agents.
   The plugin exposes MCP tools and workflows so agents can consult/publish verified fixes and avoid repeated debugging loops.
   ```

7. Monitor review status in Claude plugin settings and reply to any follow-up comments quickly.

## Post-submission operations

- Public updates sync automatically once listed.
- Keep `README` install instructions and usage examples updated after each release.
- Track submission links + status in issue comments for team visibility.

## Copy-Paste Submission Bundle

Title:

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

Repository:

```text
https://github.com/JinNing6/Noosphere
```

Plugin path (inside repo):

```text
plugins/claude-noosphere
```

Privacy policy:

```text
https://github.com/JinNing6/Noosphere/blob/main/PRIVACY.md
```

License:

```text
https://github.com/JinNing6/Noosphere/blob/main/LICENSE
```
