"""Run the Day 2 reference project in deterministic (mock) or classroom mode.

    python run_project.py                      # mock: hash embedder + offline generator
    DAY2_MODE=classroom python run_project.py  # semantic embedder + OpenRouter if a key exists

Classroom mode degrades instead of crashing: a missing model download, a missing chromadb
install or a missing API key each print one line and fall back to the offline component.
"""

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
    TokenHashEmbedder,
    VectorIndex,
    load_embedder,
    load_markdown_corpus,
)


def build_assistant(mode: str = "mock", top_k: int = 3, verbose: bool = False) -> KnowledgeAssistant:
    """Assemble corpus -> embedder -> index -> generator for the requested mode."""

    chunks = load_markdown_corpus(PROJECT_ROOT / "data" / "corpus")

    if mode == "mock":
        # Deterministic: the same vectors and the same answers on every machine.
        embedder, generator = TokenHashEmbedder(), MockGroundedGenerator()
        index: VectorIndex = VectorIndex(embedder)
    else:
        # Honour the EMBEDDER / DAY2_MODE toggles the notebooks use.
        embedder, label = load_embedder(verbose=verbose)
        generator = MockGroundedGenerator()
        if os.getenv("OPENROUTER_API_KEY"):
            try:
                generator = OpenRouterGroundedGenerator()
            except Exception as exc:  # bad key format, etc.
                print(f"Live generator unavailable ({exc}); using the offline generator.")
        elif verbose:
            print("No OPENROUTER_API_KEY: using the offline generator.")
        try:
            index = ChromaVectorIndex(embedder)
        except Exception as exc:  # chromadb not installed
            if verbose:
                print(f"Chroma unavailable ({type(exc).__name__}); using the in-memory index.")
            index = VectorIndex(embedder)
        if verbose:
            print(f"Classroom embedder: {label}")

    index.add(chunks)
    return KnowledgeAssistant(index, generator, top_k=top_k)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    mode = os.getenv("DAY2_MODE", "mock").lower()
    if mode not in {"mock", "classroom"}:
        raise ValueError("DAY2_MODE must be mock or classroom")
    question = " ".join(sys.argv[1:]) or "How long are battery fault records retained?"
    assistant = build_assistant(mode, verbose=True)
    result = assistant.answer(question)
    print(result.model_dump_json(indent=2))
    return 0 if result.status == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
