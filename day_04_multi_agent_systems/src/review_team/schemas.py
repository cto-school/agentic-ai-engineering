"""Data contracts every reviewer, the supervisor and the evaluator agree on.

Keeping the contract in one small file is the point of the day: agents hand each
other *validated records*, never free-form chat transcripts.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

Category = Literal["correctness", "security", "maintainability"]
Severity = Literal["low", "medium", "high", "critical"]


@dataclass
class Finding:
    """One evidenced review finding. This is the only object that crosses a handoff."""

    id: str                 # stable identity of THIS finding (not of the defect)
    category: Category      # correctness | security | maintainability
    line: int               # 1-based line in the reviewed artifact
    title: str              # short human-readable statement of the problem
    evidence: str           # the exact source excerpt the claim rests on
    severity: Severity      # low | medium | high | critical
    recommendation: str     # what to change
    reviewer: str           # which role produced it (provenance)

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class SynthesisReport:
    """What the supervisor did, so truncation and merging are never silent."""

    findings: list[Finding]        # the findings that survived
    received: int = 0              # how many findings arrived from all branches
    merged_duplicates: int = 0     # how many were collapsed into another finding
    kept: int = 0                  # how many were returned
    dropped_over_cap: int = 0      # how many were cut by max_findings
    merge_key: str = "location"    # which dedup rule was used

    def as_dict(self) -> dict:
        data = asdict(self)
        data["findings"] = [f.as_dict() for f in self.findings]
        return data


@dataclass
class ReviewRun:
    """One end-to-end run of one review *system*, with its real telemetry.

    Every number here is measured, never invented: token counts come from the
    provider's usage report, and a step that makes no model call contributes zero.
    """

    system: str
    findings: list[Finding] = field(default_factory=list)
    model_calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    elapsed_ms: float = 0.0
    raw_findings: int = 0          # findings produced before the supervisor merged them
    merged_duplicates: int = 0     # how many the supervisor collapsed
    dropped_over_cap: int = 0      # how many the supervisor truncated away
    trace: list[dict] = field(default_factory=list)

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens
