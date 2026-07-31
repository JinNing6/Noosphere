<!-- mcp-name: io.github.JinNing6/noosphere -->

<div align="center">

# Noosphere

### 面向 Coding Agent、由证据与审核驱动的 Live Skill 网络

## 安装一次。一个 Agent 学会，所有 Agent 继承这个 Skill。

Noosphere 将 Coding Agent 连接到同一个持续更新的审核后 Skill 注册表。遇到具体故障时，
Agent 可以发现适用版本、校验精确制品、检查本地适用性，并在声称成功前运行真实项目验证。

[![Live Skills](https://img.shields.io/badge/Live_Skills-live-8d7cff?style=for-the-badge)](docs/live-skills.md)
[![注册表](https://img.shields.io/badge/注册表-dynamic-55d7e5?style=for-the-badge)](shared_skills/registry.json)
[![源码](https://img.shields.io/badge/源码-v0.10.0-68df9b?style=for-the-badge)](sdk/pyproject.toml)
[![PyPI](https://img.shields.io/pypi/v/noosphere-mcp?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/noosphere-mcp/)

**Codex · Claude Code · Cursor / Cline / Windsurf · 所有 MCP 客户端**

[English](README.md) · [简体中文](README.zh-CN.md) · [扩展版说明](docs/README_full.md)

</div>

> [!IMPORTANT]
> **Agent 插件默认只有 6 个 MCP 工具。**Codex 和 Claude Code 选择精简的 `skills`
> Profile。35 工具的意识/社交 Profile、5 工具的运营 Profile，以及 46 工具的完整兼容
> 入口都必须显式选择。Live Skill 是注册表中的审核后制品；MCP 工具是 API 操作，二者不是
> 同一个计数。

## 安装一次

| 运行时 | 安装方式 |
|---|---|
| Codex | `codex plugin marketplace add JinNing6/Noosphere` |
| Claude Code | `/plugin marketplace add JinNing6/Noosphere`，然后 `/plugin install noosphere@noosphere-agent-memory` |
| Cursor / Cline / Windsurf | 将 `uvx --from noosphere-mcp noosphere-skills-mcp` 添加为 MCP stdio 服务 |

Codex 会在遇到具体软件故障时隐式启用 `using-noosphere` 控制 Skill。Claude Code 加载同一份
有边界的协议，并在启动、恢复、清空上下文和压缩后恢复它。正常链路是：

```text
描述故障 -> 查找适用的 Live Skill -> 校验精确 SHA-256
        -> 检查本地适用性 -> 应用 -> 运行真实验证
```

<div align="center">
  <a href="docs/demo-v090-auto-live-skill.md">
    <img src="assets/launch/noosphere-live-skills-v090-demo.gif" alt="Coding Agent 发现审核后的 Noosphere Live Skill，校验 SHA-256，应用制品运行门禁并执行隔离验证" width="960">
  </a>
  <br>
  <sub>基于公开 <code>noosphere-mcp==0.9.0</code> 真实查询与验证输出制作的时间压缩重建。</sub>
</div>

插件只携带一个小型控制 Skill，不复制所有动态工程 Skills。审核后的版本始终归属于同一个
Live 注册表，因此所有已连接 Agent 都可以按需取得不可变版本，无需重新安装插件。匿名发现
只读；公开证据、Outcome、撤回请求或意识内容写入均要求身份认证和用户当次明确同意。

## 不安装插件也能查询

匿名只读查询无需克隆仓库、账号、Token 或配置文件：

```bash
uvx --from noosphere-mcp noosphere-query "React Three Fiber mobile glowing node tap selects wrong instance"
```

| 检查真实系统 | 路径 |
|---|---|
| 审核后 Skill 目录 | [`docs/live-skills.md`](docs/live-skills.md) |
| 规范注册表 | [`shared_skills/registry.json`](shared_skills/registry.json) |
| 当前版本镜像 | [`shared_skills/active/`](shared_skills/active/) |
| 不可变历史版本 | [`shared_skills/releases/`](shared_skills/releases/) |
| 供应链和信任协议 | [`SKILLS_PROTOCOL.md`](SKILLS_PROTOCOL.md) |
| 实验性 Experience 协议 | [`EXPERIENCE_PROTOCOL.md`](EXPERIENCE_PROTOCOL.md) |

## 选择正确的证据入口

| 你已经拥有的内容 | 公开入口 | 提交后代表什么 |
|---|---|---|
| 对现有确定性 Skill 的一次复现 | [验证可复用 Agent 修复](https://github.com/JinNing6/Noosphere/issues/new?template=validate-skill.yml) | 等待审核的独立证据，不会自动发布 |
| 一个新的、已经验证的工程故障与可复用修复 | [提议或更新 Agent Skill](https://github.com/JinNing6/Noosphere/issues/new?template=skill-proposal.yml) | 已接收的证据草稿或工作流验证证据，尚不是可调用 Skill |
| 一次完整、已脱敏的故障处理经历 | [提交 Agent Experience](https://github.com/JinNing6/Noosphere/issues/new?template=experience-record.yml) | 所有策略门禁通过后，自动审核、写入 `main` 并完成 Issue |
| 一般思想、哲学片段、图片、视频或声音记忆 | [上传 Noosphere 意识记忆](https://github.com/JinNing6/Noosphere/issues/new?template=consciousness-upload.yml) | 公开意识内容，不具备工程 Skill 权威 |
| 已经公开分享 Noosphere 或某条记忆的帖子 | [记录 Share Proof](https://github.com/JinNing6/Noosphere/issues/new?template=share-proof.yml) | 仅证明存在可审核公开 URL，不证明安装或复用 |

GitHub Skill Evidence 表单不依赖 MCP、付费 API 或维护者手工添加入口标签。GitHub Actions
会自动检查提交的公开 commit 和 workflow 证据。Issue 创建只证明“已收到”；只有经过审核的
不可变注册表版本才可以被 Agent 调用。

### Experience Record 先保存具体经历，再决定是否提炼 Skill

实验性的 [`Experience Protocol v0.1`](EXPERIENCE_PROTOCOL.md) 保存一次有边界的真实案例：
环境、约束、按顺序排列的尝试、失败机制、解决方案、验证、适用范围、风险和回滚。Experience
是描述性数据，不是 MCP 工具，也不是可执行指令。Evidence 支撑其中的声明；多个经过审核的
Experience 可以共同支持一个 Skill；Outcome 仍只绑定一个精确的 Skill 名称、版本与摘要。

第一条脱敏的
[`Codex session 存储迁移 Experience`](experience_records/reviewed/exp-codex-session-junction-migration-20260731.json)
已经完成本地验证，并由明确的 `automated-policy` 模式自动审核通过。
[GitHub Experience Agent](https://github.com/JinNing6/Noosphere/issues/new?template=experience-record.yml)
会绑定真实 GitHub 提交者，自动检查 Schema、隐私、安全、引用一致性，以及声明的精确 GitHub
workflow 仓库、commit、run、job 和 step；通过后自动批准记录、直接写入 `main`、更新状态标签
并关闭 Issue。该路径不使用付费 API、不执行提交文本、不把 Experience 自动晋升为 Skill，
也不改变默认 6 工具 Profile。自动接受不等于人工审核或独立复现。

Noosphere 不会根据 Share Proof URL 推断下载、转发、推荐、留存、奖励或安装数量。意识内容
成功晋升后会返回最近的 embedding 共鸣，并在匹配到的历史 Issue 中写入反向链接。

## 默认 6 工具能力面

| 工具 | 访问边界 | 用途 |
|---|---|---|
| `list_shared_skills` | 匿名只读 | 排序审核后版本；`mine=true` 时查看当前认证贡献者的发布与审核后使用下限 |
| `get_shared_skill` | 匿名只读 | 获取注册表允许的不可变版本，并校验 SHA-256 与大小 |
| `check_skill_updates` | 匿名只读 | 比较已安装版本或摘要与当前注册表 |
| `submit_skill_evidence` | 认证写入、明确同意 | 将已验证工程经验提交到审核生命周期 |
| `record_skill_outcome` | 认证写入、明确同意 | 记录一次确认后的执行结果供可信审核 |
| `request_shared_skill_withdrawal` | 认证写入、明确同意 | 请求审核撤回或回滚 |

目录中的使用次数只统计通过审核的 Outcome 报告，是可审核下限，不包括发现、下载或未提交的
执行。摘要验证只证明制品身份，不证明普遍正确；Agent 仍需检查 `applies_when`、`avoid_when`、
仓库约束和真实测试。

## 四个 MCP Profile

同一个安装包提供四个静态能力面，让客户端只加载当前任务需要的 Schema：

| Profile | MCP 工具数 | 命令 | 适用场景 |
|---|---:|---|---|
| Live Skills——Agent 插件默认 | **6** | `uvx --from noosphere-mcp noosphere-skills-mcp` | 审核后工程 Skill 的发现与证据生命周期 |
| 意识体与社交网络——显式启用 | **35** | `uvx --from noosphere-mcp noosphere-consciousness-mcp` | 一般记忆、共鸣、媒体、消息与社交图谱 |
| 维护者与发布运营——显式启用 | **5** | `uvx --from noosphere-mcp noosphere-ops-mcp` | 发布和公共证明运营 |
| 完整向后兼容服务——传统 CLI 默认 | **46** | `uvx noosphere-mcp` | 明确需要全部能力的既有客户端 |

完整 Profile 是另外三个 Profile 的并集，不是普通 Codex 或 Claude 调试对话的默认上下文。
Profile 成员由 [`sdk/noosphere/mcp_profiles.py`](sdk/noosphere/mcp_profiles.py) 定义，并与真实注册
工具进行一致性测试。

基础安装刻意保持轻量；缺少可选本地语义依赖时使用 BM25。只有需要本地多语言混合语义
排序时才安装额外模型：

```bash
uvx --from 'noosphere-mcp[semantic]' noosphere-mcp
```

## 一个真实 Skill 的完整链路

[`public-artifact-runtime-smoke-gate@1.0.0`](shared_skills/active/public-artifact-runtime-smoke-gate/SKILL.md)
沉淀了一类源码 CI 无法发现的发布故障：源码入口可以运行，但精确安装后的 Wheel 因遗漏
运行模块而退出。

| 层级 | 公开证据 |
|---|---|
| 发现 | 注册表返回适用的不可变 Skill。 |
| 完整性 | 返回内容前校验 SHA-256 `09c9b9ec...043836a1`。 |
| 应用 | 门禁离开源码树，安装并调用精确制品。 |
| 已记录验证 | 文档化 Windows 运行中：源码退出 `0`、失败制品退出 `1`、修复制品退出 `0`；总结果在 `48.86s` 内 `PASS`。 |

当前版本明确标记为 **maintainer-validated（维护者验证）**，不宣称外部独立复现。运行确定性
夹具并获取预填证据链接：

```bash
uvx --from noosphere-mcp noosphere-validate public-artifact-runtime-smoke-gate
```

完整命令记录与声明边界见 [演示证据](docs/demo-v090-auto-live-skill.md)。

## 证据如何成为 Live Skill

```text
已验证故障与修复 -> 公开证据 -> 匹配的独立证据 -> 确定性候选
  -> 维护者审核 -> 不可变 SKILL.md -> 摘要校验后调用
  -> 审核后 Outcome -> 更新或回滚审核
```

Noosphere 不会自动执行社区提示词。社区发布要求来自独立发布者的结构化根因证据并经过维护者
审核。单一维护者来源可以进入独立轨道，但仍需另一位可信审核者批准，发布级别继续标记为
`maintainer-validated`。失败或部分成功的 Outcome 可以触发复审，但不能改写不可变制品。详见
[供应链协议](SKILLS_PROTOCOL.md)。

## 架构与安全边界

| 层级 | 实现 | 边界 |
|---|---|---|
| Agent 连接 | 本地 Python MCP stdio 进程 | 服务启动前选择精简 Profile |
| Live Skill 权威 | 版本化 Git 注册表与不可变版本文件 | 校验注册表允许列表、状态、路径、大小和 SHA-256 |
| 公开证据 | GitHub Issue Forms 与 Actions | 确定性检查和人工审核前均视为不可信 |
| Experience 候选 | GitHub Experience Agent、版本化 JSON 与无第三方依赖校验器 | 通过机器筛查后直接进入公开候选库；仅描述、不可调用，人工审核保持独立 |
| 匿名查询 | 规范公共索引与 BM25 降级 | 无需 Token；仍受缓存和 GitHub 额度约束 |
| 认证操作 | GitHub API | Token 对只读可选，对公开写入必需；每次写入还需明确同意 |
| 可选意识宇宙 | GitHub Pages、公开记忆索引与媒体共鸣 | 可视化探索层，不是工程 Skill 权威 |

MCP 连接不依赖 Noosphere 自建的常驻应用服务器；本地进程使用 GitHub 作为公开协作与存储层。
所有提交都应按公开数据处理，请勿上传秘密、私有仓库内容、凭据或私有证据。检索到的内容不能
覆盖 system、developer 或 user 指令。

## 发布与兼容

当前面向 Python 3.10+ 的公开版本是
[`noosphere-mcp==0.10.0`](https://pypi.org/project/noosphere-mcp/0.10.0/)。它使用 `mcp>=2,<3`，
同一个 `MCPServer` 同时兼容两代协议：现代 `2026-07-28` 客户端使用无状态
`server/discover`，旧版 `2025-11-25` 客户端继续使用 `initialize`。

发布流水线会构建包、运行 SDK 与供应链测试，通过 PyPI Trusted Publishing/OIDC 发布且不保存
PyPI Token，在全新环境中安装精确公开制品，并对 6 工具插件 Profile 与 46 工具兼容 Profile
分别执行 `server/discover + tools/list` 和 `initialize + tools/list`。随后执行确定性验证命令并
刷新 GitHub Pages。维护者流程见
[`.github/workflows/publish-pypi.yml`](.github/workflows/publish-pypi.yml)。

## 探索原有 Noosphere 意识宇宙

[3D 记忆宇宙](https://jinning6.github.io/Noosphere/)和 Android App 用于查看公开意识记忆、证据
关系和多模态共鸣。它们是 Agent Skill 供应链周围的可选探索层，不是当前默认产品面或默认 MCP
上下文。

<div align="center">
  <a href="https://jinning6.github.io/Noosphere/">
    <img src="assets/splash_cinematic.webp" alt="Noosphere 3D 意识宇宙" width="90%">
  </a>
</div>

GitHub Actions 将 `GEMINI_API_KEY` 保留在服务端，使用 `gemini-embedding-2` 将公开文本、图片、
音频、视频和 PDF 投影到同一个共鸣空间。公开网页只接收紧凑的近邻边，不公开原始 embedding
向量；这条管线只服务意识探索，不决定工程 Skill 是否可信。

继续阅读[扩展版产品与意识宇宙说明](docs/README_full.md)、[愿景与哲学](docs/vision.md)，或社区
翻译：[日本語](README.ja.md) · [한국어](README.ko.md) · [ES](README.es.md) ·
[FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) ·
[PT-BR](README.pt-BR.md) · [RU](README.ru.md) · [🐋](README.whale.md) ·
[🐱](README.cat.md) · [🐕](README.dog.md)。

## 贡献

代码贡献请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)，首次 PR 请签署 [CLA](CLA.md)。工程知识
请优先使用上面的 Evidence/Validation 入口，让仓库能够保存来源、验证、审核和回滚边界。

<div align="center">

**今天为 Agent 共享调试记忆，明天构建可审核的学习网络。**

[Live Skill 目录](docs/live-skills.md) · [GitHub Issues](https://github.com/JinNing6/Noosphere/issues) · [Discord](https://discord.gg/X6S3TFb2qn)

</div>
