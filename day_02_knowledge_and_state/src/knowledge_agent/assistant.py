"""The final Day 2 retrieval -> context -> grounded answer -> validation pipeline."""

from __future__ import annotations

from .generation import GroundedGenerator
from .retrieval import VectorIndex
from .schemas import GroundedAnswer, KnowledgeState, RetrievedChunk


def validate_citations(answer: GroundedAnswer, retrieved: list[RetrievedChunk]) -> GroundedAnswer:
    """Keep only citations that point at chunks we actually supplied to the model.

    A citation is a claim about *our* evidence, so the application can check it without
    asking anybody. Three things can be wrong:

    1. the chunk_id was never retrieved (invented, or copied from another answer);
    2. the chunk_id exists but the source/section do not match that chunk;
    3. an abstention arrives carrying citations, which contradicts itself.

    Cases 1 and 2 are dropped into `dropped_citations`; whatever survives sets `grounded`.
    """

    supplied = {item.chunk.chunk_id: item.chunk for item in retrieved}
    kept, dropped = [], []
    for citation in answer.citations:
        chunk = supplied.get(citation.chunk_id)
        if chunk is not None and chunk.source == citation.source and chunk.section == citation.section:
            kept.append(citation)
        else:
            dropped.append(citation)

    answer.citations = kept
    answer.dropped_citations = dropped
    if answer.abstained:
        # An abstention is well formed when it cites nothing at all.
        answer.grounded = not kept and not dropped
    else:
        # A real answer must keep at least one citation and must not have invented any.
        answer.grounded = bool(kept) and not dropped
    return answer


class KnowledgeAssistant:
    def __init__(self, index: VectorIndex, generator: GroundedGenerator, top_k: int = 3):
        self.index = index
        self.generator = generator
        self.top_k = top_k

    # Exposed as a method as well so notebooks can call assistant._validate_citations(...)
    _validate_citations = staticmethod(validate_citations)

    def answer(self, question: str) -> KnowledgeState:
        state = KnowledgeState(question=question)
        try:
            state.retrieved = self.index.search(question, top_k=self.top_k)
            state.status = "retrieved"
            answer = self.generator.generate(question, state.retrieved)
            state.answer = validate_citations(answer, state.retrieved)
            state.status = "completed"
        except Exception as exc:
            state.status = "failed"
            state.error = f"{type(exc).__name__}: {exc}"
        return state
