import base64
import json
from unittest.mock import patch

import pytest
import respx
from httpx import Response

from noosphere.engine.memory_integrity import (
    canonicalize_permanent_entries,
    parse_tombstoned_issue_numbers,
)
from noosphere.noosphere_mcp import (
    _close_client,
    _fetch_file_payloads,
    _get_client,
    _invalidate_cache,
)


def _entry(filename: str, issue_number: int | None, promoted_at: str) -> dict:
    payload = {
        "thought_vector_text": filename,
        "promoted_at": promoted_at,
    }
    if issue_number is not None:
        payload["promoted_from_issue"] = issue_number
    return {"filename": filename, "payload": payload}


def test_canonicalize_permanent_entries_keeps_latest_record_per_source_issue():
    entries = [
        _entry("warning_old_issue0007.json", 7, "2026-01-01T00:00:00Z"),
        _entry("warning_new_issue0007.json", 7, "2026-02-01T00:00:00Z"),
        _entry("pattern_issue0008.json", 8, "2026-01-15T00:00:00Z"),
        _entry("legacy_without_issue.json", None, "2026-01-20T00:00:00Z"),
    ]

    canonical = canonicalize_permanent_entries(entries, tombstoned_issue_numbers=set())

    assert [entry["filename"] for entry in canonical] == [
        "legacy_without_issue.json",
        "warning_new_issue0007.json",
        "pattern_issue0008.json",
    ]


def test_canonicalize_permanent_entries_orders_malformed_and_naive_timestamps_safely():
    entries = [
        _entry("malformed_issue0007.json", 7, "not-a-timestamp"),
        _entry("naive_issue0007.json", 7, "2026-01-01T00:00:00"),
        _entry("aware_issue0007.json", 7, "2026-01-02T00:00:00+08:00"),
    ]

    canonical = canonicalize_permanent_entries(entries, tombstoned_issue_numbers=set())

    assert [entry["filename"] for entry in canonical] == ["aware_issue0007.json"]


def test_canonicalize_permanent_entries_excludes_tombstoned_promotions():
    entries = [
        _entry("warning_issue0010.json", 10, "2026-01-01T00:00:00Z"),
        _entry("pattern_issue0011.json", 11, "2026-01-02T00:00:00Z"),
    ]

    canonical = canonicalize_permanent_entries(entries, tombstoned_issue_numbers={10})

    assert [entry["filename"] for entry in canonical] == ["pattern_issue0011.json"]


def test_parse_tombstoned_issue_numbers_accepts_only_positive_unique_ids():
    manifest = {
        "version": 1,
        "withdrawn_issues": [
            {"issue_number": 10},
            {"issue_number": "10"},
            {"issue_number": 11},
            {"issue_number": 0},
            {"issue_number": "invalid"},
        ],
    }

    assert parse_tombstoned_issue_numbers(manifest) == {10, 11}


@pytest.mark.asyncio
@respx.mock
async def test_fetch_file_payloads_excludes_tombstones_and_legacy_duplicates():
    def encoded(value: dict) -> str:
        return base64.b64encode(json.dumps(value).encode()).decode()

    directory_url = "https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads"
    tombstones_url = "https://api.github.com/repos/test_owner/test_repo/contents/consciousness_tombstones.json"
    old_url = f"{directory_url}/warning_old_issue0010.json"
    new_url = f"{directory_url}/warning_new_issue0010.json"
    active_url = f"{directory_url}/pattern_issue0011.json"

    respx.get(directory_url).mock(
        return_value=Response(
            200,
            json=[
                {"name": "warning_old_issue0010.json", "url": old_url, "html_url": "old"},
                {"name": "warning_new_issue0010.json", "url": new_url, "html_url": "new"},
                {"name": "pattern_issue0011.json", "url": active_url, "html_url": "active"},
            ],
        )
    )
    respx.get(old_url).mock(
        return_value=Response(
            200,
            json={
                "content": encoded(
                    {
                        "promoted_from_issue": 10,
                        "promoted_at": "2026-01-01T00:00:00Z",
                        "thought_vector_text": "old",
                    }
                )
            },
        )
    )
    respx.get(new_url).mock(
        return_value=Response(
            200,
            json={
                "content": encoded(
                    {
                        "promoted_from_issue": 10,
                        "promoted_at": "2026-02-01T00:00:00Z",
                        "thought_vector_text": "new",
                    }
                )
            },
        )
    )
    respx.get(active_url).mock(
        return_value=Response(
            200,
            json={
                "content": encoded(
                    {
                        "promoted_from_issue": 11,
                        "promoted_at": "2026-02-01T00:00:00Z",
                        "thought_vector_text": "active",
                    }
                )
            },
        )
    )
    respx.get(tombstones_url).mock(
        return_value=Response(
            200,
            json={
                "content": encoded(
                    {
                        "version": 1,
                        "withdrawn_issues": [{"issue_number": 10}],
                    }
                )
            },
        )
    )

    _invalidate_cache()
    await _close_client()
    with patch("noosphere.noosphere_mcp.GITHUB_TOKEN", "test"), patch("noosphere.noosphere_mcp.GITHUB_BRANCH", "main"):
        client = await _get_client()
        entries = await _fetch_file_payloads(client, "test_owner", "test_repo")

    await _close_client()
    _invalidate_cache()
    assert [entry["filename"] for entry in entries] == ["pattern_issue0011.json"]


@pytest.mark.asyncio
@respx.mock
async def test_fetch_file_payloads_fails_closed_when_tombstones_are_unavailable():
    def encoded(value: dict) -> str:
        return base64.b64encode(json.dumps(value).encode()).decode()

    directory_url = "https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads"
    tombstones_url = "https://api.github.com/repos/test_owner/test_repo/contents/consciousness_tombstones.json"
    active_url = f"{directory_url}/pattern_issue0011.json"
    respx.get(directory_url).mock(
        return_value=Response(
            200,
            json=[{"name": "pattern_issue0011.json", "url": active_url, "html_url": "active"}],
        )
    )
    respx.get(active_url).mock(
        return_value=Response(
            200,
            json={
                "content": encoded(
                    {
                        "promoted_from_issue": 11,
                        "promoted_at": "2026-02-01T00:00:00Z",
                        "thought_vector_text": "active",
                    }
                )
            },
        )
    )
    respx.get(tombstones_url).mock(return_value=Response(503))

    _invalidate_cache()
    await _close_client()
    with (
        patch("noosphere.noosphere_mcp.GITHUB_TOKEN", "test"),
        patch("noosphere.noosphere_mcp.GITHUB_BRANCH", "main"),
    ):
        client = await _get_client()
        with pytest.raises(RuntimeError, match="tombstones: HTTP 503"):
            await _fetch_file_payloads(client, "test_owner", "test_repo")

    await _close_client()
    _invalidate_cache()
