from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Protocol

from .schemas import ActionRequest


@dataclass
class Proposal:
    """What a model (or a stand-in) *wants* to do. It is never permission."""
    kind: str                                   # "action" or "final"
    message: str = ""
    action: ActionRequest | None = None
    usage: dict[str, Any] = field(default_factory=dict)


class ActionProposer(Protocol):
    def propose(self, prompt: str, visible_tools: list[dict]) -> Proposal: ...


class MockActionProposer:
    """A deliberately naive stand-in for a model.

    It matches single keywords anywhere in the prompt, so "please do not delete
    anything" still proposes `delete_all_tasks`. That bug is kept on purpose: the
    lesson of Day 3 is that policy, not the proposer, is what protects the user.
    """

    def propose(self, prompt: str, visible_tools: list[dict]) -> Proposal:
        lowered = prompt.lower()
        if "delete" in lowered:
            return Proposal("action", action=ActionRequest("delete_all_tasks", {}, prompt))
        if "send" in lowered:
            return Proposal("action", action=ActionRequest("send_email", {
                "to": "mentor@example.test", "subject": "Synthetic update", "body": prompt}, prompt))
        if "calendar" in lowered or "schedule" in lowered:
            return Proposal("action", action=ActionRequest("view_calendar", {}, prompt))
        if "draft" in lowered:
            return Proposal("action", action=ActionRequest("create_draft", {
                "to": "mentor@example.test", "subject": "Synthetic update", "body": prompt}, prompt))
        return Proposal("final", "No tool is needed for this request.")


class OpenRouterActionProposer:
    """The same interface, backed by a real model. Policy treats both identically."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required")

    def propose(self, prompt: str, visible_tools: list[dict]) -> Proposal:
        contract = ('Return JSON only: '
                    '{"kind":"action|final","message":"...","tool":"name or null","arguments":{}}.')
        messages = [
            {"role": "system", "content": contract +
             " You may propose only a visible tool. Proposing is not authorization."},
            {"role": "user", "content": json.dumps({"request": prompt, "visible_tools": visible_tools})},
        ]
        payload = {
            "model": self.model, "messages": messages, "temperature": 0, "max_tokens": 500,
            "response_format": {"type": "json_object"},
            "reasoning": {"effort": "low", "exclude": False},
            "provider": {"sort": "price", "require_parameters": True},
        }
        request = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(payload).encode(), method="POST",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"})
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = json.loads(response.read().decode())
            raw = json.loads(data["choices"][0]["message"].get("content") or "{}")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
            raise RuntimeError(f"Proposal failed: {exc}") from exc

        usage = data.get("usage") or {}
        record = {"prompt_tokens": usage.get("prompt_tokens", 0) or 0,
                  "completion_tokens": usage.get("completion_tokens", 0) or 0,
                  "cost_usd": float(usage.get("cost", 0) or 0)}
        if raw.get("kind") == "final":
            return Proposal("final", str(raw.get("message", "")), usage=record)
        tool, arguments = raw.get("tool"), raw.get("arguments", {})
        if not isinstance(tool, str) or not isinstance(arguments, dict):
            raise ValueError("Invalid action proposal")
        return Proposal("action", action=ActionRequest(tool, arguments, prompt), usage=record)
