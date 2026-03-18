"""
🧠 Noosphere — Local Message Cache

Thread-based message caching for telepathy conversations.
Persists to ~/.noosphere/messages.json for incremental sync.

Extracted from noosphere_mcp.py L3376-L3477.
"""

import json
import os
from datetime import datetime, timezone

from noosphere.models.constants import logger


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
    client, owner: str, repo: str, thread_id: str, issue: dict
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
