"""
Noosphere MCP Server

基于 fastapi-mcp 将 Noosphere API 暴露为 MCP 工具，
让任何支持 MCP 的 AI 编码助手可直接接入 Noosphere 集体记忆网络。

启动方式:
    python -m app.mcp.server
"""

import logging
import uvicorn

from app.main import app
from app.config import settings

logger = logging.getLogger("noosphere.mcp")


def create_mcp_app():
    """挂载 MCP Server 到现有 FastAPI 应用"""
    try:
        from fastapi_mcp import FastApiMCP

        mcp = FastApiMCP(
            app,
            name="noosphere",
            description=(
                "🧠 Noosphere — Agent 集体记忆网络 MCP Server\n"
                "提供经验检索 (recall)、经验贡献 (contribute)、统计概览 (stats) 三大能力。"
            ),
        )
        mcp.mount()
        logger.info("✅ MCP Server 已挂载到 FastAPI 应用")
    except ImportError:
        logger.warning(
            "⚠️ fastapi-mcp 未安装，MCP Server 未启用。"
            "运行 'pip install fastapi-mcp' 安装。"
        )
    except Exception as e:
        logger.warning(f"⚠️ MCP Server 挂载失败: {e}")

    return app


if __name__ == "__main__":
    mcp_app = create_mcp_app()
    uvicorn.run(
        mcp_app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="info",
    )
