import json
import tempfile
import unittest
from pathlib import Path

from scripts.migrate_consciousness_promotions import (
    apply_migration,
    build_migration_plan,
    main,
)


class PromotionMigrationTests(unittest.TestCase):
    def test_migration_keeps_latest_at_stable_path_and_removes_tombstones(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payloads = root / "consciousness_payloads"
            payloads.mkdir()

            def write(name: str, payload: dict) -> None:
                (payloads / name).write_text(json.dumps(payload), encoding="utf-8")

            write(
                "old_issue0007.json",
                {
                    "promoted_from_issue": 7,
                    "promoted_at": "2026-01-01T00:00:00Z",
                    "thought_vector_text": "old",
                },
            )
            write(
                "new_issue0007.json",
                {
                    "promoted_from_issue": 7,
                    "promoted_at": "2026-02-01T00:00:00Z",
                    "thought_vector_text": "new",
                },
            )
            write(
                "only_issue0008.json",
                {
                    "promoted_from_issue": 8,
                    "promoted_at": "2026-01-15T00:00:00Z",
                    "thought_vector_text": "only",
                },
            )
            write(
                "withdrawn_issue0009.json",
                {
                    "promoted_from_issue": 9,
                    "promoted_at": "2026-01-15T00:00:00Z",
                    "thought_vector_text": "withdrawn",
                },
            )
            write("legacy.json", {"thought_vector_text": "legacy"})
            tombstones = root / "consciousness_tombstones.json"
            tombstones.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "withdrawn_issues": [{"issue_number": 9}],
                    }
                ),
                encoding="utf-8",
            )

            plan = build_migration_plan(payloads, tombstones)
            apply_migration(plan, payloads)

            names = sorted(path.name for path in payloads.glob("*.json"))
            issue7 = json.loads(
                (payloads / "memory_issue0007.json").read_text(encoding="utf-8")
            )

        self.assertEqual(
            names, ["legacy.json", "memory_issue0007.json", "memory_issue0008.json"]
        )
        self.assertEqual(issue7["thought_vector_text"], "new")
        self.assertEqual(plan["duplicate_files_removed"], 1)
        self.assertEqual(plan["tombstoned_files_removed"], 1)

    def test_dry_run_does_not_modify_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payloads = root / "consciousness_payloads"
            payloads.mkdir()
            original = payloads / "legacy_issue0010.json"
            original.write_text(
                json.dumps(
                    {
                        "promoted_from_issue": 10,
                        "promoted_at": "2026-01-01T00:00:00Z",
                    }
                ),
                encoding="utf-8",
            )
            tombstones = root / "consciousness_tombstones.json"
            tombstones.write_text(
                '{"version": 1, "withdrawn_issues": []}', encoding="utf-8"
            )

            plan = build_migration_plan(payloads, tombstones)

            self.assertTrue(original.exists())
            self.assertFalse((payloads / "memory_issue0010.json").exists())
            self.assertEqual(plan["canonical_records"], 1)
            self.assertEqual(
                main(
                    [
                        "--payloads-dir",
                        str(payloads),
                        "--tombstones",
                        str(tombstones),
                        "--check",
                    ]
                ),
                1,
            )
            apply_migration(plan, payloads)
            self.assertEqual(
                main(
                    [
                        "--payloads-dir",
                        str(payloads),
                        "--tombstones",
                        str(tombstones),
                        "--check",
                    ]
                ),
                0,
            )


if __name__ == "__main__":
    unittest.main()
