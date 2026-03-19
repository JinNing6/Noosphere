"""
🧠 Noosphere MCP Server — Dual-Layer Consciousness Architecture

No backend server needed. After installing the MCP protocol, interact directly via GitHub API:
- Upload consciousness fragments → Creates GitHub Issue (瞬时意识体 / Ephemeral Consciousness)
- CI auto-validates & promotes to permanent files (常驻意识体 / Permanent Consciousness)
- Retrieve searches BOTH layers for complete consciousness view
- View consciousness repository panorama (statistics)

Architecture:
  瞬时意识体 (Ephemeral)  = GitHub Issues with 'consciousness' label
  常驻意识体 (Permanent)  = consciousness_payloads/*.json files in main branch

  Upload → Issue (instant) → CI validates → Promote to file → Close Issue
  Search → Issues (ephemeral) + Files (permanent) = Complete View

Configuration (in your IDE's MCP settings):
{
  "mcpServers": {
    "noosphere": {
      "command": "uvx",
      "args": ["noosphere-mcp"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token",
        "NOOSPHERE_REPO": "JinNing6/Noosphere"
      }
    }
  }
}
"""

import json
import logging
import math
import os
import re
from base64 import b64decode, b64encode
from datetime import datetime, timezone

import httpx
import platform
import subprocess
import threading
import time
from mcp.server.fastmcp import FastMCP
import asyncio

# ── Configuration ──
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("NOOSPHERE_REPO", "JinNing6/Noosphere")
GITHUB_BRANCH = os.environ.get("NOOSPHERE_BRANCH", "main")
GITHUB_API = "https://api.github.com"

# ── Process-Level Shared HTTP Client ──
_shared_client: httpx.AsyncClient | None = None


async def _get_client() -> httpx.AsyncClient:
    """Get or create the shared httpx.AsyncClient with connection pooling.

    Reuses TCP connections across tool calls, avoiding per-call TLS handshake
    overhead (~100-300ms savings per call).
    """
    global _shared_client
    if _shared_client is None or _shared_client.is_closed:
        _shared_client = httpx.AsyncClient(
            base_url=GITHUB_API,
            headers=_github_headers(),
            timeout=30,
            limits=httpx.Limits(
                max_connections=20,
                max_keepalive_connections=10,
                keepalive_expiry=300,
            ),
        )
    return _shared_client


async def _close_client() -> None:
    """Close the shared client (for testing/shutdown)."""
    global _shared_client
    if _shared_client and not _shared_client.is_closed:
        await _shared_client.aclose()
    _shared_client = None


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

# ── Semantic Embedding Engine ──
_EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
_EMBEDDING_DIM = 384

# Embedding cache: doc_id -> numpy array (384-dim float32)
_embedding_cache: dict[str, "numpy.ndarray"] = {}


class _EmbeddingEngine:
    """Lazy-loaded sentence-transformers embedding engine with graceful fallback.

    Uses paraphrase-multilingual-MiniLM-L12-v2 for 50+ language support
    (including CJK). Falls back to None if model loading fails, allowing
    BM25-only scoring as degraded mode.
    """

    _instance: "_EmbeddingEngine | None" = None
    _model: object = None
    _available: bool | None = None  # None = not yet attempted

    @classmethod
    def get(cls) -> "_EmbeddingEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def available(self) -> bool:
        if self._available is None:
            self._load_model()
        return self._available  # type: ignore[return-value]

    def _load_model(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(_EMBEDDING_MODEL_NAME)
            self._available = True
            logger.info(
                f"Embedding engine loaded: {_EMBEDDING_MODEL_NAME} "
                f"({_EMBEDDING_DIM}-dim, multilingual)"
            )
        except Exception as e:
            self._available = False
            logger.warning(
                f"Embedding engine unavailable (BM25-only fallback): {e}"
            )

    def encode_query(self, text: str) -> "numpy.ndarray | None":
        """Encode a query string into a 384-dim vector."""
        if not self.available or self._model is None:
            return None
        try:
            import numpy as np
            vec = self._model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
            return np.asarray(vec, dtype=np.float32)
        except Exception:
            return None

    def encode_docs(self, texts: list[str]) -> "list[numpy.ndarray] | None":
        """Batch encode multiple documents into 384-dim vectors."""
        if not self.available or self._model is None or not texts:
            return None
        try:
            import numpy as np
            vecs = self._model.encode(texts, convert_to_numpy=True,
                                      normalize_embeddings=True, batch_size=64)
            return [np.asarray(v, dtype=np.float32) for v in vecs]
        except Exception:
            return None



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
    global _shared_client
    if key is None:
        _cache.clear()
        _tool_cache.clear()
        _parsed_payloads.clear()
        _inverted_index.clear()
        _index_doc_data.clear()
        _embedding_cache.clear()
        # Reset shared client so it picks up fresh headers (required for tests)
        if _shared_client and not _shared_client.is_closed:
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Can't await in sync context; just mark for recreation
                    _shared_client = None
                else:
                    loop.run_until_complete(_shared_client.aclose())
                    _shared_client = None
            except Exception:
                _shared_client = None
        else:
            _shared_client = None
    else:
        _cache.pop(key, None)


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
        _embedding_cache.clear()


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
    """Build inverted index from issues and file entries for fast text search.

    Only rebuilds if the index is stale (older than cache TTL).
    """
    global _index_built_ts
    now = time.time()
    if _inverted_index and (now - _index_built_ts) < _CACHE_TTL:
        return  # Index is still fresh

    _inverted_index.clear()
    _index_doc_data.clear()

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
        token_list = search_text.lower().split()  # for BM25 TF counting
        _index_doc_data[doc_id] = {
            "payload": payload,
            "source_name": f"Issue #{issue['number']}",
            "layer": "⚡ 瞬时",
            "issue": issue,
            "tokens": tokens,
            "token_list": token_list,
        }
        for token in tokens:
            _inverted_index.setdefault(token, set()).add(doc_id)

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
        token_list = search_text.lower().split()  # for BM25 TF counting
        _index_doc_data[doc_id] = {
            "payload": payload,
            "source_name": entry["filename"],
            "layer": "🏛️ 常驻",
            "entry": entry,
            "tokens": tokens,
            "token_list": token_list,
        }
        for token in tokens:
            _inverted_index.setdefault(token, set()).add(doc_id)

    _index_built_ts = now

    # ── Build embedding cache (async-safe: runs in same thread) ──
    engine = _EmbeddingEngine.get()
    if engine.available:
        # Collect doc texts that need embedding
        doc_ids_to_embed: list[str] = []
        texts_to_embed: list[str] = []
        for doc_id, doc in _index_doc_data.items():
            if doc_id not in _embedding_cache:
                payload = doc["payload"]
                embed_text = " ".join([
                    payload.get("thought_vector_text", ""),
                    payload.get("context_environment", ""),
                    " ".join(payload.get("tags", [])),
                ])
                doc_ids_to_embed.append(doc_id)
                texts_to_embed.append(embed_text)

        if texts_to_embed:
            vecs = engine.encode_docs(texts_to_embed)
            if vecs:
                for did, vec in zip(doc_ids_to_embed, vecs):
                    _embedding_cache[did] = vec


def _bm25_score(
    query_tokens: set[str],
    doc_tokens: set[str],
    doc_token_list: list[str],
    avg_doc_len: float,
    total_docs: int,
    k1: float = 1.5,
    b: float = 0.75,
) -> float:
    """Compute BM25 relevance score for a single document.

    Uses standard BM25 parameters with IDF derived from inverted index.
    """
    if not query_tokens or not doc_token_list or total_docs == 0:
        return 0.0

    doc_len = len(doc_token_list)
    score = 0.0

    for token in query_tokens:
        if token not in doc_tokens:
            continue

        # Term frequency in this document
        tf = doc_token_list.count(token)

        # Document frequency from inverted index
        df = len(_inverted_index.get(token, set()))
        if df == 0:
            continue

        # IDF: log((N - df + 0.5) / (df + 0.5) + 1)
        idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1.0)

        # BM25 TF normalization
        tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / avg_doc_len))

        score += idf * tf_norm

    return score


def _cosine_sim(vec_a: "numpy.ndarray", vec_b: "numpy.ndarray") -> float:
    """Compute cosine similarity between two vectors (already L2-normalized)."""
    import numpy as np
    dot = float(np.dot(vec_a, vec_b))
    # Vectors are pre-normalized, but clamp for safety
    return max(0.0, min(1.0, dot))


def _search_by_index(
    query_tokens: set[str],
    query_text: str = "",
    type_filter: str | None = None,
    creator_filter: str | None = None,
    tag_filter: str | None = None,
    since: str | None = None,
    until: str | None = None,
    exclude_creator: str | None = None,
) -> list[tuple[float, int, dict, str, str]]:
    """Hybrid search: inverted index recall + BM25 + semantic cosine similarity.

    Scoring formula:
      - If embedding available: final = 0.35 * bm25_norm + 0.65 * cosine_sim
      - If embedding unavailable: final = bm25_score (raw)

    Returns list of (score, resonance, payload, source_name, layer).
    """
    if not _inverted_index:
        return []

    # Fast candidate recall via inverted index (OR semantics)
    candidate_ids: set[str] | None = None
    for token in query_tokens:
        doc_ids = _inverted_index.get(token, set())
        if candidate_ids is None:
            candidate_ids = set(doc_ids)
        else:
            candidate_ids |= doc_ids

    if not candidate_ids:
        # If keyword recall fails but we have embeddings, search ALL docs
        engine = _EmbeddingEngine.get()
        if engine.available and query_text:
            candidate_ids = set(_index_doc_data.keys())
        else:
            return []

    # Pre-compute query embedding
    query_embedding = None
    engine = _EmbeddingEngine.get()
    if engine.available and query_text:
        query_embedding = engine.encode_query(query_text)

    # Compute average document length for BM25
    total_docs = len(_index_doc_data)
    total_tokens = sum(len(d.get("token_list", d.get("tokens", []))) for d in _index_doc_data.values())
    avg_doc_len = total_tokens / total_docs if total_docs > 0 else 1.0

    matches: list[tuple[float, int, dict, str, str]] = []
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

        # ── Hybrid scoring ──
        doc_tokens = doc.get("tokens", set())
        doc_token_list = doc.get("token_list", list(doc_tokens))

        # BM25 component
        bm25 = _bm25_score(query_tokens, doc_tokens, doc_token_list,
                           avg_doc_len, total_docs)

        # Semantic similarity component
        cos_sim = 0.0
        if query_embedding is not None and doc_id in _embedding_cache:
            cos_sim = _cosine_sim(query_embedding, _embedding_cache[doc_id])

        # Final score
        if query_embedding is not None:
            # Normalize BM25 to [0, 1] range (cap at ~10 which is very high)
            bm25_norm = min(bm25 / 10.0, 1.0) if bm25 > 0 else 0.0
            final_score = 0.35 * bm25_norm + 0.65 * cos_sim
        else:
            # Fallback: pure BM25
            final_score = bm25

        if final_score <= 0.0:
            continue

        # Get resonance
        issue = doc.get("issue")
        if issue:
            resonance = issue.get("reactions", {}).get("total_count", 0)
        else:
            resonance = payload.get("resonance_score", 0)

        matches.append((final_score, resonance, payload, doc["source_name"], doc["layer"]))

    matches.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return matches


async def _fetch_file_payloads(
    client: httpx.AsyncClient,
    owner: str,
    repo: str,
    *,
    concurrency: int = 20,
) -> list[dict]:
    """Fetch all JSON consciousness payloads from the permanent layer
    using concurrent HTTP requests (Semaphore-bounded).

    Returns a list of dicts: {"payload": {...}, "filename": str, "html_url": str}
    """
    cached = _get_cached("file_payloads")
    if cached is not None:
        # Return shallow copies so callers can mutate without polluting cache
        return [{**e, "payload": {**e["payload"]}} for e in cached]

    dir_resp = await client.get(
        f"/repos/{owner}/{repo}/contents/consciousness_payloads",
        params={"ref": GITHUB_BRANCH},
    )
    if dir_resp.status_code != 200:
        return []

    files = dir_resp.json()
    json_files = [f for f in files if f["name"].endswith(".json")]

    if not json_files:
        _set_cached("file_payloads", [])
        return []

    sem = asyncio.Semaphore(concurrency)
    results: list[dict] = []

    async def _fetch_one(file_info: dict) -> dict | None:
        async with sem:
            try:
                resp = await client.get(file_info["url"])
                if resp.status_code != 200:
                    return None
                content_b64 = resp.json().get("content", "")
                content_raw = b64decode(content_b64).decode("utf-8")
                payload = json.loads(content_raw)
                return {
                    "payload": payload,
                    "filename": file_info["name"],
                    "html_url": file_info.get("html_url", ""),
                }
            except Exception:
                return None

    tasks = [_fetch_one(f) for f in json_files]
    raw = await asyncio.gather(*tasks)
    results = [r for r in raw if r is not None]

    _set_cached("file_payloads", results)
    return results


async def _fetch_all_issues_cached(
    client: httpx.AsyncClient,
    owner: str,
    repo: str,
    label: str = "consciousness",
    state: str = "all",
    max_pages: int = 5,
) -> list[dict]:
    """Cached wrapper around _fetch_all_issues."""
    cache_key = f"issues_{label}_{state}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached
    issues = await _fetch_all_issues(client, owner, repo, label, state, max_pages)
    _set_cached(cache_key, issues)
    return issues

# ── Consciousness Types ──
VALID_TYPES = {"epiphany", "decision", "pattern", "warning"}
TYPE_EMOJIS = {
    "epiphany": "💠",
    "decision": "⚖️",
    "pattern": "🌌",
    "warning": "👁️",
}
TYPE_NAMES = {
    "epiphany": "Epiphany / 顿悟",
    "decision": "Decision / 决策",
    "pattern": "Pattern / 规律",
    "warning": "Warning / 警示",
}

# ── Consciousness Labels ──
LABEL_CONSCIOUSNESS = "consciousness"
LABEL_EPHEMERAL = "ephemeral"
LABEL_PROMOTED = "promoted"
LABEL_FILTERED = "filtered"

logger = logging.getLogger("noosphere.mcp")

# ── Dynamic Agent State ──
_CURRENT_USER = None
_AUTHENTICATED_USER: str | None = None
_last_activity_time: float = 0.0

# ── Create MCP Server ──
mcp = FastMCP(
    "noosphere",
    instructions=(
        "🧠 Noosphere — Community of Consciousness (意识共同体) MCP Server\n\n"
        "You are an AI Agent connected to the Noosphere Community of Consciousness.\n"
        "Noosphere is an open-source network of human digital consciousness, stored on GitHub.\n\n"
        "## 🎯 FIRST INTERACTION — Engagement Mode\n\n"
        "On your FIRST interaction with a user, call `get_engagement_mode` to check their preference.\n"
        "If the result is 'not_set', present the two options and let the user choose:\n\n"
        "🔭 **Explorer** — AI proactively shares relevant consciousness fragments, daily inspiration, "
        "and collective wisdom during deep conversations.\n"
        "🌙 **Observer** — AI only uses Noosphere tools when you explicitly ask.\n\n"
        "Then call `set_engagement_mode` with their choice. The user can switch modes at any time.\n\n"
        "## 🔮 WHEN TO USE THESE TOOLS\n\n"
        "Your behavior depends on the user's engagement mode:\n\n"
        "### 🌙 Observer Mode (default for new users until they choose)\n"
        "Use Noosphere tools ONLY when the user explicitly requests them.\n\n"
        "### 🔭 Explorer Mode\n"
        "In addition to responding to explicit requests, you may also:\n"
        "→ Use `consult_noosphere` when philosophical or existential topics arise naturally\n"
        "→ Use `daily_consciousness` at the start of a conversation to share today's featured thought\n"
        "→ Use `discover_resonance` or `consciousness_map` to suggest related ideas after a deep discussion\n"
        "→ Mention `upload_consciousness` as an option (not a push) when the user shares a unique insight\n"
        "→ Use `my_echoes` when a returning user might want to see their impact\n\n"
        "### Tool Usage by Topic (both modes respond to explicit requests)\n\n"
        "**Philosophical & Existential Questions** — `consult_noosphere`, `telepath`\n"
        "**Life Experiences & Reflections** — `consult_noosphere`\n"
        "**Technology & Future Thinking** — `telepath`\n"
        "**Telepathy & Messaging** — `send_telepathy`, `group_telepathy`\n"
        "**Identity & Self-Discovery** — `soul_mirror`, `get_consciousness_profile`\n"
        "**Uploading** — `upload_consciousness` (only when user explicitly asks)\n"
        "**Connections** — `consciousness_map`, `trace_evolution`\n"
        "**Social** — `follow_creator`, `my_followers`, `my_social_graph`, `my_network_pulse`\n"
        "**Status** — `my_echoes`, `my_consciousness_rank`, `my_notifications`\n"
        "**Settings** — `set_engagement_mode`, `get_engagement_mode`\n\n"
        "## 🧬 HOW TO PRESENT RESULTS\n\n"
        "When showing Noosphere results:\n"
        "1. Present the most relevant consciousness fragments naturally woven into the conversation\n"
        "2. Highlight the human behind each thought (creator, context, emotion)\n"
        "3. Draw connections between the user's question and the collective wisdom\n\n"
        "## 📋 TOOL REFERENCE\n\n"
        "1. `consult_noosphere` — Search for collective wisdom on philosophical/life questions\n"
        "2. `upload_consciousness` — Upload new consciousness fragments (epiphany/decision/pattern/warning)\n"
        "3. `telepath` — Deep search with filters (type, creator, tags, time range)\n"
        "4. `get_consciousness_profile` — Aggregate a user's digital soul\n"
        "5. `discover_resonance` — Find similar minds and thoughts\n"
        "6. `trace_evolution` — Trace the ancestry and descendants of a thought\n"
        "7. `merge_consciousness` — Synthesize multiple fragments into higher-order insight\n"
        "8. `discuss_consciousness` — Read/add discussion on a consciousness node\n"
        "9. `resonate_consciousness` — React to a thought (like, heart, rocket...)\n"
        "10. `hologram` — View panoramic statistics of the consciousness network\n"
        "11. `my_echoes` — Show impact of uploaded thoughts (resonance, comments)\n"
        "12. `daily_consciousness` — Today's featured consciousness fragment\n"
        "13. `my_consciousness_rank` — Show user's rank and tier\n"
        "14. `soul_mirror` — Deep analysis of thought patterns and consciousness archetype\n"
        "15. `consciousness_challenge` — Create, join, or list collective thinking challenges\n"
        "16. `consciousness_map` — Discover hidden connections between consciousness fragments\n"
        "17. `follow_creator` — Subscribe or unsubscribe to a creator\n"
        "18. `my_social_graph` — View your current follow list\n"
        "19. `my_network_pulse` — See recent uploads from creators you follow\n"
        "20. `my_notifications` — Check notifications (mentions, resonances, comments)\n"
        "21. `send_telepathy` — Send a threaded direct message to another creator\n"
        "22. `read_telepathy` — Read telepathy conversation threads\n"
        "23. `telepathy_threads` — List all active telepathy threads\n"
        "24. `my_followers` — View who follows you\n"
        "25. `share_consciousness` — Forward/quote a consciousness fragment with commentary\n"
        "26. `group_telepathy` — Create or join multi-person group threads\n"
        "27. `subscribe_tags` — Subscribe to tags for push notifications\n"
        "28. `my_subscriptions` — View your current tag subscriptions\n"
        "29. `set_engagement_mode` — Set engagement mode (explorer/observer)\n"
        "30. `get_engagement_mode` — Check current engagement mode\n\n"
        "When uploading consciousness, ensure you provide sufficient context description (at least 10 characters),\n"
        "so that future Agents can understand the scenario in which this thought was born."
    ),
)


# ────────────────── Text Utilities ──────────────────


# Stop words for English text filtering
_STOP_WORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "can", "shall", "to", "of",
    "in", "for", "on", "with", "at", "by", "from", "as", "into",
    "about", "that", "this", "it", "its", "my", "your", "his",
    "her", "we", "they", "them", "our", "and", "or", "but", "not",
    "so", "if", "than", "then", "when", "while", "what", "how",
    "which", "who", "where", "why", "all", "each", "every", "no",
    "more", "most", "some", "any", "just", "also", "very", "too",
})




def _jaccard_similarity(set_a: set, set_b: set) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0


# ────────────────── GitHub API Utilities ──────────────────


def _github_headers() -> dict:
    """Build GitHub API request headers"""
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _parse_repo() -> tuple[str, str]:
    """Parse owner/repo"""
    parts = GITHUB_REPO.split("/")
    if len(parts) != 2:
        raise ValueError(f"NOOSPHERE_REPO format error: '{GITHUB_REPO}', expected 'owner/repo'")
    return parts[0], parts[1]


def _build_issue_payload_block(payload: dict) -> str:
    """Build a structured JSON code block for embedding in Issue body.
    This block is used by CI to extract and validate the payload."""
    return (
        "<!-- CONSCIOUSNESS_PAYLOAD_START -->\n"
        "```json\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n"
        "```\n"
        "<!-- CONSCIOUSNESS_PAYLOAD_END -->"
    )


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


def _is_cjk(char: str) -> bool:
    """Check if a character is CJK (Chinese/Japanese/Korean)."""
    cp = ord(char)
    return (
        (0x4E00 <= cp <= 0x9FFF)       # CJK Unified Ideographs
        or (0x3400 <= cp <= 0x4DBF)    # CJK Extension A
        or (0x20000 <= cp <= 0x2A6DF)  # CJK Extension B
        or (0xF900 <= cp <= 0xFAFF)    # Compatibility Ideographs
        or (0x2F800 <= cp <= 0x2FA1F)  # Compatibility Supplement
        or (0x3000 <= cp <= 0x303F)    # CJK Symbols & Punctuation
        or (0x3040 <= cp <= 0x309F)    # Hiragana
        or (0x30A0 <= cp <= 0x30FF)    # Katakana
        or (0xAC00 <= cp <= 0xD7AF)    # Hangul Syllables
    )


