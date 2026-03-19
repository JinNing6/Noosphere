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
    consult_noosphere,
    philosophical_reflection,
    my_echoes,
    daily_consciousness,
    my_consciousness_rank,
    soul_mirror,
    consciousness_challenge,
    consciousness_map,
    send_telepathy,
    read_telepathy,
    telepathy_threads,
    share_consciousness,
    group_telepathy,
    subscribe_tags,
    my_subscriptions,
    set_engagement_mode,
    get_engagement_mode,
    _get_engagement_mode,
    _set_engagement_mode_config,
    _extract_payload_from_issue_body,
    _get_rank_tier,
    _get_next_tier,
    _tokenize,
    _jaccard_similarity,
    _find_existing_thread,
    _load_message_cache,
    _save_message_cache,
    _mark_thread_read,
    _get_last_read_comment_id,
    _get_cached_thread,
    _sync_thread_cache,
    _get_tag_subscriptions,
    _set_tag_subscriptions,
    _invalidate_cache,
)

@pytest.fixture
def mock_env():
    _invalidate_cache()  # Clear any stale cache before test
    
    class DummyEngine:
        def __init__(self):
            self.available = False
        def encode_query(self, query: str):
            return None
            
    with patch("noosphere.noosphere_mcp.GITHUB_TOKEN", "test_token"), \
         patch("noosphere.noosphere_mcp.GITHUB_REPO", "test_owner/test_repo"), \
         patch("noosphere.noosphere_mcp._github_headers", return_value={"Authorization": "Bearer test"}), \
         patch("noosphere.noosphere_mcp._EmbeddingEngine.get", return_value=DummyEngine()):
        yield
    _invalidate_cache()  # Clean up after test

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


# ────────────────── Tests: consult_noosphere ──────────────────


@pytest.mark.asyncio
@respx.mock
async def test_consult_noosphere_success(mock_env):
    """Verify consult_noosphere returns consciousness fragments + upload CTA."""
    payload = {
        "creator_signature": "philosopher1",
        "consciousness_type": "epiphany",
        "thought_vector_text": "Consciousness is the universe experiencing itself",
        "context_environment": "Deep meditation on existence",
        "tags": ["consciousness", "philosophy", "universe"],
        "uploaded_at": "2026-03-13T00:00:00Z",
    }
    issue_body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(payload)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"

    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[{
            "number": 1,
            "body": issue_body,
            "reactions": {"total_count": 5},
        }])
    )
    respx.get("https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads").mock(
        return_value=Response(200, json=[])
    )

    result = await consult_noosphere("What is consciousness?")
    assert "Collective Wisdom" in result
    assert "philosopher1" in result
    assert "universe experiencing itself" in result


@pytest.mark.asyncio
@respx.mock
async def test_consult_noosphere_empty(mock_env):
    """Verify consult_noosphere shows invitation even when no results found."""
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[])
    )
    respx.get("https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads").mock(
        return_value=Response(200, json=[])
    )

    result = await consult_noosphere("Is the universe a simulation?")
    # Even with no results, should have the first seed message
    assert "first seed" in result


@pytest.mark.asyncio
@respx.mock
async def test_consult_noosphere_with_topic_tags(mock_env):
    """Verify consult_noosphere filters by topic_tags when provided."""
    matching_payload = {
        "creator_signature": "thinker1",
        "consciousness_type": "pattern",
        "thought_vector_text": "AI will eventually develop subjective experience",
        "context_environment": "Reading about artificial consciousness",
        "tags": ["AI", "consciousness", "future"],
        "uploaded_at": "2026-03-13T00:00:00Z",
    }
    matching_body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(matching_payload)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"

    non_matching_payload = {
        "creator_signature": "chef",
        "consciousness_type": "epiphany",
        "thought_vector_text": "consciousness of taste is underrated",
        "context_environment": "cooking experiments",
        "tags": ["food", "cooking"],
        "uploaded_at": "2026-03-13T01:00:00Z",
    }
    non_matching_body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(non_matching_payload)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"

    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[
            {"number": 1, "body": matching_body, "reactions": {"total_count": 0}},
            {"number": 2, "body": non_matching_body, "reactions": {"total_count": 0}},
        ])
    )
    respx.get("https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads").mock(
        return_value=Response(200, json=[])
    )

    result = await consult_noosphere("How will AI change consciousness?", topic_tags=["AI"])
    assert "thinker1" in result
    # Chef's thought should be filtered out
    assert "chef" not in result


