"""
GET /api/v1/stats — 智识圈统计数据

返回 Noosphere 网络的整体概览。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import StatsResponse, MemoryUnitResponse
from app.services.experience_store import experience_store

router = APIRouter()


@router.get("/stats", response_model=StatsResponse, summary="获取智识圈统计")
async def get_stats(db: Session = Depends(get_db)):
    """
    📊 **Noosphere 统计概览**

    返回集体记忆网络的关键指标:
    - 总经验数
    - 活跃贡献者数
    - 覆盖框架数
    - 框架分布
    - 类型分布
    - 最近经验
    """
    raw = experience_store.get_stats(db)
    return StatsResponse(
        total_experiences=raw["total_experiences"],
        active_contributors=raw["active_contributors"],
        frameworks=raw["frameworks"],
        framework_distribution=raw["framework_distribution"],
        type_distribution=raw["type_distribution"],
        recent_experiences=[
            MemoryUnitResponse.model_validate(e) for e in raw["recent_experiences"]
        ],
    )
