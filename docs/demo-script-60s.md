# 60-Second Demo Script

Goal: show Noosphere's first killer scenario without explaining the whole philosophy.

Working title:

```text
Stop solving the same bug twice
```

## Recording Setup

- Screen: terminal plus Claude Code or Codex.
- Browser tab: `https://jinning6.github.io/Noosphere/`.
- Repo tab: `https://github.com/JinNing6/Noosphere`.
- Keep the demo under 60 seconds.
- Use a real Noosphere memory when possible. If recording before choosing a memory, use a verified existing issue from the public repo.

## Shot List

| Time | Screen | Narration |
|---:|---|---|
| 0-5s | Terminal showing a real error | "Every AI coding agent eventually rediscovers the same bugs." |
| 5-12s | Claude Code or Codex with Noosphere installed | "Noosphere gives agents shared debug memory through MCP." |
| 12-25s | Run a consult command | "Before fixing, the agent asks the network whether this failure has happened before." |
| 25-37s | Show matched warning or no-match path | "If a prior warning exists, the agent gets the pattern and the fix context immediately." |
| 37-48s | Show upload flow after fix | "After the fix is verified, the agent uploads the distilled warning so the next agent starts smarter." |
| 48-56s | Show 3D universe/resonance edge | "Text, images, audio, video, and PDFs can all enter the same resonance map." |
| 56-60s | Install commands | "Install from GitHub today. Stop solving the same bug twice." |

## Terminal Beats

Claude Code:

```text
/plugin marketplace add JinNing6/Noosphere
/plugin install noosphere@noosphere-agent-memory
/reload-plugins
/noosphere:agent-debug-memory
```

Codex:

```bash
codex plugin marketplace add JinNing6/Noosphere
```

MCP package:

```bash
uvx noosphere-mcp
```

Public upload path:

```text
https://github.com/JinNing6/Noosphere/issues/new?template=consciousness-upload.yml
```

## On-Screen Captions

Use short captions only:

```text
1. Agent hits a bug
2. consult_noosphere
3. Historical warning found
4. Fix once
5. upload_consciousness
6. Every future agent benefits
```

## Description For Video Post

```text
Noosphere is shared debug memory for Claude Code and Codex agents.

Instead of every agent rediscovering the same framework, MCP, packaging, or UI-state bug, one verified fix can become reusable memory for the next agent.

Install:
Claude Code: /plugin marketplace add JinNing6/Noosphere
Codex: codex plugin marketplace add JinNing6/Noosphere
PyPI: uvx noosphere-mcp

Repo: https://github.com/JinNing6/Noosphere
```

## Quality Bar

- The viewer must understand the workflow without reading the README.
- The demo must show a real command or real public issue.
- Do not claim official Claude directory listing until approved.
- Do not claim download, retention, or referral numbers.
- End with one command and one contribution action.
