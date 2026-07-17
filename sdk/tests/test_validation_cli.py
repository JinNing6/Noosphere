import hashlib
import json
import zipfile
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import pytest

from noosphere.validation_cli import build_parser, main
from noosphere.validation_kits.public_artifact_runtime_smoke_gate import (
    FIXED_VERSION,
    FORM_URL,
    PACKAGE_NAME,
    PAYLOAD_END,
    PAYLOAD_START,
    SKILL_NAME,
    VALIDATION_COMMAND,
    build_evidence_payload,
    build_fixture_wheel,
    build_submission_url,
    render_evidence_markdown,
    run_validation,
)


@pytest.fixture(scope="module")
def completed_validation(tmp_path_factory):
    return run_validation(tmp_path_factory.mktemp("public-artifact-validation"))


def test_fixture_wheels_are_byte_deterministic_and_expose_the_same_entry_point(tmp_path):
    first = build_fixture_wheel(tmp_path / "first", "1.0.1", include_runtime_module=True)
    second = build_fixture_wheel(tmp_path / "second", "1.0.1", include_runtime_module=True)

    assert first.read_bytes() == second.read_bytes()
    assert hashlib.sha256(first.read_bytes()).hexdigest() == hashlib.sha256(second.read_bytes()).hexdigest()

    with zipfile.ZipFile(first) as archive:
        names = set(archive.namelist())
        entry_points = archive.read("noosphere_public_artifact_fixture-1.0.1.dist-info/entry_points.txt").decode(
            "utf-8"
        )

    assert f"{PACKAGE_NAME}/__main__.py" in names
    assert "noosphere-runtime-fixture = noosphere_public_artifact_fixture.__main__:main" in entry_points


def test_validation_reproduces_the_artifact_failure_and_verifies_the_fix(completed_validation):
    result = completed_validation

    assert result.passed is True
    assert result.source_exit_code == 0
    assert result.failing_artifact_exit_code != 0
    assert result.fixed_artifact_exit_code == 0
    assert result.installed_fixed_version == FIXED_VERSION
    assert "no module named" in result.observed_failure.lower()
    assert f"{PACKAGE_NAME}.__main__" in result.observed_failure
    assert '"status": "runtime-ok"' in result.observed_success
    assert "<validation-workdir>" in result.observed_failure
    assert result.duration_seconds < 60


def test_generated_evidence_is_canonical_and_submission_ready(completed_validation):
    payload = build_evidence_payload(completed_validation)
    markdown = render_evidence_markdown(completed_validation)
    marker_body = markdown.split(PAYLOAD_START, 1)[1].split(PAYLOAD_END, 1)[0].strip()
    parsed = json.loads(marker_body.removeprefix("```json").removesuffix("```").strip())

    assert parsed == payload
    assert payload["target_skill"] == SKILL_NAME
    assert payload["evidence"]["test_commands"] == [VALIDATION_COMMAND]
    assert len(payload["evidence"]["source_urls"]) == 2
    assert all(url.startswith("https://github.com/") for url in payload["evidence"]["source_urls"])
    assert FORM_URL in markdown


def test_submission_url_prefills_canonical_evidence_without_credentials(completed_validation):
    submission_url = build_submission_url(completed_validation)
    parsed_url = urlsplit(submission_url)
    query = parse_qs(parsed_url.query)
    marker_body = query["generated_validation_evidence"][0].split(PAYLOAD_START, 1)[1].split(PAYLOAD_END, 1)[0].strip()
    parsed_payload = json.loads(marker_body.removeprefix("```json").removesuffix("```").strip())

    assert parsed_url.scheme == "https"
    assert parsed_url.netloc == "github.com"
    assert query["template"] == ["validate-skill.yml"]
    assert query["title"] == [f"Skill validation: {SKILL_NAME}"]
    assert parsed_payload == build_evidence_payload(completed_validation)
    assert len(submission_url) < 8000
    assert "token=" not in submission_url.lower()


def test_cli_has_one_explicit_kit_and_writes_generated_evidence(tmp_path, completed_validation):
    args = build_parser().parse_args([SKILL_NAME, "--format", "markdown"])
    output = tmp_path / "evidence.md"

    assert args.skill == SKILL_NAME
    with patch("noosphere.validation_cli.run_validation", return_value=completed_validation):
        exit_code = main([SKILL_NAME, "--output", str(output)])

    assert exit_code == 0
    assert PAYLOAD_START in output.read_text(encoding="utf-8")


def test_cli_opens_the_prefilled_submission_url(completed_validation):
    expected_url = build_submission_url(completed_validation)
    with (
        patch("noosphere.validation_cli.run_validation", return_value=completed_validation),
        patch("noosphere.validation_cli.webbrowser.open") as open_browser,
    ):
        exit_code = main([SKILL_NAME, "--format", "json", "--open-form"])

    assert exit_code == 0
    open_browser.assert_called_once_with(expected_url, new=2)
