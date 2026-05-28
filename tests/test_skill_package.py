import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SelfImprovementSkillPackageTests(unittest.TestCase):
    def test_required_files_exist(self):
        expected = [
            "SKILL.md",
            "README.md",
            "agents/openai.yaml",
            "assets/self-improvement-flow.svg",
            "assets/self-improvement-hero.png",
            "references/audit-method.md",
            "references/operating-rules.md",
            "scripts/extract_conversation_cards.py",
            "scripts/install_skill.py",
        ]
        for relpath in expected:
            self.assertTrue((ROOT / relpath).exists(), relpath)

    def test_skill_frontmatter_is_installable(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        self.assertIn("name: self-improvement", text)
        self.assertRegex(text, r"description: Use when .+conversation")
        self.assertIn("subagents", text.lower())
        self.assertLess(len(text.split()), 1200)

    def test_readme_marketing_and_install_paths(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("assets/self-improvement-flow.svg", text)
        self.assertIn("subagent", text.lower())
        self.assertIn("GPT-5.3-Codex-Spark", text)
        self.assertIn("Codex", text)
        self.assertIn("Claude", text)
        self.assertIn("install_skill.py", text)

    def test_workflow_diagram_shows_core_advantage(self):
        text = (ROOT / "assets" / "self-improvement-flow.svg").read_text(encoding="utf-8")
        self.assertIn("Conversation history", text)
        self.assertIn("GPT-5.3-", text)
        self.assertIn("Codex-Spark", text)
        self.assertIn("Evidence ledger", text)

    def test_installer_dry_run_mentions_all_agent_targets(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "install_skill.py"), "--dry-run"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(".codex/skills/self-improvement", result.stdout)
        self.assertIn(".claude/skills/self-improvement", result.stdout)
        self.assertIn(".agents/skills/self-improvement", result.stdout)

    def test_extract_conversation_cards_has_help(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "extract_conversation_cards.py"), "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--codex-root", result.stdout)
        self.assertIn("--claude-root", result.stdout)


if __name__ == "__main__":
    unittest.main()
