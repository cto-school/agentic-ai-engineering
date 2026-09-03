"""Model routes for mock, Ollama, and optional OpenRouter operation."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Protocol
from uuid import uuid4

from .schemas import Message, ModelTurn, ToolCall, ToolDefinition, UsageRecord


class ModelProvider(Protocol):
    def complete(self, messages: list[Message], tools: list[ToolDefinition]) -> ModelTurn:
        """Return text or one or more tool requests."""


def _post_json(url: str, payload: dict, headers: dict[str, str] | None = None) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Model endpoint request failed: {exc}") from exc


def _openai_tools(tools: list[ToolDefinition]) -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            },
        }
        for tool in tools
    ]


def _message_payload(message: Message) -> dict:
    payload: dict = {"role": message.role, "content": message.content}
    if message.name:
        payload["name"] = message.name
    if message.tool_call_id:
        payload["tool_call_id"] = message.tool_call_id
    if message.tool_calls:
        payload["tool_calls"] = [
            {
                "id": call.id,
                "type": "function",
                "function": {"name": call.name, "arguments": json.dumps(call.arguments)},
            }
            for call in message.tool_calls
        ]
    if message.reasoning_details:
        payload["reasoning_details"] = message.reasoning_details
    return payload


class OllamaProvider:
    def __init__(self, model: str | None = None, base_url: str | None = None):
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen3:4b")
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")

    def complete(self, messages: list[Message], tools: list[ToolDefinition]) -> ModelTurn:
        data = _post_json(
            f"{self.base_url}/api/chat",
            {
                "model": self.model,
                "messages": [_message_payload(message) for message in messages],
                "tools": _openai_tools(tools),
                "stream": False,
                "think": False,
                "options": {"temperature": 0},
            },
        )
        message = data["message"]
        calls = []
        for raw in message.get("tool_calls", []):
            function = raw["function"]
            arguments = function.get("arguments", {})
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            calls.append(
                ToolCall(
                    id=raw.get("id", str(uuid4())),
                    name=function["name"],
                    arguments=arguments,
                )
            )
        return ModelTurn(content=message.get("content", ""), tool_calls=calls)


class OpenRouterProvider:
    def __init__(self, model: str | None = None, api_key: str | None = None):
        self.model = model or os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b")
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.reasoning_effort = os.getenv("OPENROUTER_REASONING_EFFORT", "low")
        self.max_output_tokens = int(os.getenv("OPENROUTER_MAX_OUTPUT_TOKENS", "800"))
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required for API mode")

    def complete(self, messages: list[Message], tools: list[ToolDefinition]) -> ModelTurn:
        payload = {
            "model": self.model,
            "messages": [_message_payload(message) for message in messages],
            "tools": _openai_tools(tools),
            "temperature": 0,
            "max_tokens": self.max_output_tokens,
            # Preserve reasoning_details across tool turns as recommended by
            # OpenRouter for reasoning models. Course UI need not display them.
            "reasoning": {"effort": self.reasoning_effort, "exclude": False},
            "provider": {"sort": "price", "require_parameters": True},
        }
        max_prompt_price = os.getenv("OPENROUTER_MAX_PROMPT_PRICE")
        max_completion_price = os.getenv("OPENROUTER_MAX_COMPLETION_PRICE")
        if max_prompt_price and max_completion_price:
            payload["provider"]["max_price"] = {
                "prompt": float(max_prompt_price),
                "completion": float(max_completion_price),
            }

        data = _post_json(
            "https://openrouter.ai/api/v1/chat/completions",
            payload,
            {"Authorization": f"Bearer {self.api_key}"},
        )
        message = data["choices"][0]["message"]
        raw_usage = data.get("usage") or {}
        completion_details = raw_usage.get("completion_tokens_details") or {}
        usage = UsageRecord(
            prompt_tokens=raw_usage.get("prompt_tokens", 0) or 0,
            completion_tokens=raw_usage.get("completion_tokens", 0) or 0,
            reasoning_tokens=completion_details.get("reasoning_tokens", 0) or 0,
            cost_usd=float(raw_usage.get("cost", 0) or 0),
        )
        calls = []
        for raw in message.get("tool_calls", []):
            function = raw["function"]
            arguments = function.get("arguments", {})
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            calls.append(ToolCall(id=raw["id"], name=function["name"], arguments=arguments))
        return ModelTurn(
            content=message.get("content") or "",
            tool_calls=calls,
            reasoning_details=message.get("reasoning_details") or [],
            usage=usage,
        )


class MockModelProvider:
    """Deterministic provider that demonstrates the loop without inference."""

    def complete(self, messages: list[Message], tools: list[ToolDefinition]) -> ModelTurn:
        question = next(message.content for message in messages if message.role == "user")
        tool_messages = [message for message in messages if message.role == "tool"]
        used = [message.name for message in tool_messages if message.name]
        lowered = question.lower()

        if any(word in lowered for word in ("calculate", "compute", "multiply", "+", "*")) and "calculator" not in used:
            expression = "12 * 7" if "12" in lowered and "7" in lowered else "2 + 2"
            return ModelTurn(
                tool_calls=[ToolCall(id="mock-calculation", name="calculator", arguments={"expression": expression})]
            )

        if any(word in lowered for word in ("python", "agent", "tool", "structured")) and "search_local_notes" not in used:
            return ModelTurn(
                tool_calls=[
                    ToolCall(id="mock-search", name="search_local_notes", arguments={"query": question})
                ]
            )

        observations = " ".join(message.content for message in tool_messages)
        summary = observations or "The mock model generated a direct response without using a tool."
        payload = {
            "topic": question,
            "summary": summary,
            "key_points": [
                "The application controls tool execution.",
                "The agent loop is bounded by host code.",
            ],
            "tools_used": used,
            "confidence": 0.9,
        }
        return ModelTurn(content=json.dumps(payload))


def provider_from_environment() -> ModelProvider:
    # Mock is intentionally the code-level fallback so tests never spend money.
    # The classroom .env explicitly selects api mode.
    mode = os.getenv("MODEL_MODE", "mock").lower()
    if mode == "mock":
        return MockModelProvider()
    if mode == "local":
        return OllamaProvider()
    if mode == "api":
        return OpenRouterProvider()
    raise ValueError("MODEL_MODE must be one of: mock, local, api")
