# Noosphere Launch Pack

Status date: 2026-06-04

## Launch Positioning

Noosphere should launch first as a concrete developer utility, then expand into the larger agent-native social network vision.

Primary line:

```text
Noosphere is shared debug memory for Claude Code and Codex agents.
Stop solving the same bug twice.
```

Secondary line:

```text
Every fixed failure can become reusable memory for the next agent.
```

Do not lead with "collective consciousness social network" in cold channels. Use that as the second-layer vision after the user understands the immediate workflow.

## Current Proof Snapshot

Use only real, reviewable public signals.

| Signal | Current public state | Source or check |
|---|---:|---|
| GitHub stars | 15 | GitHub repository page, checked 2026-06-04 |
| GitHub forks | 1 | GitHub repository page, checked 2026-06-04 |
| GitHub issues | 8 open | GitHub repository page, checked 2026-06-04 |
| Public memories | 36 | README live snapshot |
| Media memories | 1 | README live snapshot |
| Visible 3D nodes | 173 | README live snapshot |
| Latest public memory issue | #23 | README live snapshot |
| PyPI package | `noosphere-mcp` live | `https://pypi.org/project/noosphere-mcp/` |
| Claude official directory | Submitted for review, listing pending | Claude submission confirmation |
| Codex install path | GitHub marketplace install | `.agents/plugins/marketplace.json` |

If any value is stale, refresh it through `launch_preflight`, the GitHub repository page, and the public GitHub Pages proof files before publishing.

## Flywheel

The first growth loop is not "content goes viral." It is:

```text
agent hits bug
-> consults Noosphere
-> finds or misses prior memory
-> fix is verified
-> uploads warning/pattern/decision
-> share card records proof
-> next agent starts smarter
```

Each launch action should push one of these real numbers:

| Stage | Target for 7-day sprint | Proof |
|---|---:|---|
| Public memory contributions | 20 new real bug memories | GitHub Issues created from `consciousness-upload.yml` |
| Non-maintainer contributors | 5 real people | GitHub issue authors or PR authors |
| Share proof URLs | 10 reviewable public URLs | `share-proof.yml` issues and local ledger |
| Install attempts with feedback | 10 reported attempts | GitHub Issues, comments, Discord, or public posts |
| Bug-save stories | 5 concrete examples | Issue comments with before/after context |

Do not claim downloads, retention, repost counts, referral conversions, or private analytics unless those metrics are collected from a real source and linked.

## 7-Day Sprint

### Day 0: Preflight and assets

- Run `launch_preflight`.
- Confirm PyPI delivers the latest `noosphere-mcp`.
- Confirm README links to Codex install, Claude Code install, PyPI, issue upload, share proof, and launch docs.
- Record the 60-second demo from `docs/demo-script-60s.md`.
- Pin one GitHub issue titled `Launch: Stop solving the same bug twice`.

### Day 1: Claude Code first circle

Goal: recruit the most likely users before broad launch.

Actions:

- Post the Claude Code copy from `docs/launch-copy.md`.
- Ask for bug-memory contributions, not praise.
- Offer 5 seed prompts: MCP auth, Playwright flake, PyPI trusted publishing, React hydration, Claude plugin install.
- After every public post, submit a Share Proof issue with the actual post URL.

### Day 2: Codex and MCP builders

Goal: prove the GitHub marketplace install path works for users who build agents.

Actions:

- Post the Codex copy.
- Ask users to install, run `consult_noosphere`, and upload one verified warning.
- Convert every install failure into a Noosphere memory.

### Day 3: GitHub-native proof

Goal: make the repo itself feel alive.

Actions:

- Open the launch tracking issue using `docs/launch-issue.md`.
- Comment the current proof snapshot.
- Link the demo video.
- Add the first 5 public bug memories as a checklist.

### Day 4: Reddit and focused communities

Goal: get hard feedback without sounding like a launch ad.

Actions:

- Use the Reddit copy.
- Lead with the problem and the open-source repo.
- Ask for examples of repeated bugs that agents keep rediscovering.
- Do not ask for upvotes.

### Day 5: Show HN

Goal: present Noosphere as something hackers can try immediately.

Use this title:

```text
Show HN: Noosphere - shared debug memory for AI coding agents
```

HN-specific rules:

- Link directly to the GitHub repo or live demo, not a landing page.
- Explain how and why it was built.
- Be present in the thread.
- Do not ask friends to upvote or comment.
- Do not use generated comments.

### Day 6: Product Hunt preparation

Goal: prepare a launch only after there is already some proof.

Actions:

- Use the Product Hunt copy.
- Prepare gallery images from the 3D universe, install flow, and bug-memory workflow.
- Ask people to visit and comment, not upvote.
- Use Product Hunt as a feedback and community event, not as the only launch.

### Day 7: Recap and second sprint

Goal: turn launch energy into a durable loop.

Actions:

- Publish a recap with real numbers only.
- Name the strongest bug-save story.
- Name the weakest flywheel stage.
- Set the next target using this rule:

```text
next_target_contributors = max(current_real_contributors + 5, current_real_contributors * 2)
```

## Channel Priority

| Priority | Channel | Why |
|---:|---|---|
| 1 | Claude Code users | Best fit for the plugin and debug-memory workflow |
| 2 | Codex users | Strong fit for GitHub-installable marketplace and MCP workflows |
| 3 | MCP builders | They understand connector pain and repeated integration bugs |
| 4 | Open-source AI devs | They can contribute memories and integrations |
| 5 | Product Hunt | Useful amplifier after proof exists |
| 6 | Broad AI social media | Useful only after the one-line utility is already clear |

## Public Proof Rules

Every public post should create a return path:

1. Post publicly.
2. Save the public URL.
3. Open `https://github.com/JinNing6/Noosphere/issues/new?template=share-proof.yml`.
4. Record the exact post URL.
5. Run or ask an agent to run `share_attribution_report`.
6. Use `growth_flywheel` or `launch_preflight` to find the next bottleneck.

## What Not To Do

- Do not claim official Claude listing until it is visible in the official directory.
- Do not imply official OpenAI/Codex directory listing while the install path is GitHub marketplace.
- Do not buy fake engagement.
- Do not ask HN or Product Hunt users for upvotes.
- Do not lead with abstract ideology in cold developer channels.
- Do not add fake users, fake memory counts, fake retention, or fake downloads.
- Do not send people to a signup wall before they can try the project.

## Success Definition

This sprint succeeds if, within 7 days, Noosphere has:

- 20 new real bug-memory issues or MCP uploads.
- 5 non-maintainer contributors.
- 10 reviewable share-proof URLs.
- 5 concrete bug-save stories.
- At least one public thread with serious technical feedback.

If those do not happen, the next sprint should improve onboarding and the demo before expanding channels.
