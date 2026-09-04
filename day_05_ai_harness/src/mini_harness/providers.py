"""Provider adapters. Swapping the model must not change policy or the registry."""
from __future__ import annotations
import json
import os
import urllib.error
import urllib.request
from typing import Any, Protocol
from .schemas import AgentConfig, ModelDecision, ToolSpec


class ModelProvider(Protocol):
    def decide(self, prompt: str, config: AgentConfig, tools: list[ToolSpec], history: list[dict]) -> ModelDecision: ...


# Values used when a mock plan does not spell an argument out itself.
_PLACEHOLDER_BY_TYPE: dict[str, Any] = {
    "string": "", "integer": 1, "number": 1, "boolean": True, "array": [], "object": {},
}


def _fill(value: Any, prompt: str) -> Any:
    """Replace the literal token {prompt} inside strings coming from a mock plan."""
    if isinstance(value, str):
        return value.replace("{prompt}", prompt)
    if isinstance(value, dict):
        return {key: _fill(item, prompt) for key, item in value.items()}
    if isinstance(value, list):
        return [_fill(item, prompt) for item in value]
    return value


def default_arguments(spec: ToolSpec, prompt: str) -> dict[str, Any]:
    """Build schema-valid arguments for a tool nobody wrote a mock plan for.

    Every required string gets the prompt; other required types get a harmless
    placeholder. This is why a brand-new agent configuration still produces a
    real tool request (and therefore a real policy event) in mock mode.
    """
    schema = spec.input_schema
    arguments: dict[str, Any] = {}
    for key in schema.get("required", []):
        kind = schema.get("properties", {}).get(key, {}).get("type", "string")
        arguments[key] = prompt if kind == "string" else _PLACEHOLDER_BY_TYPE.get(kind, prompt)
    return arguments


def applicable_plan(config: AgentConfig, tools: list[ToolSpec], prompt: str) -> list[dict[str, Any]]:
    """Turn config.mock_plan into the concrete steps this prompt should take."""
    visible = {spec.name: spec for spec in tools}
    steps: list[dict[str, Any]] = []
    for entry in config.mock_plan:
        name = entry.get("tool")
        if name not in visible:
            continue  # not on this agent's allow-list -> the step cannot apply
        trigger = entry.get("when")
        if trigger and trigger.lower() not in prompt.lower():
            continue  # this step only applies to prompts containing `when`
        if entry.get("arguments") is None:
            arguments = default_arguments(visible[name], prompt)
        else:
            arguments = _fill(entry["arguments"], prompt)
        steps.append({"tool": name, "arguments": arguments})
    if steps or not tools:
        return steps
    # Sensible default: the config carries no plan, so request the first visible tool once.
    first = tools[0]
    return [{"tool": first.name, "arguments": default_arguments(first, prompt)}]


class MockModel:
    """Deterministic orchestration test double; it never pretends to be intelligent.

    It reads the *configuration*, not the agent's name, so adding a third agent
    configuration needs no change to this file.
    """

    def decide(self, prompt, config, tools, history):
        steps = applicable_plan(config, tools, prompt)
        results = [item for item in history if item.get("role") == "tool"]
        if len(results) < len(steps):
            step = steps[len(results)]
            return ModelDecision("tool", tool=step["tool"], arguments=step["arguments"])
        if results:
            return ModelDecision("final", content=f"Completed with tool result: {results[-1]['content']}")
        return ModelDecision("final", content="No permitted tool is needed.")


class FlakyModel:
    """Teaching double: fails its first `failures` calls, then behaves normally.

    Used to make the runtime's bounded retry with backoff visible in the events.
    """

    def __init__(self, failures: int = 1, inner: ModelProvider | None = None,
                 error: str = "Simulated 429 rate limit from the provider"):
        self.failures = failures
        self.inner = inner or MockModel()
        self.error = error
        self.calls = 0

    def decide(self, prompt, config, tools, history):
        self.calls += 1
        if self.calls <= self.failures:
            raise RuntimeError(f"{self.error} (attempt {self.calls})")
        return self.inner.decide(prompt, config, tools, history)


def build_provider(config):
    """Map a ModelConfig onto a concrete adapter. Mock costs nothing and needs no key."""
    if config.provider == "mock":
        return MockModel()
    if config.provider == "openrouter":
        return OpenAICompatibleProvider(
            model=config.model, base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"), max_tokens=config.max_output_tokens,
            temperature=config.temperature,
            reasoning_effort=os.getenv("OPENROUTER_REASONING_EFFORT", "low"))
    if config.provider == "ollama":
        return OpenAICompatibleProvider(
            model=config.model, base_url=os.getenv("OLLAMA_OPENAI_BASE_URL", "http://localhost:11434/v1"),
            api_key="ollama", max_tokens=config.max_output_tokens, temperature=config.temperature)
    raise ValueError(f"Unsupported provider: {config.provider}")


class OpenAICompatibleProvider:
    """Small OpenRouter/Ollama adapter using the provider-neutral harness contracts."""

    def __init__(self, model: str, base_url: str, api_key: str | None, max_tokens: int = 400,
                 temperature: float = 0.0, reasoning_effort: str | None = None):
        if not api_key:
            raise ValueError("The selected provider API key is not configured")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.reasoning_effort = reasoning_effort

    def decide(self, prompt, config, tools, history):
        normalized_history = []
        keep = {"role", "content", "tool_calls", "tool_call_id", "name", "reasoning_details"}
        for item in history:
            normalized_history.append({key: value for key, value in item.items() if key in keep})
        messages = [{"role": "system", "content": config.instructions},
                    {"role": "user", "content": prompt}, *normalized_history]
        payload = {"model": self.model, "messages": messages, "temperature": self.temperature,
                   "max_tokens": self.max_tokens,
                   "tools": [{"type": "function", "function": {
                       "name": tool.name, "description": tool.description,
                       "parameters": tool.input_schema}} for tool in tools]}
        if self.reasoning_effort:
            payload["reasoning"] = {"effort": self.reasoning_effort, "exclude": False}
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"), method="POST",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"})
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            # RuntimeError is treated as transient by the runtime's retry budget.
            raise RuntimeError(f"Model request failed: {exc}") from exc
        message = data["choices"][0]["message"]
        usage = data.get("usage") or {}
        usage_record = {"prompt_tokens": usage.get("prompt_tokens", 0) or 0,
                        "completion_tokens": usage.get("completion_tokens", 0) or 0,
                        "cost_usd": float(usage.get("cost", 0) or 0)}
        calls = message.get("tool_calls") or []
        if calls:
            function = calls[0]["function"]
            arguments = function.get("arguments", {})
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            return ModelDecision("tool", tool=function["name"], arguments=arguments, usage=usage_record,
                                 call_id=calls[0].get("id"),
                                 reasoning_details=message.get("reasoning_details") or [])
        return ModelDecision("final", content=message.get("content") or "", usage=usage_record,
                             reasoning_details=message.get("reasoning_details") or [])
