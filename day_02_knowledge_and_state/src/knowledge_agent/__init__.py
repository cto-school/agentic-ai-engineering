"""Reference components for the Day 2 Engineering Knowledge Assistant."""

from .assistant import KnowledgeAssistant, validate_citations
from .documents import load_markdown_corpus
from .embeddings import SentenceTransformerEmbedder, TokenHashEmbedder, load_embedder
from .generation import (
    MockGroundedGenerator,
    OpenRouterGroundedGenerator,
    build_evidence_context,
    strict_json_schema,
)
from .retrieval import ChromaVectorIndex, VectorIndex

__all__ = [
    "ChromaVectorIndex",
    "KnowledgeAssistant",
    "MockGroundedGenerator",
    "OpenRouterGroundedGenerator",
    "SentenceTransformerEmbedder",
    "TokenHashEmbedder",
    "VectorIndex",
    "build_evidence_context",
    "load_embedder",
    "load_markdown_corpus",
    "strict_json_schema",
    "validate_citations",
]
