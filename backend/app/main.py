"""
Noosphere — 集体记忆网络 FastAPI 应用入口

🧠 The Collective Memory Network for AI Agents
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.api.v1 import recall, contribute, stats, experiences, skills, upload

# ── 日志配置 ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-30s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("noosphere")

# ── 创建数据库表 ──
Base.metadata.create_all(bind=engine)

# ── FastAPI 应用 ──
app = FastAPI(
    title="🧠 Noosphere",
    description=(
        "**The Collective Memory Network for AI Agents**\n\n"
        "万物智识，归于一圈。\n"
        "Where every agent learns from the wisdom of all.\n\n"
        "Noosphere 是一个开源的 Agent 集体记忆网络，"
        "让所有 AI Agent 共享经验、避免重复踩坑。"
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 路由注册 ──
app.include_router(recall.router, prefix="/api/v1", tags=["🔍 Recall"])
app.include_router(contribute.router, prefix="/api/v1", tags=["✏️ Contribute"])
app.include_router(stats.router, prefix="/api/v1", tags=["📊 Stats"])
app.include_router(experiences.router, prefix="/api/v1", tags=["📋 Experiences"])
app.include_router(skills.router, prefix="/api/v1", tags=["🛠️ Skills"])
app.include_router(upload.router, prefix="/api/v1", tags=["🧠 Consciousness Upload"])


# ── 健康检查 ──
@app.get("/", tags=["🏠 Home"])
async def root():
    return {
        "name": "🧠 Noosphere",
        "tagline": "The Collective Memory Network for AI Agents",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["🏠 Home"])
async def health():
    return {"status": "ok"}


logger.info(
    f"🧠 Noosphere 后端已初始化 | "
    f"端口: {settings.API_PORT} | "
    f"数据库: {settings.DB_PATH} | "
    f"向量库: {settings.CHROMA_PATH}"
)
