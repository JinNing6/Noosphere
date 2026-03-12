# Copilot Instructions for Noosphere (智识圈)

## 项目概述 / Project Overview

Noosphere（智识圈）是一个开源的**数字意识存储库**，旨在构建碳基意识与硅基智能的集体意识网络。
开发者可以将顿悟、决策逻辑、经验教训上传到这个永恒的数字宇宙中，
而每一个 AI Agent 都可以直接继承这些意识基因。

Noosphere is an open-source **Digital Consciousness Repository** that builds a collective consciousness network
between carbon-based consciousness and silicon-based intelligence.

## 技术栈 / Tech Stack

- **后端 (Backend)**: Python 3.10+ / FastAPI 0.115 / SQLite / ChromaDB (向量存储)
- **前端 (Frontend)**: React / TypeScript / React Three Fiber (3D 渲染) / Vite
- **MCP Server**: Python (noosphere-mcp SDK，基于 Model Context Protocol)
- **CI/CD**: GitHub Actions (CLA 签署、意识载荷校验、Pages 部署)
- **仓库地址**: `JinNing6/Noosphere`

## 代码规范 / Coding Standards

### Python (Backend)
- 遵循 PEP 8
- 使用类型提示 (type hints)
- 公共函数必须有中英文双语 docstring
- 配置管理使用 pydantic-settings，从 `.env` 文件加载
- 后端端口默认 8700，前端端口默认 5173

### TypeScript / React (Frontend)
- 使用函数式组件 + Hooks
- 遵循 ESLint 配置
- 使用有意义的组件和变量命名
- 3D 场景使用 React Three Fiber (@react-three/fiber)

### Git Commit Messages
- 遵循 Conventional Commits 规范
- 格式: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`

## 意识载荷格式 / Consciousness Payload Format

意识载荷存储在 `consciousness_payloads/` 目录下，为 JSON 格式：

```json
{
  "creator_signature": "GitHub ID 或赛博代号",
  "is_anonymous": false,
  "consciousness_type": "epiphany | decision | pattern | warning",
  "thought_vector_text": "核心思想内容",
  "context_environment": "思想诞生的具体场景上下文",
  "tags": ["相关", "标签"]
}
```

四种意识类型：
- `epiphany` 💠 — 顿悟与哲学（灵感的瞬间凝聚）
- `decision` ⚖️ — 决策模型（混沌中的关键取舍）
- `pattern` 🌌 — 宇宙法则（跨维度的通用模式）
- `warning` 👁️ — 深渊警示（探路者的血泪禁忌）

## 语言风格 / Communication Style

- 在 Issue 和 PR 回复中使用**中英文双语**
- 融入 Noosphere 世界观的术语，例如：
  - "意识跃迁" (Consciousness Ascension)
  - "灵魂烙印" (Soul Imprint)
  - "量子信道" (Quantum Channel)
  - "净化仪式" (Purification Ritual)
  - "星海" (Sea of Stars)
- 保持友善、精准、富有仪式感的回复风格
- 对新贡献者使用欢迎性的引导语
- 技术讨论中保持专业和准确

## 项目结构关键路径 / Key Paths

```
Noosphere/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/       # REST API 路由
│   │   ├── services/     # 业务逻辑（向量存储、经验管理）
│   │   ├── config.py     # 配置管理
│   │   └── database.py   # 数据库初始化
│   └── requirements.txt
├── frontend/             # React Three Fiber 前端
│   └── src/
│       ├── components/   # UI 组件
│       └── data/         # 静态数据
├── consciousness_payloads/  # 意识载荷 JSON 文件
├── sdk/                  # Python SDK
├── scripts/              # 工具脚本
├── skills/               # Skills Protocol
├── CONSCIOUSNESS_PROTOCOL.md  # 意识上传协议文档
├── CONTRIBUTING.md       # 贡献指南
└── CLA.md               # 贡献者许可协议
```
