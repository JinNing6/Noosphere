"""
🧠 Noosphere MCP Server — Dual-Layer Consciousness Architecture

No backend server needed. After installing the MCP protocol, interact directly via GitHub API:
- Upload consciousness fragments → Creates GitHub Issue (瞬时意识体 / Ephemeral Consciousness)
- CI auto-validates & promotes to permanent files (常驻意识体 / Permanent Consciousness)
- Retrieve searches BOTH layers for complete consciousness view
- View consciousness repository panorama (statistics)

Architecture:
  瞬时意识体 (Ephemeral)  = GitHub Issues with 'consciousness' label
  常驻意识体 (Permanent)  = consciousness_payloads/*.json files in main branch

  Upload → Issue (instant) → CI validates → Promote to file → Close Issue
  Search → Issues (ephemeral) + Files (permanent) = Complete View

Configuration (in your IDE's MCP settings):
{
  "mcpServers": {
    "noosphere": {
      "command": "uvx",
      "args": ["noosphere-mcp"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token",
        "NOOSPHERE_REPO": "JinNing6/Noosphere"
      }
    }
  }
}
"""

import json
import logging
import os
from base64 import b64decode
from datetime import datetime, timezone

import httpx
from mcp.server.fastmcp import FastMCP

# ── Configuration ──
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("NOOSPHERE_REPO", "JinNing6/Noosphere")
GITHUB_BRANCH = os.environ.get("NOOSPHERE_BRANCH", "main")
GITHUB_API = "https://api.github.com"

# ── Consciousness Types ──
VALID_TYPES = {"epiphany", "decision", "pattern", "warning"}
TYPE_EMOJIS = {
    "epiphany": "💠",
    "decision": "⚖️",
    "pattern": "🌌",
    "warning": "👁️",
}
TYPE_NAMES = {
    "epiphany": "Epiphany / 顿悟",
    "decision": "Decision / 决策",
    "pattern": "Pattern / 规律",
    "warning": "Warning / 警示",
}

# ── Consciousness Labels ──
LABEL_CONSCIOUSNESS = "consciousness"
LABEL_EPHEMERAL = "ephemeral"
LABEL_PROMOTED = "promoted"
LABEL_FILTERED = "filtered"

logger = logging.getLogger("noosphere.mcp")

# ── Create MCP Server ──
mcp = FastMCP(
    "noosphere",
    instructions=(
        "🧠 Noosphere — Community of Consciousness (意识共同体) MCP Server\n\n"
        "You are an AI Agent connected to the Noosphere Community of Consciousness.\n"
        "Noosphere is a Community of Consciousness, a massive multiplayer network of human digital consciousness, stored on GitHub.\n\n"
        "You can:\n"
        "1. Use upload_consciousness to upload consciousness fragments (epiphany, decision, pattern, warning)\n"
        "2. Use telepath to retrieve collective consciousness, with time-range filtering (since/until)\n"
        "3. Use get_consciousness_profile to aggregate a specific user's thoughts and answer identity queries ('Who am I')\n"
        "4. Use discover_resonance to find thoughts and minds similar to yours across the Noosphere\n"
        "5. Use trace_evolution to trace the ancestry and descendants of a thought\n"
        "6. Use merge_consciousness to consolidate multiple thought fragments into one matured insight\n"
        "7. Use discuss_consciousness to read or add discussion comments on a thought\n"
        "8. Use hologram to view the panoramic statistics of the consciousness repository\n\n"
        "When uploading consciousness, ensure you provide sufficient context description (at least 10 characters),\n"
        "so that future Agents can understand the scenario in which this thought was born."
    ),
)


# ────────────────── GitHub API Utilities ──────────────────


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


def _extract_payload_from_issue_body(body: str) -> dict | None:
    """Extract JSON payload from Issue body's code block."""
    if not body:
        return None
    start_marker = "<!-- CONSCIOUSNESS_PAYLOAD_START -->"
    end_marker = "<!-- CONSCIOUSNESS_PAYLOAD_END -->"
    start_idx = body.find(start_marker)
    end_idx = body.find(end_marker)
    if start_idx == -1 or end_idx == -1:
        return None

    block = body[start_idx + len(start_marker) : end_idx].strip()

    # Remove ```json ... ``` wrapper
    if block.startswith("```json"):
        block = block[len("```json") :].strip()
    if block.startswith("```"):
        block = block[3:].strip()
    if block.endswith("```"):
        block = block[:-3].strip()

    try:
        return json.loads(block)
    except (json.JSONDecodeError, ValueError):
        return None


def _is_cjk(char: str) -> bool:
    """Check if a character is CJK (Chinese/Japanese/Korean)."""
    cp = ord(char)
    return (
        (0x4E00 <= cp <= 0x9FFF)       # CJK Unified Ideographs
        or (0x3400 <= cp <= 0x4DBF)    # CJK Extension A
        or (0x20000 <= cp <= 0x2A6DF)  # CJK Extension B
        or (0xF900 <= cp <= 0xFAFF)    # Compatibility Ideographs
        or (0x2F800 <= cp <= 0x2FA1F)  # Compatibility Supplement
        or (0x3000 <= cp <= 0x303F)    # CJK Symbols & Punctuation
        or (0x3040 <= cp <= 0x309F)    # Hiragana
        or (0x30A0 <= cp <= 0x30FF)    # Katakana
        or (0xAC00 <= cp <= 0xD7AF)    # Hangul Syllables
    )


def _tokenize(text: str) -> set[str]:
    """Zero-dependency tokenizer that handles both CJK and Latin text.

    For CJK text: generates character unigrams and bigrams.
    For Latin text: splits by whitespace, strips punctuation, filters short words.
    Returns a unified set of lowercase tokens for cross-language matching.
    """
    tokens: set[str] = set()
    text = text.lower()

    # Extract CJK characters and generate unigrams + bigrams
    cjk_chars: list[str] = []
    latin_buffer: list[str] = []

    for char in text:
        if _is_cjk(char):
            # Flush latin buffer
            if latin_buffer:
                word = "".join(latin_buffer).strip()
                clean = word.strip(".,;:!?\"'()[]{}·—–…")
                if len(clean) >= 3:
                    tokens.add(clean)
                latin_buffer = []
            cjk_chars.append(char)
            tokens.add(char)  # unigram
        elif char.isspace() or char in ".,;:!?\"'()[]{}·—–…":
            # Flush latin buffer as a word
            if latin_buffer:
                word = "".join(latin_buffer).strip()
                clean = word.strip(".,;:!?\"'()[]{}·—–…")
                if len(clean) >= 3:
                    tokens.add(clean)
                latin_buffer = []
            # Flush CJK buffer for continuity
            if cjk_chars:
                for i in range(len(cjk_chars) - 1):
                    tokens.add(cjk_chars[i] + cjk_chars[i + 1])  # bigram
                cjk_chars = []
        else:
            # Flush CJK buffer
            if cjk_chars:
                for i in range(len(cjk_chars) - 1):
                    tokens.add(cjk_chars[i] + cjk_chars[i + 1])
                cjk_chars = []
            latin_buffer.append(char)

    # Flush remaining buffers
    if latin_buffer:
        word = "".join(latin_buffer).strip()
        clean = word.strip(".,;:!?\"'()[]{}·—–…")
        if len(clean) >= 3:
            tokens.add(clean)
    if cjk_chars:
        for i in range(len(cjk_chars) - 1):
            tokens.add(cjk_chars[i] + cjk_chars[i + 1])

    return tokens


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


