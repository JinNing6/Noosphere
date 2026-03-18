"""
🧠 Noosphere — Local Social Graph Management

Follow/unfollow creators, tag subscriptions, and GitHub sync.
Persists to ~/.noosphere/config.json.

Extracted from noosphere_mcp.py L3483-L3561, L4704-L4716.
"""

import json
import os
from base64 import b64encode
from datetime import datetime, timezone

from noosphere.models.constants import (
    GITHUB_TOKEN,
    GITHUB_BRANCH,
    logger,
)


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


async def _sync_social_graph_to_github(creator: str, following: list[str]):
    """Sync the follow list to GitHub repo so others can query who follows them."""
    if not GITHUB_TOKEN:
        return
    try:
        from noosphere.engine.github_client import _get_client, _parse_repo

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


# ── Tag Subscriptions ──


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
