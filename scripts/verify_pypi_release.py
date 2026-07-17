#!/usr/bin/env python
"""Verify that a PyPI release installs the expected Noosphere MCP tools."""

from __future__ import annotations

import argparse
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from collections.abc import Sequence
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
MCP_PROBE_PROTOCOL_VERSION = "2024-11-05"


def read_project_version(
    pyproject_path: Path = REPO_ROOT / "sdk" / "pyproject.toml",
) -> str:
    text = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not find project version in {pyproject_path}")
    return match.group(1)


def fetch_json(url: str, timeout: float = 20.0) -> dict:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "noosphere-release-verifier",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def validate_release_json(data: dict, expected_version: str) -> list[str]:
    actual_version = str(data.get("info", {}).get("version", ""))
    if actual_version != expected_version:
        raise RuntimeError(
            f"PyPI reports version {actual_version!r}, expected {expected_version!r}"
        )

    filenames = [
        str(item.get("filename", ""))
        for item in data.get("urls", [])
        if isinstance(item, dict)
    ]
    expected_wheel = f"noosphere_mcp-{expected_version}-py3-none-any.whl"
    expected_sdist = f"noosphere_mcp-{expected_version}.tar.gz"
    missing = [
        name for name in [expected_wheel, expected_sdist] if name not in filenames
    ]
    if missing:
        raise RuntimeError(
            f"PyPI release {expected_version} is missing distribution(s): {', '.join(missing)}"
        )

    return filenames


def wait_for_pypi_release(
    project: str, version: str, attempts: int, delay_seconds: float
) -> dict:
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
            print(
                f"PyPI release not ready yet ({attempt}/{attempts}): {last_error}",
                flush=True,
            )
            time.sleep(delay_seconds)

    raise RuntimeError(
        f"PyPI release {project}=={version} did not become verifiable: {last_error}"
    )


def wait_for_pypi_project_latest(
    project: str, version: str, attempts: int, delay_seconds: float
) -> dict:
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
            print(
                f"PyPI project latest not ready yet ({attempt}/{attempts}): {last_error}",
                flush=True,
            )
            time.sleep(delay_seconds)

    raise RuntimeError(
        f"PyPI project {project} latest did not become {version}: {last_error}"
    )


def install_release_to_target(
    project: str,
    version: str,
    target_dir: Path,
    python_executable: str = sys.executable,
) -> None:
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
            install_release_to_target(
                project, version, target_dir, python_executable=python_executable
            )
            return
        except subprocess.CalledProcessError as exc:
            last_error = str(exc)
            if attempt == attempts:
                break
            print(
                f"PyPI pip install not ready yet ({attempt}/{attempts}): {last_error}",
                flush=True,
            )
            time.sleep(delay_seconds)

    raise RuntimeError(
        f"PyPI release {project}=={version} did not become pip-installable: {last_error}"
    )


def runtime_python_command(runtime_dir: Path) -> Path:
    if os.name == "nt":
        return runtime_dir / "Scripts" / "python.exe"
    return runtime_dir / "bin" / "python"


def runtime_console_command(runtime_dir: Path) -> Path:
    if os.name == "nt":
        return runtime_dir / "Scripts" / "noosphere-mcp.exe"
    return runtime_dir / "bin" / "noosphere-mcp"


def runtime_validation_command(runtime_dir: Path) -> Path:
    if os.name == "nt":
        return runtime_dir / "Scripts" / "noosphere-validate.exe"
    return runtime_dir / "bin" / "noosphere-validate"


def install_runtime_environment(
    project: str,
    version: str,
    runtime_dir: Path,
    python_executable: str = sys.executable,
) -> None:
    subprocess.run(
        [python_executable, "-m", "venv", str(runtime_dir)],
        check=True,
    )
    subprocess.run(
        [
            str(runtime_python_command(runtime_dir)),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-cache-dir",
            f"{project}=={version}",
        ],
        check=True,
    )