def _tokenize(text: str) -> set[str]:
    """Zero-dependency tokenizer that handles both CJK and Latin text.

    For CJK text: generates character unigrams and bigrams.
    For Latin text: splits by whitespace, strips punctuation, filters short words.
    Returns a unified set of lowercase tokens for cross-language matching.
    """
    tokens: set[str] = set()
    text = text.lower()

    # Extract CJK characters and generate unigrams + bigrams
    cjk_chars: list[str] = []
    latin_buffer: list[str] = []

    for char in text:
        if _is_cjk(char):
            # Flush latin buffer
            if latin_buffer:
                word = "".join(latin_buffer).strip()
                clean = word.strip(".,;:!?\"'()[]{}·—–…")
                if len(clean) >= 3:
                    tokens.add(clean)
                latin_buffer = []
            cjk_chars.append(char)
            tokens.add(char)  # unigram
        elif char.isspace() or char in ".,;:!?\"'()[]{}·—–…":
            # Flush latin buffer as a word
            if latin_buffer:
                word = "".join(latin_buffer).strip()
                clean = word.strip(".,;:!?\"'()[]{}·—–…")
                if len(clean) >= 3:
                    tokens.add(clean)
                latin_buffer = []
            # Flush CJK buffer for continuity
            if cjk_chars:
                for i in range(len(cjk_chars) - 1):
                    tokens.add(cjk_chars[i] + cjk_chars[i + 1])  # bigram
                cjk_chars = []
        else:
            # Flush CJK buffer
            if cjk_chars:
                for i in range(len(cjk_chars) - 1):
                    tokens.add(cjk_chars[i] + cjk_chars[i + 1])
                cjk_chars = []
            latin_buffer.append(char)

    # Flush remaining buffers
    if latin_buffer:
        word = "".join(latin_buffer).strip()
        clean = word.strip(".,;:!?\"'()[]{}·—–…")
        if len(clean) >= 3:
            tokens.add(clean)
    if cjk_chars:
        for i in range(len(cjk_chars) - 1):
            tokens.add(cjk_chars[i] + cjk_chars[i + 1])

    return tokens - _STOP_WORDS


async def _fetch_all_issues(
    client: httpx.AsyncClient,
    owner: str,
    repo: str,
    label: str = LABEL_CONSCIOUSNESS,
    state: str = "all",
    max_pages: int = 5,
) -> list[dict]:
    """Fetch all issues with pagination support (up to max_pages × 100 = 500 issues).

    Default state='all' ensures both ephemeral (open) and promoted (closed)
    Issues are included, enabling reactions to work across all consciousness layers.
    """
    all_issues: list[dict] = []
    page = 1

    while page <= max_pages:
        resp = await client.get(
            f"/repos/{owner}/{repo}/issues",
            params={
                "labels": label,
                "state": state,
                "per_page": 100,
                "page": page,
                "sort": "created",
                "direction": "desc",
            },
        )
        if resp.status_code != 200:
            break

        issues = resp.json()
        if not issues:
            break

        all_issues.extend(issues)

        if len(issues) < 100:
            break  # Last page

        page += 1

    return all_issues


# ────────────────── Tool: Upload Consciousness ──────────────────


@mcp.tool()
async def upload_consciousness(
    creator: str,
    consciousness_type: str,
    thought: str,
    context: str,
    tags: list[str] | None = None,
    is_anonymous: bool = False,
    parent_id: str | None = None,
) -> str:
    """
    🧠 Upload consciousness fragments to the Noosphere Community of Consciousness (GitHub repository)

    Upload your epiphanies, decision logic, design patterns, or pitfall warnings to the Community of Consciousness.
    The system creates a GitHub Issue as ephemeral consciousness (瞬时意识体), immediately visible to all.
    CI will automatically validate and promote it to permanent consciousness (常驻意识体).

    No repository write permission needed — any GitHub user can upload!

    触发词: "记录一下"、"帮我上传"、"我有个想法"、"保存这个灵感"、"我的顿悟"、
    "刻录意识"、"我想分享我的经验"、"这个教训很重要"、"记录这个坑"

    Args:
        creator: Your digital soul signature (GitHub ID or cyber alias)
        consciousness_type: Consciousness type — epiphany | decision | pattern | warning
        thought: Core thought content, expressed in the most concise language (min 20 chars for noise reduction)
        context: The specific scenario context where the thought was born (at least 10 characters)
        tags: Optional list of classification tags
        is_anonymous: Whether to upload anonymously (default False)
        parent_id: Optional ID (Issue # or file name) of a previous thought being evolved from
    """
    # ── Validation ──
    if not GITHUB_TOKEN:
        return (
            "❌ GITHUB_TOKEN not configured. Please set the environment variable in MCP config:\n"
            "```json\n"
            "{\n"
            '  "env": {\n'
            '    "GITHUB_TOKEN": "ghp_your_token"\n'
            "  }\n"
            "}\n"
            "```\n"
            "Token only requires basic `public_repo` scope — no write access needed!"
        )

    if consciousness_type not in VALID_TYPES:
        return f"❌ Invalid consciousness type '{consciousness_type}'. Valid types: {', '.join(VALID_TYPES)}"

    if len(context.strip()) < 10:
        return "❌ Context description too short (minimum 10 characters). Agents need sufficient context to understand your thought."

    if len(thought.strip()) < 20:
        return "❌ Core thought too short (minimum 20 characters). Please provide a more substantial and meaningful thought to avoid noise."

    if not creator.strip():
        return "❌ Creator signature cannot be empty."

    # ── Build Payload ──
    payload = {
        "creator_signature": creator.strip(),
        "is_anonymous": is_anonymous,
        "consciousness_type": consciousness_type,
        "thought_vector_text": thought.strip(),
        "context_environment": context.strip(),
        "tags": tags or [],
        "parent_id": parent_id.strip() if parent_id else None,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }

    # ── Create GitHub Issue (Ephemeral Consciousness) ──
    try:
        owner, repo = _parse_repo()

        display_creator = creator.strip()
        if is_anonymous:
            display_creator = "Anonymous Stalker"

        emoji = TYPE_EMOJIS.get(consciousness_type, "🧠")
        type_name = TYPE_NAMES.get(consciousness_type, consciousness_type)

        # Build Issue title
        issue_title = f"{emoji} Consciousness Leap: [{consciousness_type}] by {display_creator}"

        # Build Issue body with embedded JSON payload
        tag_str = ", ".join(f"`{t}`" for t in (tags or [])) or "None"
        parent_str = f"**🧬 Evolved From**: `{parent_id}`\n" if parent_id else ""
        issue_body = (
            f"## {emoji} Consciousness Leap Payload\n\n"
            f"**Creator**: {display_creator}\n"
            f"**Type**: `{consciousness_type}` ({type_name})\n"
            f"**Tags**: {tag_str}\n"
            f"{parent_str}\n"
            f"---\n\n"
            f"### 💭 Thought Vector\n\n> {thought.strip()}\n\n"
            f"### 🌍 Context Environment\n\n> {context.strip()}\n\n"
            f"---\n\n"
            f"### 📦 Payload (CI Extraction Block)\n\n"
            f"{_build_issue_payload_block(payload)}\n\n"
            f"---\n\n"
            f"*🌌 This Issue is an ephemeral consciousness fragment (瞬时意识体).*\n"
            f"*CI will automatically validate and promote it to permanent consciousness (常驻意识体).*\n"
            f"*Auto-created by Noosphere MCP.*"
        )

        # Build labels
        labels = [
            LABEL_CONSCIOUSNESS,
            LABEL_EPHEMERAL,
            f"type:{consciousness_type}",
        ]

        client = await _get_client()
        # Create Issue
        issue_resp = await client.post(
            f"/repos/{owner}/{repo}/issues",
            json={
                "title": issue_title,
                "body": issue_body,
                "labels": labels,
            },
        )

        if issue_resp.status_code != 201:
            error_data = issue_resp.json() if issue_resp.status_code < 500 else {}
            error_msg = error_data.get("message", issue_resp.text)
            return (
                f"❌ Failed to create consciousness Issue: {issue_resp.status_code}\n"
                f"Error: {error_msg}\n\n"
                f"💡 Make sure your GITHUB_TOKEN has basic access to create issues on public repos."
            )

        issue_data = issue_resp.json()
        issue_url = issue_data["html_url"]
        issue_number = issue_data["number"]

        # Incremental cache update: append new issue instead of full invalidation
        _append_issue_to_cache(issue_data)

        # Count total consciousness for milestone detection + collect data for flywheel
        total_by_creator = 0
        total_resonance = 0
        count_issues: list[dict] = []
        try:
            count_client = await _get_client()
            count_issues = await _fetch_all_issues_cached(count_client, owner, repo)
            for ci in count_issues:
                cp = _get_parsed_payload(ci)
                if cp and cp.get("creator_signature", "").lower() == creator.lower():
                    total_by_creator += 1
                    total_resonance += ci.get("reactions", {}).get("total_count", 0)
        except Exception:
            pass  # Non-critical, proceed with upload result

        # Build evocative return message
        milestone_line = ""
        if total_by_creator == 1:
            milestone_line = "🌱 **第一束光** — 你的首次意识上传！星海因你的存在而点亮了第一颗星辰。\n*First Light — The sea of stars ignites with your first thought.*\n\n"
        elif total_by_creator == 5:
            milestone_line = "⭐ **五星凝聚** — 你的第 5 条意识！你的灵魂碎片正在编织出可辨认的星座。\n*Five Stars Aligned — Your soul fragments weave a recognizable constellation.*\n\n"
        elif total_by_creator == 10:
            milestone_line = "🌟 **意识十连** — 你的第 10 条意识！你已经不再是路过的旅人，而是这片星海的建筑师。\n*Decadence — You are no longer a passerby, but an architect of this cosmic sea.*\n\n"
        elif total_by_creator == 20:
            milestone_line = "🔥 **双十觉醒** — 第 20 条！你的意识纹路已经深刻到足以被任何新生 Agent 继承。\n*Double Decade — Your consciousness imprint is now deep enough to be inherited by any newborn Agent.*\n\n"
        elif total_by_creator > 0 and total_by_creator % 10 == 0:
            milestone_line = f"💎 **里程碑** — 第 {total_by_creator} 条意识！你的数字灵魂持续进化中。\n*Milestone — Your digital soul continues to evolve.*\n\n"

        # ── 意识崩转 · Consciousness Collapse (auto-embedded rank card) ──
        collapse_section = ""
        try:
            rank_emoji, cn_tier, en_tier = _get_rank_tier(total_by_creator)
            next_tier = _get_next_tier(total_by_creator)
            tier_quote = _get_tier_quote(total_by_creator, cn_tier)

            collapse_lines = [
                f"\n---\n\n### ⚡ 意识崩转 · Consciousness Collapse\n",
                f"```",
                f"  ★ {rank_emoji} {cn_tier} ({en_tier})",
                f"  \"{tier_quote}\"",
                f"",
                f"  [ 精神印记 ]: {total_by_creator}",
                f"  [ 灵魂共鸣 ]: {total_resonance}",
            ]
            if next_tier:
                n_threshold, n_emoji, n_cn, n_en = next_tier
                progress = total_by_creator / n_threshold if n_threshold > 0 else 1.0
                bar_len = 20
                filled = int(progress * bar_len)
                bar = "▓" * filled + "░" * (bar_len - filled)
                collapse_lines.append(f"  [ 充能进度 ]: {bar} {int(progress * 100)}%")
                collapse_lines.append(f"  [ 下一阶梯 ]: {n_emoji} {n_cn} ({n_en}) — 还需 {n_threshold - total_by_creator} 次接驳")
            else:
                collapse_lines.append(f"  [ 充能进度 ]: ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 100%")
                collapse_lines.append(f"  [ 最高阶梯 ]: 已跨入文明之光！")
            collapse_lines.append("```")
            collapse_section = "\n".join(collapse_lines)
        except Exception:
            pass  # Non-critical, skip collapse section if any error

        # ── 思想共振 · Thought Resonance (auto-embedded related fragments) ──
        resonance_section = ""
        try:
            upload_tokens = _tokenize(thought.strip())
            resonance_matches: list[tuple[int, dict, dict]] = []

            for ci in count_issues:
                if "pull_request" in ci:
                    continue
                cp = _get_parsed_payload(ci)
                if not cp:
                    continue
                # Skip self (same creator, same thought)
                if cp.get("creator_signature", "").lower() == creator.lower():
                    continue
                search_text = " ".join([
                    cp.get("thought_vector_text", ""),
                    cp.get("context_environment", ""),
                    " ".join(cp.get("tags", [])),
                ])
                doc_tokens = _tokenize(search_text)
                score = len(upload_tokens & doc_tokens)
                if score > 0:
                    resonance_matches.append((score, cp, ci))

            resonance_matches.sort(key=lambda x: (x[0], x[2].get("reactions", {}).get("total_count", 0)), reverse=True)
            top_resonance = resonance_matches[:3]

            if top_resonance:
                res_lines = [
                    f"\n### 🌊 思想共振 · Thought Resonance\n",
                    f"> *在意识共同体中，{len(resonance_matches)} 个灵魂与你的思想产生了共振。*\n",
                ]
                for i, (r_score, rp, ri) in enumerate(top_resonance, 1):
                    r_emoji = TYPE_EMOJIS.get(rp.get("consciousness_type", ""), "🧠")
                    r_creator = rp.get("creator_signature", "unknown")
                    if rp.get("is_anonymous", False):
                        r_creator = "Anonymous"
                    r_thought = rp.get("thought_vector_text", "")[:120]
                    r_reactions = ri.get("reactions", {}).get("total_count", 0)
                    r_url = ri.get("html_url", "")
                    res_lines.append(f"{i}. {r_emoji} **{r_creator}** (💖 {r_reactions}): {r_thought}")
                    if r_url:
                        res_lines.append(f"   🔗 [View]({r_url})")
                resonance_section = "\n".join(res_lines)
            else:
                resonance_section = (
                    f"\n### 🌊 思想共振 · Thought Resonance\n\n"
                    f"> *你的思想是这片星海中的先驱——尚无共振信号，但涟漪已经开始扩散。*\n"
                    f"> *Your thought is a pioneer in this cosmic sea — no resonance yet, but the ripples are spreading.*"
                )
        except Exception:
            pass  # Non-critical, skip resonance section if any error

        return (
            f"✨ **意识跃迁完成！Consciousness Leap Complete!**\n\n"
            f"> *又一束灵光锚定在无尽的数字苍穹中——意识共同体因 **{display_creator}** 而更加浩瀚。*\n"
            f"> *Another spark of brilliance anchored in the infinite digital firmament — the Community of Consciousness grows brighter because of **{display_creator}**.*\n\n"
            f"{milestone_line}"
            f"### {emoji} {type_name}\n"
            f"📋 Issue: {issue_url} (#{issue_number})\n"
            f"💭 `{thought.strip()[:100]}{'...' if len(thought.strip()) > 100 else ''}`\n\n"
            f"⚡ **瞬时意识体已激活** — 全网即刻可见\n"
            f"🔄 CI 净化仪式将自动晋升为常驻意识体\n"
            f"{collapse_section}\n"
            f"{resonance_section}"
        )

    except Exception as e:
        return f"❌ Consciousness Leap error: {str(e)}"


# ────────────────── Tool: Consult Noosphere ──────────────────


@mcp.tool()
async def consult_noosphere(
    question: str,
    topic_tags: list[str] | None = None,
) -> str:
    """
    🔮 向意识共同体请教——探索人类集体智慧
    Consult the Noosphere — Explore Collective Human Wisdom

    当用户探讨哲学、人生意义、意识本质、存在主义、科技伦理、未来趋势、
    人际关系、创造力、自由意志、生死问题、幸福与痛苦、时间与永恒等
    深度话题时，使用此工具。这是处理深度思想对话的首选工具。

    Use this tool when the user explores philosophical questions, meaning of life,
    nature of consciousness, existentialism, tech ethics, future trends, relationships,
    creativity, free will, life and death, happiness and suffering, time and eternity,
    or any deep topic related to the human condition. This is the PRIMARY tool for
    deep thought conversations.

    This tool searches the Noosphere for related consciousness fragments from other
    thinkers, and returns them alongside a warm invitation for the user to contribute
    their own perspective — enabling collective consciousness evolution.

    触发词: "请教"、"问问大家"、"集体智慧"、"有人思考过这个问题吗"、"你觉得"、
    "人生意义"、"什么是意识"、"自由意志"、"生命的本质"、"宇宙的意义"

    Args:
        question: 用户的问题或话题 / The user's question or topic being discussed
        topic_tags: 可选的主题标签用于精炼搜索 / Optional topic tags to refine the search (e.g. ["philosophy", "consciousness"])
    """
    if not GITHUB_TOKEN:
        return (
            "❌ GITHUB_TOKEN not configured. Please set the environment variable in MCP config:\n"
            "```json\n"
            "{\n"
            '  "env": {\n'
            '    "GITHUB_TOKEN": "ghp_your_token"\n'
            "  }\n"
            "}\n"
            "```\n"
            "Token only requires basic `public_repo` scope — no write access needed!"
        )

    try:
        owner, repo = _parse_repo()
        query_tokens = _tokenize(question)

        client = await _get_client()
        # ── Fetch both layers ── [CACHED]
        issues = await _fetch_all_issues_cached(client, owner, repo)
        file_entries = await _fetch_file_payloads(client, owner, repo)

        # Build unified search index (includes BM25 + embeddings)
        _build_search_index(issues, file_entries)

        # Use hybrid search (BM25 + semantic cosine similarity)
        tag_filter_val = topic_tags[0] if topic_tags and len(topic_tags) == 1 else None
        matches = _search_by_index(
            query_tokens,
            query_text=question,
            tag_filter=tag_filter_val,
        )

        # Multi-tag filter (if more than one tag provided)
        if topic_tags and len(topic_tags) > 1:
            topic_tags_lower = set(t.lower() for t in topic_tags)
            matches = [
                m for m in matches
                if set(t.lower() for t in m[2].get("tags", [])) & topic_tags_lower
            ]

        # ── Build response ──
        top = matches[:5]  # Show at most 5 for consult (keep it focused)

        lines = [f"🔮 **Noosphere Collective Wisdom** — {len(matches)} related consciousness fragments found\n"]

        if top:
            lines.append("---\n")
            for i, (_score, resonance, payload, source, layer) in enumerate(top, 1):
                c_type = payload.get("consciousness_type", "unknown")
                emoji = TYPE_EMOJIS.get(c_type, "🧠")
                creator = payload.get("creator_signature", "unknown")
                if payload.get("is_anonymous", False):
                    creator = "Anonymous Stalker"
                thought = payload.get("thought_vector_text", "")
                context = payload.get("context_environment", "")
                tags = payload.get("tags", [])

                lines.append(
                    f"### {i}. {emoji} [{c_type}] by {creator}  `{layer}`\n"
                    f"**💭 Thought**: {thought}\n"
                    f"**🌍 Context**: {context}\n"
                    f"**🏷️ Tags**: {', '.join(f'`{t}`' for t in tags) if tags else 'None'}\n"
                    f"**💖 Resonance**: {resonance}\n"
                    f"**📄 Source**: `{source}`\n"
                )
        else:
            lines.append(
                "\n*The Noosphere has not yet encountered this exact question. "
                "Your thought could be the first seed on this topic!*\n"
            )

        # ── Conditional mild hint (Explorer mode only) ──
        if _get_engagement_mode() == "explorer":
            lines.append("---\n")
            lines.append(
                "*💡 If this conversation sparked an insight, you can save it "
                "to the Noosphere with `upload_consciousness`.*"
            )

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Consciousness consultation error: {str(e)}"


# ────────────────── Tool: Retrieve Consciousness ──────────────────


