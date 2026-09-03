"""Run the Day 2 reference project in deterministic or classroom mode."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from knowledge_agent import (  # noqa: E402
    ChromaVectorIndex,
    KnowledgeAssistant,
    MockGroundedGenerator,
    OpenRouterGroundedGenerator,
    SentenceTransformerEmbedder,
    TokenHashEmbedder,
    VectorIndex,
    load_markdown_corpus,
)


def build_assistant(mode: str = "mock") -> KnowledgeAssistant:
    chunks = load_markdown_corpus(PROJECT_ROOT / "data" / "corpus")
    embedder = (
        TokenHashEmbedder()
        if mode == "mock"
        else SentenceTransformerEmbedder(os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))
    )
    generator = MockGroundedGenerator() if mode == "mock" else OpenRouterGroundedGenerator()
    index = VectorIndex(embedder) if mode == "mock" else ChromaVectorIndex(embedder)
    index.add(chunks)
    return KnowledgeAssistant(index, generator, top_k=3)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    mode = os.getenv("DAY2_MODE", "mock").lower()
    if mode not in {"mock", "classroom"}:
        raise ValueError("DAY2_MODE must be mock or classroom")
    question = " ".join(sys.argv[1:]) or "How long are battery fault records retained?"
    state = build_assistant(mode)
    result = state.answer(question)
    print(result.model_dump_json(indent=2))
    return 0 if result.status == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