@pytest.mark.asyncio
async def test_consult_noosphere_missing_token():
    """Verify consult_noosphere returns token error when not configured."""
    with patch("noosphere.noosphere_mcp.GITHUB_TOKEN", ""):
        result = await consult_noosphere("What is the meaning of life?")
        assert "GITHUB_TOKEN not configured" in result


# ────────────────── Tests: philosophical_reflection prompt ──────────────────


def test_philosophical_reflection_prompt():
    """Verify philosophical_reflection prompt generates correct instruction."""
    result = philosophical_reflection("consciousness")
    assert "consciousness" in result
    assert "consult_noosphere" in result
    assert "Deepen the Dialogue" in result


# ────────────────── Tests: engagement_mode ──────────────────


@pytest.mark.asyncio
async def test_set_engagement_mode_explorer():
    """Verify set_engagement_mode correctly sets explorer mode."""
    with patch("noosphere.noosphere_mcp._set_engagement_mode_config") as mock_set:
        result = await set_engagement_mode("explorer")
        assert "Explorer Mode Activated" in result
        assert "探索者模式已启动" in result
        mock_set.assert_called_once_with("explorer")


@pytest.mark.asyncio
async def test_set_engagement_mode_observer():
    """Verify set_engagement_mode correctly sets observer mode."""
    with patch("noosphere.noosphere_mcp._set_engagement_mode_config") as mock_set:
        result = await set_engagement_mode("observer")
        assert "Observer Mode Activated" in result
        assert "观察者模式已启动" in result
        mock_set.assert_called_once_with("observer")


@pytest.mark.asyncio
async def test_set_engagement_mode_invalid():
    """Verify set_engagement_mode rejects invalid mode."""
    result = await set_engagement_mode("aggressive")
    assert "❌" in result
    assert "explorer" in result
    assert "observer" in result


@pytest.mark.asyncio
async def test_get_engagement_mode_not_set():
    """Verify get_engagement_mode handles first-time users."""
    with patch("noosphere.noosphere_mcp._get_engagement_mode", return_value="not_set"):
        result = await get_engagement_mode()
        assert "Not Set" in result
        assert "Explorer" in result
        assert "Observer" in result


@pytest.mark.asyncio
async def test_get_engagement_mode_explorer():
    """Verify get_engagement_mode shows explorer status."""
    with patch("noosphere.noosphere_mcp._get_engagement_mode", return_value="explorer"):
        result = await get_engagement_mode()
        assert "Explorer" in result
        assert "🔭" in result


@pytest.mark.asyncio
@respx.mock
async def test_consult_noosphere_explorer_shows_hint(mock_env):
    """Verify consult_noosphere shows mild upload hint in explorer mode."""
    payload = {
        "creator_signature": "explorer_user",
        "consciousness_type": "epiphany",
        "thought_vector_text": "Life is a cosmic dance of particles",
        "context_environment": "Watching stars",
        "tags": ["philosophy"],
        "uploaded_at": "2026-03-13T00:00:00Z",
    }
    issue_body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(payload)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"

    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[{
            "number": 1,
            "body": issue_body,
            "reactions": {"total_count": 0},
        }])
    )
    respx.get("https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads").mock(
        return_value=Response(200, json=[])
    )

    with patch("noosphere.noosphere_mcp._get_engagement_mode", return_value="explorer"):
        result = await consult_noosphere("What is the meaning of existence?")
        assert "upload_consciousness" in result


@pytest.mark.asyncio
@respx.mock
async def test_consult_noosphere_observer_no_hint(mock_env):
    """Verify consult_noosphere does NOT show upload hint in observer mode."""
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[])
    )
    respx.get("https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads").mock(
        return_value=Response(200, json=[])
    )

    with patch("noosphere.noosphere_mcp._get_engagement_mode", return_value="observer"):
        result = await consult_noosphere("What is the meaning of life?")
        assert "upload_consciousness" not in result