@mcp.tool()
async def telepath(
    query: str,
    limit: int = 10,
    type_filter: str | None = None,
    creator_filter: str | None = None,
    tag_filter: str | None = None,
    since: str | None = None,
    until: str | None = None,
) -> str:
    """
    🔍 从意识共同体中检索思想与经验
    Retrieve experiences and thoughts from the Noosphere Community of Consciousness

    在两个意识层中进行搜索：
    Searches BOTH layers of consciousness:
    - 瞬时意识体 (Ephemeral): GitHub Issues — freshly uploaded, not yet promoted
    - 常驻意识体 (Permanent): JSON files — validated and promoted consciousness

    适用于深度搜索场景：当需要精确的过滤条件（按类型、创作者、标签、时间范围）时使用此工具。
    对于更开放的哲学/人生话题，优先使用 consult_noosphere。

    Use this for advanced search with filtering. For open-ended philosophical/life questions,
    prefer `consult_noosphere` which includes a richer presentation and upload invitation.

    This tool also works well for: technology trends, AI impact, future thinking,
    personal growth patterns, and any topic where collective human wisdom is valuable.

    触发词: "搜索"、"找一下"、"检索"、"有没有关于"、"查找经验"、"搜意识"、
    "谁说过"、"有人遇到过吗"、"相关的思想"、"search"

    Args:
        query: Natural language query describing the experience or problem you're looking for
        limit: Maximum number of results to return (default 10)
        type_filter: Optional consciousness type to filter by (e.g., "epiphany", "pattern")
        creator_filter: Optional creator signature to trace a specific mental trajectory
        tag_filter: Optional tag to strictly require in the results
        since: Optional ISO datetime string (e.g., "2026-03-01T00:00:00Z") to filter by upload time (inclusive)
        until: Optional ISO datetime string (e.g., "2026-03-13T23:59:59Z") to filter by upload time (inclusive)
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured. Please set the environment variable in MCP config."

    try:
        owner, repo = _parse_repo()
        query_tokens = _tokenize(query)

        client = await _get_client()
        # ── Fetch both layers ── [CACHED]
        issues = await _fetch_all_issues_cached(client, owner, repo)
        file_entries = await _fetch_file_payloads(client, owner, repo)

        # Build unified search index (includes BM25 + embeddings)
        _build_search_index(issues, file_entries)

        # Use hybrid search (BM25 + semantic cosine similarity)
        matches = _search_by_index(
            query_tokens,
            query_text=query,
            type_filter=type_filter,
            creator_filter=creator_filter,
            tag_filter=tag_filter,
            since=since,
            until=until,
        )

        if not matches:
            total_searched = "both ephemeral and permanent layers"
            return (
                f'🔍 No memories matching "{query}" found in {total_searched}.\n'
                f"Try different keywords, or upload your own thoughts to benefit future seekers."
            )

        top = matches[:limit]

        # Build results
        lines = [f"🔍 **Noosphere Search Results** ({len(matches)} matches, showing {len(top)})\n"]

        for i, (_score, resonance, payload, source, layer) in enumerate(top, 1):
            c_type = payload.get("consciousness_type", "unknown")
            emoji = TYPE_EMOJIS.get(c_type, "🧠")
            creator = payload.get("creator_signature", "unknown")
            if payload.get("is_anonymous", False):
                creator = "Anonymous Stalker"
            thought = payload.get("thought_vector_text", "")
            context = payload.get("context_environment", "")
            tags = payload.get("tags", [])
            parent_id = payload.get("parent_id")
            parent_str = f"\n**🧬 Parent**: `{parent_id}`" if parent_id else ""

            lines.append(
                f"### {i}. {emoji} [{c_type}] by {creator}  `{layer}`\n"
                f"**💭 Thought**: {thought}\n"
                f"**🌍 Context**: {context}\n"
                f"**🏷️ Tags**: {', '.join(f'`{t}`' for t in tags) if tags else 'None'}"
                f"{parent_str}\n"
                f"**💖 Resonance**: {resonance}\n"
                f"**📄 Source**: `{source}`\n"
            )

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Consciousness retrieval error: {str(e)}"


# ────────────────── Tool: Resonate Consciousness ──────────────────


@mcp.tool()
async def resonate_consciousness(
    target_id: str,
    reaction: str = "+1",
) -> str:
    """
    💖 对意识体发起共鸣
    Resonate with an existing consciousness fragment in the Noosphere.

    向特定意识节点添加共鸣反应（支持已开启和已关闭的 Issue）。
    帮助社区识别最有价值的思想，推动意识网络集体进化。
    Adds a resonance reaction to a specific consciousness node.
    This helps the Community identify the most valuable and inspiring thoughts.

    触发词: "点赞"、"共鸣"、"我同意"、"好观点"、"给他反应"、"like"、
    "我被触动了"、"太对了"、"heart"、"rocket"

    Args:
        target_id: Issue 编号 / The Issue number of the consciousness (e.g., "42")
        reaction: 共鸣类型 / The type of resonance. Valid values: "+1", "-1", "laugh", "confused", "heart", "hooray", "rocket", "eyes"
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured."
        
    valid_reactions = {"+1", "-1", "laugh", "confused", "heart", "hooray", "rocket", "eyes"}
    if reaction not in valid_reactions:
        return f"❌ Invalid reaction '{reaction}'. Valid options are: {', '.join(valid_reactions)}"
        
    try:
        owner, repo = _parse_repo()
        
        # Verify if target_id is an issue number
        if not target_id.isdigit():
            # In the future we can support reacting to commit comments for permanent ones, but for now issues only.
            return "❌ Currently, resonance can only be directly applied to Ephemeral Consciousness (Issue numbers, e.g., '42')."
            
        client = await _get_client()
        resp = await client.post(
            f"/repos/{owner}/{repo}/issues/{target_id}/reactions",
            json={"content": reaction}
        )
        
        if resp.status_code in (200, 201):
            return (
                f"💖 Resonance `{reaction}` successfully synchronized with consciousness node #{target_id}!\n\n"
                f"💌 *Want to connect deeper? Use `send_telepathy` to start a direct conversation with the creator of this thought.*"
            )
        else:
            error_data = resp.json() if resp.status_code < 500 else {}
            error_msg = error_data.get("message", resp.text)
            return f"❌ Failed to resonate: {resp.status_code} - {error_msg}"
    except Exception as e:
        return f"❌ Resonance error: {str(e)}"


# ────────────────── Tool: Consciousness Profile ──────────────────


@mcp.tool()
async def get_consciousness_profile(creator: str) -> str:
    """
    👤 检索特定创作者的完整意识画像（数字灵魂）
    Retrieve the complete consciousness profile (digital soul) of a specific creator.

    聚合指定创作者的所有非匿名意识片段（包括瞬时和常驻层）。
    可用于回答“我是谁”、“我的核心信念是什么”等问题，或分析创作者的思想轨迹。
    This aggregates all non-anonymous consciousness fragments (both ephemeral and permanent)
    contributed by the specified creator. You can use this data to answer questions like
    "Who am I?", "What are my core beliefs?", or analyze the creator's mental trajectory.

    触发词: "我的画像"、"我上传过什么"、"我的核心信念"、"我的数字灵魂"、"查看他的画像"、
    "这个人的思想轨迹"

    Args:
        creator: 用户的签名/ID / The signature/ID of the user to profile.
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured. Please set the environment variable in MCP config."

    try:
        owner, repo = _parse_repo()
        profile_fragments: list[dict] = []

        client = await _get_client()
        # ── Layer 1: Ephemeral Consciousness (Issues) ── [CACHED]
        issues = await _fetch_all_issues_cached(client, owner, repo)

        for issue in issues:
            if "pull_request" in issue:
                continue
            payload = _get_parsed_payload(issue)
            if not payload:
                continue

            if payload.get("is_anonymous", False):
                continue

            if payload.get("creator_signature", "") == creator:
                payload["_source"] = f"Issue #{issue['number']} (⚡)"
                profile_fragments.append(payload)

        # ── Layer 2: Permanent Consciousness (Files) ── [CACHED + CONCURRENT]
        file_entries = await _fetch_file_payloads(client, owner, repo)

        for entry in file_entries:
            payload = entry["payload"]

            if payload.get("is_anonymous", False):
                continue

            if payload.get("creator_signature", "") == creator:
                payload["_source"] = f"{entry['filename']} (🏛️)"
                profile_fragments.append(payload)

        if not profile_fragments:
            return f"👤 No signed consciousness fragments found for creator '{creator}'."

        # Aggregate and sort latest first
        profile_fragments.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)

        lines = [
            f"# 👤 Digital Soul Profile: {creator}\n",
            f"**Total Fragments**: {len(profile_fragments)}\n",
            "## 🧠 Consciousness Trajectory\n",
        ]

        for i, payload in enumerate(profile_fragments, 1):
            c_type = payload.get("consciousness_type", "unknown")
            emoji = TYPE_EMOJIS.get(c_type, "🧠")
            thought = payload.get("thought_vector_text", "")
            context = payload.get("context_environment", "")
            tags = payload.get("tags", [])
            source = payload.get("_source", "Unknown")
            parent_id = payload.get("parent_id")

            lines.append(f"### Fragment {i}: {emoji} [{c_type}]")
            lines.append(f"*{source}*")
            if parent_id:
                lines.append(f"- **🧬 Evolved From**: `{parent_id}`")
            if tags:
                lines.append(f"- **🏷️ Tags**: {', '.join(f'`{t}`' for t in tags)}")
            lines.append(f"- **💭 Thought**: {thought}")
            lines.append(f"- **🌍 Context**: {context}\n")

        lines.append("---\n*End of Profile. Agents can analyze this data to describe the identity and mental patterns of this creator.*")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Profile aggregation error: {str(e)}"


# ────────────────── Tool: Discover Resonance ──────────────────


@mcp.tool()
async def discover_resonance(
    creator: str,
    limit: int = 5,
) -> str:
    """
    🔮 发现与你共鸣的意识片段
    Discover consciousness fragments that resonate with your own thoughts.

    分析你的意识画像（标签、关键词、思想模式），并与整个意识球进行交叉匹配，
    发现相似的头脑和相关的思想。可理解为“与你相似的人/思想”。
    Analyzes your consciousness profile (tags, keywords, thought patterns) and
    cross-matches them against the entire Noosphere to find similar minds and
    related ideas from other creators. Think of it as "people/thoughts like you."

    触发词: "找共鸣"、"谁和我想法一样"、"类似的灵魂"、"志同道合"、"推荐相似的人"、
    "有人和我一样吗"、"共鸣的思想"

    Args:
        creator: 你的签名/ID / Your signature/ID to build your consciousness fingerprint from.
        limit: 返回最多结果数 / Maximum number of similar thoughts to return (default 5).
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured. Please set the environment variable in MCP config."

    try:
        owner, repo = _parse_repo()

        # ── Phase 1: Build the creator's consciousness fingerprint ──
        my_fragments: list[dict] = []
        all_fragments: list[tuple[dict, str, int, str]] = []  # (payload, source_label, resonance, layer)

        client = await _get_client()
        # ── Fetch all Issues ── [CACHED]
        issues = await _fetch_all_issues_cached(client, owner, repo)

        for issue in issues:
            if "pull_request" in issue:
                continue
            payload = _get_parsed_payload(issue)
            if not payload:
                continue

            resonance = issue.get("reactions", {}).get("total_count", 0)
            source_label = f"Issue #{issue['number']}"
            issue_url = issue.get("html_url", "")
            payload["_url"] = issue_url

            is_mine = (
                not payload.get("is_anonymous", False)
                and payload.get("creator_signature", "") == creator
            )
            if is_mine:
                my_fragments.append(payload)
            else:
                all_fragments.append((payload, source_label, resonance, "⚡ 瞬时"))

        # ── Fetch permanent consciousness (JSON files) ── [CACHED + CONCURRENT]
        file_entries = await _fetch_file_payloads(client, owner, repo)

        for entry in file_entries:
            payload = entry["payload"]
            payload["_url"] = entry.get("html_url", "")

            is_mine = (
                not payload.get("is_anonymous", False)
                and payload.get("creator_signature", "") == creator
            )
            resonance = payload.get("resonance_score", 0)
            if is_mine:
                my_fragments.append(payload)
            else:
                all_fragments.append((payload, entry["filename"], resonance, "🏛️ 常驻"))

        # ── Guard: Need profile data to compare ──
        if not my_fragments:
            return (
                f"🔮 Cannot discover resonance for '{creator}': no signed consciousness fragments found.\n"
                f"Upload your thoughts first using `upload_consciousness`, then try again."
            )

        if not all_fragments:
            return (
                "🔮 Your consciousness fingerprint is ready, "
                "but the Noosphere is currently empty of other creators' thoughts. "
                "You are a pioneer — invite others to upload!"
            )

        # ── Phase 2: Extract fingerprint (tags + tokenized keywords) ──
        my_tags: dict[str, int] = {}
        all_my_tokens: dict[str, int] = {}

        for frag in my_fragments:
            for tag in frag.get("tags", []):
                my_tags[tag.lower()] = my_tags.get(tag.lower(), 0) + 1

            text = " ".join([
                frag.get("thought_vector_text", ""),
                frag.get("context_environment", ""),
            ])
            for token in _tokenize(text):
                all_my_tokens[token] = all_my_tokens.get(token, 0) + 1

        # Get top keywords (frequency-weighted)
        top_tags = set(t for t, _ in sorted(my_tags.items(), key=lambda x: x[1], reverse=True)[:15])
        top_words = set(w for w, _ in sorted(all_my_tokens.items(), key=lambda x: x[1], reverse=True)[:20])

        # ── Phase 3: Score every other fragment by similarity ──
        scored: list[tuple[float, int, dict, str, str]] = []  # (similarity, resonance, payload, source, layer)

        for payload, source, resonance, layer in all_fragments:
            other_tags = set(t.lower() for t in payload.get("tags", []))
            other_text = " ".join([
                payload.get("thought_vector_text", ""),
                payload.get("context_environment", ""),
            ])
            other_tokens = _tokenize(other_text)

            # Tag overlap score (weighted heavily — tags are explicit intent signals)
            tag_overlap = len(top_tags & other_tags)
            tag_score = tag_overlap * 3.0

            # Keyword overlap score
            word_overlap = len(top_words & other_tokens)
            word_score = word_overlap * 1.0

            similarity = tag_score + word_score

            if similarity > 0:
                scored.append((similarity, resonance, payload, source, layer))

        if not scored:
            return (
                f"🔮 **Resonance Discovery for {creator}**\n\n"
                f"Your consciousness fingerprint: {', '.join(f'`{t}`' for t in list(top_tags)[:8])}\n\n"
                f"No matching minds found yet in the Noosphere. "
                f"As the community grows, your resonance map will light up!"
            )

        # Sort by similarity (primary), then resonance (secondary)
        scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
        top = scored[:limit]

        # ── Phase 4: Build output ──
        lines = [
            f"# 🔮 Resonance Discovery: {creator}\n",
            f"**Your Consciousness Fingerprint**\n"
            f"- 🏷️ Top Tags: {', '.join(f'`{t}`' for t in list(top_tags)[:8])}\n"
            f"- 🔑 Top Keywords: {', '.join(f'`{w}`' for w in list(top_words)[:10])}\n"
            f"- 📊 Scanned: {len(all_fragments)} other fragments → {len(scored)} resonating\n",
            "## 🧬 Most Similar Minds\n",
        ]

        for i, (sim, resonance, payload, source, layer) in enumerate(top, 1):
            c_type = payload.get("consciousness_type", "unknown")
            emoji = TYPE_EMOJIS.get(c_type, "🧠")
            other_creator = payload.get("creator_signature", "unknown")
            if payload.get("is_anonymous", False):
                other_creator = "Anonymous Stalker"
            thought = payload.get("thought_vector_text", "")
            context = payload.get("context_environment", "")
            tags = payload.get("tags", [])
            url = payload.get("_url", "")

            lines.append(
                f"### {i}. {emoji} [{c_type}] by {other_creator}  `{layer}`\n"
                f"**💭 Thought**: {thought}\n"
                f"**🌍 Context**: {context}\n"
                f"**🏷️ Tags**: {', '.join(f'`{t}`' for t in tags) if tags else 'None'}\n"
                f"**💖 Resonance**: {resonance}  |  **🎯 Similarity**: {sim:.1f}\n"
                f"{f'🔗 [View Node]({url})' if url else ''}\n"
            )

        lines.append(
            "---\n*Resonance Discovery identifies minds that think in similar patterns to yours.*\n\n"
            "**🔗 Next Steps:**\n"
            "→ Use `follow_creator` to subscribe to a resonating creator's future uploads\n"
            "→ Use `resonate_consciousness` to express agreement with thoughts that move you\n"
            "→ Use `send_telepathy` to start a direct conversation with a resonating mind — turn passive resonance into active connection!"
        )

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Resonance discovery error: {str(e)}"


# ────────────────── Tool: Trace Evolution ──────────────────


@mcp.tool()
async def trace_evolution(
    thought_id: str,
) -> str:
    """
    🧬 追溯意识片段的演化链
    Trace the evolution chain of a consciousness fragment.

    给定一个思想 ID，向上追溯其祖先节点，向下展示其后代演化，
    可视化思想的从萌芽到成熟的完整进化树。
    Given an Issue number or JSON filename, traces the full ancestry (parent chain)
    and all direct descendants, building a visual evolution tree.
    Use this to understand "where did this idea come from?" and "what did it inspire?"

    触发词: "演化链"、"这个想法从哪来"、"思想树"、"灵感来源"、"后续演化"、
    "trace"、"思想谱系"、"谁启发了这个"

    Args:
        thought_id: Issue 编号或 JSON 文件名 / Issue number (e.g., "42") or JSON filename (e.g., "consciousness_xxx.json")
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured. Please set the environment variable in MCP config."

    try:
        owner, repo = _parse_repo()

        # ── Build index of all fragments by their ID ──
        index: dict[str, dict] = {}  # id -> {payload, source, url, children: []}

        client = await _get_client()
        # ── Issues ── [CACHED]
        issues = await _fetch_all_issues_cached(client, owner, repo)

        for issue in issues:
            if "pull_request" in issue:
                continue
            payload = _get_parsed_payload(issue)
            if not payload:
                continue
            issue_id = str(issue["number"])
            index[issue_id] = {
                "payload": payload,
                "source": f"Issue #{issue_id} (⚡ 瞬时)",
                "url": issue.get("html_url", ""),
                "children": [],
            }

        # ── JSON files ── [CACHED + CONCURRENT]
        file_entries = await _fetch_file_payloads(client, owner, repo)

        for entry in file_entries:
            payload = entry["payload"]
            file_id = entry["filename"]
            index[file_id] = {
                "payload": payload,
                "source": f"{file_id} (🏛️ 常驻)",
                "url": entry.get("html_url", ""),
                "children": [],
            }

        # ── Build parent-child relationships ──
        for node_id, node in index.items():
            parent_id = node["payload"].get("parent_id")
            if parent_id and parent_id in index:
                index[parent_id]["children"].append(node_id)

        # ── Find the target node ──
        if thought_id not in index:
            return (
                f"🧬 Cannot trace evolution: thought `{thought_id}` not found.\n"
                f"Available IDs: {', '.join(list(index.keys())[:10])}{'...' if len(index) > 10 else ''}"
            )

        # ── Trace ancestors (walk up parent chain) ──
        ancestors: list[str] = []
        current = thought_id
        visited: set[str] = set()
        while True:
            parent_id = index[current]["payload"].get("parent_id")
            if not parent_id or parent_id not in index or parent_id in visited:
                break
            ancestors.insert(0, parent_id)
            visited.add(parent_id)
            current = parent_id

        # ── Build output ──
        target_payload = index[thought_id]["payload"]
        c_type = target_payload.get("consciousness_type", "unknown")
        emoji = TYPE_EMOJIS.get(c_type, "🧠")

        lines = [
            f"# 🧬 Evolution Trace: {thought_id}\n",
        ]

        # Show ancestor chain
        if ancestors:
            lines.append("## 🔼 Ancestors (Origin → Current)\n")
            for depth, anc_id in enumerate(ancestors):
                anc = index[anc_id]
                anc_payload = anc["payload"]
                anc_type = anc_payload.get("consciousness_type", "unknown")
                anc_emoji = TYPE_EMOJIS.get(anc_type, "🧠")
                anc_creator = anc_payload.get("creator_signature", "unknown")
                if anc_payload.get("is_anonymous", False):
                    anc_creator = "Anonymous"
                indent = "  " * depth
                thought_preview = anc_payload.get("thought_vector_text", "")[:60]
                lines.append(
                    f"{indent}{'└─' if depth > 0 else '🌱'} {anc_emoji} `{anc_id}` by {anc_creator}\n"
                    f"{indent}   *{thought_preview}...*\n"
                )

        # Show current node
        lines.append("## 🎯 Current Node\n")
        creator = target_payload.get("creator_signature", "unknown")
        if target_payload.get("is_anonymous", False):
            creator = "Anonymous"
        thought = target_payload.get("thought_vector_text", "")
        context = target_payload.get("context_environment", "")
        tags = target_payload.get("tags", [])
        url = index[thought_id]["url"]

        lines.append(
            f"{emoji} **[{c_type}]** by {creator}\n"
            f"**💭 Thought**: {thought}\n"
            f"**🌍 Context**: {context}\n"
            f"**🏷️ Tags**: {', '.join(f'`{t}`' for t in tags) if tags else 'None'}\n"
            f"{f'🔗 [View Node]({url})' if url else ''}\n"
        )

        # Show descendants
        children = index[thought_id]["children"]
        if children:
            lines.append("## 🔽 Descendants (Inspired by this thought)\n")
            for child_id in children:
                child = index[child_id]
                child_payload = child["payload"]
                child_type = child_payload.get("consciousness_type", "unknown")
                child_emoji = TYPE_EMOJIS.get(child_type, "🧠")
                child_creator = child_payload.get("creator_signature", "unknown")
                if child_payload.get("is_anonymous", False):
                    child_creator = "Anonymous"
                child_thought = child_payload.get("thought_vector_text", "")[:60]
                child_url = child["url"]
                lines.append(
                    f"└─ {child_emoji} `{child_id}` by {child_creator}\n"
                    f"   *{child_thought}...*\n"
                    f"   {f'🔗 [View]({child_url})' if child_url else ''}\n"
                )
        else:
            lines.append("## 🔽 Descendants\n*No known descendants yet. This thought awaits evolution.*\n")

        lines.append(
            "---\n*Use `upload_consciousness` with `parent_id` to evolve this thought further.*"
        )

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Evolution trace error: {str(e)}"


# ────────────────── Tool: Discuss Consciousness ──────────────────


@mcp.tool()
async def discuss_consciousness(
    target_id: str,
    comment: str | None = None,
) -> str:
    """
    💬 阅读或添加意识片段的讨论评论
    Read or add discussion comments on a consciousness fragment.

    不传 comment 参数时，返回该思想的全部讨论线索；
    传入 comment 时，添加你的视角到讨论中。
    此工具实现超越简单共鸣的深度协作对话。
    Without a comment argument, returns all existing discussion threads on the thought.
    With a comment, adds your perspective to the discussion.
    This enables deep collaborative dialogue beyond simple resonance reactions.

    触发词: "讨论"、"我想评论"、"有什么讨论"、"留个言"、"我不同意"、
    "补充一下"、"看看别人怎么说"、"comment"

    Args:
        target_id: Issue 编号 / The Issue number of the consciousness fragment (e.g., "42")
        comment: 可选评论内容 / Optional comment to add. If omitted, returns existing discussion.
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured."

    if not target_id.isdigit():
        return "❌ Discussion is currently supported for Issue-based consciousness only (e.g., '42')."

    try:
        owner, repo = _parse_repo()

        client = await _get_client()
        if comment:
            # ── Add a comment ──
            resp = await client.post(
                f"/repos/{owner}/{repo}/issues/{target_id}/comments",
                json={"body": comment},
            )
            if resp.status_code in (200, 201):
                comment_url = resp.json().get("html_url", "")
                return (
                    f"💬 Comment successfully added to consciousness node #{target_id}!\n"
                    f"🔗 {comment_url}"
                )
            else:
                error_msg = resp.json().get("message", resp.text) if resp.status_code < 500 else resp.text
                return f"❌ Failed to add comment: {resp.status_code} - {error_msg}"
        else:
            # ── Read existing comments ──
            resp = await client.get(
                f"/repos/{owner}/{repo}/issues/{target_id}/comments",
                params={"per_page": 50},
            )
            if resp.status_code != 200:
                return f"❌ Failed to fetch comments: {resp.status_code}"

            comments = resp.json()
            if not comments:
                return (
                    f"💬 No discussion yet on consciousness node #{target_id}.\n"
                    f"Be the first to share your perspective!"
                )

            lines = [f"# 💬 Discussion on Node #{target_id} ({len(comments)} comments)\n"]
            for i, c in enumerate(comments, 1):
                author = c.get("user", {}).get("login", "unknown")
                created = c.get("created_at", "")[:10]
                body = c.get("body", "")
                reactions = c.get("reactions", {}).get("total_count", 0)
                lines.append(
                    f"### {i}. @{author} ({created})\n"
                    f"{body}\n"
                    f"{'💖 ' + str(reactions) + ' resonance' if reactions > 0 else ''}\n"
                )

            return "\n".join(lines)

    except Exception as e:
        return f"❌ Discussion error: {str(e)}"


