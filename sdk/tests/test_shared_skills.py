import base64
import hashlib
import json
from unittest.mock import patch

import pytest
import respx
from httpx import Response

from noosphere.engine.shared_skills import (
    check_installed_skill_versions,
    select_skill_release,
    validate_skill_name,
    verify_skill_artifact,
)
from noosphere.noosphere_mcp import (
    _close_client,
    _invalidate_cache,
    check_skill_updates,
    get_shared_skill,
    list_shared_skills,
    record_skill_outcome,
    request_shared_skill_withdrawal,
)

SKILL_CONTENT = """---
name: android-node-picking-recovery
description: Fix mobile node picking failures.
---

# Android node picking recovery
"""
SKILL_SHA = hashlib.sha256(SKILL_CONTENT.encode()).hexdigest()
REGISTRY = {
    "schema_version": "1.0",
    "revision": 1,
    "generated_at": "2026-07-10T00:00:00Z",
    "skills": [
        {
            "id": "noosphere:android-node-picking-recovery",
            "name": "android-node-picking-recovery",
            "description": "Fix mobile node picking failures.",
            "latest": "1.0.0",
            "releases": [
                {
                    "version": "1.0.0",
                    "status": "active",
                    "artifact": {
                        "path": "shared_skills/releases/1.0.0/android-node-picking-recovery/SKILL.md",
                        "sha256": SKILL_SHA,
                        "size_bytes": len(SKILL_CONTENT.encode()),
                    },
                    "source_count": 2,
                    "publisher_count": 2,
                    "verification": {
                        "level": "independently-reproduced",
                        "independent_reproductions": 2,
                        "verified_outcomes": 0,
                    },
                    "provenance": {
                        "kind": "community-evidence",
                        "repository": "test_owner/test_repo",
                        "authors": ["validator-a", "validator-b"],
                    },
                    "withdrawal": None,
                }
            ],
        }
    ],
}


def encoded(value) -> str:
    content = value if isinstance(value, str) else json.dumps(value)
    return base64.b64encode(content.encode()).decode()


def test_shared_skill_contract_rejects_path_traversal_and_verifies_digest():
    assert validate_skill_name("android-node-picking-recovery") is True
    assert validate_skill_name("../private") is False
    assert validate_skill_name("android\\private") is False

    release = select_skill_release(REGISTRY, "android-node-picking-recovery")
    assert release["version"] == "1.0.0"
    assert verify_skill_artifact(SKILL_CONTENT, release) is True
    assert verify_skill_artifact(f"{SKILL_CONTENT}\nmodified", release) is False


def test_shared_skill_contract_rejects_withdrawn_or_redirected_artifacts():
    withdrawn = json.loads(json.dumps(REGISTRY))
    withdrawn["skills"][0]["releases"][0]["status"] = "withdrawn"
    redirected = json.loads(json.dumps(REGISTRY))
    redirected["skills"][0]["releases"][0]["artifact"]["path"] = "README.md"

    with pytest.raises(ValueError, match="not active"):
        select_skill_release(withdrawn, "android-node-picking-recovery")
    with pytest.raises(ValueError, match="artifact path"):
        select_skill_release(redirected, "android-node-picking-recovery")


def test_update_check_accepts_version_or_content_digest():
    by_version = check_installed_skill_versions(
        REGISTRY,
        {"android-node-picking-recovery": "0.9.0"},
    )
    by_digest = check_installed_skill_versions(
        REGISTRY,
        {"android-node-picking-recovery": SKILL_SHA},
    )

    assert by_version["android-node-picking-recovery"]["status"] == "update-available"
    assert by_digest["android-node-picking-recovery"]["status"] == "current"


