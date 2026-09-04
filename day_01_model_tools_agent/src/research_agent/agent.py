"""A manual, bounded model -> tool -> observation agent loop."""

from __future__ import annotations

import json

from pydantic import ValidationError

from .providers import ModelProvider
from .schemas import AgentResult, Message, ResearchResponse, UsageRecord
from .tools import Tool


SYSTEM_MESSAGE = """You are a small teaching research assistant.
Use tools when they are useful. The application, not you, executes them.
When finished, respond with only valid JSON matching this shape:
{
  "topic": "string",
  "summary": "string",
  "key_points": ["string"],
  "tools_used": ["string"],
  "confidence": 0.0
}
Confidence must be between 0 and 1.
"""


class AgentRunner:
    def __init__(
        self,
        provider: ModelProvider,
        tools: dict[str, Tool],
        max_steps: int = 5,
    ):
        if max_steps < 1:
            raise ValueError("max_steps must be at least 1")
        self.provider = provider
        self.tools = tools
        self.max_steps = max_steps

    def run(self, question: str) -> AgentResult:
        messages = [
            Message(role="system", content=SYSTEM_MESSAGE),
            Message(role="user", content=question),
        ]
        seen_calls: set[tuple[str, str]] = set()
        usage = UsageRecord()

        for step in range(1, self.max_steps + 1):
            try:
                turn = self.provider.complete(
                    messages,
                    [tool.definition for tool in self.tools.values()],
                )
            except Exception as exc:
                return AgentResult(
                    status="failed", messages=messages, steps=step, usage=usage, error=str(exc)
                )

            usage = usage.add(turn.usage)

            assistant_message = Message(
                role="assistant",
                content=turn.content,
                tool_calls=turn.tool_calls,
                reasoning_details=turn.reasoning_details,
            )
            messages.append(assistant_message)

            if not turn.tool_calls:
                try:
                    response = ResearchResponse.model_validate_json(turn.content)
                except ValidationError as exc:
                    return AgentResult(
                        status="failed",
                        messages=messages,
                        steps=step,
                        usage=usage,
                        error=f"Final response failed validation: {exc}",
                    )
                return AgentResult(
                    status="completed", response=response, messages=messages, steps=step, usage=usage
                )

            for call in turn.tool_calls:
                # The signature must describe WHAT was requested, not WHICH request
                # object carried it. Providers give every tool call a fresh random id,
                # so including call.id here would make each signature unique and the
                # duplicate check could never fire. Sorting the argument keys makes
                # {"a": 1, "b": 2} and {"b": 2, "a": 1} the same signature.
                signature = (call.name, json.dumps(call.arguments, sort_keys=True))
                if signature in seen_calls:
                    return AgentResult(
                        status="failed",
                        messages=messages,
                        steps=step,
                        usage=usage,
                        error=f"Duplicate tool request stopped: {call.name}",
                    )
                seen_calls.add(signature)

                tool = self.tools.get(call.name)
                if tool is None:
                    output = f"Tool error: unknown tool '{call.name}'"
                else:
                    result = tool.execute(call.id, call.arguments)
                    output = result.output

                messages.append(
                    Message(
                        role="tool",
                        name=call.name,
                        tool_call_id=call.id,
                        content=output,
                    )
                )

        return AgentResult(
            status="max_steps",
            messages=messages,
            steps=self.max_steps,
            usage=usage,
            error=f"Agent stopped after {self.max_steps} steps",
        )
