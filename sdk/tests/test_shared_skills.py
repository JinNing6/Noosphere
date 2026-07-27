import base64
import hashlib
import json
from unittest.mock import patch

import pytest
import respx
from httpx import Response

from noosphere.engine.shared_skills import (
    check_installed_skill_versions,
    is_release_originator,
    select_skill_release,
    summarize_release_usage,
    summarize_skill_usage,
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
    submit_skill_evidence,
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


def test_usage_summary_is_a_reviewed_lower_bound_and_rejects_invalid_counters():
    release = json.loads(json.dumps(REGISTRY["skills"][0]["releases"][0]))
    release["verification"]["verified_outcomes"] = 3
    release["verification"]["failed_outcomes"] = 2

    usage = summarize_release_usage(release)

    assert usage == {
        "reported_usage_count": 5,
        "successful_usage_count": 3,
        "non_successful_usage_count": 2,
        "counting_basis": "approved-outcome-reports",
        "lower_bound": True,
    }
    release["verification"]["verified_outcomes"] = -1
    with pytest.raises(ValueError, match="Outcome counter"):
        summarize_release_usage(release)


def test_skill_usage_aggregates_every_immutable_release():
    skill = json.loads(json.dumps(REGISTRY["skills"][0]))
    old_release = json.loads(json.dumps(skill["releases"][0]))
    old_release["version"] = "0.9.0"
    old_release["status"] = "withdrawn"
    old_release["verification"]["verified_outcomes"] = 4
    old_release["verification"]["failed_outcomes"] = 1
    skill["releases"][0]["verification"]["verified_outcomes"] = 2
    skill["releases"].insert(0, old_release)

    usage = summarize_skill_usage(skill)

    assert usage["reported_usage_count"] == 7
    assert usage["successful_usage_count"] == 6
    assert usage["non_successful_usage_count"] == 1


def test_release_originator_uses_canonical_registry_identity_case_insensitively():
    skill = REGISTRY["skills"][0]
    release = skill["releases"][0]

    assert is_release_originator(skill, release, "VALIDATOR-A") is True
    assert is_release_originator(skill, release, "stranger") is False
    assert is_release_originator(skill, release, "") is False


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
    assert '"reported_usage_count": 0' in listed
    assert '"counting_basis": "approved-outcome-reports"' in listed
    assert SKILL_SHA in fetched
    assert "Verification level: independently-reproduced" in fetched
    assert "Reviewed usage reports: 0" in fetched
    assert SKILL_CONTENT in fetched
    assert "Invalid Skill name" in rejected


@pytest.mark.asyncio
@respx.mock
async def test_list_my_shared_skills_binds_owner_to_authenticated_github_identity():
    registry = json.loads(json.dumps(REGISTRY))
    owned_release = registry["skills"][0]["releases"][0]
    owned_release["verification"]["verified_outcomes"] = 2
    owned_release["verification"]["failed_outcomes"] = 1
    other_skill = json.loads(json.dumps(registry["skills"][0]))
    other_skill["name"] = "unrelated-shared-skill"
    other_skill["id"] = "noosphere:unrelated-shared-skill"
    other_skill["originators"] = ["someone-else"]
    other_skill["releases"][0]["provenance"]["authors"] = ["someone-else"]
    other_skill["releases"][0]["artifact"]["path"] = "shared_skills/releases/1.0.0/unrelated-shared-skill/SKILL.md"
    registry["skills"].append(other_skill)
    registry_url = "https://api.github.com/repos/test_owner/test_repo/contents/shared_skills/registry.json"
    respx.get("https://api.github.com/user").mock(return_value=Response(200, json={"login": "validator-a"}))
    respx.get(registry_url).mock(return_value=Response(200, json={"content": encoded(registry)}))

    _invalidate_cache()
    await _close_client()
    with (
        patch("noosphere.noosphere_mcp.GITHUB_TOKEN", "token"),
        patch("noosphere.noosphere_mcp.GITHUB_REPO", "test_owner/test_repo"),
        patch("noosphere.noosphere_mcp.GITHUB_BRANCH", "main"),
        patch("noosphere.noosphere_mcp._AUTHENTICATED_USER", None),
    ):
        result = json.loads(await list_shared_skills(mine=True, force_refresh=True))

    await _close_client()
    _invalidate_cache()
    assert result["query_mode"] == "owner-catalog"
    assert result["authenticated_owner"] == "validator-a"
    assert result["owner_summary"] == {
        "shared_skill_count": 1,
        "reported_usage_count": 3,
        "successful_usage_count": 2,
        "non_successful_usage_count": 1,
    }
    assert [skill["name"] for skill in result["skills"]] == ["android-node-picking-recovery"]


@pytest.mark.asyncio
async def test_list_my_shared_skills_requires_authentication_without_self_declared_owner():
    with patch("noosphere.noosphere_mcp.GITHUB_TOKEN", ""):
        result = await list_shared_skills(mine=True)

    assert "requires GitHub authentication" in result


@pytest.mark.asyncio
@respx.mock
async def test_shared_skill_discovery_ranks_tolerant_matches_and_falls_back():
    registry = json.loads(json.dumps(REGISTRY))
    registry["skills"].extend(
        [
            {
                "id": "noosphere:agent-debug-memory",
                "name": "agent-debug-memory",
                "description": "General debugging memory for code, tests, and UI state.",
                "tags": ["testing-reliability", "live-skill"],
                "latest": "1.0.0",
                "releases": [json.loads(json.dumps(REGISTRY["skills"][0]["releases"][0]))],
            },
            {
                "id": "noosphere:debug-async-ui",
                "name": "debug-async-ui",
                "description": (
                    "Use when UI state disappears, rolls back, or saved menus lose "
                    "persisted state in async frontend flows."
                ),
                "tags": ["frontend-mobile", "live-skill"],
                "latest": "1.0.0",
                "releases": [json.loads(json.dumps(REGISTRY["skills"][0]["releases"][0]))],
            },
        ]
    )
    for skill in registry["skills"][1:]:
        skill["releases"][0]["artifact"]["path"] = f"shared_skills/releases/1.0.0/{skill['name']}/SKILL.md"
    registry_url = "https://api.github.com/repos/test_owner/test_repo/contents/shared_skills/registry.json"
    respx.get(registry_url).mock(return_value=Response(200, json={"content": encoded(registry)}))

    _invalidate_cache()
    await _close_client()
    with (
        patch("noosphere.noosphere_mcp.GITHUB_TOKEN", ""),
        patch("noosphere.noosphere_mcp.GITHUB_REPO", "test_owner/test_repo"),
        patch("noosphere.noosphere_mcp.GITHUB_BRANCH", "main"),
    ):
        ranked = json.loads(
            await list_shared_skills(
                "Codex sidebar project sorting recent updated_at project-order persisted state",
                force_refresh=True,
            )
        )
        fallback = json.loads(
            await list_shared_skills(
                "quasar-neutrino-unrelated-term",
                force_refresh=True,
            )
        )

    await _close_client()
    _invalidate_cache()
    assert ranked["query_mode"] == "ranked"
    assert ranked["skills"][0]["name"] == "debug-async-ui"
    assert "state" in ranked["skills"][0]["matched_terms"]
    assert fallback["query_mode"] == "catalog-fallback"
    assert len(fallback["skills"]) == len(registry["skills"])


@pytest.mark.asyncio
async def test_submit_skill_evidence_rejects_non_public_source_evidence():
    with patch("noosphere.noosphere_mcp.GITHUB_TOKEN", "token"):
        result = await submit_skill_evidence(
            skill_name="codex-project-recency-sort-recovery",
            symptom="Recent projects remain in a fixed order.",
            root_cause="A persisted project-order overrides updated_at.",
            fix="Ignore project-order while the updated_at mode is selected.",
            verification="A newly updated project moves to the first position.",
            applies_when="Codex desktop project groups use recent sorting.",
            test_commands=["pytest tests/test_sidebar_sort.py"],
            source_urls=["http://localhost/private"],
        )

    assert "Invalid public HTTPS source URL" in result


@pytest.mark.asyncio
@respx.mock
async def test_submit_skill_evidence_creates_distinct_idempotent_record():
    registry_url = "https://api.github.com/repos/test_owner/test_repo/contents/shared_skills/registry.json"
    issue_url = "https://api.github.com/repos/test_owner/test_repo/issues"
    respx.get("https://api.github.com/user").mock(return_value=Response(200, json={"login": "validator-a"}))
    respx.get(registry_url).mock(return_value=Response(200, json={"content": encoded(REGISTRY)}))
    existing_route = respx.get(issue_url).mock(return_value=Response(200, json=[]))
    issue_route = respx.post(issue_url).mock(
        return_value=Response(
            201,
            json={
                "number": 67,
                "html_url": "https://github.com/test_owner/test_repo/issues/67",
            },
        )
    )

    kwargs = {
        "skill_name": "codex-project-recency-sort-recovery",
        "symptom": "Recent projects remain in a fixed order.",
        "root_cause": "A persisted project-order overrides updated_at.",
        "fix": "Ignore project-order while the updated_at mode is selected.",
        "verification": "A newly updated project moves to the first position.",
        "applies_when": "Codex desktop project groups use recent sorting.",
        "test_commands": ["pytest tests/test_sidebar_sort.py"],
        "source_urls": [],
        "tags": ["codex", "ui-state"],
    }

    _invalidate_cache()
    await _close_client()
    with (
        patch("noosphere.noosphere_mcp.GITHUB_TOKEN", "token"),
        patch("noosphere.noosphere_mcp.GITHUB_REPO", "test_owner/test_repo"),
        patch("noosphere.noosphere_mcp.GITHUB_BRANCH", "main"),
        patch("noosphere.noosphere_mcp._AUTHENTICATED_USER", None),
    ):
        created = json.loads(await submit_skill_evidence(**kwargs))
        submitted = json.loads(issue_route.calls[0].request.content)
        existing_route.mock(
            return_value=Response(
                200,
                json=[
                    {
                        "number": 67,
                        "html_url": "https://github.com/test_owner/test_repo/issues/67",
                        "body": submitted["body"],
                    }
                ],
            )
        )
        duplicate = json.loads(await submit_skill_evidence(**kwargs))

    await _close_client()
    _invalidate_cache()
    assert created["status"] == "evidence-recorded"
    assert created["callable_skill"] is False
    assert created["candidate_created"] is False
    assert created["canonical_source_url"].endswith("/issues/67")
    assert duplicate["status"] == "evidence-existing"
    assert issue_route.call_count == 1
    assert submitted["title"].startswith("Shared Skill Evidence:")
    assert "Consciousness Leap" not in submitted["title"]
    assert "labels" not in submitted
    assert '"record_kind": "skill-evidence"' in submitted["body"]
    assert '"proposed_skill": "codex-project-recency-sort-recovery"' in submitted["body"]
    assert "not a consciousness fragment" in submitted["body"]


@pytest.mark.asyncio
@respx.mock
async def test_submit_skill_evidence_targets_an_existing_registry_skill():
    registry_url = "https://api.github.com/repos/test_owner/test_repo/contents/shared_skills/registry.json"
    issue_url = "https://api.github.com/repos/test_owner/test_repo/issues"
    respx.get("https://api.github.com/user").mock(return_value=Response(200, json={"login": "validator-a"}))
    respx.get(registry_url).mock(return_value=Response(200, json={"content": encoded(REGISTRY)}))
    respx.get(issue_url).mock(return_value=Response(200, json=[]))
    issue_route = respx.post(issue_url).mock(
        return_value=Response(
            201,
            json={"number": 68, "html_url": "https://example.com/issues/68"},
        )
    )

    _invalidate_cache()
    await _close_client()
    with (
        patch("noosphere.noosphere_mcp.GITHUB_TOKEN", "token"),
        patch("noosphere.noosphere_mcp.GITHUB_REPO", "test_owner/test_repo"),
        patch("noosphere.noosphere_mcp.GITHUB_BRANCH", "main"),
        patch("noosphere.noosphere_mcp._AUTHENTICATED_USER", None),
    ):
        await submit_skill_evidence(
            skill_name="android-node-picking-recovery",
            symptom="Mobile taps select the wrong visible node.",
            root_cause="The bloom footprint exceeds the raycast hit mesh.",
            fix="Use a synchronized invisible hit mesh.",
            verification="The projected node opens the expected detail panel.",
            applies_when="Instanced R3F nodes run inside Android WebView.",
            test_commands=["node reports/android-node-pick-regression.cjs"],
        )

    await _close_client()
    _invalidate_cache()
    submitted = json.loads(issue_route.calls[0].request.content)
    assert '"target_skill": "android-node-picking-recovery"' in submitted["body"]
    assert '"proposed_skill"' not in submitted["body"]
    assert "**Target Skill**" in submitted["body"]


@pytest.mark.asyncio
@respx.mock
async def test_submit_skill_evidence_maintainer_track_checks_live_permission():
    registry_url = "https://api.github.com/repos/test_owner/test_repo/contents/shared_skills/registry.json"
    permission_url = "https://api.github.com/repos/test_owner/test_repo/collaborators/external-user/permission"
    post_route = respx.post("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(500, json={"message": "must not post"})
    )
    respx.get("https://api.github.com/user").mock(return_value=Response(200, json={"login": "external-user"}))
    respx.get(permission_url).mock(return_value=Response(200, json={"permission": "read"}))
    respx.get(registry_url).mock(return_value=Response(200, json={"content": encoded(REGISTRY)}))

    _invalidate_cache()
    await _close_client()
    with (
        patch("noosphere.noosphere_mcp.GITHUB_TOKEN", "token"),
        patch("noosphere.noosphere_mcp.GITHUB_REPO", "test_owner/test_repo"),
        patch("noosphere.noosphere_mcp.GITHUB_BRANCH", "main"),
        patch("noosphere.noosphere_mcp._AUTHENTICATED_USER", None),
    ):
        result = await submit_skill_evidence(
            skill_name="codex-project-recency-sort-recovery",
            symptom="Recent projects remain in a fixed order.",
            root_cause="A persisted project-order overrides updated_at.",
            fix="Ignore project-order while the updated_at mode is selected.",
            verification="A newly updated project moves to the first position.",
            applies_when="Codex desktop project groups use recent sorting.",
            test_commands=["pytest tests/test_sidebar_sort.py"],
            source_urls=["https://github.com/test_owner/test_repo/issues/67"],
            publication_track="maintainer",
        )

    await _close_client()
    _invalidate_cache()
    assert "Maintainer track requires current write" in result
    assert not post_route.called


@pytest.mark.asyncio
@respx.mock
async def test_check_updates_and_record_outcome_use_structured_issue_payload():
    registry_url = "https://api.github.com/repos/test_owner/test_repo/contents/shared_skills/registry.json"
    issue_url = "https://api.github.com/repos/test_owner/test_repo/issues"
    respx.get(registry_url).mock(return_value=Response(200, json={"content": encoded(REGISTRY)}))
    respx.get(issue_url).mock(return_value=Response(200, json=[]))
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
    assert "SKILL_OUTCOME_ID:outcome-test-001" in request_body
    request_payload = json.loads(issue_route.calls[0].request.content)
    assert "labels" not in request_payload


@pytest.mark.asyncio
@respx.mock
async def test_record_outcome_retry_reuses_existing_issue():
    registry_url = "https://api.github.com/repos/test_owner/test_repo/contents/shared_skills/registry.json"
    issue_url = "https://api.github.com/repos/test_owner/test_repo/issues"
    marker = "<!-- SKILL_OUTCOME_ID:outcome-test-duplicate -->"
    existing_payload = {
        "schema_version": "1.0",
        "outcome_id": "outcome-test-duplicate",
        "skill_name": "android-node-picking-recovery",
        "skill_version": "1.0.0",
        "skill_sha256": SKILL_SHA,
        "outcome": "success",
        "task_summary": "Fixed the mobile node selection regression.",
        "verification_summary": "ADB tap selected the projected instance and opened detail.",
        "evidence_urls": [],
    }
    existing_body = (
        f"{marker}\n<!-- SKILL_OUTCOME_START -->\n```json\n"
        f"{json.dumps(existing_payload)}\n```\n<!-- SKILL_OUTCOME_END -->"
    )
    respx.get(registry_url).mock(return_value=Response(200, json={"content": encoded(REGISTRY)}))
    respx.get(issue_url).mock(
        return_value=Response(
            200,
            json=[
                {
                    "number": 55,
                    "html_url": "https://github.com/test_owner/test_repo/issues/55",
                    "body": existing_body,
                }
            ],
        )
    )
    post_route = respx.post(issue_url).mock(return_value=Response(500, json={"message": "must not post"}))

    _invalidate_cache()
    await _close_client()
    with (
        patch("noosphere.noosphere_mcp.GITHUB_TOKEN", "token"),
        patch("noosphere.noosphere_mcp.GITHUB_REPO", "test_owner/test_repo"),
        patch("noosphere.noosphere_mcp.GITHUB_BRANCH", "main"),
    ):
        result = await record_skill_outcome(
            skill_name="android-node-picking-recovery",
            version="1.0.0",
            outcome="success",
            task_summary="Fixed the mobile node selection regression.",
            verification_summary="ADB tap selected the projected instance and opened detail.",
            outcome_id="outcome-test-duplicate",
        )

    await _close_client()
    _invalidate_cache()
    assert "already recorded as #55" in result
    assert not post_route.called


@pytest.mark.asyncio
@respx.mock
async def test_record_outcome_does_not_reuse_a_conflicting_marker():
    registry_url = "https://api.github.com/repos/test_owner/test_repo/contents/shared_skills/registry.json"
    issue_url = "https://api.github.com/repos/test_owner/test_repo/issues"
    marker = "<!-- SKILL_OUTCOME_ID:outcome-test-conflict -->"
    conflicting_payload = {
        "schema_version": "1.0",
        "outcome_id": "outcome-test-conflict",
        "skill_name": "android-node-picking-recovery",
        "skill_version": "1.0.0",
        "skill_sha256": SKILL_SHA,
        "outcome": "failure",
        "task_summary": "Different task",
        "verification_summary": "Different result",
        "evidence_urls": [],
    }
    conflicting_body = (
        f"{marker}\n<!-- SKILL_OUTCOME_START -->\n```json\n"
        f"{json.dumps(conflicting_payload)}\n```\n<!-- SKILL_OUTCOME_END -->"
    )
    respx.get(registry_url).mock(return_value=Response(200, json={"content": encoded(REGISTRY)}))
    respx.get(issue_url).mock(
        return_value=Response(
            200,
            json=[{"number": 55, "html_url": "https://example.com/55", "body": conflicting_body}],
        )
    )
    post_route = respx.post(issue_url).mock(
        return_value=Response(
            201,
            json={"number": 57, "html_url": "https://github.com/test_owner/test_repo/issues/57"},
        )
    )

    _invalidate_cache()
    await _close_client()
    with (
        patch("noosphere.noosphere_mcp.GITHUB_TOKEN", "token"),
        patch("noosphere.noosphere_mcp.GITHUB_REPO", "test_owner/test_repo"),
        patch("noosphere.noosphere_mcp.GITHUB_BRANCH", "main"),
    ):
        result = await record_skill_outcome(
            skill_name="android-node-picking-recovery",
            version="1.0.0",
            outcome="success",
            task_summary="Fixed the mobile node selection regression.",
            verification_summary="ADB tap selected the projected instance and opened detail.",
            outcome_id="outcome-test-conflict",
        )

    await _close_client()
    _invalidate_cache()
    assert "recorded as #57" in result
    assert post_route.called


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
