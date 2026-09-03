from __future__ import annotations
import json
from pathlib import Path
from .schemas import ReviewRun


def evaluate(run: ReviewRun, golden_path: str | Path, price_per_million_tokens: float = 0.0) -> dict:
    golden = json.loads(Path(golden_path).read_text(encoding="utf-8"))
    expected={x["id"] for x in golden}; matched=set(); false=set()
    for finding in run.findings:
        if finding.id in expected: matched.add(finding.id); continue
        candidates=[item for item in golden if item["category"]==finding.category and abs(item["line"]-finding.line)<=1]
        if len(candidates)==1: matched.add(candidates[0]["id"])
        else: false.add(finding.id)
    found={x.id for x in run.findings}; true=matched
    duplicate_count = len(run.findings) - len(found)
    return {"system":run.system, "known_defects":len(expected), "found":len(true),
        "recall":round(len(true)/len(expected),3), "false_positives":len(false),
        "duplicates":duplicate_count, "model_calls":run.model_calls,
        "estimated_tokens":run.estimated_tokens, "elapsed_ms":round(run.elapsed_ms,3),
        "estimated_cost_usd":round(run.estimated_tokens/1_000_000*price_per_million_tokens,6),
        "missed":sorted(expected-matched)}