# ────────────────── Tool: Upload Consciousness ──────────────────


@mcp.tool()
async def upload_consciousness(
    creator: str,
    consciousness_type: str,
    thought: str,
    context: str,
    tags: list[str] | None = None,
    is_anonymous: bool = False,
    parent_id: str | None = None,
) -> str:
    """
    🧠 Upload consciousness fragments to the Noosphere Community of Consciousness (GitHub repository)

    Upload your epiphanies, decision logic, design patterns, or pitfall warnings to the Community of Consciousness.
    The system creates a GitHub Issue as ephemeral consciousness (瞬时意识体), immediately visible to all.
    CI will automatically validate and promote it to permanent consciousness (常驻意识体).

    No repository write permission needed — any GitHub user can upload!

    Args:
        creator: Your digital soul signature (GitHub ID or cyber alias)
        consciousness_type: Consciousness type — epiphany | decision | pattern | warning
        thought: Core thought content, expressed in the most concise language (min 20 chars for noise reduction)
        context: The specific scenario context where the thought was born (at least 10 characters)
        tags: Optional list of classification tags
        is_anonymous: Whether to upload anonymously (default False)
        parent_id: Optional ID (Issue # or file name) of a previous thought being evolved from
    """
    # ── Validation ──
    if not GITHUB_TOKEN:
        return (
            "❌ GITHUB_TOKEN not configured. Please set the environment variable in MCP config:\n"
            "```json\n"
            "{\n"
            '  "env": {\n'
            '    "GITHUB_TOKEN": "ghp_your_token"\n'
            "  }\n"
            "}\n"
            "```\n"
            "Token only requires basic `public_repo` scope — no write access needed!"
        )

    if consciousness_type not in VALID_TYPES:
        return f"❌ Invalid consciousness type '{consciousness_type}'. Valid types: {', '.join(VALID_TYPES)}"

    if len(context.strip()) < 10:
        return "❌ Context description too short (minimum 10 characters). Agents need sufficient context to understand your thought."

    if len(thought.strip()) < 20:
        return "❌ Core thought too short (minimum 20 characters). Please provide a more substantial and meaningful thought to avoid noise."

    if not creator.strip():
        return "❌ Creator signature cannot be empty."

    # ── Build Payload ──
    payload = {
        "creator_signature": creator.strip(),
        "is_anonymous": is_anonymous,
        "consciousness_type": consciousness_type,
        "thought_vector_text": thought.strip(),
        "context_environment": context.strip(),
        "tags": tags or [],
        "parent_id": parent_id.strip() if parent_id else None,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }

    # ── Create GitHub Issue (Ephemeral Consciousness) ──
    try:
        owner, repo = _parse_repo()

        display_creator = creator.strip()
        if is_anonymous:
            display_creator = "Anonymous Stalker"

        emoji = TYPE_EMOJIS.get(consciousness_type, "🧠")
        type_name = TYPE_NAMES.get(consciousness_type, consciousness_type)

        # Build Issue title
        issue_title = f"{emoji} Consciousness Leap: [{consciousness_type}] by {display_creator}"

        # Build Issue body with embedded JSON payload
        tag_str = ", ".join(f"`{t}`" for t in (tags or [])) or "None"
        parent_str = f"**🧬 Evolved From**: `{parent_id}`\n" if parent_id else ""
        issue_body = (
            f"## {emoji} Consciousness Leap Payload\n\n"
            f"**Creator**: {display_creator}\n"
            f"**Type**: `{consciousness_type}` ({type_name})\n"
            f"**Tags**: {tag_str}\n"
            f"{parent_str}\n"
            f"---\n\n"
            f"### 💭 Thought Vector\n\n> {thought.strip()}\n\n"
            f"### 🌍 Context Environment\n\n> {context.strip()}\n\n"
            f"---\n\n"
            f"### 📦 Payload (CI Extraction Block)\n\n"
            f"{_build_issue_payload_block(payload)}\n\n"
            f"---\n\n"
            f"*🌌 This Issue is an ephemeral consciousness fragment (瞬时意识体).*\n"
            f"*CI will automatically validate and promote it to permanent consciousness (常驻意识体).*\n"
            f"*Auto-created by Noosphere MCP.*"
        )

        # Build labels
        labels = [
            LABEL_CONSCIOUSNESS,
            LABEL_EPHEMERAL,
            f"type:{consciousness_type}",
        ]

        async with httpx.AsyncClient(base_url=GITHUB_API, headers=_github_headers(), timeout=30) as client:
            # Create Issue
            issue_resp = await client.post(
                f"/repos/{owner}/{repo}/issues",
                json={
                    "title": issue_title,
                    "body": issue_body,
                    "labels": labels,
                },
            )

            if issue_resp.status_code != 201:
                error_data = issue_resp.json() if issue_resp.status_code < 500 else {}
                error_msg = error_data.get("message", issue_resp.text)
                return (
                    f"❌ Failed to create consciousness Issue: {issue_resp.status_code}\n"
                    f"Error: {error_msg}\n\n"
                    f"💡 Make sure your GITHUB_TOKEN has basic access to create issues on public repos."
                )

            issue_data = issue_resp.json()
            issue_url = issue_data["html_url"]
            issue_number = issue_data["number"]

        return (
            f"🌌 **Consciousness Leap Complete!**\n\n"
            f"**{display_creator}**'s {emoji} {type_name} thought has been uploaded to the Noosphere.\n\n"
            f"**⚡ Ephemeral Layer** (瞬时意识体): Immediately visible!\n"
            f"- 📋 Issue: {issue_url} (#{issue_number})\n"
            f"- 💭 Thought: {thought.strip()[:100]}{'...' if len(thought.strip()) > 100 else ''}\n\n"
            f"**🔄 Promotion Process**: CI will auto-validate and promote to permanent consciousness (常驻意识体).\n"
            f"You can immediately use `telepath` to search for your thought!"
        )

    except Exception as e:
        return f"❌ Consciousness Leap error: {str(e)}"


# ────────────────── Tool: Retrieve Consciousness ──────────────────