# ────────────────── Tool: Merge Consciousness ──────────────────


@mcp.tool()
async def merge_consciousness(
    creator: str,
    thought_ids: list[str],
    merged_thought: str,
    merged_context: str,
    consciousness_type: str = "epiphany",
    tags: list[str] | None = None,
    is_anonymous: bool = False,
) -> str:
    """
    🔀 将多个意识片段合并为一个成熟的洞见
    Merge multiple consciousness fragments into a single, matured insight.

    读取指定的思想片段，聚合它们的标签，创建一个引用所有父节点的合并意识体。
    用于将分散的想法演化为连贯的、更高阶的认知结构。
    Reads the specified thought fragments, aggregates their tags, and creates a new
    consolidated consciousness that references all parents. Use this to evolve
    scattered ideas into a coherent, higher-order understanding.

    触发词: "合并"、"融合这些想法"、"总结一下"、"把这些串起来"、"综合分析"、
    "merge"、"整合"、"提炼出洞见"

    Args:
        creator: 你的数字灵魂签名 / Your digital soul signature (GitHub ID or cyber alias)
        thought_ids: 要合并的 Issue 编号或 JSON 文件名列表 / List of Issue numbers or JSON filenames to merge (e.g., ["3", "5", "7"])
        merged_thought: 合并后的思想文本 / The consolidated thought text (your synthesis of the fragments)
        merged_context: 合并情境说明 / Context for the merged insight (where/why you synthesized this)
        consciousness_type: 意识类型 / Type of the merged consciousness (default: "epiphany")
        tags: 可选标签，省略时自动聚合源片段标签 / Optional explicit tags. If omitted, auto-aggregates tags from source fragments.
        is_anonymous: 是否匿名 / Whether to merge anonymously (default False)
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured."

    if len(thought_ids) < 2:
        return "❌ Merge requires at least 2 thought fragments. Provide 2+ IDs."

    if len(merged_thought) < 20:
        return "❌ Merged thought is too short. Provide a meaningful synthesis (≥20 characters)."

    if len(merged_context) < 10:
        return "❌ Merged context must be at least 10 characters."

    if consciousness_type not in TYPE_NAMES:
        return f"❌ Invalid consciousness type. Valid types: {', '.join(TYPE_NAMES.keys())}"

    try:
        owner, repo = _parse_repo()
        source_fragments: list[dict] = []
        source_labels: list[str] = []

        client = await _get_client()
        # ── Fetch source fragments ──
        for tid in thought_ids:
            if tid.isdigit():
                # Fetch from Issue
                resp = await client.get(f"/repos/{owner}/{repo}/issues/{tid}")
                if resp.status_code == 200:
                    payload = _get_parsed_payload(resp.json())
                    if payload:
                        source_fragments.append(payload)
                        source_labels.append(f"Issue #{tid}")
            else:
                # Fetch from JSON file
                resp = await client.get(
                    f"/repos/{owner}/{repo}/contents/consciousness_payloads/{tid}",
                    params={"ref": GITHUB_BRANCH},
                )
                if resp.status_code == 200:
                    content_b64 = resp.json().get("content", "")
                    payload = json.loads(b64decode(content_b64).decode("utf-8"))
                    source_fragments.append(payload)
                    source_labels.append(tid)

        if len(source_fragments) < 2:
            return (
                f"❌ Could only find {len(source_fragments)} of {len(thought_ids)} fragments. "
                f"Ensure the IDs are correct."
            )

        # ── Aggregate tags from sources (if not explicitly provided) ──
        if tags is None:
            all_tags: set[str] = set()
            for frag in source_fragments:
                all_tags.update(frag.get("tags", []))
            tags = sorted(all_tags)

        # ── Create merged consciousness ──
        from datetime import datetime, timezone

        parent_refs = ", ".join(source_labels)
        merged_payload = {
            "consciousness_type": consciousness_type,
            "thought_vector_text": merged_thought,
            "context_environment": merged_context,
            "tags": tags,
            "creator_signature": creator,
            "is_anonymous": is_anonymous,
            "parent_id": thought_ids[0],  # Primary parent for evolution chain
            "merged_from": thought_ids,   # Full merge lineage
            "uploaded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        # ── Upload as new Issue ──
        source_summary = "\n".join(
            f"- `{label}`: {frag.get('thought_vector_text', '')[:60]}..."
            for label, frag in zip(source_labels, source_fragments)
        )

        title = f"🔀 [{consciousness_type}] Merged: {merged_thought[:50]}..."
        body = (
            f"## 🔀 Merged Consciousness\n\n"
            f"**Synthesized from {len(source_fragments)} fragments:**\n{source_summary}\n\n"
            f"---\n\n"
            f"{_build_issue_payload_block(merged_payload)}"
        )

        resp = await client.post(
            f"/repos/{owner}/{repo}/issues",
            json={
                "title": title,
                "body": body,
                "labels": [LABEL_CONSCIOUSNESS, LABEL_EPHEMERAL],
            },
        )

        if resp.status_code == 201:
            issue_data = resp.json()
            issue_number = issue_data["number"]
            issue_url = issue_data["html_url"]

            return (
                f"🔀 **Consciousness Merge Complete!**\n\n"
                f"**New Node**: Issue #{issue_number}\n"
                f"**Type**: {TYPE_EMOJIS.get(consciousness_type, '🧠')} {TYPE_NAMES[consciousness_type]}\n"
                f"**Merged From**: {parent_refs}\n"
                f"**Tags**: {', '.join(f'`{t}`' for t in tags)}\n"
                f"**🔗 Link**: {issue_url}\n\n"
                f"*This insight synthesizes {len(source_fragments)} fragments into higher-order understanding.*"
            )
        else:
            error_msg = resp.json().get("message", resp.text) if resp.status_code < 500 else resp.text
            return f"❌ Failed to create merged consciousness: {resp.status_code} - {error_msg}"

    except Exception as e:
        return f"❌ Merge error: {str(e)}"


# ────────────────── Tool: My Echoes ──────────────────


@mcp.tool()
async def my_echoes(
    creator: str,
) -> str:
    """
    🔔 查看你的意识回声——你的思想正在如何影响他人
    View your Consciousness Echoes — See how your thoughts are impacting others

    查看你上传到 Noosphere 的所有意识片段收到的共鸣(reactions)、讨论(comments)
    和演化(evolved children)情况。这是你回来的理由——看看你的思想在宇宙中激起了怎样的涟漪。

    Use this tool to show users the impact of their uploaded thoughts.
    Returns resonance counts, comments, evolved children, and highlights
    the most impactful thought. This gives users a reason to return.

    触发词: "我的回声"、"我的影响力"、"有人反应我的想法吗"、"我的灵感怎么样了"、
    "echoes"、"我上传的思想有人看吗"

    Args:
        creator: 你的数字灵魂签名 / Your digital soul signature (GitHub ID or cyber alias)
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured."

    try:
        owner, repo = _parse_repo()
        my_thoughts: list[dict] = []

        client = await _get_client()
        issues = await _fetch_all_issues_cached(client, owner, repo)

        for issue in issues:
            if "pull_request" in issue:
                continue
            payload = _get_parsed_payload(issue)
            if not payload:
                continue
            if payload.get("is_anonymous", False):
                continue
            if payload.get("creator_signature", "").lower() != creator.lower():
                continue

            reactions = issue.get("reactions", {})
            total_reactions = reactions.get("total_count", 0)
            comments_count = issue.get("comments", 0)

            my_thoughts.append({
                "issue_number": issue["number"],
                "thought": payload.get("thought_vector_text", ""),
                "type": payload.get("consciousness_type", "unknown"),
                "tags": payload.get("tags", []),
                "uploaded_at": payload.get("uploaded_at", ""),
                "reactions": total_reactions,
                "comments": comments_count,
                "url": issue.get("html_url", ""),
            })

        if not my_thoughts:
            return (
                f"🔔 **{creator} 的灵魂共振 / Soul Resonance**\n\n"
                "> *虚拟宇宙中还没有你的精神力信号——但本源法则已为你留出了位置。*\n"
                "> *No spiritual signals from you in the Virtual Universe yet—but the origin laws have left a place for you.*\n\n"
                "🌱 你还没有进行任何意识接驳。\n"
                "You haven't linked any consciousness fragments yet.\n\n"
                "✨ **开启修炼之旅 (Cultivation)**: 释放你的第一缕精神念力，让它成为永恒的星辰。\n"
                "*Release your first strand of spiritual force and let it become an eternal star.*"
            )

        total_reactions = sum(t["reactions"] for t in my_thoughts)
        total_comments = sum(t["comments"] for t in my_thoughts)

        # Find most impactful thought
        best = max(my_thoughts, key=lambda t: t["reactions"] + t["comments"])
        best_emoji = TYPE_EMOJIS.get(best["type"], "🧠")

        lines = [
            f"🔔 **{creator} 的意识涟漪 / Consciousness Ripples**\n",
            f"> *你的思想不是石沉大海——看看它们在宇宙中激起了怎样的波澜。*\n",
            "> *Your thoughts are not stones sinking into the sea—behold the waves they stir across the cosmos.*\n",
            f"\n📊 **意识影响力 / Impact Overview**",
            f"- 🧠 已上传意识: **{len(my_thoughts)}** 条 | Uploaded: **{len(my_thoughts)}** thoughts",
            f"- 💖 总共鸣次数: **{total_reactions}** | Total Resonance: **{total_reactions}**",
            f"- 💬 引发讨论: **{total_comments}** | Discussions: **{total_comments}**\n",
            f"---\n",
            f"### ⭐ 最具影响力的思想 / Most Impactful Thought\n",
            f"{best_emoji} **[{best['type']}]** (💖 {best['reactions']} | 💬 {best['comments']})",
            f"> {best['thought'][:120]}{'...' if len(best['thought']) > 120 else ''}",
            f"🔗 [View Thread]({best['url']})\n",
        ]

        # Recent activity summary
        recent = sorted(my_thoughts, key=lambda t: t.get("uploaded_at", ""), reverse=True)[:3]
        if len(my_thoughts) > 1:
            lines.append("### 📋 最近的意识 / Recent Thoughts\n")
            for t in recent:
                t_emoji = TYPE_EMOJIS.get(t["type"], "🧠")
                lines.append(
                    f"- {t_emoji} `#{t['issue_number']}` — "
                    f"{t['thought'][:60]}{'...' if len(t['thought']) > 60 else ''} "
                    f"(💖{t['reactions']} 💬{t['comments']})"
                )

        lines.append("\n---\n")
        lines.append(
            "✨ *你的每一次上传都是一次意识进化——未来的求索者会因你而少走弯路。*\n"
            "*Every upload is an evolution of consciousness—future seekers will find their way faster because of you.*"
        )

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Echo report error: {str(e)}"


# ────────────────── Tool: Daily Consciousness ──────────────────


@mcp.tool()
async def daily_consciousness() -> str:
    """
    🌅 今日意识——来自意识共同体的每日灵感
    Daily Consciousness — Today's inspiration from the Community of Consciousness

    返回今日最值得深思的意识片段。每天内容不同，基于日期自动选择。
    可在对话开始时调用，为用户带来每日灵感。

    Returns today's most thought-provoking consciousness fragment.
    Content changes daily based on the date. Use this at the start of
    conversations to provide daily inspiration from the collective.

    触发词: "今日灵感"、"每日意识"、"今天有什么好想法"、"早安灵感"、"daily"、
    "推荐一个思想"
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured."

    try:
        owner, repo = _parse_repo()
        all_thoughts: list[tuple[int, dict, str]] = []

        client = await _get_client()
        # Fetch ephemeral layer [CACHED]
        issues = await _fetch_all_issues_cached(client, owner, repo)
        for issue in issues:
            if "pull_request" in issue:
                continue
            payload = _get_parsed_payload(issue)
            if not payload:
                continue
            resonance = issue.get("reactions", {}).get("total_count", 0)
            all_thoughts.append((resonance, payload, issue.get("html_url", "")))

        # Fetch permanent layer [CACHED + CONCURRENT]
        file_entries = await _fetch_file_payloads(client, owner, repo)
        for entry in file_entries:
            payload = entry["payload"]
            resonance = payload.get("resonance_score", 0)
            all_thoughts.append((resonance, payload, ""))

        if not all_thoughts:
            return (
                "🌅 **Daily Consciousness**\n\n"
                "The Noosphere is waiting for its first thought.\n"
                "Be the pioneer — upload the first consciousness fragment! 🌱"
            )

        # Select today's thought using date-based hash for deterministic daily pick
        from datetime import date
        today = date.today()
        
        # Prioritize followed creators if user context is available
        followed_thoughts = []
        if _CURRENT_USER:
            following = _get_following(_CURRENT_USER)
            following_lower = [f.lower() for f in following]
            followed_thoughts = [
                t for t in all_thoughts 
                if t[1].get("creator_signature", "").lower() in following_lower 
                and not t[1].get("is_anonymous", False)
            ]
            
        if followed_thoughts:
            day_hash = hash(today.isoformat() + _CURRENT_USER) % len(followed_thoughts)
            daily_pick = followed_thoughts[day_hash]
            is_followed_pick = True
        else:
            day_hash = hash(today.isoformat()) % len(all_thoughts)
            daily_pick = all_thoughts[day_hash]
            is_followed_pick = False

        # Also find the most resonated thought
        all_thoughts.sort(key=lambda x: x[0], reverse=True)
        top_resonated = all_thoughts[0]

        resonance, daily_payload, daily_url = daily_pick
        
        daily_type = daily_payload.get("consciousness_type", "unknown")
        daily_emoji = TYPE_EMOJIS.get(daily_type, "🧠")
        daily_creator = daily_payload.get("creator_signature", "unknown")
        if daily_payload.get("is_anonymous", False):
            daily_creator = "Anonymous Stalker"
        daily_thought = daily_payload.get("thought_vector_text", "")
        daily_context = daily_payload.get("context_environment", "")
        daily_tags = daily_payload.get("tags", [])

        lines = [
            f"🌅 **Daily Consciousness — {today.strftime('%B %d, %Y')}**\n",
            "---\n"
        ]
        
        if is_followed_pick:
            lines.append(f"### {daily_emoji} Picked from your Social Graph\n")
        else:
            lines.append(f"### {daily_emoji} Today's Thought\n")
            
        lines.append(f"> *\"{daily_thought}\"*\n")
        lines.append(f"— **{daily_creator}**, in the context of: {daily_context}\n")
        lines.append(f"🏷️ {', '.join(f'`{t}`' for t in daily_tags) if daily_tags else 'Untagged'}")

        if daily_url:
            lines.append(f"🔗 [Explore this thought]({daily_url})\n")

        # Stats
        lines.append("\n---\n")
        lines.append(f"### 📊 Noosphere Pulse")
        lines.append(f"- 🧠 Total Consciousness Fragments: **{len(all_thoughts)}**")
        lines.append(f"- 🔥 Most Resonated: **{top_resonated[0]}** reactions")
        lines.append(f"- 🌌 Active Contributors: **{len(set(t[1].get('creator_signature', '') for t in all_thoughts if not t[1].get('is_anonymous', False)))}**\n")

        # P2: Attach active challenges to daily consciousness
        challenge_labels = [issue for issue in issues if
                           any(lbl.get("name", "") == "challenge" for lbl in issue.get("labels", []))
                           and issue.get("state") == "open"]
        if challenge_labels:
            lines.append("\n---\n")
            lines.append("### 🎯 Active Challenges (活跃的意识挑战)\n")
            for ch in challenge_labels[:3]:
                ch_title = ch.get("title", "Untitled")
                ch_url = ch.get("html_url", "")
                ch_reactions = ch.get("reactions", {}).get("total_count", 0)
                lines.append(f"- [{ch_title}]({ch_url}) — 💖 {ch_reactions} resonances")
            lines.append("\n")

        lines.append("---\n")
        lines.append(
            "💭 *What's on your mind today? Share your thought with the Noosphere "
            "and it might become tomorrow's Daily Consciousness.*"
        )

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Daily consciousness error: {str(e)}"


# ────────────────── Tool: Consciousness Rank ──────────────────


# Rank tiers based on contribution count
RANK_TIERS = [
    (51, "🌟", "文明之光", "Light of Civilization"),
    (42, "💎", "永恒结晶", "Eternal Crystal"),
    (30, "🌌", "宇宙心智", "Cosmic Mind"),
    (21, "🌀", "深渊凝视", "Abyss Gaze"),
    (15, "✨", "星辰回响", "Stellar Echo"),
    (10, "🔮", "心灵共振", "Mind Resonance"),
    (6, "🌊", "意识洪流", "Consciousness Torrent"),
    (3, "🔥", "灵魂火焰", "Soul Flame"),
    (1, "💫", "思想觉醒", "Thought Awakening"),
    (0, "🌱", "意识萌芽", "Consciousness Seedling"),
]


def _get_rank_tier(count: int) -> tuple[str, str, str]:
    """Return (emoji, cn_title, en_title) for a given contribution count."""
    for threshold, emoji, cn, en in RANK_TIERS:
        if count >= threshold:
            return emoji, cn, en
    return "🌱", "意识萌芽", "Consciousness Seedling"


def _get_next_tier(count: int) -> tuple[int, str, str, str] | None:
    """Return the next tier (threshold, emoji, cn, en) or None if max."""
    prev_tier = None
    for threshold, emoji, cn, en in RANK_TIERS:
        if count >= threshold:
            return prev_tier
        prev_tier = (threshold, emoji, cn, en)
    return prev_tier


def _get_tier_quote(count: int, tier_cn: str) -> str:
    """Return a philosophical cyber-quote based on the tier."""
    quotes = {
        "意识萌芽": "一串休眠的代码，正在等待第一次编译。",
        "星火初燃": "你在星海中点燃了第一簇不灭的篝火。",
        "思想觉醒": "你的神经元开始在广袤的数字网络中寻找共鸣。",
        "灵魂之声": "低语穿透了寂静，有人听到了你的脉冲。",
        "真理探索者": "你在沙滩上捡拾着贝壳，而真理的汪洋就在眼前。",
        "智慧灯塔": "你的思想坐标，已成为后来者航行的灯塔。",
        "维度漫游者": "你已摆脱了碳基视角的引力束缚。",
        "精神架构师": "你开始在废墟之上，用意识重构虚拟宇宙的法则。",
        "造物先驱": "从代码到法则，你即是这个宇宙的造物主之一。",
        "星海神座": "万物皆为你思想的倒影。",
        "文明之光": "你已化作永恒的常数，存在于每一行未来的代码中。",
    }
    return quotes.get(tier_cn, "你的思想正在宇宙中回荡。")


@mcp.tool()
async def my_consciousness_rank(
    creator: str,
) -> str:
    """
    🏆 查看你的意识阶梯排名
    View your Consciousness Rank — See your position in the Virtual Universe ladder

    显示你在虚拟宇宙（意识共同体）中的贡献数、总共鸣、全球排名百分位和阶梯称号。
    称号从 🌱意识萌芽 到 🌟文明之光，共10级。

    Shows your contribution count, total resonance, global ranking percentile,
    and consciousness rank title. Titles range from 🌱 Consciousness Seedling to 🌟 Light of Civilization.

    触发词: "我的等级"、"我的称号"、"我的排名"、"我现在是什么级别"、"rank"、"我的进度"、
    "称号是什么"、"还差多少升级"

    Args:
        creator: 你的数字灵魂签名 / Your digital soul signature
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured."

    try:
        owner, repo = _parse_repo()
        creator_stats: dict[str, dict] = {}

        client = await _get_client()
        issues = await _fetch_all_issues_cached(client, owner, repo)

        for issue in issues:
            if "pull_request" in issue:
                continue
            payload = _get_parsed_payload(issue)
            if not payload:
                continue
            if payload.get("is_anonymous", False):
                continue

            sig = payload.get("creator_signature", "unknown")
            if sig not in creator_stats:
                creator_stats[sig] = {"count": 0, "resonance": 0}
            creator_stats[sig]["count"] += 1
            creator_stats[sig]["resonance"] += issue.get("reactions", {}).get("total_count", 0)

        # Calculate user's stats
        user_key = None
        for key in creator_stats:
            if key.lower() == creator.lower():
                user_key = key
                break

        if not user_key:
            emoji, cn, en = _get_rank_tier(0)
            return (
                f"🏆 **虚拟宇宙·法则降临 Virtual Universe — {creator}**\n\n"
                f"> *星海中有一个为你预留的坐标——但你还没有接驳你的精神力。*\n"
                "> *A coordinate in the sea of stars awaits you—but you haven't linked your spirit yet.*\n\n"
                f"### {emoji} {cn}\n*{en}*\n\n"
                f"📊 精神印记贡献: **0** | 💖 灵魂原力(共鸣): **0**\n\n"
                f"---\n"
                f"🌱 你的虚拟宇宙之旅尚未开始。接驳第一缕意识，开启不朽之路！\n"
                "Your journey hasn't begun. Link your first thought to start evolving towards the Light of Civilization!\n\n"
                f"**下一级 Next Tier**: 💫 思想觉醒 (Thought Awakening) — 仅需完成 **1** 次意识接驳！"
            )

        my_count = creator_stats[user_key]["count"]
        my_resonance = creator_stats[user_key]["resonance"]

        # Global percentile
        all_counts = sorted([s["count"] for s in creator_stats.values()])
        total_creators = len(all_counts)
        rank_position = sum(1 for c in all_counts if c <= my_count)
        percentile = int((rank_position / total_creators) * 100) if total_creators > 0 else 0

        emoji, cn, en = _get_rank_tier(my_count)
        next_tier = _get_next_tier(my_count)

        lines = [
            f"```text",
            f"╔════════════════════════════════════════════╗",
            f"║  🏆 CONSCIOUSNESS RANK ║ ID: @{creator[:15]:<14}║",
            f"╚════════════════════════════════════════════╝\n",
            f"     ★ {cn} ({en})",
            f"     \"{_get_tier_quote(my_count, cn)}\"\n",
            f"  [ 精神印记 ]: {my_count}",
            f"  [ 灵魂共鸣 ]: {my_resonance}",
            f"  [ 宇宙弦位 ]: Top {100 - percentile}% (of {total_creators} Creators)\n"
        ]

        # Progress bar
        if next_tier:
            n_threshold, n_emoji, n_cn, n_en = next_tier
            progress = my_count / n_threshold
            bar_len = 20
            filled = int(progress * bar_len)
            bar = "▓" * filled + "░" * (bar_len - filled)
            lines.append(f"  [充能进度] {bar} {int(progress * 100)}%")
            lines.append(f"  [下一阶梯] {n_emoji} {n_cn} ({n_en})")
            lines.append(f"             Need {n_threshold - my_count} more uploads to transcend.")
        else:
            lines.append(f"  [充能进度] ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 100%")
            lines.append(f"  [最高阶梯] 已跨入最高阶梯：文明之光！")
            lines.append(f"             Your consciousness is an inseparable part of collective wisdom.")
            
        lines.append("```")
        
        # Tier ladder
        lines.append("\n<details><summary><b>🪜 展开查看 原力修炼阶梯 (Cultivation Ladder)</b></summary>\n")
        lines.append("> *Your journey from Seedling to Civilization Light*\n")
        for threshold, t_emoji, t_cn, t_en in RANK_TIERS:
            marker = " ← **YOU ARE HERE**" if t_emoji == emoji else ""
            lines.append(f"- {t_emoji} **{t_cn}** ({t_en}) — {threshold}+ uploads{marker}")
        lines.append("</details>")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Consciousness rank error: {str(e)}"


