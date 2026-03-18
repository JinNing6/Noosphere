"""
🧠 Noosphere MCP Server — Entry Point

This module serves as the NEW entry point for the Noosphere MCP server.
During the transition period, it imports the `mcp` instance from the
original `noosphere_mcp.py` which still contains all 28 tool registrations.

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

import threading


# Import the mcp instance (along with all registered tools)
# from the original monolithic file. This ensures all 28 tools
# are available without having to move them all at once.
from noosphere.noosphere_mcp import (  # noqa: F401
    mcp,
    consciousness_protocol,
    philosophical_reflection,
)


# ── Entry Point ──


def main():
    """MCP Server entry point"""
    import sys as _sys

    from noosphere.boot_animation import play_boot_sequence
    from noosphere.preflight import run_preflight, print_diagnostics

    play_boot_sequence()

    # ── Pre-flight Diagnostics (启动前自检) ──
    preflight_result = run_preflight()
    print_diagnostics(preflight_result)

    if not preflight_result.passed:
        # Fatal errors — cannot start MCP server
        _sys.exit(1)

    # Start the background daemon for OS push notifications
    from noosphere.notifications.daemon import _poll_notifications_daemon
    daemon = threading.Thread(target=_poll_notifications_daemon, daemon=True)
    daemon.start()

    mcp.run()


if __name__ == "__main__":
    main()