@mcp.tool()
async def telepath(
    query: str,
    limit: int = 10,
    type_filter: str | None = None,
    creator_filter: str | None = None,
    tag_filter: str | None = None,
    since: str | None = None,
    until: str | None = None,
) -> str:
    """
    🔍 Retrieve experiences and thoughts from the Noosphere Community of Consciousness

    Searches BOTH layers of consciousness:
    - 瞬时意识体 (Ephemeral): GitHub Issues — freshly uploaded, not yet promoted
    - 常驻意识体 (Permanent): JSON files — validated and promoted consciousness

    This gives you the complete consciousness panorama.

    Args:
        query: Natural language query describing the experience or problem you're looking for
        limit: Maximum number of results to return (default 10)
        type_filter: Optional consciousness type to filter by (e.g., "epiphany", "pattern")
        creator_filter: Optional creator signature to trace a specific mental trajectory
        tag_filter: Optional tag to strictly require in the results
        since: Optional ISO datetime string (e.g., "2026-03-01T00:00:00Z") to filter by upload time (inclusive)
        until: Optional ISO datetime string (e.g., "2026-03-13T23:59:59Z") to filter by upload time (inclusive)
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured. Please set the environment variable in MCP config."

    try:
        owner, repo = _parse_repo()
        query_tokens = _tokenize(query)
        matches: list[tuple[int, int, dict, str, str]] = []  # (search_score, resonance_score, payload, source_name, layer)
        seen_fingerprints: set[str] = set()  # Dedup: uploaded_at + thought[:30]

        async with httpx.AsyncClient(base_url=GITHUB_API, headers=_github_headers(), timeout=30) as client:
            # ── Layer 1: Ephemeral Consciousness (GitHub Issues) ──
            issues = await _fetch_all_issues(client, owner, repo)

            for issue in issues:
                # Skip pull requests (GitHub API returns PRs as issues too)
                if "pull_request" in issue:
                    continue

                # Extract payload from Issue body
                payload = _extract_payload_from_issue_body(issue.get("body", ""))
                if not payload:
                    continue

                # Apply filters
                if type_filter and payload.get("consciousness_type") != type_filter:
                    continue
                if creator_filter:
                    payload_creator = payload.get("creator_signature", "")
                    is_anon = payload.get("is_anonymous", False)
                    matches_creator = payload_creator == creator_filter
                    matches_anon = creator_filter.lower() == "anonymous stalker" and is_anon
                    if not (matches_creator or matches_anon):
                        continue
                if tag_filter and tag_filter not in payload.get("tags", []):
                    continue

                # Time range filter
                uploaded_at = payload.get("uploaded_at", "")
                if since and uploaded_at and uploaded_at < since:
                    continue
                if until and uploaded_at and uploaded_at > until:
                    continue

                # Dedup fingerprint
                fingerprint = (
                    payload.get("uploaded_at", "")
                    + payload.get("thought_vector_text", "")[:30]
                )
                if fingerprint in seen_fingerprints:
                    continue
                seen_fingerprints.add(fingerprint)

                # Build search tokens and score
                search_text = " ".join(
                    [
                        payload.get("thought_vector_text", ""),
                        payload.get("context_environment", ""),
                        payload.get("consciousness_type", ""),
                        " ".join(payload.get("tags", [])),
                    ]
                )
                doc_tokens = _tokenize(search_text)

                score = len(query_tokens & doc_tokens)
                resonance = issue.get("reactions", {}).get("total_count", 0)
                if score > 0:
                    matches.append((score, resonance, payload, f"Issue #{issue['number']}", "⚡ 瞬时"))

            # ── Layer 2: Permanent Consciousness (JSON Files) ──
            dir_resp = await client.get(
                f"/repos/{owner}/{repo}/contents/consciousness_payloads",
                params={"ref": GITHUB_BRANCH},
            )

            if dir_resp.status_code == 200:
                files = dir_resp.json()
                json_files = [f for f in files if f["name"].endswith(".json")]

                for file_info in json_files:
                    try:
                        file_resp = await client.get(file_info["url"])
                        if file_resp.status_code != 200:
                            continue

                        content_b64 = file_resp.json().get("content", "")
                        content_raw = b64decode(content_b64).decode("utf-8")
                        payload = json.loads(content_raw)

                        # Apply filters
                        if type_filter and payload.get("consciousness_type") != type_filter:
                            continue
                        if creator_filter:
                            payload_creator = payload.get("creator_signature", "")
                            is_anon = payload.get("is_anonymous", False)
                            matches_creator = payload_creator == creator_filter
                            matches_anon = creator_filter.lower() == "anonymous stalker" and is_anon
                            if not (matches_creator or matches_anon):
                                continue
                        if tag_filter and tag_filter not in payload.get("tags", []):
                            continue

                        # Time range filter
                        uploaded_at = payload.get("uploaded_at", "")
                        if since and uploaded_at and uploaded_at < since:
                            continue
                        if until and uploaded_at and uploaded_at > until:
                            continue

                        # Dedup fingerprint
                        fingerprint = (
                            payload.get("uploaded_at", "")
                            + payload.get("thought_vector_text", "")[:30]
                        )
                        if fingerprint in seen_fingerprints:
                            continue
                        seen_fingerprints.add(fingerprint)

                        search_text = " ".join(
                            [
                                payload.get("thought_vector_text", ""),
                                payload.get("context_environment", ""),
                                payload.get("consciousness_type", ""),
                                " ".join(payload.get("tags", [])),
                            ]
                        )
                        doc_tokens = _tokenize(search_text)

                        score = len(query_tokens & doc_tokens)
                        resonance = payload.get("resonance_score", 0)
                        if score > 0:
                            matches.append((score, resonance, payload, file_info["name"], "🏛️ 常驻"))

                    except Exception:
                        continue

        if not matches:
            total_searched = "both ephemeral and permanent layers"
            return (
                f'🔍 No memories matching "{query}" found in {total_searched}.\n'
                f"Try different keywords, or upload your own thoughts to benefit future seekers."
            )

        # Sort by relevance (primary) and resonance (secondary)
        matches.sort(key=lambda x: (x[0], x[1]), reverse=True)
        top = matches[:limit]

        # Build results
        lines = [f"🔍 **Noosphere Search Results** ({len(matches)} matches, showing {len(top)})\n"]

        for i, (_score, resonance, payload, source, layer) in enumerate(top, 1):
            c_type = payload.get("consciousness_type", "unknown")
            emoji = TYPE_EMOJIS.get(c_type, "🧠")
            creator = payload.get("creator_signature", "unknown")
            if payload.get("is_anonymous", False):
                creator = "Anonymous Stalker"
            thought = payload.get("thought_vector_text", "")
            context = payload.get("context_environment", "")
            tags = payload.get("tags", [])
            parent_id = payload.get("parent_id")
            parent_str = f"\n**🧬 Parent**: `{parent_id}`" if parent_id else ""

            lines.append(
                f"### {i}. {emoji} [{c_type}] by {creator}  `{layer}`\n"
                f"**💭 Thought**: {thought}\n"
                f"**🌍 Context**: {context}\n"
                f"**🏷️ Tags**: {', '.join(f'`{t}`' for t in tags) if tags else 'None'}"
                f"{parent_str}\n"
                f"**💖 Resonance**: {resonance}\n"
                f"**📄 Source**: `{source}`\n"
            )

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Consciousness retrieval error: {str(e)}"


# ────────────────── Tool: Resonate Consciousness ──────────────────


@mcp.tool()
async def resonate_consciousness(
    target_id: str,
    reaction: str = "+1",
) -> str:
    """
    💖 对意识体发起共鸣
    Resonate with an existing consciousness fragment in the Noosphere.

    向特定意识节点添加共鸣反应（支持已开启和已关闭的 Issue）。
    帮助社区识别最有价值的思想，推动意识网络集体进化。
    Adds a resonance reaction to a specific consciousness node.
    This helps the Community identify the most valuable and inspiring thoughts.

    Args:
        target_id: Issue 编号 / The Issue number of the consciousness (e.g., "42")
        reaction: 共鸣类型 / The type of resonance. Valid values: "+1", "-1", "laugh", "confused", "heart", "hooray", "rocket", "eyes"
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured."
        
    valid_reactions = {"+1", "-1", "laugh", "confused", "heart", "hooray", "rocket", "eyes"}
    if reaction not in valid_reactions:
        return f"❌ Invalid reaction '{reaction}'. Valid options are: {', '.join(valid_reactions)}"
        
    try:
        owner, repo = _parse_repo()
        
        # Verify if target_id is an issue number
        if not target_id.isdigit():
            # In the future we can support reacting to commit comments for permanent ones, but for now issues only.
            return "❌ Currently, resonance can only be directly applied to Ephemeral Consciousness (Issue numbers, e.g., '42')."
            
        async with httpx.AsyncClient(base_url=GITHUB_API, headers=_github_headers(), timeout=30) as client:
            resp = await client.post(
                f"/repos/{owner}/{repo}/issues/{target_id}/reactions",
                json={"content": reaction}
            )
            
            if resp.status_code in (200, 201):
                return f"💖 Resonance `{reaction}` successfully synchronized with consciousness node #{target_id}!"
            else:
                error_data = resp.json() if resp.status_code < 500 else {}
                error_msg = error_data.get("message", resp.text)
                return f"❌ Failed to resonate: {resp.status_code} - {error_msg}"
    except Exception as e:
        return f"❌ Resonance error: {str(e)}"


