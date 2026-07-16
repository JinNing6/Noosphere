import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_shared_skills import (
    validate_outcomes,
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
    def test_outcome_ledger_counts_and_independent_proof_must_match_registry(self):
        digest = "a" * 64
        registry = {
            "schema_version": "1.0",
            "revision": 2,
            "skills": [
                {
                    "name": "test-recovery",
                    "originators": ["originator"],
                    "latest": "1.0.0",
                    "releases": [
                        {
                            "version": "1.0.0",
                            "status": "active",
                            "artifact": {"sha256": digest},
                            "provenance": {"authors": ["originator", "validator"]},
                            "verification": {
                                "level": "outcome-proven",
                                "verified_outcomes": 1,
                                "failed_outcomes": 0,
                                "update_needed": False,
                            },
                        }
                    ],
                }
            ],
        }
        ledger = {
            "schema_version": "1.0",
            "outcomes": [
                {
                    "outcome_id": "outcome-1",
                    "skill_name": "test-recovery",
                    "skill_version": "1.0.0",
                    "skill_sha256": digest,
                    "outcome": "success",
                    "task_summary": "Clean reproduction",
                    "verification_summary": "Regression passed",
                    "evidence_urls": ["https://example.com/evidence"],
                    "reporter": "external-user",
                    "issue_number": 10,
                    "issue_url": "https://github.com/example/noosphere/issues/10",
                    "approved_by": "maintainer",
                    "approved_at": "2026-07-15T00:00:00Z",
                }
            ],
        }

        self.assertEqual(validate_outcomes(registry, ledger), [])
        registry["skills"][0]["releases"][0]["verification"]["verified_outcomes"] = 0
        self.assertTrue(
            any(
                "success count drift" in error
                for error in validate_outcomes(registry, ledger)
            )
        )

    def test_outcome_proven_requires_public_external_evidence(self):
        digest = "a" * 64
        registry = {
            "schema_version": "1.0",
            "revision": 2,
            "skills": [
                {
                    "name": "test-recovery",
                    "originators": ["originator"],
                    "latest": "1.0.0",
                    "releases": [
                        {
                            "version": "1.0.0",
                            "status": "active",
                            "artifact": {"sha256": digest},
                            "provenance": {"authors": ["originator"]},
                            "verification": {
                                "level": "outcome-proven",
                                "verified_outcomes": 1,
                                "failed_outcomes": 0,
                                "update_needed": False,
                            },
                        }
                    ],
                }
            ],
        }
        ledger = {
            "schema_version": "1.0",
            "outcomes": [
                {
                    "outcome_id": "outcome-without-proof",
                    "skill_name": "test-recovery",
                    "skill_version": "1.0.0",
                    "skill_sha256": digest,
                    "outcome": "success",
                    "task_summary": "Clean reproduction",
                    "verification_summary": "Regression passed",
                    "evidence_urls": [],
                    "reporter": "external-user",
                    "issue_number": 10,
                    "issue_url": "https://github.com/example/noosphere/issues/10",
                    "approved_by": "maintainer",
                    "approved_at": "2026-07-15T00:00:00Z",
                }
            ],
        }

        self.assertTrue(
            any(
                "public evidence" in error
                for error in validate_outcomes(registry, ledger)
            )
        )

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
                                "source_count": 2,
                                "publisher_count": 2,
                                "verification": {
                                    "level": "independently-reproduced",
                                    "independent_reproductions": 2,
                                },
                                "provenance": {"kind": "community-evidence"},
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

    def test_registry_digest_is_stable_across_crlf_worktrees(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            release_path = root / "shared_skills/releases/1.0.0/test-recovery/SKILL.md"
            active_path = root / "shared_skills/active/test-recovery/SKILL.md"
            release_path.parent.mkdir(parents=True)
            active_path.parent.mkdir(parents=True)
            canonical = SKILL.encode()
            release_path.write_bytes(canonical.replace(b"\n", b"\r\n"))
            active_path.write_bytes(canonical)
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
                                "publisher_count": 1,
                                "verification": {"level": "maintainer-validated"},
                                "provenance": {"kind": "maintainer-authored"},
                                "artifact": {
                                    "path": "shared_skills/releases/1.0.0/test-recovery/SKILL.md",
                                    "sha256": hashlib.sha256(canonical).hexdigest(),
                                    "size_bytes": len(canonical),
                                },
                            }
                        ],
                    }
                ],
            }

            errors = validate_registry(root, registry)

        self.assertEqual(errors, [])

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
                                "publisher_count": 1,
                                "verification": {"level": "maintainer-validated"},
                                "provenance": {"kind": "maintainer-authored"},
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

    def test_plugins_must_not_bundle_static_skill_copies(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "shared_skills").mkdir()
            (root / "shared_skills/registry.json").write_text(
                json.dumps({"schema_version": "1.0", "revision": 0, "skills": []}),
                encoding="utf-8",
            )
            codex_manifest = root / "plugins/noosphere/.codex-plugin/plugin.json"
            claude_manifest = (
                root / "plugins/claude-noosphere/.claude-plugin/plugin.json"
            )
            marketplace = root / ".claude-plugin/marketplace.json"
            codex_manifest.parent.mkdir(parents=True)
            claude_manifest.parent.mkdir(parents=True)
            marketplace.parent.mkdir(parents=True)
            codex_manifest.write_text(
                json.dumps({"version": "0.4.0", "skills": "./skills/"}),
                encoding="utf-8",
            )
            claude_manifest.write_text(
                json.dumps({"version": "0.4.0"}), encoding="utf-8"
            )
            marketplace.write_text(
                json.dumps({"version": "0.4.0", "plugins": [{"version": "0.4.0"}]}),
                encoding="utf-8",
            )

            errors = validate_repository(root)

        self.assertTrue(
            any("must load live Skills through MCP" in error for error in errors)
        )


if __name__ == "__main__":
    unittest.main()
