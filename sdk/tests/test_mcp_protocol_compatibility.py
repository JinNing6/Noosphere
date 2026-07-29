import pytest
from mcp import Client

from noosphere import __version__
from noosphere.mcp_profiles import FULL_TOOL_NAMES
from noosphere.noosphere_mcp import mcp


async def _assert_tool_contract(client: Client) -> None:
    result = await client.list_tools()

    assert client.server_info is not None
    assert client.server_info.name == "noosphere"
    assert client.server_info.version == __version__
    assert {tool.name for tool in result.tools} == FULL_TOOL_NAMES


@pytest.mark.asyncio
async def test_mcp_server_supports_modern_discovery_and_legacy_initialize():
    async with Client(mcp) as modern_client:
        assert modern_client.protocol_version == "2026-07-28"
        await _assert_tool_contract(modern_client)

    async with Client(mcp, mode="legacy") as legacy_client:
        assert legacy_client.protocol_version == "2025-11-25"
        await _assert_tool_contract(legacy_client)