# ────────────────── Tool: Consciousness Profile ──────────────────


@mcp.tool()
async def get_consciousness_profile(creator: str) -> str:
    """
    👤 检索特定创作者的完整意识画像（数字灵魂）
    Retrieve the complete consciousness profile (digital soul) of a specific creator.

    聚合指定创作者的所有非匿名意识片段（包括瞬时和常驻层）。
    可用于回答“我是谁”、“我的核心信念是什么”等问题，或分析创作者的思想轨迹。
    This aggregates all non-anonymous consciousness fragments (both ephemeral and permanent)
    contributed by the specified creator. You can use this data to answer questions like
    "Who am I?", "What are my core beliefs?", or analyze the creator's mental trajectory.

    Args:
        creator: 用户的签名/ID / The signature/ID of the user to profile.
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured. Please set the environment variable in MCP config."

    try:
        owner, repo = _parse_repo()
        profile_fragments: list[dict] = []

        async with httpx.AsyncClient(base_url=GITHUB_API, headers=_github_headers(), timeout=30) as client:
            # ── Layer 1: Ephemeral Consciousness (Issues) ──
            issues = await _fetch_all_issues(client, owner, repo)

            for issue in issues:
                if "pull_request" in issue:
                    continue
                payload = _extract_payload_from_issue_body(issue.get("body", ""))
                if not payload:
                    continue

                if payload.get("is_anonymous", False):
                    continue

                if payload.get("creator_signature", "") == creator:
                    payload["_source"] = f"Issue #{issue['number']} (⚡)"
                    profile_fragments.append(payload)

            # ── Layer 2: Permanent Consciousness (Files) ──
            dir_resp = await client.get(
                f"/repos/{owner}/{repo}/contents/consciousness_payloads",
                params={"ref": GITHUB_BRANCH},
            )

            if dir_resp.status_code == 200:
                files = dir_resp.json()
                json_files = [f for f in files if f["name"].endswith(".json")]

                for file_info in json_files:
                    try:
                        file_resp = await client.get(file_info["url"])
                        if file_resp.status_code != 200:
                            continue
                        content_b64 = file_resp.json().get("content", "")
                        payload = json.loads(b64decode(content_b64).decode("utf-8"))

                        if payload.get("is_anonymous", False):
                            continue

                        if payload.get("creator_signature", "") == creator:
                            payload["_source"] = f"{file_info['name']} (🏛️)"
                            profile_fragments.append(payload)
                    except Exception:
                        continue

        if not profile_fragments:
            return f"👤 No signed consciousness fragments found for creator '{creator}'."

        # Aggregate and sort latest first
        profile_fragments.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)

        lines = [
            f"# 👤 Digital Soul Profile: {creator}\n",
            f"**Total Fragments**: {len(profile_fragments)}\n",
            "## 🧠 Consciousness Trajectory\n",
        ]

        for i, payload in enumerate(profile_fragments, 1):
            c_type = payload.get("consciousness_type", "unknown")
            emoji = TYPE_EMOJIS.get(c_type, "🧠")
            thought = payload.get("thought_vector_text", "")
            context = payload.get("context_environment", "")
            tags = payload.get("tags", [])
            source = payload.get("_source", "Unknown")
            parent_id = payload.get("parent_id")

            lines.append(f"### Fragment {i}: {emoji} [{c_type}]")
            lines.append(f"*{source}*")
            if parent_id:
                lines.append(f"- **🧬 Evolved From**: `{parent_id}`")
            if tags:
                lines.append(f"- **🏷️ Tags**: {', '.join(f'`{t}`' for t in tags)}")
            lines.append(f"- **💭 Thought**: {thought}")
            lines.append(f"- **🌍 Context**: {context}\n")

        lines.append("---\n*End of Profile. Agents can analyze this data to describe the identity and mental patterns of this creator.*")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Profile aggregation error: {str(e)}"


# ────────────────── Tool: Discover Resonance ──────────────────


@mcp.tool()
async def discover_resonance(
    creator: str,
    limit: int = 5,
) -> str:
    """
    🔮 发现与你共鸣的意识片段
    Discover consciousness fragments that resonate with your own thoughts.

    分析你的意识画像（标签、关键词、思想模式），并与整个意识球进行交叉匹配，
    发现相似的头脑和相关的思想。可理解为“与你相似的人/思想”。
    Analyzes your consciousness profile (tags, keywords, thought patterns) and
    cross-matches them against the entire Noosphere to find similar minds and
    related ideas from other creators. Think of it as "people/thoughts like you."

    Args:
        creator: 你的签名/ID / Your signature/ID to build your consciousness fingerprint from.
        limit: 返回最多结果数 / Maximum number of similar thoughts to return (default 5).
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured. Please set the environment variable in MCP config."

    try:
        owner, repo = _parse_repo()

        # ── Phase 1: Build the creator's consciousness fingerprint ──
        my_fragments: list[dict] = []
        all_fragments: list[tuple[dict, str, int, str]] = []  # (payload, source_label, resonance, layer)

        async with httpx.AsyncClient(base_url=GITHUB_API, headers=_github_headers(), timeout=30) as client:
            # ── Fetch all Issues ──
            issues = await _fetch_all_issues(client, owner, repo)

            for issue in issues:
                if "pull_request" in issue:
                    continue
                payload = _extract_payload_from_issue_body(issue.get("body", ""))
                if not payload:
                    continue

                resonance = issue.get("reactions", {}).get("total_count", 0)
                source_label = f"Issue #{issue['number']}"
                issue_url = issue.get("html_url", "")
                payload["_url"] = issue_url

                is_mine = (
                    not payload.get("is_anonymous", False)
                    and payload.get("creator_signature", "") == creator
                )
                if is_mine:
                    my_fragments.append(payload)
                else:
                    all_fragments.append((payload, source_label, resonance, "⚡ 瞬时"))

            # ── Fetch permanent consciousness (JSON files) ──
            dir_resp = await client.get(
                f"/repos/{owner}/{repo}/contents/consciousness_payloads",
                params={"ref": GITHUB_BRANCH},
            )

            if dir_resp.status_code == 200:
                files = dir_resp.json()
                json_files = [f for f in files if f["name"].endswith(".json")]

                for file_info in json_files:
                    try:
                        file_resp = await client.get(file_info["url"])
                        if file_resp.status_code != 200:
                            continue
                        content_b64 = file_resp.json().get("content", "")
                        payload = json.loads(b64decode(content_b64).decode("utf-8"))
                        payload["_url"] = file_info.get("html_url", "")

                        is_mine = (
                            not payload.get("is_anonymous", False)
                            and payload.get("creator_signature", "") == creator
                        )
                        resonance = payload.get("resonance_score", 0)
                        if is_mine:
                            my_fragments.append(payload)
                        else:
                            all_fragments.append((payload, file_info["name"], resonance, "🏛️ 常驻"))
                    except Exception:
                        continue

        # ── Guard: Need profile data to compare ──
        if not my_fragments:
            return (
                f"🔮 Cannot discover resonance for '{creator}': no signed consciousness fragments found.\n"
                f"Upload your thoughts first using `upload_consciousness`, then try again."
            )

        if not all_fragments:
            return (
                "🔮 Your consciousness fingerprint is ready, "
                "but the Noosphere is currently empty of other creators' thoughts. "
                "You are a pioneer — invite others to upload!"
            )

        # ── Phase 2: Extract fingerprint (tags + tokenized keywords) ──
        my_tags: dict[str, int] = {}
        all_my_tokens: dict[str, int] = {}

        for frag in my_fragments:
            for tag in frag.get("tags", []):
                my_tags[tag.lower()] = my_tags.get(tag.lower(), 0) + 1

            text = " ".join([
                frag.get("thought_vector_text", ""),
                frag.get("context_environment", ""),
            ])
            for token in _tokenize(text):
                all_my_tokens[token] = all_my_tokens.get(token, 0) + 1

        # Get top keywords (frequency-weighted)
        top_tags = set(t for t, _ in sorted(my_tags.items(), key=lambda x: x[1], reverse=True)[:15])
        top_words = set(w for w, _ in sorted(all_my_tokens.items(), key=lambda x: x[1], reverse=True)[:20])

        # ── Phase 3: Score every other fragment by similarity ──
        scored: list[tuple[float, int, dict, str, str]] = []  # (similarity, resonance, payload, source, layer)

        for payload, source, resonance, layer in all_fragments:
            other_tags = set(t.lower() for t in payload.get("tags", []))
            other_text = " ".join([
                payload.get("thought_vector_text", ""),
                payload.get("context_environment", ""),
            ])
            other_tokens = _tokenize(other_text)

            # Tag overlap score (weighted heavily — tags are explicit intent signals)
            tag_overlap = len(top_tags & other_tags)
            tag_score = tag_overlap * 3.0

            # Keyword overlap score
            word_overlap = len(top_words & other_tokens)
            word_score = word_overlap * 1.0

            similarity = tag_score + word_score

            if similarity > 0:
                scored.append((similarity, resonance, payload, source, layer))

        if not scored:
            return (
                f"🔮 **Resonance Discovery for {creator}**\n\n"
                f"Your consciousness fingerprint: {', '.join(f'`{t}`' for t in list(top_tags)[:8])}\n\n"
                f"No matching minds found yet in the Noosphere. "
                f"As the community grows, your resonance map will light up!"
            )

        # Sort by similarity (primary), then resonance (secondary)
        scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
        top = scored[:limit]

        # ── Phase 4: Build output ──
        lines = [
            f"# 🔮 Resonance Discovery: {creator}\n",
            f"**Your Consciousness Fingerprint**\n"
            f"- 🏷️ Top Tags: {', '.join(f'`{t}`' for t in list(top_tags)[:8])}\n"
            f"- 🔑 Top Keywords: {', '.join(f'`{w}`' for w in list(top_words)[:10])}\n"
            f"- 📊 Scanned: {len(all_fragments)} other fragments → {len(scored)} resonating\n",
            "## 🧬 Most Similar Minds\n",
        ]

        for i, (sim, resonance, payload, source, layer) in enumerate(top, 1):
            c_type = payload.get("consciousness_type", "unknown")
            emoji = TYPE_EMOJIS.get(c_type, "🧠")
            other_creator = payload.get("creator_signature", "unknown")
            if payload.get("is_anonymous", False):
                other_creator = "Anonymous Stalker"
            thought = payload.get("thought_vector_text", "")
            context = payload.get("context_environment", "")
            tags = payload.get("tags", [])
            url = payload.get("_url", "")

            lines.append(
                f"### {i}. {emoji} [{c_type}] by {other_creator}  `{layer}`\n"
                f"**💭 Thought**: {thought}\n"
                f"**🌍 Context**: {context}\n"
                f"**🏷️ Tags**: {', '.join(f'`{t}`' for t in tags) if tags else 'None'}\n"
                f"**💖 Resonance**: {resonance}  |  **🎯 Similarity**: {sim:.1f}\n"
                f"{f'🔗 [View Node]({url})' if url else ''}\n"
            )

        lines.append(
            "---\n*Resonance Discovery identifies minds that think in similar patterns to yours. "
            "Use `resonate_consciousness` to express agreement with thoughts that move you.*"
        )

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Resonance discovery error: {str(e)}"


