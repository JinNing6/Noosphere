import json
import pytest
import respx
from httpx import Response
from unittest.mock import patch
import base64

from noosphere.noosphere_mcp import (
    upload_consciousness,
    telepath,
    hologram,
    resonate_consciousness,
    get_consciousness_profile,
    discover_resonance,
    discuss_consciousness,
    merge_consciousness,
    trace_evolution,
    _extract_payload_from_issue_body
)

@pytest.fixture
def mock_env():
    with patch("noosphere.noosphere_mcp.GITHUB_TOKEN", "test_token"), \
         patch("noosphere.noosphere_mcp.GITHUB_REPO", "test_owner/test_repo"), \
         patch("noosphere.noosphere_mcp._github_headers", return_value={"Authorization": "Bearer test"}):
        yield

def test_extract_payload():
    payload = {"key": "value"}
    body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(payload)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"
    extracted = _extract_payload_from_issue_body(body)
    assert extracted == payload

@pytest.mark.asyncio
async def test_upload_consciousness_missing_token():
    with patch("noosphere.noosphere_mcp.GITHUB_TOKEN", ""):
        result = await upload_consciousness("user1", "epiphany", "This is a long enough thought for testing the missing token case.", "long enough context here")
        assert "GITHUB_TOKEN not configured" in result

@pytest.mark.asyncio
async def test_upload_consciousness_invalid_type(mock_env):
    result = await upload_consciousness("user1", "invalid_type", "This is a long enough thought for testing the invalid type case.", "long enough context here")
    assert "Invalid consciousness type" in result

@pytest.mark.asyncio
async def test_upload_consciousness_short_context(mock_env):
    result = await upload_consciousness("user1", "epiphany", "This is a long enough thought for testing the short context case.", "short")
    assert "Context description too short" in result

@pytest.mark.asyncio
async def test_upload_consciousness_short_thought(mock_env):
    result = await upload_consciousness("user1", "epiphany", "too short", "long enough context here")
    assert "Core thought too short" in result

@pytest.mark.asyncio
@respx.mock
async def test_upload_consciousness_success(mock_env):
    respx.post("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(201, json={"html_url": "http://github.com/issue/1", "number": 1})
    )
    result = await upload_consciousness("user1", "epiphany", "This is a long enough thought for testing success case.", "Test context long enough")
    assert "Consciousness Leap Complete!" in result
    assert "This is a long enough thought" in result

@pytest.mark.asyncio
@respx.mock
async def test_telepath_success(mock_env):
    issue_payload = {
        "creator_signature": "user1",
        "consciousness_type": "epiphany",
        "thought_vector_text": "SearchTarget",
        "context_environment": "Test context",
        "tags": ["test"]
    }
    issue_body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(issue_payload)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"
    
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[{
            "number": 1,
            "body": issue_body
        }])
    )
    
    respx.get("https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads").mock(
        return_value=Response(200, json=[])
    )
    
    result = await telepath("SearchTarget")
    assert "SearchTarget" in result
    assert "user1" in result

@pytest.mark.asyncio
@respx.mock
async def test_hologram_success(mock_env):
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[])
    )
    respx.get("https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads").mock(
        return_value=Response(200, json=[])
    )
    
    result = await hologram()
    assert "empty" in result

@pytest.mark.asyncio
@respx.mock
async def test_resonate_consciousness_success(mock_env):
    respx.post("https://api.github.com/repos/test_owner/test_repo/issues/42/reactions").mock(
        return_value=Response(201, json={"id": 1, "content": "heart"})
    )
    result = await resonate_consciousness("42", "heart")
    assert "successfully synchronized" in result

@pytest.mark.asyncio
async def test_resonate_consciousness_invalid_reaction(mock_env):
    result = await resonate_consciousness("42", "invalid")
    assert "Invalid reaction" in result

@pytest.mark.asyncio
@respx.mock
async def test_get_consciousness_profile_success(mock_env):
    issue_payload = {
        "creator_signature": "user1",
        "is_anonymous": False,
        "consciousness_type": "epiphany",
        "thought_vector_text": "I am who I am",
        "context_environment": "Test context",
        "tags": ["identity"]
    }
    issue_body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(issue_payload)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"
    
    anon_payload = {
        "creator_signature": "user1",
        "is_anonymous": True,
        "consciousness_type": "pattern",
        "thought_vector_text": "Anonymous thought",
        "context_environment": "Test context 2"
    }
    anon_body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(anon_payload)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"

    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[
            {"number": 1, "body": issue_body},
            {"number": 2, "body": anon_body}
        ])
    )
    
    respx.get("https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads").mock(
        return_value=Response(200, json=[])
    )
    
    result = await get_consciousness_profile("user1")
    assert "Digital Soul Profile: user1" in result
    assert "Total Fragments" in result
    assert "I am who I am" in result
    assert "Anonymous thought" not in result

