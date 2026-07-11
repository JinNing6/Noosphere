"""Zero-configuration, read-only Noosphere query command."""

import argparse
import asyncio
import sys

from noosphere.noosphere_mcp import consult_noosphere


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="noosphere-query",
        description="Search Noosphere's public Agent debug memory without a token.",
    )
    parser.add_argument("question", help="The failure, symptom, or engineering question to search")
    parser.add_argument(
        "--tag",
        action="append",
        dest="tags",
        default=None,
        help="Optional topic tag; repeat to supply more than one tag",
    )
    return parser


async def query_public_memory(question: str, tags: list[str] | None = None) -> str:
    return await consult_noosphere(question, topic_tags=tags)


def configure_console_output() -> None:
    """Replace unsupported glyphs instead of crashing legacy Windows consoles."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding=sys.stdout.encoding or "utf-8", errors="replace")


def main() -> int:
    args = build_parser().parse_args()
    result = asyncio.run(query_public_memory(args.question, args.tags))
    configure_console_output()
    print(result)
    return 1 if result.startswith("❌") else 0


if __name__ == "__main__":
    raise SystemExit(main())