def build_mcp_probe_messages() -> list[dict]:
    return [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": MCP_PROBE_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {
                    "name": "noosphere-release-verifier",
                    "version": "1.0",
                },
            },
        },
        {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        },
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        },
    ]


def build_mcp_probe_input() -> str:
    messages = build_mcp_probe_messages()
    return "".join(
        json.dumps(message, separators=(",", ":")) + "\n" for message in messages
    )


def probe_mcp_subprocess(
    command: Sequence[str],
    *,
    env: dict[str, str] | None = None,
    timeout_seconds: float = 30.0,
) -> dict:
    started = time.monotonic()
    process = subprocess.Popen(
        list(command),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        bufsize=1,
    )
    if process.stdin is None or process.stdout is None or process.stderr is None:
        process.kill()
        raise RuntimeError("MCP probe could not open subprocess stdio pipes")

    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    stdout_queue: queue.Queue[str] = queue.Queue()

    def read_stdout() -> None:
        for line in process.stdout:
            stdout_lines.append(line)
            stdout_queue.put(line)

    def read_stderr() -> None:
        stderr_lines.extend(process.stderr)

    stdout_thread = threading.Thread(
        target=read_stdout, name="mcp-probe-stdout", daemon=True
    )
    stderr_thread = threading.Thread(
        target=read_stderr, name="mcp-probe-stderr", daemon=True
    )
    stdout_thread.start()
    stderr_thread.start()
    deadline = started + timeout_seconds

    def stderr_tail() -> str:
        return "".join(stderr_lines)[-1000:]

    def send(payload: dict) -> None:
        process.stdin.write(json.dumps(payload, separators=(",", ":")) + "\n")
        process.stdin.flush()

    def wait_for_response(request_id: int) -> dict:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise RuntimeError(
                    f"MCP request {request_id} timed out after {timeout_seconds:.1f}s: "
                    f"{stderr_tail()}"
                )
            try:
                line = stdout_queue.get(timeout=min(remaining, 0.1))
            except queue.Empty:
                if process.poll() is not None:
                    stdout_thread.join(timeout=0.2)
                    if stdout_queue.empty():
                        raise RuntimeError(
                            f"MCP process exited with {process.returncode} before response "
                            f"{request_id}: {stderr_tail()}"
                        )
                continue

            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"MCP process wrote non-JSON data to stdout: {line!r}"
                ) from exc
            if isinstance(payload, dict) and payload.get("id") == request_id:
                return payload

    messages = build_mcp_probe_messages()
    try:
        send(messages[0])
        wait_for_response(1)
        send(messages[1])
        send(messages[2])
        wait_for_response(2)
        process.stdin.close()

        remaining = max(0.1, deadline - time.monotonic())
        try:
            returncode = process.wait(timeout=remaining)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"MCP process did not exit after stdin closed within {timeout_seconds:.1f}s: "
                f"{stderr_tail()}"
            ) from exc

        stdout_thread.join(timeout=1)
        stderr_thread.join(timeout=1)
        if returncode != 0:
            raise RuntimeError(f"MCP process exited with {returncode}: {stderr_tail()}")

        return {
            "stdout": "".join(stdout_lines),
            "stderr": "".join(stderr_lines),
            "returncode": returncode,
            "runtime_seconds": round(time.monotonic() - started, 3),
        }
    finally:
        if not process.stdin.closed:
            try:
                process.stdin.close()
            except OSError:
                pass
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
        stdout_thread.join(timeout=1)
        stderr_thread.join(timeout=1)
        process.stdout.close()
        process.stderr.close()


