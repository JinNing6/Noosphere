"""
POST /api/v1/contribute — 贡献新经验

接收结构化经验数据，写入 Noosphere 智识圈。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import ContributeRequest, MemoryUnitResponse
from app.services.experience_store import experience_store

router = APIRouter()


@router.post(
    "/contribute",
    response_model=MemoryUnitResponse,
    status_code=201,
    summary="贡献新经验",
)
def contribute_experience(
    data: ContributeRequest,
    db: Session = Depends(get_db),
):
    """
    ✏️ **贡献经验到 Noosphere**

    将 Agent 或开发者的经验结构化后写入集体记忆网络。
    支持五种经验类型: failure, success, pattern, warning, migration。

    经验会同时写入:
    1. SQLite 关系型数据库（完整元数据）
    2. ChromaDB 向量数据库（语义检索索引）
    """
    unit = experience_store.contribute(db, data)
    return MemoryUnitResponse.model_validate(unit)
