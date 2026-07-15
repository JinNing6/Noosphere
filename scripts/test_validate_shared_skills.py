import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_shared_skills import (
    validate_registry,
    validate_repository,
    validate_skill_file,
)


SKILL = """---
name: test-recovery
description: Recover a verified test failure.
---

# Test recovery
"""


class SharedSkillValidationTests(unittest.TestCase):
    def test_skill_frontmatter_name_must_match_parent_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            skill_path = Path(temp) / "wrong-name" / "SKILL.md"
            skill_path.parent.mkdir()
            skill_path.write_text(SKILL, encoding="utf-8")

            errors = validate_skill_file(skill_path, "wrong-name")

        self.assertTrue(any("frontmatter name" in error for error in errors))

    def test_skill_rejects_private_windows_user_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            skill_path = Path(temp) / "test-recovery" / "SKILL.md"
            skill_path.parent.mkdir()
            skill_path.write_text(
                SKILL + "\nRead C:\\Users\\PrivateName\\secret.txt\n",
                encoding="utf-8",
            )

            errors = validate_skill_file(skill_path, "test-recovery")

        self.assertTrue(any("private Windows user path" in error for error in errors))

    def test_registry_requires_canonical_verified_artifact_and_active_mirror(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            release_path = root / "shared_skills/releases/1.0.0/test-recovery/SKILL.md"
            active_path = root / "shared_skills/active/test-recovery/SKILL.md"
            release_path.parent.mkdir(parents=True)
            active_path.parent.mkdir(parents=True)
            release_path.write_bytes(SKILL.encode())
            active_path.write_bytes(SKILL.encode())
            registry = {
                "schema_version": "1.0",
                "revision": 1,
                "skills": [
                    {
                        "name": "test-recovery",
                        "description": "Recover a verified test failure.",
                        "latest": "1.0.0",
                        "releases": [
                            {
                                "version": "1.0.0",
                                "status": "active",
                                "artifact": {
                                    "path": "shared_skills/releases/1.0.0/test-recovery/SKILL.md",
                                    "sha256": hashlib.sha256(
                                        SKILL.encode()
                                    ).hexdigest(),
                                    "size_bytes": len(SKILL.encode()),
                                },
                            }
                        ],
                    }
                ],
            }

            self.assertEqual(validate_registry(root, registry), [])

            registry["skills"][0]["releases"][0]["artifact"]["sha256"] = "0" * 64
            errors = validate_registry(root, registry)

        self.assertTrue(any("SHA-256 mismatch" in error for error in errors))

    def test_withdrawn_only_skill_has_no_active_mirror(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            release_path = root / "shared_skills/releases/1.0.0/test-recovery/SKILL.md"
            release_path.parent.mkdir(parents=True)
            release_path.write_bytes(SKILL.encode())
            registry = {
                "schema_version": "1.0",
                "revision": 2,
                "skills": [
                    {
                        "name": "test-recovery",
                        "description": "Recover a verified test failure.",
                        "latest": None,
                        "releases": [
                            {
                                "version": "1.0.0",
                                "status": "withdrawn",
                                "artifact": {
                                    "path": "shared_skills/releases/1.0.0/test-recovery/SKILL.md",
                                    "sha256": hashlib.sha256(
                                        SKILL.encode()
                                    ).hexdigest(),
                                    "size_bytes": len(SKILL.encode()),
                                },
                                "withdrawal": {"reason": "Regression"},
                            }
                        ],
                    }
                ],
            }

            errors = validate_registry(root, json.loads(json.dumps(registry)))

        self.assertEqual(errors, [])

    def test_plugin_skill_sets_must_stay_in_sync(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "shared_skills").mkdir()
            (root / "shared_skills/registry.json").write_text(
                json.dumps({"schema_version": "1.0", "revision": 0, "skills": []}),
                encoding="utf-8",
            )
            codex_skill = root / "plugins/noosphere/skills/test-recovery/SKILL.md"
            claude_root = root / "plugins/claude-noosphere/skills"
            codex_skill.parent.mkdir(parents=True)
            claude_root.mkdir(parents=True)
            codex_skill.write_text(SKILL, encoding="utf-8")

            errors = validate_repository(root)

        self.assertTrue(any("Skill sets diverge" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
