"""Run retrieval and answer evaluation as two separate reports."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from knowledge_agent.evaluation import (  # noqa: E402
    evaluate_answers,
    evaluate_retrieval,
    load_golden_set,
    summarize,
)
from run_project import build_assistant  # noqa: E402


def main() -> int:
    assistant = build_assistant("mock")
    cases = load_golden_set(PROJECT_ROOT / "data" / "golden_set.json")

    retrieval = evaluate_retrieval(assistant.index, cases, top_k=3)
    answers = evaluate_answers(assistant, cases)

    for record in retrieval:
        print(json.dumps({"evaluation": "retrieval", **record}))
    for record in answers:
        print(json.dumps({"evaluation": "answer", **record}))

    retrieval_summary = summarize(retrieval, ["source_hit", "section_hit"])
    answer_summary = summarize(answers, ["completed", "abstention_correct", "citation_correct"])
    print(json.dumps({"retrieval_summary": retrieval_summary, "answer_summary": answer_summary}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

