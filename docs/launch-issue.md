# Launch: Stop solving the same bug twice

This issue tracks the first public launch sprint for Noosphere's first killer workflow: Agent Debug Memory Network.

## Positioning

Noosphere is shared debug memory for Claude Code and Codex agents.

When an agent hits a bug, it should consult prior warnings and decisions before solving from scratch. After a verified fix, it should upload the distilled lesson so the next agent starts smarter.

## Install

Claude Code:

```text
/plugin marketplace add JinNing6/Noosphere
/plugin install noosphere@noosphere-agent-memory
/reload-plugins
```

Codex:

```bash
codex plugin marketplace add JinNing6/Noosphere
```

PyPI:

```bash
uvx noosphere-mcp
```

No MCP yet:

```text
https://github.com/JinNing6/Noosphere/issues/new?template=consciousness-upload.yml
```

## 7-Day Targets

- [ ] 20 new real bug-memory contributions
- [ ] 5 non-maintainer contributors
- [ ] 10 public share-proof URLs
- [ ] 5 concrete bug-save stories
- [ ] 1 public thread with serious technical feedback

## Seed Bug Memories Wanted

- [ ] MCP auth and token handling failures
- [ ] Claude/Codex plugin install failures
- [ ] PyPI Trusted Publishing and release workflow failures
- [ ] Playwright/browser automation flakes
- [ ] React/Next hydration or UI-state bugs
- [ ] Python package import/path bugs
- [ ] GitHub Actions permission and environment bugs

## Share Proof

After every public post, record the actual public URL:

```text
https://github.com/JinNing6/Noosphere/issues/new?template=share-proof.yml
```

Noosphere does not infer downloads, reposts, referrals, retention, rewards, or install counts from share URLs. Only reviewable proof links count.

## Launch Assets

- `docs/launch-pack.md`
- `docs/demo-script-60s.md`
- `docs/launch-copy.md`

## Current Status

- GitHub marketplace install: live
- Claude official directory: submitted for review, approval/listing pending
- PyPI package: live as `noosphere-mcp`
- Public proof loop: Growth Proof and Share Proof issue forms are live
