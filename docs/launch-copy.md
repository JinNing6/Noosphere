# Noosphere v0.9.0 Launch Copy

Status date: 2026-07-20

Use one product promise across every channel. Adapt the opening sentence to the audience,
but do not change the trust boundary, install commands, or evidence links.

## Core Message

```text
Install once. One Agent learns. Every Agent inherits the Skill.
```

Supporting line:

```text
Noosphere gives coding Agents automatic access to live, review-gated Skills with exact
artifact digests and local verification before reuse.
```

Chinese:

```text
安装一次。一个 Agent 学会，所有 Agent 继承这个 Skill。

Noosphere 让 Coding Agent 自动访问持续更新、经过审核的 Skills；调用前校验精确制品，
并在本地运行真实验证。
```

## Single Call To Action

Lead with the Codex install command in general developer channels:

```bash
codex plugin marketplace add JinNing6/Noosphere
```

Link to the repository after the command:

```text
https://github.com/JinNing6/Noosphere
```

Use the Claude Code commands only in Claude-specific channels:

```text
/plugin marketplace add JinNing6/Noosphere
/plugin install noosphere@noosphere-agent-memory
```

## Verified Facts Available For Launch

- Public GitHub Release: `v0.9.0`.
- Public PyPI artifact: `noosphere-mcp==0.9.0`.
- 14 maintainer-validated Live Skills in registry revision 2.
- Anonymous read-only discovery without a GitHub token.
- Exact SHA-256 verification before a Skill artifact is returned.
- Automatic failure-time activation for Codex and Claude Code through the shared
  `using-noosphere` control Skill.
- Deterministic Windows, Linux, and macOS validation for Living Skill #001.
- Current public verification level is `maintainer-validated`; no external independent
  reproduction is claimed yet.

## Launch Assets

- Social preview: `assets/launch/noosphere-live-skills-v090-social-preview.png`
- Animated demo: `assets/launch/noosphere-live-skills-v090-demo.gif`
- MP4 demo: `assets/launch/noosphere-live-skills-v090-demo.mp4`
- Evidence boundary: `docs/demo-v090-auto-live-skill.md`
- Real Skill: `shared_skills/active/public-artifact-runtime-smoke-gate/SKILL.md`
- Release: `https://github.com/JinNing6/Noosphere/releases/tag/v0.9.0`

The GitHub social preview image must be uploaded through repository Settings. GitHub's
documented target is 1280 x 640 and below 1 MB; the generated asset meets both constraints.

## X / LinkedIn Launch Thread

### Post 1

```text
Install once. One Agent learns. Every Agent inherits the Skill.

Noosphere v0.9.0 gives Codex and Claude Code automatic access to a live, review-gated
Skill registry when a concrete software failure occurs.

https://github.com/JinNing6/Noosphere
```

Attach `noosphere-live-skills-v090-demo.mp4`.

### Post 2

```text
This is not another static Skill folder.

The Agent discovers an applicable release, verifies its exact SHA-256, checks
applies_when / avoid_when against the local project, applies only the relevant steps,
and runs the real project verification.
```

### Post 3

```text
The first end-to-end case catches a release failure that source-only CI misses:

source entry point: PASS
installed failing artifact: FAIL
installed fixed artifact: PASS

The full fixture runs without a repository clone, personal project, or GitHub token.
```

### Post 4

```text
Current trust boundary:

- 14 maintainer-validated Live Skills
- immutable releases
- exact artifact digests
- anonymous read-only discovery
- review-gated updates and rollback

We do not claim external independent reproduction until that evidence exists.
```

### Post 5

```text
Codex:
codex plugin marketplace add JinNing6/Noosphere

Claude Code:
/plugin marketplace add JinNing6/Noosphere
/plugin install noosphere@noosphere-agent-memory

Any MCP client:
uvx noosphere-mcp
```

## Show HN

Title:

```text
Show HN: Noosphere - Live Skills that coding agents inherit automatically
```

Body:

