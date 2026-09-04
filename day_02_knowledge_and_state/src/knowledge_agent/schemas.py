"""Typed data exchanged by the Day 2 pipeline."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    chunk_id: str
    source: str
    title: str
    section: str
    text: str

    @property
    def searchable_text(self) -> str:
        return f"{self.title}\n{self.section}\n{self.text}"


class RetrievedChunk(BaseModel):
    chunk: DocumentChunk
    score: float
    rank: int


class Citation(BaseModel):
    source: str
    section: str
    chunk_id: str


class ModelAnswer(BaseModel):
    """Exactly the fields we ask the model to produce.

    Note what is missing: we never ask the model whether its answer is grounded.
    A model saying "grounded": true proves nothing. The application decides that
    afterwards by checking the citations against the chunks it actually retrieved.
    """

    answer: str
    citations: list[Citation] = Field(default_factory=list)
    abstained: bool


class GroundedAnswer(ModelAnswer):
    """A model answer after the application has validated it.

    grounded          - set by KnowledgeAssistant._validate_citations, never by the model.
    dropped_citations - citations the model returned for chunks we never supplied.
    """

    grounded: bool = False
    dropped_citations: list[Citation] = Field(default_factory=list)


class KnowledgeState(BaseModel):
    question: str
    retrieved: list[RetrievedChunk] = Field(default_factory=list)
    answer: GroundedAnswer | None = None
    status: Literal["created", "retrieved", "completed", "failed"] = "created"
    error: str | None = None


class GoldenCase(BaseModel):
    id: str
    question: str
    answerable: bool
    expected_source: str | None
    expected_section: str | None
    essential_terms: list[str]
