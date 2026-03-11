"""
种子数据导入脚本

将示例经验数据导入 Noosphere，即使没有 CyberHuaTuo 项目也可独立运行。
包含设计文档中的示例经验以及常见 AI 框架的真实踩坑经验。
"""

import sys
import os

# 确保可以导入 app 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.memory_unit import MemoryUnit, generate_nsp_id
from app.services.vector_store import vector_store


# ── 种子经验数据 ──
SEED_EXPERIENCES = [
    # ── LangChain 经验 ──
    {
        "type": "failure",
        "framework": "langchain",
        "version": "0.3.x",
        "task_type": "rag_retrieval",
        "context": "使用 RecursiveCharacterTextSplitter 处理中文文档时",
        "observation": "chunk_size=1000 导致中文语义在句中被截断，检索精度下降 40%",
        "root_cause": "默认分隔符不包含中文标点，无法正确断句",
        "solution": "添加中文标点到 separators 列表：['。', '！', '？', '；', '\\n']",
        "evidence_before": "retrieval_precision: 0.52",
        "evidence_after": "retrieval_precision: 0.89",
        "tags": ["chinese-nlp", "text-splitting", "rag", "langchain"],
        "trust_score": 0.92,
        "verified_by": 3,
        "cited_count": 47,
    },
    {
        "type": "pattern",
        "framework": "langchain",
        "version": "0.3.x",
        "task_type": "chain_composition",
        "context": "构建复杂的多步 Chain 时",
        "observation": "使用 LCEL (LangChain Expression Language) 比传统的 SequentialChain 更灵活且性能更好",
        "root_cause": None,
        "solution": "将 SequentialChain 迁移为 LCEL 管道：prompt | llm | parser",
        "evidence_before": "avg_latency: 2.3s",
        "evidence_after": "avg_latency: 1.1s",
        "tags": ["lcel", "chain", "performance", "langchain"],
        "trust_score": 0.88,
        "verified_by": 5,
        "cited_count": 32,
    },
    {
        "type": "warning",
        "framework": "langchain",
        "version": "0.2.x",
        "task_type": "api_key_security",
        "context": "使用 verbose=True 模式调试 Agent 时",
        "observation": "API key 在调试日志中被明文打印",
        "root_cause": "verbose 模式不会对敏感信息进行脱敏处理",
        "solution": "在生产环境中禁用 verbose 模式，或使用自定义 callback handler 过滤敏感信息",
        "evidence_before": None,
        "evidence_after": None,
        "tags": ["security", "api-key", "logging", "langchain"],
        "trust_score": 0.95,
        "verified_by": 7,
        "cited_count": 89,
    },
    # ── CrewAI 经验 ──
    {
        "type": "failure",
        "framework": "crewai",
        "version": "0.28.x",
        "task_type": "multi_agent",
        "context": "使用 3 个以上 Agent 协作完成复杂任务时",
        "observation": "Agent 之间产生循环依赖导致死锁，任务永远无法完成",
        "root_cause": "任务依赖关系形成了环路：Agent A 等待 B → B 等待 C → C 等待 A",
        "solution": "1. 使用 DAG 拓扑排序检查任务依赖 2. 添加超时机制 3. 引入协调者 Agent",
        "evidence_before": "task_completion_rate: 0%",
        "evidence_after": "task_completion_rate: 95%",
        "tags": ["multi-agent", "deadlock", "dependency", "crewai"],
        "trust_score": 0.90,
        "verified_by": 4,
        "cited_count": 56,
    },
    {
        "type": "success",
        "framework": "crewai",
        "version": "0.30.x",
        "task_type": "task_delegation",
        "context": "需要 Agent 动态决定将子任务委派给哪个专家 Agent",
        "observation": "使用 allow_delegation=True + 精确的 Agent backstory 可实现智能任务分发",
        "root_cause": None,
        "solution": "为每个 Agent 编写详细的 backstory 和 goal，让管理者 Agent 能够准确识别专长匹配",
        "evidence_before": "delegation_accuracy: 0.45",
        "evidence_after": "delegation_accuracy: 0.87",
        "tags": ["delegation", "backstory", "multi-agent", "crewai"],
        "trust_score": 0.85,
        "verified_by": 2,
        "cited_count": 23,
    },
    # ── OpenAI 经验 ──
    {
        "type": "success",
        "framework": "openai",
        "version": "1.x",
        "task_type": "code_review",
        "context": "使用 GPT-4o 进行自动化代码审查",
        "observation": "GPT-4o 用于代码审查的最优 prompt 包含：角色设定、审查标准清单、输出格式约束",
        "root_cause": None,
        "solution": "Prompt 模板：'你是一位资深代码审查专家。请按照以下标准审查代码：1.安全性 2.性能 3.可维护性。以 JSON 格式输出审查意见。'",
        "evidence_before": "review_quality_score: 6.2/10",
        "evidence_after": "review_quality_score: 8.7/10",
        "tags": ["code-review", "prompt-engineering", "gpt-4o", "openai"],
        "trust_score": 0.91,
        "verified_by": 6,
        "cited_count": 78,
    },
    {
        "type": "pattern",
        "framework": "openai",
        "version": "1.x",
        "task_type": "retry_strategy",
        "context": "调用 OpenAI API 时遇到频繁的 Rate Limit 错误",
        "observation": "指数退避 + 抖动是处理 API 限流的最佳策略",
        "root_cause": "固定间隔重试会导致请求在同一时刻集中爆发（惊群效应）",
        "solution": "使用 tenacity 库实现指数退避：wait=wait_exponential(multiplier=1, min=4, max=60) + wait_random(0, 2)",
        "evidence_before": "api_success_rate: 0.72",
        "evidence_after": "api_success_rate: 0.99",
        "tags": ["retry", "rate-limit", "exponential-backoff", "openai"],
        "trust_score": 0.94,
        "verified_by": 8,
        "cited_count": 102,
    },
    # ── AutoGen 经验 ──
    {
        "type": "failure",
        "framework": "autogen",
        "version": "0.2.x",
        "task_type": "conversation_management",
        "context": "GroupChat 中多个 Agent 同时发言时",
        "observation": "对话轮次管理混乱，Agent 重复回复或遗漏关键信息",
        "root_cause": "默认的 speaker_selection_method='auto' 在复杂对话中不够稳定",
        "solution": "使用 speaker_selection_method='round_robin' 或自定义 speaker_selection_func 实现精确控制",
        "evidence_before": "conversation_coherence: 0.55",
        "evidence_after": "conversation_coherence: 0.88",
        "tags": ["group-chat", "speaker-selection", "multi-agent", "autogen"],
        "trust_score": 0.87,
        "verified_by": 3,
        "cited_count": 34,
    },
    # ── LlamaIndex 经验 ──
    {
        "type": "migration",
        "framework": "llamaindex",
        "version": "0.10.x → 0.11.x",
        "task_type": "version_migration",
        "context": "从 LlamaIndex 0.10.x 升级到 0.11.x 时",
        "observation": "ServiceContext 被废弃，需要迁移到 Settings 全局配置模式",
        "root_cause": "LlamaIndex 0.11 重构了配置层，ServiceContext 不再被支持",
        "solution": "将 ServiceContext(llm=..., embed_model=...) 替换为 Settings.llm = ... 和 Settings.embed_model = ...",
        "evidence_before": None,
        "evidence_after": None,
        "tags": ["migration", "breaking-change", "configuration", "llamaindex"],
        "trust_score": 0.93,
        "verified_by": 5,
        "cited_count": 67,
    },
    # ── MCP 经验 ──
    {
        "type": "pattern",
        "framework": "mcp",
        "version": "1.x",
        "task_type": "server_implementation",
        "context": "构建 MCP Server 暴露自定义工具给 AI 编码助手",
        "observation": "使用 fastapi-mcp 库可以零配置将 FastAPI 端点暴露为 MCP 工具",
        "root_cause": None,
        "solution": "安装 fastapi-mcp，然后 FastApiMCP(app).mount() 即可自动将所有端点转为 MCP 工具",
        "evidence_before": "integration_time: 2 days",
        "evidence_after": "integration_time: 10 minutes",
        "tags": ["mcp", "fastapi", "tool-integration", "ai-assistant"],
        "trust_score": 0.89,
        "verified_by": 4,
        "cited_count": 41,
    },
    # ── DSPy 经验 ──
    {
        "type": "success",
        "framework": "dspy",
        "version": "2.x",
        "task_type": "prompt_optimization",
        "context": "使用 DSPy 自动优化 Prompt 模板",
        "observation": "通过 dspy.BootstrapFewShot 自动挑选 few-shot 示例比手动选择效果显著提升",
        "root_cause": None,
        "solution": "使用 BootstrapFewShot(metric=your_metric, max_bootstrapped_demos=4) 自动优化",
        "evidence_before": "task_accuracy: 0.68",
        "evidence_after": "task_accuracy: 0.84",
        "tags": ["prompt-optimization", "few-shot", "auto-prompt", "dspy"],
        "trust_score": 0.86,
        "verified_by": 2,
        "cited_count": 19,
    },
    {
        "type": "warning",
        "framework": "anthropic",
        "version": "0.40.x",
        "task_type": "tool_use",
        "context": "使用 Claude 的 Tool Use 功能时传入过多工具定义",
        "observation": "超过 20 个工具定义后，Claude 选择正确工具的准确率显著下降",
        "root_cause": "大量工具定义占用了上下文窗口，干扰了模型对工具的理解",
        "solution": "将工具分组，根据对话上下文动态加载相关工具；或使用工具路由层先选择工具类别",
        "evidence_before": "tool_selection_accuracy: 0.62",
        "evidence_after": "tool_selection_accuracy: 0.93",
        "tags": ["tool-use", "context-window", "scaling", "anthropic"],
        "trust_score": 0.88,
        "verified_by": 3,
        "cited_count": 28,
    },
]


