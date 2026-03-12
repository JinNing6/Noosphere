"""
Pydantic v2 请求 / 响应模型

所有 API 端点的输入输出数据验证层
"""

from datetime import datetime

from pydantic import BaseModel, Field

# ────────────────── 贡献经验 ──────────────────


class EvidenceSchema(BaseModel):
    """经验证据"""

    before: str | None = None
    after: str | None = None


class ContributeRequest(BaseModel):
    """POST /api/v1/contribute 请求体"""

    type: str = Field(
        ...,
        description="经验类型: failure | success | pattern | warning | migration",
        pattern=r"^(failure|success|pattern|warning|migration)$",
    )
    framework: str = Field(..., description="AI 框架名称", min_length=1)
    version: str | None = Field(None, description="框架版本")
    task_type: str | None = Field(None, description="任务类型")
    context: str | None = Field(None, description="场景上下文")
    observation: str = Field(..., description="观察到的现象", min_length=1)
    root_cause: str | None = Field(None, description="根本原因")
    solution: str | None = Field(None, description="解决方案")
    evidence: EvidenceSchema | None = Field(None, description="数据证据")
    tags: list[str] = Field(default_factory=list, description="标签列表")
    contributor: str | None = Field(None, description="贡献者标识")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": "failure",
                    "framework": "langchain",
                    "version": "0.3.x",
                    "task_type": "rag_retrieval",
                    "context": "使用 RecursiveCharacterTextSplitter 处理中文文档时",
                    "observation": "chunk_size=1000 导致中文语义在句中被截断，检索精度下降 40%",
                    "root_cause": "默认分隔符不包含中文标点，无法正确断句",
                    "solution": "添加中文标点到 separators 列表：['。', '！', '？', '；', '\\n']",
                    "evidence": {"before": "retrieval_precision: 0.52", "after": "retrieval_precision: 0.89"},
                    "tags": ["chinese-nlp", "text-splitting", "rag", "langchain"],
                }
            ]
        }
    }


# ────────────────── 经验响应 ──────────────────


class MemoryUnitResponse(BaseModel):
    """经验单元完整响应"""

    id: str
    type: str
    framework: str
    version: str | None = None
    task_type: str | None = None
    context: str | None = None
    observation: str
    root_cause: str | None = None
    solution: str | None = None
    evidence_before: str | None = None
    evidence_after: str | None = None
    contributor: str | None = None
    trust_score: float
    verified_by: int
    cited_count: int
    tags: list[str] = []
    relations: dict = {}
    created_at: datetime
    similarity: float | None = Field(None, description="语义相似度（仅检索时返回）")

    model_config = {"from_attributes": True}


# ────────────────── 检索 ──────────────────


class RecallResponse(BaseModel):
    """GET /api/v1/recall 响应"""

    query: str
    total: int
    results: list[MemoryUnitResponse]


# ────────────────── 统计 ──────────────────


class StatsResponse(BaseModel):
    """GET /api/v1/stats 响应"""

    total_experiences: int
    active_contributors: int
    frameworks: int
    framework_distribution: dict[str, int] = {}
    type_distribution: dict[str, int] = {}
    recent_experiences: list[MemoryUnitResponse] = []


class ContributorRankResponse(BaseModel):
    """贡献者排行榜单体"""

    contributor: str
    epiphanies: int
    decisions: int
    total_score: int


# ────────────────── 通用 ──────────────────


class PaginatedResponse(BaseModel):
    """分页响应"""

    page: int
    size: int
    total: int
    items: list[MemoryUnitResponse]


class MessageResponse(BaseModel):
    """通用消息响应"""

    message: str
    id: str | None = None


# ────────────────── 意识上传 (Consciousness Upload) ──────────────────


class ConsciousnessUploadRequest(BaseModel):
    """POST /api/v1/upload 意识上传请求体

    遵循 CONSCIOUSNESS_PROTOCOL.md 定义的神圣格式
    """

    creator_signature: str = Field(
        ...,
        description="数字灵魂签名（GitHub ID 或赛博代号）",
        min_length=1,
    )
    is_anonymous: bool = Field(
        False,
        description="是否匿名，为 true 时展示为 '佚名潜行者 (Anonymous Stalker)'",
    )
    consciousness_type: str = Field(
        ...,
        description="意识形态: epiphany | decision | pattern | warning",
        pattern=r"^(epiphany|decision|pattern|warning)$",
    )
    thought_vector_text: str = Field(
        ...,
        description="核心思想、碎碎念或定律。请用最凝练的语言。",
        min_length=1,
    )
    context_environment: str = Field(
        ...,
        description="思想诞生的具体场景上下文，至少 10 个字符",
        min_length=10,
    )
    tags: list[str] = Field(
        default_factory=list,
        description="宇宙坐标系标签，用于快速聚类",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "creator_signature": "JinNing6",
                    "is_anonymous": False,
                    "consciousness_type": "epiphany",
                    "thought_vector_text": "UI 设计不应该是填充信息的容器，而应当是意识交互的流体映射。",
                    "context_environment": "在重构前端状态机时产生的直觉设计。",
                    "tags": ["frontend", "architecture", "philosophy"],
                }
            ]
        }
    }


class ConsciousnessUploadResponse(BaseModel):
    """POST /api/v1/upload 意识上传响应"""

    nsp_id: str = Field(..., description="本地存储 ID (nsp-xxx)")
    github_pr_url: str | None = Field(None, description="GitHub PR 链接")
    github_pr_number: int | None = Field(None, description="GitHub PR 编号")
    github_synced: bool = Field(False, description="是否已成功同步到 GitHub")
    message: str = Field(..., description="操作结果消息")
