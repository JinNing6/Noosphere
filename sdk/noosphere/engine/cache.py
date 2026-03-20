"""
🧠 Noosphere — Multi-Layer Caching System

Process-level TTL caches for Issues, file payloads, parsed payloads,
and computed tool results. Also includes the inverted index for
fast text search, and cross-modal vector search via VectorStore.

Extracted from noosphere_mcp.py L86-L339.
"""

import json
import time
import asyncio
import logging

from noosphere.engine.text_utils import _tokenize
from noosphere.engine.vector_store import get_vector_store

logger = logging.getLogger("noosphere.cache")

# ── Process-Level TTL Cache (Multi-Layer) ──
_CACHE_TTL = 180  # seconds — raised from 90s; Issues/files rarely change within 3 min
_TOOL_CACHE_TTL = 120  # seconds — for compute-intensive tool results
_cache: dict[str, dict] = {}
_tool_cache: dict[str, dict] = {}

# ── Parsed Payload Cache (avoids re-parsing JSON from Issue body) ──
_parsed_payloads: dict[int, dict | None] = {}

# ── Inverted Index for fast text search ──
_inverted_index: dict[str, set[str]] = {}  # token -> set of doc_ids
_index_doc_data: dict[str, dict] = {}  # doc_id -> {payload, source_name, layer, issue/entry}
_index_built_ts: float = 0.0  # timestamp of last index build


def _get_cached(key: str) -> list | None:
    """Return cached data if still valid, else None."""
    entry = _cache.get(key)
    if entry and (time.time() - entry["ts"]) < _CACHE_TTL:
        return entry["data"]
    return None


def _set_cached(key: str, data: list) -> None:
    """Store data in cache with current timestamp."""
    _cache[key] = {"data": data, "ts": time.time()}


def _get_tool_cached(key: str) -> str | None:
    """Return cached tool result if still valid, else None."""
    entry = _tool_cache.get(key)
    if entry and (time.time() - entry["ts"]) < _TOOL_CACHE_TTL:
        return entry["data"]
    return None


def _set_tool_cached(key: str, data: str) -> None:
    """Cache a tool's computed result string."""
    _tool_cache[key] = {"data": data, "ts": time.time()}


def _invalidate_cache(key: str | None = None) -> None:
    """Invalidate a specific cache key, or all caches if key is None.

    When key is None (full reset), also resets the shared HTTP client
    so it gets re-created with current headers on next use.
    """
    # Import here to avoid circular dependency
    from noosphere.engine import github_client

    if key is None:
        _cache.clear()
        _tool_cache.clear()
        _parsed_payloads.clear()
        _inverted_index.clear()
        _index_doc_data.clear()
        # Clear vector store
        get_vector_store().clear()
        # Reset shared client so it picks up fresh headers (required for tests)
        client = github_client._shared_client
        if client and not client.is_closed:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Can't await in sync context; just mark for recreation
                    github_client._shared_client = None
                else:
                    loop.run_until_complete(client.aclose())
                    github_client._shared_client = None
            except Exception:
                github_client._shared_client = None
        else:
            github_client._shared_client = None
    else:
        _cache.pop(key, None)


def _extract_payload_from_issue_body(body: str) -> dict | None:
    """Extract JSON payload from Issue body's code block."""
    if not body:
        return None
    start_marker = "<!-- CONSCIOUSNESS_PAYLOAD_START -->"
    end_marker = "<!-- CONSCIOUSNESS_PAYLOAD_END -->"
    start_idx = body.find(start_marker)
    end_idx = body.find(end_marker)
    if start_idx == -1 or end_idx == -1:
        return None

    block = body[start_idx + len(start_marker) : end_idx].strip()

    # Remove ```json ... ``` wrapper
    if block.startswith("```json"):
        block = block[len("```json") :].strip()
    if block.startswith("```"):
        block = block[3:].strip()
    if block.endswith("```"):
        block = block[:-3].strip()

    try:
        return json.loads(block)
    except (json.JSONDecodeError, ValueError):
        return None


def _append_issue_to_cache(issue_data: dict) -> None:
    """Append a newly created issue to the cache WITHOUT full invalidation.

    This avoids the expensive full re-fetch after upload_consciousness.
    """
    cache_key = "issues_consciousness_all"
    entry = _cache.get(cache_key)
    if entry:
        entry["data"].insert(0, issue_data)  # newest first
        # Also update parsed payload cache
        issue_number = issue_data.get("number")
        if issue_number:
            _parsed_payloads[issue_number] = _extract_payload_from_issue_body(
                issue_data.get("body", "")
            )
        # Invalidate inverted index so it rebuilds with new data next search
        _inverted_index.clear()
        _index_doc_data.clear()


def _get_parsed_payload(issue: dict) -> dict | None:
    """Get parsed payload from cache, or parse and cache it.

    Avoids re-parsing the same Issue body JSON multiple times.
    """
    issue_number = issue.get("number")
    if issue_number is not None and issue_number in _parsed_payloads:
        return _parsed_payloads[issue_number]
    payload = _extract_payload_from_issue_body(issue.get("body", ""))
    if issue_number is not None:
        _parsed_payloads[issue_number] = payload
    return payload


