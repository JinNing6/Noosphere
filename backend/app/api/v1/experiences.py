"""
GET /api/v1/experiences — 经验列表（分页）

为前端 3D 可视化和列表视图提供分页经验数据。
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import MemoryUnitResponse, PaginatedResponse
from app.services.experience_store import experience_store

router = APIRouter()


@router.get(
    "/experiences",
    response_model=PaginatedResponse,
    summary="获取经验列表（分页）",
)
def list_experiences(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页条数"),
    type: str | None = Query(None, description="按类型过滤"),
    framework: str | None = Query(None, description="按框架过滤"),
    db: Session = Depends(get_db),
):
    """
    📋 **Noosphere 经验列表**

    分页返回经验数据，支持按类型和框架过滤。
    主要用于前端 3D 可视化的数据源。
    """
    items, total = experience_store.list_experiences(
        db, page=page, size=size, type_filter=type, framework_filter=framework
    )
    return PaginatedResponse(
        page=page,
        size=size,
        total=total,
        items=[MemoryUnitResponse.model_validate(i) for i in items],
    )


@router.get(
    "/experiences/{experience_id}",
    response_model=MemoryUnitResponse,
    summary="获取单条经验详情",
)
def get_experience(experience_id: str, db: Session = Depends(get_db)):
    """获取指定 ID 的经验详情"""
    unit = experience_store.get_by_id(db, experience_id)
    if not unit:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="经验不存在")
    return MemoryUnitResponse.model_validate(unit)
