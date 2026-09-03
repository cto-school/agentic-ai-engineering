from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Literal

Category = Literal["correctness", "security", "maintainability"]


@dataclass
class Finding:
    id: str
    category: Category
    line: int
    title: str
    evidence: str
    severity: Literal["low", "medium", "high", "critical"]
    recommendation: str
    reviewer: str

    def as_dict(self): return asdict(self)


@dataclass
class ReviewRun:
    system: str
    findings: list[Finding] = field(default_factory=list)
    model_calls: int = 0
    estimated_tokens: int = 0
    elapsed_ms: float = 0
    trace: list[dict] = field(default_factory=list)
