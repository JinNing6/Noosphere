# Live Skill Proof Wave — 2026-07-21

Campaign ID: `live-skill-proof-20260721`

Status: active; the first public surface was published on 2026-07-21 at 16:37 +08:00

North star: `Weekly External Verified Reuses`

## One Verified Story

```text
One runtime packaging pattern. Three real projects.
One released upstream repair and two regression-tested fixes under review.
```

Noosphere's `public-artifact-runtime-smoke-gate@1.0.0` captures a recurring boundary:
source-tree checks can pass while the exact package, CLI, or MCP artifact users install is
broken. The Skill requires building or downloading the real artifact, installing it into a
clean environment, invoking its public entry point, and proving the repaired artifact in the
same way.

This wave is about the repeatable method and its public evidence. It is not a claim that an
independent third party has reused the Noosphere Skill digest.

## Primary Evidence

### 1. okflint: released repair

- Exact failing artifact: `okflint==0.3.0`.
- Reproduction: `uvx --isolated --from okflint==0.3.0 okflint --help` exited `1` with
  `ModuleNotFoundError: No module named 'beartype'`.
- Root cause: the CLI imported `beartype`, but the public Wheel did not declare it as a
  runtime dependency.
- Exact repaired artifact: `okflint==0.3.1`.
- Verification: `uvx --isolated --from okflint==0.3.1 okflint --help` exited `0`.
- Public chain: [Issue](https://github.com/mattdav/okflint/issues/2),
  [independent upstream repair](https://github.com/mattdav/okflint/commit/d727ceb),
  [v0.3.1 release](https://github.com/mattdav/okflint/releases/tag/v0.3.1), and
  [Noosphere Outcome #57](https://github.com/JinNing6/Noosphere/issues/57).

The upstream maintainer landed an equivalent remediation independently. Noosphere does not
claim that the maintainer adopted the contributor PR or used Noosphere.

### 2. brainctl: actionable optional-extra boundary

- Exact artifact: `brainctl==2.8.0`.
- Base install plus `brainctl-mcp --help`: exit `1` with a raw missing-`mcp` traceback.
- `[mcp]` extra plus the same command: exit `0`.
- Proposed boundary: the base artifact exits `1` with exact pip/pipx remediation and no
  traceback; the `[mcp]` path continues to start normally.
- Local evidence: 26 related tests passed, and both base-Wheel and `[mcp]`-Wheel smoke paths
  were exercised.
- Public fix: [brainctl PR #170](https://github.com/TSchonleber/brainctl/pull/170).

The PR is open and mergeable. Its workflow is waiting for maintainer approval and reports
`action_required` with zero jobs. That state is neither a failed test run nor green CI.

### 3. Ahrena: disposable editable-install boundary

- Exact artifact: `ahrena-mcp==0.1.0a1`.
- Old global editable install: exit `0` while the project-local source existed, then exit `1`
  with `ModuleNotFoundError` after that disposable source path was removed.
- Proposed repair: use a self-contained non-editable pipx install and automatically migrate
  existing editable installs.
- Local evidence: 4 focused tests passed; the real pipx lifecycle stayed at exit `0` after
  both the old and the new source directories were removed.
- Public fix: [Ahrena PR #376](https://github.com/guardiatechnology/ahrena/pull/376), with a
  GitHub-signed Verified commit.

The PR is open and mergeable. Its workflow is also waiting for maintainer approval and has
not run jobs yet.

The complete sprint board and claim boundaries remain in
[Noosphere Issue #51](https://github.com/JinNing6/Noosphere/issues/51).

## Trust Boundary

- Skill: `public-artifact-runtime-smoke-gate@1.0.0`.
- Exact SHA-256:
  `09c9b9ec1925a2d624bf6f8efb2a92ce0bc41e1c2a4b64628b4d389c043836a1`.
- Registry revision after recorded Outcome #57: `3`.
- Current verification level: `maintainer-validated`.
- Recorded Outcomes: one success, reported and approved by the Noosphere maintainer.
- Independent third-party Agent reuse of this exact Skill digest: not yet proven.

## One Call To Action

Install Noosphere once, then let the Agent retrieve the current digest-pinned Skill when the
same failure boundary appears:

```bash
codex plugin marketplace add JinNing6/Noosphere
```

Repository and complete public evidence:
<https://github.com/JinNing6/Noosphere>

## X / LinkedIn

### X thread

Post 1:

```text
One packaging failure pattern. Three real Python/MCP projects.

One upstream repair is released. Two regression-tested fixes are under review.

Noosphere turned the pattern into a digest-pinned Live Skill instead of another static SKILL.md.

https://github.com/JinNing6/Noosphere
```

Attach `assets/launch/noosphere-live-skills-v090-demo.mp4`.

Post 2:

```text
The boundary: source tests can pass while the artifact users install is broken.

The Skill tests the exact Wheel/CLI/MCP entry point in a clean environment, then proves the repaired artifact the same way.

Evidence: https://github.com/JinNing6/Noosphere/issues/51
```

Post 3:

```text
Real results:

okflint 0.3.0: exit 1, missing runtime dependency
okflint 0.3.1: exit 0 after an independent upstream repair

brainctl #170 and Ahrena #376 now carry bounded fixes and regression tests; both await maintainer review.
```

Post 4:

```text
Trust boundary: maintainer-validated, not independent Agent reuse.

Install once:
codex plugin marketplace add JinNing6/Noosphere

Exact Skill digest and public Outcomes stay auditable in the registry.
```

### LinkedIn post

```text
Source tests are not release tests.

I applied one Noosphere Live Skill to three real Python/MCP packaging failures. The same pattern appeared each time: the repository looked healthy, but the exact artifact or global command users installed crossed a different runtime boundary.

The public evidence now includes:

• okflint 0.3.0 failing in isolation and 0.3.1 passing after the maintainer independently released an equivalent repair;
• brainctl PR #170 replacing a raw missing-extra traceback with exact recovery guidance and a tested optional-extra boundary;
• Ahrena PR #376 replacing a disposable editable global install with a self-contained pipx install and automatic legacy migration.

The important product idea is not the number of Skills. It is the loop: a real failure becomes an immutable, digest-pinned workflow; future Agents retrieve it, check whether it applies locally, and run the real verification before reporting success.

The current trust level remains maintainer-validated. I am not presenting these cases as independent third-party Noosphere reuse.

Install once:
codex plugin marketplace add JinNing6/Noosphere

Evidence: https://github.com/JinNing6/Noosphere/issues/51
```

## Show HN

HN's current guidelines prohibit generated or AI-edited comments. The maintainer must write
the explanatory text personally. Use only this factual outline; do not paste it as a generated
comment:

- Suggested title: `Show HN: Noosphere – Live Skills that agents inherit automatically`.
- Destination: <https://github.com/JinNing6/Noosphere>.
- Explain the repeated pain personally: Agents re-diagnose the same release boundary.
- Show that the product is directly runnable without signup:
  `uvx --from noosphere-mcp==0.9.0 noosphere-query "your error"`.
- Explain immutable releases, exact SHA-256 retrieval, local applicability checks, and local
  verification.
- Link the three-project evidence above and state which upstream results are released versus
  still under review.
- State `maintainer-validated` explicitly and ask for technical criticism of the trust and
  update model.
- Do not ask anyone to upvote, comment, or coordinate submission activity.

Official references: [Show HN guidelines](https://news.ycombinator.com/showhn.html) and
[HN guidelines](https://news.ycombinator.com/newsguidelines.html).

## Reddit

Before publishing, select one technically relevant community and check its current rules.
Do not publish identical copies across several subreddits and do not send unsolicited private
messages. Reddit's current sitewide spam guidance prohibits repetitive mass posting.

Title:

```text
I tested one release-smoke pattern against three real Python/MCP packaging failures
```

Body:

```text
I have been testing a narrow failure mode: repository tests pass, but the exact Wheel, CLI, or MCP command users install fails in a clean environment.

The same artifact boundary produced three public cases:

1. okflint 0.3.0 omitted a runtime dependency and failed from the exact public artifact. The maintainer independently released 0.3.1, which passes the same isolated command.
2. brainctl's base package exposed brainctl-mcp but failed with a raw missing-extra traceback. PR #170 adds an actionable optional-extra boundary and regression coverage.
3. Ahrena installed a global MCP command in editable mode from a disposable project directory. PR #376 makes the pipx install self-contained and migrates the legacy state.

I captured the method as a versioned Noosphere Live Skill: build or download the exact artifact, install it without development leakage, invoke its public entry point, and prove the repaired artifact the same way.

The current trust level is maintainer-validated; this is not yet independent third-party Agent reuse.

Evidence and commands: https://github.com/JinNing6/Noosphere/issues/51

I would value criticism of the verification boundary: which installed-artifact failures does this still miss?
```

Official reference: [Reddit spam policy](https://support.reddithelp.com/hc/en-us/articles/360043504051-Spam).

## V2EX

Recommended node: verify the current node rules at publication time; use a technical/programming
node only if project-sharing is allowed, otherwise use the platform's designated promotion node.

Title:

```text
同一种 Python / MCP 发布故障，我在三个真实项目里验证了一遍
```

Body:

```text
最近没有继续堆 Skill 数量，而是在验证一个更具体的问题：源码仓库里的测试通过，不代表用户真正安装到的 Wheel、CLI 或 MCP 命令可以运行。

我用同一个发布制品检查流程验证了三个公开项目：

1. okflint 0.3.0 的源码环境掩盖了缺失的运行时依赖，精确公开制品在隔离环境退出 1；维护者独立发布 0.3.1 后，相同命令退出 0。
2. brainctl 基础包暴露了 brainctl-mcp 命令，但没有安装 [mcp] extra 时直接抛缺模块 traceback。PR #170 增加了明确的 pip / pipx 修复提示和回归测试。
3. Ahrena 把全局 MCP 命令以 editable 方式指向项目内可删除目录，目录删除后全局命令失效。PR #376 改成自包含的 pipx 安装，并自动迁移旧安装。

这也是 Noosphere 与普通静态 Skill 集合最关键的区别：不是只保存一份 SKILL.md，而是把真实故障、适用边界、不可变版本、精确 SHA-256 和验证结果连成持续更新的证据链。

目前信任等级仍然是 maintainer-validated；这些案例不能被表述成第三方已经独立使用了 Noosphere。

安装：
codex plugin marketplace add JinNing6/Noosphere

完整命令和证据：
https://github.com/JinNing6/Noosphere/issues/51

最希望讨论的是：除了源码通过、安装制品失败之外，你还遇到过哪些 CI 无法覆盖的发布边界？
```

## 掘金 / DEV

Title:

```text
源码测试通过，为什么用户安装后仍然会失败：三个真实 Python / MCP 案例
```

Publish-ready structure:

1. Start with the source-versus-artifact boundary, not the Noosphere brand.
2. Reproduce `okflint==0.3.0` and `0.3.1` with the exact commands and exit states.
3. Explain why development dependencies hid the missing runtime declaration.
4. Show how brainctl's optional extra requires an explicit console-entry boundary.
5. Show why an editable pipx install cannot safely point to disposable project state.
6. Derive the reusable gate: exact artifact, clean install, public entry point, fixed artifact,
   explicit evidence.
7. Explain how Noosphere packages that gate as an immutable, digest-pinned Live Skill.
8. Close with the install command and the `maintainer-validated` boundary.

Use the evidence sections in this packet verbatim for commands, versions, PR states, and trust
claims. Adapt the surrounding explanation to the platform; do not duplicate the forum post.

## Execution Ledger

| Surface | State | Public URL | Published at | Evidence owner |
|---|---|---|---|---|
| Canonical GitHub packet | Published | [Evidence packet on `main`](https://github.com/JinNing6/Noosphere/blob/main/docs/distribution-waves/live-skill-proof-20260721.md) | 2026-07-21 16:36 +08:00 | Noosphere maintainer |
| GitHub Show and tell | Published | [Discussion #61](https://github.com/JinNing6/Noosphere/discussions/61) | 2026-07-21 16:37 +08:00 | Noosphere maintainer |
| Share Proof ledger | Recorded | [Issue #62](https://github.com/JinNing6/Noosphere/issues/62) | 2026-07-21 16:41 +08:00 | GitHub IssueOps |
| GitHub proof anchor | Active | [Issue #51](https://github.com/JinNing6/Noosphere/issues/51) | Existing | Noosphere maintainer |
| X | Prepared | Not published | — | Noosphere maintainer |
| LinkedIn | Prepared | Not published | — | Noosphere maintainer |
| Show HN | Human authorship required | Not published | — | Noosphere maintainer |
| Reddit | Community rule check required | Not published | — | Noosphere maintainer |
| V2EX | Node rule check required | Not published | — | Noosphere maintainer |
| 掘金 / DEV | Prepared outline | Not published | — | Noosphere maintainer |

Every published URL must also be recorded through the repository's Share Proof form. A public
URL proves that a post exists; it does not prove installs, reuse, or successful Outcomes.

The first loop segment is now verified: Discussion #61 is public, Share Proof #62 contains the
same URL and source Issue, and both Share Proof IssueOps runs completed successfully. This
changes the live Share Proof count from the baseline value of 0 to 1 reviewable public URL; it
does not change install, reuse, or trust claims.

## Measurement Checkpoints

Baseline captured at 2026-07-21 15:59 +08:00 through GitHub's repository API:

- 18 Stars and 1 fork.
- 39 views and 19 unique visitors in the current 14-day window.
- Top referrers: `github.com` 6 / 1 unique, Baidu 1 / 1, Google 1 / 1.
- Share Proof Issues: 0.
- Growth Proof Issues: 0.
- Recorded Skill Outcomes: 1 maintainer-reported success.

### 24-hour checkpoint

Record after the first public post:

- published URLs and substantive technical replies;
- GitHub views, unique visitors, and top referrers;
- new install/query reports supported by a public URL;
- new upstream maintainer actions on PR #170 or PR #376;
- exact-version Outcomes submitted or recorded.

### 72-hour checkpoint

Record the same fields, compare against the baseline and 24-hour checkpoint, identify the
weakest conversion bridge, and choose exactly one response:

- repair positioning if discussion shows category confusion;
- repair onboarding if attention does not produce a successful query;
- repair the Outcome path if use occurs but cannot be recorded;
- extend the strongest channel only if it produces substantive technical engagement;
- publish a follow-up only if there is new public evidence.
