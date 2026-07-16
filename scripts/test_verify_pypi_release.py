import tempfile
import unittest
import subprocess
import json
from pathlib import Path
from unittest.mock import ANY, patch

from scripts.verify_pypi_release import (
    REQUIRED_GROWTH_TOOLS,
    build_mcp_probe_input,
    inspect_installed_release,
    install_release_to_target,
    parse_mcp_probe_output,
    probe_installed_mcp_runtime,
    runtime_console_command,
    validate_release_json,
    verify_pypi_release,
    wait_for_installable_release,
    wait_for_pypi_project_latest,
)


def _tool_source(tool_names: list[str]) -> str:
    blocks = []
    for tool_name in tool_names:
        blocks.append(f"@mcp.tool()\nasync def {tool_name}():\n    return 'ok'\n")
    return "\n".join(blocks)


class VerifyPypiReleaseTests(unittest.TestCase):
    def test_validate_release_json_requires_matching_version_and_artifacts(self):
        data = {
            "info": {"version": "0.6.8"},
            "urls": [
                {"filename": "noosphere_mcp-0.6.8-py3-none-any.whl"},
                {"filename": "noosphere_mcp-0.6.8.tar.gz"},
            ],
        }

        filenames = validate_release_json(data, "0.6.8")

        self.assertEqual(
            filenames,
            ["noosphere_mcp-0.6.8-py3-none-any.whl", "noosphere_mcp-0.6.8.tar.gz"],
        )

    def test_validate_release_json_rejects_missing_wheel(self):
        data = {
            "info": {"version": "0.6.8"},
            "urls": [{"filename": "noosphere_mcp-0.6.8.tar.gz"}],
        }

        with self.assertRaisesRegex(RuntimeError, "missing distribution"):
            validate_release_json(data, "0.6.8")

    def test_inspect_installed_release_requires_version_tool_count_and_growth_tools(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            package_root = target / "noosphere"
            package_root.mkdir()
            (package_root / "__init__.py").write_text('__version__ = "0.6.8"\n', encoding="utf-8")
            tool_names = [f"tool_{index}" for index in range(35)] + REQUIRED_GROWTH_TOOLS
            (package_root / "noosphere_mcp.py").write_text(_tool_source(tool_names), encoding="utf-8")
            (package_root / "query_cli.py").write_text("def main(): return 0\n", encoding="utf-8")
            (package_root / "validation_cli.py").write_text("def main(): return 0\n", encoding="utf-8")
            validation_kits = package_root / "validation_kits"
            validation_kits.mkdir()
            (validation_kits / "public_artifact_runtime_smoke_gate.py").write_text(
                "def run_validation(): return True\n", encoding="utf-8"
            )
            dist_info = target / "noosphere_mcp-0.6.8.dist-info"
            dist_info.mkdir()
            (dist_info / "entry_points.txt").write_text(
                "[console_scripts]\n"
                "noosphere-mcp = noosphere.server:main\n"
                "noosphere-query = noosphere.query_cli:main\n"
                "noosphere-validate = noosphere.validation_cli:main\n",
                encoding="utf-8",
            )

            result = inspect_installed_release(target, "0.6.8", expected_tool_count=40)

        self.assertEqual(result["version"], "0.6.8")
        self.assertEqual(result["tool_count"], 40)
        self.assertEqual(result["query_cli"], "noosphere-query")
        self.assertEqual(result["validation_cli"], "noosphere-validate")

    def test_install_release_to_target_uses_exact_version_and_no_deps(self):
        with patch("scripts.verify_pypi_release.subprocess.run") as run:
            install_release_to_target("noosphere-mcp", "0.6.8", Path("target"), python_executable="python")

        command = run.call_args.args[0]
        self.assertIn("--no-deps", command)
        self.assertIn("--target", command)
        self.assertIn("noosphere-mcp==0.6.8", command)
        run.assert_called_once_with(command, check=True)

    def test_runtime_console_command_is_platform_aware(self):
        runtime_dir = Path("runtime")

        with patch("scripts.verify_pypi_release.os.name", "nt"):
            self.assertEqual(
                runtime_console_command(runtime_dir),
                runtime_dir / "Scripts" / "noosphere-mcp.exe",
            )

        with patch("scripts.verify_pypi_release.os.name", "posix"):
            self.assertEqual(
                runtime_console_command(runtime_dir),
                runtime_dir / "bin" / "noosphere-mcp",
            )

    def test_mcp_probe_input_initializes_before_listing_tools(self):
        messages = [json.loads(line) for line in build_mcp_probe_input().splitlines()]

        self.assertEqual(messages[0]["method"], "initialize")
        self.assertEqual(messages[1]["method"], "notifications/initialized")
        self.assertEqual(messages[2]["method"], "tools/list")

    def test_parse_mcp_probe_output_requires_version_and_exact_tool_count(self):
        stdout = "\n".join(
            [
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "result": {
                            "serverInfo": {"name": "noosphere", "version": "0.8.2"},
                        },
                    }
                ),
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "result": {
                            "tools": [{"name": f"tool_{index}"} for index in range(45)],
                        },
                    }
                ),
            ]
        )

        result = parse_mcp_probe_output(stdout, expected_version="0.8.2", expected_tool_count=45)

        self.assertEqual(result["server_version"], "0.8.2")
        self.assertEqual(result["runtime_tool_count"], 45)

    def test_parse_mcp_probe_output_rejects_missing_tool_response(self):
        stdout = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"serverInfo": {"name": "noosphere", "version": "0.8.2"}},
            }
        )

        with self.assertRaisesRegex(RuntimeError, "tools/list"):
            parse_mcp_probe_output(stdout, expected_version="0.8.2", expected_tool_count=45)

    def test_probe_installed_runtime_uses_anonymous_environment_and_timeout(self):
        completed = subprocess.CompletedProcess(
            ["noosphere-mcp"],
            0,
            stdout="\n".join(
                [
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "result": {
                                "serverInfo": {"name": "noosphere", "version": "0.8.2"},
                            },
                        }
                    ),
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": 2,
                            "result": {
                                "tools": [{"name": f"tool_{index}"} for index in range(45)],
                            },
                        }
                    ),
                ]
            ),
            stderr="",
        )

        with tempfile.TemporaryDirectory() as tmp:
            runtime_dir = Path(tmp)
            command = runtime_console_command(runtime_dir)
            command.parent.mkdir(parents=True)
            command.touch()

            with (
                patch("scripts.verify_pypi_release.subprocess.run", return_value=completed) as run,
                patch.dict(
                    "scripts.verify_pypi_release.os.environ",
                    {"GITHUB_TOKEN": "secret", "GH_TOKEN": "secret", "PATH": "test-path"},
                    clear=True,
                ),
            ):
                result = probe_installed_mcp_runtime(
                    runtime_dir,
                    expected_version="0.8.2",
                    expected_tool_count=45,
                    timeout_seconds=30,
                )

        kwargs = run.call_args.kwargs
        self.assertNotIn("GITHUB_TOKEN", kwargs["env"])
        self.assertNotIn("GH_TOKEN", kwargs["env"])
        self.assertEqual(kwargs["timeout"], 30)
        self.assertEqual(result["runtime_tool_count"], 45)

    def test_wait_for_pypi_project_latest_requires_latest_version(self):
        stale_json = {
            "info": {"version": "0.6.4"},
            "urls": [
                {"filename": "noosphere_mcp-0.6.4-py3-none-any.whl"},
                {"filename": "noosphere_mcp-0.6.4.tar.gz"},
            ],
        }
        current_json = {
            "info": {"version": "0.6.8"},
            "urls": [
                {"filename": "noosphere_mcp-0.6.8-py3-none-any.whl"},
                {"filename": "noosphere_mcp-0.6.8.tar.gz"},
            ],
        }

        with (
            patch("scripts.verify_pypi_release.fetch_json", side_effect=[stale_json, current_json]) as fetch,
            patch("scripts.verify_pypi_release.time.sleep") as sleep,
        ):
            result = wait_for_pypi_project_latest("noosphere-mcp", "0.6.8", attempts=2, delay_seconds=0)

        self.assertEqual(result["info"]["version"], "0.6.8")
        self.assertEqual(fetch.call_count, 2)
        sleep.assert_called_once_with(0)

    def test_wait_for_installable_release_retries_pip_index_lag(self):
        with (
            patch(
                "scripts.verify_pypi_release.install_release_to_target",
                side_effect=[subprocess.CalledProcessError(1, ["pip"]), None],
            ) as install,
            patch("scripts.verify_pypi_release.time.sleep") as sleep,
        ):
            wait_for_installable_release("noosphere-mcp", "0.6.8", Path("target"), attempts=2, delay_seconds=0)

        self.assertEqual(install.call_count, 2)
        sleep.assert_called_once_with(0)

    def test_verify_pypi_release_waits_installs_and_inspects(self):
        release_json = {
            "info": {"version": "0.6.8"},
            "urls": [
                {"filename": "noosphere_mcp-0.6.8-py3-none-any.whl"},
                {"filename": "noosphere_mcp-0.6.8.tar.gz"},
            ],
        }
        installed = {"version": "0.6.8", "tool_count": 40, "growth_tools": REQUIRED_GROWTH_TOOLS}
        runtime = {"server_version": "0.6.8", "runtime_tool_count": 40, "runtime_seconds": 1.5}

        with (
            patch("scripts.verify_pypi_release.wait_for_pypi_release", return_value=release_json) as wait,
            patch("scripts.verify_pypi_release.wait_for_pypi_project_latest", return_value=release_json) as wait_latest,
            patch("scripts.verify_pypi_release.wait_for_installable_release") as install,
            patch("scripts.verify_pypi_release.inspect_installed_release", return_value=installed) as inspect,
            patch("scripts.verify_pypi_release.install_runtime_environment") as install_runtime,
            patch("scripts.verify_pypi_release.probe_installed_mcp_runtime", return_value=runtime) as probe_runtime,
        ):
            result = verify_pypi_release("noosphere-mcp", "0.6.8", attempts=1, delay_seconds=0, expected_tool_count=40)

        wait.assert_called_once_with("noosphere-mcp", "0.6.8", 1, 0)
        wait_latest.assert_called_once_with("noosphere-mcp", "0.6.8", 1, 0)
        install.assert_called_once_with("noosphere-mcp", "0.6.8", ANY, 1, 0)
        inspect.assert_called_once()
        install_runtime.assert_called_once()
        probe_runtime.assert_called_once()
        self.assertEqual(result["version"], "0.6.8")
        self.assertEqual(result["tool_count"], 40)
        self.assertEqual(result["runtime_tool_count"], 40)
        self.assertEqual(result["latest_files"], result["files"])


if __name__ == "__main__":
    unittest.main()
