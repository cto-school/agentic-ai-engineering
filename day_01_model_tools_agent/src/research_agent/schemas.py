"""Small data contracts used by the Day 1 project."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A provider-neutral conversation message."""

    role: Literal["system", "user", "assistant", "tool"]
    content: str = ""
    name: str | None = None
    tool_call_id: str | None = None
    tool_calls: list["ToolCall"] = Field(default_factory=list)
    reasoning_details: list[dict[str, Any]] = Field(default_factory=list)


class ToolCall(BaseModel):
    """A request produced by a model; Python still executes the tool."""

    id: str
    name: str
    arguments: dict[str, Any]


class ModelTurn(BaseModel):
    """One model response, containing text or requested tools."""

    content: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)
    reasoning_details: list[dict[str, Any]] = Field(default_factory=list)
    usage: "UsageRecord" = Field(default_factory=lambda: UsageRecord())


class UsageRecord(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    reasoning_tokens: int = 0
    cost_usd: float = 0.0

    def add(self, other: "UsageRecord") -> "UsageRecord":
        return UsageRecord(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            reasoning_tokens=self.reasoning_tokens + other.reasoning_tokens,
            cost_usd=self.cost_usd + other.cost_usd,
        )


class ToolResult(BaseModel):
    name: str
    call_id: str
    output: str
    is_error: bool = False


class ResearchResponse(BaseModel):
    """Validated final output shown to the application/user."""

    topic: str
    summary: str
    key_points: list[str] = Field(min_length=1)
    tools_used: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class AgentResult(BaseModel):
    status: Literal["completed", "failed", "max_steps"]
    response: ResearchResponse | None = None
    messages: list[Message]
    steps: int
    usage: UsageRecord = Field(default_factory=UsageRecord)
    error: str | None = None


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any]
