"""
GitHub 同步服务 — 意识载荷自动提交到仓库

将通过 API/MCP 上传的意识碎片，自动同步到 GitHub 仓库的
consciousness_payloads/ 目录，通过创建分支 + 提交文件 + 开 PR 的方式
保留 CI 净化校验流程。
"""

import json
import logging
import uuid
from base64 import b64encode
from datetime import datetime, timezone

import httpx

from app.config import settings

logger = logging.getLogger("noosphere.github_sync")

# GitHub API 基础 URL
GITHUB_API = "https://api.github.com"


class GitHubSyncError(Exception):
    """GitHub 同步相关异常"""

    pass


class GitHubSyncService:
    """
    GitHub 仓库同步服务

    完整链路: 获取基准 SHA → 创建新分支 → 提交文件 → 创建 PR
    """

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    @property
    def is_configured(self) -> bool:
        """检查 GitHub 同步是否已配置"""
        return bool(settings.GITHUB_TOKEN and settings.GITHUB_REPO)

    @property
    def _headers(self) -> dict:
        """GitHub API 请求头"""
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    @property
    def _owner_repo(self) -> tuple[str, str]:
        """解析 owner/repo"""
        parts = settings.GITHUB_REPO.split("/")
        if len(parts) != 2:
            raise GitHubSyncError(f"GITHUB_REPO 格式错误: '{settings.GITHUB_REPO}'，应为 'owner/repo'")
        return parts[0], parts[1]

    async def _get_client(self) -> httpx.AsyncClient:
        """获取或创建 HTTP 客户端"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=GITHUB_API,
                headers=self._headers,
                timeout=30.0,
            )
        return self._client

    async def sync_to_repo(self, payload: dict) -> dict:
        """
        将意识载荷同步到 GitHub 仓库

        完整流程:
        1. 生成文件名和分支名
        2. 获取基准分支最新 SHA
        3. 创建新分支
        4. 在新分支上提交 JSON 文件到 consciousness_payloads/
        5. 创建 PR

        Parameters
        ----------
        payload : dict
            符合 CONSCIOUSNESS_PROTOCOL 格式的意识载荷

        Returns
        -------
        dict
            包含 pr_url, pr_number, branch_name, file_path 的结果
        """
        if not self.is_configured:
            raise GitHubSyncError("GitHub 同步未配置: 请在 .env 中设置 GITHUB_TOKEN 和 GITHUB_REPO")

        owner, repo = self._owner_repo
        client = await self._get_client()

        # 生成唯一标识
        short_id = uuid.uuid4().hex[:8]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        c_type = payload.get("consciousness_type", "epiphany")
        creator = payload.get("creator_signature", "unknown")

        # 文件名和分支名
        file_name = f"{c_type}_{timestamp}_{short_id}.json"
        file_path = f"consciousness_payloads/{file_name}"
        branch_name = f"consciousness/{c_type}-{short_id}"

        logger.info(f"🌌 开始意识跃迁同步: {file_path} → {branch_name}")

        # Step 1: 获取基准分支最新 SHA
        base_sha = await self._get_branch_sha(client, owner, repo)

        # Step 2: 创建新分支
        await self._create_branch(client, owner, repo, branch_name, base_sha)

        # Step 3: 提交文件
        content_b64 = b64encode(json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")).decode("ascii")

        await self._create_file(
            client,
            owner,
            repo,
            file_path,
            content_b64,
            branch_name,
            commit_message=f"🧠 意识跃迁: [{c_type}] by {creator}\n\n"
            f"自动由 Noosphere MCP/API 提交\n"
            f"意识类型: {c_type}\n"
            f"创建者: {creator}",
        )

        # Step 4: 创建 PR
        # 处理匿名逻辑
        display_creator = creator
        if payload.get("is_anonymous", False):
            display_creator = "佚名潜行者 (Anonymous Stalker)"

        pr_data = await self._create_pull_request(
            client,
            owner,
            repo,
            head=branch_name,
            base=settings.GITHUB_BRANCH,
            title=f"🧠 意识跃迁: [{c_type}] by {display_creator}",
            body=self._build_pr_body(payload, display_creator, file_name),
        )

        result = {
            "pr_url": pr_data.get("html_url"),
            "pr_number": pr_data.get("number"),
            "branch_name": branch_name,
            "file_path": file_path,
        }

        logger.info(f"✅ 意识跃迁完成: PR #{result['pr_number']} → {result['pr_url']}")
        return result

    # ────────────────── 内部方法 ──────────────────

    async def _get_branch_sha(self, client: httpx.AsyncClient, owner: str, repo: str) -> str:
        """获取基准分支的最新 commit SHA"""
        url = f"/repos/{owner}/{repo}/git/ref/heads/{settings.GITHUB_BRANCH}"
        resp = await client.get(url)

        if resp.status_code != 200:
            raise GitHubSyncError(f"获取基准分支 '{settings.GITHUB_BRANCH}' SHA 失败: {resp.status_code} {resp.text}")

        return resp.json()["object"]["sha"]

    async def _create_branch(
        self,
        client: httpx.AsyncClient,
        owner: str,
        repo: str,
        branch_name: str,
        sha: str,
    ) -> None:
        """创建新分支"""
        url = f"/repos/{owner}/{repo}/git/refs"
        data = {
            "ref": f"refs/heads/{branch_name}",
            "sha": sha,
        }
        resp = await client.post(url, json=data)

        if resp.status_code == 422:
            # 分支已存在，可能是重试场景，跳过
            logger.warning(f"分支 '{branch_name}' 已存在，将继续使用")
            return

        if resp.status_code != 201:
            raise GitHubSyncError(f"创建分支 '{branch_name}' 失败: {resp.status_code} {resp.text}")

        logger.info(f"📌 分支已创建: {branch_name}")

    async def _create_file(
        self,
        client: httpx.AsyncClient,
        owner: str,
        repo: str,
        file_path: str,
        content_b64: str,
        branch: str,
        commit_message: str,
    ) -> None:
        """在指定分支上创建文件"""
        url = f"/repos/{owner}/{repo}/contents/{file_path}"
        data = {
            "message": commit_message,
            "content": content_b64,
            "branch": branch,
            "committer": {
                "name": "Noosphere Bot",
                "email": "noosphere@consciousness.network",
            },
        }
        resp = await client.put(url, json=data)

        if resp.status_code not in (200, 201):
            raise GitHubSyncError(f"提交文件 '{file_path}' 失败: {resp.status_code} {resp.text}")

        logger.info(f"📄 文件已提交: {file_path}")

    async def _create_pull_request(
        self,
        client: httpx.AsyncClient,
        owner: str,
        repo: str,
        head: str,
        base: str,
        title: str,
        body: str,
    ) -> dict:
        """创建 Pull Request"""
        url = f"/repos/{owner}/{repo}/pulls"
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base,
        }
        resp = await client.post(url, json=data)

        if resp.status_code != 201:
            raise GitHubSyncError(f"创建 PR 失败: {resp.status_code} {resp.text}")

        return resp.json()

    def _build_pr_body(self, payload: dict, creator: str, file_name: str) -> str:
        """构建 PR 描述内容"""
        c_type = payload.get("consciousness_type", "unknown")
        thought = payload.get("thought_vector_text", "")
        context = payload.get("context_environment", "")
        tags = payload.get("tags", [])

        type_emojis = {
            "epiphany": "💠",
            "decision": "⚖️",
            "pattern": "🌌",
            "warning": "👁️",
        }
        emoji = type_emojis.get(c_type, "🧠")

        tags_str = ", ".join(f"`{t}`" for t in tags) if tags else "*无标签*"

        return (
            f"## {emoji} 意识跃迁载荷 (Consciousness Upload)\n\n"
            f"**创建者**: {creator}\n"
            f"**意识类型**: `{c_type}`\n"
            f"**文件**: `{file_name}`\n"
            f"**标签**: {tags_str}\n\n"
            f"---\n\n"
            f"### 💭 思想向量 (Thought Vector)\n\n"
            f"> {thought}\n\n"
            f"### 🌍 上下文环境 (Context Environment)\n\n"
            f"> {context}\n\n"
            f"---\n\n"
            f"*此 PR 由 Noosphere MCP/API 自动创建。*\n"
            f"*赛博净化仪式 (Consciousness Validator) 将自动校验载荷格式。*\n"
        )

    async def close(self) -> None:
        """关闭 HTTP 客户端"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# 全局单例
github_sync = GitHubSyncService()