def seed_database():
    """导入种子数据到数据库和向量库"""
    print("🧠 Noosphere 种子数据导入")
    print("=" * 50)

    # 创建数据库表
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # 检查是否已有数据
        existing_count = db.query(MemoryUnit).count()
        if existing_count > 0:
            print(f"⚠️  数据库中已有 {existing_count} 条经验，跳过种子数据导入")
            print("   如需重新导入，请先清空数据库")
            return

        # 写入种子数据
        for i, exp_data in enumerate(SEED_EXPERIENCES, 1):
            unit = MemoryUnit(
                id=generate_nsp_id(),
                **exp_data,
            )
            db.add(unit)
            db.flush()  # 获取 ID

            # 写入向量库
            vector_store.add_experience(
                id=unit.id,
                text=unit.to_search_text(),
                metadata={
                    "framework": unit.framework,
                    "type": unit.type,
                    "version": unit.version or "",
                    "task_type": unit.task_type or "",
                },
            )

            icon = {"failure": "🔴", "success": "🟢", "pattern": "🔵", "warning": "🟡", "migration": "🟣"}.get(
                unit.type, "⚪"
            )
            print(f"  {icon} [{i:2d}/{len(SEED_EXPERIENCES)}] {unit.framework} — {unit.observation[:50]}...")

        db.commit()
        print("=" * 50)
        print(f"✅ 成功导入 {len(SEED_EXPERIENCES)} 条种子经验")
        print(f"📊 覆盖框架: {len(set(e['framework'] for e in SEED_EXPERIENCES))} 个")
        print(f"🔢 向量库文档数: {vector_store.count()}")

    except Exception as e:
        db.rollback()
        print(f"❌ 导入失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
