"""Real local embeddings plus a deterministic offline teaching fallback."""

from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


def _normalize(vector: list[float]) -> list[float]:
    magnitude = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / magnitude for value in vector]


def _tokens(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [word[:-1] if word.endswith("s") and len(word) > 4 else word for word in words]


class TokenHashEmbedder:
    """Stable token vectors for tests; not a substitute for semantic embeddings."""

    def __init__(self, dimensions: int = 512):
        self.dimensions = dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for text in texts:
            vector = [0.0] * self.dimensions
            for token in _tokens(text):
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                index = int.from_bytes(digest[:4], "big") % self.dimensions
                vector[index] += 1.0
            vectors.append(_normalize(vector))
        return vectors


class SentenceTransformerEmbedder:
    """Local semantic embeddings downloaded once and reused across requests."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError("Install sentence-transformers for semantic search") from exc
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        values = self.model.encode(texts, normalize_embeddings=True)
        return [vector.tolist() for vector in values]

