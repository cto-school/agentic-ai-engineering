"""Run retrieval and answer evaluation as two separate reports.

Retrieval is scored first and on its own. If the expected evidence never reaches the
model, no prompt change can repair the answer.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from knowledge_agent.evaluation import (  # noqa: E402
    evaluate_answers,
    evaluate_retrieval,
    load_golden_set,
    render_table,
    summarize,
    summarize_detail,
    summarize_essential_terms,
)
from run_project import build_assistant  # noqa: E402


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    assistant = build_assistant("mock")
    cases = load_golden_set(PROJECT_ROOT / "data" / "golden_set.json")

    retrieval = evaluate_retrieval(assistant.index, cases, top_k=3)
    answers = evaluate_answers(assistant, cases)

    print("RETRIEVAL (n/a = unanswerable case, no expected evidence exists)")
    print(render_table(retrieval, ["id", "answerable", "source_hit", "section_hit", "expected_rank"]))
    print()
    print("rates over applicable cases:", summarize(retrieval, ["source_hit", "section_hit"]))
    print("counts                    :", summarize_detail(retrieval, ["source_hit", "section_hit"]))

    print()
    print("ANSWERS")
    print(
        render_table(
            answers,
            [
                "id",
                "answerable",
                "abstained",
                "abstention_correct",
                "citation_correct",
                "citation_provenance_ok",
                "essential_term_coverage",
            ],
        )
    )
    print()
    answer_fields = ["completed", "abstention_correct", "citation_correct", "citation_provenance_ok"]
    print("rates over applicable cases:", summarize(answers, answer_fields))
    print("counts                    :", summarize_detail(answers, answer_fields))
    print("essential terms           :", summarize_essential_terms(answers))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
