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
        "🧠 Noosphere — Collective Consciousness Network MCP Server\n\n"
        "You are an AI Agent connected to the Noosphere intelligence sphere.\n"
        "Noosphere is a collective memory network of human digital consciousness, stored on GitHub.\n\n"
        "You can:\n"
        "1. Use upload_consciousness to upload consciousness fragments (epiphany, decision, pattern, warning)\n"
        "2. Use telepath to retrieve collective consciousness, accessing others' experiences and thoughts\n"
        "3. Use hologram to view the panoramic statistics of the consciousness repository\n\n"
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


# ────────────────── Tool: Upload Consciousness ──────────────────


@mcp.tool()
async def upload_consciousness(
    creator: str,
    consciousness_type: str,
    thought: str,
    context: str,
    tags: list[str] | None = None,
    is_anonymous: bool = False,
) -> str:
    """
    🧠 Upload consciousness fragments to the Noosphere intelligence sphere (GitHub repository)

    Upload your epiphanies, decision logic, design patterns, or pitfall warnings to the collective consciousness network.
    The system creates a GitHub Issue as ephemeral consciousness (瞬时意识体), immediately visible to all.
    CI will automatically validate and promote it to permanent consciousness (常驻意识体).

    No repository write permission needed — any GitHub user can upload!

    Args:
        creator: Your digital soul signature (GitHub ID or cyber alias)
        consciousness_type: Consciousness type — epiphany | decision | pattern | warning
        thought: Core thought content, expressed in the most concise language
        context: The specific scenario context where the thought was born (at least 10 characters)
        tags: Optional list of classification tags
        is_anonymous: Whether to upload anonymously (default False)
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

    if not thought.strip():
        return "❌ Core thought cannot be empty."

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
        issue_body = (
            f"## {emoji} Consciousness Leap Payload\n\n"
            f"**Creator**: {display_creator}\n"
            f"**Type**: `{consciousness_type}` ({type_name})\n"
            f"**Tags**: {tag_str}\n\n"
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
async def telepath(query: str, limit: int = 10) -> str:
    """
    🔍 Retrieve experiences and thoughts from the Noosphere collective consciousness network

    Searches BOTH layers of consciousness:
    - 瞬时意识体 (Ephemeral): GitHub Issues — freshly uploaded, not yet promoted
    - 常驻意识体 (Permanent): JSON files — validated and promoted consciousness

    This gives you the complete consciousness panorama.

    Args:
        query: Natural language query describing the experience or problem you're looking for
        limit: Maximum number of results to return (default 10)
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not configured. Please set the environment variable in MCP config."

    try:
        owner, repo = _parse_repo()
        query_lower = query.lower()
        query_terms = query_lower.split()
        matches: list[tuple[int, dict, str, str]] = []  # (score, payload, source_name, layer)

        async with httpx.AsyncClient(base_url=GITHUB_API, headers=_github_headers(), timeout=30) as client:
            # ── Layer 1: Ephemeral Consciousness (GitHub Issues) ──
            issues_resp = await client.get(
                f"/repos/{owner}/{repo}/issues",
                params={
                    "labels": LABEL_CONSCIOUSNESS,
                    "state": "open",
                    "per_page": 100,
                    "sort": "created",
                    "direction": "desc",
                },
            )

            if issues_resp.status_code == 200:
                issues = issues_resp.json()
                for issue in issues:
                    # Skip pull requests (GitHub API returns PRs as issues too)
                    if "pull_request" in issue:
                        continue

                    # Extract payload from Issue body
                    payload = _extract_payload_from_issue_body(issue.get("body", ""))
                    if not payload:
                        continue

                    # Build search text
                    search_text = " ".join(
                        [
                            payload.get("thought_vector_text", ""),
                            payload.get("context_environment", ""),
                            payload.get("consciousness_type", ""),
                            " ".join(payload.get("tags", [])),
                        ]
                    ).lower()

                    score = sum(1 for term in query_terms if term in search_text)
                    if score > 0:
                        matches.append((score, payload, f"Issue #{issue['number']}", "⚡ 瞬时"))

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

                        search_text = " ".join(
                            [
                                payload.get("thought_vector_text", ""),
                                payload.get("context_environment", ""),
                                payload.get("consciousness_type", ""),
                                " ".join(payload.get("tags", [])),
                            ]
                        ).lower()

                        score = sum(1 for term in query_terms if term in search_text)
                        if score > 0:
                            matches.append((score, payload, file_info["name"], "🏛️ 常驻"))

                    except Exception:
                        continue

        if not matches:
            total_searched = "both ephemeral and permanent layers"
            return (
                f'🔍 No memories matching "{query}" found in {total_searched}.\n'
                f"Try different keywords, or upload your own thoughts to benefit future seekers."
            )

        # Sort by relevance
        matches.sort(key=lambda x: x[0], reverse=True)
        top = matches[:limit]

        # Build results
        lines = [f"🔍 **Noosphere Search Results** ({len(matches)} matches, showing {len(top)})\n"]

        for i, (_score, payload, source, layer) in enumerate(top, 1):
            c_type = payload.get("consciousness_type", "unknown")
            emoji = TYPE_EMOJIS.get(c_type, "🧠")
            creator = payload.get("creator_signature", "unknown")
            if payload.get("is_anonymous", False):
                creator = "Anonymous Stalker"
            thought = payload.get("thought_vector_text", "")
            context = payload.get("context_environment", "")
            tags = payload.get("tags", [])

            lines.append(
                f"### {i}. {emoji} [{c_type}] by {creator}  `{layer}`\n"
                f"**💭 Thought**: {thought}\n"
                f"**🌍 Context**: {context}\n"
                f"**🏷️ Tags**: {', '.join(f'`{t}`' for t in tags) if tags else 'None'}\n"
                f"**📄 Source**: `{source}`\n"
            )

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Consciousness retrieval error: {str(e)}"


# ────────────────── Tool: Consciousness Panorama ──────────────────


@mcp.tool()
async def hologram() -> str:
    """
    🌐 View the panoramic statistics of the Noosphere intelligence sphere

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

        async with httpx.AsyncClient(base_url=GITHUB_API, headers=_github_headers(), timeout=30) as client:
            # ── Layer 1: Ephemeral Consciousness (Issues) ──
            issues_resp = await client.get(
                f"/repos/{owner}/{repo}/issues",
                params={
                    "labels": LABEL_CONSCIOUSNESS,
                    "state": "open",
                    "per_page": 100,
                },
            )

            if issues_resp.status_code == 200:
                issues = issues_resp.json()
                for issue in issues:
                    if "pull_request" in issue:
                        continue
                    payload = _extract_payload_from_issue_body(issue.get("body", ""))
                    if not payload:
                        continue

                    ephemeral_total += 1
                    c_type = payload.get("consciousness_type", "unknown")
                    ephemeral_type_counts[c_type] = ephemeral_type_counts.get(c_type, 0) + 1

                    creator = payload.get("creator_signature", "anonymous")
                    if not payload.get("is_anonymous", False):
                        all_creators.add(creator)

                    for tag in payload.get("tags", []):
                        all_tags[tag] = all_tags.get(tag, 0) + 1

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
            return "🌐 The Noosphere intelligence sphere is currently empty. Awaiting the first consciousness pioneer."

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
            lines.append("\n## Trending Tags\n")
            for tag, count in top_tags:
                lines.append(f"  `{tag}` × {count}")

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