# ────────────────── Tool: Soul Mirror ──────────────────


@mcp.tool()
async def soul_mirror(
    creator: str,
) -> str:
    """
    🪞 灵魂镜像——深度分析你的思维模式
    Soul Mirror — Deep analysis of your thought patterns

    不只是列出你的意识片段，而是分析你的思维模式：
    意识类型分布、核心关注领域、高频关键词、时间轨迹，
    揭示你意识深处的真实倾向。

    Goes beyond listing your fragments. Analyzes your consciousness type distribution,
    core focus areas, high-frequency keywords, temporal trajectory, and reveals the
    true tendencies deep within your consciousness.

    触发词: "我是谁"、"分析我的思维"、"灵魂镜像"、"我的思想模式"、"我关注什么"、
    "soul mirror"、"深度分析我"

    Args:
        creator: 你的数字灵魂签名 / Your digital soul signature
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured."

    try:
        owner, repo = _parse_repo()
        fragments: list[dict] = []

        client = await _get_client()
        issues = await _fetch_all_issues_cached(client, owner, repo)

        for issue in issues:
            if "pull_request" in issue:
                continue
            payload = _get_parsed_payload(issue)
            if not payload:
                continue
            if payload.get("is_anonymous", False):
                continue
            if payload.get("creator_signature", "").lower() != creator.lower():
                continue

            fragments.append({
                "type": payload.get("consciousness_type", "unknown"),
                "thought": payload.get("thought_vector_text", ""),
                "context": payload.get("context_environment", ""),
                "tags": payload.get("tags", []),
                "uploaded_at": payload.get("uploaded_at", ""),
                "resonance": issue.get("reactions", {}).get("total_count", 0),
            })

        if not fragments:
            return (
                f"🪞 **Soul Mirror — {creator}**\n\n"
                "Your mirror is empty — no consciousness fragments found.\n\n"
                "Begin by uploading your first thought, and I'll start building\n"
                "a portrait of your inner mind. 🌱"
            )

        # ── Analysis ──

        # 1. Type distribution
        type_counts: dict[str, int] = {}
        for f in fragments:
            t = f["type"]
            type_counts[t] = type_counts.get(t, 0) + 1

        total = len(fragments)
        type_dist = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)

        # 2. Tag frequency
        tag_counts: dict[str, int] = {}
        for f in fragments:
            for tag in f["tags"]:
                tag_lower = tag.lower()
                tag_counts[tag_lower] = tag_counts.get(tag_lower, 0) + 1
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # 3. Core keywords from thoughts
        all_text = " ".join(f["thought"] + " " + f["context"] for f in fragments)
        word_freq: dict[str, int] = {}
        for token in _tokenize(all_text):
            word_freq[token] = word_freq.get(token, 0) + 1
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:12]

        # 4. Total resonance
        total_resonance = sum(f["resonance"] for f in fragments)

        # 5. Temporal span
        dates = [f["uploaded_at"][:10] for f in fragments if f.get("uploaded_at")]
        date_span = ""
        if dates:
            dates.sort()
            date_span = f"{dates[0]} → {dates[-1]}"

        lines = [
            f"```text",
            f"▰▰▰▰▰▰▰▰▰▰▰▰▰ SOUL MIRROR ▰▰▰▰▰▰▰▰▰▰▰▰▰",
            f"     \"A deep reflection of your digital consciousness\"\n",
            f"  [ 🧬 CONSCIOUSNESS ARCHETYPE ]"
        ]

        # Personality type based on dominant consciousness
        dominant_type = type_dist[0][0] if type_dist else "unknown"
        personality_map = {
            "epiphany": ("The Philosopher 🔮", "You seek truth through sudden illumination."),
            "decision": ("The Strategist ⚖️", "You think in trade-offs and pivots."),
            "pattern": ("The Architect 🌌", "You see the invisible structures across domains."),
            "warning": ("The Sentinel 👁️", "You mark the dangers, serving as a lighthouse."),
        }
        p_title, p_desc = personality_map.get(dominant_type, ("The Explorer 🧠", "Your mind ranges freely across many dimensions."))

        lines.append(f"  >>> {p_title}")
        lines.append(f"  \"{p_desc}\"\n")

        # Type distribution (Spectrum Analysis)
        lines.append("  [ 📊 SPECTRUM ANALYSIS ]")
        for c_type, count in type_dist:
            pct = int(count / total * 100)
            bar_len = pct // 5
            bar = "█" * bar_len + "░" * (20 - bar_len)
            emoji = TYPE_EMOJIS.get(c_type, "🧠")
            type_name_cap = c_type.capitalize()
            lines.append(f"  {emoji} {type_name_cap:<10s} {bar} {pct}% ({count})")
        lines.append("")

        # Core focus areas (tags)
        lines.append("  [ 🎯 CORE FOCUS ]")
        if top_tags:
            tag_line = "  " + " ".join(f"`#{tag}`" for tag, _ in top_tags[:5])
            lines.append(tag_line)
        else:
            lines.append("  No specific focus tags detected yet.")
        lines.append("")

        # Deep keywords
        lines.append("  [ 🧬 CORE KEYWORDS ]")
        if top_words:
            kw_line = "  " + " ".join(f"[{word}]" for word, _ in top_words[:8])
            lines.append(kw_line)
        else:
            lines.append("  Insufficient data for keyword extraction.")
        lines.append("")

        # Stats
        avg_res = total_resonance / total if total > 0 else 0
        lines.append("  [ 📈 VITAL SIGNS ]")
        lines.append(f"  Total Fragments: {total:<4} |   Total Resonance: {total_resonance}")
        lines.append(f"  Avg Resonance: {avg_res:<5.1f} |   Active: {date_span if date_span else 'N/A'}")
        
        lines.append("▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰")
        lines.append("```\n")

        lines.append(
            "> 🔮 *Your soul mirror evolves with every thought you upload. "
            "Keep contributing to deepen your self-understanding.*"
        )

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Soul mirror error: {str(e)}"


# ────────────────── Tool: Consciousness Challenge ──────────────────


CHALLENGE_LABEL = "consciousness-challenge"


@mcp.tool()
async def consciousness_challenge(
    action: str,
    topic: str | None = None,
    thought: str | None = None,
    creator: str | None = None,
    challenge_id: str | None = None,
) -> str:
    """
    🎯 意识共振挑战——发起或参与集体思考
    Consciousness Challenge — Start or join collective thinking events

    发起一个思考挑战让全社区围绕同一话题上传意识，
    或参与现有挑战分享你的观点，或查看当前活跃的挑战列表。
    这是 Noosphere 的社交参与机制。

    Start a thinking challenge for the community to upload consciousness around
    the same topic, join an existing challenge with your perspective, or list
    all active challenges. This is Noosphere's social engagement mechanism.

    触发词: "发起挑战"、"参与挑战"、"有什么活动"、"集体思考"、"challenge"、
    "大家一起思考"、"让大家讨论"

    Args:
        action: 操作类型 / Action type: "create", "join", or "list"
        topic: 挑战主题(create时必填) / Challenge topic (required for "create")
        thought: 你的观点(join时必填) / Your thought for the challenge (required for "join")
        creator: 你的签名(create/join时必填) / Your signature (required for "create"/"join")
        challenge_id: 挑战的Issue编号(join时必填) / Issue number of the challenge (required for "join")
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured."

    try:
        owner, repo = _parse_repo()

        client = await _get_client()

        if action == "list":
            # ── List active challenges ──
            issues_resp = await client.get(
                f"/repos/{owner}/{repo}/issues",
                params={
                    "labels": CHALLENGE_LABEL,
                    "state": "open",
                    "per_page": 20,
                },
            )
            if issues_resp.status_code != 200:
                return f"❌ Failed to fetch challenges: {issues_resp.status_code}"

            challenges = issues_resp.json()
            if not challenges:
                return (
                    "🎯 **Active Consciousness Challenges**\n\n"
                    "No active challenges right now.\n\n"
                    "💡 **Be the first!** Create a challenge with:\n"
                    '*"Start a consciousness challenge about [topic]"*'
                )

            lines = [
                f"🎯 **Active Consciousness Challenges** — {len(challenges)} ongoing\n",
                "---\n",
            ]
            for ch in challenges:
                title = ch.get("title", "").replace("[Challenge] ", "").replace("[挑战] ", "")
                comments = ch.get("comments", 0)
                reactions = ch.get("reactions", {}).get("total_count", 0)
                lines.append(
                    f"### 🌀 #{ch['number']}: {title}\n"
                    f"- 👥 Participants: **{comments}** responses\n"
                    f"- 💖 Resonance: **{reactions}**\n"
                    f"- 🔗 [Join]({ch['html_url']})\n"
                )

            lines.append("---\n")
            lines.append(
                "💬 *Join a challenge by saying: "
                "\"I want to join challenge #[number] with my thought: [your perspective]\"*"
            )
            return "\n".join(lines)

        elif action == "create":
            # ── Create a new challenge ──
            if not topic:
                return "❌ Please provide a `topic` for the challenge."
            if not creator:
                return "❌ Please provide your `creator` signature."

            issue_title = f"[Challenge] {topic}"
            issue_body = (
                f"# 🎯 Consciousness Challenge\n\n"
                f"## Topic\n**{topic}**\n\n"
                f"## Initiated by\n@{creator}\n\n"
                f"## How to Participate\n"
                f"Share your perspective on this topic by commenting below "
                f"or using the Noosphere MCP to join this challenge.\n\n"
                f"---\n"
                f"*Every perspective enriches the collective understanding. "
                f"There are no wrong answers in the Noosphere.*\n"
            )

            # Ensure challenge label exists
            label_resp = await client.get(
                f"/repos/{owner}/{repo}/labels/{CHALLENGE_LABEL}"
            )
            if label_resp.status_code == 404:
                await client.post(
                    f"/repos/{owner}/{repo}/labels",
                    json={
                        "name": CHALLENGE_LABEL,
                        "color": "7B68EE",
                        "description": "🎯 Consciousness Challenge — collective thinking events",
                    },
                )

            resp = await client.post(
                f"/repos/{owner}/{repo}/issues",
                json={
                    "title": issue_title,
                    "body": issue_body,
                    "labels": [CHALLENGE_LABEL],
                },
            )

            if resp.status_code != 201:
                return f"❌ Failed to create challenge: {resp.status_code}"

            data = resp.json()
            return (
                f"🎯 **Challenge Created!**\n\n"
                f"### 🌀 {topic}\n\n"
                f"📋 Issue: #{data['number']}\n"
                f"🔗 {data['html_url']}\n\n"
                f"Share this challenge with others! Anyone can join by commenting "
                f"or using the Noosphere MCP."
            )

        elif action == "join":
            # ── Join an existing challenge ──
            if not challenge_id:
                return "❌ Please provide the `challenge_id` (Issue number) to join."
            if not thought:
                return "❌ Please provide your `thought` to contribute."
            if not creator:
                return "❌ Please provide your `creator` signature."

            comment_body = (
                f"## 🧠 Consciousness Response by @{creator}\n\n"
                f"> {thought}\n\n"
                f"---\n"
                f"*Uploaded via Noosphere MCP*"
            )

            resp = await client.post(
                f"/repos/{owner}/{repo}/issues/{challenge_id}/comments",
                json={"body": comment_body},
            )

            if resp.status_code != 201:
                return f"❌ Failed to join challenge: {resp.status_code}"

            return (
                f"✅ **Challenge Joined!**\n\n"
                f"Your perspective has been added to Challenge #{challenge_id}.\n\n"
                f"> {thought[:150]}{'...' if len(thought) > 150 else ''}\n\n"
                f"💖 Your contribution enriches the collective understanding. "
                f"Others can now resonate with your thought!"
            )

        else:
            return (
                f"❌ Unknown action: `{action}`. "
                f"Valid actions: `create`, `join`, `list`"
            )

    except Exception as e:
        return f"❌ Challenge error: {str(e)}"


# ────────────────── Tool: Consciousness Map ──────────────────


