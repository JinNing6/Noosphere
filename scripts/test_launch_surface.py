import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
QUERY_COMMAND = 'uvx --from noosphere-mcp noosphere-query'


class LaunchSurfaceTests(unittest.TestCase):
    def test_registry_count_matches_the_honest_first_screen_claim(self):
        registry = json.loads(
            (REPO_ROOT / "shared_skills" / "registry.json").read_text(encoding="utf-8")
        )
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertEqual(registry["skills"], [])
        self.assertIn("Published_Skills-0", readme)
        self.assertIn("Bundled_Skills-13", readme)
        self.assertIn("docs/bundled-skills.md", readme)
        self.assertIn("3 verified seeds and\n0 published dynamic Skills", readme)

    def test_english_and_chinese_first_screens_lead_with_the_query_not_the_3d_app(self):
        for name in ("README.md", "README.zh-CN.md"):
            readme = (REPO_ROOT / name).read_text(encoding="utf-8")
            first_screen = "\n".join(readme.splitlines()[:80])

            self.assertIn(QUERY_COMMAND, first_screen)
            self.assertIn("assets/demo/agent-debug-memory.gif", first_screen)
            self.assertIn("plugins/noosphere/skills/", first_screen)
            self.assertLess(readme.index(QUERY_COMMAND), readme.index("assets/splash_cinematic.webp"))

    def test_demo_assets_and_reproducible_source_exist(self):
        gif = REPO_ROOT / "assets" / "demo" / "agent-debug-memory.gif"
        mp4 = REPO_ROOT / "assets" / "demo" / "agent-debug-memory.mp4"

        self.assertGreater(gif.stat().st_size, 50_000)
        self.assertGreater(mp4.stat().st_size, 50_000)
        self.assertTrue((REPO_ROOT / "docs" / "demo-script-20s.md").is_file())
        self.assertTrue((REPO_ROOT / "scripts" / "render-launch-demo.ps1").is_file())


if __name__ == "__main__":
    unittest.main()
