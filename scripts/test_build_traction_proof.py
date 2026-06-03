import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
spec = importlib.util.spec_from_file_location(
    "build_traction_proof", SCRIPT_DIR / "build_traction_proof.py"
)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BuildTractionProofTests(unittest.TestCase):
    def test_builds_public_traction_snapshot_from_real_sources_without_fake_metrics(self):
        memories = [
            {
                "id": "soul-debug",
                "type": "warning",
                "issue_number": 21,
                "media_type": None,
                "resonance_count": 2,
                "resonates_with": [{"id": "soul-media", "score": 0.84}],
            },
            {
                "id": "soul-media",
                "type": "image",
                "issue_number": 22,
                "media_type": "image",
                "resonance_count": 1,
                "resonates_with": [{"id": "soul-debug", "score": 0.84}],
            },
        ]
        share_proofs = {
            "summary": {
                "total_proof_issues": 2,
                "reviewable_public_urls": 1,
                "missing_or_invalid_urls": 1,
                "disclaimer": builder.NON_FABRICATION_DISCLOSURE,
            },
            "proofs": [
                {
                    "issue_number": 101,
                    "submitted_by": "agent-user",
                    "share_url": "https://example.com/post",
                    "reviewable": True,
                },
                {
                    "issue_number": 102,
                    "submitted_by": "missing-url-user",
                    "share_url": "",
                    "reviewable": False,
                },
            ],
        }
        repo = {
            "full_name": "JinNing6/Noosphere",
            "html_url": "https://github.com/JinNing6/Noosphere",
            "stargazers_count": 7,
            "forks_count": 3,
            "open_issues_count": 5,
        }
        issues = [
            {
                "number": 101,
                "title": "Share proof: Claude Code",
                "state": "open",
                "html_url": "https://github.com/JinNing6/Noosphere/issues/101",
                "user": {"login": "agent-user"},
                "labels": [{"name": "share-proof"}],
            },
            {
                "number": 21,
                "title": "Consciousness Payload",
                "state": "closed",
                "html_url": "https://github.com/JinNing6/Noosphere/issues/21",
                "user": {"login": "memory-user"},
                "labels": [{"name": "consciousness"}],
            },
        ]
        pulls = [
            {
                "number": 5,
                "html_url": "https://github.com/JinNing6/Noosphere/pull/5",
                "user": {"login": "pr-user"},
            }
        ]

        snapshot = builder.build_traction_proof(
            memories=memories,
            share_proofs=share_proofs,
            repo=repo,
            issues=issues,
            pulls=pulls,
            access_issues=[],
            history={
                "snapshots": [
                    {
                        "generated_at": "2026-06-01T00:00:00Z",
                        "repo": {"stars": 4, "forks": 2, "open_issues": 5},
                        "memory": {"public_memories": 1},
                        "share_proof": {"reviewable_public_urls": 0},
                        "target_progress": {"real_contributor_identities": 2},
                    }
                ]
            },
        )

        self.assertEqual(snapshot["repo"]["stars"], 7)
        self.assertEqual(snapshot["repo"]["forks"], 3)
        self.assertEqual(snapshot["memory"]["public_memories"], 2)
        self.assertEqual(snapshot["memory"]["media_memories"], 1)
        self.assertEqual(snapshot["memory"]["embedding_neighbor_edges"], 2)
        self.assertEqual(snapshot["share_proof"]["reviewable_public_urls"], 1)
        self.assertEqual(snapshot["issueops"]["share_proof_issues"], 1)
        self.assertEqual(snapshot["issueops"]["consciousness_issues"], 1)
        self.assertEqual(snapshot["pull_requests"]["public_prs_sampled"], 1)
        self.assertEqual(snapshot["target_progress"]["real_contributor_identities"], 3)
        self.assertIn("agent-user", snapshot["target_progress"]["contributors"])
        self.assertIn("memory-user", snapshot["target_progress"]["contributors"])
        self.assertIn("pr-user", snapshot["target_progress"]["contributors"])
        self.assertEqual(snapshot["bottleneck"]["stage"], "public share proof")
        self.assertEqual(snapshot["history"]["mode"], "manual append-only")
        self.assertEqual(snapshot["history"]["latest_velocity"]["deltas"]["stars"], 3)
        self.assertEqual(snapshot["history"]["latest_velocity"]["deltas"]["public_memories"], 1)
        self.assertIn("traction_history.json", snapshot["history"]["history_url"])
        self.assertIn("share-proof.yml", snapshot["bottleneck"]["next_action_url"])
        self.assertIn("Noosphere public traction proof", snapshot["share_card"])
        self.assertIn("real contributors", snapshot["share_card"])
        self.assertIn(builder.NON_FABRICATION_DISCLOSURE, snapshot["disclaimer"])
        self.assertNotRegex(
            json.dumps(snapshot),
            r"\b(downloads|reposts|referrals|retention|rewards|installs)\s*[:=]\s*\d+",
        )

    def test_records_recovery_surface_when_public_api_fetch_fails(self):
        snapshot = builder.build_traction_proof(
            memories=[],
            share_proofs={},
            repo=None,
            issues=[],
            pulls=[],
            access_issues=["GitHub repository fetch failed: 403 rate limit"],
            history={},
        )

        self.assertEqual(snapshot["repo"]["status"], "unavailable")
        self.assertEqual(snapshot["memory"]["public_memories"], 0)
        self.assertEqual(snapshot["target_progress"]["real_contributor_identities"], 0)
        self.assertEqual(snapshot["bottleneck"]["stage"], "public API recovery")
        self.assertIn("403 rate limit", snapshot["access_issues"][0])
        self.assertIn("Retry Pages build", snapshot["bottleneck"]["next_action"])

    def test_writes_traction_proof_json_snapshot(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            memories_file = temp_path / "consciousness_index.json"
            share_file = temp_path / "share_proofs.json"
            output_file = temp_path / "traction_proof.json"
            memories_file.write_text(
                json.dumps([
                    {
                        "id": "soul-one",
                        "issue_number": 1,
                        "media_type": None,
                        "resonance_count": 0,
                        "resonates_with": [],
                    }
                ]),
                encoding="utf-8",
            )
            share_file.write_text(
                json.dumps({
                    "summary": {
                        "total_proof_issues": 0,
                        "reviewable_public_urls": 0,
                        "missing_or_invalid_urls": 0,
                    },
                    "proofs": [],
                }),
                encoding="utf-8",
            )

            original_memory_file = builder.CONSCIOUSNESS_INDEX_FILE
            original_share_file = builder.SHARE_PROOF_FILE
            original_history_file = builder.HISTORY_FILE
            original_output_file = builder.OUTPUT_FILE
            original_fetch_repo = builder.fetch_repository
            original_fetch_issues = builder.fetch_repository_issues
            original_fetch_pulls = builder.fetch_repository_pulls

            try:
                builder.CONSCIOUSNESS_INDEX_FILE = memories_file
                builder.SHARE_PROOF_FILE = share_file
                builder.HISTORY_FILE = temp_path / "missing_traction_history.json"
                builder.OUTPUT_FILE = output_file
                builder.fetch_repository = lambda: ({
                    "full_name": "JinNing6/Noosphere",
                    "html_url": "https://github.com/JinNing6/Noosphere",
                    "stargazers_count": 2,
                    "forks_count": 1,
                    "open_issues_count": 0,
                }, None)
                builder.fetch_repository_issues = lambda: ([], None)
                builder.fetch_repository_pulls = lambda: ([], None)

                builder.write_traction_proof()
            finally:
                builder.CONSCIOUSNESS_INDEX_FILE = original_memory_file
                builder.SHARE_PROOF_FILE = original_share_file
                builder.HISTORY_FILE = original_history_file
                builder.OUTPUT_FILE = original_output_file
                builder.fetch_repository = original_fetch_repo
                builder.fetch_repository_issues = original_fetch_issues
                builder.fetch_repository_pulls = original_fetch_pulls

            snapshot = json.loads(output_file.read_text(encoding="utf-8"))
            self.assertEqual(snapshot["repo"]["stars"], 2)
            self.assertEqual(snapshot["memory"]["public_memories"], 1)
            self.assertEqual(snapshot["access_issues"], [])
            self.assertEqual(snapshot["bottleneck"]["stage"], "public share proof")
            self.assertEqual(snapshot["history"]["latest_velocity"]["status"], "baseline-only")
            self.assertIn("traction_proof.json", str(output_file))


if __name__ == "__main__":
    unittest.main()
