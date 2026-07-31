"""Regression tests for the Experience Protocol v0.1 repository gate."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_experience_records import (
    RECORDS_ROOT,
    REPO_ROOT,
    SCHEMA_PATH,
    TOP_LEVEL_KEYS,
    validate_record,
    validate_repository,
)


class ExperienceRecordValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record_path = next((RECORDS_ROOT / "candidates").glob("*.json"))
        cls.record = json.loads(cls.record_path.read_text(encoding="utf-8"))

    def assert_has_error(self, errors: list[str], fragment: str) -> None:
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected an error containing {fragment!r}, got {errors!r}",
        )

    def test_repository_candidate_is_valid(self) -> None:
        self.assertEqual([], validate_repository())

    def test_schema_declares_current_draft_and_closed_top_level(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            "https://json-schema.org/draft/2020-12/schema", schema["$schema"]
        )
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual("experience", schema["properties"]["record_kind"]["const"])
        self.assertEqual(TOP_LEVEL_KEYS, set(schema["required"]))
        self.assertEqual(
            "approved",
            schema["allOf"][0]["then"]["properties"]["review"]["properties"]["status"][
                "const"
            ],
        )
        self.assertEqual(
            {"approved", "changes-requested"},
            set(
                schema["$defs"]["review"]["allOf"][0]["if"]["properties"]["status"][
                    "enum"
                ]
            ),
        )

    def test_filename_must_match_experience_id(self) -> None:
        errors = validate_record(
            copy.deepcopy(self.record),
            relative_path=Path("candidates/exp-different-case-20260731.json"),
        )
        self.assert_has_error(errors, "must match the record filename")

    def test_attempt_sequence_must_be_ordered_and_consecutive(self) -> None:
        record = copy.deepcopy(self.record)
        record["attempts"][1]["sequence"] = 4
        errors = validate_record(record)
        self.assert_has_error(errors, "sequence values must be consecutive")

    def test_partial_attempt_requires_failure_mechanism(self) -> None:
        record = copy.deepcopy(self.record)
        del record["attempts"][2]["failure_mechanism"]
        errors = validate_record(record)
        self.assert_has_error(errors, "failure_mechanism")

    def test_unknown_evidence_reference_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["verification"]["checks"][0]["evidence_refs"] = ["ev-does-not-exist"]
        errors = validate_record(record)
        self.assert_has_error(errors, "unknown evidence reference")

    def test_independent_reproduction_cannot_use_local_evidence(self) -> None:
        record = copy.deepcopy(self.record)
        record["verification"]["level"] = "independently-reproduced"
        errors = validate_record(record)
        self.assert_has_error(errors, "may reference only public evidence")
        self.assert_has_error(errors, "passing external-run check")

    def test_candidate_cannot_claim_approved_review(self) -> None:
        record = copy.deepcopy(self.record)
        record["review"] = {
            "status": "approved",
            "reviewer": "maintainer",
            "reviewed_at": "2026-07-31T08:00:00Z",
        }
        errors = validate_record(record)
        self.assert_has_error(errors, "a candidate cannot already be approved")

    def test_changes_requested_records_reviewer_and_stays_candidate(self) -> None:
        record = copy.deepcopy(self.record)
        record["lifecycle"]["updated_at"] = "2026-07-31T08:00:00Z"
        record["review"] = {
            "status": "changes-requested",
            "reviewer": "maintainer",
            "reviewed_at": "2026-07-31T08:00:00Z",
            "notes": "Clarify the independent evidence boundary.",
        }
        errors = validate_record(
            record,
            relative_path=Path(f"candidates/{record['experience_id']}.json"),
        )
        self.assertEqual([], errors)

    def test_reviewed_path_accepts_superseded_reviewed_record(self) -> None:
        record = copy.deepcopy(self.record)
        record["lifecycle"]["status"] = "superseded"
        record["lifecycle"]["updated_at"] = "2026-07-31T08:00:00Z"
        record["review"] = {
            "status": "approved",
            "reviewer": "maintainer",
            "reviewed_at": "2026-07-31T08:00:00Z",
        }
        errors = validate_record(
            record,
            relative_path=Path(f"reviewed/{record['experience_id']}.json"),
        )
        self.assertEqual([], errors)

    def test_absolute_user_home_path_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["summary"] += " Source was C:\\Users\\private-name\\.codex\\sessions."
        errors = validate_record(record)
        self.assert_has_error(errors, "contains an absolute user-home path")

    def test_pending_redaction_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["redaction"]["status"] = "pending"
        errors = validate_record(record)
        self.assert_has_error(errors, "cannot have pending redaction")

    def test_redaction_status_matches_removed_categories(self) -> None:
        record = copy.deepcopy(self.record)
        record["redaction"]["removed_categories"] = []
        errors = validate_record(record)
        self.assert_has_error(errors, "when redaction is applied")

        record["redaction"]["status"] = "not-required"
        record["redaction"]["removed_categories"] = ["secrets"]
        errors = validate_record(record)
        self.assert_has_error(errors, "when redaction is not required")

    def test_unavailable_rollback_requires_empty_actions_and_notes(self) -> None:
        record = copy.deepcopy(self.record)
        record["rollback"]["available"] = False
        errors = validate_record(record)
        self.assert_has_error(errors, "must be empty when rollback is unavailable")
        self.assert_has_error(errors, "rollback.notes")

        record["rollback"] = {
            "available": False,
            "conditions": [],
            "steps": [],
            "notes": "The source system has no supported rollback mechanism.",
        }
        self.assertEqual([], validate_record(record))

    def test_sensitive_url_query_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["summary"] += " Receipt: https://example.test/run?access_token=private."
        errors = validate_record(record)
        self.assert_has_error(errors, "sensitive query parameter")

    def test_public_url_evidence_requires_public_https_url(self) -> None:
        record = copy.deepcopy(self.record)
        evidence = record["evidence"][0]
        evidence["kind"] = "public-url"
        errors = validate_record(record)
        self.assert_has_error(errors, "is required for public-url evidence")
        self.assert_has_error(errors, "must be public for public-url evidence")

    def test_public_issue_provenance_requires_public_evidence(self) -> None:
        record = copy.deepcopy(self.record)
        record["provenance"]["source_type"] = "public-issue"
        errors = validate_record(record)
        self.assert_has_error(errors, "may reference only public evidence")

    def test_experience_cannot_relate_to_itself(self) -> None:
        record = copy.deepcopy(self.record)
        record["relations"]["related_experiences"] = [record["experience_id"]]
        errors = validate_record(record)
        self.assert_has_error(errors, "must not contain the current experience_id")

    def test_experience_id_date_matches_observed_date(self) -> None:
        record = copy.deepcopy(self.record)
        record["context"]["observed_at"] = "2026-07-30T07:08:14Z"
        errors = validate_record(record)
        self.assert_has_error(errors, "date suffix must match")

    def test_timestamp_requires_rfc3339_separator_and_timezone(self) -> None:
        record = copy.deepcopy(self.record)
        record["lifecycle"]["created_at"] = "2026-07-31 08:00:00"
        errors = validate_record(record)
        self.assert_has_error(errors, "RFC 3339")

    def test_record_size_is_bounded(self) -> None:
        record = copy.deepcopy(self.record)
        record["summary"] = "x" * 70000
        errors = validate_record(record)
        self.assert_has_error(errors, "record limit")

    def test_ci_release_and_docs_preserve_the_v01_boundary(self) -> None:
        ci = (REPO_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        release = (REPO_ROOT / ".github/workflows/publish-pypi.yml").read_text(
            encoding="utf-8"
        )
        protocol = (REPO_ROOT / "EXPERIENCE_PROTOCOL.md").read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("experience-record-check:", ci)
        self.assertIn("scripts.test_validate_experience_records", ci)
        self.assertIn("python scripts/validate_experience_records.py", ci)
        self.assertIn("scripts.test_validate_experience_records", release)
        self.assertIn("python scripts/validate_experience_records.py", release)
        self.assertIn("adds no MCP tools", protocol)
        self.assertIn("no public upload", protocol)
        self.assertIn("no public upload", readme)
        self.assertIn("default six-tool profile", readme)

    def test_repository_rejects_duplicate_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidates = root / "candidates"
            reviewed = root / "reviewed"
            candidates.mkdir()
            reviewed.mkdir()
            first = copy.deepcopy(self.record)
            second = copy.deepcopy(self.record)
            second["lifecycle"]["status"] = "reviewed"
            second["review"] = {
                "status": "approved",
                "reviewer": "maintainer",
                "reviewed_at": "2026-07-31T08:00:00Z",
            }
            file_name = f"{first['experience_id']}.json"
            (candidates / file_name).write_text(json.dumps(first), encoding="utf-8")
            (reviewed / file_name).write_text(json.dumps(second), encoding="utf-8")
            errors = validate_repository(records_root=root)
        self.assert_has_error(errors, "duplicate experience_id")

    def test_repository_rejects_unknown_immutable_skill_relation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidates = root / "candidates"
            candidates.mkdir()
            record = copy.deepcopy(self.record)
            record["relations"]["related_skills"] = [
                {
                    "name": "not-a-real-release",
                    "version": "1.0.0",
                    "sha256": "a" * 64,
                }
            ]
            path = candidates / f"{record['experience_id']}.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            errors = validate_repository(records_root=root)
        self.assert_has_error(errors, "does not identify an exact immutable release")

    def test_repository_rejects_dangling_experience_relation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidates = root / "candidates"
            candidates.mkdir()
            record = copy.deepcopy(self.record)
            record["relations"]["related_experiences"] = [
                "exp-missing-related-case-20260731"
            ]
            path = candidates / f"{record['experience_id']}.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            errors = validate_repository(records_root=root)
        self.assert_has_error(errors, "unknown Experience Record")


if __name__ == "__main__":
    unittest.main()