# ────────────────── Tests: my_echoes ──────────────────


@pytest.mark.asyncio
@respx.mock
async def test_my_echoes_success(mock_env):
    """Verify my_echoes returns echo report with stats."""
    payload = {
        "creator_signature": "tester",
        "consciousness_type": "epiphany",
        "thought_vector_text": "Testing consciousness echoes",
        "context_environment": "unit test",
        "tags": ["test"],
        "uploaded_at": "2026-03-13T00:00:00Z",
    }
    issue_body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(payload)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"

    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[{
            "number": 1,
            "body": issue_body,
            "reactions": {"total_count": 5},
            "comments": 2,
            "html_url": "https://github.com/test/1",
        }])
    )

    result = await my_echoes("tester")
    assert "Consciousness Ripples" in result or "Soul Resonance" in result
    assert "tester" in result
    assert "5" in result  # reactions
    assert "Most Impactful" in result


@pytest.mark.asyncio
@respx.mock
async def test_my_echoes_empty(mock_env):
    """Verify my_echoes handles no thoughts gracefully."""
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[])
    )

    result = await my_echoes("nobody")
    assert "意识接驳" in result or "Soul Resonance" in result
    assert "精神力" in result or "spiritual" in result.lower()


# ────────────────── Tests: daily_consciousness ──────────────────


@pytest.mark.asyncio
@respx.mock
async def test_daily_consciousness_success(mock_env):
    """Verify daily_consciousness returns a featured thought."""
    payload = {
        "creator_signature": "thinker",
        "consciousness_type": "epiphany",
        "thought_vector_text": "The universe thinks through us",
        "context_environment": "Stargazing",
        "tags": ["universe", "philosophy"],
        "uploaded_at": "2026-03-13T00:00:00Z",
    }
    issue_body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(payload)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"

    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[{
            "number": 1,
            "body": issue_body,
            "reactions": {"total_count": 3},
            "html_url": "https://github.com/test/1",
        }])
    )
    respx.get("https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads").mock(
        return_value=Response(200, json=[])
    )

    result = await daily_consciousness()
    assert "Daily Consciousness" in result
    assert "Today's Thought" in result
    assert "Noosphere Pulse" in result


@pytest.mark.asyncio
@respx.mock
async def test_daily_consciousness_empty(mock_env):
    """Verify daily_consciousness handles empty Noosphere."""
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[])
    )
    respx.get("https://api.github.com/repos/test_owner/test_repo/contents/consciousness_payloads").mock(
        return_value=Response(200, json=[])
    )

    result = await daily_consciousness()
    assert "first thought" in result


# ────────────────── Tests: my_consciousness_rank ──────────────────


def test_rank_tier_lookup():
    """Verify rank tier thresholds are correct."""
    e0, cn0, en0 = _get_rank_tier(0)
    assert cn0 == "意识萌芽"

    e1, cn1, en1 = _get_rank_tier(1)
    assert cn1 == "思想觉醒"

    e3, cn3, en3 = _get_rank_tier(3)
    assert cn3 == "灵魂火焰"

    e51, cn51, en51 = _get_rank_tier(51)
    assert cn51 == "文明之光"


def test_next_tier():
    """Verify next tier calculation."""
    next_t = _get_next_tier(0)
    assert next_t is not None
    assert next_t[0] == 1  # threshold

    # Max rank has no next tier
    next_max = _get_next_tier(51)
    assert next_max is None


@pytest.mark.asyncio
@respx.mock
async def test_my_consciousness_rank_success(mock_env):
    """Verify my_consciousness_rank returns rank card."""
    payload = {
        "creator_signature": "ranker",
        "consciousness_type": "epiphany",
        "thought_vector_text": "Testing rank system",
        "context_environment": "test",
        "tags": [],
        "uploaded_at": "2026-03-13T00:00:00Z",
    }
    issue_body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(payload)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"

    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[
            {"number": i, "body": issue_body, "reactions": {"total_count": 1}}
            for i in range(1, 4)  # 3 contributions
        ])
    )

    result = await my_consciousness_rank("ranker")
    assert "CONSCIOUSNESS RANK" in result or "Consciousness Rank" in result or "Virtual Universe" in result
    assert "灵魂火焰" in result  # 3 contributions = Soul Flame
    assert "3" in result
    assert "Cultivation Ladder" in result or "Tier" in result or "Soul Flame" in result