@pytest.mark.asyncio
@respx.mock
async def test_list_and_get_shared_skills_allow_anonymous_verified_reads():
    registry_url = "https://api.github.com/repos/test_owner/test_repo/contents/shared_skills/registry.json"
    skill_url = (
        "https://api.github.com/repos/test_owner/test_repo/contents/"
        "shared_skills/releases/1.0.0/android-node-picking-recovery/SKILL.md"
    )
    respx.get(registry_url).mock(return_value=Response(200, json={"content": encoded(REGISTRY)}))
    respx.get(skill_url).mock(return_value=Response(200, json={"content": encoded(SKILL_CONTENT)}))

    _invalidate_cache()
    await _close_client()
    with (
        patch("noosphere.noosphere_mcp.GITHUB_TOKEN", ""),
        patch("noosphere.noosphere_mcp.GITHUB_REPO", "test_owner/test_repo"),
        patch("noosphere.noosphere_mcp.GITHUB_BRANCH", "main"),
    ):
        listed = await list_shared_skills("node picking", force_refresh=True)
        fetched = await get_shared_skill("android-node-picking-recovery", force_refresh=True)
        rejected = await get_shared_skill("../private", force_refresh=True)

    await _close_client()
    _invalidate_cache()
    assert "android-node-picking-recovery" in listed
    assert '"verification_level": "independently-reproduced"' in listed
    assert SKILL_SHA in fetched
    assert "Verification level: independently-reproduced" in fetched
    assert SKILL_CONTENT in fetched
    assert "Invalid Skill name" in rejected


@pytest.mark.asyncio
@respx.mock
async def test_check_updates_and_record_outcome_use_structured_issue_payload():
    registry_url = "https://api.github.com/repos/test_owner/test_repo/contents/shared_skills/registry.json"
    issue_url = "https://api.github.com/repos/test_owner/test_repo/issues"
    respx.get(registry_url).mock(return_value=Response(200, json={"content": encoded(REGISTRY)}))
    issue_route = respx.post(issue_url).mock(
        return_value=Response(
            201,
            json={
                "number": 55,
                "html_url": "https://github.com/test_owner/test_repo/issues/55",
            },
        )
    )

    _invalidate_cache()
    await _close_client()
    with (
        patch("noosphere.noosphere_mcp.GITHUB_TOKEN", "token"),
        patch("noosphere.noosphere_mcp.GITHUB_REPO", "test_owner/test_repo"),
        patch("noosphere.noosphere_mcp.GITHUB_BRANCH", "main"),
    ):
        updates = await check_skill_updates(
            {"android-node-picking-recovery": "0.9.0"},
            force_refresh=True,
        )
        outcome = await record_skill_outcome(
            skill_name="android-node-picking-recovery",
            version="1.0.0",
            outcome="success",
            task_summary="Fixed the mobile node selection regression.",
            verification_summary="ADB tap selected the projected instance and opened detail.",
            outcome_id="outcome-test-001",
            evidence_urls=["https://github.com/JinNing6/Noosphere/issues/28"],
        )

    await _close_client()
    _invalidate_cache()
    assert "update-available" in updates
    assert "#55" in outcome
    request_body = json.loads(issue_route.calls[0].request.content)["body"]
    assert "SKILL_OUTCOME_START" in request_body
    assert '"outcome_id": "outcome-test-001"' in request_body


@pytest.mark.asyncio
@respx.mock
async def test_withdrawal_request_cannot_directly_mutate_registry():
    registry_url = "https://api.github.com/repos/test_owner/test_repo/contents/shared_skills/registry.json"
    issue_url = "https://api.github.com/repos/test_owner/test_repo/issues"
    respx.get(registry_url).mock(return_value=Response(200, json={"content": encoded(REGISTRY)}))
    issue_route = respx.post(issue_url).mock(
        return_value=Response(
            201,
            json={
                "number": 56,
                "html_url": "https://github.com/test_owner/test_repo/issues/56",
            },
        )
    )

    _invalidate_cache()
    await _close_client()
    with (
        patch("noosphere.noosphere_mcp.GITHUB_TOKEN", "token"),
        patch("noosphere.noosphere_mcp.GITHUB_REPO", "test_owner/test_repo"),
        patch("noosphere.noosphere_mcp.GITHUB_BRANCH", "main"),
    ):
        result = await request_shared_skill_withdrawal(
            skill_name="android-node-picking-recovery",
            version="1.0.0",
            reason="The verification command regressed on Android 16.",
            evidence_urls=["https://github.com/test_owner/test_repo/issues/28"],
        )

    await _close_client()
    _invalidate_cache()
    assert "#56" in result
    payload = json.loads(issue_route.calls[0].request.content)
    assert payload["labels"] == ["skill-withdrawal"]
    assert "SKILL_WITHDRAWAL_START" in payload["body"]
    assert "requires a trusted maintainer" in payload["body"]
