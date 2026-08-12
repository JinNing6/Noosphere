import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCTOR = REPO_ROOT / "tools" / "codex-sidebar-doctor" / "Invoke-CodexSidebarDoctor.ps1"


class CodexSidebarDoctorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pwsh = shutil.which("pwsh")
        if cls.pwsh is None:
            raise unittest.SkipTest("PowerShell 7 is required for sidebar doctor tests")

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.state_path = self.root / ".codex-global-state.json"

    def tearDown(self):
        self.tempdir.cleanup()

    def write_state(
        self,
        *,
        project_order=None,
        mode="project",
        sort_mode="updated_at",
        unified_order=None,
    ):
        if project_order is None:
            project_order = ["private-project-alpha", "private-project-beta"]
        atoms = {
            "flat-project-sidebar-preferences-v1": {
                "mode": mode,
                "projectSortMode": sort_mode,
            }
        }
        if unified_order is not None:
            atoms["unified-sidebar-project-order-v1"] = unified_order
        state = {
            "project-order": project_order,
            "electron-persisted-atom-state": atoms,
            "electron-saved-workspace-roots": ["C:\\private\\secret-project"],
            "thread-project-assignments": {
                "private-thread-id": "private-project-alpha"
            },
            "unrelated": {"preserve": True},
        }
        self.state_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return state

    def run_doctor(self, *extra_args):
        command = [
            self.pwsh,
            "-NoProfile",
            "-File",
            str(DOCTOR),
            "-StatePath",
            str(self.state_path),
            "-Json",
            *map(str, extra_args),
        ]
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(completed.stdout) if completed.stdout.strip() else None
        return completed, payload

    def test_read_only_diagnosis_matches_published_legacy_state_without_leaking_ids(
        self,
    ):
        original = self.write_state()

        completed, payload = self.run_doctor()

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            payload["diagnosis"]["classification"], "legacy-single-layer-match"
        )
        self.assertEqual(payload["diagnosis"]["top_level_order_count"], 2)
        self.assertFalse(payload["diagnosis"]["second_layer_present"])
        self.assertEqual(payload["action"]["status"], "not-requested")
        self.assertEqual(
            json.loads(self.state_path.read_text(encoding="utf-8")), original
        )
        rendered = json.dumps(payload, ensure_ascii=False)
        self.assertNotIn("private-project-alpha", rendered)
        self.assertNotIn("private-thread-id", rendered)
        self.assertNotIn("secret-project", rendered)

    def test_second_order_layer_is_diagnosed_but_never_offered_the_legacy_repair(self):
        self.write_state(unified_order=["private-project-alpha"])

        completed, payload = self.run_doctor()

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(payload["diagnosis"]["classification"], "second-layer-present")
        self.assertTrue(payload["diagnosis"]["second_layer_present"])
        self.assertFalse(payload["diagnosis"]["repair_supported"])
        self.assertIn("second-order-layer", payload["diagnosis"]["repair_blockers"])

    def test_empty_order_routes_to_task_or_render_cache_investigation(self):
        self.write_state(project_order=[])

        completed, payload = self.run_doctor()

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            payload["diagnosis"]["classification"], "no-persisted-project-order"
        )
        self.assertFalse(payload["diagnosis"]["repair_supported"])
        self.assertEqual(payload["next_step"]["kind"], "collect-redacted-evidence")

    def test_non_recency_sort_is_not_treated_as_a_bug(self):
        self.write_state(sort_mode="priority")

        completed, payload = self.run_doctor()

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            payload["diagnosis"]["classification"], "not-applicable-sort-mode"
        )
        self.assertFalse(payload["diagnosis"]["repair_supported"])
        self.assertEqual(payload["next_step"]["kind"], "no-action")

    def test_explicit_repair_clears_only_the_legacy_order_and_creates_a_backup(self):
        original = self.write_state()

        completed, payload = self.run_doctor("-RepairLegacySingleLayer")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(payload["action"]["status"], "applied")
        self.assertTrue(payload["action"]["backup_created"])
        self.assertEqual(
            payload["action"]["post_repair_classification"],
            "no-persisted-project-order",
        )
        repaired = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(repaired["project-order"], [])
        self.assertEqual(
            repaired["electron-saved-workspace-roots"],
            original["electron-saved-workspace-roots"],
        )
        self.assertEqual(
            repaired["thread-project-assignments"],
            original["thread-project-assignments"],
        )
        backups = list(self.root.glob(".codex-global-state.json.backup-*.json"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(json.loads(backups[0].read_text(encoding="utf-8")), original)

    def test_explicit_repair_refuses_unknown_second_layer_without_writing(self):
        original = self.write_state(unified_order=["private-project-alpha"])

        completed, payload = self.run_doctor("-RepairLegacySingleLayer")

        self.assertEqual(completed.returncode, 3, completed.stderr)
        self.assertEqual(payload["action"]["status"], "refused")
        self.assertEqual(
            json.loads(self.state_path.read_text(encoding="utf-8")), original
        )
        self.assertEqual(
            list(self.root.glob(".codex-global-state.json.backup-*.json")), []
        )

    def test_exported_evidence_is_the_same_redacted_payload(self):
        self.write_state()
        evidence_path = self.root / "evidence.json"

        completed, payload = self.run_doctor(
            "-CodexVersion",
            "26.803.41515 (build 6321)",
            "-ExportEvidencePath",
            evidence_path,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        exported = json.loads(evidence_path.read_text(encoding="utf-8"))
        self.assertEqual(exported, payload)
        self.assertEqual(
            exported["environment"]["codex_version"],
            "26.803.41515 (build 6321)",
        )
        self.assertEqual(
            exported["privacy"],
            {
                "contains_project_names": False,
                "contains_project_paths": False,
                "contains_thread_ids": False,
                "contains_conversation_content": False,
                "contains_ordered_identifiers": False,
            },
        )

    def test_observed_scope_is_explicit_and_never_inferred_from_state(self):
        self.write_state()

        completed, unconfirmed = self.run_doctor()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            unconfirmed["observation"],
            {"stale_ordering_observed": False, "scope": None},
        )

        completed, confirmed = self.run_doctor("-ObservedScope", "tasks-within-project")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            confirmed["observation"],
            {
                "stale_ordering_observed": True,
                "scope": "tasks-within-project",
            },
        )


if __name__ == "__main__":
    unittest.main()
