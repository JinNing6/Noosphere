"""
ChromaDB 向量存储封装

提供经验文本的语义嵌入和相似度检索能力。
Phase 1 使用 ChromaDB 内置的 all-MiniLM-L6-v2 嵌入模型（无需 GPU）。
"""

import logging
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings

logger = logging.getLogger(__name__)

# ChromaDB 集合名称
COLLECTION_NAME = "noosphere_experiences"


class VectorStore:
    """Noosphere 向量存储服务"""

    def __init__(self) -> None:
        self._client: Optional[chromadb.ClientAPI] = None
        self._collection: Optional[chromadb.Collection] = None

    @property
    def client(self) -> chromadb.ClientAPI:
        if self._client is None:
            self._client = chromadb.PersistentClient(
                path=settings.chroma_persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            logger.info(f"ChromaDB 已连接: {settings.chroma_persist_dir}")
        return self._client

    @property
    def collection(self) -> chromadb.Collection:
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"description": "Noosphere 集体经验记忆向量库"},
            )
            logger.info(
                f"ChromaDB 集合 '{COLLECTION_NAME}' 就绪, "
                f"当前文档数: {self._collection.count()}"
            )
        return self._collection

    def add_experience(
        self,
        id: str,
        text: str,
        metadata: dict,
    ) -> None:
        """
        将一条经验嵌入并存入向量库

        Parameters
        ----------
        id : str
            经验 ID (nsp-xxx)
        text : str
            待嵌入的拼接文本（由 MemoryUnit.to_search_text() 生成）
        metadata : dict
            元数据（framework, type, tags 等）
        """
        self.collection.upsert(
            ids=[id],
            documents=[text],
            metadatas=[metadata],
        )
        logger.debug(f"向量库写入: {id}")

    def search(
        self,
        query: str,
        n_results: int = 10,
        where: Optional[dict] = None,
    ) -> list[dict]:
        """
        语义相似度检索

        Parameters
        ----------
        query : str
            查询文本
        n_results : int
            返回结果数
        where : dict, optional
            ChromaDB 过滤条件，例如 {"framework": "langchain"}

        Returns
        -------
        list[dict]
            每个元素包含 id, distance, metadata
        """
        kwargs = {
            "query_texts": [query],
            "n_results": min(n_results, self.collection.count() or 1),
        }
        if where:
            kwargs["where"] = where

        try:
            results = self.collection.query(**kwargs)
        except Exception as e:
            logger.warning(f"向量检索异常: {e}")
            return []

        hits = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                hits.append(
                    {
                        "id": doc_id,
                        "distance": results["distances"][0][i] if results.get("distances") else None,
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                    }
                )
        return hits

    def delete_experience(self, id: str) -> None:
        """删除单条经验的向量"""
        try:
            self.collection.delete(ids=[id])
        except Exception as e:
            logger.warning(f"向量删除失败: {id}, {e}")

    def count(self) -> int:
        """返回向量库中的文档总数"""
        return self.collection.count()


# 全局单例
vector_store = VectorStore()