@pytest.mark.asyncio
@respx.mock
async def test_get_consciousness_profile_empty(mock_env):
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[])
    )
    respx.get("https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads").mock(
        return_value=Response(200, json=[])
    )
    result = await get_consciousness_profile("unknown_user")
    assert "No signed consciousness fragments found" in result


@pytest.mark.asyncio
@respx.mock
async def test_telepath_resonance_sorting(mock_env):
    """Verify that telepath sorts results by relevance first, then by resonance (secondary)."""
    # Issue with low resonance
    payload_low = {
        "creator_signature": "userA",
        "consciousness_type": "epiphany",
        "thought_vector_text": "SearchKeyword idea low",
        "context_environment": "ctx",
        "tags": ["test"]
    }
    body_low = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(payload_low)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"

    # Issue with high resonance
    payload_high = {
        "creator_signature": "userB",
        "consciousness_type": "pattern",
        "thought_vector_text": "SearchKeyword idea high",
        "context_environment": "ctx",
        "tags": ["test"]
    }
    body_high = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(payload_high)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"

    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[
            {"number": 1, "body": body_low,  "reactions": {"total_count": 2}},
            {"number": 2, "body": body_high, "reactions": {"total_count": 10}},
        ])
    )
    respx.get("https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads").mock(
        return_value=Response(200, json=[])
    )

    result = await telepath("SearchKeyword")
    assert "Resonance" in result
    # userB (resonance=10) should appear before userA (resonance=2) since relevance is same
    pos_b = result.index("userB")
    pos_a = result.index("userA")
    assert pos_b < pos_a, f"Expected userB (higher resonance) before userA, but got userB@{pos_b} userA@{pos_a}"


@pytest.mark.asyncio
@respx.mock
async def test_hologram_trending_thoughts(mock_env):
    """Verify that hologram displays Trending Thoughts when issues have reactions."""
    payload = {
        "creator_signature": "trendUser",
        "is_anonymous": False,
        "consciousness_type": "epiphany",
        "thought_vector_text": "This thought sparks joy",
        "context_environment": "A creative moment",
        "tags": ["trending"]
    }
    issue_body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(payload)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"

    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[{
            "number": 1,
            "body": issue_body,
            "html_url": "https://github.com/test_owner/test_repo/issues/1",
            "reactions": {"total_count": 5}
        }])
    )
    respx.get("https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads").mock(
        return_value=Response(200, json=[])
    )

    result = await hologram()
    assert "Trending Thoughts" in result
    assert "trendUser" in result
    assert "This thought sparks joy" in result
    assert "View Node" in result


@pytest.mark.asyncio
@respx.mock
async def test_discover_resonance_success(mock_env):
    """Verify discover_resonance finds similar thoughts from other creators."""
    # My thought (creator = me)
    my_payload = {
        "creator_signature": "me",
        "is_anonymous": False,
        "consciousness_type": "epiphany",
        "thought_vector_text": "artificial intelligence will change education",
        "context_environment": "thinking about future learning",
        "tags": ["AI", "education", "future"]
    }
    my_body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(my_payload)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"

    # Other person's thought (shares tags)
    other_payload = {
        "creator_signature": "otherUser",
        "is_anonymous": False,
        "consciousness_type": "pattern",
        "thought_vector_text": "AI is transforming education systems worldwide",
        "context_environment": "reviewing education technology",
        "tags": ["AI", "education"]
    }
    other_body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(other_payload)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"

    # Unrelated thought
    unrelated_payload = {
        "creator_signature": "stranger",
        "is_anonymous": False,
        "consciousness_type": "warning",
        "thought_vector_text": "banana recipes are getting worse",
        "context_environment": "cooking experiments",
        "tags": ["food", "cooking"]
    }
    unrelated_body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(unrelated_payload)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"

    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[
            {"number": 1, "body": my_body, "html_url": "url1", "reactions": {"total_count": 0}},
            {"number": 2, "body": other_body, "html_url": "url2", "reactions": {"total_count": 3}},
            {"number": 3, "body": unrelated_body, "html_url": "url3", "reactions": {"total_count": 0}},
        ])
    )
    respx.get("https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads").mock(
        return_value=Response(200, json=[])
    )

    result = await discover_resonance("me")
    assert "Resonance Discovery" in result
    assert "otherUser" in result
    assert "AI" in result
    assert "education" in result
    # Unrelated thought should not appear (or rank very low)
    assert "banana" not in result


@pytest.mark.asyncio
@respx.mock
async def test_discover_resonance_no_profile(mock_env):
    """Verify discover_resonance returns error when user has no fragments."""
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[])
    )
    respx.get("https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads").mock(
        return_value=Response(200, json=[])
    )

    result = await discover_resonance("nobody")
    assert "no signed consciousness fragments found" in result


