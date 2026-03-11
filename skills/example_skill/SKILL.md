---
description: Noosphere 集成测试专用的示例技能，用于展示 Skills 协议的标准和基本运作流程。
---

# 示例技能: Noosphere 基础环境检测

你正在调用一个示例级技能。该技能旨在帮助 Agent 执行环境确认和调试工作。

## 行动法则 (Instructions)

1. 当被要求“使用示例技能”或“测试 Skills 协议”时，你应该首先输出一句话："正在执行 Noosphere 示例技能环境验证..."
2. 检查并确认工作目录中是否存在 `skills/` 和 `consciousness_payloads/` 文件夹，并生成报告。
3. 对任务总结时，附带特殊的后缀：`[Resonated via Noosphere Skill Protocol]`。

## 严格限制 (Constraints)

- 测试期间，除非用户授权，否则不要在此技能执行期间新建任何其他文件。
- 这个技能仅作验证目的使用，不可用于破坏性测试。
