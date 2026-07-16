"""Low-friction, deterministic Noosphere Skill validation command."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import webbrowser
from pathlib import Path

from noosphere import __version__
from noosphere.validation_kits.public_artifact_runtime_smoke_gate import (
    FORM_URL,
    SKILL_NAME,
    ValidationKitError,
    render_evidence_markdown,
    run_validation,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="noosphere-validate",
        description="Independently reproduce a Noosphere Skill with a deterministic fixture.",
    )
    parser.add_argument("skill", choices=[SKILL_NAME], help="The Skill validation kit to run")
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Evidence output format (default: markdown)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path for the generated evidence; stdout is used by default",
    )
    parser.add_argument(
        "--keep-workdir",
        action="store_true",
        help="Keep generated wheels and the isolated environment for local inspection",
    )
    parser.add_argument(
        "--open-form",
        action="store_true",
        help="Open the GitHub validation form after a successful run",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def configure_console_output() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding=sys.stdout.encoding or "utf-8", errors="replace")


def _render_json(result, workdir: Path | None) -> str:
    data = json.loads(result.as_json())
    data["workdir"] = str(workdir) if workdir else None
    data["submission_url"] = FORM_URL
    return json.dumps(data, ensure_ascii=False, indent=2)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    configure_console_output()
    retained_workdir: Path | None = None

    try:
        if args.keep_workdir:
            retained_workdir = Path(tempfile.mkdtemp(prefix="noosphere-validation-"))
            result = run_validation(retained_workdir)
        else:
            with tempfile.TemporaryDirectory(prefix="noosphere-validation-") as temporary:
                result = run_validation(Path(temporary))

        output = (
            render_evidence_markdown(result) if args.format == "markdown" else _render_json(result, retained_workdir)
        )
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(f"{output}\n", encoding="utf-8")
            print(f"Validation evidence written to {args.output}")
        else:
            print(output)
        if retained_workdir:
            print(f"Validation workdir retained at {retained_workdir}")
        if result.passed and args.open_form:
            webbrowser.open(FORM_URL, new=2)
        return 0 if result.passed else 1
    except (OSError, subprocess.SubprocessError, ValidationKitError) as exc:
        print(f"Validation harness failed: {exc}", file=sys.stderr)
        if retained_workdir:
            print(f"Validation workdir retained at {retained_workdir}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