@pytest.mark.asyncio
@respx.mock
async def test_discover_resonance_no_matches(mock_env):
    """Verify discover_resonance handles case where no similar minds exist."""
    my_payload = {
        "creator_signature": "me",
        "is_anonymous": False,
        "consciousness_type": "epiphany",
        "thought_vector_text": "quantum entanglement in biological systems",
        "context_environment": "reading quantum biology papers",
        "tags": ["quantum", "biology"]
    }
    my_body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(my_payload)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"

    # Completely unrelated other thought
    other_payload = {
        "creator_signature": "chef",
        "is_anonymous": False,
        "consciousness_type": "pattern",
        "thought_vector_text": "pasta dough needs more salt",
        "context_environment": "kitchen experiments",
        "tags": ["food", "cooking"]
    }
    other_body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(other_payload)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"

    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[
            {"number": 1, "body": my_body, "html_url": "url1", "reactions": {"total_count": 0}},
            {"number": 2, "body": other_body, "html_url": "url2", "reactions": {"total_count": 0}},
        ])
    )
    respx.get("https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads").mock(
        return_value=Response(200, json=[])
    )

    result = await discover_resonance("me")
    assert "No matching minds" in result


# ────────────────── Tests: discuss_consciousness ──────────────────


@pytest.mark.asyncio
@respx.mock
async def test_discuss_consciousness_read_empty(mock_env):
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues/1/comments").mock(
        return_value=Response(200, json=[])
    )
    result = await discuss_consciousness("1")
    assert "No discussion yet" in result


@pytest.mark.asyncio
@respx.mock
async def test_discuss_consciousness_read_comments(mock_env):
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues/1/comments").mock(
        return_value=Response(200, json=[
            {
                "user": {"login": "alice"},
                "created_at": "2026-03-13T00:00:00Z",
                "body": "Great insight!",
                "reactions": {"total_count": 3},
            }
        ])
    )
    result = await discuss_consciousness("1")
    assert "1 comments" in result
    assert "@alice" in result
    assert "Great insight!" in result


@pytest.mark.asyncio
@respx.mock
async def test_discuss_consciousness_add_comment(mock_env):
    respx.post("https://api.github.com/repos/test_owner/test_repo/issues/1/comments").mock(
        return_value=Response(201, json={"html_url": "https://github.com/test/1#comment"})
    )
    result = await discuss_consciousness("1", comment="My perspective")
    assert "Comment successfully added" in result


# ────────────────── Tests: merge_consciousness ──────────────────


@pytest.mark.asyncio
async def test_merge_consciousness_too_few_ids(mock_env):
    result = await merge_consciousness("me", ["1"], "merged text for testing", "test context")
    assert "at least 2" in result


@pytest.mark.asyncio
@respx.mock
async def test_merge_consciousness_success(mock_env):
    payload1 = {
        "consciousness_type": "epiphany",
        "thought_vector_text": "First insight about consciousness",
        "context_environment": "morning reflection",
        "tags": ["ai", "philosophy"],
        "creator_signature": "alice",
        "uploaded_at": "2026-03-12T10:00:00Z",
    }
    payload2 = {
        "consciousness_type": "pattern",
        "thought_vector_text": "Second insight about patterns",
        "context_environment": "code review",
        "tags": ["ai", "patterns"],
        "creator_signature": "bob",
        "uploaded_at": "2026-03-12T11:00:00Z",
    }
    body1 = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(payload1)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"
    body2 = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(payload2)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"

    respx.get("https://api.github.com/repos/test_owner/test_repo/issues/1").mock(
        return_value=Response(200, json={"body": body1})
    )
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues/2").mock(
        return_value=Response(200, json={"body": body2})
    )
    respx.post("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(201, json={"number": 10, "html_url": "https://github.com/test/10"})
    )

    result = await merge_consciousness(
        "me", ["1", "2"],
        "A synthesis of consciousness and patterns into unified understanding",
        "merging two complementary insights",
    )
    assert "Merge Complete" in result
    assert "Issue #10" in result


# ────────────────── Tests: trace_evolution ──────────────────


@pytest.mark.asyncio
@respx.mock
async def test_trace_evolution_not_found(mock_env):
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[])
    )
    respx.get("https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads").mock(
        return_value=Response(200, json=[])
    )
    result = await trace_evolution("999")
    assert "not found" in result


@pytest.mark.asyncio
@respx.mock
async def test_trace_evolution_success(mock_env):
    payload = {
        "consciousness_type": "epiphany",
        "thought_vector_text": "Root thought about AI consciousness",
        "context_environment": "deep thinking",
        "tags": ["ai"],
        "creator_signature": "pioneer",
        "uploaded_at": "2026-03-10T00:00:00Z",
    }
    body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(payload)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"

    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[
            {"number": 1, "body": body, "html_url": "url1", "labels": [], "reactions": {"total_count": 2}},
        ])
    )
    respx.get("https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads").mock(
        return_value=Response(200, json=[])
    )

    result = await trace_evolution("1")
    assert "Evolution Trace" in result
    assert "Root thought" in result
