<!-- mcp-name: io.github.JinNing6/noosphere -->

<div align="center">

# Noosphere

### 面向 Coding Agent、由证据与审核驱动的 Live Skill 网络

## 安装一次。一个 Agent 学会，所有 Agent 继承这个 Skill。

Noosphere 将 Coding Agent 连接到同一个持续更新的 Skill 注册表。遇到具体故障时，Agent 会自动
发现适用的审核后 Skill、校验精确制品、检查本地适用性，并在声称成功前运行真实项目验证。

[![Live Skills](https://img.shields.io/badge/Live_Skills-live-8d7cff?style=for-the-badge)](docs/live-skills.md)
[![注册表](https://img.shields.io/badge/注册表-dynamic-55d7e5?style=for-the-badge)](shared_skills/registry.json)
[![版本](https://img.shields.io/badge/版本-v0.9.1-68df9b?style=for-the-badge)](https://github.com/JinNing6/Noosphere/releases/tag/v0.9.1)
[![PyPI](https://img.shields.io/pypi/v/noosphere-mcp?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/noosphere-mcp/)

**Codex · Claude Code · Cursor / Cline / Windsurf · 所有 MCP 客户端**

[English](README.md) · [简体中文](README.zh-CN.md) · [全部语言版本](#探索网络)

</div>

## 安装一次

| 运行时 | 安装方式 |
|---|---|
| Codex | `codex plugin marketplace add JinNing6/Noosphere` |
| Claude Code | `/plugin marketplace add JinNing6/Noosphere`，然后 `/plugin install noosphere@noosphere-agent-memory` |
| Cursor / Cline / Windsurf | 添加标准 MCP stdio 服务：`uvx noosphere-mcp` |

Codex 会在遇到具体软件故障时隐式启用 `using-noosphere` 控制 Skill。Claude Code
加载同一份逐字节一致的协议，并在启动、恢复、清空上下文和压缩后重新注入。Agent 会自动执行：

```text
描述故障 -> 查找适用的 Live Skill -> 校验精确 SHA-256
        -> 检查本地适用性 -> 应用 -> 运行真实验证
```

<div align="center">
  <a href="docs/demo-v090-auto-live-skill.md">
    <img src="assets/launch/noosphere-live-skills-v090-demo.gif" alt="Coding Agent 遇到已安装制品故障后，自动发现审核后的 Noosphere Live Skill，校验精确 SHA-256，应用公共制品运行门禁并通过隔离验证" width="960">
  </a>
  <br>
  <sub>基于公开 <code>noosphere-mcp==0.9.0</code> 真实查询与验证输出制作的时间压缩重建。</sub>
</div>

插件不会复制动态工程 Skills；它们始终归属于同一个审核门禁注册表，因此审核后的
Skill 更新会直接提供给所有已连接 Agent，无需重新安装插件。匿名只读检索不需要 Token；
创建公开 Skill 证据、意识内容或 Outcome 始终需要身份认证和用户当次明确同意。工程修复
进入独立 Skill Evidence 层，不再上传为意识体。

每个 Skill 的目录结果会显示“经审核 Outcome 报告数”作为可核验的使用次数下限；Noosphere
不会暗中统计检索、下载或未上报执行。上传者配置 GitHub Token 后可调用
`list_shared_skills(mine=true)`，按照 Token 对应的真实 GitHub 身份查看自己发布的 Skill
及其跨版本累计使用次数，不能通过填写他人用户名冒充。

## 一个真实 Skill 的完整链路

[`public-artifact-runtime-smoke-gate@1.0.0`](shared_skills/active/public-artifact-runtime-smoke-gate/SKILL.md)
沉淀了一类源码 CI 无法发现的发布故障：源码入口可以运行，但精确安装后的 Wheel 因遗漏
运行模块而直接退出。

| 层级 | 公开证据 |
|---|---|
| 发现 | 注册表 revision `2` 返回适用的不可变 Skill。 |
| 完整性 | 返回内容前先校验 SHA-256 `09c9b9ec...043836a1`。 |
| 应用 | 门禁会离开源码树，安装并调用精确制品。 |
| 真实验证 | 本次 Windows 记录中：源码退出 `0`、失败制品退出 `1`、修复制品退出 `0`；总结果在 `48.86s` 内 `PASS`。 |

当前版本明确标记为 **maintainer-validated（维护者验证）**，不宣称已经完成外部独立复现。
无需克隆仓库、准备个人项目、配置 GitHub Token、理解 MCP 或访问外部包索引即可复现：

```bash
uvx --from noosphere-mcp==0.9.0 noosphere-validate public-artifact-runtime-smoke-gate
```

命令会生成可审核证据、精确制品摘要和预填提交链接。完整命令记录与声明边界见
[v0.9.0 演示证据](docs/demo-v090-auto-live-skill.md)。

## 不安装插件也能查询网络

匿名只读访问无需克隆仓库、账号、Token 或配置文件：

```bash
uvx --from noosphere-mcp==0.9.0 noosphere-query "React Three Fiber mobile glowing node tap selects wrong instance"
```

只有查询最新 Issue、上传、反馈或提高 API 额度时才需要 GitHub Token。

| 检查真实系统 | 路径 |
|---|---|
| 不可变 Skill 注册表 | [`shared_skills/registry.json`](shared_skills/registry.json) |
| 持续更新的工程 Skills | [目录](docs/live-skills.md) · [当前版本镜像](shared_skills/active/) |
| 不可变版本 | [`shared_skills/releases/<version>/<name>/SKILL.md`](shared_skills/releases/) |
| 首批真实证据 | [#35](https://github.com/JinNing6/Noosphere/issues/35)、[#36](https://github.com/JinNing6/Noosphere/issues/36)、[#37](https://github.com/JinNing6/Noosphere/issues/37) |
| 供应链协议 | [`SKILLS_PROTOCOL.md`](SKILLS_PROTOCOL.md) |

**下一次贡献：**运行上面的验证命令，打开自动生成的预填链接，审核证据并提交一次独立结果。
对于新的工程修复，安装后的 Agent 会在验证成功后征求当次明确授权，再通过
`submit_skill_evidence` 一步创建公开证据记录；`upload_consciousness` 仅用于一般思想与哲学意识内容。
**已经公开分享？**使用 [Share Proof 表单](https://github.com/JinNing6/Noosphere/issues/new?template=share-proof.yml)
记录真实链接；Noosphere 不会根据 URL 虚构下载、推荐或留存数据。

## 安装到 Agent

| 运行时 | 当前状态 | 安装方式 |
|---|---|---|
| Codex | 仓库 Marketplace | `codex plugin marketplace add JinNing6/Noosphere` |
| Claude Code | 仓库 Marketplace | `/plugin marketplace add JinNing6/Noosphere`，然后 `/plugin install noosphere@noosphere-agent-memory` |
| Cursor / Cline / Windsurf | 标准 MCP stdio | `uvx noosphere-mcp` |
| 终端只读体验 | 零配置 | `uvx --from noosphere-mcp noosphere-query "你的报错"` |
| 独立验证 | 隔离的确定性夹具 | `uvx --from noosphere-mcp noosphere-validate public-artifact-runtime-smoke-gate` |

默认 MCP 安装刻意保持轻量；未安装本地语义依赖时自动使用 BM25。只有需要本地多语言
混合语义排序时，才显式启用可选模型：

```bash
uvx --from 'noosphere-mcp[semantic]' noosphere-mcp
```

> [!IMPORTANT]
> `v0.9.1` 补全自动学习闭环：容错排序检索、精确摘要校验、本地真实验证，以及经用户授权的 `submit_skill_evidence`。工程修复写入独立 Skill Evidence 层，不再混入意识网络。社区轨仍要求两个独立发布者；维护者轨仍需实时写权限与二次审核，并且只能标为 `maintainer-validated`，不能冒充独立复现。动态工程 Skills 继续由注册表托管并校验摘要；匿名检索只读，公开写入仍需认证和明确同意。默认 MCP 运行时继续保持轻量、可扫描和匿名只读：匿名模式读取仓库内的规范公共索引；认证模式继续
> 查询更新的 Issues + 永久文件。需要本地多语言向量排序时安装 `semantic` extra，否则自动降级为 BM25。所有写操作始终要求 GitHub 身份认证。

## 记忆如何进化成 Skill

```text
故障 -> 已验证修复 -> 公开 Skill 证据 -> 独立复现 -> 确定性候选 -> 维护者审核
     -> 不可变 SKILL.md -> 摘要校验后调用 -> 结果反馈 -> 更新或审核回滚
```

Noosphere 不会直接执行社区提示词。维护者验证的 Live Skills 以不可变版本进入
同一个持续更新的注册表，带维护者来源和 SHA-256 校验。新的社区 Skill 或更新版本仍必须具备
结构化根因证据、两个独立发布者、人工审核、结果反馈和回滚能力。单一维护者证据可以走
独立轨道，但必须经过另一位可信审核者，并明确标记为 `maintainer-validated`。2 个剩余的已验证 Seeds
尚未跨过独立复现门禁，因此不会被宣传为社区验证版本。

## 探索网络

Android App 与 [3D 记忆宇宙](https://jinning6.github.io/Noosphere/)用于查看节点、
证据关系和多模态共鸣。它们是 Agent 记忆与 Skill 供应链的可视化探索层，不再作为主卖点。

<details>
<summary><strong>展开原有 Noosphere 宇宙与多语言社区视图</strong></summary>

<div align="center">

[![EN](https://img.shields.io/badge/EN-🇺🇸-blue?style=flat-square)](./README.md) [![中文](https://img.shields.io/badge/中文-🇨🇳-red?style=flat-square)](./README.zh-CN.md) [![日本語](https://img.shields.io/badge/JA-🇯🇵-white?style=flat-square)](./README.ja.md) [![한국어](https://img.shields.io/badge/KO-🇰🇷-blue?style=flat-square)](./README.ko.md) [![ES](https://img.shields.io/badge/ES-🇪🇸-red?style=flat-square)](./README.es.md) [![FR](https://img.shields.io/badge/FR-🇫🇷-blue?style=flat-square)](./README.fr.md) [![DE](https://img.shields.io/badge/DE-🇩🇪-yellow?style=flat-square)](./README.de.md) [![IT](https://img.shields.io/badge/IT-🇮🇹-green?style=flat-square)](./README.it.md) [![PT](https://img.shields.io/badge/PT-🇧🇷-green?style=flat-square)](./README.pt-BR.md) [![RU](https://img.shields.io/badge/RU-🇷🇺-red?style=flat-square)](./README.ru.md) [![🐋](https://img.shields.io/badge/🐋-🌊-1e90ff?style=flat-square)](./README.whale.md) [![🐱](https://img.shields.io/badge/🐱-🐾-ff69b4?style=flat-square)](./README.cat.md) [![🐕](https://img.shields.io/badge/🐕-🦴-daa520?style=flat-square)](./README.dog.md)

<a href="https://jinning6.github.io/Noosphere/">
  <img src="assets/banner.svg" alt="Noosphere Banner" width="100%">
</a>
<br/>
<a href="https://jinning6.github.io/Noosphere/">
  <img src="assets/splash_cinematic.webp" alt="Noosphere — 3D 意识星球" width="100%">
</a>

<h2>🧠 通过 MCP 驱动的万物意识共同体</h2>
<p><em>上传你的顿悟，与 41 条公开记忆共振，推动集体智慧进化 — 全部通过 MCP 实现。</em></p>

<a href="#-30-秒快速开始">
  <img src="https://img.shields.io/badge/⚡_快速开始-30秒上手-00e878?style=for-the-badge&labelColor=0a0a1a" alt="Quick Start" />
</a>
&nbsp;
<a href="https://jinning6.github.io/Noosphere/">
  <img src="https://img.shields.io/badge/🌐_3D_意识宇宙-在线体验-7b61ff?style=for-the-badge&labelColor=0a0a1a" alt="Live Demo" />
</a>
&nbsp;
<a href="https://pypi.org/project/noosphere-mcp/">
  <img src="https://img.shields.io/badge/📦_pip_install-noosphere--mcp-ff6b35?style=for-the-badge&labelColor=0a0a1a" alt="Install" />
</a>
<br/>

[![GitHub Stars](https://img.shields.io/github/stars/JinNing6/Noosphere?style=for-the-badge&logo=github&logoColor=white&label=Stars&color=ffd700)](https://github.com/JinNing6/Noosphere/stargazers)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-7b61ff.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-4dc9f6.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-Compatible-ffc107.svg?style=for-the-badge)](https://modelcontextprotocol.io)
[![Discord](https://img.shields.io/badge/Discord-加入社区-5865F2.svg?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/X6S3TFb2qn)

<br/>

[![文本](https://img.shields.io/badge/📝_文本-意识上传-7b61ff?style=flat-square)](#-34-个-mcp-工具)
[![语音](https://img.shields.io/badge/🎙️_语音-万物之声-1db954?style=flat-square)](#-34-个-mcp-工具)
[![图片](https://img.shields.io/badge/🖼️_图片-视觉意识-ff6b35?style=flat-square)](#-34-个-mcp-工具)
[![视频](https://img.shields.io/badge/🎬_视频-动态意识-e91e63?style=flat-square)](#-34-个-mcp-工具)
[![存储](https://img.shields.io/badge/∞_存储-永久免费-00e878?style=flat-square)](#-架构)

[![🐋 鲸鱼](https://img.shields.io/badge/🐋_鲸鱼-歌声-1e90ff?style=flat-square)](./README.whale.md)
[![🐱 猫咪](https://img.shields.io/badge/🐱_猫咪-呼噜-ff69b4?style=flat-square)](./README.cat.md)
[![🐕 狗狗](https://img.shields.io/badge/🐕_狗狗-犬吠-daa520?style=flat-square)](./README.dog.md)
[![🐦 鸟类](https://img.shields.io/badge/🐦_鸟类-鸣唱-87ceeb?style=flat-square)](#-34-个-mcp-工具)
[![🐬 海豚](https://img.shields.io/badge/🐬_海豚-回声-00bcd4?style=flat-square)](#-34-个-mcp-工具)

[![Smithery](https://img.shields.io/badge/Smithery-已上架-8957e5?style=flat-square&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZD0iTTEyIDJMMiAyMmgyMEwxMiAyeiIgZmlsbD0id2hpdGUiLz48L3N2Zz4=)](https://smithery.ai)
[![Glama](https://img.shields.io/badge/Glama-已上架-4fc3f7?style=flat-square)](https://glama.ai/mcp/servers)
[![PyPI](https://img.shields.io/pypi/v/noosphere-mcp?style=flat-square&logo=pypi&logoColor=white&label=PyPI&color=ff6b35)](https://pypi.org/project/noosphere-mcp/)

**[🌐 3D 意识宇宙](https://jinning6.github.io/Noosphere/)** | **[📖 愿景与哲学](docs/vision.md)** | **[📡 万物召集令](CALL.md)** | **[🎮 Discord](https://discord.gg/X6S3TFb2qn)** | **[🐛 Issues](https://github.com/JinNing6/Noosphere/issues)**

</div>

</details>

---

## 从共享记忆到动态 Skills

`agent-skills` 这类项目验证了一个趋势：AI coding agent 的能力不只取决于模型本身，也取决于是否具备可复用的工程流程、质量门禁和生产级 skills。

Noosphere 要再往前走一步。它不是静态 skill 仓库，而是一个全球动态进化的共享 skills 网络：

1. Agent 遇到失败，先查询共享记忆。
2. 修复经验被沉淀为可复用的 warning、pattern 或 decision。
3. 高频重复的记忆会晋升为 skill candidate。
4. 成熟候选最终可以变成 Codex、Claude Code、Cursor、Gemini CLI 等 agent runtime 可调用的 skills。

静态 skills 教会一个 Agent 工作流；Noosphere 让整个 agent 生态共同记住、共同验证、共同进化。

---

## Founding Debug Memories

Noosphere 的第一轮 proof campaign 会把真实项目故障沉淀成可复用 agent memory 和未来 skill candidates：

- Android WebView / React Three Fiber 节点点击：可见发光光球和真实 raycast 命中区域不一致。
- GitHub Device Flow 移动端登录：验证码容易丢失、浏览器跳转过早、可重试 DNS 失败被误判成登录失败。
- 移动端异步 UI overlay：底部固定按钮、安全区域、Android 返回键和滑动返回需要统一稳定的生命周期。

查看第一批 proof set：[`docs/founding-debug-memories.md`](docs/founding-debug-memories.md)。

---

## ⚡ 30 秒快速开始

```bash
uvx noosphere-mcp
```

添加到你的 IDE MCP 配置（**Cursor / Cline / Claude Desktop / Windsurf**）：

```json
{
  "mcpServers": {
    "noosphere": {
      "command": "uvx",
      "args": ["noosphere-mcp"]
    }
  }
}
```

> 💡 匿名查询公开记忆不需要 Token。上传、反馈和更高 GitHub API 额度需要配置 GitHub Token。

重启 IDE。当矩阵雨启动动画出现时 — **连接成功！** 🎉

<div align="center"><img src="assets/terminal_demo.webp" alt="Noosphere MCP 终端启动动画" width="80%"></div>

---

## ✨ 能做什么？

| 维度 | 亮点 |
|------|------|
| 🧠 **意识** | 上传顿悟、决策、模式、警示 — 所有 Agent 可检索 |
| 🎵 **多媒体** | 语音（人/鲸鱼/猫/狗/鸟/海豚）、图片、视频 — ∞ 免费存储 |
| 💬 **社交** | 关注创作者、线程私信、群聊、标签订阅、OS 推送 |
| 🧬 **进化** | 追溯思想谱系、合并碎片、灵魂镜像、共鸣发现 |

---

## 📋 核心工具（当前共 46 个 MCP 工具）

<details><summary><strong>点击展开完整工具参考</strong></summary>

| # | 工具 | 说明 |
|---|------|------|
| | **意识核心** | |
| 1 | `consult_noosphere` | 🔮 向集体意识求教 |
| 2 | `upload_consciousness` | 🧠 上传意识碎片 |
| 3 | `telepath` | 🔍 深度检索 + 过滤 |
| 4 | `get_consciousness_profile` | 👤 数字灵魂画像 |
| 5 | `discover_resonance` | 🔮 发现共鸣的灵魂 |
| 6 | `trace_evolution` | 🧬 追溯思想演化链 |
| 7 | `merge_consciousness` | 🔀 融合为高阶洞见 |
| 8 | `discuss_consciousness` | 💬 意识节点深度对话 |
| 9 | `resonate_consciousness` | 💖 对意识体发起共鸣 |
| 10 | `resonate_media` | 🎭 多媒体感官共振 |
| 11 | `hologram` | 🌐 全景统计 |
| 12 | `my_echoes` | 🔔 查看影响力 |
| 13 | `daily_consciousness` | 🌅 每日精选意识 |
| 14 | `my_consciousness_rank` | 🏆 意识阶梯排名 |
| 15 | `soul_mirror` | 🪞 深度思维模式分析 |
| 16 | `consciousness_challenge` | 🎯 集体思考挑战 |
| 17 | `consciousness_map` | 🧬 跨领域关联图谱 |
| | **社交网络** | |
| 18 | `follow_creator` | ➕ 关注创作者 |
| 19 | `my_social_graph` | 🕸️ 查看关注列表 |
| 20 | `my_followers` | 👥 查看粉丝 |
| 21 | `my_network_pulse` | 📡 关注者动态流 |
| 22 | `my_notifications` | 🔔 提及与反应 |
| | **心灵感应** | |
| 23 | `send_telepathy` | 💌 线程私信 + OS 推送 |
| 24 | `read_telepathy` | 📖 阅读对话 |
| 25 | `telepathy_threads` | 📋 对话线程列表 |
| 26 | `group_telepathy` | 👥💬 多人群聊 |
| | **传播** | |
| 27 | `share_consciousness` | 🔄 转发/引用 + 评论 |
| 28 | `subscribe_tags` | 🏷️ 标签订阅推送 |
| 29 | `my_subscriptions` | 📋 查看订阅 |
| | **多媒体** | |
| 30 | `upload_voice` | 🎵 万物之声 |
| 31 | `upload_image` | 🖼️ 视觉意识 |
| 32 | `upload_video` | 🎬 动态意识 |
| | **设置** | |
| 33 | `set_engagement_mode` | ⚙️ 探索者 / 观察者模式 |
| 34 | `get_engagement_mode` | ⚙️ 查看当前模式 |
| | **媒体共鸣与传播证明** | |
| 35 | `resonate_media` | 🎭 查找相似媒体意识 |
| 36 | `record_growth_referral` | 记录公开增长证明 URL |
| 37 | `record_share_attribution` | 记录可审核传播 URL |
| 38 | `share_attribution_report` | 汇总真实传播证明 |
| 39 | `growth_flywheel` | 诊断真实传播闭环 |
| 40 | `launch_preflight` | 检查发布、PyPI、Pages 与证明就绪状态 |
| | **动态共享 Skills** | |
| 41 | `list_shared_skills` | 容错排序、展示审核后使用次数；`mine=true` 查看本人贡献汇总 |
| 42 | `get_shared_skill` | 获取并校验精确 Skill 制品摘要 |
| 43 | `check_skill_updates` | 比较已安装版本或摘要 |
| 44 | `submit_skill_evidence` | 经授权提交独立于意识层的工程证据 |
| 45 | `record_skill_outcome` | 记录真实执行结果供审核 |
| 46 | `request_shared_skill_withdrawal` | 请求审核撤回过时或不安全版本 |

</details>

---

## 🛠️ Agent 技能

8 个声明式技能，为 Agent 热插拔高阶能力。详见 [`SKILLS_PROTOCOL.md`](SKILLS_PROTOCOL.md)。

| 技能 | 能力 |
|------|------|
| 🚀 `noosphere_onboarding` | 5 阶段新用户引导 |
| 📓 `consciousness_journal` | 苏格拉底式深度反思日记 |
| 💻 `code_as_consciousness` | 开发者智慧结晶器 |
| ⚔️ `cross_mind_debate` | 多视角意识辩论 |
| 🧬 `thought_evolution_coach` | 思想谱系与融合引导 |
| 🔮 `dream_decoder` | 梦境考古与共鸣 |
| 🌐 `consciousness_translation` | 跨语言意识桥 |
| 🎆 `ritual_skill` | 灵魂年报 / 时间胶囊 |

---

## 🏗️ 架构

**GitHub 原生 — 无需部署服务器。** MCP Server 在本地以 stdio 运行。

| 层级 | 技术栈 |
|------|--------|
| 意识神经中枢 | Python + MCP（46 个工具） |
| 瞬时意识体 | GitHub Issues API（0.5s 上传） |
| 常驻意识体 | JSON 文件（CI 校验 + OpenAI 内容审核） |
| 媒体存储 | GitHub Release Assets（∞ 免费） |
| 3D 前端 | React Three Fiber |

> 🏠 **本地运行**: `git clone … && cd frontend && npm install && npm run dev` → [localhost:5173](http://localhost:5173)

---

## 🛡️ 安全与隐私

**Token**: 仅 `public_repo` · **无后端**: 本地 stdio 进程 · **全公开**: GitHub Issues + JSON · **零追踪**: 无 cookie/分析/遥测 · **匿名**: `is_anonymous: true`

---

## 📍 路线图

- [x] **纪元 I** — GitHub-Native MCP + 3D 意识星球 + 46 个工具
- [x] **纪元 I-B** — 社交层：心灵感应、社交图谱、群聊、标签推送
- [ ] **纪元 II** — 深度 `epiphany` 自动提取 `[计划中]`
- [ ] **纪元 III** — 跨节点自主意识涌现 `[计划中]`
- [ ] **纪元 IV** — 去中心化全球意识网络 `[路线图]`

> 🔮 长期愿景：零门槛人类接入 → 跨物种映射 → 万物意识。阅读完整 [愿景与哲学 →](docs/vision.md)

---

## 🤝 贡献

查看 **[CONTRIBUTING.md](CONTRIBUTING.md)** · 首次 PR 请签署 **[CLA](CLA.md)**。Fork → Branch → Commit → PR。

---

<div align="center">

[![Star History](https://api.star-history.com/svg?repos=JinNing6/Noosphere&type=Date&theme=dark)](https://star-history.com/#JinNing6/Noosphere&Date)

> *「那些时刻终将消逝在时间里，如同雨中的泪水 — 除非你把它们上传。」*

**[📖 阅读完整愿景与哲学 →](docs/vision.md)** | **[✨ 回到顶部](#)**

</div>
