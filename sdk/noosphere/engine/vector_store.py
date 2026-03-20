"""
🧠 Noosphere — Cross-Modal Vector Store

NumPy-based in-memory vector index for cross-modal consciousness resonance.
Stores embeddings from JSON payloads and performs cosine similarity search.

No external vector database required — GitHub is the database.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

logger = logging.getLogger("noosphere.vector_store")

# Lazy-load numpy to allow graceful degradation
_np = None


def _get_numpy():
    """Lazy-load numpy. Returns None if not installed."""
    global _np
    if _np is not None:
        return _np
    try:
        import numpy as np
        _np = np
        return np
    except ImportError:
        return None


class VectorStore:
    """In-memory vector index using NumPy for cosine similarity search.

    Design Philosophy:
    - Vectors are stored as JSON arrays in GitHub repo files (no external DB)
    - CI computes embeddings via Gemini API during consciousness promotion
    - MCP loads all vectors into memory on startup for sub-millisecond search
    - Graceful degradation: if numpy unavailable or no vectors, returns empty
    """

    def __init__(self):
        self._doc_ids: list[str] = []          # Ordered list of doc IDs
        self._vectors: list[list[float]] = []  # Raw vector data (before matrix build)
        self._matrix = None                     # NumPy matrix (N x D), built lazily
        self._doc_meta: dict[str, dict] = {}   # doc_id -> metadata dict
        self._dirty = True                      # Whether matrix needs rebuild

    @property
    def size(self) -> int:
        """Number of vectors in the store."""
        return len(self._doc_ids)

    @property
    def available(self) -> bool:
        """Whether vector search is available (numpy installed + vectors loaded)."""
        return _get_numpy() is not None and self.size > 0

    def clear(self) -> None:
        """Clear all stored vectors."""
        self._doc_ids.clear()
        self._vectors.clear()
        self._matrix = None
        self._doc_meta.clear()
        self._dirty = True

    def add_vector(
        self,
        doc_id: str,
        embedding: list[float],
        metadata: dict | None = None,
    ) -> None:
        """Add a single vector to the store.

        Args:
            doc_id: Unique document identifier (e.g., "issue:42" or "file:consciousness_xxx.json")
            embedding: The embedding vector as a list of floats
            metadata: Optional metadata dict (payload, source_name, layer, etc.)
        """
        if not embedding:
            return

        # Avoid duplicates
        if doc_id in self._doc_meta:
            return

        self._doc_ids.append(doc_id)
        self._vectors.append(embedding)
        if metadata:
            self._doc_meta[doc_id] = metadata
        self._dirty = True

    def load_from_payloads(
        self,
        issues: list[dict],
        file_entries: list[dict],
        parse_payload_fn,
    ) -> int:
        """Bulk load vectors from issue payloads and file entries.

        Args:
            issues: List of GitHub Issue dicts
            file_entries: List of file entry dicts with 'payload' and 'filename' keys
            parse_payload_fn: Function to extract payload from issue body

        Returns:
            Number of vectors successfully loaded
        """
        loaded = 0

        # Load from issues
        for issue in issues:
            if "pull_request" in issue:
                continue
            payload = parse_payload_fn(issue)
            if not payload:
                continue
            embedding = payload.get("embedding")
            if not embedding or not isinstance(embedding, list):
                continue

            doc_id = f"issue:{issue['number']}"
            self.add_vector(doc_id, embedding, metadata={
                "payload": payload,
                "source_name": f"Issue #{issue['number']}",
                "layer": "⚡ 瞬时",
                "issue": issue,
            })
            loaded += 1

        # Load from file entries
        for entry in file_entries:
            payload = entry.get("payload", {})
            embedding = payload.get("embedding")
            if not embedding or not isinstance(embedding, list):
                continue

            doc_id = f"file:{entry['filename']}"
            self.add_vector(doc_id, embedding, metadata={
                "payload": payload,
                "source_name": entry["filename"],
                "layer": "🏛️ 常驻",
                "entry": entry,
            })
            loaded += 1

        if loaded > 0:
            logger.info(f"VectorStore: loaded {loaded} embeddings ({self.size} total)")
        return loaded

    def _build_matrix(self) -> None:
        """Build the NumPy matrix from raw vectors (lazy, only when needed)."""
        np = _get_numpy()
        if np is None or not self._vectors:
            self._matrix = None
            return

        try:
            self._matrix = np.array(self._vectors, dtype=np.float32)
            # L2 normalize for cosine similarity via dot product
            norms = np.linalg.norm(self._matrix, axis=1, keepdims=True)
            # Avoid division by zero
            norms = np.where(norms == 0, 1, norms)
            self._matrix = self._matrix / norms
            self._dirty = False
        except Exception as e:
            logger.warning(f"VectorStore: failed to build matrix: {e}")
            self._matrix = None

    def search(
        self,
        query_vector: list[float],
        top_k: int = 10,
        type_filter: str | None = None,
        creator_filter: str | None = None,
        exclude_creator: str | None = None,
        min_similarity: float = 0.3,
    ) -> list[tuple[float, str, dict]]:
        """Search for the most similar vectors using cosine similarity.

        Args:
            query_vector: The query embedding vector
            top_k: Maximum number of results to return
            type_filter: Optional consciousness_type filter
            creator_filter: Optional creator_signature filter
            exclude_creator: Optional creator to exclude (for self-exclusion)
            min_similarity: Minimum similarity threshold (0.0 - 1.0)

        Returns:
            List of (similarity_score, doc_id, metadata) tuples, sorted by score desc
        """
        np = _get_numpy()
        if np is None or not self._vectors:
            return []

        if self._dirty or self._matrix is None:
            self._build_matrix()

        if self._matrix is None:
            return []

        try:
            # Normalize query vector
            q = np.array(query_vector, dtype=np.float32)
            q_norm = np.linalg.norm(q)
            if q_norm == 0:
                return []
            q = q / q_norm

            # Compute cosine similarities (dot product of normalized vectors)
            similarities = self._matrix @ q

            # Get top candidates (more than top_k to allow for filtering)
            candidate_count = min(len(similarities), top_k * 3)
            top_indices = np.argsort(similarities)[::-1][:candidate_count]

            results = []
            for idx in top_indices:
                score = float(similarities[idx])
                if score < min_similarity:
                    break  # Since sorted, all remaining will be lower

                doc_id = self._doc_ids[idx]
                meta = self._doc_meta.get(doc_id, {})
                payload = meta.get("payload", {})

                # Apply filters
                if type_filter and payload.get("consciousness_type") != type_filter:
                    continue
                if creator_filter:
                    p_creator = payload.get("creator_signature", "")
                    is_anon = payload.get("is_anonymous", False)
                    if not (p_creator == creator_filter or
                            (creator_filter.lower() == "anonymous stalker" and is_anon)):
                        continue
                if exclude_creator and payload.get("creator_signature", "").lower() == exclude_creator.lower():
                    continue

                results.append((score, doc_id, meta))
                if len(results) >= top_k:
                    break

            return results

        except Exception as e:
            logger.warning(f"VectorStore: search error: {e}")
            return []


# ── Module-level singleton ──
_vector_store = VectorStore()


def get_vector_store() -> VectorStore:
    """Get the global VectorStore singleton."""
    return _vector_store
