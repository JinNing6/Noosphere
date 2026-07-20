import json
import struct
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
QUERY_COMMAND = "uvx --from noosphere-mcp==0.9.0 noosphere-query"
CODEX_INSTALL = "codex plugin marketplace add JinNing6/Noosphere"
CLAUDE_INSTALL = "/plugin marketplace add JinNing6/Noosphere"


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

    def test_english_and_chinese_first_screens_lead_with_automatic_agent_install(self):
        for name in ("README.md", "README.zh-CN.md"):
            readme = (REPO_ROOT / name).read_text(encoding="utf-8")
            first_screen = "\n".join(readme.splitlines()[:110])

            self.assertIn(CODEX_INSTALL, first_screen)
            self.assertIn(CLAUDE_INSTALL, first_screen)
            self.assertIn(QUERY_COMMAND, first_screen)
            self.assertIn(
                "assets/launch/noosphere-live-skills-v090-demo.gif",
                first_screen,
            )
            self.assertIn("shared_skills/active/", first_screen)
            self.assertLess(readme.index(CODEX_INSTALL), readme.index(QUERY_COMMAND))
            self.assertLess(
                readme.index(QUERY_COMMAND),
                readme.index("assets/splash_cinematic.webp"),
            )

    def test_demo_assets_and_reproducible_source_exist(self):
        gif = (
            REPO_ROOT
            / "assets"
            / "launch"
            / "noosphere-live-skills-v090-demo.gif"
        )
        mp4 = (
            REPO_ROOT
            / "assets"
            / "launch"
            / "noosphere-live-skills-v090-demo.mp4"
        )
        social = (
            REPO_ROOT
            / "assets"
            / "launch"
            / "noosphere-live-skills-v090-social-preview.png"
        )

        self.assertGreater(gif.stat().st_size, 50_000)
        self.assertGreater(mp4.stat().st_size, 50_000)
        self.assertGreater(social.stat().st_size, 50_000)
        self.assertLess(social.stat().st_size, 1_000_000)
        with social.open("rb") as handle:
            self.assertEqual(handle.read(8), b"\x89PNG\r\n\x1a\n")
            handle.read(8)
            width, height = struct.unpack(">II", handle.read(8))
        self.assertEqual((width, height), (1280, 640))
        self.assertTrue(
            (REPO_ROOT / "docs" / "demo-v090-auto-live-skill.md").is_file()
        )
        self.assertTrue(
            (REPO_ROOT / "scripts" / "render-v090-launch-assets.ps1").is_file()
        )
        self.assertTrue(
            (
                REPO_ROOT
                / "scripts"
                / "launch-assets"
                / "v090-live-skill.html"
            ).is_file()
        )

    def test_first_screen_uses_the_skill_inheritance_promise(self):
        english = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (REPO_ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

        self.assertIn(
            "Install once. One Agent learns. Every Agent inherits the Skill.",
            english,
        )
        self.assertIn(
            "安装一次。一个 Agent 学会，所有 Agent 继承这个 Skill。",
            chinese,
        )
        self.assertNotIn("inherits every verified fix", english[:4000])

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
