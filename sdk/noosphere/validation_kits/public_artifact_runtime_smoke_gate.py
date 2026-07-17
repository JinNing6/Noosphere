"""Reproduce source-versus-public-artifact runtime drift without a user project."""

from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import os
import platform
import subprocess
import sys
import time
import venv
import zipfile
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlencode

SKILL_NAME = "public-artifact-runtime-smoke-gate"
VALIDATION_COMMAND = "uvx --from noosphere-mcp noosphere-validate public-artifact-runtime-smoke-gate"
FORM_URL = "https://github.com/JinNing6/Noosphere/issues/new?template=validate-skill.yml"
ISSUE_NEW_URL = "https://github.com/JinNing6/Noosphere/issues/new"
FIXTURE_URL = (
    "https://github.com/JinNing6/Noosphere/tree/main/examples/reproductions/public-artifact-runtime-smoke-gate"
)
SEED_URL = "https://github.com/JinNing6/Noosphere/issues/37"

DIST_NAME = "noosphere-public-artifact-fixture"
PACKAGE_NAME = "noosphere_public_artifact_fixture"
ENTRY_POINT = "noosphere-runtime-fixture"
FAILING_VERSION = "1.0.0"
FIXED_VERSION = "1.0.1"

PAYLOAD_START = "<!-- CONSCIOUSNESS_PAYLOAD_START -->"
PAYLOAD_END = "<!-- CONSCIOUSNESS_PAYLOAD_END -->"


class ValidationKitError(RuntimeError):
    """Raised when the validation harness itself cannot complete."""


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str

    @property
    def combined_output(self) -> str:
        return "\n".join(part for part in [self.stdout.strip(), self.stderr.strip()] if part).strip()


@dataclass(frozen=True)
class ValidationResult:
    skill_name: str
    passed: bool
    duration_seconds: float
    environment: str
    source_exit_code: int
    failing_artifact_exit_code: int
    fixed_artifact_exit_code: int
    failing_artifact_sha256: str
    fixed_artifact_sha256: str
    installed_fixed_version: str
    observed_failure: str
    observed_success: str
    workdir: str | None = None

    def as_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)


