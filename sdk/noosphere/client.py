"""
Noosphere Python SDK

简洁的 Python 客户端，用于连接 Noosphere 集体记忆网络。

Usage:
    from noosphere import Noosphere

    nsp = Noosphere()
    results = nsp.recall("LangChain RAG Chinese")
    nsp.contribute(type="failure", framework="langchain", ...)
"""

from typing import Optional
import httpx


class Noosphere:
    """Noosphere 集体记忆网络 Python SDK"""

    def __init__(self, base_url: str = "http://localhost:8700"):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=30)

    # ── 检索 ──

    def recall(
        self,
        query: str,
        framework: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """
        从集体记忆中检索相关经验

        Parameters
        ----------
        query : str
            自然语言查询
        framework : str, optional
            过滤特定框架
        limit : int
            返回条数

        Returns
        -------
        list[dict]
            匹配的经验列表
        """
        params = {"q": query, "limit": limit}
        if framework:
            params["framework"] = framework
        resp = self._client.get("/api/v1/recall", params=params)
        resp.raise_for_status()
        return resp.json()["results"]

    # ── 贡献 ──

    def contribute(
        self,
        type: str,
        framework: str,
        observation: str,
        solution: Optional[str] = None,
        root_cause: Optional[str] = None,
        version: Optional[str] = None,
        task_type: Optional[str] = None,
        context: Optional[str] = None,
        evidence: Optional[dict] = None,
        tags: Optional[list[str]] = None,
        contributor: Optional[str] = None,
    ) -> dict:
        """
        贡献一条新经验到 Noosphere

        Parameters
        ----------
        type : str
            经验类型: failure, success, pattern, warning, migration
        framework : str
            AI 框架名称
        observation : str
            观察到的现象
        solution : str, optional
            解决方案
        ...

        Returns
        -------
        dict
            新创建的经验单元
        """
        data = {
            "type": type,
            "framework": framework,
            "observation": observation,
        }
        if solution:
            data["solution"] = solution
        if root_cause:
            data["root_cause"] = root_cause
        if version:
            data["version"] = version
        if task_type:
            data["task_type"] = task_type
        if context:
            data["context"] = context
        if evidence:
            data["evidence"] = evidence
        if tags:
            data["tags"] = tags
        if contributor:
            data["contributor"] = contributor

        resp = self._client.post("/api/v1/contribute", json=data)
        resp.raise_for_status()
        return resp.json()

    # ── 统计 ──

    def stats(self) -> dict:
        """获取 Noosphere 统计概览"""
        resp = self._client.get("/api/v1/stats")
        resp.raise_for_status()
        return resp.json()

    def __del__(self):
        try:
            self._client.close()
        except Exception:
            pass
