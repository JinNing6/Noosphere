"""
Tests for the Noosphere MCP Pre-flight Diagnostics module.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from noosphere.preflight import (
    check_dependencies,
    check_env_vars,
    check_github_connectivity,
    run_preflight,
    format_diagnostics,
    PreflightResult,
    CheckItem,
)


# ────────────────── Tests: check_dependencies ──────────────────


def test_check_dependencies_all_present():
    """All required deps are installed — all checks pass."""
    results = check_dependencies()
    assert len(results) == 2
    assert all(r.passed for r in results)


def test_check_dependencies_httpx_missing():
    """Simulate httpx not installed."""
    import importlib

    original_import = importlib.import_module

    def mock_import(name):
        if name == "httpx":
            raise ImportError("No module named 'httpx'")
        return original_import(name)

    with patch("importlib.import_module", side_effect=mock_import):
        results = check_dependencies()

    httpx_check = [r for r in results if "httpx" in r.name][0]
    assert not httpx_check.passed
    assert "缺失" in httpx_check.message
    assert "pip install httpx" in httpx_check.suggestion


def test_check_dependencies_mcp_missing():
    """Simulate mcp not installed."""
    import importlib

    original_import = importlib.import_module

    def mock_import(name):
        if name == "mcp":
            raise ImportError("No module named 'mcp'")
        return original_import(name)

    with patch("importlib.import_module", side_effect=mock_import):
        results = check_dependencies()

    mcp_check = [r for r in results if "mcp" in r.name][0]
    assert not mcp_check.passed
    assert "缺失" in mcp_check.message
    assert "pip install" in mcp_check.suggestion


def test_check_dependencies_all_missing():
    """Simulate all deps missing."""
    import importlib

    def mock_import(name):
        raise ImportError(f"No module named '{name}'")

    with patch("importlib.import_module", side_effect=mock_import):
        results = check_dependencies()

    assert len(results) == 2
    assert all(not r.passed for r in results)
    assert all(r.suggestion for r in results)


# ────────────────── Tests: check_env_vars ──────────────────


def test_check_env_vars_all_set():
    """Both GITHUB_TOKEN and NOOSPHERE_REPO are correctly configured."""
    with patch.dict(os.environ, {
        "GITHUB_TOKEN": "ghp_test1234567890abcdef",
        "NOOSPHERE_REPO": "JinNing6/Noosphere",
    }):
        results = check_env_vars()

    assert len(results) == 2
    assert all(r.passed for r in results)


def test_check_env_vars_no_token():
    """GITHUB_TOKEN is not set."""
    with patch.dict(os.environ, {"NOOSPHERE_REPO": "JinNing6/Noosphere"}, clear=False):
        # Remove GITHUB_TOKEN if present
        env = os.environ.copy()
        env.pop("GITHUB_TOKEN", None)
        with patch.dict(os.environ, env, clear=True):
            results = check_env_vars()

    token_check = [r for r in results if "GITHUB_TOKEN" in r.name][0]
    assert not token_check.passed
    assert "未配置" in token_check.message
    assert "github.com/settings/tokens" in token_check.suggestion


def test_check_env_vars_invalid_token_format():
    """GITHUB_TOKEN has unexpected format."""
    with patch.dict(os.environ, {
        "GITHUB_TOKEN": "invalid_token_format_12345",
        "NOOSPHERE_REPO": "JinNing6/Noosphere",
    }, clear=False):
        results = check_env_vars()

    token_check = [r for r in results if "GITHUB_TOKEN" in r.name][0]
    assert not token_check.passed
    assert "格式异常" in token_check.message


def test_check_env_vars_valid_token_prefixes():
    """Verify all valid GitHub token prefixes are accepted."""
    valid_prefixes = ["ghp_", "gho_", "ghs_", "ghu_", "github_pat_"]
    for prefix in valid_prefixes:
        with patch.dict(os.environ, {
            "GITHUB_TOKEN": f"{prefix}test1234567890",
            "NOOSPHERE_REPO": "JinNing6/Noosphere",
        }, clear=False):
            results = check_env_vars()
            token_check = [r for r in results if "GITHUB_TOKEN" in r.name][0]
            assert token_check.passed, f"Token with prefix '{prefix}' should be valid"


def test_check_env_vars_bad_repo_format():
    """NOOSPHERE_REPO has invalid format (not owner/repo)."""
    with patch.dict(os.environ, {
        "GITHUB_TOKEN": "ghp_test1234567890abcdef",
        "NOOSPHERE_REPO": "invalid-format",
    }, clear=False):
        results = check_env_vars()

    repo_check = [r for r in results if "NOOSPHERE_REPO" in r.name][0]
    assert not repo_check.passed
    assert "格式错误" in repo_check.message


def test_check_env_vars_missing_repo_uses_default():
    """NOOSPHERE_REPO not set — should use default and pass."""
    env = os.environ.copy()
    env.pop("NOOSPHERE_REPO", None)
    env["GITHUB_TOKEN"] = "ghp_test1234567890abcdef"
    with patch.dict(os.environ, env, clear=True):
        results = check_env_vars()

    repo_check = [r for r in results if "NOOSPHERE_REPO" in r.name][0]
    assert repo_check.passed
    assert "默认值" in repo_check.message


# ────────────────── Tests: check_github_connectivity ──────────────────


def test_check_github_connectivity_no_token():
    """Should skip connectivity check when no token is available."""
    env = os.environ.copy()
    env.pop("GITHUB_TOKEN", None)
    with patch.dict(os.environ, env, clear=True):
        results = check_github_connectivity()

    assert len(results) == 1
    assert not results[0].passed
    assert "跳过" in results[0].message


def test_check_github_connectivity_success():
    """Simulate successful GitHub API connection."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"login": "testuser"}

    with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test12345"}, clear=False):
        with patch("httpx.get", return_value=mock_response):
            results = check_github_connectivity()

    assert len(results) == 1
    assert results[0].passed
    assert "@testuser" in results[0].message