def _runtime_module(version: str) -> bytes:
    source = f'''"""Runtime entry point for the Noosphere public-artifact fixture."""

import json

from . import __version__


def main() -> int:
    print(json.dumps({{
        "distribution": "{DIST_NAME}",
        "status": "runtime-ok",
        "version": __version__,
    }}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
    return source.encode("utf-8")


def _package_init(version: str) -> bytes:
    return f'__version__ = "{version}"\n'.encode()


def _record_line(path: str, content: bytes) -> list[str]:
    digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode("ascii")
    return [path, f"sha256={digest}", str(len(content))]


def _record_bytes(files: dict[str, bytes], record_path: str) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    for path in sorted(files):
        writer.writerow(_record_line(path, files[path]))
    writer.writerow([record_path, "", ""])
    return output.getvalue().encode("utf-8")


def build_fixture_wheel(destination: Path, version: str, *, include_runtime_module: bool) -> Path:
    """Build a deterministic pure-Python wheel using only the standard library."""
    destination.mkdir(parents=True, exist_ok=True)
    normalized_dist = DIST_NAME.replace("-", "_")
    dist_info = f"{normalized_dist}-{version}.dist-info"
    wheel_name = f"{normalized_dist}-{version}-py3-none-any.whl"
    wheel_path = destination / wheel_name

    files: dict[str, bytes] = {
        f"{PACKAGE_NAME}/__init__.py": _package_init(version),
        f"{dist_info}/METADATA": (
            "Metadata-Version: 2.1\n"
            f"Name: {DIST_NAME}\n"
            f"Version: {version}\n"
            "Summary: Deterministic Noosphere validation fixture\n"
        ).encode(),
        f"{dist_info}/WHEEL": (
            b"Wheel-Version: 1.0\nGenerator: noosphere-validate\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
        ),
        f"{dist_info}/entry_points.txt": (
            f"[console_scripts]\n{ENTRY_POINT} = {PACKAGE_NAME}.__main__:main\n"
        ).encode(),
        f"{dist_info}/top_level.txt": f"{PACKAGE_NAME}\n".encode(),
    }
    if include_runtime_module:
        files[f"{PACKAGE_NAME}/__main__.py"] = _runtime_module(version)

    record_path = f"{dist_info}/RECORD"
    files[record_path] = _record_bytes(files, record_path)

    # Stored entries keep the fixture byte-identical across zlib implementations.
    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o644 << 16
            archive.writestr(info, files[name])
    return wheel_path


def _clean_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for key in ["PYTHONHOME", "PYTHONPATH", "GITHUB_TOKEN", "GH_TOKEN"]:
        environment.pop(key, None)
    environment["PYTHONNOUSERSITE"] = "1"
    environment["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    return environment


def _run(command: Sequence[str | os.PathLike[str]], *, cwd: Path, timeout: int = 90) -> CommandResult:
    completed = subprocess.run(
        [os.fspath(item) for item in command],
        cwd=cwd,
        env=_clean_environment(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)


def _require_success(result: CommandResult, operation: str) -> None:
    if result.returncode != 0:
        detail = result.combined_output[-2000:] or "no output"
        raise ValidationKitError(f"{operation} failed with exit code {result.returncode}: {detail}")


def _venv_python(environment: Path) -> Path:
    return environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _venv_entry_point(environment: Path) -> Path:
    suffix = ".exe" if os.name == "nt" else ""
    return environment / ("Scripts" if os.name == "nt" else "bin") / f"{ENTRY_POINT}{suffix}"


def _safe_output(value: str, workdir: Path, *, max_length: int = 1600) -> str:
    normalized = value.replace(str(workdir), "<validation-workdir>")
    normalized = normalized.replace(str(workdir).replace("\\", "/"), "<validation-workdir>")
    return normalized.strip()[-max_length:]


def _environment_summary() -> str:
    return " / ".join(
        [
            platform.system() or "unknown-os",
            platform.release() or "unknown-release",
            platform.machine() or "unknown-architecture",
            f"Python {platform.python_version()}",
        ]
    )


def run_validation(workdir: Path) -> ValidationResult:
    """Run the complete source, failing-artifact, and fixed-artifact lifecycle."""
    started = time.monotonic()
    workdir = workdir.resolve()
    source_root = workdir / "source"
    package_root = source_root / PACKAGE_NAME
    wheelhouse = workdir / "wheelhouse"
    runtime_root = workdir / "runtime"
    environment = workdir / "isolated-environment"
    package_root.mkdir(parents=True, exist_ok=True)
    runtime_root.mkdir(parents=True, exist_ok=True)
    (package_root / "__init__.py").write_bytes(_package_init(FIXED_VERSION))
    (package_root / "__main__.py").write_bytes(_runtime_module(FIXED_VERSION))

    source_result = _run([sys.executable, "-m", PACKAGE_NAME], cwd=source_root)
    if source_result.returncode != 0 or '"status": "runtime-ok"' not in source_result.stdout:
        raise ValidationKitError(
            "The fixture source tree did not pass before artifact packaging: "
            f"{_safe_output(source_result.combined_output, workdir)}"
        )

    failing_wheel = build_fixture_wheel(wheelhouse, FAILING_VERSION, include_runtime_module=False)
    fixed_wheel = build_fixture_wheel(wheelhouse, FIXED_VERSION, include_runtime_module=True)
    failing_sha = hashlib.sha256(failing_wheel.read_bytes()).hexdigest()
    fixed_sha = hashlib.sha256(fixed_wheel.read_bytes()).hexdigest()

    venv.EnvBuilder(with_pip=True, clear=True).create(environment)
    python = _venv_python(environment)
    install_failing = _run(
        [python, "-m", "pip", "install", "--no-index", "--no-deps", failing_wheel],
        cwd=runtime_root,
    )
    _require_success(install_failing, "Installing the failing fixture wheel")

    entry_point = _venv_entry_point(environment)
    if not entry_point.is_file():
        raise ValidationKitError(f"Installed console entry point was not created: {entry_point}")
    failing_result = _run([entry_point], cwd=runtime_root)

    install_fixed = _run(
        [
            python,
            "-m",
            "pip",
            "install",
            "--no-index",
            "--no-deps",
            "--force-reinstall",
            fixed_wheel,
        ],
        cwd=runtime_root,
    )
    _require_success(install_fixed, "Installing the fixed fixture wheel")
    fixed_result = _run([entry_point], cwd=runtime_root)
    version_result = _run(
        [
            python,
            "-I",
            "-c",
            (f"import importlib.metadata as m; print(m.version('{DIST_NAME}'))"),
        ],
        cwd=runtime_root,
    )

    observed_failure = _safe_output(failing_result.combined_output, workdir)
    observed_success = _safe_output(fixed_result.combined_output, workdir)
    installed_version = version_result.stdout.strip()
    passed = all(
        [
            source_result.returncode == 0,
            failing_result.returncode != 0,
            "no module named" in observed_failure.lower(),
            f"{PACKAGE_NAME}.__main__" in observed_failure,
            fixed_result.returncode == 0,
            '"status": "runtime-ok"' in observed_success,
            version_result.returncode == 0,
            installed_version == FIXED_VERSION,
        ]
    )

    return ValidationResult(
        skill_name=SKILL_NAME,
        passed=passed,
        duration_seconds=round(time.monotonic() - started, 2),
        environment=_environment_summary(),
        source_exit_code=source_result.returncode,
        failing_artifact_exit_code=failing_result.returncode,
        fixed_artifact_exit_code=fixed_result.returncode,
        failing_artifact_sha256=failing_sha,
        fixed_artifact_sha256=fixed_sha,
        installed_fixed_version=installed_version,
        observed_failure=observed_failure,
        observed_success=observed_success,
        workdir=None,
    )


def build_evidence_payload(result: ValidationResult) -> dict:
    if not result.passed:
        raise ValidationKitError("A failed harness run cannot be submitted as verified evidence")
    verification = (
        f"Source invocation exited {result.source_exit_code}; the installed failing artifact exited "
        f"{result.failing_artifact_exit_code}; the fixed artifact exited "
        f"{result.fixed_artifact_exit_code} and reported version {result.installed_fixed_version}. "
        f"Failing SHA-256: {result.failing_artifact_sha256}. "
        f"Fixed SHA-256: {result.fixed_artifact_sha256}."
    )
    return {
        "creator_signature": "independent-validator",
        "is_anonymous": False,
        "consciousness_type": "pattern",
        "target_skill": SKILL_NAME,
        "thought_vector_text": (
            "Source-tree tests can pass while the installed release omits a runtime module. "
            "Validate the exact artifact in a clean environment before declaring a CLI, package, "
            "MCP server, or Agent plugin releasable."
        ),
        "context_environment": (
            f"Independent deterministic fixture executed on {result.environment}. "
            "No validator-owned project, GitHub token, or external package index was used."
        ),
        "tags": ["build-release", "artifact-runtime", "python-packaging", "mcp"],
        "evidence": {
            "symptom": (
                "The source-tree entry point succeeds, but the console entry point installed from "
                "the failing wheel exits non-zero because its runtime module is absent."
            ),
            "root_cause": (
                "Release checks exercised the source tree instead of the exact built artifact. "
                "The wheel metadata exposed a console entry point while packaging omitted the module "
                "that implements it."
            ),
            "fix": (
                "Install the exact artifact in a clean environment, verify the installed distribution "
                "version, invoke its real console entry point, and assert the runtime contract. Include "
                "the entry-point module in the immutable artifact."
            ),
            "verification": verification,
            "applies_when": (
                "A Python package, CLI, MCP server, or Agent plugin passes source CI but may differ "
                "after wheel or public-registry installation."
            ),
            "avoid_when": (
                "Do not attribute failures to packaging when the exact artifact was never resolved, "
                "or when the distribution intentionally exposes no runtime entry point."
            ),
            "test_commands": [VALIDATION_COMMAND],
            "source_urls": [FIXTURE_URL, SEED_URL],
        },
    }


def _evidence_block(payload: dict, *, pretty: bool) -> str:
    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        indent=2 if pretty else None,
        separators=None if pretty else (",", ":"),
    )
    return "\n".join(
        [
            PAYLOAD_START,
            "```json",
            serialized,
            "```",
            PAYLOAD_END,
        ]
    )


def build_submission_url(result: ValidationResult) -> str:
    """Build a token-free GitHub Issue Form URL with canonical evidence prefilled."""
    payload = build_evidence_payload(result)
    query = urlencode(
        {
            "template": "validate-skill.yml",
            "title": f"Skill validation: {SKILL_NAME}",
            "generated_validation_evidence": _evidence_block(payload, pretty=False),
        }
    )
    return f"{ISSUE_NEW_URL}?{query}"


def render_evidence_markdown(result: ValidationResult) -> str:
    payload = build_evidence_payload(result)
    submission_url = build_submission_url(result)
    return "\n".join(
        [
            "# Noosphere Skill validation",
            "",
            "- Result: **PASS**",
            f"- Skill: `{SKILL_NAME}`",
            f"- Environment: `{result.environment}`",
            f"- Duration: `{result.duration_seconds:.2f}s`",
            f"- Failing artifact: `{result.failing_artifact_sha256}`",
            f"- Fixed artifact: `{result.fixed_artifact_sha256}`",
            "",
            "The submission link below already contains this canonical evidence block:",
            "",
            _evidence_block(payload, pretty=True),
            "",
            "Open the prefilled form, review the evidence, confirm the declaration, and submit:",
            f"{submission_url}",
            "",
            "The repository workflow binds authorship to the submitting GitHub account and "
            "review-gates the evidence before it can affect a published Skill.",
        ]
    )
