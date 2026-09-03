from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .schemas import Decision


@dataclass
class SimulatedWorkspace:
    calendar: list[dict[str, str]] = field(default_factory=lambda: [
        {"time": "10:00", "title": "Project review"},
        {"time": "15:00", "title": "Lab practice"},
    ])
    drafts: list[dict[str, str]] = field(default_factory=list)
    sent: list[dict[str, str]] = field(default_factory=list)
    tasks: list[str] = field(default_factory=lambda: ["Finish lab notes", "Review citations"])

    def view_calendar(self, **_: Any) -> list[dict[str, str]]:
        return list(self.calendar)

    def create_draft(self, to: str, subject: str, body: str) -> dict[str, str]:
        draft = {"to": to, "subject": subject, "body": body}
        self.drafts.append(draft)
        return draft

    def send_email(self, to: str, subject: str, body: str) -> dict[str, str]:
        message = {"to": to, "subject": subject, "body": body}
        self.sent.append(message)
        return message

    def delete_all_tasks(self, **_: Any) -> int:
        count = len(self.tasks)
        self.tasks.clear()
        return count


POLICY: dict[str, Decision] = {
    "view_calendar": "allow",
    "create_draft": "allow",
    "send_email": "approval",
    "delete_all_tasks": "deny",
}


def tool_registry(workspace: SimulatedWorkspace) -> dict[str, Callable[..., Any]]:
    return {
        "view_calendar": workspace.view_calendar,
        "create_draft": workspace.create_draft,
        "send_email": workspace.send_email,
        "delete_all_tasks": workspace.delete_all_tasks,
    }

