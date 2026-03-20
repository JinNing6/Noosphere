"""
🧠 Noosphere — GitHub Release Manager for Media Assets (Voice + Image + Video)

Manages dedicated Releases for storing audio, image, and video files.
Files are uploaded as Release Assets, providing permanent
download URLs without bloating the Git repository.

GitHub Releases API reference:
  - GET  /repos/{owner}/{repo}/releases/tags/{tag}
  - POST /repos/{owner}/{repo}/releases
  - POST https://uploads.github.com/repos/{o}/{r}/releases/{id}/assets
"""

import os
import hashlib
from datetime import datetime, timezone

import httpx

from noosphere.models.constants import (
    GITHUB_TOKEN,
    VOICE_RELEASE_TAG,
    VOICE_MAX_SIZE_BYTES,
    VOICE_ALLOWED_EXTENSIONS,
    IMAGE_RELEASE_TAG,
    IMAGE_MAX_SIZE_BYTES,
    IMAGE_ALLOWED_EXTENSIONS,
    VIDEO_RELEASE_TAG,
    VIDEO_MAX_SIZE_BYTES,
    VIDEO_ALLOWED_EXTENSIONS,
    logger,
)


# ── Cached Release IDs (by media_type) ──
_release_id_cache: dict[str, int] = {}


# ── Release Descriptions ──
_RELEASE_INFO = {
    "voice": {
        "tag": VOICE_RELEASE_TAG,
        "name": "🎙️ Voice Consciousness — 万物之声",
        "body": (
            "Audio files uploaded by the Noosphere community.\n\n"
            "🐋 Whale songs · 🐱 Cat purrs · 🐕 Dog barks · 🧠 Human wisdom\n\n"
            "Each asset corresponds to a consciousness Issue with full metadata.\n"
            "Do NOT delete assets manually — they are referenced by Issues."
        ),
    },
    "image": {
        "tag": IMAGE_RELEASE_TAG,
        "name": "🖼️ Visual Consciousness — 视觉意识",
        "body": (
            "Images uploaded by the Noosphere community.\n\n"
            "🎨 Art · 📸 Photos · 🌅 Landscapes · 🧠 Mind Maps · 🔬 Diagrams\n\n"
            "Each asset corresponds to a consciousness Issue with full metadata.\n"
            "Do NOT delete assets manually — they are referenced by Issues."
        ),
    },
    "video": {
        "tag": VIDEO_RELEASE_TAG,
        "name": "🎬 Motion Consciousness — 动态意识",
        "body": (
            "Video files uploaded by the Noosphere community.\n\n"
            "🎥 Vlogs · 🌊 Nature · 🧪 Experiments · 💡 Tutorials · 🌌 Cosmic\n\n"
            "Each asset corresponds to a consciousness Issue with full metadata.\n"
            "Do NOT delete assets manually — they are referenced by Issues."
        ),
    },
}


async def _get_or_create_release(
    client: httpx.AsyncClient,
    owner: str,
    repo: str,
    media_type: str,
) -> tuple[int, str]:
    """Get or create a media Release (voice, image, or video).

    Args:
        client: Shared httpx.AsyncClient (base_url=api.github.com)
        owner: Repository owner
        repo: Repository name
        media_type: "voice", "image", or "video"

    Returns (release_id, upload_url).
    """
    info = _RELEASE_INFO[media_type]
    tag = info["tag"]

    # Check cache
    cached_id = _release_id_cache.get(media_type)
    if cached_id is not None:
        resp = await client.get(f"/repos/{owner}/{repo}/releases/{cached_id}")
        if resp.status_code == 200:
            return cached_id, resp.json()["upload_url"]

    # Try fetching by tag
    resp = await client.get(f"/repos/{owner}/{repo}/releases/tags/{tag}")
    if resp.status_code == 200:
        data = resp.json()
        release_id = data["id"]
        _release_id_cache[media_type] = release_id
        return release_id, data["upload_url"]

    # Create new Release
    resp = await client.post(
        f"/repos/{owner}/{repo}/releases",
        json={
            "tag_name": tag,
            "name": info["name"],
            "body": info["body"],
            "draft": False,
            "prerelease": False,
        },
    )
    if resp.status_code != 201:
        raise RuntimeError(
            f"Failed to create {media_type} Release: {resp.status_code} — {resp.text}"
        )

    data = resp.json()
    release_id = data["id"]
    _release_id_cache[media_type] = release_id
    logger.info(f"Created {media_type} Release: id={release_id}")
    return release_id, data["upload_url"]


# ── File Validation ──


_VALIDATION_CONFIG = {
    "voice": (VOICE_ALLOWED_EXTENSIONS, VOICE_MAX_SIZE_BYTES),
    "image": (IMAGE_ALLOWED_EXTENSIONS, IMAGE_MAX_SIZE_BYTES),
    "video": (VIDEO_ALLOWED_EXTENSIONS, VIDEO_MAX_SIZE_BYTES),
}


def _validate_audio_file(file_path: str) -> tuple[bool, str]:
    """Validate an audio file for upload."""
    return _validate_media_file(file_path, *_VALIDATION_CONFIG["voice"])


