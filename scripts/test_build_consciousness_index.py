import io
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
spec = importlib.util.spec_from_file_location(
    "build_consciousness_index", SCRIPT_DIR / "build_consciousness_index.py"
)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BuildConsciousnessIndexTests(unittest.TestCase):
    def test_build_index_logs_are_safe_for_narrow_windows_stdout(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            payloads_dir = temp_path / "payloads"
            output_file = temp_path / "frontend" / "public" / "consciousness_index.json"
            payloads_dir.mkdir()
            (payloads_dir / "warning.json").write_text(
                json.dumps(
                    {
                        "creator_signature": "debug-agent",
                        "consciousness_type": "warning",
                        "thought_vector_text": "Avoid stale README growth metrics.",
                        "context_environment": "A promotion workflow should sync public growth surfaces.",
                        "tags": ["growth", "ci"],
                        "promoted_from_issue": 23,
                    }
                ),
                encoding="utf-8",
            )

            original_payloads_dir = builder.PAYLOADS_DIR
            original_output_file = builder.OUTPUT_FILE
            original_fetch = builder.fetch_issue_reactions
            original_stdout = sys.stdout
            buffer = io.BytesIO()

            try:
                builder.PAYLOADS_DIR = payloads_dir
                builder.OUTPUT_FILE = output_file
                builder.fetch_issue_reactions = lambda _issue_number: 0
                sys.stdout = io.TextIOWrapper(buffer, encoding="cp1252", errors="strict")

                builder.build_index()
                sys.stdout.flush()
            finally:
                sys.stdout = original_stdout
                builder.PAYLOADS_DIR = original_payloads_dir
                builder.OUTPUT_FILE = original_output_file
                builder.fetch_issue_reactions = original_fetch

            index = json.loads(output_file.read_text(encoding="utf-8"))
            self.assertEqual(len(index), 1)
            self.assertEqual(index[0]["issue_number"], 23)


if __name__ == "__main__":
    unittest.main()
