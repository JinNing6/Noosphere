import ast
import json
import struct
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
QUERY_COMMAND = "uvx --from noosphere-mcp noosphere-query"
CODEX_INSTALL = "codex plugin marketplace add JinNing6/Noosphere"
CLAUDE_INSTALL = "/plugin marketplace add JinNing6/Noosphere"


class LaunchSurfaceTests(unittest.TestCase):
    def test_first_screen_projects_a_dynamic_registry_without_count_drift(self):
        registry = json.loads(
            (REPO_ROOT / "shared_skills" / "registry.json").read_text(encoding="utf-8")
        )
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertGreaterEqual(len(registry["skills"]), 14)
        self.assertIn("Live_Skills-live", readme)
        self.assertIn("Registry-dynamic", readme)
        self.assertNotRegex(readme, r"Live_Skills-\d+")
        self.assertIn("docs/live-skills.md", readme)
        self.assertIn("Live Skills", readme)
        self.assertIn("maintainer-validated", readme)
        self.assertIn("public-artifact-runtime-smoke-gate", readme)
        for skill in registry["skills"]:
            release = next(
                item
                for item in skill["releases"]
                if item["version"] == skill["latest"] and item["status"] == "active"
            )
            self.assertIn(
                release["verification"]["level"],
                {
                    "maintainer-validated",
                    "independently-reproduced",
                    "outcome-proven",
                    "established",
                },
            )

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

    def test_readmes_define_the_focused_profile_without_tool_count_drift(self):
        english = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (REPO_ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        extended = (REPO_ROOT / "docs" / "README_full.md").read_text(encoding="utf-8")

        self.assertIn("The default Agent plugin surface is six MCP tools", english)
        self.assertIn("Agent 插件默认只有 6 个 MCP 工具", chinese)
        self.assertIn("Live Skills — Agent plugin default | **6**", english)
        self.assertIn("Live Skills——Agent 插件默认 | **6**", chinese)
        self.assertIn("Full compatibility | **46**", extended)

        for readme in (english, chinese, extended):
            self.assertNotIn("46 MCP tools are instantly available", readme)
            self.assertNotIn("核心工具（当前共 46 个 MCP 工具）", readme)
            self.assertNotIn("## 📋 34 MCP Tools", readme)

    def test_extended_reference_matches_authoritative_profile_membership(self):
        source = (REPO_ROOT / "sdk" / "noosphere" / "mcp_profiles.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(source)
        expected_names = {
            "SKILLS_TOOL_NAMES",
            "CONSCIOUSNESS_TOOL_NAMES",
            "OPS_TOOL_NAMES",
        }
        profiles = {}
        for node in tree.body:
            if not isinstance(node, ast.AnnAssign) or not isinstance(node.target, ast.Name):
                continue
            name = node.target.id
            if name not in expected_names or not isinstance(node.value, ast.Call):
                continue
            profiles[name] = set(ast.literal_eval(node.value.args[0]))

        self.assertEqual(set(profiles), expected_names)
        self.assertEqual(len(profiles["SKILLS_TOOL_NAMES"]), 6)
        self.assertEqual(len(profiles["CONSCIOUSNESS_TOOL_NAMES"]), 35)
        self.assertEqual(len(profiles["OPS_TOOL_NAMES"]), 5)
        self.assertEqual(len(set().union(*profiles.values())), 46)

        extended = (REPO_ROOT / "docs" / "README_full.md").read_text(encoding="utf-8")
        skills_section = extended.split("### Live Skills profile", 1)[1].split(
            "### Consciousness and social profile", 1
        )[0]
        consciousness_section = extended.split(
            "### Consciousness and social profile", 1
        )[1].split("### Maintainer and operations profile", 1)[0]
        ops_section = extended.split("### Maintainer and operations profile", 1)[1].split(
            "### Full compatibility profile", 1
        )[0]

        for tool_name in profiles["SKILLS_TOOL_NAMES"]:
            self.assertIn(f"`{tool_name}`", skills_section)
        for tool_name in profiles["CONSCIOUSNESS_TOOL_NAMES"]:
            self.assertIn(f"`{tool_name}`", consciousness_section)
        for tool_name in profiles["OPS_TOOL_NAMES"]:
            self.assertIn(f"`{tool_name}`", ops_section)

    def test_readmes_route_engineering_evidence_away_from_consciousness(self):
        for name in ("README.md", "README.zh-CN.md", "docs/README_full.md"):
            readme = (REPO_ROOT / name).read_text(encoding="utf-8")
            self.assertIn("template=skill-proposal.yml", readme)
            self.assertIn("template=validate-skill.yml", readme)
            self.assertIn("template=consciousness-upload.yml", readme)

        english = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("not engineering Skill authority", english)
        self.assertIn("only a reviewed immutable registry release is callable", english)

    def test_readmes_expose_the_read_only_sidebar_doctor_and_dedicated_intake(self):
        english = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (REPO_ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

        for readme in (english, chinese):
            self.assertIn("tools/codex-sidebar-doctor/README.md", readme)
            self.assertIn("Invoke-CodexSidebarDoctor.ps1", readme)
            self.assertIn("-SubmitPublicEvidence", readme)
            self.assertIn("template=codex-sidebar-diagnostic.yml", readme)

    def test_first_distribution_wave_preserves_proof_and_channel_boundaries(self):
        wave = (
            REPO_ROOT
            / "docs"
            / "distribution-waves"
            / "live-skill-proof-20260721.md"
        ).read_text(encoding="utf-8")

        for required in (
            "okflint==0.3.0",
            "okflint==0.3.1",
            "https://github.com/JinNing6/Noosphere/issues/57",
            "https://github.com/TSchonleber/brainctl/pull/170",
            "https://github.com/guardiatechnology/ahrena/pull/376",
            "https://github.com/JinNing6/Noosphere/discussions/61",
            "https://github.com/JinNing6/Noosphere/issues/62",
            "maintainer-validated",
            "Weekly External Verified Reuses",
            "X / LinkedIn",
            "Show HN",
            "Reddit",
            "V2EX",
            "掘金 / DEV",
            "24-hour",
            "72-hour",
        ):
            self.assertIn(required, wave)

        self.assertNotIn("independently validated", wave)
        self.assertNotIn("CI passed", wave)

    def test_glama_has_a_deterministic_anonymous_source_container(self):
        dockerfile = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
        dockerignore = (REPO_ROOT / ".dockerignore").read_text(encoding="utf-8")
        smithery = (REPO_ROOT / "smithery.yaml").read_text(encoding="utf-8")
        registry_manifests = [
            json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))
            for path in ("server.json", "sdk/server.json")
        ]

        self.assertIn("COPY sdk/pyproject.toml ./sdk/pyproject.toml", dockerfile)
        self.assertIn("COPY sdk/README.md ./sdk/README.md", dockerfile)
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
