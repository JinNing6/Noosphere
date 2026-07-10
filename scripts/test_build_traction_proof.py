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
        self.assertEqual(snapshot["history"]["latest_velocity"]["status"], "unavailable")
        self.assertNotIn("deltas", snapshot["history"]["latest_velocity"])

    def test_distribution_blocker_when_pypi_lags_local_package(self):
        distribution = builder.build_distribution_readiness(
            local_version="0.6.8",
            pypi_project={"info": {"version": "0.6.0"}},
            release={
                "tag_name": "v0.6.8",
                "draft": False,
                "prerelease": False,
                "html_url": "https://github.com/JinNing6/Noosphere/releases/tag/v0.6.8",
            },
            access_errors=[],
            tag_trigger_supported=True,
        )
        snapshot = builder.build_traction_proof(
            memories=[
                {
                    "id": "debug-memory-one",
                    "type": "warning",
                    "issue_number": 21,
                    "media_type": None,
                    "resonance_count": 0,
                    "resonates_with": [],
                }
            ],
            share_proofs={
                "summary": {
                    "total_proof_issues": 1,
                    "reviewable_public_urls": 1,
                    "missing_or_invalid_urls": 0,
                },
                "proofs": [
                    {
                        "issue_number": 101,
                        "submitted_by": "agent-user",
                        "share_url": "https://example.com/post",
                        "reviewable": True,
                    },
                ],
            },
            repo={
                "full_name": "JinNing6/Noosphere",
                "html_url": "https://github.com/JinNing6/Noosphere",
                "stargazers_count": 15,
                "forks_count": 1,
                "open_issues_count": 8,
            },
            issues=[],
            pulls=[],
            access_issues=[],
            history={},
            distribution=distribution,
        )

        self.assertEqual(snapshot["distribution"]["status"], "blocked")
        self.assertEqual(snapshot["distribution"]["registry_latest_version"], "0.6.0")
        self.assertEqual(snapshot["distribution"]["local_version"], "0.6.8")
        self.assertEqual(snapshot["bottleneck"]["stage"], "install-loop launch blocker")
        self.assertIn("PyPI latest 0.6.0", snapshot["bottleneck"]["reason"])
        self.assertIn(".github/workflows/publish-pypi.yml", "\n".join(snapshot["distribution"]["closure_checklist"]))
        self.assertEqual(snapshot["distribution"]["publish_trigger"], "tag-or-release")
        self.assertIn("python scripts/verify_pypi_release.py --tool-count 45", snapshot["distribution"]["verifier_command"])
        self.assertIn("Distribution:", snapshot["share_card"])
        self.assertNotRegex(
            json.dumps(snapshot),
            r"\b(downloads|reposts|referrals|retention|rewards|installs)\s*[:=]\s*\d+",
        )

    def test_distribution_ready_when_tag_trigger_available_without_github_release(self):
        distribution = builder.build_distribution_readiness(
            local_version="0.6.8",
            pypi_project={"info": {"version": "0.6.8"}},
            release=None,
            release_error="HTTP Error 404: Not Found",
            access_errors=[],
            tag_trigger_supported=True,
        )

        self.assertEqual(distribution["status"], "ready")
        self.assertEqual(distribution["publish_trigger"], "tag-or-release")
        self.assertEqual(distribution["publish_trigger_status"], "available")
        self.assertEqual(distribution["release_status"], "missing")
        self.assertEqual(distribution["access_issues"], [])
        self.assertIn("Push release tag v0.6.8", "\n".join(distribution["closure_checklist"]))

    def test_detects_publish_workflow_tag_trigger(self):
        workflow = """
        on:
          release:
            types: [published]
          push:
            tags:
              - "v*"
        """

        self.assertTrue(builder.publish_workflow_supports_tag_push(workflow))
        self.assertFalse(builder.publish_workflow_supports_tag_push("on:\n  release:\n    types: [published]\n"))

    def test_inlines_first_public_proof_action_when_share_proof_is_cold(self):
        snapshot = builder.build_traction_proof(
            memories=[
                {
                    "id": "debug-memory-one",
                    "type": "warning",
                    "issue_number": 21,
                    "media_type": None,
                    "resonance_count": 0,
                    "resonates_with": [],
                }
            ],
            share_proofs={
                "summary": {
                    "total_proof_issues": 0,
                    "reviewable_public_urls": 0,
                    "missing_or_invalid_urls": 0,
                },
                "proofs": [],
            },
            repo={
                "full_name": "JinNing6/Noosphere",
                "html_url": "https://github.com/JinNing6/Noosphere",
                "stargazers_count": 15,
                "forks_count": 1,
                "open_issues_count": 8,
            },
            issues=[],
            pulls=[],
            access_issues=[],
            history={},
        )

        action = snapshot["first_proof_action"]
        self.assertEqual(action["stage"], "first public proof")
        self.assertIn("growth-proof.yml", action["growth_issue_form_url"])
        self.assertIn("share-proof.yml", action["share_proof_form_url"])
        self.assertIn("<created-growth-issue-number>", action["created_growth_issue_url_placeholder"])
        self.assertIn("<created-share-proof-issue-number>", action["created_share_proof_issue_url_placeholder"])
        self.assertIn("<public-post-url>", action["public_post_url_placeholder"])
        self.assertGreaterEqual(len(action["commands_after_submission"]), 4)
        self.assertIn("record_growth_referral", action["commands_after_submission"][0])
        self.assertIn("<created-growth-issue-number>", action["commands_after_submission"][0])
        self.assertIn("record_share_attribution", "\n".join(action["commands_after_submission"]))
        self.assertIn("share_attribution_report()", action["commands_after_submission"])
        self.assertIn("growth_flywheel()", action["commands_after_submission"])
        self.assertIn("Noosphere public traction proof", action["copy_ready_public_proof_post"])
        self.assertIn("https://jinning6.github.io/Noosphere/traction_proof.json", action["copy_ready_public_proof_post"])
        self.assertIn("https://jinning6.github.io/Noosphere/traction_history.json", action["copy_ready_public_proof_post"])
        self.assertIn("share-proof.yml", action["copy_ready_public_proof_post"])
        self.assertIn("consciousness-upload.yml", action["copy_ready_public_proof_post"])
        self.assertIn(builder.NON_FABRICATION_DISCLOSURE, action["disclaimer"])
        self.assertIn("open_growth_proof", snapshot["actions"])
        self.assertIn("First proof", snapshot["share_card"])
        self.assertNotRegex(
            json.dumps(action),
            r"\b(downloads|reposts|referrals|retention|rewards|installs)\s*[:=]\s*\d+",
        )

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
            original_fetch_pypi = builder.fetch_pypi_project
            original_fetch_release = builder.fetch_github_release

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
                builder.fetch_pypi_project = lambda: ({"info": {"version": "0.6.8"}}, None)
                builder.fetch_github_release = lambda tag_name: ({
                    "tag_name": tag_name,
                    "draft": False,
                    "prerelease": False,
                    "html_url": f"https://github.com/JinNing6/Noosphere/releases/tag/{tag_name}",
                }, None)

                builder.write_traction_proof()
            finally:
                builder.CONSCIOUSNESS_INDEX_FILE = original_memory_file
                builder.SHARE_PROOF_FILE = original_share_file
                builder.HISTORY_FILE = original_history_file
                builder.OUTPUT_FILE = original_output_file
                builder.fetch_repository = original_fetch_repo
                builder.fetch_repository_issues = original_fetch_issues
                builder.fetch_repository_pulls = original_fetch_pulls
                builder.fetch_pypi_project = original_fetch_pypi
                builder.fetch_github_release = original_fetch_release

            snapshot = json.loads(output_file.read_text(encoding="utf-8"))
            self.assertEqual(snapshot["repo"]["stars"], 2)
            self.assertEqual(snapshot["memory"]["public_memories"], 1)
            self.assertEqual(snapshot["access_issues"], [])
            self.assertEqual(snapshot["distribution"]["status"], "ready")
            self.assertEqual(snapshot["bottleneck"]["stage"], "public share proof")
            self.assertEqual(snapshot["history"]["latest_velocity"]["status"], "baseline-only")
            self.assertIn("traction_proof.json", str(output_file))


if __name__ == "__main__":
    unittest.main()