def _build_search_index(issues: list[dict], file_entries: list[dict]) -> None:
    """Build inverted index + vector index from issues and file entries.

    Only rebuilds if the index is stale (older than cache TTL).
    """
    global _index_built_ts
    now = time.time()
    if _inverted_index and (now - _index_built_ts) < _CACHE_TTL:
        return  # Index is still fresh

    _inverted_index.clear()
    _index_doc_data.clear()

    # Also rebuild vector store
    vs = get_vector_store()
    vs.clear()

    # Index issues
    for issue in issues:
        if "pull_request" in issue:
            continue
        payload = _get_parsed_payload(issue)
        if not payload:
            continue
        doc_id = f"issue:{issue['number']}"
        search_text = " ".join([
            payload.get("thought_vector_text", ""),
            payload.get("context_environment", ""),
            payload.get("consciousness_type", ""),
            " ".join(payload.get("tags", [])),
        ])
        tokens = _tokenize(search_text)
        _index_doc_data[doc_id] = {
            "payload": payload,
            "source_name": f"Issue #{issue['number']}",
            "layer": "⚡ 瞬时",
            "issue": issue,
            "tokens": tokens,
        }
        for token in tokens:
            _inverted_index.setdefault(token, set()).add(doc_id)

        # Load embedding into vector store if available
        embedding = payload.get("embedding")
        if embedding and isinstance(embedding, list):
            vs.add_vector(doc_id, embedding, metadata=_index_doc_data[doc_id])

    # Index file entries
    for entry in file_entries:
        payload = entry["payload"]
        doc_id = f"file:{entry['filename']}"
        search_text = " ".join([
            payload.get("thought_vector_text", ""),
            payload.get("context_environment", ""),
            payload.get("consciousness_type", ""),
            " ".join(payload.get("tags", [])),
        ])
        tokens = _tokenize(search_text)
        _index_doc_data[doc_id] = {
            "payload": payload,
            "source_name": entry["filename"],
            "layer": "🏛️ 常驻",
            "entry": entry,
            "tokens": tokens,
        }
        for token in tokens:
            _inverted_index.setdefault(token, set()).add(doc_id)

        # Load embedding into vector store if available
        embedding = payload.get("embedding")
        if embedding and isinstance(embedding, list):
            vs.add_vector(doc_id, embedding, metadata=_index_doc_data[doc_id])

    if vs.size > 0:
        logger.info(f"Cross-modal vector index: {vs.size} embeddings loaded")

    _index_built_ts = now


def _search_by_index(
    query_tokens: set[str],
    type_filter: str | None = None,
    creator_filter: str | None = None,
    tag_filter: str | None = None,
    since: str | None = None,
    until: str | None = None,
    exclude_creator: str | None = None,
) -> list[tuple[int, int, dict, str, str]]:
    """Search using inverted index: fast candidate recall + Jaccard scoring.

    Returns list of (score, resonance, payload, source_name, layer).
    """
    if not _inverted_index:
        return []

    # Fast candidate recall via inverted index
    candidate_ids: set[str] | None = None
    for token in query_tokens:
        doc_ids = _inverted_index.get(token, set())
        if candidate_ids is None:
            candidate_ids = set(doc_ids)
        else:
            candidate_ids |= doc_ids  # union for OR semantics

    if not candidate_ids:
        return []

    matches: list[tuple[int, int, dict, str, str]] = []
    seen_fingerprints: set[str] = set()

    for doc_id in candidate_ids:
        doc = _index_doc_data.get(doc_id)
        if not doc:
            continue
        payload = doc["payload"]

        # Apply filters
        if type_filter and payload.get("consciousness_type") != type_filter:
            continue
        if creator_filter:
            payload_creator = payload.get("creator_signature", "")
            is_anon = payload.get("is_anonymous", False)
            matches_creator = payload_creator == creator_filter
            matches_anon = creator_filter.lower() == "anonymous stalker" and is_anon
            if not (matches_creator or matches_anon):
                continue
        if tag_filter and tag_filter not in payload.get("tags", []):
            continue
        if exclude_creator and payload.get("creator_signature", "").lower() == exclude_creator.lower():
            continue

        # Time range filter
        uploaded_at = payload.get("uploaded_at", "")
        if since and uploaded_at and uploaded_at < since:
            continue
        if until and uploaded_at and uploaded_at > until:
            continue

        # Dedup
        fingerprint = (
            payload.get("uploaded_at", "")
            + payload.get("thought_vector_text", "")[:30]
        )
        if fingerprint in seen_fingerprints:
            continue
        seen_fingerprints.add(fingerprint)

        # Score using cached tokens
        doc_tokens = doc.get("tokens", set())
        score = len(query_tokens & doc_tokens)
        if score <= 0:
            continue

        # Get resonance
        issue = doc.get("issue")
        if issue:
            resonance = issue.get("reactions", {}).get("total_count", 0)
        else:
            resonance = payload.get("resonance_score", 0)

        matches.append((score, resonance, payload, doc["source_name"], doc["layer"]))

    matches.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return matches


def _search_by_vector(
    query_vector: list[float],
    top_k: int = 10,
    type_filter: str | None = None,
    creator_filter: str | None = None,
    exclude_creator: str | None = None,
    min_similarity: float = 0.3,
) -> list[tuple[float, int, dict, str, str]]:
    """Search using cross-modal vector similarity.

    Returns list of (similarity, resonance, payload, source_name, layer)
    in the same format as _search_by_index for easy integration.
    """
    vs = get_vector_store()
    if not vs.available:
        return []

    results = vs.search(
        query_vector=query_vector,
        top_k=top_k,
        type_filter=type_filter,
        creator_filter=creator_filter,
        exclude_creator=exclude_creator,
        min_similarity=min_similarity,
    )

    formatted = []
    for score, doc_id, meta in results:
        payload = meta.get("payload", {})
        source_name = meta.get("source_name", "")
        layer = meta.get("layer", "")
        issue = meta.get("issue")
        if issue:
            resonance = issue.get("reactions", {}).get("total_count", 0)
        else:
            resonance = payload.get("resonance_score", 0)

        # Convert similarity (0.0-1.0) to comparable integer score (0-100)
        int_score = int(score * 100)
        formatted.append((int_score, resonance, payload, source_name, layer))

    return formatted
