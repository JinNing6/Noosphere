import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
spec = importlib.util.spec_from_file_location(
    "record_traction_history", SCRIPT_DIR / "record_traction_history.py"
)
recorder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recorder)


def snapshot(generated_at, stars, memories, proof_urls, contributors):
    return {
        "generated_at": generated_at,
        "repo": {
            "stars": stars,
            "forks": 1,
            "open_issues": 8,
        },
        "memory": {
            "public_memories": memories,
            "media_memories": 1,
            "embedding_neighbor_edges": 108,
        },
        "share_proof": {
            "total_proof_issues": proof_urls,
            "reviewable_public_urls": proof_urls,
        },
        "target_progress": {
            "real_contributor_identities": contributors,
            "target_contributor_count": 10,
        },
        "disclaimer": recorder.NON_FABRICATION_DISCLOSURE,
    }


class RecordTractionHistoryTests(unittest.TestCase):
    def test_appends_current_snapshot_and_computes_real_velocity_delta(self):
        existing = {
            "snapshots": [
                snapshot("2026-06-01T00:00:00Z", stars=10, memories=35, proof_urls=0, contributors=1)
            ]
        }
        current = snapshot("2026-06-03T00:00:00Z", stars=15, memories=36, proof_urls=1, contributors=2)

        history = recorder.build_traction_history(existing, current)

        self.assertEqual(len(history["snapshots"]), 2)
        self.assertEqual(history["recording_mode"], "manual append-only")
        self.assertIn("reviewable", history["recording_policy"])
        self.assertEqual(history["latest_velocity"]["baseline_generated_at"], "2026-06-01T00:00:00Z")
        self.assertEqual(history["latest_velocity"]["current_generated_at"], "2026-06-03T00:00:00Z")
        self.assertEqual(history["latest_velocity"]["deltas"]["stars"], 5)
        self.assertEqual(history["latest_velocity"]["deltas"]["public_memories"], 1)
        self.assertEqual(history["latest_velocity"]["deltas"]["reviewable_public_urls"], 1)
        self.assertEqual(history["latest_velocity"]["deltas"]["real_contributor_identities"], 1)
        self.assertAlmostEqual(history["latest_velocity"]["days_elapsed"], 2.0)
        self.assertEqual(history["latest_velocity"]["per_day"]["stars"], 2.5)
        self.assertIn("Velocity", history["share_card"])
        self.assertIn(recorder.NON_FABRICATION_DISCLOSURE, history["disclaimer"])
        self.assertNotRegex(
            json.dumps(history),
            r"\b(downloads|reposts|referrals|retention|rewards|installs)\s*[:=]\s*\d+",
        )

    def test_duplicate_snapshot_is_not_appended_again(self):
        current = snapshot("2026-06-03T00:00:00Z", stars=15, memories=36, proof_urls=0, contributors=2)
        existing = {"snapshots": [current]}

        history = recorder.build_traction_history(existing, current)

        self.assertEqual(len(history["snapshots"]), 1)
        self.assertEqual(history["latest_velocity"]["status"], "baseline-only")
        self.assertEqual(history["latest_velocity"]["deltas"]["stars"], 0)

    def test_write_history_reads_current_snapshot_and_writes_reviewable_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            traction_file = temp_path / "traction_proof.json"
            history_file = temp_path / "traction_history.json"
            traction_file.write_text(
                json.dumps(snapshot("2026-06-03T00:00:00Z", 15, 36, 0, 2)),
                encoding="utf-8",
            )
            history_file.write_text(
                json.dumps({
                    "snapshots": [
                        snapshot("2026-06-02T00:00:00Z", 14, 36, 0, 2)
                    ]
                }),
                encoding="utf-8",
            )

            original_traction_file = recorder.TRACTION_PROOF_FILE
            original_history_file = recorder.HISTORY_FILE
            try:
                recorder.TRACTION_PROOF_FILE = traction_file
                recorder.HISTORY_FILE = history_file
                recorder.write_traction_history()
            finally:
                recorder.TRACTION_PROOF_FILE = original_traction_file
                recorder.HISTORY_FILE = original_history_file

            written = json.loads(history_file.read_text(encoding="utf-8"))
            self.assertEqual(len(written["snapshots"]), 2)
            self.assertEqual(written["latest_velocity"]["deltas"]["stars"], 1)
            self.assertEqual(written["snapshots"][-1]["generated_at"], "2026-06-03T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
