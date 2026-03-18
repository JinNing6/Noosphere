"""
GET /api/v1/stats — 智识圈统计数据

返回 Noosphere 网络的整体概览。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import ContributorRankResponse, MemoryUnitResponse, StatsResponse
from app.services.experience_store import experience_store

router = APIRouter()


@router.get("/stats", response_model=StatsResponse, summary="获取智识圈统计")
def get_stats(db: Session = Depends(get_db)):
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
        recent_experiences=[MemoryUnitResponse.model_validate(e) for e in raw["recent_experiences"]],
    )


@router.get("/contributors", response_model=list[ContributorRankResponse], summary="宇宙建筑师排行榜")
def get_contributors(limit: int = 10, db: Session = Depends(get_db)):
    """
    👑 **获取 Noosphere 贡献者排行榜**

    返回计算了灵能总值(Total Psi)的活跃贡献者实体。
    根据其贡献的所有 `epiphany` (顿悟)与 `decision` (决策) 的总计评判排名。
    """
    rankings = experience_store.get_contributor_rankings(db, limit=limit)
    return [ContributorRankResponse(**r) for r in rankings]