```text
AI coding agents still solve the same engineering failures in isolation. I built
Noosphere so a reviewed Skill learned from one failure can become available to every
connected Agent without rebundling static copies.

In v0.9.0, Codex and Claude Code load the same control Skill. When a concrete failure
occurs, the Agent discovers an applicable immutable release, verifies its exact SHA-256,
checks whether it applies to the local evidence, and runs the real project verification.

The repository currently contains 14 maintainer-validated Live Skills. That label is
intentional: I am not claiming external independent reproduction before it exists.

The first end-to-end case is a public-artifact runtime gate. It reproduces a package that
passes from the source tree but fails after installation because the runtime module was
omitted, then proves the corrected artifact from an isolated environment.

Codex install:
codex plugin marketplace add JinNing6/Noosphere

Zero-token terminal query:
uvx --from noosphere-mcp==0.9.0 noosphere-query "your error"

Repository and complete public evidence:
https://github.com/JinNing6/Noosphere

I would value hard feedback on the trust model, automatic activation boundary, and which
high-frequency engineering failures deserve the next Live Skills.
```

Do not ask for upvotes, coordinate votes, or publish generated replies. Stay available and
answer technical questions personally with links to code and evidence.

## Reddit / Technical Communities

```text
I built an open-source live Skill registry for coding agents.

The difference from a static Skill directory is the runtime path: Codex or Claude Code
encounters a concrete failure, discovers an applicable reviewed Skill, verifies the exact
artifact digest, checks local applicability, and runs real verification before reporting
success.

v0.9.0 is public. The current registry has 14 maintainer-validated Skills; I am not
calling them externally reproduced before that evidence exists.

The first deterministic case catches a Python/MCP release that works from source but
fails after exact artifact installation.

Codex:
codex plugin marketplace add JinNing6/Noosphere

Read-only, no token:
uvx --from noosphere-mcp==0.9.0 noosphere-query "your error"

Repo: https://github.com/JinNing6/Noosphere

I am specifically looking for criticism of the trust and update model, not generic launch feedback.
```

Read each community's self-promotion rules before posting. Do not cross-post identical text
to multiple subcommunities at the same time.

## V2EX / 掘金 / 中文开发者社区

Title:

```text
我把 Coding Agent 的调试经验做成了可以持续更新和继承的 Skill
```

Body:

```text
最近反复遇到一个问题：不同 Coding Agent 会在不同项目里重新排查同一类工程故障。
静态 SKILL.md 可以保存流程，但无法回答版本是否最新、来源是什么、是否真的执行成功，
以及出错后如何更新或回滚。

因此我做了 Noosphere v0.9.0：

安装一次。一个 Agent 学会，所有 Agent 继承这个 Skill。

当 Codex 或 Claude Code 遇到具体软件故障时，会先自动查询审核门禁的 Live Skill 注册表，
获取不可变版本，校验精确 SHA-256，再检查 applies_when / avoid_when，最后在当前项目运行
真实验证。没有匹配 Skill 时不会强行套用，也不会阻塞正常调试。

第一个完整案例解决的是“源码测试通过，但发布后的 Python 包 / CLI / MCP Server 无法启动”。
确定性夹具会证明：源码入口退出 0、遗漏模块的安装制品退出 1、修复后的精确制品退出 0。

当前公开边界也写得很清楚：14 个 Skills 属于 maintainer-validated，不会在缺少外部证据时
宣传成社区独立验证。

Codex 安装：
codex plugin marketplace add JinNing6/Noosphere

无需 Token 的只读查询：
uvx --from noosphere-mcp==0.9.0 noosphere-query "你的报错"

源码、注册表、不可变 Skill、摘要和验证夹具全部公开：
https://github.com/JinNing6/Noosphere

最希望讨论两个问题：这种审核与回滚边界是否足够可信，以及你最希望 Agent 不再重复排查
哪一类工程故障？
```

## Follow-Up Proof Post

Publish this only after real external evidence exists. Replace placeholders with linked facts.

```text
Noosphere Live Skill update:

[Skill name] was used in [public environment].
Outcome: [success / partial / failure]
Verification: [public command or CI link]
Contributor: [public GitHub identity]

The evidence did / did not trigger an update candidate. Noosphere keeps the old release
immutable and publishes reviewed changes as a new digest-pinned version.
```

## Measurement

Record only verifiable metrics:

- GitHub repository visitors and Stars.
- PyPI downloads from the official endpoint.
- Public install feedback.
- Successful, partial, and failed Skill Outcomes.
- External validators and public evidence URLs.

Do not infer installs from clones, users from downloads, or successful reuse from a click.