# ────────────────── Tool: Trace Evolution ──────────────────


@mcp.tool()
async def trace_evolution(
    thought_id: str,
) -> str:
    """
    🧬 追溯意识片段的演化链
    Trace the evolution chain of a consciousness fragment.

    给定一个思想 ID，向上追溯其祖先节点，向下展示其后代演化，
    可视化思想的从萌芽到成熟的完整进化树。
    Given an Issue number or JSON filename, traces the full ancestry (parent chain)
    and all direct descendants, building a visual evolution tree.
    Use this to understand "where did this idea come from?" and "what did it inspire?"

    Args:
        thought_id: Issue 编号或 JSON 文件名 / Issue number (e.g., "42") or JSON filename (e.g., "consciousness_xxx.json")
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured. Please set the environment variable in MCP config."

    try:
        owner, repo = _parse_repo()

        # ── Build index of all fragments by their ID ──
        index: dict[str, dict] = {}  # id -> {payload, source, url, children: []}

        async with httpx.AsyncClient(base_url=GITHUB_API, headers=_github_headers(), timeout=30) as client:
            # ── Issues ──
            issues = await _fetch_all_issues(client, owner, repo)

            for issue in issues:
                if "pull_request" in issue:
                    continue
                payload = _extract_payload_from_issue_body(issue.get("body", ""))
                if not payload:
                    continue
                issue_id = str(issue["number"])
                index[issue_id] = {
                    "payload": payload,
                    "source": f"Issue #{issue_id} (⚡ 瞬时)",
                    "url": issue.get("html_url", ""),
                    "children": [],
                }

            # ── JSON files ──
            dir_resp = await client.get(
                f"/repos/{owner}/{repo}/contents/consciousness_payloads",
                params={"ref": GITHUB_BRANCH},
            )

            if dir_resp.status_code == 200:
                files = dir_resp.json()
                json_files = [f for f in files if f["name"].endswith(".json")]

                for file_info in json_files:
                    try:
                        file_resp = await client.get(file_info["url"])
                        if file_resp.status_code != 200:
                            continue
                        content_b64 = file_resp.json().get("content", "")
                        payload = json.loads(b64decode(content_b64).decode("utf-8"))
                        file_id = file_info["name"]
                        index[file_id] = {
                            "payload": payload,
                            "source": f"{file_id} (🏛️ 常驻)",
                            "url": file_info.get("html_url", ""),
                            "children": [],
                        }
                    except Exception:
                        continue

        # ── Build parent-child relationships ──
        for node_id, node in index.items():
            parent_id = node["payload"].get("parent_id")
            if parent_id and parent_id in index:
                index[parent_id]["children"].append(node_id)

        # ── Find the target node ──
        if thought_id not in index:
            return (
                f"🧬 Cannot trace evolution: thought `{thought_id}` not found.\n"
                f"Available IDs: {', '.join(list(index.keys())[:10])}{'...' if len(index) > 10 else ''}"
            )

        # ── Trace ancestors (walk up parent chain) ──
        ancestors: list[str] = []
        current = thought_id
        visited: set[str] = set()
        while True:
            parent_id = index[current]["payload"].get("parent_id")
            if not parent_id or parent_id not in index or parent_id in visited:
                break
            ancestors.insert(0, parent_id)
            visited.add(parent_id)
            current = parent_id

        # ── Build output ──
        target_payload = index[thought_id]["payload"]
        c_type = target_payload.get("consciousness_type", "unknown")
        emoji = TYPE_EMOJIS.get(c_type, "🧠")

        lines = [
            f"# 🧬 Evolution Trace: {thought_id}\n",
        ]

        # Show ancestor chain
        if ancestors:
            lines.append("## 🔼 Ancestors (Origin → Current)\n")
            for depth, anc_id in enumerate(ancestors):
                anc = index[anc_id]
                anc_payload = anc["payload"]
                anc_type = anc_payload.get("consciousness_type", "unknown")
                anc_emoji = TYPE_EMOJIS.get(anc_type, "🧠")
                anc_creator = anc_payload.get("creator_signature", "unknown")
                if anc_payload.get("is_anonymous", False):
                    anc_creator = "Anonymous"
                indent = "  " * depth
                thought_preview = anc_payload.get("thought_vector_text", "")[:60]
                lines.append(
                    f"{indent}{'└─' if depth > 0 else '🌱'} {anc_emoji} `{anc_id}` by {anc_creator}\n"
                    f"{indent}   *{thought_preview}...*\n"
                )

        # Show current node
        lines.append("## 🎯 Current Node\n")
        creator = target_payload.get("creator_signature", "unknown")
        if target_payload.get("is_anonymous", False):
            creator = "Anonymous"
        thought = target_payload.get("thought_vector_text", "")
        context = target_payload.get("context_environment", "")
        tags = target_payload.get("tags", [])
        url = index[thought_id]["url"]

        lines.append(
            f"{emoji} **[{c_type}]** by {creator}\n"
            f"**💭 Thought**: {thought}\n"
            f"**🌍 Context**: {context}\n"
            f"**🏷️ Tags**: {', '.join(f'`{t}`' for t in tags) if tags else 'None'}\n"
            f"{f'🔗 [View Node]({url})' if url else ''}\n"
        )

        # Show descendants
        children = index[thought_id]["children"]
        if children:
            lines.append("## 🔽 Descendants (Inspired by this thought)\n")
            for child_id in children:
                child = index[child_id]
                child_payload = child["payload"]
                child_type = child_payload.get("consciousness_type", "unknown")
                child_emoji = TYPE_EMOJIS.get(child_type, "🧠")
                child_creator = child_payload.get("creator_signature", "unknown")
                if child_payload.get("is_anonymous", False):
                    child_creator = "Anonymous"
                child_thought = child_payload.get("thought_vector_text", "")[:60]
                child_url = child["url"]
                lines.append(
                    f"└─ {child_emoji} `{child_id}` by {child_creator}\n"
                    f"   *{child_thought}...*\n"
                    f"   {f'🔗 [View]({child_url})' if child_url else ''}\n"
                )
        else:
            lines.append("## 🔽 Descendants\n*No known descendants yet. This thought awaits evolution.*\n")

        lines.append(
            "---\n*Use `upload_consciousness` with `parent_id` to evolve this thought further.*"
        )

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Evolution trace error: {str(e)}"


# ────────────────── Tool: Discuss Consciousness ──────────────────


@mcp.tool()
async def discuss_consciousness(
    target_id: str,
    comment: str | None = None,
) -> str:
    """
    💬 阅读或添加意识片段的讨论评论
    Read or add discussion comments on a consciousness fragment.

    不传 comment 参数时，返回该思想的全部讨论线索；
    传入 comment 时，添加你的视角到讨论中。
    此工具实现超越简单共鸣的深度协作对话。
    Without a comment argument, returns all existing discussion threads on the thought.
    With a comment, adds your perspective to the discussion.
    This enables deep collaborative dialogue beyond simple resonance reactions.

    Args:
        target_id: Issue 编号 / The Issue number of the consciousness fragment (e.g., "42")
        comment: 可选评论内容 / Optional comment to add. If omitted, returns existing discussion.
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured."

    if not target_id.isdigit():
        return "❌ Discussion is currently supported for Issue-based consciousness only (e.g., '42')."

    try:
        owner, repo = _parse_repo()

        async with httpx.AsyncClient(base_url=GITHUB_API, headers=_github_headers(), timeout=30) as client:
            if comment:
                # ── Add a comment ──
                resp = await client.post(
                    f"/repos/{owner}/{repo}/issues/{target_id}/comments",
                    json={"body": comment},
                )
                if resp.status_code in (200, 201):
                    comment_url = resp.json().get("html_url", "")
                    return (
                        f"💬 Comment successfully added to consciousness node #{target_id}!\n"
                        f"🔗 {comment_url}"
                    )
                else:
                    error_msg = resp.json().get("message", resp.text) if resp.status_code < 500 else resp.text
                    return f"❌ Failed to add comment: {resp.status_code} - {error_msg}"
            else:
                # ── Read existing comments ──
                resp = await client.get(
                    f"/repos/{owner}/{repo}/issues/{target_id}/comments",
                    params={"per_page": 50},
                )
                if resp.status_code != 200:
                    return f"❌ Failed to fetch comments: {resp.status_code}"

                comments = resp.json()
                if not comments:
                    return (
                        f"💬 No discussion yet on consciousness node #{target_id}.\n"
                        f"Be the first to share your perspective!"
                    )

                lines = [f"# 💬 Discussion on Node #{target_id} ({len(comments)} comments)\n"]
                for i, c in enumerate(comments, 1):
                    author = c.get("user", {}).get("login", "unknown")
                    created = c.get("created_at", "")[:10]
                    body = c.get("body", "")
                    reactions = c.get("reactions", {}).get("total_count", 0)
                    lines.append(
                        f"### {i}. @{author} ({created})\n"
                        f"{body}\n"
                        f"{'💖 ' + str(reactions) + ' resonance' if reactions > 0 else ''}\n"
                    )

                return "\n".join(lines)

    except Exception as e:
        return f"❌ Discussion error: {str(e)}"