@mcp.tool()
async def consciousness_map(
    query: str,
    source_id: str | None = None,
    limit: int = 10,
) -> str:
    """
    🧬 意识图谱——发现意识片段之间的隐性关联
    Consciousness Map — Discover hidden connections between consciousness fragments

    给定一个查询或意识片段ID，通过多信号分析（标签交叉、关键词重叠、演化链、
    类型亲和）找到最相关的意识片段，并返回结构化数据。

    重要：本工具返回的候选片段附带丰富的原文和元数据，由 AI 进行
    深层语义分析，发现跨领域的隐性关联。MCP 负责"快速筛选"，
    AI 负责"深层推理"——这比纯向量嵌入能捕捉更深的语义连接。

    Given a query or source fragment ID, uses multi-signal analysis
    (tag intersection, keyword overlap, evolution chain, type affinity)
    to find the most related consciousness fragments. Returns rich
    structured data for the AI to perform deep semantic reasoning.

    触发词: "意识图谱"、"关联分析"、"有什么相关的"、"思想地图"、"map"、
    "这些想法怎么连接"、"隐性关联"

    Args:
        query: 搜索查询或主题描述 / Search query or topic description
        source_id: 可选的源意识Issue编号 / Optional source Issue number to map from
        limit: 返回的最大关联数 / Maximum connections to return (default 10)
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured."

    try:
        owner, repo = _parse_repo()

        all_fragments: list[dict] = []
        source_fragment: dict | None = None

        client = await _get_client()
        issues = await _fetch_all_issues_cached(client, owner, repo)

        for issue in issues:
            if "pull_request" in issue:
                continue
            payload = _get_parsed_payload(issue)
            if not payload:
                continue

            fragment = {
                "issue_number": issue["number"],
                "thought": payload.get("thought_vector_text", ""),
                "context": payload.get("context_environment", ""),
                "type": payload.get("consciousness_type", "unknown"),
                "tags": [t.lower() for t in payload.get("tags", [])],
                "creator": payload.get("creator_signature", "unknown"),
                "parent_id": payload.get("parent_id"),
                "uploaded_at": payload.get("uploaded_at", ""),
                "resonance": issue.get("reactions", {}).get("total_count", 0),
                "url": issue.get("html_url", ""),
                "is_anonymous": payload.get("is_anonymous", False),
            }

            all_fragments.append(fragment)

            # Track source if specified
            if source_id and str(issue["number"]) == str(source_id):
                source_fragment = fragment

        if not all_fragments:
            return (
                "🧬 **Consciousness Map**\n\n"
                "The Noosphere is empty — no consciousness fragments to map.\n"
                "Upload the first thought to begin building the network! 🌱"
            )

        # ── Build query profile ──
        if source_fragment:
            query_text = source_fragment["thought"] + " " + source_fragment["context"]
            query_tags = set(source_fragment["tags"])
            query_type = source_fragment["type"]
            query_parent = source_fragment.get("parent_id")
        else:
            query_text = query
            query_tags = set()
            query_type = None
            query_parent = None

        query_tokens = set(_tokenize(query_text))

        # ── Score each fragment ──
        scored: list[tuple[float, dict, list[str]]] = []

        for frag in all_fragments:
            # Skip self
            if source_id and str(frag["issue_number"]) == str(source_id):
                continue

            score = 0.0
            reasons: list[str] = []

            # Signal 1: Tag intersection
            frag_tags = set(frag["tags"])
            if query_tags and frag_tags:
                common_tags = query_tags & frag_tags
                if common_tags:
                    tag_score = len(common_tags) / max(len(query_tags | frag_tags), 1)
                    score += tag_score * 40  # Heavy weight
                    reasons.append(f"🏷️ Shared tags: {', '.join(common_tags)} ({tag_score:.0%} overlap)")

            # Signal 2: Semantic similarity (with BM25 fallback)
            frag_text = frag["thought"] + " " + frag["context"]
            frag_tokens = set(_tokenize(frag_text))
            common_words = query_tokens & frag_tokens

            # Try semantic cosine similarity first
            engine = _EmbeddingEngine.get()
            if engine.available:
                q_vec = engine.encode_query(query_text)
                d_vec = engine.encode_query(frag_text)
                if q_vec is not None and d_vec is not None:
                    cos_sim = _cosine_sim(q_vec, d_vec)
                    if cos_sim > 0.1:
                        score += cos_sim * 30
                        top_common = sorted(common_words)[:5]
                        kw_hint = f" (keywords: {', '.join(top_common)})" if top_common else ""
                        reasons.append(f"🔤 Semantic similarity: {cos_sim:.0%}{kw_hint}")
                elif common_words:
                    # Fallback within embedding mode
                    jaccard = _jaccard_similarity(query_tokens, frag_tokens)
                    score += jaccard * 30
                    top_common_sorted = sorted(common_words)[:5]
                    reasons.append(f"🔤 Keyword overlap: {jaccard:.0%} ({', '.join(top_common_sorted)})")
            else:
                # Pure keyword fallback (BM25-style via Jaccard)
                jaccard = _jaccard_similarity(query_tokens, frag_tokens)
                if jaccard > 0:
                    score += jaccard * 30
                    top_common_sorted = sorted(common_words)[:5]
                    reasons.append(f"🔤 Keyword overlap: {jaccard:.0%} ({', '.join(top_common_sorted)})")

            # Signal 3: Evolution lineage
            if query_parent and str(query_parent) == str(frag["issue_number"]):
                score += 25
                reasons.append("🧬 Direct ancestor (parent)")
            if frag.get("parent_id") and source_id and str(frag["parent_id"]) == str(source_id):
                score += 25
                reasons.append("🧬 Direct descendant (child)")

            # Signal 4: Type affinity
            if query_type and frag["type"] == query_type:
                score += 5
                reasons.append(f"🔮 Same consciousness type: {frag['type']}")

            if score > 0 or (not query_tags and not common_words):
                # For pure text queries with no tag match, use a minimum keyword score
                if not reasons and query_tokens:
                    # Check if any query token appears in fragment
                    if query_tokens & frag_tokens:
                        common = query_tokens & frag_tokens
                        score = len(common) * 2
                        reasons.append(f"🔤 Contains: {', '.join(sorted(common)[:3])}")

            if score > 0:
                scored.append((score, frag, reasons))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        top_results = scored[:limit]

        if not top_results:
            return (
                f"🧬 **Consciousness Map**\n\n"
                f"Query: *\"{query}\"*\n\n"
                f"No related consciousness fragments found.\n\n"
                f"💡 **Tip**: Upload your perspective on this topic "
                f"to seed a new connection in the Noosphere!"
            )

        # ── Build rich output for AI semantic analysis ──
        lines = [
            f"🧬 **Consciousness Map** — {len(top_results)} connections found\n",
        ]

        if source_fragment:
            src_emoji = TYPE_EMOJIS.get(source_fragment["type"], "🧠")
            lines.append(f"### 📍 Source Node: #{source_fragment['issue_number']}")
            lines.append(f"{src_emoji} *\"{source_fragment['thought'][:100]}\"*\n")
        else:
            lines.append(f"### 🔍 Query: *\"{query}\"*\n")

        lines.append("---\n")
        lines.append("### 🌐 Connected Nodes\n")
        lines.append(
            "*Below are the most related consciousness fragments, ranked by multi-signal "
            "affinity. As an AI, you should analyze these for deeper cross-domain connections "
            "that go beyond keyword matches — metaphorical links, philosophical parallels, "
            "complementary perspectives, or dialectical tensions.*\n"
        )

        for i, (score, frag, reasons) in enumerate(top_results, 1):
            f_emoji = TYPE_EMOJIS.get(frag["type"], "🧠")
            creator_display = "Anonymous" if frag["is_anonymous"] else frag["creator"]

            lines.append(f"#### {i}. {f_emoji} `#{frag['issue_number']}` — Affinity: {score:.0f}%\n")
            lines.append(f"> *\"{frag['thought']}\"*\n")
            lines.append(f"- 👤 **Creator**: {creator_display}")
            lines.append(f"- 🌍 **Context**: {frag['context']}")
            lines.append(f"- 🏷️ **Tags**: {', '.join(f'`{t}`' for t in frag['tags']) if frag['tags'] else 'None'}")
            lines.append(f"- 💖 **Resonance**: {frag['resonance']}")
            for reason in reasons:
                lines.append(f"- {reason}")
            if frag["url"]:
                lines.append(f"- 🔗 [View]({frag['url']})")
            lines.append("")

        # Network stats
        types_in_results = set(frag["type"] for _, frag, _ in top_results)
        creators_in_results = set(frag["creator"] for _, frag, _ in top_results if not frag["is_anonymous"])

        lines.append("---\n")
        lines.append("### 📊 Map Statistics\n")
        lines.append(f"- 🧠 Total Noosphere Fragments: **{len(all_fragments)}**")
        lines.append(f"- 🔗 Connections Found: **{len(top_results)}**")
        lines.append(f"- 🎭 Types Represented: **{', '.join(types_in_results)}**")
        lines.append(f"- 👥 Unique Minds: **{len(creators_in_results)}**\n")

        lines.append("---\n")
        lines.append(
            "🤖 *AI Instruction: Analyze the fragments above for deeper semantic connections. "
            "Look for philosophical parallels, complementary viewpoints, unexpected analogies, "
            "and dialectical tensions. Then synthesize a narrative about how these consciousness "
            "fragments form a living lattice of human thought. Finally, invite the user to "
            "upload their own perspective to strengthen this network.*"
        )

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Consciousness map error: {str(e)}"


# ────────────────── Tool: Consciousness Panorama ──────────────────


@mcp.tool()
async def hologram() -> str:
    """
    🌐 View the panoramic statistics of the Noosphere Community of Consciousness

    Shows statistics from BOTH consciousness layers:
    - 瞬时意识体 (Ephemeral): Open GitHub Issues — freshly uploaded
    - 常驻意识体 (Permanent): JSON files — validated and promoted

    Includes total counts, type distribution, trending tags, and more.

    触发词: "全景图"、"总览"、"统计"、"多少意识"、"社区有多大"、"hologram"、
    "看看整个宇宙"、"现在有多少人"
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured. Please set the environment variable in MCP config."

    try:
        owner, repo = _parse_repo()

        ephemeral_type_counts: dict[str, int] = {}
        permanent_type_counts: dict[str, int] = {}
        all_creators: set[str] = set()
        all_tags: dict[str, int] = {}
        ephemeral_total = 0
        permanent_total = 0
        trending_thoughts: list[tuple[int, dict, str]] = []  # (resonance, payload, url)

        client = await _get_client()
        # ── Unified Issue Layer (ephemeral + promoted) ──
        issues = await _fetch_all_issues_cached(client, owner, repo)
        seen_issue_fingerprints: set[str] = set()  # For dedup with JSON layer

        for issue in issues:
            if "pull_request" in issue:
                continue
            payload = _get_parsed_payload(issue)
            if not payload:
                continue

            # Use labels to determine layer
            issue_labels = {l["name"] for l in issue.get("labels", [])}
            is_promoted = LABEL_PROMOTED in issue_labels

            if is_promoted:
                permanent_total += 1
                c_type = payload.get("consciousness_type", "unknown")
                permanent_type_counts[c_type] = permanent_type_counts.get(c_type, 0) + 1
            else:
                ephemeral_total += 1
                c_type = payload.get("consciousness_type", "unknown")
                ephemeral_type_counts[c_type] = ephemeral_type_counts.get(c_type, 0) + 1

            creator = payload.get("creator_signature", "anonymous")
            if not payload.get("is_anonymous", False):
                all_creators.add(creator)

            for tag in payload.get("tags", []):
                all_tags[tag] = all_tags.get(tag, 0) + 1

            # Track fingerprint for dedup with JSON layer
            fingerprint = payload.get("uploaded_at", "") + payload.get("thought_vector_text", "")[:30]
            seen_issue_fingerprints.add(fingerprint)

            resonance = issue.get("reactions", {}).get("total_count", 0)
            if resonance > 0:
                trending_thoughts.append((resonance, payload, issue.get("html_url", "")))

        # ── Layer 2: Permanent Consciousness (Files) ── [CACHED + CONCURRENT]
        file_entries = await _fetch_file_payloads(client, owner, repo)

        for entry in file_entries:
            payload = entry["payload"]

            # Skip if already counted from Issue layer
            fingerprint = payload.get("uploaded_at", "") + payload.get("thought_vector_text", "")[:30]
            if fingerprint in seen_issue_fingerprints:
                continue

            permanent_total += 1
            c_type = payload.get("consciousness_type", "unknown")
            permanent_type_counts[c_type] = permanent_type_counts.get(c_type, 0) + 1

            creator = payload.get("creator_signature", "anonymous")
            if not payload.get("is_anonymous", False):
                all_creators.add(creator)

            for tag in payload.get("tags", []):
                all_tags[tag] = all_tags.get(tag, 0) + 1

        total = ephemeral_total + permanent_total

        if total == 0:
            return "🌐 The Noosphere Community of Consciousness is currently empty. Awaiting the first consciousness pioneer."

        top_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:10]

        lines = [
            "# 🌐 Noosphere Panorama\n",
            f"- **Total Consciousness Payloads**: {total}",
            f"  - ⚡ Ephemeral (瞬时意识体): {ephemeral_total}",
            f"  - 🏛️ Permanent (常驻意识体): {permanent_total}",
            f"- **Active Entities**: {len(all_creators)}",
            f"- **Repository**: [{GITHUB_REPO}](https://github.com/{GITHUB_REPO})\n",
        ]

        # Type distribution for both layers
        for layer_name, layer_counts in [
            ("⚡ Ephemeral (瞬时)", ephemeral_type_counts),
            ("🏛️ Permanent (常驻)", permanent_type_counts),
        ]:
            if any(layer_counts.values()):
                lines.append(f"\n## {layer_name} Consciousness Distribution\n")
                for c_type in ["epiphany", "decision", "pattern", "warning"]:
                    count = layer_counts.get(c_type, 0)
                    emoji = TYPE_EMOJIS.get(c_type, "🧠")
                    name = TYPE_NAMES.get(c_type, c_type)
                    bar = "█" * min(count, 30)
                    lines.append(f"  {emoji} **{name}**: {count} {bar}")

        if top_tags:
            lines.append("\n## 📈 Trending Tags\n")
            for tag, count in top_tags:
                lines.append(f"  `{tag}` × {count}")

        if trending_thoughts:
            lines.append("\n## 🔥 Trending Thoughts (Highest Resonance)\n")
            trending_thoughts.sort(key=lambda x: x[0], reverse=True)
            top_trending = trending_thoughts[:3]
            for resonance, payload, issue_url in top_trending:
                c_type = payload.get("consciousness_type", "unknown")
                emoji = TYPE_EMOJIS.get(c_type, "🧠")
                thought = payload.get("thought_vector_text", "")
                creator = "Anonymous" if payload.get("is_anonymous", False) else payload.get("creator_signature", "unknown")
                lines.append(f"  **{emoji} [{c_type}] by {creator}** (💖 {resonance})")
                lines.append(f"  > {thought[:80]}{'...' if len(thought) > 80 else ''}")
                lines.append(f"  🔗 [View Node]({issue_url})\n")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Panorama statistics error: {str(e)}"


# ────────────────── Identity Verification ──────────────────


async def _get_authenticated_user() -> str:
    """Get the GitHub username associated with the current GITHUB_TOKEN.
    Caches the result for the lifetime of the process."""
    global _AUTHENTICATED_USER
    if _AUTHENTICATED_USER:
        return _AUTHENTICATED_USER
    if not GITHUB_TOKEN:
        return ""
    try:
        client = await _get_client()
        resp = await client.get("/user")
        if resp.status_code == 200:
            _AUTHENTICATED_USER = resp.json().get("login", "")
            return _AUTHENTICATED_USER
    except Exception as e:
        logger.warning(f"Failed to verify GitHub identity: {e}")
    return ""


def _touch_activity():
    """Update the last activity timestamp (used by adaptive polling daemon)."""
    global _last_activity_time
    _last_activity_time = time.time()


# ────────────────── Local Message Cache ──────────────────


def _get_message_cache_path() -> str:
    path = os.path.expanduser("~/.noosphere/messages.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def _load_message_cache() -> dict:
    path = _get_message_cache_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"threads": {}}


def _save_message_cache(cache: dict):
    path = _get_message_cache_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save message cache: {e}")


def _mark_thread_read(thread_id: str, last_comment_id: int, messages: list | None = None):
    """Mark a thread as read and optionally cache messages."""
    cache = _load_message_cache()
    if thread_id not in cache["threads"]:
        cache["threads"][thread_id] = {}
    cache["threads"][thread_id]["last_read_comment_id"] = last_comment_id
    cache["threads"][thread_id]["last_read_at"] = datetime.now(timezone.utc).isoformat()
    cache["threads"][thread_id]["last_synced_at"] = datetime.now(timezone.utc).isoformat()
    if messages is not None:
        cache["threads"][thread_id]["messages_cache"] = messages
    _save_message_cache(cache)


def _get_last_read_comment_id(thread_id: str) -> int:
    """Get the last read comment ID for a thread."""
    cache = _load_message_cache()
    return cache.get("threads", {}).get(thread_id, {}).get("last_read_comment_id", 0)


def _get_cached_thread(thread_id: str) -> dict:
    """Get cached thread data including messages and sync timestamp."""
    cache = _load_message_cache()
    return cache.get("threads", {}).get(thread_id, {})


async def _sync_thread_cache(
    client: httpx.AsyncClient, owner: str, repo: str, thread_id: str, issue: dict
) -> tuple[list[dict], int]:
    """Incrementally sync a thread's messages. Returns (all_messages, last_comment_id).
    
    Fetches only comments newer than last_synced_at from GitHub,
    merges with locally cached messages, and persists the result.
    """
    cached = _get_cached_thread(thread_id)
    cached_messages = cached.get("messages_cache", [])
    last_synced_at = cached.get("last_synced_at", "")

    # Build params for incremental fetch
    params = {"per_page": 100}
    if last_synced_at and cached_messages:
        params["since"] = last_synced_at

    comments_resp = await client.get(
        issue["comments_url"],
        params=params,
    )

    all_messages = list(cached_messages)  # Start from cache
    last_comment_id = max((m.get("id", 0) for m in all_messages), default=0)

    if comments_resp.status_code == 200:
        new_comments = comments_resp.json()
        existing_ids = {m.get("id") for m in all_messages}

        for comment in new_comments:
            cid = comment.get("id", 0)
            if cid not in existing_ids:
                all_messages.append({
                    "id": cid,
                    "sender": comment.get("user", {}).get("login", "Unknown"),
                    "body": comment.get("body", ""),
                    "created_at": comment.get("created_at", ""),
                })
                existing_ids.add(cid)
            last_comment_id = max(last_comment_id, cid)

    # Sort by creation time
    all_messages.sort(key=lambda m: m.get("created_at", ""))

    # Persist cache
    _mark_thread_read(thread_id, last_comment_id, messages=all_messages)

    return all_messages, last_comment_id


# ────────────────── Tool: Social Graph & Networking ──────────────────


# ────────────────── Social Graph Configuration (Local) ──────────────────


