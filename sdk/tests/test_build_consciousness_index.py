import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).parents[2] / "scripts" / "build_consciousness_index.py"
SPEC = importlib.util.spec_from_file_location("build_consciousness_index", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_load_canonical_payload_records_applies_tombstones_and_deduplicates(tmp_path):
    payloads_dir = tmp_path / "consciousness_payloads"
    payloads_dir.mkdir()
    tombstones_file = tmp_path / "consciousness_tombstones.json"
    tombstones_file.write_text(
        json.dumps(
            {
                "version": 1,
                "withdrawn_issues": [{"issue_number": 10}],
            }
        ),
        encoding="utf-8",
    )

    records = [
        ("warning_old_issue0010.json", 10, "2026-01-01T00:00:00Z", "withdrawn old"),
        ("warning_new_issue0010.json", 10, "2026-02-01T00:00:00Z", "withdrawn new"),
        ("pattern_old_issue0011.json", 11, "2026-01-01T00:00:00Z", "active old"),
        ("pattern_new_issue0011.json", 11, "2026-02-01T00:00:00Z", "active new"),
    ]
    for filename, issue_number, promoted_at, thought in records:
        (payloads_dir / filename).write_text(
            json.dumps(
                {
                    "promoted_from_issue": issue_number,
                    "promoted_at": promoted_at,
                    "thought_vector_text": thought,
                }
            ),
            encoding="utf-8",
        )

    loaded = MODULE.load_canonical_payload_records(payloads_dir, tombstones_file)

    assert [record["thought_vector_text"] for record in loaded] == ["active new"]


def test_load_canonical_payload_records_rejects_malformed_tombstones(tmp_path):
    payloads_dir = tmp_path / "consciousness_payloads"
    payloads_dir.mkdir()
    (payloads_dir / "memory_issue0011.json").write_text(
        json.dumps(
            {
                "promoted_from_issue": 11,
                "promoted_at": "2026-02-01T00:00:00Z",
                "thought_vector_text": "must not leak past an invalid tombstone boundary",
            }
        ),
        encoding="utf-8",
    )
    tombstones_file = tmp_path / "consciousness_tombstones.json"
    tombstones_file.write_text("{invalid", encoding="utf-8")

    with pytest.raises(ValueError, match="valid tombstone manifest"):
        MODULE.load_canonical_payload_records(payloads_dir, tombstones_file)
