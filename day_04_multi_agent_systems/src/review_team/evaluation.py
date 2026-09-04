"""Score one review run against the instructor-owned golden defect list.

Two rules keep the score honest:

1. A golden defect can be found only ONCE. If three reviewers report the same defect,
   recall goes up by one and the two extras are counted as `duplicates`.
2. A finding that matches no golden defect is a `false_positive`. We never silently
   drop it.

Matching a finding to a defect is itself a judgement call. We try the stable id first
(our scripted reviewers reuse it) and otherwise match by category plus line proximity,
which is what you must do for a real model whose ids are arbitrary.
"""
from __future__ import annotations

import json
from pathlib import Path

from .schemas import ReviewRun


def match_to_golden(finding, golden: list[dict], line_window: int = 1) -> str | None:
    """Return the id of the golden defect this finding describes, or None."""
    by_id = {item["id"]: item for item in golden}
    if finding.id in by_id:                       # the scripted reviewers reuse golden ids
        return finding.id
    # Otherwise: same category, and close enough in the file to be the same defect.
    candidates = [item for item in golden
                  if item["category"] == finding.category
                  and abs(item["line"] - finding.line) <= line_window]
    if not candidates:
        return None
    # Nearest line wins; ties break on the id so the result never depends on ordering.
    candidates.sort(key=lambda item: (abs(item["line"] - finding.line), item["id"]))
    return candidates[0]["id"]


def evaluate(run: ReviewRun, golden_path: str | Path,
             price_per_million_tokens: float = 0.0, line_window: int = 1) -> dict:
    """Turn a ReviewRun into the row of numbers we compare architectures with."""
    golden = json.loads(Path(golden_path).read_text(encoding="utf-8"))
    expected = {item["id"] for item in golden}

    matched: list[str] = []          # golden ids found, in order, one entry per finding
    duplicates: list[str] = []       # findings that re-report an already matched defect
    false_positives: list[str] = []  # findings matching no golden defect

    for finding in run.findings:
        defect_id = match_to_golden(finding, golden, line_window)
        if defect_id is None:
            false_positives.append(finding.id)
        elif defect_id in matched:
            duplicates.append(finding.id)
        else:
            matched.append(defect_id)

    tokens = run.total_tokens
    return {
        "system": run.system,
        "known_defects": len(expected),
        "found": len(matched),
        "recall": round(len(matched) / len(expected), 3) if expected else 0.0,
        "false_positives": len(false_positives),
        "duplicates": len(duplicates),               # duplicates that survived into the report
        "merged_duplicates": run.merged_duplicates,  # duplicates the supervisor absorbed
        "dropped_over_cap": run.dropped_over_cap,
        "raw_findings": run.raw_findings,
        "reported_findings": len(run.findings),
        "model_calls": run.model_calls,
        "tokens": tokens,
        "elapsed_ms": round(run.elapsed_ms, 1),
        "cost_usd": round(run.cost_usd, 6),
        "estimated_cost_usd": round(tokens / 1_000_000 * price_per_million_tokens, 6),
        "missed": sorted(expected - set(matched)),
        "false_positive_ids": false_positives,
    }