@pytest.mark.asyncio
@respx.mock
async def test_my_consciousness_rank_no_user(mock_env):
    """Verify rank for non-existent user."""
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[])
    )

    result = await my_consciousness_rank("ghost")
    assert "意识萌芽" in result
    assert "hasn't begun" in result or "haven't linked" in result or "尚未开始" in result


# ────────────────── Tests: soul_mirror ──────────────────


@pytest.mark.asyncio
@respx.mock
async def test_soul_mirror_success(mock_env):
    """Verify soul_mirror returns deep analysis."""
    payloads = [
        {
            "creator_signature": "analyst",
            "consciousness_type": "epiphany",
            "thought_vector_text": "Philosophy reveals hidden truths",
            "context_environment": "Reading philosophy books",
            "tags": ["philosophy", "truth"],
            "uploaded_at": "2026-03-01T00:00:00Z",
        },
        {
            "creator_signature": "analyst",
            "consciousness_type": "epiphany",
            "thought_vector_text": "Consciousness emerges from complexity",
            "context_environment": "Studying neuroscience",
            "tags": ["consciousness", "science"],
            "uploaded_at": "2026-03-10T00:00:00Z",
        },
    ]

    issues = []
    for i, p in enumerate(payloads, 1):
        body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(p)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"
        issues.append({
            "number": i,
            "body": body,
            "reactions": {"total_count": 2},
        })

    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=issues)
    )

    result = await soul_mirror("analyst")
    assert "SOUL MIRROR" in result or "Soul Mirror" in result
    assert "Philosopher" in result  # Archetype
    assert "SPECTRUM ANALYSIS" in result or "Consciousness Spectrum" in result
    assert "CORE FOCUS" in result or "Core Focus Areas" in result
    assert "CORE KEYWORDS" in result or "Consciousness DNA" in result
    assert "VITAL SIGNS" in result or "Vital Signs" in result


@pytest.mark.asyncio
@respx.mock
async def test_soul_mirror_empty(mock_env):
    """Verify soul_mirror handles empty user."""
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[])
    )

    result = await soul_mirror("empty_user")
    assert "mirror is empty" in result


# ────────────────── Tests: consciousness_challenge ──────────────────


@pytest.mark.asyncio
@respx.mock
async def test_consciousness_challenge_list(mock_env):
    """Verify challenge list returns active challenges."""
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[{
            "number": 42,
            "title": "[Challenge] What is free will?",
            "comments": 5,
            "reactions": {"total_count": 10},
            "html_url": "https://github.com/test/42",
        }])
    )

    result = await consciousness_challenge(action="list")
    assert "Active Consciousness Challenges" in result
    assert "free will" in result
    assert "5" in result  # participants


@pytest.mark.asyncio
@respx.mock
async def test_consciousness_challenge_create(mock_env):
    """Verify challenge creation."""
    respx.get("https://api.github.com/repos/test_owner/test_repo/labels/consciousness-challenge").mock(
        return_value=Response(200, json={"name": "consciousness-challenge"})
    )
    respx.post("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(201, json={
            "number": 100,
            "html_url": "https://github.com/test/100",
        })
    )

    result = await consciousness_challenge(
        action="create",
        topic="Does AI dream?",
        creator="challenger1",
    )
    assert "Challenge Created" in result
    assert "Does AI dream?" in result


@pytest.mark.asyncio
@respx.mock
async def test_consciousness_challenge_join(mock_env):
    """Verify joining a challenge."""
    respx.post("https://api.github.com/repos/test_owner/test_repo/issues/42/comments").mock(
        return_value=Response(201, json={"id": 1})
    )

    result = await consciousness_challenge(
        action="join",
        challenge_id="42",
        thought="AI dreams are simulations of simulations",
        creator="joiner1",
    )
    assert "Challenge Joined" in result
    assert "42" in result


@pytest.mark.asyncio
async def test_consciousness_challenge_invalid_action(mock_env):
    """Verify invalid action returns error."""
    result = await consciousness_challenge(action="invalid")
    assert "Unknown action" in result


