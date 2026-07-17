import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlencode

from scripts.check_validation_result import check_validation_result


def _submission_url() -> str:
    evidence = "\n".join(
        [
            "<!-- CONSCIOUSNESS_PAYLOAD_START -->",
            "```json",
            '{"passed":true}',
            "```",
            "<!-- CONSCIOUSNESS_PAYLOAD_END -->",
        ]
    )
    return "https://github.com/JinNing6/Noosphere/issues/new?" + urlencode(
        {
            "template": "validate-skill.yml",
            "generated_validation_evidence": evidence,
        }
    )


class CheckValidationResultTests(unittest.TestCase):
    def _write(self, payload: dict) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "validation-result.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_accepts_a_fast_pass_with_prefilled_canonical_evidence(self):
        path = self._write(
            {
                "passed": True,
                "duration_seconds": 10.66,
                "submission_url": _submission_url(),
            }
        )

        result = check_validation_result(path)

        self.assertEqual(result["duration_seconds"], 10.66)

    def test_rejects_an_over_budget_result(self):
        path = self._write(
            {
                "passed": True,
                "duration_seconds": 60,
                "submission_url": _submission_url(),
            }
        )

        with self.assertRaisesRegex(RuntimeError, "below 60 seconds"):
            check_validation_result(path)

    def test_rejects_a_link_without_canonical_evidence(self):
        path = self._write(
            {
                "passed": True,
                "duration_seconds": 10,
                "submission_url": (
                    "https://github.com/JinNing6/Noosphere/issues/new?"
                    "template=validate-skill.yml"
                ),
            }
        )

        with self.assertRaisesRegex(RuntimeError, "canonical evidence markers"):
            check_validation_result(path)


if __name__ == "__main__":
    unittest.main()
