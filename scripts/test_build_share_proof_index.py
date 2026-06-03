import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
spec = importlib.util.spec_from_file_location(
    "build_share_proof_index", SCRIPT_DIR / "build_share_proof_index.py"
)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def issue_body(share_url, source_memory="#23", share_context="Shared in a Claude Code channel."):
    return (
        "### Public share URL\n\n"
        f"{share_url}\n\n"
        "### Source Noosphere memory or Issue\n\n"
        f"{source_memory}\n\n"
        "### Share context\n\n"
        f"{share_context}\n"
    )


class BuildShareProofIndexTests(unittest.TestCase):
    def test_extracts_reviewable_public_share_proofs_from_real_issue_fields(self):
        issue = {
            "number": 101,
            "title": "Share proof: Claude Code debug memory",
            "html_url": "https://github.com/JinNing6/Noosphere/issues/101",
            "user": {"login": "agent-user"},
            "created_at": "2026-06-03T08:00:00Z",
            "updated_at": "2026-06-03T08:02:00Z",
            "labels": [{"name": "share-proof"}],
            "body": issue_body(
                "https://example.com/noosphere-post",
                "#23",
                "Shared a reusable Agent debugging lesson.",
            ),
        }

        proof = builder.proof_from_issue(issue)

        self.assertEqual(proof["issue_number"], 101)
        self.assertEqual(proof["share_url"], "https://example.com/noosphere-post")
        self.assertEqual(proof["source_memory"], "#23")
        self.assertEqual(proof["submitted_by"], "agent-user")
        self.assertTrue(proof["reviewable"])
        self.assertEqual(proof["proof_score"], 1)
        self.assertIn("No downloads, reposts, referrals, retention, rewards, or install counts are inferred", proof["disclaimer"])

    def test_rejects_non_public_or_missing_share_urls_without_inventing_metrics(self):
        issues = [
            {
                "number": 102,
                "title": "Share proof: local file",
                "html_url": "https://github.com/JinNing6/Noosphere/issues/102",
                "user": {"login": "local-user"},
                "created_at": "2026-06-03T08:03:00Z",
                "updated_at": "2026-06-03T08:03:00Z",
                "labels": [],
                "body": issue_body("file:///tmp/noosphere.txt"),
            },
            {
                "number": 103,
                "title": "Share proof: missing URL",
                "html_url": "https://github.com/JinNing6/Noosphere/issues/103",
                "user": {"login": "missing-user"},
                "created_at": "2026-06-03T08:04:00Z",
                "updated_at": "2026-06-03T08:04:00Z",
                "labels": [],
                "body": issue_body("not-a-url"),
            },
        ]

        index = builder.build_share_proof_index(issues)

        self.assertEqual(index["summary"]["total_proof_issues"], 2)
        self.assertEqual(index["summary"]["reviewable_public_urls"], 0)
        self.assertEqual(index["summary"]["missing_or_invalid_urls"], 2)
        self.assertEqual(index["summary"]["proof_score_formula"], "1 point per reviewable public http(s) URL")
        self.assertNotRegex(
            json.dumps(index["proofs"]),
            r"\b(downloads|reposts|referrals|retention|rewards|install counts)\s*[:=]\s*\d+",
        )
        self.assertIn("share-proof.yml", index["next_action_url"])

    def test_builds_share_proof_json_snapshot_from_supplied_issue_list(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "share_proofs.json"
            issues = [
                {
                    "number": 101,
                    "title": "Share proof: valid",
                    "html_url": "https://github.com/JinNing6/Noosphere/issues/101",
                    "user": {"login": "agent-user"},
                    "created_at": "2026-06-03T08:00:00Z",
                    "updated_at": "2026-06-03T08:02:00Z",
                    "labels": [{"name": "share-proof"}],
                    "body": issue_body("https://example.com/noosphere-post"),
                },
                {
                    "number": 2,
                    "title": "Unrelated bug",
                    "html_url": "https://github.com/JinNing6/Noosphere/issues/2",
                    "user": {"login": "bug-user"},
                    "created_at": "2026-06-03T08:10:00Z",
                    "updated_at": "2026-06-03T08:10:00Z",
                    "labels": [{"name": "bug"}],
                    "body": "No share proof here.",
                },
            ]

            original_output_file = builder.OUTPUT_FILE
            try:
                builder.OUTPUT_FILE = output_file
                builder.write_share_proof_index(issues)
            finally:
                builder.OUTPUT_FILE = original_output_file

            snapshot = json.loads(output_file.read_text(encoding="utf-8"))
            self.assertEqual(snapshot["summary"]["total_proof_issues"], 1)
            self.assertEqual(snapshot["summary"]["reviewable_public_urls"], 1)
            self.assertEqual(snapshot["proofs"][0]["issue_number"], 101)
            self.assertIn("Noosphere share proof", snapshot["share_card"])


if __name__ == "__main__":
    unittest.main()