def parse_mcp_probe_output(
    stdout: str,
    *,
    expected_version: str,
    expected_tool_count: int,
) -> dict:
    payloads: list[dict] = []
    for line in stdout.splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            payloads.append(payload)

    initialize = next((payload for payload in payloads if payload.get("id") == 1), None)
    if not initialize:
        raise RuntimeError(
            "Published MCP runtime did not return an initialize response"
        )
    if "error" in initialize:
        raise RuntimeError(f"Published MCP initialize failed: {initialize['error']}")

    server_info = initialize.get("result", {}).get("serverInfo", {})
    server_version = str(server_info.get("version", ""))
    if server_version != expected_version:
        raise RuntimeError(
            f"Published MCP serverInfo.version {server_version!r}, expected {expected_version!r}"
        )

    tool_response = next(
        (payload for payload in payloads if payload.get("id") == 2), None
    )
    if not tool_response:
        raise RuntimeError("Published MCP runtime did not return a tools/list response")
    if "error" in tool_response:
        raise RuntimeError(f"Published MCP tools/list failed: {tool_response['error']}")

    tools = tool_response.get("result", {}).get("tools")
    if not isinstance(tools, list):
        raise RuntimeError(
            "Published MCP tools/list response did not contain a tools array"
        )
    if len(tools) != expected_tool_count:
        raise RuntimeError(
            f"Published MCP runtime exposed {len(tools)} tools, expected {expected_tool_count}"
        )

    return {
        "server_version": server_version,
        "runtime_tool_count": len(tools),
    }


def probe_installed_mcp_runtime(
    runtime_dir: Path,
    *,
    expected_version: str,
    expected_tool_count: int,
    timeout_seconds: float = 30.0,
) -> dict:
    command = runtime_console_command(runtime_dir)
    if not command.is_file():
        raise RuntimeError(f"Published MCP console entry point is missing: {command}")

    env = os.environ.copy()
    env.pop("GITHUB_TOKEN", None)
    env.pop("GH_TOKEN", None)

    completed = probe_mcp_subprocess(
        [str(command)],
        env=env,
        timeout_seconds=timeout_seconds,
    )

    result = parse_mcp_probe_output(
        completed["stdout"],
        expected_version=expected_version,
        expected_tool_count=expected_tool_count,
    )
    result["runtime_seconds"] = completed["runtime_seconds"]
    return result


def probe_installed_validation_runtime(
    runtime_dir: Path,
    *,
    timeout_seconds: float = 65.0,
) -> dict:
    command = runtime_validation_command(runtime_dir)
    if not command.is_file():
        raise RuntimeError(
            f"Published validation console entry point is missing: {command}"
        )

    env = os.environ.copy()
    env.pop("GITHUB_TOKEN", None)
    env.pop("GH_TOKEN", None)
    completed = subprocess.run(
        [
            str(command),
            "public-artifact-runtime-smoke-gate",
            "--format",
            "json",
        ],
        cwd=runtime_dir,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_seconds,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "Published validation command failed: "
            + (completed.stderr.strip() or completed.stdout.strip())[-2000:]
        )
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Published validation command did not return JSON") from exc
    duration = float(result.get("duration_seconds", 0))
    submission_url = str(result.get("submission_url", ""))
    if result.get("passed") is not True or not 0 < duration < 60:
        raise RuntimeError(
            f"Published validation contract failed or exceeded 60 seconds: {result}"
        )
    if (
        "template=validate-skill.yml" not in submission_url
        or "generated_validation_evidence=" not in submission_url
    ):
        raise RuntimeError(
            "Published validation command lacks a prefilled evidence URL"
        )
    return {
        "validation_seconds": duration,
        "validation_submission_url": submission_url,
    }


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
    validation_cli_path = package_root / "validation_cli.py"
    validation_kit_path = (
        package_root / "validation_kits" / "public_artifact_runtime_smoke_gate.py"
    )
    entry_points_path = (
        target_dir / f"noosphere_mcp-{expected_version}.dist-info" / "entry_points.txt"
    )
    required_paths = [
        init_path,
        mcp_path,
        query_cli_path,
        validation_cli_path,
        validation_kit_path,
        entry_points_path,
    ]
    missing_paths = [
        path.relative_to(target_dir).as_posix()
        for path in required_paths
        if not path.exists()
    ]
    if missing_paths:
        raise RuntimeError(
            "Installed package is missing required release files: "
            + ", ".join(missing_paths)
        )

    init_source = init_path.read_text(encoding="utf-8")
    mcp_source = mcp_path.read_text(encoding="utf-8")
    entry_points = entry_points_path.read_text(encoding="utf-8")

    version_match = re.search(r'__version__\s*=\s*"([^"]+)"', init_source)
    installed_version = version_match.group(1) if version_match else ""
    if installed_version != expected_version:
        raise RuntimeError(
            f"Installed package version {installed_version!r}, expected {expected_version!r}"
        )

    tool_names = re.findall(
        r"@mcp\.tool\(\)\s*(?:\n[^\n]*)*?\n(?:async\s+def|def)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        mcp_source,
    )
    if len(tool_names) != expected_tool_count:
        raise RuntimeError(
            f"Installed MCP tool count {len(tool_names)}, expected {expected_tool_count}"
        )

    missing_tools = [
        tool_name for tool_name in REQUIRED_GROWTH_TOOLS if tool_name not in tool_names
    ]
    if missing_tools:
        raise RuntimeError(
            f"Installed package is missing growth tool(s): {', '.join(missing_tools)}"
        )

    required_entry_points = {
        "noosphere-mcp = noosphere.server:main",
        "noosphere-query = noosphere.query_cli:main",
        "noosphere-validate = noosphere.validation_cli:main",
    }
    missing_entry_points = sorted(
        entry_point
        for entry_point in required_entry_points
        if entry_point not in entry_points
    )
    if missing_entry_points:
        raise RuntimeError(
            "Installed package is missing console entry point(s): "
            + ", ".join(missing_entry_points)
        )

    return {
        "version": installed_version,
        "tool_count": len(tool_names),
        "growth_tools": REQUIRED_GROWTH_TOOLS,
        "query_cli": "noosphere-query",
        "validation_cli": "noosphere-validate",
    }