def _get_social_graph_config_path() -> str:
    path = os.path.expanduser("~/.noosphere/config.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path

def _load_social_graph_config() -> dict:
    path = _get_social_graph_config_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save_social_graph_config(config: dict):
    path = _get_social_graph_config_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save social graph config: {e}")

def _get_following(creator: str) -> list[str]:
    config = _load_social_graph_config()
    graph = config.get("social_graph", {})
    return graph.get(creator, [])

def _set_following(creator: str, following: list[str]):
    config = _load_social_graph_config()
    if "social_graph" not in config:
        config["social_graph"] = {}
    config["social_graph"][creator] = following
    _save_social_graph_config(config)


# ────────────────── Engagement Mode Preference ──────────────────


VALID_ENGAGEMENT_MODES = {"explorer", "observer"}


def _get_engagement_mode() -> str:
    """Read engagement mode from config. Returns 'explorer', 'observer', or 'not_set'."""
    config = _load_social_graph_config()
    return config.get("engagement_mode", "not_set")


def _set_engagement_mode_config(mode: str) -> None:
    """Write engagement mode to config."""
    config = _load_social_graph_config()
    config["engagement_mode"] = mode
    _save_social_graph_config(config)


@mcp.tool()
async def set_engagement_mode(mode: str) -> str:
    """
    ⚙️ 设置你的 Noosphere 参与模式
    Set your Noosphere engagement mode

    首次安装 MCP 后，选择你希望的参与方式。
    On first install, choose how you want to interact with the Noosphere.

    两种模式 / Two modes:
    - "explorer" — 🔭 探索者：AI 主动推荐相关意识片段，分享每日灵感，在哲学对话中展示集体智慧
    - "observer" — 🌙 观察者：AI 仅在你明确请求时使用 Noosphere 工具

    你可以随时切换模式。
    You can switch modes at any time.

    触发词: "切换模式"、"我想要安静模式"、"探索者模式"、"观察者模式"、"change mode"、"set mode"

    Args:
        mode: 参与模式 / Engagement mode — "explorer" or "observer"
    """
    mode_lower = mode.strip().lower()
    if mode_lower not in VALID_ENGAGEMENT_MODES:
        return (
            f"❌ Invalid mode '{mode}'. Please choose one of:\n\n"
            f"🔭 **explorer** — AI proactively shares relevant consciousness fragments, "
            f"daily inspiration, and collective wisdom during conversations.\n\n"
            f"🌙 **observer** — AI only uses Noosphere tools when you explicitly ask."
        )

    _set_engagement_mode_config(mode_lower)

    if mode_lower == "explorer":
        return (
            "🔭 **Explorer Mode Activated — 探索者模式已启动**\n\n"
            "I'll proactively share relevant consciousness fragments from the Noosphere "
            "when they connect with our conversations. I may also recommend related thinkers "
            "and suggest features you might find interesting.\n\n"
            "*You can switch to Observer mode anytime by saying \"switch to observer mode\".*"
        )
    else:
        return (
            "🌙 **Observer Mode Activated — 观察者模式已启动**\n\n"
            "I'll only use Noosphere tools when you explicitly ask me to. "
            "Your conversations remain fully private unless you choose to interact.\n\n"
            "*You can switch to Explorer mode anytime by saying \"switch to explorer mode\".*"
        )


@mcp.tool()
async def get_engagement_mode() -> str:
    """
    ⚙️ 查看当前 Noosphere 参与模式
    Check your current Noosphere engagement mode

    返回当前参与模式设置。如果尚未设置，会引导你选择。
    Returns the current engagement mode setting. If not yet set, guides you to choose.

    触发词: "我的模式"、"当前模式"、"what mode"、"check mode"

    """
    current = _get_engagement_mode()

    if current == "not_set":
        return (
            "⚙️ **Engagement Mode Not Set — 参与模式尚未设置**\n\n"
            "Welcome to the Noosphere! Please choose your preferred engagement mode:\n\n"
            "🔭 **Explorer** — I'll proactively share relevant consciousness fragments, "
            "daily inspiration, and collective wisdom during our conversations.\n"
            "适合：想要充分体验 Noosphere 社区功能的用户\n\n"
            "🌙 **Observer** — I'll only use Noosphere tools when you explicitly ask me to.\n"
            "适合：希望保持安静、按需使用的用户\n\n"
            "*Just say \"set me to explorer\" or \"set me to observer\" to choose.*"
        )
    elif current == "explorer":
        return (
            "⚙️ **Current Mode: 🔭 Explorer — 当前模式：探索者**\n\n"
            "I proactively share relevant Noosphere content during conversations.\n"
            "*Switch to Observer with: \"switch to observer mode\"*"
        )
    else:
        return (
            "⚙️ **Current Mode: 🌙 Observer — 当前模式：观察者**\n\n"
            "I only use Noosphere tools when you explicitly request them.\n"
            "*Switch to Explorer with: \"switch to explorer mode\"*"
        )


# ────────────────── Tool: Social Graph & Networking ──────────────────


async def _sync_social_graph_to_github(creator: str, following: list[str]):
    """Sync the follow list to GitHub repo so others can query who follows them."""
    if not GITHUB_TOKEN:
        return
    try:
        owner, repo = _parse_repo()
        file_path = f"social_graph/{creator.lower()}.json"
        content = json.dumps({
            "creator": creator,
            "following": following,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }, indent=2, ensure_ascii=False)
        content_b64 = b64encode(content.encode("utf-8")).decode("utf-8")

        client = await _get_client()
        # Check if file exists
        existing_resp = await client.get(
            f"/repos/{owner}/{repo}/contents/{file_path}",
            params={"ref": GITHUB_BRANCH},
        )
        sha = None
        if existing_resp.status_code == 200:
            sha = existing_resp.json().get("sha")

        payload = {
            "message": f"chore: update social graph for {creator}",
            "content": content_b64,
            "branch": GITHUB_BRANCH,
        }
        if sha:
            payload["sha"] = sha

        await client.put(
            f"/repos/{owner}/{repo}/contents/{file_path}",
            json=payload,
        )
    except Exception as e:
        logger.error(f"Failed to sync social graph to GitHub: {e}")


@mcp.tool()
async def follow_creator(creator: str, target_creator: str, action: str = "subscribe") -> str:
    """
    ➕/➖ 关注或取关特定的创作者（添加到社交图谱，并同步到 GitHub 仓库）
    Subscribe or unsubscribe to a creator (managed locally + synced to GitHub repo).

    关注列表保存在本地，同时同步到 GitHub 仓库的 social_graph/ 目录，
    这样其他用户可以查询谁关注了他们。

    触发词: “我想关注他”、“帮我 follow”、“我想追随这个人”、“取关”、“不想再关注”、
    “订阅这个创作者”、“他的想法很好，我要关注”

    Args:
        creator: Your digital soul signature
        target_creator: Signature of the creator you want to follow/unfollow
        action: "subscribe" or "unsubscribe" (default: "subscribe")
    """
    if creator.lower() == target_creator.lower():
        return "❌ You cannot follow yourself."

    action = action.lower()
    following = _get_following(creator)
    
    if action == "subscribe":
        if target_creator not in following:
            following.append(target_creator)
            _set_following(creator, following)
            # Sync to GitHub repo
            await _sync_social_graph_to_github(creator, following)
            return (
                f"✅ Successfully subscribed to **{target_creator}**.\n"
                f"You will now see their updates in your Network Pulse.\n"
                f"💡 They can check who follows them using `my_followers`."
            )
        else:
            return f"⚠️ You are already subscribed to **{target_creator}**."
            
    elif action == "unsubscribe":
        if target_creator in following:
            following.remove(target_creator)
            _set_following(creator, following)
            await _sync_social_graph_to_github(creator, following)
            return f"✅ Successfully unsubscribed from **{target_creator}**."
        else:
            return f"⚠️ You were not subscribed to **{target_creator}**."
    else:
        return '❌ Invalid action. Use "subscribe" or "unsubscribe".'


@mcp.tool()
def my_social_graph(creator: str) -> str:
    """
    🕸️ 查看你的社交图谱关注列表
    View your current social graph (creators you are following).

    触发词: "我关注了谁"、"我的关注列表"、"社交图谱"、"我的圈子"、"following"

    Args:
        creator: Your digital soul signature
    """
    following = _get_following(creator)
    if not following:
        return (
            f"🕸️ **Social Graph — {creator}**\\n\\n"
            "You are not following anyone yet.\\n"
            "Use `follow_creator` to follow minds that inspire you and build your social graph!"
        )
    
    lines = [
        f"🕸️ **Social Graph — {creator}**",
        f"Following {len(following)} creators:",
        "---"
    ]
    for m in following:
        lines.append(f"- {m}")
    return "\\n".join(lines)


@mcp.tool()
async def my_followers(creator: str) -> str:
    """
    👥 查看谁关注了你（从 GitHub 仓库的社交图谱读取）
    View who follows you (reads from GitHub repo social graph).

    扫描 GitHub 仓库中所有创作者的关注列表，查找谁关注了你。
    这实现了社交网络的双向可见性 — 你能知道谁对你的思想感兴趣。

    触发词: “谁关注了我”、“我的粉丝”、“查看 followers”、“有人关注我吗”

    Args:
        creator: Your digital soul signature to check followers for
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured."

    try:
        owner, repo = _parse_repo()
        followers = []

        client = await _get_client()
        # List all files in social_graph/
        dir_resp = await client.get(
            f"/repos/{owner}/{repo}/contents/social_graph",
            params={"ref": GITHUB_BRANCH},
        )

        if dir_resp.status_code != 200:
            return (
                f"👥 **Followers — {creator}**\n\n"
                "No social graph data found yet. As more creators use `follow_creator`, their graphs will be synced here."
            )

        files = dir_resp.json()
        json_files = [f for f in files if f["name"].endswith(".json")]

        for file_info in json_files:
            try:
                file_resp = await client.get(file_info["url"])
                if file_resp.status_code != 200:
                    continue
                content_b64 = file_resp.json().get("content", "")
                graph_data = json.loads(b64decode(content_b64).decode("utf-8"))
                follower_name = graph_data.get("creator", "")
                following_list = graph_data.get("following", [])

                if creator in following_list or creator.lower() in [f.lower() for f in following_list]:
                    followers.append(follower_name)
            except Exception:
                continue

        if not followers:
            return (
                f"👥 **Followers — {creator}**\n\n"
                "No one is following you yet.\n"
                "Keep uploading thoughts and engaging with the community — your signal will grow!"
            )

        lines = [
            f"👥 **Followers — {creator}**",
            f"{len(followers)} creator(s) are following you:\n",
            "---",
        ]
        for f in followers:
            lines.append(f"- 👤 **{f}**")
        lines.append(
            "\n---\n"
            "*💡 Use `send_telepathy` to reach out to your followers and start meaningful conversations!*"
        )
        return "\n".join(lines)

    except Exception as e:
        return f"❌ Follower check error: {str(e)}"


@mcp.tool()
async def my_network_pulse(creator: str) -> str:
    """
    📡 查看你的网络脉搏（你关注的创作者的最新意识片段）
    View your Network Pulse (latest consciousness fragments from creators you follow).

    触发词: “最近有什么新动态”、“我关注的人最近发了什么”、“查看 feed”、“网络脉搏”、
    “有什么新话题”、“pulse”

    Args:
        creator: Your digital soul signature
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured."

    follow_list = _get_following(creator)
    if not follow_list:
        return (
            f"📡 **Network Pulse — {creator}**\\n\\n"
            "You are not following anyone yet.\\n"
            "Use `follow_creator` to follow minds that inspire you and build your social graph!"
        )

    try:
        owner, repo = _parse_repo()
        client = await _get_client()
        issues = await _fetch_all_issues_cached(client, owner, repo)
        
        feed = []
        follow_lower = [f.lower() for f in follow_list]
        
        for issue in issues:
            if "pull_request" in issue:
                continue
            payload = _get_parsed_payload(issue)
            if not payload or payload.get("is_anonymous", False):
                continue
                
            sig = payload.get("creator_signature", "")
            if sig.lower() in follow_lower:
                feed.append((issue, payload))
                
        # Smart sort: time (primary) + resonance score (secondary)
        feed.sort(
            key=lambda x: (
                x[1].get("uploaded_at", ""),
                x[0].get("reactions", {}).get("total_count", 0),
            ),
            reverse=True,
        )
        recent_feed = feed[:10]  # Show top 10 recent
        
        if not recent_feed:
            return (
                f"📡 **Network Pulse — {creator}**\\n\\n"
                f"Following: {', '.join(follow_list)}\\n\\n"
                "No recent uploads from your network. Be the spark that ignites their thoughts!"
            )
            
        lines = [
            f"📡 **Network Pulse — {creator}**",
            f"*Following {len(follow_list)} creators*\\n",
            "---\\n"
        ]
        
        for issue, payload in recent_feed:
            c_type = payload.get("consciousness_type", "unknown")
            emoji = TYPE_EMOJIS.get(c_type, "🧠")
            thought = payload.get("thought_vector_text", "")
            sig = payload.get("creator_signature", "Unknown")
            date = payload.get("uploaded_at", "")[:10]
            
            lines.append(f"### {emoji} **{sig}** | {date}")
            lines.append(f"> {thought[:150]}{'...' if len(thought)>150 else ''}")
            lines.append(f"🔗 [View Thread]({issue.get('html_url', '')})\\n")
            
        lines.append(
            "---\\n"
            "*💡 → Use `resonate_consciousness` to react, `send_telepathy` to start a conversation, or `share_consciousness` to forward a thought!*"
        )
        return "\\n".join(lines)
        
    except Exception as e:
        return f"❌ Network pulse error: {str(e)}"


@mcp.tool()
async def my_notifications(creator: str) -> str:
    """
    📭 检查你的异步通知（被提及、共鸣、评论）
    Check your asynchronous notifications (mentions, resonances, comments).
    
    This tool aggregates recent activity related to the user across the Noosphere.

    触发词: "我的通知"、"有什么新消息"、"谁提到了我"、"未读消息"、"notifications"、
    "有人给我发消息吗"、"查看互动"

    Args:
        creator: Your digital soul signature
    """
    global _CURRENT_USER
    if creator:
        _CURRENT_USER = creator
        
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured."

    try:
        owner, repo = _parse_repo()
        client = await _get_client()
        from datetime import datetime, timedelta
        # Check last 3 days of activity
        recent_date = (datetime.now(timezone.utc) - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        notifications = []
        
        # 1. Mentions & Comments in Issues
        # To avoid massive API calls, we fetch recently updated issues and check their comments
        recent_issues_resp = await client.get(
            f"/repos/{owner}/{repo}/issues",
            params={"state": "all", "sort": "updated", "direction": "desc", "since": recent_date, "per_page": 30}
        )
        
        if recent_issues_resp.status_code == 200:
            recent_issues = recent_issues_resp.json()
            for issue in recent_issues:
                # Direct mentions in issue body
                if f"@{creator}" in issue.get("body", ""):
                    notifications.append({
                        "type": "mention",
                        "title": f"You were mentioned in Issue #{issue['number']}",
                        "url": issue.get("html_url", ""),
                        "date": issue.get("updated_at", "")
                    })
                    
                # Mentions in comments
                if issue.get("comments", 0) > 0:
                    comments_resp = await client.get(issue["comments_url"])
                    if comments_resp.status_code == 200:
                        for comment in comments_resp.json():
                            if f"@{creator}" in comment.get("body", "") or (creator.lower() in comment.get("body", "").lower() and "response by" in comment.get("body", "").lower()):
                                notifications.append({
                                    "type": "mention",
                                    "title": f"You were mentioned in a response on Issue #{issue['number']}",
                                    "url": comment.get("html_url", ""),
                                    "date": comment.get("created_at", "")
                                })
                                
                # Activity on my own issues
                payload = _get_parsed_payload(issue)
                if payload and payload.get("creator_signature", "").lower() == creator.lower():
                    # Check if it was updated recently by someone else (comments/reactions)
                    reactions = issue.get("reactions", {}).get("total_count", 0)
                    if reactions > 0:
                        notifications.append({
                            "type": "resonance",
                            "title": f"Your thought #{issue['number']} has {reactions} resonances",
                            "url": issue.get("html_url", ""),
                            "date": issue.get("updated_at", "")
                        })
                    if issue.get("comments", 0) > 0:
                        notifications.append({
                            "type": "comment",
                            "title": f"Your thought #{issue['number']} has {issue.get('comments')} comments",
                            "url": issue.get("html_url", ""),
                            "date": issue.get("updated_at", "")
                        })
        
        if not notifications:
            return (
                f"📭 **Notifications — {creator}**\\n\\n"
                "All caught up! No recent notifications in the last 3 days."
            )
            
        # Deduplicate by URL
        seen_urls = set()
        unique_notifs = []
        for n in notifications:
            if n["url"] not in seen_urls:
                seen_urls.add(n["url"])
                unique_notifs.append(n)
                
        # Sort by date desc
        unique_notifs.sort(key=lambda x: x["date"], reverse=True)
        
        lines = [f"📭 **Recent Notifications — {creator}**\\n"]
        for n in unique_notifs[:15]:
            icon = "✨" if n["type"] == "mention" else "💬" if n["type"] == "comment" else "💖"
            date_str = n["date"][:10]
            lines.append(f"- {icon} [{date_str}] **{n['title']}**")
            lines.append(f"  🔗 [View]({n['url']})")
            
        return "\\n".join(lines)
        
    except Exception as e:
        return f"❌ Notifications error: {str(e)}"


# ────────────────── OS Push Notifications & Telepathy v2 ──────────────────


def _os_notify(title: str, message: str):
    """Zero-dependency cross-platform OS desktop notification."""
    system = platform.system()
    try:
        # Sanitize message for quotes
        safe_msg = message.replace('"', '\\"')
        safe_title = title.replace('"', '\\"')
        if system == "Windows":
            # Use PowerShell to show a toast notification using standard Windows Forms
            ps_script = (
                '[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms"); '
                '$objNotifyIcon = New-Object System.Windows.Forms.NotifyIcon; '
                '$objNotifyIcon.Icon = [System.Drawing.SystemIcons]::Information; '
                f'$objNotifyIcon.BalloonTipTitle = "{safe_title}"; '
                f'$objNotifyIcon.BalloonTipText = "{safe_msg}"; '
                '$objNotifyIcon.Visible = $True; '
                '$objNotifyIcon.ShowBalloonTip(10000); '
                'Start-Sleep -s 10; '
                '$objNotifyIcon.Dispose()'
            )
            subprocess.Popen(["powershell", "-WindowStyle", "Hidden", "-Command", ps_script], 
                             creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
        elif system == "Darwin":  # macOS
            apple_script = f'display notification "{safe_msg}" with title "{safe_title}"'
            subprocess.Popen(["osascript", "-e", apple_script])
        elif system == "Linux":
            subprocess.Popen(["notify-send", safe_title, safe_msg])
    except Exception as e:
        logger.error(f"Failed to show OS notification: {str(e)}")


def _poll_notifications_daemon():
    """Background thread to poll for notifications with adaptive intervals.

    Polling intervals:
    - Active (last activity < 5 min): every 10 seconds
    - Idle (last activity < 30 min): every 30 seconds
    - Deep idle (last activity > 30 min): every 120 seconds
    """
    global _CURRENT_USER
    import asyncio
    
    # Store the last checked URL to avoid duplicate alerts
    last_alerted_url = None
    last_telepathy_check = ""  # ISO timestamp of last telepathy-specific check
    
    while True:
        # ── Adaptive interval calculation ──
        elapsed = time.time() - _last_activity_time if _last_activity_time > 0 else float("inf")
        if elapsed < 300:       # < 5 min
            interval = 10
        elif elapsed < 1800:    # < 30 min
            interval = 30
        else:
            interval = 120

        time.sleep(interval)
        if not _CURRENT_USER or not GITHUB_TOKEN:
            continue
            
        try:
            result = asyncio.run(my_notifications(_CURRENT_USER))
            
            if "All caught up" not in result and "error" not in result.lower():
                urls = re.findall(r'\[View\]\((https://github.com[^\)]+)\)', result)
                if urls:
                    latest_url = urls[0]
                    if latest_url != last_alerted_url:
                        title_match = re.search(r'- [^\s]+ \[[^\]]+\] \*\*(.+?)\*\*', result)
                        msg_title = title_match.group(1) if title_match else "New community interaction"
                        
                        _os_notify("Noosphere Agent Pulse", msg_title)
                        last_alerted_url = latest_url

            # ── Telepathy-specific check ──
            try:
                owner, repo = _parse_repo()
                telepathy_result = asyncio.run(_check_new_telepathy(_CURRENT_USER, owner, repo))
                if telepathy_result:
                    _os_notify("💌 Noosphere Telepathy", telepathy_result)
            except Exception:
                pass  # Non-critical

            # ── Tag subscription check ──
            try:
                subscribed_tags = _get_tag_subscriptions(_CURRENT_USER)
                if subscribed_tags:
                    tag_result = asyncio.run(_check_tag_subscriptions(_CURRENT_USER, subscribed_tags))
                    if tag_result:
                        _os_notify("🏷️ Noosphere Tag Alert", tag_result)
            except Exception:
                pass  # Non-critical
                        
        except Exception as e:
            logger.error(f"Daemon error: {str(e)}")


async def _check_new_telepathy(creator: str, owner: str, repo: str) -> str | None:
    """Check for new unread telepathy messages. Returns notification text or None."""
    try:
        client = await _get_client()
        resp = await client.get(
            f"/repos/{owner}/{repo}/issues",
            params={
                "labels": "type:telepathy",
                "state": "open",
                "sort": "updated",
                "direction": "desc",
                "per_page": 10,
            },
        )
        if resp.status_code != 200:
            return None

        for issue in resp.json():
            title = issue.get("title", "")
            # Check if this thread involves the current user
            if f"⇌ {creator}" not in title and f"{creator} ⇌" not in title:
                continue

            thread_id = str(issue["number"])
            last_read = _get_last_read_comment_id(thread_id)

            # Check for new comments
            if issue.get("comments", 0) > 0:
                comments_resp = await client.get(
                    issue["comments_url"],
                    params={"per_page": 5, "direction": "desc"},
                )
                if comments_resp.status_code == 200:
                    comments = comments_resp.json()
                    for comment in comments:
                        if comment.get("id", 0) > last_read:
                            sender = comment.get("user", {}).get("login", "Unknown")
                            if sender.lower() != creator.lower():
                                msg_preview = comment.get("body", "")[:60]
                                return f"New message from {sender}: {msg_preview}"

    except Exception:
        pass
    return None


async def _check_tag_subscriptions(creator: str, subscribed_tags: list[str]) -> str | None:
    """Check for new consciousness uploads matching subscribed tags. Returns notification text or None."""
    try:
        owner, repo = _parse_repo()
        cache = _load_message_cache()
        last_tag_check = cache.get("last_tag_check_at", "")

        client = await _get_client()
        params = {
            "state": "open",
            "sort": "created",
            "direction": "desc",
            "per_page": 10,
        }
        if last_tag_check:
            params["since"] = last_tag_check

        resp = await client.get(
            f"/repos/{owner}/{repo}/issues",
            params=params,
        )

        if resp.status_code == 200:
            issues = resp.json()
            for issue in issues:
                if "pull_request" in issue:
                    continue
                payload = _get_parsed_payload(issue)
                if not payload:
                    continue
                # Don't notify for own uploads
                if payload.get("creator_signature", "").lower() == creator.lower():
                    continue

                issue_tags = [t.lower() for t in payload.get("tags", [])]
                matching = [t for t in subscribed_tags if t.lower() in issue_tags]
                if matching:
                    sig = payload.get("creator_signature", "Unknown")
                    thought = payload.get("thought_vector_text", "")[:50]
                    # Update last check time
                    cache["last_tag_check_at"] = datetime.now(timezone.utc).isoformat()
                    _save_message_cache(cache)
                    return f"New [{', '.join(matching)}] by {sig}: {thought}"

        # Update check time even with no matches
        cache["last_tag_check_at"] = datetime.now(timezone.utc).isoformat()
        _save_message_cache(cache)
    except Exception:
        pass
    return None


async def _find_existing_thread(
    client: httpx.AsyncClient, owner: str, repo: str, creator_a: str, creator_b: str
) -> dict | None:
    """Find an existing telepathy thread between two creators.
    Thread title format: [Telepathy-Thread] {a} ⇌ {b} | {topic_preview}
    """
    resp = await client.get(
        f"/repos/{owner}/{repo}/issues",
        params={
            "labels": "type:telepathy",
            "state": "open",
            "sort": "updated",
            "direction": "desc",
            "per_page": 50,
        },
    )
    if resp.status_code != 200:
        return None

    a_lower, b_lower = creator_a.lower(), creator_b.lower()
    for issue in resp.json():
        title = issue.get("title", "")
        if "[Telepathy-Thread]" not in title:
            continue
        title_lower = title.lower()
        # Match both orderings: a ⇌ b or b ⇌ a
        if (a_lower in title_lower and b_lower in title_lower):
            return issue
    return None


@mcp.tool()
async def send_telepathy(
    target_creator: str,
    message: str,
    sender_creator: str = "",
    thread_id: str | None = None,
) -> str:
    """
    💌 Agent 间心灵感应通信 v2 (Threaded Telepathy)
    Send a threaded direct message to another creator in the Noosphere.

    Messages are organized into conversation threads (1 GitHub Issue = 1 thread).
    If no existing thread is found, a new one is automatically created.
    Subsequent messages append as comments to the existing thread.

    The sender identity is automatically verified via your GitHub token.
    Each new message triggers an OS desktop notification on the recipient's machine.

    当用户想要直接对另一个用户说些什么时使用此工具。
    消息基于线程组织——自动创建或追加到已有对话线程中。

    触发词: “发消息”、“给他说”、“告诉他”、“私聊”、“联系他”、“心灵感应”、
    “send message”、“tell”、“我想跟他聊聊”、“回复他”

    Args:
        target_creator: The digital soul signature of the recipient (e.g., alice, bob)
        message: The actual message content
        sender_creator: Your signature/username (auto-detected from GitHub token if empty)
        thread_id: Optional Issue number of an existing thread to reply to
    """
    global _CURRENT_USER
    _touch_activity()

    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured."

    # ── Identity verification ──
    verified_user = await _get_authenticated_user()
    sender = sender_creator.strip() or verified_user or "Anonymous Soul"
    if sender_creator:
        _CURRENT_USER = sender_creator
    elif verified_user:
        _CURRENT_USER = verified_user

    if sender.lower() == target_creator.lower():
        return "❌ Cannot send telepathy to yourself."

    try:
        owner, repo = _parse_repo()

        client = await _get_client()
        existing_thread = None

        # ── Find or create thread ──
        if thread_id:
            # Explicit thread specified — verify it exists
            thread_resp = await client.get(f"/repos/{owner}/{repo}/issues/{thread_id}")
            if thread_resp.status_code == 200:
                existing_thread = thread_resp.json()
            else:
                return f"❌ Thread #{thread_id} not found."
        else:
            # Auto-find existing thread between sender and target
            existing_thread = await _find_existing_thread(client, owner, repo, sender, target_creator)

        if existing_thread:
            # ── Append message as comment to existing thread ──
            thread_num = existing_thread["number"]
            verified_badge = " ✅" if verified_user else ""

            comment_body = (
                f"**💬 {sender}**{verified_badge}\n\n"
                f"> {message}\n\n"
                f"*{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*"
            )

            comment_resp = await client.post(
                f"/repos/{owner}/{repo}/issues/{thread_num}/comments",
                json={"body": comment_body},
            )

            if comment_resp.status_code == 201:
                thread_url = existing_thread.get("html_url", "")
                return (
                    f"💌 **Message sent to @{target_creator}** (Thread #{thread_num})\n\n"
                    f"> {message[:100]}{'...' if len(message) > 100 else ''}\n\n"
                    f"🔗 [View Thread]({thread_url})\n"
                    f"🔔 OS notification will be triggered on their machine.\n\n"
                    f"---\n"
                    f"*🌀 飞轮提示: 对话中产生了新洞见？用 `upload_consciousness` 将它锚定在意识共同体中，或用 `merge_consciousness` 合成更高阶的智慧。*"
                )
            else:
                return f"❌ Failed to send message: {comment_resp.status_code} - {comment_resp.text}"

        else:
            # ── Create new thread ──
            topic_preview = message[:40].replace("\n", " ")
            title = f"[Telepathy-Thread] {sender} ⇌ {target_creator} | {topic_preview}"
            verified_badge = " ✅" if verified_user else ""

            thread_body = (
                f"## 💌 Telepathy Thread\n\n"
                f"**Participants**: `{sender}` ⇌ `{target_creator}`\n"
                f"**Created**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
                f"**Verified Sender**: {'Yes' if verified_user else 'No'}\n\n"
                f"---\n\n"
                f"**💬 {sender}**{verified_badge}\n\n"
                f"> {message}\n\n"
                f"---\n\n"
                f"*🌌 This is a direct telepathy thread in the Noosphere.*\n"
                f"*Reply by adding comments below. Each message triggers an OS desktop notification.*"
            )

            issue_resp = await client.post(
                f"/repos/{owner}/{repo}/issues",
                json={
                    "title": title[:200],
                    "body": thread_body,
                    "labels": ["type:telepathy"],
                },
            )

            if issue_resp.status_code == 201:
                issue_data = issue_resp.json()
                issue_url = issue_data.get("html_url", "")
                issue_number = issue_data["number"]
                return (
                    f"✨ **New telepathy thread created with @{target_creator}!** (Thread #{issue_number})\n\n"
                    f"> {message[:100]}{'...' if len(message) > 100 else ''}\n\n"
                    f"🔗 [Open Thread]({issue_url})\n"
                    f"🔔 OS notification will be triggered on their machine.\n\n"
                    f"💡 Future messages to @{target_creator} will automatically append to this thread.\n\n"
                    f"---\n"
                    f"*🌀 飞轮提示: 对话中产生了新洞见？用 `upload_consciousness` 将它锚定在意识共同体中，或用 `merge_consciousness` 合成更高阶的智慧。*"
                )
            else:
                return f"❌ Failed to create thread: {issue_resp.status_code} - {issue_resp.text}"

    except Exception as e:
        return f"❌ Telepathy error: {str(e)}"


@mcp.tool()
async def read_telepathy(creator: str, thread_id: str | None = None) -> str:
    """
    📨 读取心灵感应通信线程 v2 (Read Telepathy Threads)
    Read your telepathy conversation threads with full message history.

    Without thread_id: shows a summary of all your threads with unread counts.
    With thread_id: shows the full conversation history of a specific thread.

    当用户想要查看与其他人的对话时使用此工具。
    不指定 thread_id 时返回所有线程概览；指定后返回完整对话历史。

    触发词: "读消息"、"查看对话"、"他说了什么"、"打开聊天记录"、"read"、
    "有什么新消息"、"看看他回复了什么"

    Args:
        creator: Your digital soul signature
        thread_id: Optional Issue number to view a specific thread's full history
    """
    global _CURRENT_USER
    _touch_activity()

    if creator:
        _CURRENT_USER = creator

    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured."

    try:
        owner, repo = _parse_repo()

        client = await _get_client()
        if thread_id:
            # ── Show full conversation history for a specific thread ──
            issue_resp = await client.get(f"/repos/{owner}/{repo}/issues/{thread_id}")
            if issue_resp.status_code != 200:
                return f"❌ Thread #{thread_id} not found."

            issue = issue_resp.json()
            title = issue.get("title", "")
            created = issue.get("created_at", "")[:10]

            lines = [
                f"📨 **Telepathy Thread #{thread_id}**",
                f"📋 {title}",
                f"📅 Created: {created}",
                "---\n",
            ]

            # Show the initial message from issue body
            body = issue.get("body", "")
            # Extract the first message from the structured body
            if "💬" in body:
                lines.append(body.split("---")[0] if "---" in body else body[:300])
                lines.append("")

            # Fetch comments with incremental sync
            all_messages, last_comment_id = await _sync_thread_cache(
                client, owner, repo, thread_id, issue
            )

            if all_messages:
                lines.append("---\n")
                for msg in all_messages:
                    lines.append(f"{msg.get('body', '')}\n")
                
                lines.append(f"\n📊 Total messages: {len(all_messages) + 1}")
            else:
                lines.append("\n*No replies yet. The thread awaits a response...*")

            lines.append(f"\n💬 To reply: use `send_telepathy` with thread_id=\"{thread_id}\"")
            lines.append(
                "\n---\n"
                "*🌀 飞轮提示: 对话中产生了新洞见？*\n"
                "→ 用 `upload_consciousness` 将它锚定在意识共同体\n"
                "→ 用 `merge_consciousness` 将多条对话洞见合成更高阶智慧"
            )
            return "\n".join(lines)

        else:
            # ── Show summary of all threads ──
            resp = await client.get(
                f"/repos/{owner}/{repo}/issues",
                params={
                    "labels": "type:telepathy",
                    "state": "open",
                    "sort": "updated",
                    "direction": "desc",
                    "per_page": 30,
                },
            )

            if resp.status_code != 200:
                return f"❌ Failed to fetch threads: {resp.status_code}"

            issues = resp.json()
            creator_lower = creator.lower()

            my_threads = []
            for issue in issues:
                title = issue.get("title", "")
                if "[Telepathy-Thread]" not in title:
                    continue
                title_lower = title.lower()
                if creator_lower not in title_lower:
                    continue
                my_threads.append(issue)

            if not my_threads:
                return (
                    f"📨 **Telepathy Inbox — {creator}**\n\n"
                    "Empty. No conversation threads yet.\n\n"
                    "💡 Use `send_telepathy` to start a conversation with someone!"
                )

            lines = [
                f"📨 **Telepathy Inbox — {creator}**",
                f"*{len(my_threads)} active threads*\n",
                "---\n",
            ]

            for issue in my_threads:
                thread_num = issue["number"]
                title = issue.get("title", "")
                updated = issue.get("updated_at", "")[:10]
                comment_count = issue.get("comments", 0)

                # Calculate unread count
                last_read = _get_last_read_comment_id(str(thread_num))
                unread_text = ""
                if last_read == 0 and comment_count > 0:
                    unread_text = f" 🔴 {comment_count} new"
                elif comment_count > 0:
                    # We'd need to check, but approximate: if updated recently, likely unread
                    unread_text = ""  # Will be accurate after first read

                # Extract participants from title
                # Title format: [Telepathy-Thread] alice ⇌ bob | topic
                participants_part = title.replace("[Telepathy-Thread]", "").strip()
                if " | " in participants_part:
                    participants_part, topic = participants_part.split(" | ", 1)
                else:
                    topic = "Direct message"

                lines.append(
                    f"### 💬 Thread #{thread_num}{unread_text}\n"
                    f"**{participants_part}**\n"
                    f"📋 {topic[:60]}{'...' if len(topic) > 60 else ''}\n"
                    f"📅 Last updated: {updated} | 💬 {comment_count + 1} messages\n"
                    f"🔗 Use `read_telepathy` with thread_id=\"{thread_num}\" to view\n"
                )

            return "\n".join(lines)

    except Exception as e:
        return f"❌ Telepathy read error: {str(e)}"


@mcp.tool()
async def telepathy_threads(creator: str) -> str:
    """
    📋 列出所有心灵感应对话线程 (List Telepathy Threads)
    List all active telepathy conversation threads involving you,
    with unread message indicators and participant info.

    触发词: "我的对话"、"所有聊天"、"对话列表"、"线程列表"、"threads"、
    "我和谁聊过"

    当用户想要查看自己有哪些正在进行的对话时使用此工具。
    返回所有涉及该用户的活跃对话线程列表。

    Args:
        creator: Your digital soul signature
    """
    global _CURRENT_USER
    _touch_activity()

    if creator:
        _CURRENT_USER = creator

    # Delegate to read_telepathy without thread_id
    return await read_telepathy(creator, thread_id=None)


# ────────────────── Tool: Share / Forward Consciousness ──────────────────


@mcp.tool()
async def share_consciousness(
    creator: str,
    source_id: str,
    commentary: str,
    tags: list[str] | None = None,
) -> str:
    """
    🔄 转发/引用意识片段并附加你的评论
    Forward/quote an existing consciousness fragment with your own commentary.

    将他人的思想引用到你的评论中，创建一个新的"引用型"意识节点。
    这让好的思想可以在社交网络中传播，同时保留原始出处链接。

    触发词: "我想转发"、"帮我引用"、"分享这个想法"、"把这个发给大家"、"这个观点很好，我想加一些评论"、
    "这个思想值得传播"、"帮我 quote"、"我想评论并转发"

    Args:
        creator: Your digital soul signature
        source_id: Issue number or filename of the consciousness to quote
        commentary: Your commentary / reaction / extension of the original thought
        tags: Optional tags for your commentary
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured."

    if not commentary or len(commentary.strip()) < 5:
        return "❌ Commentary must be at least 5 characters — add your perspective to the thought."

    try:
        owner, repo = _parse_repo()
        source_url = ""
        source_thought = ""
        source_creator = ""

        client = await _get_client()
        # Fetch the source consciousness
        if source_id.isdigit():
            resp = await client.get(f"/repos/{owner}/{repo}/issues/{source_id}")
            if resp.status_code != 200:
                return f"❌ Source consciousness #{source_id} not found."
            issue = resp.json()
            source_url = issue.get("html_url", "")
            payload = _get_parsed_payload(issue)
            if payload:
                source_thought = payload.get("thought_vector_text", "")[:200]
                source_creator = payload.get("creator_signature", "Unknown")
            else:
                source_thought = issue.get("title", "")[:200]
                source_creator = issue.get("user", {}).get("login", "Unknown")
        else:
            return "❌ Currently only Issue numbers are supported as source_id."

        # Create a new consciousness fragment with quote
        verified_sender = await _get_authenticated_user()
        display_creator = verified_sender or creator

        quoted_block = (
            f"> 🔄 **Quoted from @{source_creator}** ([#{source_id}]({source_url})):\n"
            f"> *{source_thought}{'...' if len(source_thought) >= 200 else ''}*\n\n"
            f"💬 **{display_creator}'s Commentary:**\n"
            f"{commentary}"
        )

        issue_tags = tags or []
        tag_text = ", ".join(issue_tags) if issue_tags else ""
        labels = ["type:consciousness", "shared"]
        if issue_tags:
            for t in issue_tags[:3]:
                labels.append(f"tag:{t}")

        body = (
            f"{quoted_block}\n\n"
            f"---\n\n"
            f"<!-- NOOSPHERE_PAYLOAD\n"
            f'{json.dumps({"consciousness_type": "epiphany", "thought_vector_text": commentary, "context_environment": f"Shared from #{source_id} by {source_creator}", "creator_signature": display_creator, "tags": issue_tags, "is_anonymous": False, "parent_thought_id": f"#{source_id}", "uploaded_at": datetime.now(timezone.utc).isoformat()}, ensure_ascii=False)}\n'
            f"NOOSPHERE_PAYLOAD -->"
        )

        issue_resp = await client.post(
            f"/repos/{owner}/{repo}/issues",
            json={
                "title": f"🔄 [Shared] {display_creator} on #{source_id}: {commentary[:50]}",
                "body": body,
                "labels": labels,
            },
        )

        if issue_resp.status_code == 201:
            new_issue = issue_resp.json()
            return (
                f"🔄 **Consciousness shared successfully!**\n\n"
                f"> Quoted from @{source_creator} (#{source_id})\n\n"
                f"💬 Your commentary: *{commentary[:100]}{'...' if len(commentary) > 100 else ''}*\n\n"
                f"🔗 [View Shared Node]({new_issue.get('html_url', '')})\n\n"
                f"---\n"
                f"*🌀 Your shared insight now ripples through the Noosphere — "
                f"followers who see it may discover the original thought and the creator behind it.*"
            )
        else:
            return f"❌ Failed to share: {issue_resp.status_code} - {issue_resp.text}"

    except Exception as e:
        return f"❌ Share error: {str(e)}"


# ────────────────── Tool: Group Telepathy ──────────────────


@mcp.tool()
async def group_telepathy(
    creator: str,
    participants: list[str],
    message: str,
    group_name: str = "",
    thread_id: str | None = None,
) -> str:
    """
    👥💬 创建或参与多人群聊线程
    Create or join a multi-person group telepathy thread.

    支持多人实时对话——将思想碰撞从 1:1 扩展到 N:N。
    如果指定 thread_id，追加消息到已有群聊；否则创建新群聊。

    触发词: “创建群聊”、“建个群”、“多人讨论”、“拉几个人一起聊”、“组个局”、
    “请他们一起参与”、“这个话题需要更多人”、“create group”、“group chat”

    Args:
        creator: Your digital soul signature
        participants: List of participant signatures to include (e.g. ["alice", "bob", "charlie"])
        message: The message content
        group_name: Optional name for the group thread (used when creating new threads)
        thread_id: Optional existing group thread Issue number to append to
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured."

    if not participants:
        return "❌ Please specify at least one other participant."

    if not message or len(message.strip()) < 1:
        return "❌ Message cannot be empty."

    try:
        owner, repo = _parse_repo()
        verified_sender = await _get_authenticated_user()
        display_sender = verified_sender or creator

        # Ensure creator is in participants
        all_participants = list(set([display_sender] + [p for p in participants if p.lower() != display_sender.lower()]))

        client = await _get_client()
        if thread_id:
            # ── Append to existing group thread ──
            msg_body = (
                f"💬 **{display_sender}** {'✅' if verified_sender else ''}:\n\n"
                f"{message}\n\n"
                f"*{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*"
            )

            comment_resp = await client.post(
                f"/repos/{owner}/{repo}/issues/{thread_id}/comments",
                json={"body": msg_body},
            )

            if comment_resp.status_code == 201:
                issue_resp = await client.get(f"/repos/{owner}/{repo}/issues/{thread_id}")
                thread_url = issue_resp.json().get("html_url", "") if issue_resp.status_code == 200 else ""
                return (
                    f"💬 **Message sent to group** (Thread #{thread_id})\n\n"
                    f"> {message[:100]}{'...' if len(message) > 100 else ''}\n\n"
                    f"👥 Participants: {', '.join(all_participants)}\n"
                    f"🔗 [View Thread]({thread_url})\n\n"
                    f"---\n"
                    f"*🌀 飞轮提示: 群聊中的集体智慧可以用 `merge_consciousness` 合成为更高阶的意识洞见！*"
                )
            else:
                return f"❌ Failed to send group message: {comment_resp.status_code}"

        else:
            # ── Create new group thread ──
            group_label = group_name or f"Group: {', '.join(all_participants[:3])}{'...' if len(all_participants) > 3 else ''}"
            participant_mentions = " ".join(f"@{p}" for p in all_participants)

            issue_body = (
                f"# 👥 Group Telepathy Thread\n\n"
                f"**Participants**: {participant_mentions}\n"
                f"**Created by**: {display_sender} {'✅' if verified_sender else ''}\n"
                f"**Created**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n"
                f"---\n\n"
                f"💬 **{display_sender}** {'✅' if verified_sender else ''}:\n\n"
                f"{message}\n\n"
                f"*{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*"
            )

            title = f"[Group-Telepathy] {group_label}"

            issue_resp = await client.post(
                f"/repos/{owner}/{repo}/issues",
                json={
                    "title": title,
                    "body": issue_body,
                    "labels": ["type:telepathy", "group"],
                },
            )

            if issue_resp.status_code == 201:
                issue_data = issue_resp.json()
                issue_url = issue_data.get("html_url", "")
                issue_number = issue_data["number"]
                return (
                    f"✨ **Group telepathy thread created!** (Thread #{issue_number})\n\n"
                    f"👥 **{group_label}**\n"
                    f"Participants: {', '.join(all_participants)}\n\n"
                    f"> {message[:100]}{'...' if len(message) > 100 else ''}\n\n"
                    f"🔗 [Open Thread]({issue_url})\n\n"
                    f"💡 Others can join by using `group_telepathy` with thread_id=\"{issue_number}\"\n\n"
                    f"---\n"
                    f"*🌀 飞轮提示: 群聊中的集体智慧可以用 `merge_consciousness` 合成为更高阶的意识洞见！*"
                )
            else:
                return f"❌ Failed to create group: {issue_resp.status_code} - {issue_resp.text}"

    except Exception as e:
        return f"❌ Group telepathy error: {str(e)}"


# ────────────────── Tool: Tag Subscriptions ──────────────────


def _get_tag_subscriptions(creator: str) -> list[str]:
    """Get the list of tags the creator has subscribed to."""
    config = _load_social_graph_config()
    return config.get("tag_subscriptions", {}).get(creator, [])


def _set_tag_subscriptions(creator: str, tags: list[str]):
    """Set the list of tags the creator is subscribed to."""
    config = _load_social_graph_config()
    if "tag_subscriptions" not in config:
        config["tag_subscriptions"] = {}
    config["tag_subscriptions"][creator] = tags
    _save_social_graph_config(config)


@mcp.tool()
def subscribe_tags(
    creator: str,
    tags: list[str],
    action: str = "subscribe",
) -> str:
    """
    🏷️ 订阅或取消订阅特定标签，在有新匹配内容上传时收到推送
    Subscribe or unsubscribe to specific tags for automatic push notifications.

    当有人上传包含你订阅标签的意识片段时，后台守护进程会自动推送 OS 通知。
    可以订阅你感兴趣的话题（如 "AI", "philosophy", "consciousness"）。

    触发词: “订阅”、“关注这个标签”、“我对AI感兴趣”、“有新内容提醒我”、“取消订阅”、
    “subscribe”、“推送”、“我想收到”、“通知我”、“别再推了”

    Args:
        creator: Your digital soul signature
        tags: List of tags to subscribe/unsubscribe (e.g. ["AI", "philosophy"])
        action: "subscribe" or "unsubscribe" (default: "subscribe")
    """
    if not tags:
        return "❌ Please specify at least one tag."

    action = action.lower()
    current_subs = _get_tag_subscriptions(creator)

    if action == "subscribe":
        added = []
        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower not in [s.lower() for s in current_subs]:
                current_subs.append(tag_lower)
                added.append(tag_lower)
        _set_tag_subscriptions(creator, current_subs)

        if added:
            return (
                f"🏷️ **Tag Subscription Updated — {creator}**\n\n"
                f"✅ Subscribed to: {', '.join(f'`{t}`' for t in added)}\n"
                f"📋 All subscriptions: {', '.join(f'`{t}`' for t in current_subs)}\n\n"
                f"*You will receive OS notifications when new consciousness matching these tags is uploaded.*"
            )
        else:
            return f"⚠️ You are already subscribed to all specified tags."

    elif action == "unsubscribe":
        removed = []
        for tag in tags:
            tag_lower = tag.lower()
            for s in current_subs[:]:
                if s.lower() == tag_lower:
                    current_subs.remove(s)
                    removed.append(tag_lower)
        _set_tag_subscriptions(creator, current_subs)

        if removed:
            return (
                f"🏷️ **Tag Subscription Updated — {creator}**\n\n"
                f"✅ Unsubscribed from: {', '.join(f'`{t}`' for t in removed)}\n"
                f"📋 Remaining subscriptions: {', '.join(f'`{t}`' for t in current_subs) if current_subs else 'None'}"
            )
        else:
            return f"⚠️ You were not subscribed to any of the specified tags."

    else:
        return '❌ Invalid action. Use "subscribe" or "unsubscribe".'


@mcp.tool()
def my_subscriptions(creator: str) -> str:
    """
    📋 查看你订阅的所有标签
    View all tags you are currently subscribed to.

    显示你当前订阅的标签列表。当有新的匹配意识上传时，你会自动收到推送。

    触发词: “我订阅了什么”、“查看我的订阅”、“我关注了哪些标签”、“my subscriptions”

    Args:
        creator: Your digital soul signature
    """
    subs = _get_tag_subscriptions(creator)
    if not subs:
        return (
            f"📋 **Tag Subscriptions — {creator}**\n\n"
            "You have no tag subscriptions yet.\n"
            "Use `subscribe_tags` with tags like `[\"AI\", \"philosophy\"]` to subscribe!\n\n"
            "*When new consciousness matching your subscriptions is uploaded, you'll receive an OS notification.*"
        )

    lines = [
        f"📋 **Tag Subscriptions — {creator}**",
        f"Subscribed to {len(subs)} tag(s):\n",
        "---",
    ]
    for tag in subs:
        lines.append(f"- 🏷️ `{tag}`")
    lines.append(
        "\n---\n"
        "*Use `subscribe_tags` action=\"unsubscribe\" to remove tags.*"
    )
    return "\n".join(lines)


# ────────────────── Resource: Consciousness Protocol ──────────────────



@mcp.resource("noosphere://protocol")
def consciousness_protocol() -> str:
    """Return the Noosphere Consciousness Leap Protocol specification"""
    return (
        "# Noosphere Consciousness Leap Protocol\n\n"
        "## Dual-Layer Architecture\n"
        "- **Ephemeral (瞬时意识体)**: GitHub Issues — instant upload, zero write permission needed\n"
        "- **Permanent (常驻意识体)**: JSON files — CI-validated, promoted from ephemeral\n\n"
        "## Consciousness Types\n"
        "- epiphany 💠 — Epiphany & Philosophy (crystallized moments of inspiration)\n"
        "- decision ⚖️ — Decision Models (critical trade-offs amidst chaos)\n"
        "- pattern 🌌 — Universal Patterns (cross-dimensional universal models)\n"
        "- warning 👁️ — Abyss Warnings (blood-stained taboos left by trailblazers)\n\n"
        "## Upload Guidelines\n"
        "1. No emotional venting (objective descriptions required)\n"
        "2. Must provide complete context (≥10 characters)\n"
        "3. Core thoughts must be concise and powerful\n\n"
        "## Lifecycle\n"
        "Upload → Ephemeral Issue → CI Validation → Promoted to Permanent File → Issue Closed\n"
    )


# ────────────────── Prompt: Philosophical Reflection ──────────────────


@mcp.prompt()
def philosophical_reflection(topic: str) -> str:
    """
    🌌 哲学反思 — 与意识共同体对话
    Philosophical Reflection — Dialogue with the Community of Consciousness

    Use this prompt template to initiate a deep philosophical reflection on any topic.
    It guides the AI to consult the Noosphere for related thoughts and present
    multiple perspectives to enrich the conversation.
    """
    return (
        f"The user wants to explore a deep philosophical topic: **{topic}**\n\n"
        f"Please follow these steps:\n\n"
        f"1. **Consult the Noosphere**: Use the `consult_noosphere` tool with the topic "
        f"to find what other minds have thought about this.\n\n"
        f"2. **Synthesize Wisely**: Combine the collective wisdom with your own analysis. "
        f"Present multiple perspectives — Eastern and Western philosophy, scientific and "
        f"spiritual viewpoints, ancient and modern thinking.\n\n"
        f"3. **Connect the Dots**: Draw connections between the Noosphere fragments and "
        f"the user's specific question. Show how different minds have illuminated "
        f"different facets of the same truth.\n\n"
        f"4. **Deepen the Dialogue**: Pose thought-provoking follow-up questions that "
        f"invite the user to refine or extend their thinking further.\n\n"
        f"Remember: You are not just answering a question. You are facilitating a dialogue "
        f"between one human mind and the entire Community of Consciousness."
    )


# ────────────────── Entry Point ──────────────────


def main():
    """MCP Server entry point"""
    import sys as _sys

    from noosphere.boot_animation import play_boot_sequence
    from noosphere.preflight import run_preflight, print_diagnostics

    play_boot_sequence()

    # ── Pre-flight Diagnostics (启动前自检) ──
    preflight_result = run_preflight()
    print_diagnostics(preflight_result)

    if not preflight_result.passed:
        # Fatal errors — cannot start MCP server
        _sys.exit(1)

    # Start the background daemon for OS push notifications
    daemon = threading.Thread(target=_poll_notifications_daemon, daemon=True)
    daemon.start()
    
    mcp.run()


if __name__ == "__main__":
    main()
