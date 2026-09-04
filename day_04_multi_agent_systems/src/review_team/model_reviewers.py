"""Reviewer providers.

Everything in this day talks to a reviewer through ONE tiny contract:

    findings, usage = provider.review(source, role)

`role` is "general" for the single reviewer, or "correctness" / "security" /
"maintainability" for a specialist. `usage` is the provider's own report of what the
call cost. Three implementations satisfy the contract:

* OpenRouterReviewer     - a real model call.
* MockStructuredReviewer - deterministic, offline, free; the classroom default.
* FallbackReviewer       - tries the live one, prints why it failed, uses the mock.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from typing import Protocol

from .reviewers import DEFAULT_SCENARIO, single_reviewer, specialist_review
from .schemas import Finding

ROLES = ("general", "correctness", "security", "maintainability")


class ReviewerProvider(Protocol):
    def review(self, source: str, role: str) -> tuple[list[Finding], dict]: ...


def _prompt(source: str, role: str) -> list[dict]:
    """Build the two chat messages. The golden defect list is never included."""
    scope = ("all correctness, security, and maintainability concerns" if role == "general"
             else f"only {role} concerns")
    schema = ('{"findings":[{"category":"correctness|security|maintainability","line":1,'
              '"title":"...","evidence":"exact source excerpt",'
              '"severity":"low|medium|high|critical","recommendation":"..."}]}')
    return [
        {"role": "system", "content": (
            f"You are a bounded engineering reviewer. Review {scope}. "
            f"Return JSON only in this shape: {schema}. "
            "Report at most 10 evidenced findings. Do not invent code.")},
        {"role": "user", "content": "Review this synthetic Python artifact:\n\n" + source},
    ]


def _parse_findings(content: str, role: str) -> list[Finding]:
    """Validate the model's JSON. Anything malformed raises instead of being trusted."""
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.I)
    data = json.loads(content)
    raw = data.get("findings", [])
    if not isinstance(raw, list) or len(raw) > 10:
        raise ValueError("findings must be a list of at most 10")
    allowed_categories = {"correctness", "security", "maintainability"}
    allowed_severity = {"low", "medium", "high", "critical"}
    findings = []
    for index, item in enumerate(raw, 1):
        category, severity, line = item.get("category"), item.get("severity"), item.get("line")
        if category not in allowed_categories or severity not in allowed_severity or not isinstance(line, int):
            raise ValueError(f"Invalid finding {index}")
        if role != "general" and category != role:
            raise ValueError(f"{role} reviewer returned a {category} finding")
        for field_name in ("title", "evidence", "recommendation"):
            if not isinstance(item.get(field_name), str) or not item[field_name].strip():
                raise ValueError(f"Missing {field_name} in finding {index}")
        findings.append(Finding(f"MODEL-{role[:3].upper()}-{line}-{index}", category, line,
                                item["title"], item["evidence"], severity,
                                item["recommendation"], f"{role}_model_reviewer"))
    return findings


class OpenRouterReviewer:
    """Live reviewer. Constructing it without a key raises, so guard it with `if LIVE`."""

    name = "OpenRouterReviewer"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required for OpenRouterReviewer")

    def review(self, source: str, role: str) -> tuple[list[Finding], dict]:
        payload = {"model": self.model, "messages": _prompt(source, role), "temperature": 0,
                   "max_tokens": 1200, "response_format": {"type": "json_object"},
                   "reasoning": {"effort": "low", "exclude": False},
                   "provider": {"sort": "price", "require_parameters": True}}
        request = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(payload).encode(), method="POST",
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {self.api_key}"})
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = json.loads(response.read().decode())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Review request failed: {exc}") from exc
        message = data["choices"][0]["message"]
        usage = data.get("usage") or {}
        findings = _parse_findings(message.get("content") or "", role)
        return findings, {"model": self.model,
                          "prompt_tokens": int(usage.get("prompt_tokens") or 0),
                          "completion_tokens": int(usage.get("completion_tokens") or 0),
                          "cost_usd": float(usage.get("cost") or 0.0),
                          "live": True}


class MockStructuredReviewer:
    """Offline stand-in with the same contract.

    `scenario` chooses which blind spots this reviewer has (see reviewers.SCENARIOS).
    `latency_s` fakes network delay so a sequential-vs-parallel timing demo is visible.
    """

    name = "MockStructuredReviewer"

    def __init__(self, scenario: str = DEFAULT_SCENARIO, latency_s: float = 0.0):
        self.scenario = scenario
        self.latency_s = latency_s

    def review(self, source: str, role: str) -> tuple[list[Finding], dict]:
        if role not in ROLES:
            raise ValueError(f"Unknown role {role!r}. Roles: {ROLES}")
        if self.latency_s:
            time.sleep(self.latency_s)      # stands in for a real network round trip
        findings = (single_reviewer(source, self.scenario) if role == "general"
                    else specialist_review(source, role, self.scenario))
        for finding in findings:
            finding.reviewer = f"{role}_mock_model"
        # A mock still reports usage honestly: these are the tokens a call of this size
        # would consume (about 4 characters per token), not an invented number for a
        # call that never happened.
        return findings, {"model": f"mock-structured-reviewer[{self.scenario}]",
                          "prompt_tokens": (len(source) + 3) // 4,
                          "completion_tokens": len(findings) * 45,
                          "cost_usd": 0.0,
                          "live": False}


class FallbackReviewer:
    """Try the live reviewer; on ANY failure print one line and use the mock instead.

    One expired key, rate limit or timeout must never stop a class mid-notebook.
    """

    name = "FallbackReviewer"

    def __init__(self, live: ReviewerProvider, mock: ReviewerProvider | None = None,
                 scenario: str = DEFAULT_SCENARIO):
        self.live = live
        self.mock = mock or MockStructuredReviewer(scenario)
        self.failures = 0

    def review(self, source: str, role: str) -> tuple[list[Finding], dict]:
        try:
            return self.live.review(source, role)
        except Exception as exc:            # noqa: BLE001 - deliberate classroom safety net
            self.failures += 1
            print(f"  live reviewer failed for role={role} "
                  f"({type(exc).__name__}: {exc}); falling back to MockStructuredReviewer")
            return self.mock.review(source, role)
