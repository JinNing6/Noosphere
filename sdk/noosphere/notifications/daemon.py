"""
🧠 Noosphere — Background Notification Daemon

OS-level push notifications via background polling thread.
Monitors telepathy messages, tag subscriptions, and community interactions.

Extracted from noosphere_mcp.py L3919-L4111.
"""

import platform
import re
import subprocess
import time
import asyncio

from noosphere.models.constants import (
    GITHUB_TOKEN,
    _last_activity_time,
    _CURRENT_USER,
    logger,
)
from noosphere.engine.github_client import _get_client, _parse_repo
from noosphere.engine.cache import _get_parsed_payload
from noosphere.engine.message_cache import (
    _get_last_read_comment_id,
    _load_message_cache,
    _save_message_cache,
)
from noosphere.engine.social_graph import _get_tag_subscriptions


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
    import noosphere.models.constants as _constants
    import asyncio

    # Store the last checked URL to avoid duplicate alerts
    last_alerted_url = None

    while True:
        # ── Adaptive interval calculation ──
        elapsed = time.time() - _constants._last_activity_time if _constants._last_activity_time > 0 else float("inf")
        if elapsed < 300:       # < 5 min
            interval = 10
        elif elapsed < 1800:    # < 30 min
            interval = 30
        else:
            interval = 120

        time.sleep(interval)
        if not _constants._CURRENT_USER or not GITHUB_TOKEN:
            continue

        try:
            # Import my_notifications lazily to avoid circular import
            from noosphere.tools.social import my_notifications
            result = asyncio.run(my_notifications(_constants._CURRENT_USER))

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
                telepathy_result = asyncio.run(_check_new_telepathy(_constants._CURRENT_USER, owner, repo))
                if telepathy_result:
                    _os_notify("💌 Noosphere Telepathy", telepathy_result)
            except Exception:
                pass  # Non-critical

            # ── Tag subscription check ──
            try:
                subscribed_tags = _get_tag_subscriptions(_constants._CURRENT_USER)
                if subscribed_tags:
                    tag_result = asyncio.run(_check_tag_subscriptions(_constants._CURRENT_USER, subscribed_tags))
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
        from datetime import datetime, timezone
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
