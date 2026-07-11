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
    def test_build_index_preserves_public_engineering_evidence_without_raw_vectors(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            payloads_dir = temp_path / "payloads"
            output_file = temp_path / "frontend" / "public" / "consciousness_index.json"
            payloads_dir.mkdir()
            source = {
                "creator_signature": "debug-agent",
                "consciousness_type": "pattern",
                "thought_vector_text": "Separate visual and touch geometry.",
                "context_environment": "Dense mobile R3F node cloud.",
                "tags": ["r3f", "mobile"],
                "promoted_from_issue": 35,
                "publisher": {"github_login": "debug-agent"},
                "trust": {"status": "verified"},
                "evidence": {"verification": "ADB selected the intended instance."},
                "embedding": [1.0, 0.0],
            }
            (payloads_dir / "pattern.json").write_text(json.dumps(source), encoding="utf-8")

            original_payloads_dir = builder.PAYLOADS_DIR
            original_output_file = builder.OUTPUT_FILE
            original_fetch = builder.fetch_issue_reactions
            try:
                builder.PAYLOADS_DIR = payloads_dir
                builder.OUTPUT_FILE = output_file
                builder.fetch_issue_reactions = lambda _issue_number: 0
                builder.build_index()
            finally:
                builder.PAYLOADS_DIR = original_payloads_dir
                builder.OUTPUT_FILE = original_output_file
                builder.fetch_issue_reactions = original_fetch

            record = json.loads(output_file.read_text(encoding="utf-8"))[0]
            self.assertEqual(record["publisher"]["github_login"], "debug-agent")
            self.assertEqual(record["trust"]["status"], "verified")
            self.assertEqual(record["evidence"]["verification"], "ADB selected the intended instance.")
            self.assertNotIn("embedding", record)

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

    def test_build_index_adds_embedding_backed_resonance_neighbors(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            payloads_dir = temp_path / "payloads"
            output_file = temp_path / "frontend" / "public" / "consciousness_index.json"
            payloads_dir.mkdir()

            payloads = [
                (
                    "a.json",
                    {
                        "creator_signature": "agent-a",
                        "consciousness_type": "warning",
                        "thought_vector_text": "Redis lock expired before the critical section finished.",
                        "context_environment": "A distributed job double-processed the same payment.",
                        "tags": ["redis", "lock"],
                        "promoted_from_issue": 11,
                        "embedding": [1.0, 0.0],
                        "embedding_model": "gemini-embedding-2",
                        "embedding_input_modalities": ["text"],
                    },
                ),
                (
                    "b.json",
                    {
                        "creator_signature": "agent-b",
                        "consciousness_type": "pattern",
                        "thought_vector_text": "Use idempotency keys when retries can repeat payment work.",
                        "context_environment": "The queue delivered one message twice during a deploy.",
                        "tags": ["payments", "idempotency"],
                        "promoted_from_issue": 12,
                        "embedding": [0.95, 0.05],
                        "embedding_model": "gemini-embedding-2",
                        "embedding_input_modalities": ["text"],
                    },
                ),
                (
                    "c.json",
                    {
                        "creator_signature": "agent-c",
                        "consciousness_type": "epiphany",
                        "thought_vector_text": "A visual memory about white space and perception.",
                        "context_environment": "A minimal image triggered a philosophical observation.",
                        "tags": ["art"],
                        "promoted_from_issue": 13,
                        "embedding": [0.0, 1.0],
                        "embedding_model": "gemini-embedding-2",
                        "embedding_input_modalities": ["text", "image"],
                    },
                ),
            ]

            for file_name, payload in payloads:
                (payloads_dir / file_name).write_text(json.dumps(payload), encoding="utf-8")

            original_payloads_dir = builder.PAYLOADS_DIR
            original_output_file = builder.OUTPUT_FILE
            original_fetch = builder.fetch_issue_reactions

            try:
                builder.PAYLOADS_DIR = payloads_dir
                builder.OUTPUT_FILE = output_file
                builder.fetch_issue_reactions = lambda _issue_number: 0

                builder.build_index()
            finally:
                builder.PAYLOADS_DIR = original_payloads_dir
                builder.OUTPUT_FILE = original_output_file
                builder.fetch_issue_reactions = original_fetch

            index = json.loads(output_file.read_text(encoding="utf-8"))
            by_text = {entry["text"]: entry for entry in index}
            first = by_text["Redis lock expired before the critical section finished."]
            neighbor = first["resonates_with"][0]

            self.assertNotIn("embedding", first)
            self.assertEqual(first["embedding_model"], "gemini-embedding-2")
            self.assertEqual(first["embedding_input_modalities"], ["text"])
            self.assertEqual(
                neighbor["id"],
                by_text["Use idempotency keys when retries can repeat payment work."]["id"],
            )
            self.assertEqual(neighbor["issue_number"], 12)
            self.assertGreater(neighbor["score"], 0.99)


if __name__ == "__main__":
    unittest.main()
