import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.verify_pypi_release import (
    REQUIRED_GROWTH_TOOLS,
    inspect_installed_release,
    install_release_to_target,
    validate_release_json,
    verify_pypi_release,
)


def _tool_source(tool_names: list[str]) -> str:
    blocks = []
    for tool_name in tool_names:
        blocks.append(f"@mcp.tool()\nasync def {tool_name}():\n    return 'ok'\n")
    return "\n".join(blocks)


class VerifyPypiReleaseTests(unittest.TestCase):
    def test_validate_release_json_requires_matching_version_and_artifacts(self):
        data = {
            "info": {"version": "0.6.3"},
            "urls": [
                {"filename": "noosphere_mcp-0.6.3-py3-none-any.whl"},
                {"filename": "noosphere_mcp-0.6.3.tar.gz"},
            ],
        }

        filenames = validate_release_json(data, "0.6.3")

        self.assertEqual(
            filenames,
            ["noosphere_mcp-0.6.3-py3-none-any.whl", "noosphere_mcp-0.6.3.tar.gz"],
        )

    def test_validate_release_json_rejects_missing_wheel(self):
        data = {
            "info": {"version": "0.6.3"},
            "urls": [{"filename": "noosphere_mcp-0.6.3.tar.gz"}],
        }

        with self.assertRaisesRegex(RuntimeError, "missing distribution"):
            validate_release_json(data, "0.6.3")

    def test_inspect_installed_release_requires_version_tool_count_and_growth_tools(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            package_root = target / "noosphere"
            package_root.mkdir()
            (package_root / "__init__.py").write_text('__version__ = "0.6.3"\n', encoding="utf-8")
            tool_names = [f"tool_{index}" for index in range(35)] + REQUIRED_GROWTH_TOOLS
            (package_root / "noosphere_mcp.py").write_text(_tool_source(tool_names), encoding="utf-8")

            result = inspect_installed_release(target, "0.6.3", expected_tool_count=40)

        self.assertEqual(result["version"], "0.6.3")
        self.assertEqual(result["tool_count"], 40)

    def test_install_release_to_target_uses_exact_version_and_no_deps(self):
        with patch("scripts.verify_pypi_release.subprocess.run") as run:
            install_release_to_target("noosphere-mcp", "0.6.3", Path("target"), python_executable="python")

        command = run.call_args.args[0]
        self.assertIn("--no-deps", command)
        self.assertIn("--target", command)
        self.assertIn("noosphere-mcp==0.6.3", command)
        run.assert_called_once_with(command, check=True)

    def test_verify_pypi_release_waits_installs_and_inspects(self):
        release_json = {
            "info": {"version": "0.6.3"},
            "urls": [
                {"filename": "noosphere_mcp-0.6.3-py3-none-any.whl"},
                {"filename": "noosphere_mcp-0.6.3.tar.gz"},
            ],
        }
        installed = {"version": "0.6.3", "tool_count": 40, "growth_tools": REQUIRED_GROWTH_TOOLS}

        with (
            patch("scripts.verify_pypi_release.wait_for_pypi_release", return_value=release_json) as wait,
            patch("scripts.verify_pypi_release.install_release_to_target") as install,
            patch("scripts.verify_pypi_release.inspect_installed_release", return_value=installed) as inspect,
        ):
            result = verify_pypi_release("noosphere-mcp", "0.6.3", attempts=1, delay_seconds=0, expected_tool_count=40)

        wait.assert_called_once_with("noosphere-mcp", "0.6.3", 1, 0)
        install.assert_called_once()
        inspect.assert_called_once()
        self.assertEqual(result["version"], "0.6.3")
        self.assertEqual(result["tool_count"], 40)


if __name__ == "__main__":
    unittest.main()
