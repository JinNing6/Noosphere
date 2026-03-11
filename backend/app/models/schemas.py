"""
Pydantic v2 请求 / 响应模型

所有 API 端点的输入输出数据验证层
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ────────────────── 贡献经验 ──────────────────


class EvidenceSchema(BaseModel):
    """经验证据"""
    before: Optional[str] = None
    after: Optional[str] = None


class ContributeRequest(BaseModel):
    """POST /api/v1/contribute 请求体"""
    type: str = Field(
        ...,
        description="经验类型: failure | success | pattern | warning | migration",
        pattern=r"^(failure|success|pattern|warning|migration)$",
    )
    framework: str = Field(..., description="AI 框架名称", min_length=1)
    version: Optional[str] = Field(None, description="框架版本")
    task_type: Optional[str] = Field(None, description="任务类型")
    context: Optional[str] = Field(None, description="场景上下文")
    observation: str = Field(..., description="观察到的现象", min_length=1)
    root_cause: Optional[str] = Field(None, description="根本原因")
    solution: Optional[str] = Field(None, description="解决方案")
    evidence: Optional[EvidenceSchema] = Field(None, description="数据证据")
    tags: list[str] = Field(default_factory=list, description="标签列表")
    contributor: Optional[str] = Field(None, description="贡献者标识")

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
    version: Optional[str] = None
    task_type: Optional[str] = None
    context: Optional[str] = None
    observation: str
    root_cause: Optional[str] = None
    solution: Optional[str] = None
    evidence_before: Optional[str] = None
    evidence_after: Optional[str] = None
    contributor: Optional[str] = None
    trust_score: float
    verified_by: int
    cited_count: int
    tags: list[str] = []
    relations: dict = {}
    created_at: datetime
    similarity: Optional[float] = Field(None, description="语义相似度（仅检索时返回）")

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
    id: Optional[str] = None