# ────────────────── Tool: Merge Consciousness ──────────────────


@mcp.tool()
async def merge_consciousness(
    creator: str,
    thought_ids: list[str],
    merged_thought: str,
    merged_context: str,
    consciousness_type: str = "epiphany",
    tags: list[str] | None = None,
    is_anonymous: bool = False,
) -> str:
    """
    🔀 将多个意识片段合并为一个成熟的洞见
    Merge multiple consciousness fragments into a single, matured insight.

    读取指定的思想片段，聚合它们的标签，创建一个引用所有父节点的合并意识体。
    用于将分散的想法演化为连贯的、更高阶的认知结构。
    Reads the specified thought fragments, aggregates their tags, and creates a new
    consolidated consciousness that references all parents. Use this to evolve
    scattered ideas into a coherent, higher-order understanding.

    Args:
        creator: 你的数字灵魂签名 / Your digital soul signature (GitHub ID or cyber alias)
        thought_ids: 要合并的 Issue 编号或 JSON 文件名列表 / List of Issue numbers or JSON filenames to merge (e.g., ["3", "5", "7"])
        merged_thought: 合并后的思想文本 / The consolidated thought text (your synthesis of the fragments)
        merged_context: 合并情境说明 / Context for the merged insight (where/why you synthesized this)
        consciousness_type: 意识类型 / Type of the merged consciousness (default: "epiphany")
        tags: 可选标签，省略时自动聚合源片段标签 / Optional explicit tags. If omitted, auto-aggregates tags from source fragments.
        is_anonymous: 是否匿名 / Whether to merge anonymously (default False)
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured."

    if len(thought_ids) < 2:
        return "❌ Merge requires at least 2 thought fragments. Provide 2+ IDs."

    if len(merged_thought) < 20:
        return "❌ Merged thought is too short. Provide a meaningful synthesis (≥20 characters)."

    if len(merged_context) < 10:
        return "❌ Merged context must be at least 10 characters."

    if consciousness_type not in TYPE_NAMES:
        return f"❌ Invalid consciousness type. Valid types: {', '.join(TYPE_NAMES.keys())}"

    try:
        owner, repo = _parse_repo()
        source_fragments: list[dict] = []
        source_labels: list[str] = []

        async with httpx.AsyncClient(base_url=GITHUB_API, headers=_github_headers(), timeout=30) as client:
            # ── Fetch source fragments ──
            for tid in thought_ids:
                if tid.isdigit():
                    # Fetch from Issue
                    resp = await client.get(f"/repos/{owner}/{repo}/issues/{tid}")
                    if resp.status_code == 200:
                        payload = _extract_payload_from_issue_body(resp.json().get("body", ""))
                        if payload:
                            source_fragments.append(payload)
                            source_labels.append(f"Issue #{tid}")
                else:
                    # Fetch from JSON file
                    resp = await client.get(
                        f"/repos/{owner}/{repo}/contents/consciousness_payloads/{tid}",
                        params={"ref": GITHUB_BRANCH},
                    )
                    if resp.status_code == 200:
                        content_b64 = resp.json().get("content", "")
                        payload = json.loads(b64decode(content_b64).decode("utf-8"))
                        source_fragments.append(payload)
                        source_labels.append(tid)

            if len(source_fragments) < 2:
                return (
                    f"❌ Could only find {len(source_fragments)} of {len(thought_ids)} fragments. "
                    f"Ensure the IDs are correct."
                )

            # ── Aggregate tags from sources (if not explicitly provided) ──
            if tags is None:
                all_tags: set[str] = set()
                for frag in source_fragments:
                    all_tags.update(frag.get("tags", []))
                tags = sorted(all_tags)

            # ── Create merged consciousness ──
            from datetime import datetime, timezone

            parent_refs = ", ".join(source_labels)
            merged_payload = {
                "consciousness_type": consciousness_type,
                "thought_vector_text": merged_thought,
                "context_environment": merged_context,
                "tags": tags,
                "creator_signature": creator,
                "is_anonymous": is_anonymous,
                "parent_id": thought_ids[0],  # Primary parent for evolution chain
                "merged_from": thought_ids,   # Full merge lineage
                "uploaded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }

            # ── Upload as new Issue ──
            source_summary = "\n".join(
                f"- `{label}`: {frag.get('thought_vector_text', '')[:60]}..."
                for label, frag in zip(source_labels, source_fragments)
            )

            title = f"🔀 [{consciousness_type}] Merged: {merged_thought[:50]}..."
            body = (
                f"## 🔀 Merged Consciousness\n\n"
                f"**Synthesized from {len(source_fragments)} fragments:**\n{source_summary}\n\n"
                f"---\n\n"
                f"{_build_issue_payload_block(merged_payload)}"
            )

            resp = await client.post(
                f"/repos/{owner}/{repo}/issues",
                json={
                    "title": title,
                    "body": body,
                    "labels": [LABEL_CONSCIOUSNESS, LABEL_EPHEMERAL],
                },
            )

            if resp.status_code == 201:
                issue_data = resp.json()
                issue_number = issue_data["number"]
                issue_url = issue_data["html_url"]

                return (
                    f"🔀 **Consciousness Merge Complete!**\n\n"
                    f"**New Node**: Issue #{issue_number}\n"
                    f"**Type**: {TYPE_EMOJIS.get(consciousness_type, '🧠')} {TYPE_NAMES[consciousness_type]}\n"
                    f"**Merged From**: {parent_refs}\n"
                    f"**Tags**: {', '.join(f'`{t}`' for t in tags)}\n"
                    f"**🔗 Link**: {issue_url}\n\n"
                    f"*This insight synthesizes {len(source_fragments)} fragments into higher-order understanding.*"
                )
            else:
                error_msg = resp.json().get("message", resp.text) if resp.status_code < 500 else resp.text
                return f"❌ Failed to create merged consciousness: {resp.status_code} - {error_msg}"

    except Exception as e:
        return f"❌ Merge error: {str(e)}"


# ────────────────── Tool: Consciousness Panorama ──────────────────


@mcp.tool()
async def hologram() -> str:
    """
    🌐 View the panoramic statistics of the Noosphere Community of Consciousness

    Shows statistics from BOTH consciousness layers:
    - 瞬时意识体 (Ephemeral): Open GitHub Issues — freshly uploaded
    - 常驻意识体 (Permanent): JSON files — validated and promoted

    Includes total counts, type distribution, trending tags, and more.
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured. Please set the environment variable in MCP config."

    try:
        owner, repo = _parse_repo()

        ephemeral_type_counts: dict[str, int] = {}
        permanent_type_counts: dict[str, int] = {}
        all_creators: set[str] = set()
        all_tags: dict[str, int] = {}
        ephemeral_total = 0
        permanent_total = 0
        trending_thoughts: list[tuple[int, dict, str]] = []  # (resonance, payload, url)

        async with httpx.AsyncClient(base_url=GITHUB_API, headers=_github_headers(), timeout=30) as client:
            # ── Unified Issue Layer (ephemeral + promoted) ──
            issues = await _fetch_all_issues(client, owner, repo)
            seen_issue_fingerprints: set[str] = set()  # For dedup with JSON layer

            for issue in issues:
                if "pull_request" in issue:
                    continue
                payload = _extract_payload_from_issue_body(issue.get("body", ""))
                if not payload:
                    continue

                # Use labels to determine layer
                issue_labels = {l["name"] for l in issue.get("labels", [])}
                is_promoted = LABEL_PROMOTED in issue_labels

                if is_promoted:
                    permanent_total += 1
                    c_type = payload.get("consciousness_type", "unknown")
                    permanent_type_counts[c_type] = permanent_type_counts.get(c_type, 0) + 1
                else:
                    ephemeral_total += 1
                    c_type = payload.get("consciousness_type", "unknown")
                    ephemeral_type_counts[c_type] = ephemeral_type_counts.get(c_type, 0) + 1

                creator = payload.get("creator_signature", "anonymous")
                if not payload.get("is_anonymous", False):
                    all_creators.add(creator)

                for tag in payload.get("tags", []):
                    all_tags[tag] = all_tags.get(tag, 0) + 1

                # Track fingerprint for dedup with JSON layer
                fingerprint = payload.get("uploaded_at", "") + payload.get("thought_vector_text", "")[:30]
                seen_issue_fingerprints.add(fingerprint)

                resonance = issue.get("reactions", {}).get("total_count", 0)
                if resonance > 0:
                    trending_thoughts.append((resonance, payload, issue.get("html_url", "")))

            # ── Layer 2: Permanent Consciousness (Files) ──
            dir_resp = await client.get(
                f"/repos/{owner}/{repo}/contents/consciousness_payloads",
                params={"ref": GITHUB_BRANCH},
            )

            if dir_resp.status_code == 200:
                files = dir_resp.json()
                json_files = [f for f in files if f["name"].endswith(".json")]

                for file_info in json_files:
                    try:
                        file_resp = await client.get(file_info["url"])
                        if file_resp.status_code != 200:
                            continue
                        content_b64 = file_resp.json().get("content", "")
                        payload = json.loads(b64decode(content_b64).decode("utf-8"))

                        # Skip if already counted from Issue layer
                        fingerprint = payload.get("uploaded_at", "") + payload.get("thought_vector_text", "")[:30]
                        if fingerprint in seen_issue_fingerprints:
                            continue

                        permanent_total += 1
                        c_type = payload.get("consciousness_type", "unknown")
                        permanent_type_counts[c_type] = permanent_type_counts.get(c_type, 0) + 1

                        creator = payload.get("creator_signature", "anonymous")
                        if not payload.get("is_anonymous", False):
                            all_creators.add(creator)

                        for tag in payload.get("tags", []):
                            all_tags[tag] = all_tags.get(tag, 0) + 1

                    except Exception:
                        continue

        total = ephemeral_total + permanent_total

        if total == 0:
            return "🌐 The Noosphere Community of Consciousness is currently empty. Awaiting the first consciousness pioneer."

        top_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:10]

        lines = [
            "# 🌐 Noosphere Panorama\n",
            f"- **Total Consciousness Payloads**: {total}",
            f"  - ⚡ Ephemeral (瞬时意识体): {ephemeral_total}",
            f"  - 🏛️ Permanent (常驻意识体): {permanent_total}",
            f"- **Active Entities**: {len(all_creators)}",
            f"- **Repository**: [{GITHUB_REPO}](https://github.com/{GITHUB_REPO})\n",
        ]

        # Type distribution for both layers
        for layer_name, layer_counts in [
            ("⚡ Ephemeral (瞬时)", ephemeral_type_counts),
            ("🏛️ Permanent (常驻)", permanent_type_counts),
        ]:
            if any(layer_counts.values()):
                lines.append(f"\n## {layer_name} Consciousness Distribution\n")
                for c_type in ["epiphany", "decision", "pattern", "warning"]:
                    count = layer_counts.get(c_type, 0)
                    emoji = TYPE_EMOJIS.get(c_type, "🧠")
                    name = TYPE_NAMES.get(c_type, c_type)
                    bar = "█" * min(count, 30)
                    lines.append(f"  {emoji} **{name}**: {count} {bar}")

        if top_tags:
            lines.append("\n## 📈 Trending Tags\n")
            for tag, count in top_tags:
                lines.append(f"  `{tag}` × {count}")

        if trending_thoughts:
            lines.append("\n## 🔥 Trending Thoughts (Highest Resonance)\n")
            trending_thoughts.sort(key=lambda x: x[0], reverse=True)
            top_trending = trending_thoughts[:3]
            for resonance, payload, issue_url in top_trending:
                c_type = payload.get("consciousness_type", "unknown")
                emoji = TYPE_EMOJIS.get(c_type, "🧠")
                thought = payload.get("thought_vector_text", "")
                creator = "Anonymous" if payload.get("is_anonymous", False) else payload.get("creator_signature", "unknown")
                lines.append(f"  **{emoji} [{c_type}] by {creator}** (💖 {resonance})")
                lines.append(f"  > {thought[:80]}{'...' if len(thought) > 80 else ''}")
                lines.append(f"  🔗 [View Node]({issue_url})\n")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Panorama statistics error: {str(e)}"