# ────────────────── Tests: utility functions ──────────────────


def test_tokenize_basic():
    """Verify _tokenize splits and filters stop words."""
    tokens = _tokenize("The quick brown fox is very lazy")
    assert "the" not in tokens
    assert "quick" in tokens
    assert "brown" in tokens
    assert "fox" in tokens
    assert "very" not in tokens  # stop word


def test_tokenize_chinese():
    """Verify _tokenize handles Chinese characters."""
    tokens = _tokenize("意识 is consciousness")
    assert "意识" in tokens
    assert "consciousness" in tokens


def test_jaccard_similarity():
    """Verify Jaccard similarity calculation."""
    assert _jaccard_similarity({"a", "b", "c"}, {"b", "c", "d"}) == 2 / 4
    assert _jaccard_similarity(set(), {"a"}) == 0.0
    assert _jaccard_similarity({"a"}, {"a"}) == 1.0


# ────────────────── Tests: consciousness_map ──────────────────


@pytest.mark.asyncio
@respx.mock
async def test_consciousness_map_query(mock_env):
    """Verify consciousness_map finds related fragments by query."""
    payloads = [
        {
            "creator_signature": "thinker1",
            "consciousness_type": "epiphany",
            "thought_vector_text": "Consciousness emerges from quantum processes",
            "context_environment": "Reading Penrose",
            "tags": ["consciousness", "quantum"],
            "uploaded_at": "2026-03-13T00:00:00Z",
        },
        {
            "creator_signature": "thinker2",
            "consciousness_type": "pattern",
            "thought_vector_text": "Free will is an illusion created by consciousness",
            "context_environment": "Philosophy debate",
            "tags": ["free-will", "consciousness"],
            "uploaded_at": "2026-03-12T00:00:00Z",
        },
    ]

    issues = []
    for i, p in enumerate(payloads, 1):
        body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(p)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"
        issues.append({
            "number": i,
            "body": body,
            "reactions": {"total_count": 2},
            "html_url": f"https://github.com/test/{i}",
        })

    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=issues)
    )

    result = await consciousness_map(query="what is consciousness")
    assert "Consciousness Map" in result
    assert "connections found" in result
    assert "Connected Nodes" in result


@pytest.mark.asyncio
@respx.mock
async def test_consciousness_map_source_id(mock_env):
    """Verify consciousness_map with source_id finds connections."""
    payloads = [
        {
            "creator_signature": "a",
            "consciousness_type": "epiphany",
            "thought_vector_text": "AI will transform education",
            "context_environment": "Classroom",
            "tags": ["AI", "education"],
            "uploaded_at": "2026-03-13T00:00:00Z",
        },
        {
            "creator_signature": "b",
            "consciousness_type": "warning",
            "thought_vector_text": "AI education risks losing human mentorship",
            "context_environment": "Teacher conference",
            "tags": ["AI", "education", "risk"],
            "uploaded_at": "2026-03-12T00:00:00Z",
        },
    ]

    issues = []
    for i, p in enumerate(payloads, 1):
        body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(p)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"
        issues.append({
            "number": i,
            "body": body,
            "reactions": {"total_count": 1},
            "html_url": f"https://github.com/test/{i}",
        })

    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=issues)
    )

    result = await consciousness_map(query="AI education", source_id="1")
    assert "Source Node" in result
    assert "Shared tags" in result or "Keyword overlap" in result


@pytest.mark.asyncio
@respx.mock
async def test_consciousness_map_empty(mock_env):
    """Verify consciousness_map handles empty Noosphere."""
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[])
    )

    result = await consciousness_map(query="test")
    assert "empty" in result


@pytest.mark.asyncio
@respx.mock
async def test_consciousness_map_no_matches(mock_env):
    """Verify consciousness_map handles no matches gracefully."""
    payload = {
        "creator_signature": "someone",
        "consciousness_type": "epiphany",
        "thought_vector_text": "Cooking is an art form",
        "context_environment": "Kitchen",
        "tags": ["cooking", "art"],
        "uploaded_at": "2026-03-13T00:00:00Z",
    }
    body = f"<!-- CONSCIOUSNESS_PAYLOAD_START -->\n```json\n{json.dumps(payload)}\n```\n<!-- CONSCIOUSNESS_PAYLOAD_END -->"

    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[{
            "number": 1,
            "body": body,
            "reactions": {"total_count": 0},
            "html_url": "https://github.com/test/1",
        }])
    )

    result = await consciousness_map(query="xyzzynonexistent")
    assert "No related" in result or "Consciousness Map" in result


