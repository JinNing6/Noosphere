"""
🧠 Noosphere MCP Server — Entry Point

This module serves as the entry point for Noosphere's static MCP profiles.
It imports the registered `mcp` instance from the original monolithic module,
then removes tools that are outside the selected capability profile before
the server begins accepting requests.

Architecture:
  server.py (entry point + main)
    └── imports mcp from noosphere_mcp.py (tools still live there)
         └── noosphere_mcp.py imports infrastructure from engine/*
              ├── models/constants.py
              ├── engine/cache.py
              ├── engine/github_client.py
              ├── engine/text_utils.py
              ├── engine/message_cache.py
              └── engine/social_graph.py

As tools are gradually migrated to tools/*.py modules, noosphere_mcp.py
will shrink and eventually become a pure re-export layer.
"""

import asyncio
import os
import threading

# ── Entry Point ──


def _run(profile: str, *, start_notifications: bool) -> None:
    """Run one static MCP capability profile."""
    import sys as _sys

    from noosphere.boot_animation import play_boot_sequence
    from noosphere.mcp_profiles import apply_tool_profile, normalize_profile
    from noosphere.preflight import print_diagnostics, run_preflight

    normalized_profile = normalize_profile(profile)
    os.environ["NOOSPHERE_MCP_PROFILE"] = normalized_profile

    # Import after selecting the profile so FastMCP receives the matching
    # bounded server instructions without mutating private SDK internals.
    from noosphere.noosphere_mcp import mcp

    play_boot_sequence()

    # ── Pre-flight Diagnostics (启动前自检) ──
    preflight_result = run_preflight()
    print_diagnostics(preflight_result)

    if not preflight_result.passed:
        # Fatal errors — cannot start MCP server
        _sys.exit(1)

    asyncio.run(apply_tool_profile(mcp, normalized_profile))

    if start_notifications:
        from noosphere.notifications.daemon import _poll_notifications_daemon

        daemon = threading.Thread(target=_poll_notifications_daemon, daemon=True)
        daemon.start()

    mcp.run()


def main() -> None:
    """Backward-compatible entry point with an opt-in static profile."""
    profile = os.environ.get("NOOSPHERE_MCP_PROFILE", "full")
    _run(profile, start_notifications=profile.strip().lower() in {"full", "consciousness"})


def skills_main() -> None:
    """Context-efficient Live Skills MCP entry point used by Agent plugins."""
    _run("skills", start_notifications=False)


def consciousness_main() -> None:
    """Opt-in consciousness and social MCP entry point."""
    _run("consciousness", start_notifications=True)


def ops_main() -> None:
    """Opt-in maintainer and launch-operations MCP entry point."""
    _run("ops", start_notifications=False)


if __name__ == "__main__":
    main()
