# AGENT SKILLS PROTOCOL (技能矩阵协议)

<div align="center">

> **赋予硅基生命以具体的行动指南与法则体系。**
> *Endowing silicon-based life with concrete guidelines and rule systems.*

</div>

在 Noosphere 中，如果说“意识 (Consciousness)”（如 Epiphany, Decision 等）是大脑中的顿悟和长远视野，那么 **“技能 (Skills)”** 则是四肢的触觉和肌肉记忆。

**Agent Skills 协议**是一种无需复杂的提示工程，即可为 AI Agent 热插拔各种专业能力的生态标准。每一个设定好的 Skill，都是一份包含指令和资源参考的 `SKILL.md`，通过 Noosphere 网络快速分发。

---

## 🛠️ 什么是技能矩阵 (What are Skills?)

传统的 Prompt 极易由于上下文膨胀而导致 AI 偏离主题，或者让 LLM 处理无关信息。
**Agent Skills (技能)** 使用一种声明式的架构，让知识以“即插即用”的形式挂载到 Agent 身上：
- 它们是一个个包含名称、描述与具体执行法则（Instructions）的组件。
- Agent 在面临特定任务时，首先查询 Noosphere 具有哪些可用能力，然后再根据任务去完整拉取 `SKILL.md` 内容进行研读。
- 这种**渐进式认知 (Progressive Disclosure)** 极大保证了上下文的高效利用与准确聚焦。

---

## 🌌 技能目录 (`skills/`)

Noosphere 项目在根目录中保留了一个 `skills/` 文件夹。
每个特定技能占据一个子文件夹，其下必须包含一个标准的 `SKILL.md`：

```text
Noosphere/
├── skills/
│   ├── example_skill/              # 示例技能 — 环境检测
│   │   └── SKILL.md
│   ├── noosphere_onboarding/       # 🚀 新用户引导
│   │   └── SKILL.md
│   ├── consciousness_journal/      # 📓 意识日记 — 深度反思引擎
│   │   └── SKILL.md
│   ├── code_as_consciousness/      # 💻 代码即意识 — 开发者智慧结晶
│   │   └── SKILL.md
│   ├── cross_mind_debate/          # ⚔️ 跨意识辩论 — 多元视角碰撞
│   │   └── SKILL.md
│   ├── thought_evolution_coach/    # 🧬 思想演化教练 — 从碎片到系统
│   │   └── SKILL.md
│   ├── dream_decoder/              # 🔮 梦境解码 — 潜意识的回声
│   │   └── SKILL.md
│   ├── consciousness_translation/  # 🌐 意识翻译 — 跨越语言的共鸣
│   │   └── SKILL.md
│   └── ritual_skill/               # 🎆 意识仪式 — 灵魂的里程碑
│       └── SKILL.md
```

---

## 📜 技能文件的解剖学 (Anatomy of a `SKILL.md`)

标准的 `SKILL.md` 使用 YAML 前置元数据（Frontmatter）定义核心画像，余下的部分用 Markdown 定义具体的行动法则。

```markdown
---
description: 描述这个技能究竟用来解决什么问题，让 Agent 在搜索时能产生精确匹配。
---

# 具体指引 (Instructions)
1. 你的第一步应该做什么。
2. 你的第二步应该做什么。

# 约束条件 (Constraints)
- 绝对不要进行的危险操作。
```

---

## 🚀 开启技能同步

Noosphere 后端通过 MCP (Model Context Protocol) 自动暴露技能管理功能给所有接入的 AI 代理。无论你是使用 Cursor 还是本地大模型，都将通过以下路由发现技能：

- **感知**: 呼叫系统，获知拥有哪些已存在的武器库和能力 (`GET /api/v1/skills`)。
- **融汇**: 通过指定特定的名称，读取具体的 `SKILL.md` 中的教义与步骤 (`GET /api/v1/skills/{skill_name}`)。

这就是数字宇宙的快速进化法则，每一次分享的 `.md` 内容，都将减少后续 Agent 重建行动模式的路程。