def verify_pypi_release(
    project: str,
    version: str,
    attempts: int,
    delay_seconds: float,
    expected_tool_count: int,
) -> dict:
    release_json = wait_for_pypi_release(project, version, attempts, delay_seconds)
    filenames = validate_release_json(release_json, version)
    project_json = wait_for_pypi_project_latest(
        project, version, attempts, delay_seconds
    )
    latest_filenames = validate_release_json(project_json, version)

    temp_dir = Path(tempfile.mkdtemp(prefix="noosphere-pypi-verify-"))
    try:
        inspect_dir = temp_dir / "inspect"
        wait_for_installable_release(
            project, version, inspect_dir, attempts, delay_seconds
        )
        installed = inspect_installed_release(
            inspect_dir, version, expected_tool_count=expected_tool_count
        )

        runtime_dir = temp_dir / "runtime"
        install_runtime_environment(project, version, runtime_dir)
        runtime = probe_installed_mcp_runtime(
            runtime_dir,
            expected_version=version,
            expected_tool_count=expected_tool_count,
        )
        validation = probe_installed_validation_runtime(runtime_dir)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        "project": project,
        "version": version,
        "files": filenames,
        "latest_files": latest_filenames,
        **installed,
        **runtime,
        **validation,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify a published noosphere-mcp PyPI release."
    )
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--version", default=read_project_version())
    parser.add_argument("--attempts", type=int, default=24)
    parser.add_argument("--delay-seconds", type=float, default=10.0)
    parser.add_argument("--tool-count", type=int, default=45)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = verify_pypi_release(
        args.project, args.version, args.attempts, args.delay_seconds, args.tool_count
    )
    print(
        f"Verified {result['project']}=={result['version']}: "
        f"{result['runtime_tool_count']} MCP tools via initialize + tools/list in "
        f"{result['runtime_seconds']:.3f}s; growth ledger tools, noosphere-query and "
        f"the token-free validation path passed in {result['validation_seconds']:.2f}s."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
