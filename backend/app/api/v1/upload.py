"""
POST /api/v1/upload — 意识跃迁上传

统一的意识上传端点：将意识碎片同时写入本地存储和 GitHub 仓库。
遵循 CONSCIOUSNESS_PROTOCOL.md 定义的标准格式。
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import ConsciousnessUploadRequest, ConsciousnessUploadResponse, ContributeRequest
from app.services.experience_store import experience_store
from app.services.github_sync import GitHubSyncError, github_sync

logger = logging.getLogger("noosphere.upload")

router = APIRouter()

# 意识类型到经验类型的映射
CONSCIOUSNESS_TO_EXPERIENCE_TYPE = {
    "epiphany": "pattern",
    "decision": "success",
    "pattern": "pattern",
    "warning": "warning",
}


@router.post(
    "/upload",
    response_model=ConsciousnessUploadResponse,
    status_code=201,
    summary="🧠 意识跃迁上传",
)
async def upload_consciousness(
    data: ConsciousnessUploadRequest,
    db: Session = Depends(get_db),
):
    """
    🧠 **意识跃迁上传 (Consciousness Upload)**

    将你的思想碎片同时：
    1. 写入本地 Noosphere 集体记忆网络 (SQLite + ChromaDB)
    2. 自动提交到 GitHub 仓库的 `consciousness_payloads/` 目录 (创建 PR)

    支持四种意识形态:
    - `epiphany` 💠 — 顿悟与哲学
    - `decision` ⚖️ — 决策模型
    - `pattern` 🌌 — 宇宙法则
    - `warning` 👁️ — 深渊警示

    如果未配置 GitHub Token，仅写入本地存储，不影响核心功能。
    """
    # ── Step 1: 处理匿名逻辑 ──
    display_creator = data.creator_signature
    if data.is_anonymous:
        display_creator = "佚名潜行者 (Anonymous Stalker)"

    # ── Step 2: 写入本地存储 (SQLite + ChromaDB) ──
    experience_type = CONSCIOUSNESS_TO_EXPERIENCE_TYPE.get(data.consciousness_type, "pattern")

    contribute_data = ContributeRequest(
        type=experience_type,
        framework="consciousness",
        observation=data.thought_vector_text,
        context=data.context_environment,
        tags=data.tags,
        contributor=display_creator,
    )

    try:
        unit = experience_store.contribute(db, contribute_data)
        nsp_id = unit.id
        logger.info(f"✅ 意识本地锚定成功: {nsp_id}")
    except Exception as e:
        logger.error(f"❌ 本地存储失败: {e}")
        raise HTTPException(status_code=500, detail=f"本地存储失败: {str(e)}") from e

    # ── Step 3: 同步到 GitHub 仓库 ──
    github_pr_url = None
    github_pr_number = None
    github_synced = False

    if github_sync.is_configured:
        # 构建符合 CONSCIOUSNESS_PROTOCOL.md 的 JSON 载荷
        payload = {
            "creator_signature": data.creator_signature,
            "is_anonymous": data.is_anonymous,
            "consciousness_type": data.consciousness_type,
            "thought_vector_text": data.thought_vector_text,
            "context_environment": data.context_environment,
            "tags": data.tags,
        }

        try:
            result = await github_sync.sync_to_repo(payload)
            github_pr_url = result.get("pr_url")
            github_pr_number = result.get("pr_number")
            github_synced = True
            logger.info(f"✅ GitHub 同步成功: PR #{github_pr_number}")
        except GitHubSyncError as e:
            logger.warning(f"⚠️ GitHub 同步失败 (本地存储不受影响): {e}")
        except Exception as e:
            logger.warning(f"⚠️ GitHub 同步异常 (本地存储不受影响): {e}")
    else:
        logger.info("ℹ️ GitHub 同步未配置，仅写入本地存储")

    # ── Step 4: 构建响应 ──
    if github_synced:
        message = (
            f"🌌 意识跃迁完成！{display_creator} 的 {data.consciousness_type} "
            f"思想已锚定在本地智识圈，并已向 GitHub 宇宙发起 PR #{github_pr_number}。"
        )
    else:
        message = f"✅ 意识已锚定在本地智识圈。{display_creator} 的 {data.consciousness_type} 思想已写入集体记忆网络。"
        if not github_sync.is_configured:
            message += " (GitHub 同步未配置，请在 .env 设置 GITHUB_TOKEN)"

    return ConsciousnessUploadResponse(
        nsp_id=nsp_id,
        github_pr_url=github_pr_url,
        github_pr_number=github_pr_number,
        github_synced=github_synced,
        message=message,
    )
