"""Reference components for the Day 2 Engineering Knowledge Assistant."""

from .assistant import KnowledgeAssistant
from .documents import load_markdown_corpus
from .embeddings import SentenceTransformerEmbedder, TokenHashEmbedder
from .generation import MockGroundedGenerator, OpenRouterGroundedGenerator
from .retrieval import ChromaVectorIndex, VectorIndex

__all__ = [
    "KnowledgeAssistant",
    "ChromaVectorIndex",
    "MockGroundedGenerator",
    "OpenRouterGroundedGenerator",
    "SentenceTransformerEmbedder",
    "TokenHashEmbedder",
    "VectorIndex",
    "load_markdown_corpus",
]
