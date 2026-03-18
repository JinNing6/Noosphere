"""
GET /api/v1/recall — 经验语义检索

从 Noosphere 集体记忆中按自然语言查询检索相关经验。
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import MemoryUnitResponse, RecallResponse
from app.services.experience_store import experience_store

router = APIRouter()


@router.get("/recall", response_model=RecallResponse, summary="检索集体经验")
def recall_experiences(
    q: str = Query(..., description="自然语言查询", min_length=1),
    framework: str | None = Query(None, description="按框架过滤"),
    limit: int = Query(10, ge=1, le=50, description="返回条数"),
    db: Session = Depends(get_db),
):
    """
    🔍 **Noosphere 经验检索**

    从集体记忆网络中语义检索相关经验。
    支持自然语言查询 + 框架过滤。

    示例查询:
    - `LangChain RAG 检索精度低`
    - `CrewAI multi-agent deadlock`
    - `GPT-4o code review prompt`
    """
    results = experience_store.recall(db, query=q, framework=framework, limit=limit)
    return RecallResponse(
        query=q,
        total=len(results),
        results=[MemoryUnitResponse(**r) for r in results],
    )