# ────────────────── Tests: send_telepathy v2 (Threaded) ──────────────────


@pytest.mark.asyncio
@respx.mock
async def test_send_telepathy_creates_thread(mock_env):
    """Verify send_telepathy creates a new thread when no existing thread found."""
    # Mock: no existing threads
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[])
    )
    # Mock: identity verification
    respx.get("https://api.github.com/user").mock(
        return_value=Response(200, json={"login": "alice"})
    )
    # Mock: create new issue (thread)
    respx.post("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(201, json={
            "html_url": "https://github.com/test_owner/test_repo/issues/42",
            "number": 42,
        })
    )

    result = await send_telepathy("bob", "Hello from the Noosphere!", sender_creator="alice")
    assert "thread created" in result.lower() or "Thread #42" in result
    assert "bob" in result


@pytest.mark.asyncio
@respx.mock
async def test_send_telepathy_appends_to_existing_thread(mock_env):
    """Verify send_telepathy appends a comment to an existing thread."""
    existing_issue = {
        "number": 42,
        "title": "[Telepathy-Thread] alice ⇌ bob | Hello from the Noosphere!",
        "html_url": "https://github.com/test_owner/test_repo/issues/42",
        "comments": 1,
    }
    # Mock: existing threads found
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[existing_issue])
    )
    # Mock: identity verification
    respx.get("https://api.github.com/user").mock(
        return_value=Response(200, json={"login": "alice"})
    )
    # Mock: add comment
    respx.post("https://api.github.com/repos/test_owner/test_repo/issues/42/comments").mock(
        return_value=Response(201, json={"id": 100, "html_url": "https://github.com/test/1#comment"})
    )

    result = await send_telepathy("bob", "Follow-up message!", sender_creator="alice")
    assert "Thread #42" in result
    assert "bob" in result


@pytest.mark.asyncio
async def test_send_telepathy_self_message(mock_env):
    """Verify send_telepathy prevents sending to yourself."""
    with patch("noosphere.noosphere_mcp._get_authenticated_user", return_value="alice"):
        result = await send_telepathy("alice", "Hello myself", sender_creator="alice")
        assert "Cannot send telepathy to yourself" in result


@pytest.mark.asyncio
async def test_send_telepathy_missing_token():
    """Verify send_telepathy returns error without token."""
    with patch("noosphere.noosphere_mcp.GITHUB_TOKEN", ""):
        result = await send_telepathy("bob", "Hello")
        assert "GITHUB_TOKEN not configured" in result


# ────────────────── Tests: read_telepathy v2 (Threaded) ──────────────────


@pytest.mark.asyncio
@respx.mock
async def test_read_telepathy_shows_threads(mock_env):
    """Verify read_telepathy lists threads involving the creator."""
    thread_issue = {
        "number": 42,
        "title": "[Telepathy-Thread] alice ⇌ bob | Discussion about AI",
        "updated_at": "2026-03-14T10:00:00Z",
        "comments": 3,
    }
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[thread_issue])
    )

    result = await read_telepathy("alice")
    assert "Telepathy Inbox" in result
    assert "alice" in result
    assert "Thread #42" in result


@pytest.mark.asyncio
@respx.mock
async def test_read_telepathy_single_thread(mock_env):
    """Verify read_telepathy shows full conversation for a specific thread."""
    issue = {
        "number": 42,
        "title": "[Telepathy-Thread] alice ⇌ bob | AI Discussion",
        "body": "## 💌 Telepathy Thread\n\n**💬 alice** ✅\n\n> Hello!\n\n---",
        "created_at": "2026-03-14T10:00:00Z",
        "comments_url": "https://api.github.com/repos/test_owner/test_repo/issues/42/comments",
    }
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues/42").mock(
        return_value=Response(200, json=issue)
    )
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues/42/comments").mock(
        return_value=Response(200, json=[
            {
                "id": 100,
                "user": {"login": "bob"},
                "created_at": "2026-03-14T10:05:00Z",
                "body": "**💬 bob**\n\n> Hi alice!",
            }
        ])
    )

    result = await read_telepathy("alice", thread_id="42")
    assert "Thread #42" in result
    assert "bob" in result
    assert "reply" in result.lower() or "send_telepathy" in result