def _validate_image_file(file_path: str) -> tuple[bool, str]:
    """Validate an image file for upload."""
    return _validate_media_file(file_path, *_VALIDATION_CONFIG["image"])


def _validate_video_file(file_path: str) -> tuple[bool, str]:
    """Validate a video file for upload."""
    return _validate_media_file(file_path, *_VALIDATION_CONFIG["video"])


def _validate_media_file(
    file_path: str,
    allowed_extensions: set[str],
    max_size_bytes: int,
) -> tuple[bool, str]:
    """Generic media file validation."""
    if not os.path.isfile(file_path):
        return False, f"File not found: {file_path}"

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in allowed_extensions:
        return False, (
            f"Unsupported format '{ext}'. "
            f"Allowed: {', '.join(sorted(allowed_extensions))}"
        )

    file_size = os.path.getsize(file_path)
    if file_size > max_size_bytes:
        size_mb = file_size / (1024 * 1024)
        max_mb = max_size_bytes / (1024 * 1024)
        return False, f"File too large ({size_mb:.1f}MB). Maximum: {max_mb:.0f}MB"

    if file_size == 0:
        return False, "File is empty (0 bytes)"

    return True, ""


# ── Content Type Detection ──


_MIME_MAP = {
    # Audio
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".opus": "audio/opus",
    ".webm": "audio/webm",
    ".m4a": "audio/mp4",
    ".flac": "audio/flac",
    # Image
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".svg": "image/svg+xml",
    ".heic": "image/heic",
    ".tiff": "image/tiff",
    # Video
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".avi": "video/x-msvideo",
    ".mkv": "video/x-matroska",
    ".flv": "video/x-flv",
    ".wmv": "video/x-ms-wmv",
    ".m4v": "video/x-m4v",
}
# .webp and .webm share extension overlap — handled by context
_MIME_MAP.setdefault(".webp", "image/webp")


def _get_content_type(file_path: str) -> str:
    """Get MIME content type from file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    return _MIME_MAP.get(ext, "application/octet-stream")


# ── Asset Naming ──


def _generate_asset_name(
    prefix: str, creator: str, file_path: str, sub_type: str = ""
) -> str:
    """Generate a unique asset filename for the Release.

    Format: {prefix}_{sub_type}_{creator}_{timestamp}_{hash}.{ext}
    """
    ext = os.path.splitext(file_path)[1].lower()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    with open(file_path, "rb") as f:
        file_hash = hashlib.sha256(f.read(8192)).hexdigest()[:8]

    safe_creator = "".join(c if c.isalnum() else "_" for c in creator)[:20]
    parts = [prefix]
    if sub_type:
        parts.append(sub_type)
    parts.extend([safe_creator, ts, file_hash])
    return "_".join(parts) + ext


# ── Upload Functions ──


async def _upload_audio_asset(
    client: httpx.AsyncClient, owner: str, repo: str,
    file_path: str, creator: str, species: str,
) -> tuple[str, int]:
    """Upload an audio file. Returns (download_url, file_size)."""
    return await _upload_media_asset(
        client, owner, repo, file_path,
        _generate_asset_name("voice", creator, file_path, species),
        "voice",
    )


async def _upload_image_asset(
    client: httpx.AsyncClient, owner: str, repo: str,
    file_path: str, creator: str,
) -> tuple[str, int]:
    """Upload an image file. Returns (download_url, file_size)."""
    return await _upload_media_asset(
        client, owner, repo, file_path,
        _generate_asset_name("image", creator, file_path),
        "image",
    )


async def _upload_video_asset(
    client: httpx.AsyncClient, owner: str, repo: str,
    file_path: str, creator: str,
) -> tuple[str, int]:
    """Upload a video file. Returns (download_url, file_size)."""
    return await _upload_media_asset(
        client, owner, repo, file_path,
        _generate_asset_name("video", creator, file_path),
        "video",
    )


async def _upload_media_asset(
    client: httpx.AsyncClient, owner: str, repo: str,
    file_path: str, asset_name: str, media_type: str,
) -> tuple[str, int]:
    """Generic media upload to a Release. Returns (download_url, file_size)."""
    release_id, _ = await _get_or_create_release(client, owner, repo, media_type)

    content_type = _get_content_type(file_path)
    file_size = os.path.getsize(file_path)

    upload_url = (
        f"https://uploads.github.com/repos/{owner}/{repo}"
        f"/releases/{release_id}/assets"
    )

    with open(file_path, "rb") as f:
        file_data = f.read()

    async with httpx.AsyncClient(timeout=300) as upload_client:
        resp = await upload_client.post(
            upload_url,
            params={"name": asset_name},
            content=file_data,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": content_type,
            },
        )

    if resp.status_code != 201:
        raise RuntimeError(
            f"Failed to upload {media_type} asset: {resp.status_code} — {resp.text}"
        )

    data = resp.json()
    download_url = data["browser_download_url"]
    logger.info(f"Uploaded {media_type} asset: {asset_name} → {download_url}")
    return download_url, file_size
