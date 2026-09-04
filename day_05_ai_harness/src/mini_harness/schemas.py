"""Small data contracts shared by every part of the mini harness.

These dataclasses are deliberately plain: configuration is *data*, so it can be
stored in JSON files under ``configs/`` and reviewed like any other artefact.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any, Literal


@dataclass
class ModelConfig:
    """Which model to talk to and how. Never holds an API key (that lives in .env)."""
    provider: Literal["mock", "openrouter", "ollama"] = "mock"
    model: str = "mock-deterministic"
    temperature: float = 0.0
    max_output_tokens: int = 400


@dataclass
class ToolSpec:
    """What the model is told about a tool, plus the local risk label policy reads."""
    name: str
    description: str
    input_schema: dict[str, Any]
    risk: Literal["read", "write", "external", "destructive"]


@dataclass
class AgentConfig:
    """One application-specific agent: instructions, allow-list, limits, model.

    ``mock_plan`` is teaching-only. It lets a JSON config describe what the
    deterministic MockModel should request, so a new agent configuration can be
    added without editing ``providers.py``. Each entry looks like::

        {"tool": "send_email",
         "arguments": {"to": "mentor@example.test", "body": "{prompt}"},
         "when": "send"}

    ``when`` is an optional lower-case substring that must appear in the prompt
    for that step to apply; ``{prompt}`` inside a string argument is replaced by
    the run prompt. An empty plan falls back to a schema-derived default.
    """
    name: str
    instructions: str
    allowed_tools: list[str]
    max_steps: int = 4
    model: ModelConfig = field(default_factory=ModelConfig)
    mock_plan: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ModelDecision:
    """The only thing a provider may return: 'call this tool' or 'here is the answer'."""
    kind: Literal["tool", "final"]
    content: str = ""
    tool: str | None = None
    arguments: dict[str, Any] = field(default_factory=dict)
    usage: dict[str, float | int] = field(default_factory=dict)
    call_id: str | None = None
    reasoning_details: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class RunResult:
    """The outcome of one run. Every run ends in exactly one of these statuses."""
    run_id: str
    status: Literal["completed", "pending_approval", "cancelled", "failed", "step_limit"]
    output: str = ""
    pending_action: dict[str, Any] | None = None
    events: list[dict[str, Any]] = field(default_factory=list)