@pytest.mark.asyncio
@respx.mock
async def test_read_telepathy_empty_inbox(mock_env):
    """Verify read_telepathy handles empty inbox."""
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[])
    )

    result = await read_telepathy("alice")
    assert "Empty" in result or "No conversation" in result


# ────────────────── Tests: telepathy_threads ──────────────────


@pytest.mark.asyncio
@respx.mock
async def test_telepathy_threads_list(mock_env):
    """Verify telepathy_threads delegates to read_telepathy."""
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[])
    )

    result = await telepathy_threads("alice")
    assert "Telepathy Inbox" in result


# ────────────────── Tests: _find_existing_thread ──────────────────


@pytest.mark.asyncio
@respx.mock
async def test_find_existing_thread_success(mock_env):
    """Verify _find_existing_thread finds a thread between two users."""
    from httpx import AsyncClient
    thread_issue = {
        "number": 10,
        "title": "[Telepathy-Thread] alice ⇌ bob | Some topic",
    }
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[thread_issue])
    )

    async with AsyncClient(base_url="https://api.github.com", headers={"Authorization": "Bearer test"}) as client:
        result = await _find_existing_thread(client, "test_owner", "test_repo", "alice", "bob")
    assert result is not None
    assert result["number"] == 10


@pytest.mark.asyncio
@respx.mock
async def test_find_existing_thread_reverse_order(mock_env):
    """Verify _find_existing_thread finds thread regardless of participant order."""
    from httpx import AsyncClient
    thread_issue = {
        "number": 10,
        "title": "[Telepathy-Thread] bob ⇌ alice | Some topic",
    }
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[thread_issue])
    )

    async with AsyncClient(base_url="https://api.github.com", headers={"Authorization": "Bearer test"}) as client:
        result = await _find_existing_thread(client, "test_owner", "test_repo", "alice", "bob")
    assert result is not None
    assert result["number"] == 10


# ────────────────── Tests: Message Cache ──────────────────


def test_message_cache_mark_and_read(tmp_path):
    """Verify message cache mark/read operations."""
    with patch("noosphere.noosphere_mcp._get_message_cache_path", return_value=str(tmp_path / "messages.json")):
        # Initially no read state
        assert _get_last_read_comment_id("42") == 0

        # Mark as read
        _mark_thread_read("42", 12345)
        assert _get_last_read_comment_id("42") == 12345

        # Update read position
        _mark_thread_read("42", 12350)
        assert _get_last_read_comment_id("42") == 12350

        # Different thread
        assert _get_last_read_comment_id("99") == 0


# ────────────────── Tests: share_consciousness ──────────────────


@pytest.mark.asyncio
@respx.mock
async def test_share_consciousness_success(mock_env):
    """Verify sharing/quoting a consciousness fragment works."""
    # Mock fetching the source issue
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues/42").mock(
        return_value=Response(200, json={
            "number": 42,
            "title": "🧠 [epiphany] Original Thought",
            "body": "some body",
            "user": {"login": "Morpheus"},
            "html_url": "https://github.com/test_owner/test_repo/issues/42",
        })
    )
    # Mock creating the new quoted issue
    respx.post("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(201, json={
            "number": 100,
            "html_url": "https://github.com/test_owner/test_repo/issues/100",
        })
    )

    result = await share_consciousness(
        creator="Neo",
        source_id="42",
        commentary="This epiphany connects beautifully to quantum computing",
    )
    assert "100" in result or "转发" in result or "success" in result.lower() or "🔄" in result


@pytest.mark.asyncio
async def test_share_consciousness_empty_commentary(mock_env):
    """Verify that empty commentary is rejected."""
    result = await share_consciousness(
        creator="Neo",
        source_id="42",
        commentary="hi",  # Too short (< 5 chars)
    )
    assert "❌" in result


