import json
import re
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 release runners
    import tomli as tomllib


REPO_ROOT = Path(__file__).resolve().parents[2]
SDK_ROOT = REPO_ROOT / "sdk"
PYPI_BASELINE_VERSION = "0.6.0"


def _version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def _project_metadata() -> dict:
    return tomllib.loads((SDK_ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def _package_version() -> str:
    source = (SDK_ROOT / "noosphere" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"([^"]+)"', source)
    assert match, "noosphere.__version__ must be declared for release verification"
    return match.group(1)


def test_release_versions_are_synchronized_and_newer_than_pypi_baseline():
    project_version = _project_metadata()["project"]["version"]
    sdk_server_manifest = json.loads((SDK_ROOT / "server.json").read_text(encoding="utf-8"))
    root_server_manifest = json.loads((REPO_ROOT / "server.json").read_text(encoding="utf-8"))
    expected_release_version = _package_version()

    assert project_version == expected_release_version
    assert sdk_server_manifest["version"] == expected_release_version
    assert sdk_server_manifest["packages"][0]["version"] == expected_release_version
    assert root_server_manifest["version"] == expected_release_version
    assert root_server_manifest["packages"][0]["version"] == expected_release_version
    assert _version_tuple(project_version) > _version_tuple(PYPI_BASELINE_VERSION)


def test_release_exposes_zero_configuration_read_only_query_command():
    scripts = _project_metadata()["project"]["scripts"]

    assert scripts["noosphere-query"] == "noosphere.query_cli:main"
    assert (SDK_ROOT / "noosphere" / "query_cli.py").is_file()


def test_release_exposes_deterministic_living_skill_validation_command():
    scripts = _project_metadata()["project"]["scripts"]

    assert scripts["noosphere-validate"] == "noosphere.validation_cli:main"
    assert (SDK_ROOT / "noosphere" / "validation_cli.py").is_file()
    assert (SDK_ROOT / "noosphere" / "validation_kits" / "public_artifact_runtime_smoke_gate.py").is_file()


def test_default_runtime_excludes_optional_semantic_model_stack():
    project = _project_metadata()["project"]

    assert project["dependencies"] == [
        "mcp>=1.27,<2",
        "httpx>=0.28.0",
    ]
    assert project["optional-dependencies"]["semantic"] == [
        "sentence-transformers>=2.2.0",
        "numpy>=1.24.0",
    ]


def test_mcp_handshake_advertises_noosphere_distribution_version():
    from noosphere.noosphere_mcp import mcp

    assert mcp._mcp_server.version == _package_version()


def test_publish_workflow_uses_single_release_trigger_with_trusted_publishing_quality_gates():
    workflow = (REPO_ROOT / ".github" / "workflows" / "publish-pypi.yml").read_text(encoding="utf-8")

    assert "release:" in workflow
    assert "types: [published]" in workflow
    assert "push:" not in workflow
    assert "tags:" not in workflow
    assert "workflow_dispatch" not in workflow
    assert "PYPI_TOKEN" not in workflow
    assert "password:" not in workflow
    assert re.search(r"permissions:\s*\n\s*id-token:\s*write", workflow)
    assert "environment:" in workflow and "name: pypi" in workflow
    assert "pypa/gh-action-pypi-publish@release/v1" in workflow

    assert "python -m pytest tests" in workflow
    assert "node --test .github/scripts/*.test.cjs" in workflow
    assert "python scripts/validate_shared_skills.py" in workflow
    assert "scripts.test_migrate_consciousness_promotions" in workflow
    assert "python scripts/migrate_consciousness_promotions.py --check" in workflow
    assert "python -m unittest scripts.test_verify_pypi_release" in workflow
    assert "import noosphere.noosphere_mcp" in workflow
    assert "python -m build" in workflow
    assert "verify-pypi:" in workflow
    assert "needs: publish-pypi" in workflow
    assert "python scripts/verify_pypi_release.py --tool-count 45" in workflow
    assert "initialize + tools/list" in workflow
    assert "refresh-pages-proof:" in workflow
    assert "needs: verify-pypi" in workflow
    assert "actions: write" in workflow
    assert "Dispatch Pages deploy on main after PyPI verification" in workflow
    assert "/actions/workflows/deploy-pages.yml/dispatches" in workflow
    assert """-d '{"ref":"main"}'""" in workflow


def test_package_release_includes_growth_ledger_tools():
    source = (SDK_ROOT / "noosphere" / "noosphere_mcp.py").read_text(encoding="utf-8")
    tool_names = re.findall(
        r"@mcp\.tool\(\)\s*(?:\n[^\n]*)*?\n(?:async\s+def|def)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        source,
    )

    assert len(tool_names) == 45
    for tool_name in [
        "record_growth_referral",
        "record_share_attribution",
        "share_attribution_report",
        "growth_flywheel",
        "launch_preflight",
        "list_shared_skills",
        "get_shared_skill",
        "check_skill_updates",
        "record_skill_outcome",
        "request_shared_skill_withdrawal",
    ]:
        assert tool_name in tool_names


def test_readme_documents_pypi_release_recovery_route():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert f"v{_package_version()}" in readme
    assert ".github/workflows/publish-pypi.yml" in readme
    assert "Trusted Publishing" in readme
    assert "45 MCP tools" in readme
    assert "noosphere-validate public-artifact-runtime-smoke-gate" in readme
