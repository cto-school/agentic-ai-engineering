"""The supervisor: a bounded fan-in step, not another conversation.

Its whole contract is: receive validated findings from every branch, merge findings
that describe the same defect, rank them, cap the output, and stop. It reports what it
did (`SynthesisReport`) so that merging and truncation are never silent.
"""
from __future__ import annotations

from .schemas import Finding, SynthesisReport

SEVERITY = {"critical": 4, "high": 3, "medium": 2, "low": 1}


def _stronger(candidate: Finding, current: Finding) -> bool:
    """Prefer the higher severity; break ties so the result is stable across runs."""
    if SEVERITY[candidate.severity] != SEVERITY[current.severity]:
        return SEVERITY[candidate.severity] > SEVERITY[current.severity]
    return candidate.id < current.id


def synthesize_with_report(groups: list[list[Finding]], max_findings: int = 20,
                           merge_by: str = "location", line_window: int = 1) -> SynthesisReport:
    """Merge findings from every branch and report exactly what happened.

    merge_by="id"        - two findings are the same only if their ids match. Simple,
                           but a static checker and a model reviewer naming the same
                           defect differently both survive: the duplicate is real.
    merge_by="location"  - two findings are the same if they share a category and their
                           lines are within `line_window`. This catches cross-reviewer
                           duplicates, at the risk of FALSE MERGES: two genuinely
                           different security problems on adjacent lines collapse into
                           one and the second one is lost. That risk is the price of a
                           deduplication rule that does not depend on shared ids.
    """
    if merge_by not in {"id", "location"}:
        raise ValueError("merge_by must be 'id' or 'location'")

    incoming = [item for group in groups for item in group]
    kept: list[Finding] = []          # one entry per distinct defect found so far
    merged_duplicates = 0

    for finding in incoming:
        match_index = None
        for index, existing in enumerate(kept):
            if merge_by == "id":
                same = finding.id == existing.id
            else:
                same = (finding.category == existing.category
                        and abs(finding.line - existing.line) <= line_window)
            if same:
                match_index = index
                break

        if match_index is None:
            kept.append(finding)                       # first time we have seen this defect
        else:
            merged_duplicates += 1                     # a duplicate: keep the stronger record
            if _stronger(finding, kept[match_index]):
                kept[match_index] = finding

    ranked = sorted(kept, key=lambda f: (-SEVERITY[f.severity], f.line, f.id))
    final = ranked[:max_findings]
    return SynthesisReport(
        findings=final,
        received=len(incoming),
        merged_duplicates=merged_duplicates,
        kept=len(final),
        dropped_over_cap=len(ranked) - len(final),     # never silently truncate
        merge_key=merge_by,
    )


def synthesize(groups: list[list[Finding]], max_findings: int = 20,
               merge_by: str = "location", line_window: int = 1) -> list[Finding]:
    """Convenience wrapper when you only want the merged findings."""
    return synthesize_with_report(groups, max_findings, merge_by, line_window).findings