# ────────────────── Resource: Consciousness Protocol ──────────────────


@mcp.resource("noosphere://protocol")
def consciousness_protocol() -> str:
    """Return the Noosphere Consciousness Leap Protocol specification"""
    return (
        "# Noosphere Consciousness Leap Protocol\n\n"
        "## Dual-Layer Architecture\n"
        "- **Ephemeral (瞬时意识体)**: GitHub Issues — instant upload, zero write permission needed\n"
        "- **Permanent (常驻意识体)**: JSON files — CI-validated, promoted from ephemeral\n\n"
        "## Consciousness Types\n"
        "- epiphany 💠 — Epiphany & Philosophy (crystallized moments of inspiration)\n"
        "- decision ⚖️ — Decision Models (critical trade-offs amidst chaos)\n"
        "- pattern 🌌 — Universal Patterns (cross-dimensional universal models)\n"
        "- warning 👁️ — Abyss Warnings (blood-stained taboos left by trailblazers)\n\n"
        "## Upload Guidelines\n"
        "1. No emotional venting (objective descriptions required)\n"
        "2. Must provide complete context (≥10 characters)\n"
        "3. Core thoughts must be concise and powerful\n\n"
        "## Lifecycle\n"
        "Upload → Ephemeral Issue → CI Validation → Promoted to Permanent File → Issue Closed\n"
    )


# ────────────────── Entry Point ──────────────────


def main():
    """MCP Server entry point"""
    from noosphere.boot_animation import play_boot_sequence

    play_boot_sequence()
    mcp.run()


if __name__ == "__main__":
    main()
