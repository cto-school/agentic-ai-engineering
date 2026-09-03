"""Safe, deterministic tools for the first teaching project."""

from __future__ import annotations

import ast
import operator
from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel, Field, ValidationError

from .schemas import ToolDefinition, ToolResult


class CalculatorArguments(BaseModel):
    expression: str = Field(min_length=1, max_length=100)


class SearchArguments(BaseModel):
    query: str = Field(min_length=2, max_length=200)


_BINARY_OPERATORS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _evaluate_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _evaluate_node(node.left)
        right = _evaluate_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 10:
            raise ValueError("Exponent is limited to 10")
        return _BINARY_OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_evaluate_node(node.operand))
    raise ValueError("Only basic arithmetic is allowed")


def calculate(expression: str) -> str:
    """Evaluate basic arithmetic without using eval()."""

    tree = ast.parse(expression, mode="eval")
    result = _evaluate_node(tree.body)
    return str(int(result)) if result.is_integer() else str(result)


_LOCAL_RESEARCH = {
    "python": (
        "Python is a high-level programming language known for readable syntax. "
        "Its standard library and package ecosystem make it common in AI engineering."
    ),
    "agent": (
        "In this course, an agent is an application that uses a model to choose "
        "actions, execute tools through host code, observe results, and decide when to stop."
    ),
    "tool": (
        "A tool is a schema-described capability. The model requests the capability; "
        "the host application validates the arguments and executes the underlying function."
    ),
    "structured output": (
        "Structured output gives model responses a predictable shape that application "
        "code can validate and consume."
    ),
}


def search_local_notes(query: str) -> str:
    """Search a tiny deterministic course dataset."""

    terms = query.lower().split()
    matches = [text for key, text in _LOCAL_RESEARCH.items() if key in query.lower()]
    if not matches:
        matches = [
            text
            for key, text in _LOCAL_RESEARCH.items()
            if any(term in key or term in text.lower() for term in terms)
        ]
    return "\n".join(matches) if matches else "No matching note was found."


@dataclass(frozen=True)
class Tool:
    definition: ToolDefinition
    argument_model: type[BaseModel]
    function: Callable[..., str]

    def execute(self, call_id: str, arguments: dict[str, Any]) -> ToolResult:
        try:
            validated = self.argument_model.model_validate(arguments)
            output = self.function(**validated.model_dump())
            return ToolResult(name=self.definition.name, call_id=call_id, output=output)
        except (ValidationError, ValueError, SyntaxError, ZeroDivisionError) as exc:
            return ToolResult(
                name=self.definition.name,
                call_id=call_id,
                output=f"Tool error: {exc}",
                is_error=True,
            )


def default_tool_registry() -> dict[str, Tool]:
    return {
        "calculator": Tool(
            definition=ToolDefinition(
                name="calculator",
                description="Evaluate basic arithmetic. Use it instead of doing arithmetic mentally.",
                parameters={
                    "type": "object",
                    "properties": {"expression": {"type": "string"}},
                    "required": ["expression"],
                    "additionalProperties": False,
                },
            ),
            argument_model=CalculatorArguments,
            function=calculate,
        ),
        "search_local_notes": Tool(
            definition=ToolDefinition(
                name="search_local_notes",
                description="Search the small local course-note collection for factual background.",
                parameters={
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                    "additionalProperties": False,
                },
            ),
            argument_model=SearchArguments,
            function=search_local_notes,
        ),
    }

