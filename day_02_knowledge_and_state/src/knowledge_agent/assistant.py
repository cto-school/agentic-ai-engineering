"""The final Day 2 retrieval -> context -> grounded answer pipeline."""

from __future__ import annotations

from .generation import GroundedGenerator
from .retrieval import VectorIndex
from .schemas import KnowledgeState


class KnowledgeAssistant:
    def __init__(self, index: VectorIndex, generator: GroundedGenerator, top_k: int = 3):
        self.index = index
        self.generator = generator
        self.top_k = top_k

    def answer(self, question: str) -> KnowledgeState:
        state = KnowledgeState(question=question)
        try:
            state.retrieved = self.index.search(question, top_k=self.top_k)
            state.status = "retrieved"
            state.answer = self.generator.generate(question, state.retrieved)
            state.status = "completed"
        except Exception as exc:
            state.status = "failed"
            state.error = str(exc)
        return state

