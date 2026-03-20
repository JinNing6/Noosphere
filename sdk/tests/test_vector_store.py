"""
🧬 Tests for VectorStore — Cross-Modal Vector Search Engine

Tests the NumPy-based in-memory vector store that powers
cross-modal consciousness resonance in Noosphere.
"""

import pytest
import math


class TestVectorStore:
    """Tests for the VectorStore class."""

    def _make_store(self):
        """Create a fresh VectorStore instance."""
        from noosphere.engine.vector_store import VectorStore
        return VectorStore()

    def test_empty_store(self):
        """Empty store should report size 0 and return no results."""
        vs = self._make_store()
        assert vs.size == 0
        results = vs.search([1.0, 0.0, 0.0])
        assert results == []

    def test_add_and_search_exact_match(self):
        """Adding a vector and searching with the same vector should return it."""
        vs = self._make_store()
        vec = [1.0, 0.0, 0.0]
        vs.add_vector("doc:1", vec, metadata={"payload": {"consciousness_type": "epiphany"}})
        assert vs.size == 1

        results = vs.search(vec, top_k=5, min_similarity=0.5)
        assert len(results) == 1
        score, doc_id, meta = results[0]
        assert doc_id == "doc:1"
        assert score > 0.99  # Should be ~1.0 for exact match

    def test_cosine_similarity_ordering(self):
        """Results should be ordered by cosine similarity, highest first."""
        vs = self._make_store()
        # Add three vectors at different angles
        vs.add_vector("close", [0.9, 0.1, 0.0], metadata={"payload": {}})
        vs.add_vector("medium", [0.5, 0.5, 0.0], metadata={"payload": {}})
        vs.add_vector("far", [0.0, 0.0, 1.0], metadata={"payload": {}})

        results = vs.search([1.0, 0.0, 0.0], top_k=10, min_similarity=0.0)
        doc_ids = [doc_id for _, doc_id, _ in results]
        assert doc_ids[0] == "close"
        assert doc_ids[1] == "medium"
        assert doc_ids[2] == "far"

    def test_min_similarity_filter(self):
        """Results below min_similarity should be excluded."""
        vs = self._make_store()
        vs.add_vector("similar", [0.9, 0.1, 0.0], metadata={"payload": {}})
        vs.add_vector("orthogonal", [0.0, 0.0, 1.0], metadata={"payload": {}})

        results = vs.search([1.0, 0.0, 0.0], top_k=10, min_similarity=0.5)
        doc_ids = [doc_id for _, doc_id, _ in results]
        assert "similar" in doc_ids
        assert "orthogonal" not in doc_ids

    def test_type_filter(self):
        """Type filter should only return matching consciousness types."""
        vs = self._make_store()
        vs.add_vector("img1", [1.0, 0.0], metadata={
            "payload": {"consciousness_type": "image"},
        })
        vs.add_vector("txt1", [0.9, 0.1], metadata={
            "payload": {"consciousness_type": "epiphany"},
        })

        # Search for only images
        results = vs.search([1.0, 0.0], type_filter="image", min_similarity=0.0)
        assert len(results) == 1
        assert results[0][1] == "img1"

    def test_creator_filter(self):
        """Creator filter should only return matching creators."""
        vs = self._make_store()
        vs.add_vector("alice_doc", [1.0, 0.0], metadata={
            "payload": {"creator_signature": "alice", "consciousness_type": "epiphany"},
        })
        vs.add_vector("bob_doc", [0.9, 0.1], metadata={
            "payload": {"creator_signature": "bob", "consciousness_type": "epiphany"},
        })

        results = vs.search([1.0, 0.0], creator_filter="alice", min_similarity=0.0)
        assert len(results) == 1
        assert results[0][1] == "alice_doc"

    def test_exclude_creator(self):
        """Exclude creator should filter out the specified creator."""
        vs = self._make_store()
        vs.add_vector("alice_doc", [1.0, 0.0], metadata={
            "payload": {"creator_signature": "alice"},
        })
        vs.add_vector("bob_doc", [0.9, 0.1], metadata={
            "payload": {"creator_signature": "bob"},
        })

        results = vs.search([1.0, 0.0], exclude_creator="alice", min_similarity=0.0)
        assert len(results) == 1
        assert results[0][1] == "bob_doc"

    def test_top_k_limit(self):
        """Should return at most top_k results."""
        vs = self._make_store()
        for i in range(20):
            angle = i * 0.01
            vs.add_vector(f"doc:{i}", [1.0 - angle, angle], metadata={"payload": {}})

        results = vs.search([1.0, 0.0], top_k=5, min_similarity=0.0)
        assert len(results) <= 5

    def test_no_duplicate_ids(self):
        """Adding the same doc_id twice should not create duplicates."""
        vs = self._make_store()
        vs.add_vector("doc:1", [1.0, 0.0], metadata={"payload": {}})
        vs.add_vector("doc:1", [0.0, 1.0], metadata={"payload": {}})
        assert vs.size == 1

    def test_clear(self):
        """Clear should remove all vectors."""
        vs = self._make_store()
        vs.add_vector("doc:1", [1.0, 0.0], metadata={"payload": {}})
        assert vs.size == 1
        vs.clear()
        assert vs.size == 0
        assert vs.search([1.0, 0.0]) == []

    def test_empty_embedding_ignored(self):
        """Empty or None embeddings should be silently ignored."""
        vs = self._make_store()
        vs.add_vector("doc:1", [], metadata={"payload": {}})
        vs.add_vector("doc:2", None, metadata={"payload": {}})
        assert vs.size == 0

    def test_zero_vector_query(self):
        """Zero vector query should return empty results (avoid div by zero)."""
        vs = self._make_store()
        vs.add_vector("doc:1", [1.0, 0.0], metadata={"payload": {}})
        results = vs.search([0.0, 0.0])
        assert results == []

    def test_load_from_payloads(self):
        """load_from_payloads should extract embeddings from issues and files."""
        vs = self._make_store()

        issues = [
            {
                "number": 42,
                "body": '<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{"thought_vector_text": "test", "embedding": [1.0, 0.0, 0.5]}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->',
            },
            {
                "number": 43,
                "body": '<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{"thought_vector_text": "no_vec"}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->',
            },
        ]

        file_entries = [
            {
                "filename": "epiphany_001.json",
                "payload": {
                    "thought_vector_text": "file test",
                    "embedding": [0.0, 1.0, 0.5],
                },
            },
        ]

        def parse_fn(issue):
            body = issue.get("body", "")
            import json
            start = body.find('```json\n') + len('```json\n')
            end = body.find('\n```\n')
            if start > 0 and end > 0:
                return json.loads(body[start:end])
            return None

        loaded = vs.load_from_payloads(issues, file_entries, parse_fn)
        # issue 42 has embedding, issue 43 does not, file entry has embedding
        assert loaded == 2
        assert vs.size == 2

    def test_cross_modal_resonance(self):
        """Core use case: image vector should find similar text vector."""
        vs = self._make_store()

        # Simulate: text about sunset → vector near [0.8, 0.6]
        vs.add_vector("text:sunset_poem", [0.8, 0.6], metadata={
            "payload": {
                "consciousness_type": "epiphany",
                "thought_vector_text": "今人不见古时月",
                "creator_signature": "poet",
            },
        })

        # Simulate: audio of waves → vector near [0.1, 0.9]
        vs.add_vector("audio:waves", [0.1, 0.9], metadata={
            "payload": {
                "consciousness_type": "voice",
                "thought_vector_text": "海浪声",
                "creator_signature": "musician",
            },
        })

        # Simulate: image of sunset → vector near [0.75, 0.65]
        # (should be most similar to sunset poem, not waves)
        query = [0.75, 0.65]
        results = vs.search(query, top_k=5, min_similarity=0.0)

        assert len(results) == 2
        # Sunset poem should be the closest match
        assert results[0][1] == "text:sunset_poem"
        # Waves audio should be further away
        assert results[1][1] == "audio:waves"

        # The score for sunset poem should be significantly higher
        assert results[0][0] > results[1][0]


class TestSearchByVector:
    """Tests for the _search_by_vector cache function."""

    def test_returns_empty_when_no_vectors(self):
        """Should return empty list when vector store has no data."""
        from noosphere.engine.cache import _search_by_vector
        from noosphere.engine.vector_store import get_vector_store

        vs = get_vector_store()
        vs.clear()

        results = _search_by_vector([1.0, 0.0, 0.0])
        assert results == []

    def test_returns_formatted_results(self):
        """Results should be in (score, resonance, payload, name, layer) format."""
        from noosphere.engine.cache import _search_by_vector
        from noosphere.engine.vector_store import get_vector_store

        vs = get_vector_store()
        vs.clear()
        vs.add_vector("test:1", [1.0, 0.0], metadata={
            "payload": {"consciousness_type": "image", "resonance_score": 5},
            "source_name": "Issue #99",
            "layer": "⚡ 瞬时",
        })

        results = _search_by_vector([1.0, 0.0], min_similarity=0.0)
        assert len(results) == 1

        score, resonance, payload, name, layer = results[0]
        assert isinstance(score, int)  # Converted to int (0-100)
        assert score > 50
        assert name == "Issue #99"
        assert layer == "⚡ 瞬时"

        # Cleanup
        vs.clear()
