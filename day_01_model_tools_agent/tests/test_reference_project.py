from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from research_agent.agent import AgentRunner
from research_agent.providers import MockModelProvider
from research_agent.tools import calculate, default_tool_registry


class CalculatorTests(unittest.TestCase):
    def test_basic_arithmetic(self):
        self.assertEqual(calculate("12 * 7"), "84")

    def test_rejects_python_code(self):
        with self.assertRaises((ValueError, SyntaxError)):
            calculate("__import__('os').getcwd()")


class AgentTests(unittest.TestCase):
    def test_direct_response(self):
        result = AgentRunner(MockModelProvider(), default_tool_registry()).run("Say hello")
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.response.tools_used, [])

    def test_uses_two_tools_and_finishes(self):
        result = AgentRunner(MockModelProvider(), default_tool_registry()).run(
            "Explain an AI agent and calculate 12 * 7"
        )
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.response.tools_used, ["calculator", "search_local_notes"])
        self.assertIn("84", result.response.summary)


if __name__ == "__main__":
    unittest.main()

