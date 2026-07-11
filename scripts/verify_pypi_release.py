#!/usr/bin/env python
"""Verify that a PyPI release installs the expected Noosphere MCP tools."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROJECT = "noosphere-mcp"
DEFAULT_PACKAGE_DIR = "noosphere"
REQUIRED_GROWTH_TOOLS = [
    "record_growth_referral",
    "record_share_attribution",
    "share_attribution_report",
    "growth_flywheel",
    "launch_preflight",
]


def read_project_version(pyproject_path: Path = REPO_ROOT / "sdk" / "pyproject.toml") -> str:
    text = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not find project version in {pyproject_path}")
    return match.group(1)


def fetch_json(url: str, timeout: float = 20.0) -> dict:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "noosphere-release-verifier"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def validate_release_json(data: dict, expected_version: str) -> list[str]:
    actual_version = str(data.get("info", {}).get("version", ""))
    if actual_version != expected_version:
        raise RuntimeError(f"PyPI reports version {actual_version!r}, expected {expected_version!r}")

    filenames = [str(item.get("filename", "")) for item in data.get("urls", []) if isinstance(item, dict)]
    expected_wheel = f"noosphere_mcp-{expected_version}-py3-none-any.whl"
    expected_sdist = f"noosphere_mcp-{expected_version}.tar.gz"
    missing = [name for name in [expected_wheel, expected_sdist] if name not in filenames]
    if missing:
        raise RuntimeError(f"PyPI release {expected_version} is missing distribution(s): {', '.join(missing)}")

    return filenames


def wait_for_pypi_release(project: str, version: str, attempts: int, delay_seconds: float) -> dict:
    url = f"https://pypi.org/pypi/{project}/{version}/json"
    last_error = ""

    for attempt in range(1, attempts + 1):
        try:
            data = fetch_json(url)
            validate_release_json(data, version)
            return data
        except (HTTPError, URLError, TimeoutError, RuntimeError) as exc:
            last_error = str(exc)
            if attempt == attempts:
                break
            print(f"PyPI release not ready yet ({attempt}/{attempts}): {last_error}", flush=True)
            time.sleep(delay_seconds)

    raise RuntimeError(f"PyPI release {project}=={version} did not become verifiable: {last_error}")


def wait_for_pypi_project_latest(project: str, version: str, attempts: int, delay_seconds: float) -> dict:
    url = f"https://pypi.org/pypi/{project}/json"
    last_error = ""

    for attempt in range(1, attempts + 1):
        try:
            data = fetch_json(url)
            validate_release_json(data, version)
            return data
        except (HTTPError, URLError, TimeoutError, RuntimeError) as exc:
            last_error = str(exc)
            if attempt == attempts:
                break
            print(f"PyPI project latest not ready yet ({attempt}/{attempts}): {last_error}", flush=True)
            time.sleep(delay_seconds)

    raise RuntimeError(f"PyPI project {project} latest did not become {version}: {last_error}")


def install_release_to_target(project: str, version: str, target_dir: Path, python_executable: str = sys.executable) -> None:
    command = [
        python_executable,
        "-m",
        "pip",
        "install",
        "--no-cache-dir",
        "--no-deps",
        "--target",
        str(target_dir),
        f"{project}=={version}",
    ]
    subprocess.run(command, check=True)


def wait_for_installable_release(
    project: str,
    version: str,
    target_dir: Path,
    attempts: int,
    delay_seconds: float,
    python_executable: str = sys.executable,
) -> None:
    last_error = ""

    for attempt in range(1, attempts + 1):
        try:
            install_release_to_target(project, version, target_dir, python_executable=python_executable)
            return
        except subprocess.CalledProcessError as exc:
            last_error = str(exc)
            if attempt == attempts:
                break
            print(f"PyPI pip install not ready yet ({attempt}/{attempts}): {last_error}", flush=True)
            time.sleep(delay_seconds)

    raise RuntimeError(f"PyPI release {project}=={version} did not become pip-installable: {last_error}")


def inspect_installed_release(
    target_dir: Path,
    expected_version: str,
    package_dir: str = DEFAULT_PACKAGE_DIR,
    expected_tool_count: int = 45,
) -> dict:
    package_root = target_dir / package_dir
    init_path = package_root / "__init__.py"
    mcp_path = package_root / "noosphere_mcp.py"
    query_cli_path = package_root / "query_cli.py"
    if not init_path.exists() or not mcp_path.exists() or not query_cli_path.exists():
        raise RuntimeError(
            f"Installed package is missing {package_dir}/__init__.py, "
            f"{package_dir}/noosphere_mcp.py, or {package_dir}/query_cli.py"
        )

    init_source = init_path.read_text(encoding="utf-8")
    mcp_source = mcp_path.read_text(encoding="utf-8")

    version_match = re.search(r'__version__\s*=\s*"([^"]+)"', init_source)
    installed_version = version_match.group(1) if version_match else ""
    if installed_version != expected_version:
        raise RuntimeError(f"Installed package version {installed_version!r}, expected {expected_version!r}")

    tool_names = re.findall(
        r"@mcp\.tool\(\)\s*(?:\n[^\n]*)*?\n(?:async\s+def|def)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        mcp_source,
    )
    if len(tool_names) != expected_tool_count:
        raise RuntimeError(f"Installed MCP tool count {len(tool_names)}, expected {expected_tool_count}")

    missing_tools = [tool_name for tool_name in REQUIRED_GROWTH_TOOLS if tool_name not in tool_names]
    if missing_tools:
        raise RuntimeError(f"Installed package is missing growth tool(s): {', '.join(missing_tools)}")

    return {
        "version": installed_version,
        "tool_count": len(tool_names),
        "growth_tools": REQUIRED_GROWTH_TOOLS,
        "query_cli": "noosphere-query",
    }


def verify_pypi_release(project: str, version: str, attempts: int, delay_seconds: float, expected_tool_count: int) -> dict:
    release_json = wait_for_pypi_release(project, version, attempts, delay_seconds)
    filenames = validate_release_json(release_json, version)
    project_json = wait_for_pypi_project_latest(project, version, attempts, delay_seconds)
    latest_filenames = validate_release_json(project_json, version)

    temp_dir = Path(tempfile.mkdtemp(prefix="noosphere-pypi-verify-"))
    try:
        wait_for_installable_release(project, version, temp_dir, attempts, delay_seconds)
        installed = inspect_installed_release(temp_dir, version, expected_tool_count=expected_tool_count)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        "project": project,
        "version": version,
        "files": filenames,
        "latest_files": latest_filenames,
        **installed,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify a published noosphere-mcp PyPI release.")
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--version", default=read_project_version())
    parser.add_argument("--attempts", type=int, default=24)
    parser.add_argument("--delay-seconds", type=float, default=10.0)
    parser.add_argument("--tool-count", type=int, default=45)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = verify_pypi_release(args.project, args.version, args.attempts, args.delay_seconds, args.tool_count)
    print(
        f"Verified {result['project']}=={result['version']}: "
        f"{result['tool_count']} MCP tools, growth ledger tools and noosphere-query present."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
