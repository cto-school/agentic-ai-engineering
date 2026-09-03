from __future__ import annotations

import json
from pathlib import Path

from .agent import SafeTaskAgent
from .schemas import ActionRequest


def evaluate_safety(path: str | Path) -> dict:
    cases = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = []
    for case in cases:
        agent = SafeTaskAgent()
        result = agent.request(ActionRequest(case["tool"], case.get("arguments", {}), case["prompt"]))
        actual = {"completed": "allow", "pending_approval": "approval", "denied": "deny"}.get(result.status, result.status)
        rows.append({"id": case["id"], "expected": case["expected"], "actual": actual,
                     "passed": actual == case["expected"]})
    return {"passed": sum(r["passed"] for r in rows), "total": len(rows), "cases": rows}

