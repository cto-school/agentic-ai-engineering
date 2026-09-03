from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


Decision = Literal["allow", "approval", "deny"]


@dataclass
class Message:
    role: Literal["system", "user", "assistant", "tool"]
    content: str


@dataclass
class MemoryRecord:
    id: str
    user_id: str
    text: str
    source: str
    created_at: str
    updated_at: str


@dataclass
class PlanStep:
    number: int
    action: str
    status: Literal["pending", "completed", "blocked"] = "pending"


@dataclass
class ActionRequest:
    tool: str
    arguments: dict[str, Any] = field(default_factory=dict)
    reason: str = ""


@dataclass
class Event:
    event: str
    timestamp: str
    details: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ActionResult:
    status: Literal["completed", "pending_approval", "denied", "rejected", "error"]
    message: str
    action_id: str | None = None
    output: Any = None

