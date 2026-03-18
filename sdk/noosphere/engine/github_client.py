"""
🧠 Noosphere — GitHub API Client & Utilities

Shared HTTP client with connection pooling, GitHub API helpers,
Issue fetching with pagination, and file payload retrieval.

Extracted from noosphere_mcp.py L54-L84, L342-L416, L601-L777.
"""

import json
import asyncio
from base64 import b64decode

import httpx

from noosphere.models.constants import (
    GITHUB_TOKEN,
    GITHUB_API,
    GITHUB_BRANCH,
    GITHUB_REPO,
    LABEL_CONSCIOUSNESS,
    logger,
    _AUTHENTICATED_USER,
)
from noosphere.engine.cache import _get_cached, _set_cached


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


# ── GitHub API Utilities ──


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


# ── Issue Fetching ──


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


# ── File Payload Fetching ──


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


# ── Identity Verification ──


async def _get_authenticated_user() -> str:
    """Get the GitHub username associated with the current GITHUB_TOKEN.
    Caches the result for the lifetime of the process."""
    import noosphere.models.constants as _constants
    if _constants._AUTHENTICATED_USER:
        return _constants._AUTHENTICATED_USER
    if not GITHUB_TOKEN:
        return ""
    try:
        client = await _get_client()
        resp = await client.get("/user")
        if resp.status_code == 200:
            _constants._AUTHENTICATED_USER = resp.json().get("login", "")
            return _constants._AUTHENTICATED_USER
    except Exception as e:
        logger.warning(f"Failed to verify GitHub identity: {e}")
    return ""
