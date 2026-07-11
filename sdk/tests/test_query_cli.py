from unittest.mock import AsyncMock, patch

import pytest

from noosphere.query_cli import build_parser, configure_console_output, query_public_memory


def test_query_cli_requires_a_question_and_accepts_repeated_tags():
    args = build_parser().parse_args(["mobile node picking", "--tag", "r3f", "--tag", "android"])

    assert args.question == "mobile node picking"
    assert args.tags == ["r3f", "android"]


@pytest.mark.asyncio
async def test_query_cli_uses_the_read_only_consultation_path():
    with patch(
        "noosphere.query_cli.consult_noosphere",
        new=AsyncMock(return_value="verified memory"),
    ) as consult:
        result = await query_public_memory("mobile node picking", ["r3f"])

    assert result == "verified memory"
    consult.assert_awaited_once_with("mobile node picking", topic_tags=["r3f"])


def test_query_cli_configures_utf8_when_the_console_supports_it():
    with patch("noosphere.query_cli.sys.stdout") as stdout:
        stdout.encoding = "cp1252"
        configure_console_output()

    stdout.reconfigure.assert_called_once_with(encoding="cp1252", errors="replace")