def test_check_github_connectivity_401():
    """Simulate invalid/expired token."""
    mock_response = MagicMock()
    mock_response.status_code = 401

    with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_expired12345"}, clear=False):
        with patch("httpx.get", return_value=mock_response):
            results = check_github_connectivity()

    assert len(results) == 1
    assert not results[0].passed
    assert "401" in results[0].message
    assert "过期" in results[0].suggestion


def test_check_github_connectivity_403():
    """Simulate rate limiting."""
    mock_response = MagicMock()
    mock_response.status_code = 403

    with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_ratelimited"}, clear=False):
        with patch("httpx.get", return_value=mock_response):
            results = check_github_connectivity()

    assert len(results) == 1
    assert not results[0].passed
    assert "403" in results[0].message


def test_check_github_connectivity_timeout():
    """Simulate network timeout."""
    import httpx

    with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test12345"}, clear=False):
        with patch("httpx.get", side_effect=httpx.TimeoutException("Connection timed out")):
            results = check_github_connectivity()

    assert len(results) == 1
    assert not results[0].passed
    assert "连接失败" in results[0].message
    assert "超时" in results[0].suggestion or "代理" in results[0].suggestion


def test_check_github_connectivity_connection_error():
    """Simulate DNS/connection failure."""
    with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test12345"}, clear=False):
        with patch("httpx.get", side_effect=ConnectionError("Failed to resolve 'api.github.com'")):
            results = check_github_connectivity()

    assert len(results) == 1
    assert not results[0].passed
    assert "连接失败" in results[0].message


# ────────────────── Tests: run_preflight (aggregated) ──────────────────


def test_run_preflight_all_pass():
    """Full preflight with all checks passing."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"login": "testuser"}

    with patch.dict(os.environ, {
        "GITHUB_TOKEN": "ghp_test1234567890abcdef",
        "NOOSPHERE_REPO": "JinNing6/Noosphere",
    }, clear=False):
        with patch("httpx.get", return_value=mock_response):
            result = run_preflight()

    assert result.passed
    assert result.all_clear


def test_run_preflight_skip_network():
    """Preflight with network check skipped."""
    with patch.dict(os.environ, {
        "GITHUB_TOKEN": "ghp_test1234567890abcdef",
        "NOOSPHERE_REPO": "JinNing6/Noosphere",
    }, clear=False):
        result = run_preflight(skip_network=True)

    # Should only have dependency + env checks (no network)
    check_names = [c.name_en for c in result.checks]
    assert not any("Network" in n for n in check_names)
    assert result.passed


def test_run_preflight_with_dep_error():
    """Preflight fails when dependencies are missing."""
    import importlib

    def mock_import(name):
        if name == "httpx":
            raise ImportError("No module named 'httpx'")
        return importlib.__import__(name)

    with patch("importlib.import_module", side_effect=mock_import):
        with patch.dict(os.environ, {
            "GITHUB_TOKEN": "ghp_test1234567890abcdef",
        }, clear=False):
            result = run_preflight(skip_network=True)

    # Should have errors (dependencies are fatal)
    assert not result.passed
    assert len(result.errors) > 0


# ────────────────── Tests: format_diagnostics ──────────────────


def test_format_diagnostics_all_pass():
    """Verify formatting for all-clear result."""
    result = PreflightResult(checks=[
        CheckItem("依赖: httpx", "Dependency: httpx", True, "httpx ✓"),
        CheckItem("环境变量: GITHUB_TOKEN", "Env: GITHUB_TOKEN", True, "已配置"),
    ])
    output = format_diagnostics(result)
    assert "全部通过" in output
    assert "Pre-flight" in output


def test_format_diagnostics_with_errors():
    """Verify formatting for fatal errors."""
    result = PreflightResult(checks=[
        CheckItem("依赖: httpx", "Dependency: httpx", False, "缺失 httpx", "pip install httpx"),
    ])
    output = format_diagnostics(result)
    assert "启动失败" in output
    assert "pip install httpx" in output
    assert "无法启动" in output


def test_format_diagnostics_with_warnings():
    """Verify formatting for warnings (non-fatal)."""
    result = PreflightResult(checks=[
        CheckItem("依赖: httpx", "Dependency: httpx", True, "httpx ✓"),
        CheckItem("网络: GitHub API", "Network: GitHub API", False, "跳过"),
    ])
    output = format_diagnostics(result)
    assert "部分警告" in output
