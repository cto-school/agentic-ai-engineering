"""Separate retrieval evaluation from answer evaluation."""

from __future__ import annotations

import json
from pathlib import Path

from .assistant import KnowledgeAssistant
from .retrieval import VectorIndex
from .schemas import GoldenCase


def load_golden_set(path: str | Path) -> list[GoldenCase]:
    return [GoldenCase.model_validate(item) for item in json.loads(Path(path).read_text(encoding="utf-8"))]


def evaluate_retrieval(index: VectorIndex, cases: list[GoldenCase], top_k: int = 3) -> list[dict]:
    records = []
    for case in cases:
        retrieved = index.search(case.question, top_k=top_k)
        sources = [item.chunk.source for item in retrieved]
        sections = [item.chunk.section for item in retrieved]
        source_hit = (not case.answerable) or case.expected_source in sources
        section_hit = (not case.answerable) or any(
            item.chunk.source == case.expected_source and item.chunk.section == case.expected_section
            for item in retrieved
        )
        records.append(
            {
                "id": case.id,
                "answerable": case.answerable,
                "source_hit": source_hit,
                "section_hit": section_hit,
                "retrieved_sources": sources,
                "retrieved_sections": sections,
            }
        )
    return records


def evaluate_answers(assistant: KnowledgeAssistant, cases: list[GoldenCase]) -> list[dict]:
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
        records.append(
            {
                "id": case.id,
                "completed": state.status == "completed",
                "abstention_correct": abstention_correct,
                "citation_correct": citation_correct,
                "essential_terms_found": len(term_hits),
                "essential_terms_total": len(case.essential_terms),
                "error": state.error,
            }
        )
    return records


def summarize(records: list[dict], fields: list[str]) -> dict[str, float]:
    if not records:
        return {field: 0.0 for field in fields}
    return {
        field: sum(bool(record[field]) for record in records) / len(records)
        for field in fields
    }

