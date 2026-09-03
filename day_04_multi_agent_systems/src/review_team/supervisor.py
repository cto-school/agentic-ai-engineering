from __future__ import annotations
from .schemas import Finding

SEVERITY = {"critical": 4, "high": 3, "medium": 2, "low": 1}


def synthesize(groups: list[list[Finding]], max_findings: int = 20) -> list[Finding]:
    """Bounded fan-in: deduplicate by stable defect ID and retain strongest evidence."""
    merged: dict[str, Finding] = {}
    for finding in (item for group in groups for item in group):
        current = merged.get(finding.id)
        if current is None or SEVERITY[finding.severity] > SEVERITY[current.severity]:
            merged[finding.id] = finding
    return sorted(merged.values(), key=lambda f: (-SEVERITY[f.severity], f.line, f.id))[:max_findings]
