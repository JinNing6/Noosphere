#!/usr/bin/env python
"""Check the portable contract emitted by noosphere-validate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


def check_validation_result(path: Path) -> dict:
    result = json.loads(path.read_text(encoding="utf-8"))
    if result.get("passed") is not True:
        raise RuntimeError("Validation result did not pass")

    duration = float(result.get("duration_seconds", 0))
    if not 0 < duration < 60:
        raise RuntimeError(
            f"Validation duration must be below 60 seconds, got {duration}"
        )

    submission_url = str(result.get("submission_url", ""))
    parsed = urlsplit(submission_url)
    query = parse_qs(parsed.query)
    if parsed.scheme != "https" or parsed.netloc != "github.com":
        raise RuntimeError("Validation submission URL must use GitHub HTTPS")
    if query.get("template") != ["validate-skill.yml"]:
        raise RuntimeError("Validation submission URL targets the wrong Issue Form")
    evidence = query.get("generated_validation_evidence", [""])[0]
    if not all(
        marker in evidence
        for marker in ["CONSCIOUSNESS_PAYLOAD_START", "CONSCIOUSNESS_PAYLOAD_END"]
    ):
        raise RuntimeError("Validation submission URL lacks canonical evidence markers")
    if len(submission_url) >= 8000:
        raise RuntimeError(
            "Validation submission URL exceeds the tested length boundary"
        )

    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", type=Path)
    args = parser.parse_args(argv)
    result = check_validation_result(args.result)
    print(
        f"Validated in {float(result['duration_seconds']):.2f}s with a prefilled evidence link"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
