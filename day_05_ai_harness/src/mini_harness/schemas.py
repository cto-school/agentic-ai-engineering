from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any, Literal


@dataclass
class ModelConfig:
    provider: Literal["mock", "openrouter", "ollama"] = "mock"
    model: str = "mock-deterministic"
    temperature: float = 0.0
    max_output_tokens: int = 400


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]
    risk: Literal["read", "write", "external", "destructive"]


@dataclass
class AgentConfig:
    name: str
    instructions: str
    allowed_tools: list[str]
    max_steps: int = 4
    model: ModelConfig = field(default_factory=ModelConfig)


@dataclass
class ModelDecision:
    kind: Literal["tool", "final"]
    content: str = ""
    tool: str | None = None
    arguments: dict[str, Any] = field(default_factory=dict)
    usage: dict[str, float | int] = field(default_factory=dict)
    call_id: str | None = None
    reasoning_details: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class RunResult:
    run_id: str
    status: Literal["completed", "pending_approval", "cancelled", "failed", "step_limit"]
    output: str = ""
    pending_action: dict[str, Any] | None = None
    events: list[dict[str, Any]] = field(default_factory=list)