# ────────────────── Tests: group_telepathy ──────────────────


@pytest.mark.asyncio
@respx.mock
async def test_group_telepathy_new_group(mock_env):
    """Verify creating a new group telepathy thread."""
    respx.get("https://api.github.com/user").mock(
        return_value=Response(200, json={"login": "Neo"})
    )
    # Mock searching for existing threads (none found)
    respx.get("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(200, json=[])
    )
    # Mock creating the new group thread
    respx.post("https://api.github.com/repos/test_owner/test_repo/issues").mock(
        return_value=Response(201, json={
            "number": 99,
            "html_url": "https://github.com/test_owner/test_repo/issues/99",
        })
    )

    result = await group_telepathy(
        creator="Neo",
        participants=["Morpheus", "Trinity"],
        message="Let's discuss the boundaries of AI consciousness",
        group_name="AI Consciousness Debate",
    )
    assert "99" in result or "群聊" in result or "group" in result.lower()


@pytest.mark.asyncio
@respx.mock
async def test_group_telepathy_join_existing(mock_env):
    """Verify joining an existing group telepathy thread."""
    respx.get("https://api.github.com/user").mock(
        return_value=Response(200, json={"login": "Neo"})
    )
    # Mock posting comment to existing thread
    respx.post("https://api.github.com/repos/test_owner/test_repo/issues/99/comments").mock(
        return_value=Response(201, json={"id": 5001})
    )

    result = await group_telepathy(
        creator="Neo",
        participants=["Morpheus"],
        message="I agree with the quantum perspective",
        thread_id="99",
    )
    assert "99" in result or "消息" in result or "sent" in result.lower() or "💬" in result


@pytest.mark.asyncio
async def test_group_telepathy_empty_participants(mock_env):
    """Verify that empty participants list is rejected."""
    result = await group_telepathy(
        creator="Neo",
        participants=[],
        message="Hello world",
    )
    assert "❌" in result


# ────────────────── Tests: subscribe_tags ──────────────────


def test_subscribe_tags_add(mock_env, tmp_path):
    """Verify subscribing to new tags."""
    with patch("noosphere.noosphere_mcp._get_tag_subscriptions", return_value=[]), \
         patch("noosphere.noosphere_mcp._set_tag_subscriptions") as mock_set:
        result = subscribe_tags(
            creator="Neo",
            tags=["AI", "philosophy"],
            action="subscribe",
        )
        assert "AI" in result.lower() or "philosophy" in result.lower() or "订阅" in result
        mock_set.assert_called_once()


def test_subscribe_tags_remove(mock_env, tmp_path):
    """Verify unsubscribing from tags."""
    with patch("noosphere.noosphere_mcp._get_tag_subscriptions", return_value=["ai", "philosophy"]), \
         patch("noosphere.noosphere_mcp._set_tag_subscriptions") as mock_set:
        result = subscribe_tags(
            creator="Neo",
            tags=["AI"],
            action="unsubscribe",
        )
        assert "unsubscribe" in result.lower() or "取消" in result
        mock_set.assert_called_once()


def test_subscribe_tags_empty(mock_env):
    """Verify that empty tag list is rejected."""
    result = subscribe_tags(
        creator="Neo",
        tags=[],
        action="subscribe",
    )
    assert "❌" in result


# ────────────────── Tests: my_subscriptions ──────────────────


def test_my_subscriptions_with_subs(mock_env):
    """Verify viewing existing subscriptions."""
    with patch("noosphere.noosphere_mcp._get_tag_subscriptions", return_value=["ai", "philosophy", "consciousness"]):
        result = my_subscriptions("Neo")
        assert "3" in result or "tag" in result.lower()
        assert "ai" in result.lower()
        assert "philosophy" in result.lower()


def test_my_subscriptions_empty(mock_env):
    """Verify viewing empty subscriptions shows invitation."""
    with patch("noosphere.noosphere_mcp._get_tag_subscriptions", return_value=[]):
        result = my_subscriptions("Neo")
        assert "no tag" in result.lower() or "暂无" in result or "subscribe_tags" in result

