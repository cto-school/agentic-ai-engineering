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


class GroundedAnswer(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    grounded: bool
    abstained: bool


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

