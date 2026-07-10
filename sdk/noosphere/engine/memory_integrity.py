"""Permanent-memory canonicalization and withdrawal tombstone helpers."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any


def _positive_issue_number(value: Any) -> int | None:
    try:
        issue_number = int(value)
    except (TypeError, ValueError):
        return None
    return issue_number if issue_number > 0 else None


def parse_tombstoned_issue_numbers(manifest: Any) -> set[int]:
    """Return valid source Issue IDs from a tombstone manifest."""
    if not isinstance(manifest, dict):
        return set()

    tombstoned: set[int] = set()
    records = manifest.get("withdrawn_issues", [])
    if not isinstance(records, list):
        return tombstoned

    for record in records:
        if not isinstance(record, dict):
            continue
        issue_number = _positive_issue_number(record.get("issue_number"))
        if issue_number is not None:
            tombstoned.add(issue_number)
    return tombstoned


def _promotion_order(entry: dict) -> tuple[datetime, str]:
    payload = entry.get("payload", {})
    promoted_at = payload.get("promoted_at", "") if isinstance(payload, dict) else ""
    try:
        parsed = datetime.fromisoformat(str(promoted_at).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        parsed = datetime.min.replace(tzinfo=timezone.utc)
    else:
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        else:
            parsed = parsed.astimezone(timezone.utc)
    return parsed, str(entry.get("filename", ""))


def canonicalize_permanent_entries(
    entries: Iterable[dict],
    tombstoned_issue_numbers: set[int],
) -> list[dict]:
    """Deduplicate promotions by source Issue and remove withdrawn records.

    Historical payloads without a source Issue remain addressable. When legacy
    workflows promoted the same Issue multiple times, the newest record wins.
    """
    by_issue: dict[int, dict] = {}
    legacy: list[dict] = []

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        payload = entry.get("payload")
        if not isinstance(payload, dict):
            continue

        issue_number = _positive_issue_number(payload.get("promoted_from_issue"))
        if issue_number is None:
            legacy.append(entry)
            continue
        if issue_number in tombstoned_issue_numbers:
            continue

        current = by_issue.get(issue_number)
        if current is None or _promotion_order(entry) > _promotion_order(current):
            by_issue[issue_number] = entry

    return sorted(legacy, key=lambda entry: str(entry.get("filename", ""))) + [
        by_issue[issue_number] for issue_number in sorted(by_issue)
    ]
