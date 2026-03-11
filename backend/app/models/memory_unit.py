"""
MemoryUnit — Noosphere 经验单元 SQLAlchemy ORM 模型

对应设计文档中的经验数据模型 (Section 三)
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, JSON
from app.database import Base


def generate_nsp_id() -> str:
    """生成 Noosphere 经验 ID: nsp-{short_uuid}"""
    return f"nsp-{uuid.uuid4().hex[:12]}"


class MemoryUnit(Base):
    """
    Noosphere 经验单元

    存储结构化的 Agent 经验记忆，包括失败记录、成功模式、
    设计模式、风险预警和迁移指南。
    """

    __tablename__ = "memory_units"

    id = Column(String(64), primary_key=True, default=generate_nsp_id)

    # ── 经验类型 ──
    # failure | success | pattern | warning | migration
    type = Column(String(20), nullable=False, index=True)

    # ── 场景描述 ──
    framework = Column(String(100), nullable=False, index=True)
    version = Column(String(50), nullable=True)
    task_type = Column(String(100), nullable=True)
    context = Column(Text, nullable=True)

    # ── 经验内容 ──
    observation = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=True)
    solution = Column(Text, nullable=True)
    evidence_before = Column(String(255), nullable=True)
    evidence_after = Column(String(255), nullable=True)

    # ── 元数据 ──
    contributor = Column(String(100), nullable=True, default="anonymous")
    trust_score = Column(Float, nullable=False, default=0.5)
    verified_by = Column(Integer, nullable=False, default=0)
    cited_count = Column(Integer, nullable=False, default=0)
    tags = Column(JSON, nullable=True, default=list)

    # ── 关联 ──
    relations = Column(JSON, nullable=True, default=dict)

    # ── 时间戳 ──
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<MemoryUnit(id={self.id}, type={self.type}, framework={self.framework})>"

    def to_search_text(self) -> str:
        """生成用于向量检索的拼接文本"""
        parts = [
            f"[{self.type}]",
            f"Framework: {self.framework}",
        ]
        if self.version:
            parts.append(f"Version: {self.version}")
        if self.task_type:
            parts.append(f"Task: {self.task_type}")
        if self.context:
            parts.append(f"Context: {self.context}")
        parts.append(f"Observation: {self.observation}")
        if self.root_cause:
            parts.append(f"Root Cause: {self.root_cause}")
        if self.solution:
            parts.append(f"Solution: {self.solution}")
        return " | ".join(parts)
