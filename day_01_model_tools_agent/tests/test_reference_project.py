from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from research_agent.agent import AgentRunner
from research_agent.providers import MockModelProvider
from research_agent.schemas import Message, ModelTurn, ToolCall, ToolDefinition
from research_agent.tools import Tool, calculate, default_tool_registry

from pydantic import BaseModel


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


class RepeatingProvider:
    """Always asks for the same tool with the same arguments.

    Every request carries a NEW call id, exactly like a real provider. The runner
    must still recognise the repetition, otherwise a stuck model would burn the
    whole step budget.
    """

    def __init__(self):
        self.calls = 0

    def complete(self, messages: list[Message], tools: list[ToolDefinition]) -> ModelTurn:
        self.calls += 1
        return ModelTurn(
            tool_calls=[
                ToolCall(
                    id=f"call-{self.calls}",
                    name="calculator",
                    arguments={"expression": "2 + 2"},
                )
            ]
        )


class ReorderedArgumentsProvider(RepeatingProvider):
    """Same two arguments, written in a different order the second time."""

    def complete(self, messages: list[Message], tools: list[ToolDefinition]) -> ModelTurn:
        self.calls += 1
        arguments = {"a": 1, "b": 2} if self.calls == 1 else {"b": 2, "a": 1}
        return ModelTurn(
            tool_calls=[ToolCall(id=f"call-{self.calls}", name="adder", arguments=arguments)]
        )


class AdderArguments(BaseModel):
    a: int
    b: int


def adder_registry() -> dict[str, Tool]:
    return {
        "adder": Tool(
            definition=ToolDefinition(
                name="adder",
                description="Add two whole numbers.",
                parameters={
                    "type": "object",
                    "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                    "required": ["a", "b"],
                    "additionalProperties": False,
                },
            ),
            argument_model=AdderArguments,
            function=lambda a, b: str(a + b),
        )
    }


class DuplicateCallTests(unittest.TestCase):
    def test_repeated_tool_request_is_stopped(self):
        provider = RepeatingProvider()
        result = AgentRunner(provider, default_tool_registry(), max_steps=5).run("Calculate 2 + 2")
        self.assertEqual(result.status, "failed")
        self.assertIn("Duplicate tool request stopped", result.error or "")
        # Stopped on the second model turn, not after exhausting max_steps.
        self.assertEqual(result.steps, 2)
        self.assertEqual(provider.calls, 2)

    def test_signature_ignores_call_id_and_argument_order(self):
        # Regression guard: the signature must not contain call.id (every request gets
        # a new one) and must not depend on the order the model wrote the keys in.
        provider = ReorderedArgumentsProvider()
        result = AgentRunner(provider, adder_registry(), max_steps=5).run("Add 1 and 2")
        self.assertEqual(result.status, "failed")
        self.assertIn("Duplicate tool request stopped: adder", result.error or "")


class ToolValidationTests(unittest.TestCase):
    def test_invalid_argument_returns_a_tool_error_instead_of_raising(self):
        tool = default_tool_registry()["calculator"]
        result = tool.execute("call-1", {"expression": ""})
        self.assertTrue(result.is_error)
        self.assertIn("Tool error", result.output)

    def test_dangerous_expression_is_refused(self):
        tool = default_tool_registry()["calculator"]
        result = tool.execute("call-2", {"expression": "__import__('os').getcwd()"})
        self.assertTrue(result.is_error)


if __name__ == "__main__":
    unittest.main()

