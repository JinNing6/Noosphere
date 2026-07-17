import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
QUERY_COMMAND = "uvx --from noosphere-mcp noosphere-query"


class LaunchSurfaceTests(unittest.TestCase):
    def test_registry_count_matches_the_honest_first_screen_claim(self):
        registry = json.loads(
            (REPO_ROOT / "shared_skills" / "registry.json").read_text(encoding="utf-8")
        )
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertEqual(len(registry["skills"]), 14)
        self.assertIn("Live_Skills-14", readme)
        self.assertIn("docs/live-skills.md", readme)
        self.assertIn("maintainer-validated Live Skills", readme)
        self.assertIn("public-artifact-runtime-smoke-gate", readme)
        for skill in registry["skills"]:
            release = next(
                item
                for item in skill["releases"]
                if item["version"] == skill["latest"] and item["status"] == "active"
            )
            self.assertEqual(release["verification"]["level"], "maintainer-validated")

    def test_english_and_chinese_first_screens_lead_with_the_query_not_the_3d_app(self):
        for name in ("README.md", "README.zh-CN.md"):
            readme = (REPO_ROOT / name).read_text(encoding="utf-8")
            first_screen = "\n".join(readme.splitlines()[:80])

            self.assertIn(QUERY_COMMAND, first_screen)
            self.assertIn("assets/demo/agent-debug-memory.gif", first_screen)
            self.assertIn("shared_skills/active/", first_screen)
            self.assertLess(
                readme.index(QUERY_COMMAND),
                readme.index("assets/splash_cinematic.webp"),
            )

    def test_demo_assets_and_reproducible_source_exist(self):
        gif = REPO_ROOT / "assets" / "demo" / "agent-debug-memory.gif"
        mp4 = REPO_ROOT / "assets" / "demo" / "agent-debug-memory.mp4"

        self.assertGreater(gif.stat().st_size, 50_000)
        self.assertGreater(mp4.stat().st_size, 50_000)
        self.assertTrue((REPO_ROOT / "docs" / "demo-script-20s.md").is_file())
        self.assertTrue((REPO_ROOT / "scripts" / "render-launch-demo.ps1").is_file())

    def test_glama_has_a_deterministic_anonymous_source_container(self):
        dockerfile = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
        dockerignore = (REPO_ROOT / ".dockerignore").read_text(encoding="utf-8")
        smithery = (REPO_ROOT / "smithery.yaml").read_text(encoding="utf-8")
        registry_manifests = [
            json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))
            for path in ("server.json", "sdk/server.json")
        ]

        self.assertIn("COPY sdk/pyproject.toml ./sdk/pyproject.toml", dockerfile)
        self.assertIn("COPY sdk/noosphere ./sdk/noosphere", dockerfile)
        self.assertIn(
            "python -m pip install --disable-pip-version-check --no-cache-dir ./sdk",
            dockerfile,
        )
        self.assertIn("USER noosphere", dockerfile)
        self.assertIn('CMD ["noosphere-mcp"]', dockerfile)
        self.assertIn("!sdk/noosphere/**", dockerignore)
        self.assertNotIn("required:\n      - githubToken", smithery)
        self.assertIn(
            "config.githubToken ? { GITHUB_TOKEN: config.githubToken } : {}", smithery
        )
        for manifest in registry_manifests:
            environment = {
                item["name"]: item
                for item in manifest["packages"][0]["environmentVariables"]
            }
            self.assertFalse(environment["GITHUB_TOKEN"]["isRequired"])
            self.assertFalse(environment["NOOSPHERE_REPO"]["isRequired"])


if __name__ == "__main__":
    unittest.main()
