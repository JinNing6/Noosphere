"""
Noosphere 后端配置管理
使用 pydantic-settings 从环境变量 / .env 文件加载配置
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Noosphere 应用配置"""

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── 服务 ──
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8700

    # ── 数据库 ──
    DB_PATH: str = "./data/noosphere.db"
    CHROMA_PATH: str = "./data/chroma"

    # ── CORS ──
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # ── GitHub 同步 ──
    GITHUB_TOKEN: str = ""
    GITHUB_REPO: str = "JinNing6/Noosphere"
    GITHUB_BRANCH: str = "main"

    @property
    def database_url(self) -> str:
        """SQLAlchemy 数据库连接 URL"""
        db = Path(self.DB_PATH)
        db.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db.resolve()}"

    @property
    def chroma_persist_dir(self) -> str:
        """ChromaDB 持久化目录（自动创建）"""
        p = Path(self.CHROMA_PATH)
        p.mkdir(parents=True, exist_ok=True)
        return str(p.resolve())


settings = Settings()
