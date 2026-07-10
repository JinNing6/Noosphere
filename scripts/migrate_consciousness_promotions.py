#!/usr/bin/env python
"""Canonicalize historical permanent-memory promotions by source Issue."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "sdk"))

from noosphere.engine.memory_integrity import (  # noqa: E402
    canonicalize_permanent_entries,
    parse_tombstoned_issue_numbers,
)


def _issue_number(payload: dict[str, Any]) -> int | None:
    try:
        value = int(payload.get("promoted_from_issue"))
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def _load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot migrate malformed JSON file {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Cannot migrate non-object JSON file {path}")
    return value


def build_migration_plan(payloads_dir: Path, tombstones_file: Path) -> dict:
    records = []
    groups: dict[int, list[dict]] = defaultdict(list)
    legacy_count = 0
    for path in sorted(payloads_dir.glob("*.json")):
        payload = _load_json(path)
        record = {
            "path": path,
            "filename": path.name,
            "payload": payload,
            "content": path.read_bytes(),
        }
        records.append(record)
        issue = _issue_number(payload)
        if issue is None:
            legacy_count += 1
        else:
            groups[issue].append(record)

    manifest = _load_json(tombstones_file) if tombstones_file.exists() else {}
    tombstoned = parse_tombstoned_issue_numbers(manifest)
    canonical = canonicalize_permanent_entries(records, tombstoned)
    winners = {
        _issue_number(record["payload"]): record
        for record in canonical
        if _issue_number(record["payload"]) is not None
    }

    writes = []
    deletes: set[Path] = set()
    duplicate_files_removed = 0
    tombstoned_files_removed = 0
    canonical_records = 0
    for issue, issue_records in sorted(groups.items()):
        if issue in tombstoned:
            deletes.update(record["path"] for record in issue_records)
            tombstoned_files_removed += len(issue_records)
            continue

        winner = winners[issue]
        target = payloads_dir / f"memory_issue{issue:04d}.json"
        target_record = next(
            (record for record in issue_records if record["path"] == target),
            None,
        )
        if target_record is None or target_record["content"] != winner["content"]:
            writes.append(
                {
                    "source": winner["path"],
                    "target": target,
                    "content": winner["content"],
                }
            )
        deletes.update(
            record["path"] for record in issue_records if record["path"] != target
        )
        duplicate_files_removed += max(0, len(issue_records) - 1)
        canonical_records += 1

    return {
        "writes": writes,
        "deletes": sorted(deletes),
        "canonical_records": canonical_records,
        "duplicate_files_removed": duplicate_files_removed,
        "tombstoned_files_removed": tombstoned_files_removed,
        "legacy_records_untouched": legacy_count,
    }


def _assert_direct_child(path: Path, root: Path) -> None:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    if resolved_path.parent != resolved_root or resolved_path.suffix != ".json":
        raise ValueError(f"Refusing migration path outside payload directory: {path}")


def apply_migration(plan: dict, payloads_dir: Path) -> None:
    """Apply a precomputed plan after checking every target path boundary."""
    for write in plan["writes"]:
        target = Path(write["target"])
        _assert_direct_child(target, payloads_dir)
        temporary = target.with_suffix(".json.migration-tmp")
        temporary.write_bytes(write["content"])
        temporary.replace(target)
    for path in plan["deletes"]:
        path = Path(path)
        _assert_direct_child(path, payloads_dir)
        path.unlink(missing_ok=True)


def _public_plan(plan: dict) -> dict:
    return {
        "canonical_records": plan["canonical_records"],
        "duplicate_files_removed": plan["duplicate_files_removed"],
        "tombstoned_files_removed": plan["tombstoned_files_removed"],
        "legacy_records_untouched": plan["legacy_records_untouched"],
        "writes": [
            {"source": str(item["source"]), "target": str(item["target"])}
            for item in plan["writes"]
        ],
        "deletes": [str(path) for path in plan["deletes"]],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--payloads-dir", type=Path, default=REPO_ROOT / "consciousness_payloads"
    )
    parser.add_argument(
        "--tombstones", type=Path, default=REPO_ROOT / "consciousness_tombstones.json"
    )
    action = parser.add_mutually_exclusive_group()
    action.add_argument(
        "--apply", action="store_true", help="Apply the migration; default is dry-run"
    )
    action.add_argument(
        "--check",
        action="store_true",
        help="Fail when canonicalization changes are pending",
    )
    args = parser.parse_args(argv)

    plan = build_migration_plan(args.payloads_dir.resolve(), args.tombstones.resolve())
    print(json.dumps(_public_plan(plan), ensure_ascii=False, indent=2))
    pending = bool(plan["writes"] or plan["deletes"])
    if args.check:
        if pending:
            print(
                "Promotion canonicalization check failed: migration changes are pending."
            )
            return 1
        print("Promotion canonicalization check passed.")
    elif args.apply:
        apply_migration(plan, args.payloads_dir.resolve())
        print("Promotion migration applied.")
    else:
        print("Dry run only. Re-run with --apply after reviewing the plan.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
