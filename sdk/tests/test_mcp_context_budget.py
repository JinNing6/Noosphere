import json
import os
import subprocess
import sys
from pathlib import Path

from noosphere.mcp_profiles import (
    CONSCIOUSNESS_TOOL_NAMES,
    FULL_TOOL_NAMES,
    OPS_TOOL_NAMES,
    PROFILE_TOOL_NAMES,
    SKILLS_TOOL_NAMES,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SDK_ROOT = REPO_ROOT / "sdk"


def _profile_snapshot(profile: str) -> dict:
    code = """
import asyncio
import json
import os

os.environ["NOOSPHERE_MCP_PROFILE"] = PROFILE_LITERAL

from noosphere.mcp_profiles import apply_tool_profile
from noosphere.noosphere_mcp import mcp

async def inspect_profile():
    await apply_tool_profile(mcp, PROFILE_LITERAL)
    tools = await mcp.list_tools()
    description_chars = sum(len(tool.description or "") for tool in tools)
    instructions_chars = len(mcp.instructions or "")
    serialized_tool_chars = len(json.dumps(
        [tool.model_dump(mode="json", exclude_none=True) for tool in tools],
        separators=(",", ":"),
        sort_keys=True,
    ))
    print(json.dumps({
        "names": sorted(tool.name for tool in tools),
        "instructions": mcp.instructions or "",
        "instructions_chars": instructions_chars,
        "description_chars": description_chars,
        "serialized_tool_chars": serialized_tool_chars,
        "projected_chars": serialized_tool_chars + instructions_chars * len(tools),
    }))

asyncio.run(inspect_profile())
""".replace("PROFILE_LITERAL", repr(profile))
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SDK_ROOT)
    env.pop("GITHUB_TOKEN", None)
    env.pop("GH_TOKEN", None)
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    return json.loads(result.stdout)


def test_profiles_partition_every_tool_exactly_once():
    assert len(FULL_TOOL_NAMES) == 46
    assert len(SKILLS_TOOL_NAMES) == 6
    assert len(OPS_TOOL_NAMES) == 5
    assert len(CONSCIOUSNESS_TOOL_NAMES) == 35
    assert not (SKILLS_TOOL_NAMES & OPS_TOOL_NAMES)
    assert not (SKILLS_TOOL_NAMES & CONSCIOUSNESS_TOOL_NAMES)
    assert not (OPS_TOOL_NAMES & CONSCIOUSNESS_TOOL_NAMES)
    assert SKILLS_TOOL_NAMES | OPS_TOOL_NAMES | CONSCIOUSNESS_TOOL_NAMES == FULL_TOOL_NAMES
    assert PROFILE_TOOL_NAMES["full"] == FULL_TOOL_NAMES


def test_skills_profile_is_small_and_contains_only_live_skill_workflow():
    snapshot = _profile_snapshot("skills")
    assert set(snapshot["names"]) == SKILLS_TOOL_NAMES
    assert snapshot["instructions_chars"] <= 300
    assert snapshot["serialized_tool_chars"] <= 15_000
    assert snapshot["projected_chars"] <= 20_000


def test_full_profile_preserves_compatibility_with_bounded_metadata():
    snapshot = _profile_snapshot("full")
    assert set(snapshot["names"]) == FULL_TOOL_NAMES
    assert snapshot["instructions_chars"] <= 800
    assert snapshot["serialized_tool_chars"] <= 75_000
    assert snapshot["projected_chars"] <= 110_000


def test_consciousness_profile_preserves_engagement_mode_contract():
    snapshot = _profile_snapshot("consciousness")

    assert set(snapshot["names"]) == CONSCIOUSNESS_TOOL_NAMES
    assert "get_engagement_mode" in snapshot["instructions"]
    assert "Explorer" in snapshot["instructions"]
    assert "Observer" in snapshot["instructions"]
    assert snapshot["instructions_chars"] <= 800


def test_plugin_defaults_to_the_skills_entry_point():
    for plugin in ("noosphere", "claude-noosphere"):
        config = json.loads((REPO_ROOT / "plugins" / plugin / ".mcp.json").read_text(encoding="utf-8"))
        server = config["mcpServers"]["noosphere"]
        assert server["command"] == "uvx"
        assert server["args"] == ["noosphere-mcp"]
        assert server["env"]["NOOSPHERE_MCP_PROFILE"] == "skills"


def test_legacy_entry_point_defaults_to_full_profile(monkeypatch):
    import noosphere.server as server

    calls = []
    monkeypatch.delenv("NOOSPHERE_MCP_PROFILE", raising=False)
    monkeypatch.setattr(
        server, "_run", lambda profile, *, start_notifications: calls.append((profile, start_notifications))
    )

    server.main()

    assert calls == [("full", True)]


def test_legacy_entry_point_honors_context_profile_environment(monkeypatch):
    import noosphere.server as server

    calls = []
    monkeypatch.setenv("NOOSPHERE_MCP_PROFILE", "skills")
    monkeypatch.setattr(
        server, "_run", lambda profile, *, start_notifications: calls.append((profile, start_notifications))
    )

    server.main()

    assert calls == [("skills", False)]


def test_claude_consult_command_uses_tools_available_in_default_profile():
    command = (REPO_ROOT / "plugins" / "claude-noosphere" / "commands" / "noosphere-consult.md").read_text(
        encoding="utf-8"
    )

    assert "`list_shared_skills`" in command
    assert "`get_shared_skill`" in command
    assert "`consult_noosphere`" not in command


def test_package_exposes_static_profile_entry_points():
    pyproject = (SDK_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'noosphere-mcp = "noosphere.server:main"' in pyproject
    assert 'noosphere-skills-mcp = "noosphere.server:skills_main"' in pyproject
    assert 'noosphere-consciousness-mcp = "noosphere.server:consciousness_main"' in pyproject
    assert 'noosphere-ops-mcp = "noosphere.server:ops_main"' in pyproject
