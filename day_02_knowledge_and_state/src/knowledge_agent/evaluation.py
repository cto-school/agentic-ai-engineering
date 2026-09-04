"""Separate retrieval evaluation from answer evaluation.

Two rules make this scorecard honest:

* A check that cannot apply to a case is reported as None ("n/a"), never as a pass.
  The unanswerable case has no expected source, so "did we retrieve it?" is meaningless.
* Rates are computed over the cases where the check applies, and the count is printed
  next to the rate so 1.0 out of 1 case never looks like 1.0 out of 10.
"""

from __future__ import annotations

import json
from pathlib import Path

from .assistant import KnowledgeAssistant
from .retrieval import VectorIndex
from .schemas import GoldenCase


def load_golden_set(path: str | Path) -> list[GoldenCase]:
    return [GoldenCase.model_validate(item) for item in json.loads(Path(path).read_text(encoding="utf-8"))]


def evaluate_retrieval(index: VectorIndex, cases: list[GoldenCase], top_k: int = 3) -> list[dict]:
    """Did the expected evidence reach the top-k list? Generation is not involved."""

    records = []
    for case in cases:
        retrieved = index.search(case.question, top_k=top_k)
        sources = [item.chunk.source for item in retrieved]
        sections = [item.chunk.section for item in retrieved]
        if case.answerable:
            source_hit = case.expected_source in sources
            section_hit = any(
                item.chunk.source == case.expected_source and item.chunk.section == case.expected_section
                for item in retrieved
            )
            # Where in the ranking did the expected chunk land? None means "not in top-k".
            expected_rank = next(
                (
                    item.rank
                    for item in retrieved
                    if item.chunk.source == case.expected_source and item.chunk.section == case.expected_section
                ),
                None,
            )
        else:
            # Nothing is expected, so a hit rate would be a fabricated pass.
            source_hit = section_hit = expected_rank = None
        records.append(
            {
                "id": case.id,
                "answerable": case.answerable,
                "source_hit": source_hit,
                "section_hit": section_hit,
                "expected_rank": expected_rank,
                "retrieved_ids": [item.chunk.chunk_id for item in retrieved],
                "retrieved_sources": sources,
                "retrieved_sections": sections,
            }
        )
    return records


def evaluate_answers(assistant: KnowledgeAssistant, cases: list[GoldenCase]) -> list[dict]:
    """Did the answer abstain correctly, cite retrieved evidence, and mention the facts?"""

    records = []
    for case in cases:
        state = assistant.answer(case.question)
        answer = state.answer
        cited_sources = [citation.source for citation in answer.citations] if answer else []
        text = answer.answer.lower() if answer else ""
        term_hits = [term for term in case.essential_terms if term.lower() in text]

        abstention_correct = bool(answer) and answer.abstained == (not case.answerable)
        citation_correct = bool(answer) and (
            (not case.answerable and not answer.citations)
            or (case.answerable and case.expected_source in cited_sources)
        )
        # Provenance is the application's own check: every citation survived validation.
        citation_provenance_ok = bool(answer) and answer.grounded
        coverage = len(term_hits) / len(case.essential_terms) if case.essential_terms else None

        records.append(
            {
                "id": case.id,
                "answerable": case.answerable,
                "completed": state.status == "completed",
                "abstained": bool(answer) and answer.abstained,
                "abstention_correct": abstention_correct,
                "citation_correct": citation_correct,
                "citation_provenance_ok": citation_provenance_ok,
                "dropped_citations": len(answer.dropped_citations) if answer else 0,
                "essential_terms_found": len(term_hits),
                "essential_terms_total": len(case.essential_terms),
                "essential_term_coverage": coverage,
                "missing_terms": [term for term in case.essential_terms if term not in term_hits],
                "error": state.error,
            }
        )
    return records


def summarize(records: list[dict], fields: list[str]) -> dict[str, float]:
    """Rate per field over the records where the field applies (None is skipped)."""

    summary: dict[str, float] = {}
    for field in fields:
        applicable = [record for record in records if record.get(field) is not None]
        summary[field] = round(sum(bool(record[field]) for record in applicable) / len(applicable), 3) if applicable else 0.0
    return summary


def summarize_detail(records: list[dict], fields: list[str]) -> dict[str, str]:
    """Same numbers as summarize(), formatted as 'hits/applicable' so 1.0 is readable."""

    detail: dict[str, str] = {}
    for field in fields:
        applicable = [record for record in records if record.get(field) is not None]
        hits = sum(bool(record[field]) for record in applicable)
        skipped = len(records) - len(applicable)
        note = f" ({skipped} n/a)" if skipped else ""
        detail[field] = f"{hits}/{len(applicable)}{note}"
    return detail


def summarize_essential_terms(records: list[dict]) -> dict[str, float | str]:
    """Essential-term coverage over the cases that define essential terms."""

    scored = [record for record in records if record["essential_terms_total"]]
    found = sum(record["essential_terms_found"] for record in scored)
    total = sum(record["essential_terms_total"] for record in scored)
    return {
        "cases_scored": len(scored),
        "terms_found": found,
        "terms_total": total,
        "coverage": round(found / total, 3) if total else 0.0,
    }


def render_table(records: list[dict], columns: list[str]) -> str:
    """Small aligned text table so notebooks can print results without extra libraries."""

    def cell(value: object) -> str:
        if value is None:
            return "n/a"
        if isinstance(value, bool):
            return "yes" if value else "NO"
        if isinstance(value, list):
            return ", ".join(str(item) for item in value)
        if isinstance(value, float):
            return f"{value:.2f}"
        return str(value)

    widths = [max(len(column), *(len(cell(record.get(column))) for record in records)) for column in columns]
    lines = ["  ".join(column.ljust(width) for column, width in zip(columns, widths))]
    lines.append("  ".join("-" * width for width in widths))
    for record in records:
        lines.append("  ".join(cell(record.get(column)).ljust(width) for column, width in zip(columns, widths)))
    return "\n".join(lines)
